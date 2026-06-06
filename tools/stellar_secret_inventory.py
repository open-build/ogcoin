#!/usr/bin/env python3
"""Inventory local Stellar secret keys without printing the secret values.

The report lists file locations, derived public keys, and whether any discovered
key is a signer for the accounts under review. It never prints S... secrets.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from stellar_sdk import Keypair
from stellar_sdk.exceptions import Ed25519SecretSeedInvalidError
from stellar_sdk.strkey import StrKey


DEFAULT_TARGET_SIGNER = "GDJ4HVRGT2OVVL5YFLBR7XAJIHCMWUO6OKLBXWWTVW3OK4VBFRAYQJHV"
DEFAULT_LOCKED_ACCOUNTS = [
    "GC5PRFNWGGWTKVH5DLIO3QL5DV4FPBFAE26Q77BPSXCPQQWGJQVHSW7U",
    "GBCOBOTX7SWYWMEE5AZAOAEJ3O5CDE3P2EX7YXLR4AW64VXQUZQIUD3W",
]

SECRET_RE = re.compile(r"S[A-Z2-7]{55}")
PUBLIC_RE = re.compile(r"G[A-Z2-7]{55}")

SKIP_DIRS = {
    ".Trash",
    ".cache",
    ".codex",
    ".git",
    ".hg",
    ".npm",
    ".rustup",
    ".svn",
    ".tox",
    ".venv",
    "__pycache__",
    "Applications",
    "Library/Caches",
    "Library",
    "node_modules",
    "site-packages",
    "venv",
}

TEXT_EXTENSIONS = {
    "",
    ".bash_history",
    ".cfg",
    ".conf",
    ".csv",
    ".env",
    ".ini",
    ".json",
    ".jsonl",
    ".log",
    ".md",
    ".py",
    ".sh",
    ".txt",
    ".yaml",
    ".yml",
}


@dataclass
class SecretHit:
    public_key: str
    locations: set[str] = field(default_factory=set)
    labels: set[str] = field(default_factory=set)


def is_probably_text(path: Path, max_size: int) -> bool:
    if path.stat().st_size > max_size:
        return False
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    return path.name in {".env", ".bash_history", ".zsh_history"}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & SKIP_DIRS)


def iter_scan_paths(root: Path) -> Any:
    if root.is_file():
        yield root
        return
    if not root.is_dir():
        return

    skip_names = {name for name in SKIP_DIRS if "/" not in name}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if dirname not in skip_names and not dirname.startswith(".")
        ]
        for filename in filenames:
            yield Path(dirpath) / filename


def line_label(line: str) -> str:
    if "=" in line:
        return line.split("=", 1)[0].strip()[:80]
    if ":" in line:
        return line.split(":", 1)[0].strip()[:80]
    return ""


def scan_file(path: Path) -> tuple[list[tuple[str, int, str]], bool]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return [], False

    hits: list[tuple[str, int, str]] = []
    target_public_seen = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        if DEFAULT_TARGET_SIGNER in line:
            target_public_seen = True
        for secret in set(SECRET_RE.findall(line)):
            try:
                keypair = Keypair.from_secret(secret)
            except Ed25519SecretSeedInvalidError:
                continue
            hits.append((keypair.public_key, line_number, line_label(line)))
    return hits, target_public_seen


def scan_roots(roots: list[Path], max_size: int) -> tuple[dict[str, SecretHit], list[str]]:
    discovered: dict[str, SecretHit] = {}
    target_public_locations: list[str] = []

    for root in roots:
        for path in iter_scan_paths(root):
            if should_skip(path):
                continue
            try:
                if not is_probably_text(path, max_size):
                    continue
            except OSError:
                continue

            hits, target_seen = scan_file(path)
            if target_seen:
                target_public_locations.append(str(path))

            for public_key, line_number, label in hits:
                hit = discovered.setdefault(public_key, SecretHit(public_key=public_key))
                hit.locations.add(f"{path}:{line_number}")
                if label:
                    hit.labels.add(label)

    return discovered, sorted(set(target_public_locations))


def fetch_signers(account: str) -> dict[str, int]:
    import urllib.request

    url = f"https://horizon.stellar.org/accounts/{account}"
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception:
        return {}
    return {str(signer["key"]): int(signer.get("weight", 0)) for signer in data.get("signers", [])}


def format_account_status(public_key: str, account_signers: dict[str, dict[str, int]]) -> list[str]:
    statuses: list[str] = []
    for account, signers in account_signers.items():
        weight = signers.get(public_key)
        if weight is not None:
            statuses.append(f"signer for {account} with weight {weight}")
    return statuses


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inventory local Stellar S... secrets without revealing them.")
    parser.add_argument(
        "roots",
        nargs="*",
        default=[
            str(Path.home() / "Projects"),
            str(Path.home() / "Documents"),
            str(Path.home() / "Desktop"),
            str(Path.home() / "Downloads"),
        ],
        help="Files or directories to scan. Defaults to Projects, Documents, Desktop, and Downloads.",
    )
    parser.add_argument(
        "--target-signer",
        default=DEFAULT_TARGET_SIGNER,
        help="Public G... signer to flag. Default: current missing Lobstr signer.",
    )
    parser.add_argument(
        "--locked-account",
        action="append",
        default=[],
        help="Locked account to compare against. May be repeated.",
    )
    parser.add_argument("--max-size", type=int, default=2_000_000, help="Max file size to scan. Default: 2MB.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    target_signer = args.target_signer.strip()
    if not StrKey.is_valid_ed25519_public_key(target_signer):
        print("ERROR: --target-signer must be a valid Stellar G... public key.", file=sys.stderr)
        return 1

    locked_accounts = args.locked_account or DEFAULT_LOCKED_ACCOUNTS
    for account in locked_accounts:
        if not StrKey.is_valid_ed25519_public_key(account):
            print(f"ERROR: locked account is not a valid public key: {account}", file=sys.stderr)
            return 1

    roots = [Path(root).expanduser() for root in args.roots]
    discovered, target_public_locations = scan_roots(roots, args.max_size)
    account_signers = {account: fetch_signers(account) for account in locked_accounts}

    records: list[dict[str, Any]] = []
    for public_key, hit in sorted(discovered.items()):
        account_status = format_account_status(public_key, account_signers)
        records.append(
            {
                "public_key": public_key,
                "matches_target_signer": public_key == target_signer,
                "locked_account_status": account_status,
                "labels": sorted(hit.labels),
                "locations": sorted(hit.locations),
            }
        )

    if args.json:
        print(
            json.dumps(
                {
                    "target_signer": target_signer,
                    "roots": [str(root) for root in roots],
                    "secret_count": len(records),
                    "matching_target_secret_found": any(record["matches_target_signer"] for record in records),
                    "target_public_locations": target_public_locations,
                    "records": records,
                },
                indent=2,
            )
        )
        return 0

    print("# Stellar Secret Inventory")
    print()
    print("No S... secret values are printed by this report.")
    print(f"Target signer: {target_signer}")
    print(f"Roots scanned: {', '.join(str(root) for root in roots)}")
    print(f"Derived public keys found: {len(records)}")
    print()

    matching = [record for record in records if record["matches_target_signer"]]
    if matching:
        print("## Target Signer Secret")
        for record in matching:
            print(f"- FOUND secret for target signer at: {', '.join(record['locations'])}")
    else:
        print("## Target Signer Secret")
        print("- No discovered secret derives to the target signer.")

    if target_public_locations:
        print()
        print("## Files Mentioning Target Public Key")
        for location in target_public_locations:
            print(f"- {location}")

    print()
    print("## Derived Public Keys")
    for record in records:
        marker = " TARGET" if record["matches_target_signer"] else ""
        print(f"- {record['public_key']}{marker}")
        if record["locked_account_status"]:
            for status in record["locked_account_status"]:
                print(f"  status: {status}")
        if record["labels"]:
            print(f"  labels: {', '.join(record['labels'])}")
        print(f"  locations: {', '.join(record['locations'])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
