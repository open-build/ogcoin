#!/usr/bin/env python3
"""Create an unsigned XDR for OGC issuer signer and threshold hardening.

This script never asks for or handles secret keys. It builds a Set Options
transaction that must be reviewed, signed, and submitted by human signers.
"""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal

try:
    from stellar_sdk import Network, Server, Signer, TransactionBuilder
    from stellar_sdk.exceptions import NotFoundError
    from stellar_sdk.strkey import StrKey
except ImportError:
    print("stellar-sdk is required. Install with: pip install stellar-sdk", file=sys.stderr)
    raise


ISSUER = "GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57"

NETWORKS = {
    "public": {
        "horizon": "https://horizon.stellar.org",
        "passphrase": Network.PUBLIC_NETWORK_PASSPHRASE,
        "lab": "https://lab.stellar.org/transaction/sign",
    },
    "testnet": {
        "horizon": "https://horizon-testnet.stellar.org",
        "passphrase": Network.TESTNET_NETWORK_PASSPHRASE,
        "lab": "https://lab.stellar.org/transaction/sign",
    },
}


class SignerXdrError(ValueError):
    """Raised when a proposed signer hardening transaction is unsafe."""


def validate_public_key(value: str, label: str) -> str:
    value = value.strip()
    if not StrKey.is_valid_ed25519_public_key(value):
        raise SignerXdrError(f"{label} must be a valid Stellar public key")
    return value


def parse_weight(value: str) -> int:
    try:
        weight = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("weight must be an integer") from exc
    if weight < 0 or weight > 255:
        raise argparse.ArgumentTypeError("weight must be between 0 and 255")
    return weight


def parse_signer(value: str) -> tuple[str, int]:
    if ":" not in value:
        raise argparse.ArgumentTypeError("signer must use PUBLIC_KEY:WEIGHT")
    public_key, raw_weight = value.rsplit(":", 1)
    try:
        return validate_public_key(public_key, "signer public key"), parse_weight(raw_weight)
    except SignerXdrError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def stroops_to_xlm(value: int | str) -> Decimal:
    return Decimal(str(value)) / Decimal("10000000")


def native_balance(account_data: dict) -> Decimal:
    for balance in account_data.get("balances", []):
        if balance.get("asset_type") == "native":
            return Decimal(balance["balance"])
    return Decimal("0")


def signer_map(account_data: dict) -> dict[str, int]:
    return {
        signer["key"]: int(signer["weight"])
        for signer in account_data.get("signers", [])
        if signer.get("type") == "ed25519_public_key"
    }


def latest_base_reserve(server: Server) -> Decimal:
    ledger = server.ledgers().order(desc=True).limit(1).call()["_embedded"]["records"][0]
    return stroops_to_xlm(ledger["base_reserve_in_stroops"])


def future_signers(
    account_data: dict,
    issuer: str,
    proposed_signers: list[tuple[str, int]],
    master_weight: int | None,
) -> dict[str, int]:
    weights = signer_map(account_data)
    if master_weight is not None:
        weights[issuer] = master_weight
    for public_key, weight in proposed_signers:
        weights[public_key] = weight
    return {key: weight for key, weight in weights.items() if weight > 0}


def new_signer_count(account_data: dict, issuer: str, proposed_signers: list[tuple[str, int]]) -> int:
    current = signer_map(account_data)
    count = 0
    for public_key, weight in proposed_signers:
        if public_key == issuer:
            continue
        if weight > 0 and current.get(public_key, 0) == 0:
            count += 1
    return count


def threshold_values(account_data: dict, args: argparse.Namespace) -> dict[str, int]:
    current = account_data.get("thresholds", {})
    return {
        "low": args.low_threshold if args.low_threshold is not None else int(current.get("low_threshold", 0)),
        "medium": args.med_threshold if args.med_threshold is not None else int(current.get("med_threshold", 0)),
        "high": args.high_threshold if args.high_threshold is not None else int(current.get("high_threshold", 0)),
    }


def validate_plan(
    account_data: dict,
    issuer: str,
    proposed_signers: list[tuple[str, int]],
    args: argparse.Namespace,
    base_reserve: Decimal,
) -> tuple[dict[str, int], Decimal, Decimal]:
    weights = future_signers(account_data, issuer, proposed_signers, args.master_weight)
    total_weight = sum(weights.values())
    thresholds = threshold_values(account_data, args)

    if not args.allow_lockout and total_weight == 0:
        raise SignerXdrError("Proposed signer weights would leave the issuer with no usable signer")

    for label, threshold in thresholds.items():
        if threshold < 0 or threshold > 255:
            raise SignerXdrError(f"{label} threshold must be between 0 and 255")
        if threshold > total_weight and not args.allow_lockout:
            raise SignerXdrError(
                f"{label} threshold {threshold} exceeds future signer weight {total_weight}; "
                "pass --allow-lockout only for an intentional irreversible lock"
            )

    added_signers = new_signer_count(account_data, issuer, proposed_signers)
    current_subentries = int(account_data.get("subentry_count", 0))
    future_min_balance = Decimal(2 + current_subentries + added_signers) * base_reserve
    available_balance = native_balance(account_data)
    projected_after_fee = available_balance - Decimal("0.00001")
    if projected_after_fee < future_min_balance:
        raise SignerXdrError(
            f"Issuer has about {available_balance} XLM; adding {added_signers} signer(s) "
            f"needs roughly {future_min_balance} XLM minimum balance"
        )

    return weights, available_balance, future_min_balance


def append_set_options(builder: TransactionBuilder, args: argparse.Namespace) -> TransactionBuilder:
    for public_key, weight in args.signer:
        builder.append_set_options_op(signer=Signer.ed25519_public_key(public_key, weight))

    if any(
        value is not None
        for value in (args.master_weight, args.low_threshold, args.med_threshold, args.high_threshold)
    ):
        builder.append_set_options_op(
            master_weight=args.master_weight,
            low_threshold=args.low_threshold,
            med_threshold=args.med_threshold,
            high_threshold=args.high_threshold,
        )
    return builder


def build_signer_xdr(args: argparse.Namespace) -> tuple[str, dict[str, int], Decimal, Decimal]:
    issuer = validate_public_key(args.issuer, "issuer")
    network_config = NETWORKS[args.network]
    server = Server(network_config["horizon"])
    try:
        source_account = server.load_account(issuer)
    except NotFoundError as exc:
        raise SignerXdrError(f"Issuer account not found on {args.network}") from exc

    account_data = source_account.raw_data
    base_reserve = latest_base_reserve(server)
    weights, available_balance, future_min_balance = validate_plan(
        account_data=account_data,
        issuer=issuer,
        proposed_signers=args.signer,
        args=args,
        base_reserve=base_reserve,
    )

    transaction_builder = TransactionBuilder(
        source_account=source_account,
        network_passphrase=network_config["passphrase"],
        base_fee=100,
    )
    append_set_options(transaction_builder, args)
    transaction = transaction_builder.set_timeout(args.timeout).build()
    return transaction.to_xdr(), weights, available_balance, future_min_balance


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create an unsigned Set Options XDR for issuer signer and threshold hardening."
    )
    parser.add_argument("--issuer", default=ISSUER, help="Issuer public key")
    parser.add_argument("--network", choices=sorted(NETWORKS), default="public")
    parser.add_argument(
        "--signer",
        action="append",
        type=parse_signer,
        default=[],
        help="Signer public key and weight as PUBLIC_KEY:WEIGHT. Repeat for multiple signers.",
    )
    parser.add_argument("--master-weight", type=parse_weight, help="Future master key weight")
    parser.add_argument("--low-threshold", type=parse_weight, help="Future low threshold")
    parser.add_argument("--med-threshold", type=parse_weight, help="Future medium threshold")
    parser.add_argument("--high-threshold", type=parse_weight, help="Future high threshold")
    parser.add_argument("--timeout", type=int, default=3600, help="Transaction timeout in seconds")
    parser.add_argument(
        "--allow-lockout",
        action="store_true",
        help="Allow a plan where thresholds exceed available signer weight. Use only for intentional lockout.",
    )
    args = parser.parse_args()

    if not args.signer and all(
        value is None
        for value in (args.master_weight, args.low_threshold, args.med_threshold, args.high_threshold)
    ):
        print("ERROR: provide at least one --signer or threshold/master-weight option", file=sys.stderr)
        return 1

    try:
        xdr, weights, available_balance, future_min_balance = build_signer_xdr(args)
    except SignerXdrError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("Unsigned XDR:")
    print(xdr)
    print()
    print("Planned future signer weights:")
    for public_key, weight in sorted(weights.items()):
        print(f"- {public_key}: {weight}")
    print()
    print(f"Issuer native balance: {available_balance} XLM")
    print(f"Estimated minimum balance after signer changes: {future_min_balance} XLM")
    print()
    print("Next step:")
    print("Review the signer set, sign with currently authorized issuer signer(s), then submit.")
    print(f"Stellar Lab signer: {NETWORKS[args.network]['lab']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
