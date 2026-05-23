#!/usr/bin/env python3
"""Generate OGCoin role wallet keypairs and write public Markdown.

The public output contains only Stellar public `G...` addresses. A separate
local seed file is written under `.ogcoin-secrets/` by default and should be
moved into a password manager or hardware-wallet custody process immediately.

This script does not fund accounts, create trustlines, sign transactions, or
submit anything to Stellar.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import stat
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from stellar_sdk import Keypair
except Exception as exc:  # pragma: no cover - dependency guard
    print("ERROR: stellar-sdk is required. Install with: pip install stellar-sdk", file=sys.stderr)
    raise SystemExit(1) from exc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PUBLIC_OUTPUT = PROJECT_ROOT / "devdocs" / "GENERATED_ROLE_WALLETS.md"
DEFAULT_SECRET_DIR = PROJECT_ROOT / ".ogcoin-secrets"

ISSUER = "GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57"
DISTRIBUTION_ACCOUNT = "GDD6IVZJVY3ZFWJ5T5BCZDURLF64ZTQJDDR5X5A7XEDJYTEC6ISDGWZB"
ISSUER_SIGNER = "GBZAC66WWHFU2FEOG5KECSEVR6EJO7BYK63UGB52SENDN4JEJTJEVK5L"

DEFAULT_ROLES = ("treasury", "grant", "liquidity")

ROLE_PURPOSES = {
    "treasury": "Cold or low-frequency reserves and approved program funding.",
    "grant": "Approved open source project grants and community allocations.",
    "liquidity": "Tiny, policy-limited OGC/XLM test activity after approval.",
}

ROLE_FIRST_STEPS = {
    "treasury": "Fund with minimum XLM reserve; keep cold unless an approved movement is needed.",
    "grant": "Fund with minimum XLM reserve and add OGC trustline before receiving OGC inventory.",
    "liquidity": "Fund with minimum XLM reserve, add OGC trustline, then keep market activity blocked until limits are approved.",
}


@dataclass(frozen=True)
class RoleWallet:
    role: str
    public_key: str
    secret_key: str


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def default_secret_output() -> Path:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return DEFAULT_SECRET_DIR / f"{stamp}-role-wallet-seeds.md"


def resolve_output(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path


def generate_wallets(roles: list[str]) -> list[RoleWallet]:
    wallets: list[RoleWallet] = []
    for role in roles:
        keypair = Keypair.random()
        wallets.append(RoleWallet(role=role, public_key=keypair.public_key, secret_key=keypair.secret))
    return wallets


def markdown_table_row(values: list[str]) -> str:
    return "| " + " | ".join(value.replace("\n", " ") for value in values) + " |"


def wallet_designation_command(wallets: list[RoleWallet]) -> str:
    parts = ["python3 tools/ogcoin_next_steps.py wallet-designation"]
    for wallet in wallets:
        parts.append(f"  --{wallet.role} {wallet.public_key}")
    return " \\\n".join(parts)


def build_public_markdown(wallets: list[RoleWallet], secret_output: Path | None) -> str:
    lines = [
        "# OGCoin Generated Role Wallets",
        "",
        f"Generated: `{now_utc()}`",
        "",
        "This file contains public Stellar account addresses only. These accounts are not active on Stellar mainnet until they are funded with XLM.",
        "",
        "## Public Addresses",
        "",
        markdown_table_row(["Role", "Public address", "Purpose", "First step"]),
        markdown_table_row(["---", "---", "---", "---"]),
    ]
    for wallet in wallets:
        lines.append(
            markdown_table_row(
                [
                    f"`{wallet.role}`",
                    f"`{wallet.public_key}`",
                    ROLE_PURPOSES.get(wallet.role, "Approved OGCoin role wallet."),
                    ROLE_FIRST_STEPS.get(wallet.role, "Fund with minimum XLM reserve before use."),
                ]
            )
        )

    lines.extend(
        [
            "",
            "## Designation Dry Run",
            "",
            "Run this after the seed keys have been secured and the public addresses are approved:",
            "",
            "```bash",
            wallet_designation_command(wallets),
            "```",
            "",
            "Then run each printed `tools/transparency_log.py designate-account` command with `--dry-run`, review the output, remove `--dry-run` only after approval, and commit the transparency log update.",
            "",
            "## Activation Checklist",
            "",
            "1. Move seed keys into a password manager, hardware signer, or other approved custody process.",
            "2. Delete any plaintext seed file after custody is confirmed.",
            "3. Fund each public account with enough XLM for minimum balance, trustlines, and fees.",
            "4. Add OGC trustlines for grant and liquidity wallets before sending OGC to them.",
            "5. Keep liquidity activity blocked until exposure limits and approval are public.",
            "6. Never use the issuer, distribution wallet, or personal issuer signer as these operating wallets.",
            "",
            "## Existing Accounts Not To Reuse",
            "",
            f"- Issuer: `{ISSUER}`",
            f"- Distribution: `{DISTRIBUTION_ACCOUNT}`",
            f"- Issuer signer / personal signer: `{ISSUER_SIGNER}`",
            "",
            "## Private Seed Location",
            "",
        ]
    )
    if secret_output:
        lines.append(f"The generated seed keys were written to local gitignored file: `{relative(secret_output)}`.")
        lines.append("Move them into durable secure custody, then delete that plaintext file.")
    else:
        lines.append("No seed file was written. If you did not separately capture the seeds, these generated addresses are not usable.")
    lines.append("")
    return "\n".join(lines)


def build_secret_markdown(wallets: list[RoleWallet], public_output: Path) -> str:
    lines = [
        "# OGCoin Role Wallet Seed Keys",
        "",
        f"Generated: `{now_utc()}`",
        "",
        "WARNING: This file contains Stellar secret seed keys. Anyone with these `S...` values can control the corresponding accounts.",
        "",
        "Move these seeds into approved secure custody immediately. Do not commit this file. Delete the plaintext copy after custody is confirmed.",
        "",
        f"Public address document: `{relative(public_output)}`",
        "",
        "## Seeds",
        "",
        markdown_table_row(["Role", "Public address", "Secret seed"]),
        markdown_table_row(["---", "---", "---"]),
    ]
    for wallet in wallets:
        lines.append(markdown_table_row([f"`{wallet.role}`", f"`{wallet.public_key}`", f"`{wallet.secret_key}`"]))
    lines.append("")
    return "\n".join(lines)


def write_file(path: Path, content: str, *, force: bool, private: bool = False) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"{relative(path)} already exists. Pass --force to overwrite.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if private:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate OGCoin role wallets and write public Markdown.")
    parser.add_argument(
        "--role",
        action="append",
        choices=DEFAULT_ROLES,
        help="Role to generate. May be repeated. Defaults to treasury, grant, and liquidity.",
    )
    parser.add_argument(
        "--public-output",
        type=Path,
        default=DEFAULT_PUBLIC_OUTPUT,
        help=f"Public Markdown output. Default: {DEFAULT_PUBLIC_OUTPUT}",
    )
    parser.add_argument(
        "--secret-output",
        type=Path,
        help="Private seed Markdown output. Default: .ogcoin-secrets/<timestamp>-role-wallet-seeds.md",
    )
    parser.add_argument(
        "--no-secret-file",
        action="store_true",
        help="Do not write the private seed file. This makes the generated wallets unusable unless seeds are captured another way.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing output files.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    roles = args.role or list(DEFAULT_ROLES)
    wallets = generate_wallets(roles)

    public_output = resolve_output(args.public_output)
    secret_output = None if args.no_secret_file else resolve_output(args.secret_output or default_secret_output())

    public_markdown = build_public_markdown(wallets, secret_output)
    secret_markdown = build_secret_markdown(wallets, public_output) if secret_output else None

    write_file(public_output, public_markdown, force=args.force)
    if secret_output and secret_markdown:
        write_file(secret_output, secret_markdown, force=args.force, private=True)

    print(f"Wrote public wallet addresses: {public_output}")
    if secret_output:
        print(f"Wrote private seed file: {secret_output}")
        print("Move seed keys into secure custody, then delete the plaintext seed file.")
    else:
        print("No seed file written. Generated wallets are unusable unless seeds were captured separately.")
    print("Next: review the public Markdown, then run the wallet-designation dry-run command it contains.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
