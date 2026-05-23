#!/usr/bin/env python3
"""Prepare safe OGCoin next-step operations.

This helper is intentionally non-custodial. It validates public account
formats, reads the public transparency log, and prints reviewable commands.
It never reads secret keys, signs transactions, or submits anything to Stellar.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shlex
import sys
import urllib.error
import urllib.request
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

try:
    from stellar_sdk import StrKey
except Exception:  # pragma: no cover - optional dependency fallback
    StrKey = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRANSPARENCY_LOG = PROJECT_ROOT / "data" / "transparency-log.json"

ASSET_CODE = "OGC"
ISSUER = "GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57"
DISTRIBUTION_ACCOUNT = "GDD6IVZJVY3ZFWJ5T5BCZDURLF64ZTQJDDR5X5A7XEDJYTEC6ISDGWZB"
TRUSTLINE_URL = "https://www.opengreencoin.com/trustline.html"
LIQUIDITY_POLICY_URL = "https://www.opengreencoin.com/liquidity-policy.html"
TRANSPARENCY_URL = "https://www.opengreencoin.com/transparency.html"
HORIZON_URL = "https://horizon.stellar.org"

PUBLIC_ACCOUNT_RE = re.compile(r"^G[A-Z2-7]{55}$")
SECRET_KEY_RE = re.compile(r"^S[A-Z2-7]{55}$")

CORE_ROLES = ("treasury", "grant", "liquidity")

ROLE_POLICIES = {
    "treasury": (
        "Cold or low-frequency account for approved OGCoin treasury activity; "
        "no routine airdrops, payroll, or liquidity operations."
    ),
    "grant": (
        "Public grant disbursement account for approved open source project "
        "allocations; no issuer configuration, payroll, or liquidity operations."
    ),
    "liquidity": (
        "Public liquidity test account for policy-limited OGC/XLM market activity; "
        "must stay within approved exposure limits and public reconciliation rules."
    ),
}

ROLE_SUMMARIES = {
    "treasury": "Designated the public treasury wallet for approved OGCoin reserve and program funding activity.",
    "grant": "Designated the public grant wallet for approved open source project and community allocations.",
    "liquidity": "Designated the public liquidity wallet for policy-limited OGC/XLM test activity.",
}


class OpsError(ValueError):
    """Raised when a proposed operation is unsafe or malformed."""


def today() -> str:
    return dt.date.today().isoformat()


def load_log(path: Path = TRANSPARENCY_LOG) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise OpsError(f"Transparency log not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise OpsError(f"Transparency log is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise OpsError("Transparency log must be a JSON object.")
    return data


def accounts_by_role(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    accounts = data.get("accounts")
    if not isinstance(accounts, list):
        raise OpsError("Transparency log accounts must be a list.")
    return {
        str(account.get("role")): account
        for account in accounts
        if isinstance(account, dict) and account.get("role")
    }


def validate_public_account(address: str, label: str = "account") -> str:
    address = (address or "").strip()
    if SECRET_KEY_RE.fullmatch(address):
        raise OpsError(f"{label} looks like a secret key. Use public G... addresses only.")
    if not PUBLIC_ACCOUNT_RE.fullmatch(address):
        raise OpsError(f"{label} must be a Stellar public account that starts with G.")
    if StrKey and not StrKey.is_valid_ed25519_public_key(address):
        raise OpsError(f"{label} is not a valid Stellar public account checksum.")
    return address


def parse_amount(value: str, label: str) -> Decimal:
    try:
        amount = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise OpsError(f"{label} must be a decimal amount.") from exc
    if amount <= 0:
        raise OpsError(f"{label} must be greater than 0.")
    if amount.as_tuple().exponent < -7:
        raise OpsError(f"{label} cannot have more than 7 decimal places.")
    return amount


def validate_date(value: str) -> str:
    try:
        dt.date.fromisoformat(value)
    except ValueError as exc:
        raise OpsError("--date must use YYYY-MM-DD.") from exc
    return value


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def stellar_expert_tx_url_placeholder() -> str:
    return "https://stellar.expert/explorer/public/tx/TX_HASH"


def print_heading(title: str) -> None:
    print(f"\n## {title}")


def current_wallet_status(data: dict[str, Any]) -> None:
    accounts = accounts_by_role(data)
    print_heading("Wallet Designation Status")
    for role in ("issuer", "issuer_signer", "distribution", *CORE_ROLES):
        account = accounts.get(role)
        if not account:
            print(f"- {role}: missing from transparency log")
            continue
        address = account.get("address") or "pending"
        print(f"- {role}: {account.get('status', 'unknown')} - {address}")


def command_status(_args: argparse.Namespace) -> int:
    data = load_log()
    current_wallet_status(data)
    print_heading("Next Safe Actions")
    print(f"1. Share {TRUSTLINE_URL} with known testers and collect public G... addresses only.")
    print("2. Choose separate public accounts for treasury, grant, and liquidity.")
    print("3. Publish each wallet designation through a dry-run review, then commit the transparency log.")
    print("4. Keep OGC/XLM market activity blocked until the liquidity wallet is designated and funded for a tiny test.")
    return 0


def command_trustline_campaign(args: argparse.Namespace) -> int:
    target = args.target
    if target < 1:
        raise OpsError("--target must be at least 1.")
    amount = parse_amount(args.amount, "--amount")

    print_heading("Trustline Growth Plan")
    print(f"Target: {target} known testers with active OGC trustlines.")
    print(f"Public guide: {TRUSTLINE_URL}")
    print("\nInvite copy:")
    print(
        "OGCoin (OGC) is an experimental Stellar asset for Open Build open source funding and "
        "developer education. If you want to help test the distribution flow, add the OGC "
        f"trustline using {TRUSTLINE_URL}, then send only your public Stellar G... address. "
        "Never send a secret key or recovery phrase. OGC distributions are discretionary and "
        "do not promise profit, redemption, or liquidity."
    )

    print("\nCSV collection template:")
    print("address,amount,memo")
    print(f"G...PUBLIC_ACCOUNT,{amount.normalize()},trustline-pilot")

    print("\nValidation path:")
    print("- Paste the CSV into the local console recipient validator, with online checks enabled.")
    print("- Count only rows marked ready: account exists and has OGC trustline.")
    print("- Do not run a distribution until the dry-run total and recipient list are reviewed.")
    print("\nCommands:")
    print("python3 tools/ogcoin_console.py")
    print("python3 tools/ogcoin_console.py --check")
    return 0


def designation_command(role: str, address: str, date: str) -> str:
    return shell_join(
        [
            "python3",
            "tools/transparency_log.py",
            "designate-account",
            "--role",
            role,
            "--address",
            address,
            "--date",
            date,
            "--policy",
            ROLE_POLICIES[role],
            "--summary",
            ROLE_SUMMARIES[role],
            "--dry-run",
        ]
    )


def validate_wallet_plan(data: dict[str, Any], proposed: dict[str, str]) -> None:
    if not proposed:
        return

    seen: dict[str, str] = {}
    for role, address in proposed.items():
        validate_public_account(address, role)
        if address in {ISSUER, DISTRIBUTION_ACCOUNT}:
            raise OpsError(f"{role} must be separate from the issuer and distribution accounts.")
        if address in seen:
            raise OpsError(f"{role} and {seen[address]} cannot use the same account.")
        seen[address] = role

    accounts = accounts_by_role(data)
    for role, address in proposed.items():
        existing = accounts.get(role, {})
        existing_address = existing.get("address")
        if existing_address and existing_address != address:
            raise OpsError(
                f"{role} already has {existing_address}. Use transparency_log.py --replace only after review."
            )

        for other_role, other_account in accounts.items():
            if other_role == role:
                continue
            other_address = other_account.get("address")
            if other_address and other_address == address:
                raise OpsError(f"{role} must be separate from existing {other_role} account.")


def command_wallet_designation(args: argparse.Namespace) -> int:
    data = load_log()
    date = validate_date(args.date)
    proposed = {
        role: value.strip()
        for role, value in {
            "treasury": args.treasury,
            "grant": args.grant,
            "liquidity": args.liquidity,
        }.items()
        if value
    }

    current_wallet_status(data)
    if not proposed:
        print("\nPass --treasury, --grant, and/or --liquidity with public G... accounts to draft commands.")
        return 0

    validate_wallet_plan(data, proposed)
    print_heading("Review Commands")
    print("Run each command first as printed. Remove --dry-run only after review.")
    for role in CORE_ROLES:
        address = proposed.get(role)
        if address:
            print()
            print(f"# {role}")
            print(designation_command(role, address, date))

    print("\nAfter applying approved designations:")
    print("python3 tools/transparency_log.py validate")
    print("git diff data/transparency-log.json")
    return 0


def fetch_horizon_account(address: str) -> dict[str, Any]:
    url = f"{HORIZON_URL}/accounts/{address}"
    request = urllib.request.Request(url, headers={"User-Agent": "ogcoin-next-steps/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise OpsError(f"{address} is not funded on Stellar mainnet.") from exc
        raise OpsError(f"Horizon account check failed with HTTP {exc.code}.") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise OpsError(f"Horizon account check failed: {exc}") from exc


def summarize_balances(account: dict[str, Any]) -> tuple[str, str, bool]:
    native = "0"
    ogc = "0"
    has_ogc_trustline = False
    for balance in account.get("balances", []):
        if balance.get("asset_type") == "native":
            native = balance.get("balance", "0")
        if balance.get("asset_code") == ASSET_CODE and balance.get("asset_issuer") == ISSUER:
            ogc = balance.get("balance", "0")
            has_ogc_trustline = True
    return native, ogc, has_ogc_trustline


def command_liquidity_checklist(args: argparse.Namespace) -> int:
    data = load_log()
    date = validate_date(args.date)
    accounts = accounts_by_role(data)
    designated_wallet = accounts.get("liquidity", {}).get("address")
    wallet = args.wallet or designated_wallet

    print_heading("Tiny OGC/XLM Liquidity Checklist")
    print(f"Policy: {LIQUIDITY_POLICY_URL}")
    if not wallet:
        print("Blocked: no liquidity wallet is designated yet.")
        print("Run wallet-designation after choosing a separate public G... account.")
        return 1

    wallet = validate_public_account(wallet, "liquidity wallet")
    if wallet in {ISSUER, DISTRIBUTION_ACCOUNT}:
        raise OpsError("The liquidity wallet must be separate from issuer and distribution accounts.")
    if designated_wallet and wallet != designated_wallet:
        print(f"Warning: {wallet} is not the published liquidity wallet {designated_wallet}.")
    if not designated_wallet:
        print("Blocked: this wallet is not published in the transparency log as liquidity yet.")
        print("Designate it publicly before any market action.")
        return 1

    ogc_amount = parse_amount(args.ogc_amount, "--ogc-amount")
    xlm_exposure = parse_amount(args.xlm_exposure, "--xlm-exposure")

    print(f"Wallet: {wallet}")
    print(f"Maximum proposed test amount: {ogc_amount.normalize()} OGC")
    print(f"Maximum proposed XLM exposure: {xlm_exposure.normalize()} XLM")

    if args.online:
        account = fetch_horizon_account(wallet)
        native, ogc, has_ogc_trustline = summarize_balances(account)
        print(f"Live XLM balance: {native}")
        print(f"Live OGC balance: {ogc}")
        print(f"OGC trustline: {'yes' if has_ogc_trustline else 'no'}")
        if not has_ogc_trustline:
            print("Blocked: liquidity wallet needs an OGC trustline before it can hold or trade OGC.")

    print("\nPreconditions:")
    print("- Treasury/legal approval has named the maximum OGC and XLM exposure.")
    print("- Liquidity wallet is funded only with the approved tiny test amounts.")
    print("- Use one test path first: a small SDEX offer or a small liquidity-pool deposit, not both.")
    print("- Do not promote OGC as liquid, redeemable, or investment-like.")

    print("\nConservative first test:")
    print("- Use Stellar Lab on public network from the liquidity wallet.")
    print("- Create one Manage Sell Offer or Manage Buy Offer for OGC/XLM with the approved price and amount.")
    print("- Sign with the liquidity wallet only. Do not use the issuer for market activity.")
    print("- Submit, copy the transaction hash and ledger, then record it publicly.")

    print("\nPost-settlement record template:")
    print(
        shell_join(
            [
                "python3",
                "tools/transparency_log.py",
                "add",
                "--id",
                f"{date}-tiny-ogc-xlm-liquidity-test",
                "--date",
                date,
                "--category",
                "liquidity",
                "--status",
                "confirmed_on_chain",
                "--title",
                "Tiny OGC/XLM liquidity test",
                "--summary",
                "Executed a policy-limited tiny OGC/XLM liquidity test from the designated liquidity wallet.",
                "--account-role",
                "liquidity",
                "--account",
                wallet,
                "--amount-ogc",
                str(ogc_amount.normalize()),
                "--counter-asset",
                "XLM",
                "--tx",
                "TX_HASH",
                "--ledger",
                "LEDGER_NUMBER",
                "--link",
                LIQUIDITY_POLICY_URL,
                "--link",
                stellar_expert_tx_url_placeholder(),
                "--dry-run",
            ]
        )
    )
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare safe next-step OGCoin operations.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Show current wallet and action status")
    status_parser.set_defaults(func=command_status)

    campaign_parser = subparsers.add_parser("trustline-campaign", help="Print invite copy and validation path")
    campaign_parser.add_argument("--target", type=int, default=25, help="Tester trustline target. Default: 25")
    campaign_parser.add_argument("--amount", default="1", help="Default tiny test distribution amount. Default: 1")
    campaign_parser.set_defaults(func=command_trustline_campaign)

    wallet_parser = subparsers.add_parser("wallet-designation", help="Draft dry-run wallet designation commands")
    wallet_parser.add_argument("--treasury", help="Public treasury wallet address")
    wallet_parser.add_argument("--grant", help="Public grant wallet address")
    wallet_parser.add_argument("--liquidity", help="Public liquidity wallet address")
    wallet_parser.add_argument("--date", default=today(), help="Record date in YYYY-MM-DD format")
    wallet_parser.set_defaults(func=command_wallet_designation)

    liquidity_parser = subparsers.add_parser("liquidity-checklist", help="Check preconditions for a tiny OGC/XLM test")
    liquidity_parser.add_argument("--wallet", help="Public liquidity wallet address. Defaults to transparency log value.")
    liquidity_parser.add_argument("--ogc-amount", default="1", help="Maximum OGC test amount. Default: 1")
    liquidity_parser.add_argument("--xlm-exposure", default="1", help="Maximum XLM exposure. Default: 1")
    liquidity_parser.add_argument("--date", default=today(), help="Record date in YYYY-MM-DD format")
    liquidity_parser.add_argument("--online", action="store_true", help="Check live liquidity wallet balances on Horizon")
    liquidity_parser.set_defaults(func=command_liquidity_checklist)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        return args.func(args)
    except OpsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
