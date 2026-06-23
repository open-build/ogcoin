#!/usr/bin/env python3
"""Build an unsigned atomic 95/5 OGC impact payment for human review."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from decimal import Decimal
from pathlib import Path

from stellar_sdk import Asset, Keypair, Network, Server, TransactionBuilder

from impact_policy import (
    DEFAULT_POLICY_PATH,
    ImpactPolicyError,
    amount_text,
    calculate_split,
    load_policy,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / ".ogcoin-xdr"
HORIZON_URL = "https://horizon.stellar.org"
NETWORK_PASSPHRASE = Network.PUBLIC_NETWORK_PASSPHRASE
ISSUER = "GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57"
REFERENCE_RE = re.compile(r"^[A-Za-z0-9._-]{1,20}$")
FLOW_TYPES = {
    "official_app_checkout",
    "official_campaign",
    "official_marketplace",
    "official_sponsorship",
}


class ImpactPaymentError(ImpactPolicyError):
    """Raised when an impact payment cannot be built safely."""


def validate_public_key(value: str, label: str) -> str:
    try:
        return Keypair.from_public_key(value).public_key
    except Exception as exc:
        raise ImpactPaymentError(f"{label} is not a valid Stellar G... account") from exc


def find_ogc_balance(account: dict) -> dict | None:
    for balance in account.get("balances", []):
        if balance.get("asset_code") == "OGC" and balance.get("asset_issuer") == ISSUER:
            return balance
    return None


def find_native_balance(account: dict) -> Decimal:
    for balance in account.get("balances", []):
        if balance.get("asset_type") == "native":
            return Decimal(balance["balance"])
    return Decimal("0")


def require_authorized_trustline(account: dict, label: str) -> dict:
    balance = find_ogc_balance(account)
    if balance is None:
        raise ImpactPaymentError(f"{label} does not have an OGC trustline")
    if not balance.get("is_authorized", True):
        raise ImpactPaymentError(f"{label} OGC trustline is not authorized")
    return balance


def available_ogc(balance: dict) -> Decimal:
    return Decimal(balance["balance"]) - Decimal(balance.get("selling_liabilities", "0"))


def receiving_capacity(balance: dict) -> Decimal:
    return (
        Decimal(balance["limit"])
        - Decimal(balance["balance"])
        - Decimal(balance.get("buying_liabilities", "0"))
    )


def minimum_native_balance(account: dict, base_reserve: Decimal) -> Decimal:
    reserve_units = (
        Decimal("2")
        + Decimal(str(account.get("subentry_count", 0)))
        + Decimal(str(account.get("num_sponsoring", 0)))
        - Decimal(str(account.get("num_sponsored", 0)))
    )
    return reserve_units * base_reserve


def write_outputs(envelope, manifest: dict, output_dir: Path, reference: str) -> tuple[Path, Path]:
    output_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = f"{stamp}-{reference}-impact-payment"
    xdr_path = output_dir / f"{stem}.xdr"
    manifest_path = output_dir / f"{stem}.json"
    xdr_path.write_text(envelope.to_xdr() + "\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    xdr_path.chmod(0o600)
    manifest_path.chmod(0o600)
    return xdr_path, manifest_path


def build_payment(args: argparse.Namespace) -> None:
    policy_path = Path(args.policy).expanduser()
    if not policy_path.is_absolute():
        policy_path = Path.cwd() / policy_path
    policy = load_policy(policy_path)

    if policy["status"] != "pilot":
        raise ImpactPaymentError("impact routing is not in pilot status")
    if args.flow_type not in policy["included_flows"] or args.flow_type not in FLOW_TYPES:
        raise ImpactPaymentError(f"flow type is not included in policy v{policy['policy_version']}")
    if not REFERENCE_RE.fullmatch(args.reference):
        raise ImpactPaymentError(
            "reference must be 1-20 ASCII letters, numbers, periods, underscores, or hyphens"
        )

    source = validate_public_key(args.source, "source")
    recipient = validate_public_key(args.recipient, "recipient")
    treasury = validate_public_key(policy["routing"]["treasury"], "impact treasury")
    if source == recipient:
        raise ImpactPaymentError("source and recipient must be different accounts")
    if source in {ISSUER, treasury}:
        raise ImpactPaymentError("issuer and impact treasury cannot be routed-payment sources")
    if recipient in {ISSUER, treasury}:
        raise ImpactPaymentError("issuer and impact treasury cannot be routed-payment recipients")

    split = calculate_split(args.gross_amount, policy)
    gross = Decimal(split["gross_amount"])
    contribution = Decimal(split["contribution_amount"])

    server = Server(HORIZON_URL)
    source_record = server.accounts().account_id(source).call()
    recipient_record = server.accounts().account_id(recipient).call()
    treasury_record = server.accounts().account_id(treasury).call()

    source_ogc = require_authorized_trustline(source_record, "source")
    recipient_ogc = require_authorized_trustline(recipient_record, "recipient")
    treasury_ogc = require_authorized_trustline(treasury_record, "impact treasury")
    if available_ogc(source_ogc) < gross:
        raise ImpactPaymentError(
            f"source has only {amount_text(available_ogc(source_ogc))} available OGC"
        )
    recipient_amount = Decimal(split["recipient_amount"])
    if receiving_capacity(recipient_ogc) < recipient_amount:
        raise ImpactPaymentError("recipient OGC trustline does not have enough receiving capacity")

    treasury_balance = Decimal(treasury_ogc["balance"])
    treasury_limit = Decimal(treasury_ogc["limit"])
    pilot_cap = Decimal(str(policy["routing"]["maximum_pilot_treasury_balance_ogc"]))
    if contribution > min(receiving_capacity(treasury_ogc), pilot_cap - treasury_balance):
        raise ImpactPaymentError(
            "impact contribution would exceed the treasury trustline or pilot balance cap"
        )

    latest_ledger = server.ledgers().order(desc=True).limit(1).call()["_embedded"]["records"][0]
    base_reserve = Decimal(latest_ledger["base_reserve_in_stroops"]) / Decimal("10000000")
    base_fee = max(100, server.fetch_base_fee())
    estimated_fee = Decimal(base_fee * 2) / Decimal("10000000")
    required_xlm = minimum_native_balance(source_record, base_reserve) + estimated_fee
    if find_native_balance(source_record) < required_xlm:
        raise ImpactPaymentError("source does not have enough spendable XLM for reserves and fees")

    memo = f"impact:{args.reference}"
    expires_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=15)
    envelope = (
        TransactionBuilder(
            source_account=server.load_account(source),
            network_passphrase=NETWORK_PASSPHRASE,
            base_fee=base_fee,
        )
        .add_text_memo(memo)
        .append_payment_op(
            destination=recipient,
            asset=Asset("OGC", ISSUER),
            amount=split["recipient_amount"],
        )
        .append_payment_op(
            destination=treasury,
            asset=Asset("OGC", ISSUER),
            amount=split["contribution_amount"],
        )
        .set_timeout(900)
        .build()
    )

    manifest = {
        "policy_version": policy["policy_version"],
        "policy_url": policy["policy_url"],
        "network": "mainnet",
        "flow_type": args.flow_type,
        "reference": args.reference,
        "memo": memo,
        "source": source,
        "recipient": recipient,
        "impact_treasury": treasury,
        "asset_code": "OGC",
        "asset_issuer": ISSUER,
        **split,
        "operation_count": 2,
        "transaction_hash": envelope.hash_hex(),
        "expires_at": expires_at.replace(microsecond=0).isoformat(),
        "status": "unsigned_not_submitted",
    }
    output_dir = Path(args.output_dir).expanduser()
    if not output_dir.is_absolute():
        output_dir = Path.cwd() / output_dir
    xdr_path, manifest_path = write_outputs(envelope, manifest, output_dir, args.reference)

    print(f"Policy: OpenGreenCoin Impact Policy v{policy['policy_version']} ({policy['status']})")
    print(f"Flow: {args.flow_type}")
    print(f"Reference: {args.reference}")
    print(f"Gross: {split['gross_amount']} OGC")
    print(f"Recipient: {split['recipient_amount']} OGC -> {recipient}")
    print(f"Impact contribution: {split['contribution_amount']} OGC -> {treasury}")
    print("Direct peer-to-peer transfers are not affected.")
    print(f"Unsigned XDR: {xdr_path}")
    print(f"Manifest: {manifest_path}")
    print(f"Transaction hash: {envelope.hash_hex()}")
    print(f"Expires at: {manifest['expires_at']}")
    print("Status: unsigned and not submitted. Review the manifest, then import the XDR into a trusted signer.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an unsigned atomic OGC payment with a disclosed 95/5 impact split."
    )
    parser.add_argument("--source", required=True, help="Payer public G... account")
    parser.add_argument("--recipient", required=True, help="Recipient public G... account")
    parser.add_argument("--gross-amount", required=True, help="Total OGC authorized by the payer")
    parser.add_argument("--flow-type", required=True, choices=sorted(FLOW_TYPES))
    parser.add_argument("--reference", required=True, help="Public-safe reconciliation reference")
    parser.add_argument("--policy", default=str(DEFAULT_POLICY_PATH), help="Impact policy JSON")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Local XDR output directory")
    return parser.parse_args()


def main() -> int:
    try:
        build_payment(parse_args())
    except ImpactPolicyError as exc:
        print(f"ERROR: {exc}")
        return 1
    except Exception as exc:
        print(f"ERROR: unable to build impact payment: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
