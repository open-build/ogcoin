#!/usr/bin/env python3
"""Validate and update the public OGCoin transparency log.

This helper only edits data/transparency-log.json. It does not sign Stellar
transactions, submit XDR, read secret keys, or make network calls.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_PATH = PROJECT_ROOT / "data" / "transparency-log.json"

CATEGORIES = {
    "distribution",
    "governance",
    "grant",
    "liquidity",
    "policy",
    "treasury",
}

STATUSES = {
    "approved",
    "cancelled",
    "confirmed_on_chain",
    "executed",
    "pending_review",
    "published",
    "voided",
}

TOP_LEVEL_KEYS = {
    "schema_version",
    "updated_at",
    "network",
    "asset",
    "accounts",
    "entries",
    "open_items",
    "reporting_rules",
}

ENTRY_KEYS = {
    "id",
    "date",
    "category",
    "status",
    "title",
    "summary",
    "account_role",
    "account",
    "amount_ogc",
    "counter_asset",
    "transaction_hash",
    "ledger",
    "links",
}

PUBLIC_ACCOUNT_RE = re.compile(r"^G[A-Z2-7]{55}$")
TRANSACTION_HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")
ENTRY_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,}$")


class TransparencyLogError(ValueError):
    """Raised when the log or proposed entry fails validation."""


def load_log(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise TransparencyLogError(f"{path} does not exist") from exc
    except json.JSONDecodeError as exc:
        raise TransparencyLogError(f"{path} is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise TransparencyLogError("Transparency log must be a JSON object")
    return data


def write_log(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")
    temp_path.replace(path)


def utc_timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_log_date(value: str, label: str) -> None:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise TransparencyLogError(f"{label} must use YYYY-MM-DD")
    try:
        dt.date.fromisoformat(value)
    except ValueError as exc:
        raise TransparencyLogError(f"{label} is not a valid calendar date") from exc


def parse_timestamp(value: str, label: str) -> None:
    if not isinstance(value, str):
        raise TransparencyLogError(f"{label} must be a string")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        dt.datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise TransparencyLogError(f"{label} must be an ISO-8601 timestamp") from exc


def normalize_amount(value: str | int | float | Decimal | None) -> str:
    if value in (None, ""):
        value = "0"
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise TransparencyLogError("amount_ogc must be a decimal number") from exc

    if amount < 0:
        raise TransparencyLogError("amount_ogc cannot be negative")
    if amount.as_tuple().exponent < -7:
        raise TransparencyLogError("amount_ogc cannot have more than 7 decimal places")

    normalized = format(amount.normalize(), "f")
    if normalized == "-0":
        return "0"
    return normalized


def require_string(value: Any, label: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, str):
        raise TransparencyLogError(f"{label} must be a string")
    if not allow_empty and not value.strip():
        raise TransparencyLogError(f"{label} cannot be empty")


def validate_url(value: Any, label: str) -> None:
    require_string(value, label)
    if not value.startswith(("https://", "http://")):
        raise TransparencyLogError(f"{label} must start with http:// or https://")


def validate_public_account(value: Any, label: str) -> None:
    if value is None:
        return
    require_string(value, label)
    if not PUBLIC_ACCOUNT_RE.fullmatch(value):
        raise TransparencyLogError(f"{label} must look like a Stellar public account")


def validate_entry(entry: Any, label: str) -> None:
    if not isinstance(entry, dict):
        raise TransparencyLogError(f"{label} must be an object")

    missing = sorted(ENTRY_KEYS - set(entry))
    if missing:
        raise TransparencyLogError(f"{label} is missing keys: {', '.join(missing)}")

    extra = sorted(set(entry) - ENTRY_KEYS)
    if extra:
        raise TransparencyLogError(f"{label} has unsupported keys: {', '.join(extra)}")

    require_string(entry["id"], f"{label}.id")
    if not ENTRY_ID_RE.fullmatch(entry["id"]):
        raise TransparencyLogError(f"{label}.id must use lowercase letters, numbers, and hyphens")

    require_string(entry["date"], f"{label}.date")
    parse_log_date(entry["date"], f"{label}.date")

    require_string(entry["category"], f"{label}.category")
    if entry["category"] not in CATEGORIES:
        raise TransparencyLogError(f"{label}.category must be one of: {', '.join(sorted(CATEGORIES))}")

    require_string(entry["status"], f"{label}.status")
    if entry["status"] not in STATUSES:
        raise TransparencyLogError(f"{label}.status must be one of: {', '.join(sorted(STATUSES))}")

    require_string(entry["title"], f"{label}.title")
    require_string(entry["summary"], f"{label}.summary")

    if entry["account_role"] is not None:
        require_string(entry["account_role"], f"{label}.account_role")
    validate_public_account(entry["account"], f"{label}.account")

    normalize_amount(entry["amount_ogc"])

    if entry["counter_asset"] is not None:
        require_string(entry["counter_asset"], f"{label}.counter_asset")

    transaction_hash = entry["transaction_hash"]
    ledger = entry["ledger"]
    if transaction_hash is not None:
        require_string(transaction_hash, f"{label}.transaction_hash")
        if not TRANSACTION_HASH_RE.fullmatch(transaction_hash):
            raise TransparencyLogError(f"{label}.transaction_hash must be 64 hex characters")
    if ledger is not None:
        if not isinstance(ledger, int) or ledger <= 0:
            raise TransparencyLogError(f"{label}.ledger must be a positive integer or null")

    if bool(transaction_hash) != bool(ledger):
        raise TransparencyLogError(f"{label} must include both transaction_hash and ledger, or neither")
    if entry["status"] == "confirmed_on_chain" and not transaction_hash:
        raise TransparencyLogError(f"{label} is confirmed_on_chain but has no transaction hash")

    links = entry["links"]
    if not isinstance(links, list):
        raise TransparencyLogError(f"{label}.links must be a list")
    for index, link in enumerate(links):
        validate_url(link, f"{label}.links[{index}]")


def validate_log(data: dict[str, Any]) -> None:
    missing = sorted(TOP_LEVEL_KEYS - set(data))
    if missing:
        raise TransparencyLogError(f"Transparency log is missing keys: {', '.join(missing)}")

    parse_timestamp(data["updated_at"], "updated_at")

    accounts = data["accounts"]
    if not isinstance(accounts, list):
        raise TransparencyLogError("accounts must be a list")
    for index, account in enumerate(accounts):
        if not isinstance(account, dict):
            raise TransparencyLogError(f"accounts[{index}] must be an object")
        require_string(account.get("role"), f"accounts[{index}].role")
        validate_public_account(account.get("address"), f"accounts[{index}].address")
        require_string(account.get("status"), f"accounts[{index}].status")
        require_string(account.get("policy"), f"accounts[{index}].policy")

    entries = data["entries"]
    if not isinstance(entries, list):
        raise TransparencyLogError("entries must be a list")

    seen_ids: set[str] = set()
    for index, entry in enumerate(entries):
        validate_entry(entry, f"entries[{index}]")
        entry_id = entry["id"]
        if entry_id in seen_ids:
            raise TransparencyLogError(f"Duplicate entry id: {entry_id}")
        seen_ids.add(entry_id)

    if not isinstance(data["open_items"], list):
        raise TransparencyLogError("open_items must be a list")
    if not isinstance(data["reporting_rules"], list):
        raise TransparencyLogError("reporting_rules must be a list")
    for index, rule in enumerate(data["reporting_rules"]):
        require_string(rule, f"reporting_rules[{index}]")


def build_entry(args: argparse.Namespace) -> dict[str, Any]:
    transaction_hash = args.tx.lower() if args.tx else None
    return {
        "id": args.id,
        "date": args.date,
        "category": args.category,
        "status": args.status,
        "title": args.title.strip(),
        "summary": args.summary.strip(),
        "account_role": args.account_role,
        "account": args.account,
        "amount_ogc": normalize_amount(args.amount_ogc),
        "counter_asset": args.counter_asset,
        "transaction_hash": transaction_hash,
        "ledger": args.ledger,
        "links": args.link or [],
    }


def sort_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(entries, key=lambda entry: (entry["date"], entry["id"]))


def print_entry_list(data: dict[str, Any]) -> None:
    entries = data["entries"]
    if not entries:
        print("No transparency entries yet.")
        return

    for entry in entries:
        amount = entry["amount_ogc"]
        if entry["counter_asset"]:
            amount = f"{amount} OGC / {entry['counter_asset']}"
        else:
            amount = f"{amount} OGC"
        chain = ""
        if entry["transaction_hash"]:
            chain = f" ledger {entry['ledger']} tx {entry['transaction_hash'][:10]}..."
        print(f"{entry['date']}  {entry['category']:<12} {entry['status']:<18} {amount:<18} {entry['id']}{chain}")


def command_validate(args: argparse.Namespace) -> int:
    data = load_log(args.path)
    validate_log(data)
    print(f"OK: {args.path} is valid ({len(data['entries'])} entries, {len(data['accounts'])} accounts).")
    return 0


def command_list(args: argparse.Namespace) -> int:
    data = load_log(args.path)
    validate_log(data)
    print_entry_list(data)
    return 0


def command_add(args: argparse.Namespace) -> int:
    data = load_log(args.path)
    validate_log(data)

    entry = build_entry(args)
    validate_entry(entry, "new entry")

    existing_ids = {item["id"] for item in data["entries"]}
    if entry["id"] in existing_ids:
        raise TransparencyLogError(f"Entry id already exists: {entry['id']}")

    data["entries"] = sort_entries([*data["entries"], entry])
    data["updated_at"] = utc_timestamp()
    validate_log(data)

    if args.dry_run:
        print("Dry run only; file was not changed. Proposed entry:")
        print(json.dumps(entry, indent=2))
        return 0

    write_log(args.path, data)
    print(f"Added {entry['id']} to {args.path}.")
    return 0


def add_path_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_LOG_PATH,
        help=f"Path to transparency log JSON. Default: {DEFAULT_LOG_PATH}",
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and append reviewed records to the OGCoin transparency log.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate the transparency log schema")
    add_path_argument(validate_parser)
    validate_parser.set_defaults(func=command_validate)

    list_parser = subparsers.add_parser("list", help="List current transparency entries")
    add_path_argument(list_parser)
    list_parser.set_defaults(func=command_list)

    add_parser = subparsers.add_parser("add", help="Append a reviewed transparency entry")
    add_path_argument(add_parser)
    add_parser.add_argument("--id", required=True, help="Stable lowercase id, for example 2026-05-22-home-domain")
    add_parser.add_argument("--date", required=True, help="Record date in YYYY-MM-DD format")
    add_parser.add_argument("--category", required=True, choices=sorted(CATEGORIES))
    add_parser.add_argument("--status", required=True, choices=sorted(STATUSES))
    add_parser.add_argument("--title", required=True, help="Short public title")
    add_parser.add_argument("--summary", required=True, help="Public summary with no private recipient or payroll data")
    add_parser.add_argument("--account-role", help="Public account role, for example issuer, treasury, grant, liquidity")
    add_parser.add_argument("--account", help="Public Stellar account involved in the record")
    add_parser.add_argument("--amount-ogc", default="0", help="OGC amount, up to 7 decimal places. Default: 0")
    add_parser.add_argument("--counter-asset", help="Counter asset for liquidity records, for example XLM")
    add_parser.add_argument("--tx", help="64-character Stellar transaction hash")
    add_parser.add_argument("--ledger", type=int, help="Stellar ledger number for the transaction")
    add_parser.add_argument("--link", action="append", help="Public supporting URL. May be repeated")
    add_parser.add_argument("--dry-run", action="store_true", help="Validate and print the entry without editing the file")
    add_parser.set_defaults(func=command_add)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        return args.func(args)
    except TransparencyLogError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
