#!/usr/bin/env python3
"""Build and diagnose Stellar recovery/funding transactions for OGCoin.

This helper cannot bypass Stellar multisig. It can inspect signer thresholds,
build reviewable XDRs, add local signatures from environment variables, and
submit a fully signed XDR when explicitly requested.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from stellar_sdk import Asset, Keypair, Network, Server, TransactionBuilder, TransactionEnvelope
from stellar_sdk.exceptions import (
    AccountNotFoundException,
    BadRequestError,
    Ed25519PublicKeyInvalidError,
    Ed25519SecretSeedInvalidError,
    NotFoundError,
)
from stellar_sdk.strkey import StrKey


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRANSPARENCY_LOG = PROJECT_ROOT / "data" / "transparency-log.json"
DEFAULT_XDR_DIR = PROJECT_ROOT / ".ogcoin-xdr"

HORIZON_URL = "https://horizon.stellar.org"
NETWORK_PASSPHRASE = Network.PUBLIC_NETWORK_PASSPHRASE
ASSET_CODE = "OGC"
ISSUER = "GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57"

DEFAULT_ROLE_AMOUNTS = {
    "treasury": Decimal("0"),
    "grant": Decimal("3"),
    "liquidity": Decimal("5"),
}

MEDIUM_OPS = {
    "CreateAccount",
    "Payment",
    "PathPaymentStrictReceive",
    "PathPaymentStrictSend",
    "ManageSellOffer",
    "ManageBuyOffer",
    "CreatePassiveSellOffer",
    "ChangeTrust",
    "AllowTrust",
    "Clawback",
    "ClawbackClaimableBalance",
    "LiquidityPoolDeposit",
    "LiquidityPoolWithdraw",
}

HIGH_OPS = {
    "AccountMerge",
    "SetOptions",
    "BeginSponsoringFutureReserves",
    "EndSponsoringFutureReserves",
    "RevokeSponsorship",
    "SetTrustLineFlags",
}


class RecoveryError(ValueError):
    """Raised when a requested recovery action is unsafe or malformed."""


def server() -> Server:
    return Server(HORIZON_URL)


def validate_public_key(value: str, label: str = "account") -> str:
    value = (value or "").strip()
    if not StrKey.is_valid_ed25519_public_key(value):
        raise RecoveryError(f"{label} must be a valid Stellar public G... key.")
    return value


def validate_secret(value: str, label: str = "secret") -> str:
    value = (value or "").strip()
    if not StrKey.is_valid_ed25519_secret_seed(value):
        raise RecoveryError(f"{label} must be a valid Stellar secret S... key.")
    return value


def parse_amount(value: str | Decimal, label: str = "amount", *, allow_zero: bool = False) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise RecoveryError(f"{label} must be a decimal amount.") from exc
    if amount < 0 or (amount == 0 and not allow_zero):
        comparator = "zero or greater" if allow_zero else "greater than zero"
        raise RecoveryError(f"{label} must be {comparator}.")
    if amount.as_tuple().exponent < -7:
        raise RecoveryError(f"{label} cannot have more than 7 decimal places.")
    return amount


def amount_text(amount: Decimal) -> str:
    return format(amount.quantize(Decimal("0.0000001")).normalize(), "f")


def load_transparency_log(path: Path = TRANSPARENCY_LOG) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RecoveryError(f"Transparency log not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RecoveryError(f"Transparency log is not valid JSON: {exc}") from exc


def role_accounts() -> dict[str, str]:
    data = load_transparency_log()
    accounts = data.get("accounts", [])
    roles: dict[str, str] = {}
    for account in accounts:
        if not isinstance(account, dict):
            continue
        role = account.get("role")
        address = account.get("address")
        if role and address and role in DEFAULT_ROLE_AMOUNTS:
            roles[role] = validate_public_key(str(address), f"{role} address")
    return roles


def load_account_record(public_key: str) -> dict[str, Any]:
    try:
        return server().accounts().account_id(public_key).call()
    except (NotFoundError, AccountNotFoundException) as exc:
        raise RecoveryError(f"{public_key} is not funded on Stellar mainnet.") from exc


def account_exists(public_key: str) -> bool:
    try:
        load_account_record(public_key)
        return True
    except RecoveryError:
        return False


def native_balance(account: dict[str, Any]) -> Decimal:
    for balance in account.get("balances", []):
        if balance.get("asset_type") == "native":
            return Decimal(balance.get("balance", "0"))
    return Decimal("0")


def min_balance_estimate(account: dict[str, Any]) -> Decimal:
    # Stellar classic minimum balance is (2 + subentries + sponsored reserves
    # adjustments) * base reserve. Horizon exposes sponsor counts separately;
    # this estimate keeps a safety margin for recovery planning.
    subentries = Decimal(str(account.get("subentry_count", 0)))
    sponsoring = Decimal(str(account.get("num_sponsoring", 0)))
    sponsored = Decimal(str(account.get("num_sponsored", 0)))
    base_reserve = Decimal("0.5")
    reserve_units = Decimal("2") + subentries + sponsoring - sponsored
    if reserve_units < Decimal("2"):
        reserve_units = Decimal("2")
    return reserve_units * base_reserve


def signer_weights(account: dict[str, Any]) -> dict[str, int]:
    return {str(signer.get("key")): int(signer.get("weight", 0)) for signer in account.get("signers", [])}


def threshold_for(account: dict[str, Any], level: str) -> int:
    thresholds = account.get("thresholds", {})
    key = {
        "low": "low_threshold",
        "medium": "med_threshold",
        "high": "high_threshold",
    }[level]
    return int(thresholds.get(key, 0))


def available_weight(account: dict[str, Any], public_keys: list[str]) -> int:
    weights = signer_weights(account)
    return sum(weights.get(public_key, 0) for public_key in dict.fromkeys(public_keys))


def operation_threshold_level(operation_type: str) -> str:
    if operation_type in HIGH_OPS:
        return "high"
    if operation_type in MEDIUM_OPS:
        return "medium"
    return "medium"


def required_level_for_operations(operation_types: list[str]) -> str:
    return "high" if any(operation_threshold_level(op) == "high" for op in operation_types) else "medium"


def signer_public_keys_from_env(env_names: list[str]) -> list[str]:
    public_keys: list[str] = []
    for env_name in env_names:
        secret = os.getenv(env_name)
        if not secret:
            raise RecoveryError(f"Environment variable {env_name} is not set.")
        validate_secret(secret, env_name)
        public_keys.append(Keypair.from_secret(secret).public_key)
    return public_keys


def sign_transaction_from_env(envelope: TransactionEnvelope, env_names: list[str]) -> list[str]:
    signed_by: list[str] = []
    for env_name in env_names:
        secret = os.getenv(env_name)
        if not secret:
            raise RecoveryError(f"Environment variable {env_name} is not set.")
        validate_secret(secret, env_name)
        keypair = Keypair.from_secret(secret)
        envelope.sign(keypair)
        signed_by.append(keypair.public_key)
    return signed_by


def print_account_summary(account: dict[str, Any], signer_keys: list[str]) -> None:
    account_id = account["account_id"]
    balance = native_balance(account)
    min_balance = min_balance_estimate(account)
    spendable = balance - min_balance
    if spendable < 0:
        spendable = Decimal("0")

    print(f"Account: {account_id}")
    print(f"XLM balance: {amount_text(balance)}")
    print(f"Estimated minimum reserve: {amount_text(min_balance)}")
    print(f"Estimated spendable before fees: {amount_text(spendable)}")
    print(f"Subentries: {account.get('subentry_count', 0)}")
    print("Thresholds:")
    print(f"- low: {threshold_for(account, 'low')}")
    print(f"- medium: {threshold_for(account, 'medium')}")
    print(f"- high: {threshold_for(account, 'high')}")
    print("Signers:")
    for signer in account.get("signers", []):
        key = signer.get("key")
        marker = " (provided)" if key in signer_keys else ""
        print(f"- {key}: weight {signer.get('weight', 0)}{marker}")

    if signer_keys:
        medium_weight = available_weight(account, signer_keys)
        print("Provided signer weight:")
        print(f"- medium actions need {threshold_for(account, 'medium')}; provided weight is {medium_weight}")
        print(f"- high actions need {threshold_for(account, 'high')}; provided weight is {medium_weight}")
        if medium_weight < threshold_for(account, "medium"):
            missing = [
                signer.get("key")
                for signer in account.get("signers", [])
                if signer.get("key") not in signer_keys and int(signer.get("weight", 0)) > 0
            ]
            print("Result: not spendable with the provided signer key(s).")
            if missing:
                print("Missing useful signer(s):")
                for key in missing:
                    print(f"- {key}")
        else:
            print("Result: medium-threshold transactions should be signable with the provided signer key(s).")
    else:
        print("No signer secrets were provided, so this was an inspection only.")


def build_transaction(
    source_public: str,
    operation_specs: list[dict[str, str]],
    memo: str | None,
    signer_envs: list[str],
    base_fee: int,
) -> tuple[TransactionEnvelope, list[str], str, int, int]:
    source_public = validate_public_key(source_public, "source account")
    source_account = server().load_account(source_public)
    source_record = load_account_record(source_public)

    builder = TransactionBuilder(
        source_account=source_account,
        network_passphrase=NETWORK_PASSPHRASE,
        base_fee=base_fee,
    )
    if memo:
        builder.add_text_memo(memo[:28])

    operation_types: list[str] = []
    for spec in operation_specs:
        op_type = spec["type"]
        operation_types.append(op_type)
        if op_type == "CreateAccount":
            builder.append_create_account_op(
                destination=validate_public_key(spec["destination"], "destination"),
                starting_balance=spec["amount"],
            )
        elif op_type == "Payment":
            builder.append_payment_op(
                destination=validate_public_key(spec["destination"], "destination"),
                asset=Asset.native(),
                amount=spec["amount"],
            )
        elif op_type == "AccountMerge":
            builder.append_account_merge_op(destination=validate_public_key(spec["destination"], "destination"))
        else:
            raise RecoveryError(f"Unsupported operation type: {op_type}")

    envelope = builder.set_timeout(300).build()
    signed_by = sign_transaction_from_env(envelope, signer_envs) if signer_envs else []
    required_level = required_level_for_operations(operation_types)
    required_weight = threshold_for(source_record, required_level)
    provided_weight = available_weight(source_record, signed_by)
    return envelope, signed_by, required_level, required_weight, provided_weight


def write_xdr(envelope: TransactionEnvelope, stem: str, output_file: str | None) -> Path:
    if output_file:
        path = Path(output_file).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
    else:
        DEFAULT_XDR_DIR.mkdir(mode=0o700, exist_ok=True)
        stamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
        path = DEFAULT_XDR_DIR / f"{stamp}-{stem}.xdr"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(envelope.to_xdr() + "\n", encoding="utf-8")
    path.chmod(0o600)
    return path


def print_xdr_result(
    envelope: TransactionEnvelope,
    path: Path,
    signed_by: list[str],
    required_level: str,
    required_weight: int,
    provided_weight: int,
) -> None:
    print(f"Transaction hash: {envelope.hash_hex()}")
    print(f"XDR written to: {path}")
    print(f"Required threshold: {required_level} ({required_weight})")
    print(f"Provided signer weight: {provided_weight}")
    if signed_by:
        print("Signed by:")
        for public_key in signed_by:
            print(f"- {public_key}")
        if provided_weight < required_weight:
            print("Status: signed XDR is still under-authorized and will fail until more signer weight is added.")
        else:
            print("Status: signed XDR appears to have enough signer weight for this source account.")
    else:
        print("Status: unsigned XDR. Sign it with a wallet or rerun with --signer-secret-env.")


def command_inspect(args: argparse.Namespace) -> int:
    account_id = validate_public_key(args.account, "account")
    signer_keys = signer_public_keys_from_env(args.signer_secret_env)
    account = load_account_record(account_id)
    print_account_summary(account, signer_keys)
    return 0


def command_build_role_funding(args: argparse.Namespace) -> int:
    source = validate_public_key(args.source, "source account")
    roles = role_accounts()
    amounts = {
        "treasury": parse_amount(args.treasury_amount, "--treasury-amount", allow_zero=True),
        "grant": parse_amount(args.grant_amount, "--grant-amount", allow_zero=True),
        "liquidity": parse_amount(args.liquidity_amount, "--liquidity-amount", allow_zero=True),
    }

    operation_specs: list[dict[str, str]] = []
    for role in ("treasury", "grant", "liquidity"):
        amount = amounts[role]
        if amount == 0:
            continue
        destination = roles.get(role)
        if not destination:
            raise RecoveryError(f"No {role} account is published in the transparency log.")
        op_type = "Payment" if account_exists(destination) else "CreateAccount"
        operation_specs.append(
            {
                "type": op_type,
                "role": role,
                "destination": destination,
                "amount": amount_text(amount),
            }
        )

    if not operation_specs:
        raise RecoveryError("No funding operations requested. Set at least one role amount above zero.")

    print("Role funding operations:")
    for spec in operation_specs:
        action = "pay" if spec["type"] == "Payment" else "create"
        print(f"- {action} {spec['role']}: {spec['amount']} XLM -> {spec['destination']}")

    envelope, signed_by, required_level, required_weight, provided_weight = build_transaction(
        source_public=source,
        operation_specs=operation_specs,
        memo=args.memo,
        signer_envs=args.signer_secret_env,
        base_fee=args.base_fee,
    )
    path = write_xdr(envelope, "role-funding", args.output_file)
    print_xdr_result(envelope, path, signed_by, required_level, required_weight, provided_weight)
    if args.submit:
        submit_envelope(envelope)
    return 0


def command_build_drain(args: argparse.Namespace) -> int:
    source = validate_public_key(args.source, "source account")
    destination = validate_public_key(args.destination, "destination")
    account = load_account_record(source)
    balance = native_balance(account)
    estimated_min = min_balance_estimate(account)
    safety_reserve = parse_amount(args.reserve, "--reserve", allow_zero=True)

    operation_specs: list[dict[str, str]]
    if args.merge:
        if int(account.get("subentry_count", 0)) > 0:
            print("Warning: account_merge usually fails while the account has trustlines, offers, or other subentries.")
        operation_specs = [{"type": "AccountMerge", "destination": destination}]
        amount_info = "all remaining XLM if account_merge is allowed"
    else:
        if args.amount:
            payment_amount = parse_amount(args.amount, "--amount")
        else:
            payment_amount = balance - estimated_min - safety_reserve
            if payment_amount <= 0:
                raise RecoveryError(
                    "No safely spendable balance after estimated reserve. Pass --amount explicitly if you want to override."
                )
        operation_specs = [
            {
                "type": "Payment",
                "destination": destination,
                "amount": amount_text(payment_amount),
            }
        ]
        amount_info = f"{amount_text(payment_amount)} XLM"

    print(f"Drain operation: {source} -> {destination}")
    print(f"Amount: {amount_info}")
    print(f"Current balance: {amount_text(balance)} XLM")
    print(f"Estimated minimum reserve: {amount_text(estimated_min)} XLM")

    envelope, signed_by, required_level, required_weight, provided_weight = build_transaction(
        source_public=source,
        operation_specs=operation_specs,
        memo=args.memo,
        signer_envs=args.signer_secret_env,
        base_fee=args.base_fee,
    )
    path = write_xdr(envelope, "drain", args.output_file)
    print_xdr_result(envelope, path, signed_by, required_level, required_weight, provided_weight)
    if args.submit:
        submit_envelope(envelope)
    return 0


def read_xdr_arg(args: argparse.Namespace) -> str:
    if args.xdr and args.xdr_file:
        raise RecoveryError("Pass either --xdr or --xdr-file, not both.")
    if args.xdr:
        return args.xdr.strip()
    if args.xdr_file:
        return Path(args.xdr_file).expanduser().read_text(encoding="utf-8").strip()
    raise RecoveryError("Pass --xdr or --xdr-file.")


def command_sign_xdr(args: argparse.Namespace) -> int:
    xdr = read_xdr_arg(args)
    envelope = TransactionEnvelope.from_xdr(xdr, NETWORK_PASSPHRASE)
    signed_by = sign_transaction_from_env(envelope, args.signer_secret_env)
    path = write_xdr(envelope, "signed", args.output_file)
    print(f"Transaction hash: {envelope.hash_hex()}")
    print(f"Signed XDR written to: {path}")
    print("Signed by:")
    for public_key in signed_by:
        print(f"- {public_key}")
    if args.submit:
        submit_envelope(envelope)
    return 0


def submit_envelope(envelope: TransactionEnvelope) -> None:
    print("Submitting transaction to Stellar mainnet...")
    try:
        response = server().submit_transaction(envelope)
    except BadRequestError as exc:
        print("Submission failed.")
        extras = getattr(exc, "extras", None)
        if extras:
            print(json.dumps(extras, indent=2))
        raise
    print("Submission succeeded.")
    print(f"Hash: {response.get('hash')}")
    print(f"Ledger: {response.get('ledger')}")
    print(f"StellarExpert: https://stellar.expert/explorer/public/tx/{response.get('hash')}")


def command_submit_xdr(args: argparse.Namespace) -> int:
    xdr = read_xdr_arg(args)
    envelope = TransactionEnvelope.from_xdr(xdr, NETWORK_PASSPHRASE)
    submit_envelope(envelope)
    return 0


def add_common_build_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--signer-secret-env",
        action="append",
        default=[],
        help="Environment variable containing a local S... signer secret. May be repeated.",
    )
    parser.add_argument("--base-fee", type=int, default=100000, help="Base fee in stroops. Default: 100000.")
    parser.add_argument("--memo", help="Optional text memo. Stellar text memos are capped at 28 bytes.")
    parser.add_argument("--output-file", help="Where to write the XDR. Default: .ogcoin-xdr/<timestamp>-*.xdr")
    parser.add_argument("--submit", action="store_true", help="Submit the resulting signed XDR to mainnet.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnose and build Stellar recovery/funding XDRs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect an account's balances, signers, and thresholds.")
    inspect_parser.add_argument("--account", required=True, help="Public G... account to inspect.")
    inspect_parser.add_argument(
        "--signer-secret-env",
        action="append",
        default=[],
        help="Environment variable containing an S... signer secret to test. May be repeated.",
    )
    inspect_parser.set_defaults(func=command_inspect)

    role_parser = subparsers.add_parser("build-role-funding", help="Build XDR to fund designated OGC role wallets.")
    role_parser.add_argument("--source", required=True, help="Funding source public G... account.")
    role_parser.add_argument("--treasury-amount", default=str(DEFAULT_ROLE_AMOUNTS["treasury"]))
    role_parser.add_argument("--grant-amount", default=str(DEFAULT_ROLE_AMOUNTS["grant"]))
    role_parser.add_argument("--liquidity-amount", default=str(DEFAULT_ROLE_AMOUNTS["liquidity"]))
    add_common_build_args(role_parser)
    role_parser.set_defaults(func=command_build_role_funding)

    drain_parser = subparsers.add_parser("build-drain", help="Build XDR to move XLM out of an accessible account.")
    drain_parser.add_argument("--source", required=True, help="Source public G... account.")
    drain_parser.add_argument("--destination", required=True, help="Destination public G... account.")
    drain_parser.add_argument("--amount", help="XLM amount. Omit to estimate spendable balance.")
    drain_parser.add_argument("--reserve", default="1", help="Extra XLM safety reserve when --amount is omitted.")
    drain_parser.add_argument("--merge", action="store_true", help="Use account_merge instead of a payment.")
    add_common_build_args(drain_parser)
    drain_parser.set_defaults(func=command_build_drain)

    sign_parser = subparsers.add_parser("sign-xdr", help="Add local signatures to an existing XDR.")
    sign_parser.add_argument("--xdr", help="Transaction envelope XDR.")
    sign_parser.add_argument("--xdr-file", help="File containing transaction envelope XDR.")
    sign_parser.add_argument(
        "--signer-secret-env",
        action="append",
        required=True,
        help="Environment variable containing an S... signer secret. May be repeated.",
    )
    sign_parser.add_argument("--output-file", help="Where to write the signed XDR.")
    sign_parser.add_argument("--submit", action="store_true", help="Submit the signed XDR to mainnet.")
    sign_parser.set_defaults(func=command_sign_xdr)

    submit_parser = subparsers.add_parser("submit-xdr", help="Submit an already signed XDR to Stellar mainnet.")
    submit_parser.add_argument("--xdr", help="Transaction envelope XDR.")
    submit_parser.add_argument("--xdr-file", help="File containing transaction envelope XDR.")
    submit_parser.set_defaults(func=command_submit_xdr)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv or sys.argv[1:])
        return args.func(args)
    except (
        RecoveryError,
        Ed25519PublicKeyInvalidError,
        Ed25519SecretSeedInvalidError,
        BadRequestError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
