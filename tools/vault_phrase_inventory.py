#!/usr/bin/env python3
"""Find local BIP39 recovery phrase candidates without printing the phrases.

This script is for local recovery work. It reports file paths, line ranges,
derived Stellar public keys, and whether a candidate phrase derives to the
target signer. It never prints mnemonic words or Stellar S... secret keys.
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from stellar_sdk import Keypair
from stellar_sdk.sep.mnemonic import Mnemonic
from stellar_sdk.strkey import StrKey


DEFAULT_TARGET_SIGNER = "GDJ4HVRGT2OVVL5YFLBR7XAJIHCMWUO6OKLBXWWTVW3OK4VBFRAYQJHV"
PHRASE_LENGTHS = (12, 15, 18, 21, 24)
WORD_RE = re.compile(r"[A-Za-z]+")

SKIP_DIRS = {
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
    "Library",
    "node_modules",
    "site-packages",
    "venv",
}

TEXT_EXTENSIONS = {
    "",
    ".csv",
    ".env",
    ".ini",
    ".json",
    ".jsonl",
    ".log",
    ".md",
    ".rtf",
    ".txt",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True)
class Candidate:
    phrase: str
    file: Path
    start_line: int
    end_line: int
    word_count: int


def iter_scan_paths(root: Path) -> Any:
    if root.is_file():
        yield root
        return
    if not root.is_dir():
        return

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if dirname not in SKIP_DIRS and not dirname.startswith(".")
        ]
        for filename in filenames:
            yield Path(dirpath) / filename


def is_probably_text(path: Path, max_size: int) -> bool:
    try:
        if path.stat().st_size > max_size:
            return False
    except OSError:
        return False
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    return path.name in {".env", ".bash_history", ".zsh_history"}


def tokenize(text: str) -> list[tuple[str, int]]:
    tokens: list[tuple[str, int]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in WORD_RE.finditer(line):
            tokens.append((match.group(0).lower(), line_number))
    return tokens


def phrase_fingerprint(phrase: str) -> str:
    # A short local identifier lets repeated reports be compared without
    # exposing the phrase. It is not a recovery aid.
    return hashlib.sha256(phrase.encode("utf-8")).hexdigest()[:12]


def find_candidates(path: Path, mnemonic: Mnemonic, wordlist: set[str]) -> list[Candidate]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    tokens = tokenize(text)
    candidates: list[Candidate] = []
    seen: set[str] = set()

    for index in range(len(tokens)):
        for length in PHRASE_LENGTHS:
            window = tokens[index : index + length]
            if len(window) != length:
                continue
            words = [word for word, _line in window]
            if not all(word in wordlist for word in words):
                continue
            phrase = " ".join(words)
            if phrase in seen:
                continue
            if not mnemonic.check(phrase):
                continue
            seen.add(phrase)
            candidates.append(
                Candidate(
                    phrase=phrase,
                    file=path,
                    start_line=window[0][1],
                    end_line=window[-1][1],
                    word_count=length,
                )
            )
    return candidates


def derive_public_keys(phrase: str, index_max: int) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index in range(index_max + 1):
        keypair = Keypair.from_mnemonic_phrase(phrase, index=index)
        records.append({"index": index, "public_key": keypair.public_key})
    return records


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inventory local recovery phrase candidates without printing phrases.")
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
    parser.add_argument("--target-signer", default=DEFAULT_TARGET_SIGNER, help="Public G... signer to search for.")
    parser.add_argument("--index-max", type=int, default=10, help="Highest Stellar derivation index to test. Default: 10.")
    parser.add_argument("--max-size", type=int, default=500_000, help="Max file size to scan. Default: 500KB.")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for recovery phrases without echoing them instead of scanning files.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args(argv)


def interactive_check(target: str, index_max: int) -> int:
    mnemonic = Mnemonic("english")
    print("# Interactive Vault Phrase Check")
    print()
    print("Input is hidden. No recovery phrase or S... secret key will be printed.")
    print(f"Target signer: {target}")
    print("Press Enter on an empty prompt to stop.")
    print()

    checked = 0
    while True:
        phrase = getpass.getpass("Recovery phrase: ").strip().lower()
        if not phrase:
            break
        checked += 1
        candidate_id = phrase_fingerprint(phrase)
        words = phrase.split()
        print(f"Candidate `{candidate_id}`: {len(words)} words")
        if len(words) not in PHRASE_LENGTHS:
            print("- not a standard BIP39 length")
            print()
            continue
        if not mnemonic.check(phrase):
            print("- not a valid BIP39 checksum")
            print()
            continue

        derived = derive_public_keys(phrase, index_max)
        matches = [record for record in derived if record["public_key"] == target]
        if matches:
            indices = ", ".join(str(record["index"]) for record in matches)
            print(f"- MATCH: derives to target signer at Stellar index {indices}")
        else:
            print(f"- no target match in Stellar indices 0-{index_max}")
            preview_count = min(5, len(derived))
            print("- first derived public keys:")
            for record in derived[:preview_count]:
                print(f"  {record['index']}: {record['public_key']}")
        print()

    print(f"Checked {checked} phrase candidate(s).")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    target = args.target_signer.strip()
    if not StrKey.is_valid_ed25519_public_key(target):
        print("ERROR: --target-signer must be a valid Stellar public G... key.", file=sys.stderr)
        return 1
    if args.index_max < 0 or args.index_max > 100:
        print("ERROR: --index-max must be between 0 and 100.", file=sys.stderr)
        return 1

    if args.interactive:
        return interactive_check(target, args.index_max)

    mnemonic = Mnemonic("english")
    wordlist = set(mnemonic.wordlist)
    roots = [Path(root).expanduser() for root in args.roots]

    all_records: list[dict[str, Any]] = []
    for root in roots:
        for path in iter_scan_paths(root):
            if not is_probably_text(path, args.max_size):
                continue
            for candidate in find_candidates(path, mnemonic, wordlist):
                derived = derive_public_keys(candidate.phrase, args.index_max)
                matches = [record for record in derived if record["public_key"] == target]
                all_records.append(
                    {
                        "id": phrase_fingerprint(candidate.phrase),
                        "file": str(candidate.file),
                        "start_line": candidate.start_line,
                        "end_line": candidate.end_line,
                        "word_count": candidate.word_count,
                        "target_match": bool(matches),
                        "target_match_indices": [record["index"] for record in matches],
                        "derived_public_keys": derived,
                    }
                )

    if args.json:
        print(
            json.dumps(
                {
                    "target_signer": target,
                    "roots": [str(root) for root in roots],
                    "candidate_count": len(all_records),
                    "target_match_found": any(record["target_match"] for record in all_records),
                    "records": all_records,
                },
                indent=2,
            )
        )
        return 0

    print("# Vault Phrase Inventory")
    print()
    print("No recovery phrases or S... secret keys are printed by this report.")
    print(f"Target signer: {target}")
    print(f"Roots scanned: {', '.join(str(root) for root in roots)}")
    print(f"Valid BIP39 phrase candidates found: {len(all_records)}")
    print()

    matches = [record for record in all_records if record["target_match"]]
    print("## Target Match")
    if matches:
        for record in matches:
            line_range = f"{record['start_line']}-{record['end_line']}"
            indices = ", ".join(str(index) for index in record["target_match_indices"])
            print(f"- FOUND candidate `{record['id']}` in {record['file']}:{line_range}; Stellar index {indices}")
    else:
        print("- No candidate phrase derives to the target signer for the tested indices.")

    if all_records:
        print()
        print("## Candidates")
        for record in all_records:
            line_range = f"{record['start_line']}-{record['end_line']}"
            print(f"- `{record['id']}` {record['word_count']}-word phrase candidate at {record['file']}:{line_range}")
            if record["target_match"]:
                print(f"  target match indices: {record['target_match_indices']}")
            preview = ", ".join(
                f"{derived['index']}:{derived['public_key']}" for derived in record["derived_public_keys"][:3]
            )
            print(f"  first derived public keys: {preview}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
