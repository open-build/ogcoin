#!/usr/bin/env python3
"""Send tiny OGC inventory from distribution to the liquidity wallet.

Secrets are read from local gitignored env files or environment variables and
are never printed. By default this writes a signed XDR for review; pass
--submit to broadcast.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

from stellar_sdk import Asset, Keypair, Network, Server, TransactionBuilder
from stellar_sdk.exceptions import BadRequestError, Ed25519SecretSeedInvalidError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILES = [
    PROJECT_ROOT / ".ogcoin-secrets" / "distribution.env",
    PROJECT_ROOT / ".ogcoin-secrets" / "role-wallets.env",
]
DEFAULT_XDR_DIR = PROJECT_ROOT / ".ogcoin-xdr"

HORIZON_URL = "https://horizon.stellar.org"
NETWORK_PASSPHRASE = Network.PUBLIC_NETWORK_PASSPHRASE
ASSET_CODE = "OGC"
ISSUER = "GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57"
DISTRIBUTION = "GDD6IVZJVY3ZFWJ5T5BCZDURLF64ZTQJDDR5X5A7XEDJYTEC6ISDGWZB"
LIQUIDITY = "GAL3OOPQRNZ3MFX3AUR45M7P2DBF5LWSH3XWFI5CN7SZEMQWLOOOCRRC"
POLICY_MAX_OGC = Decimal("1")


class InventoryError(ValueError):
    """Raised when an inventory movement request is unsafe or malformed."""


def parse_env_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise InventoryError(f"{path}:{line_number} is not KEY=VALUE format.")
        key, value = line.split("=", 1)
        key = key.strip()
        value = parse_env_value(value)
        if not key:
            raise InventoryError(f"{path}:{line_number} has an empty key.")
        if key not in os.environ and value:
            os.environ[key] = value


def parse_amount(value: str) -> Decimal:
    try:
        amount = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise InventoryError("--amount must be a decimal amount.") from exc
    if amount <= 0:
        raise InventoryError("--amount must be greater than zero.")
    if amount.as_tuple().exponent < -7:
        raise InventoryError("--amount cannot have more than 7 decimal places.")
    if amount > POLICY_MAX_OGC:
        raise InventoryError(f"--amount cannot exceed the published liquidity cap of {POLICY_MAX_OGC} OGC.")
    return amount


def amount_text(amount: Decimal) -> str:
    return format(amount.quantize(Decimal("0.0000001")).normalize(), "f")


def server() -> Server:
    return Server(HORIZON_URL)


def load_distribution_keypair() -> Keypair:
    secret = (os.getenv("OGC_DISTRIBUTION_SECRET") or "").strip()
    if not secret:
        raise InventoryError("OGC_DISTRIBUTION_SECRET is not set.")
    try:
        keypair = Keypair.from_secret(secret)
    except Ed25519SecretSeedInvalidError as exc:
        raise InventoryError("OGC_DISTRIBUTION_SECRET is not a valid Stellar S... secret.") from exc
    if keypair.public_key != DISTRIBUTION:
        raise InventoryError(
            f"OGC_DISTRIBUTION_SECRET derives {keypair.public_key}, but expected {DISTRIBUTION}."
        )
    return keypair


def ogc_balance(account_record: dict) -> tuple[Decimal | None, Decimal | None]:
    for balance in account_record.get("balances", []):
        if balance.get("asset_code") == ASSET_CODE and balance.get("asset_issuer") == ISSUER:
            return Decimal(balance.get("balance", "0")), Decimal(balance.get("limit", "0"))
    return None, None


def native_balance(account_record: dict) -> Decimal:
    for balance in account_record.get("balances", []):
        if balance.get("asset_type") == "native":
            return Decimal(balance.get("balance", "0"))
    return Decimal("0")


def write_xdr(envelope, output_dir: Path) -> Path:
    output_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = output_dir / f"{stamp}-liquidity-ogc-inventory.xdr"
    path.write_text(envelope.to_xdr() + "\n", encoding="utf-8")
    path.chmod(0o600)
    return path


def build_payment(amount: Decimal, memo: str, output_dir: Path, submit: bool) -> None:
    distribution_keypair = load_distribution_keypair()
    distribution_record = server().accounts().account_id(DISTRIBUTION).call()
    liquidity_record = server().accounts().account_id(LIQUIDITY).call()
    distribution_ogc, _ = ogc_balance(distribution_record)
    liquidity_ogc, liquidity_limit = ogc_balance(liquidity_record)

    if distribution_ogc is None:
        raise InventoryError("Distribution wallet does not have an OGC trustline.")
    if liquidity_ogc is None or liquidity_limit is None:
        raise InventoryError("Liquidity wallet does not have an OGC trustline.")
    if distribution_ogc < amount:
        raise InventoryError(f"Distribution wallet only has {amount_text(distribution_ogc)} OGC.")
    if liquidity_ogc + amount > liquidity_limit:
        raise InventoryError(
            f"Liquidity wallet limit is {amount_text(liquidity_limit)} OGC; "
            f"current balance {amount_text(liquidity_ogc)} plus {amount_text(amount)} would exceed it."
        )

    print(f"Distribution wallet: {DISTRIBUTION}")
    print(f"Liquidity wallet: {LIQUIDITY}")
    print(f"Amount: {amount_text(amount)} OGC")
    print(f"Distribution OGC balance before: {amount_text(distribution_ogc)}")
    print(f"Liquidity OGC balance before: {amount_text(liquidity_ogc)}")
    print(f"Liquidity XLM balance before: {amount_text(native_balance(liquidity_record))}")

    source_account = server().load_account(DISTRIBUTION)
    envelope = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .add_text_memo(memo[:28])
        .append_payment_op(destination=LIQUIDITY, asset=Asset(ASSET_CODE, ISSUER), amount=amount_text(amount))
        .set_timeout(300)
        .build()
    )
    envelope.sign(distribution_keypair)
    path = write_xdr(envelope, output_dir)

    print(f"Signed XDR: {path}")
    print(f"Transaction hash: {envelope.hash_hex()}")
    if not submit:
        print("Status: signed, not submitted. Rerun with --submit to broadcast.")
        return

    print("Submitting to Stellar mainnet...")
    try:
        response = server().submit_transaction(envelope)
    except BadRequestError as exc:
        print("Submission failed.")
        extras = getattr(exc, "extras", None)
        if extras:
            print(f"Horizon extras: {extras}")
        raise
    print("Submission succeeded.")
    print(f"Hash: {response.get('hash')}")
    print(f"Ledger: {response.get('ledger')}")
    print(f"StellarExpert: https://stellar.expert/explorer/public/tx/{response.get('hash')}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send policy-limited OGC inventory to the liquidity wallet.")
    parser.add_argument("--amount", default="1", help="OGC amount to send. Default and max: 1.")
    parser.add_argument("--memo", default="liquidity inventory", help="Text memo. Truncated to 28 bytes.")
    parser.add_argument(
        "--env-file",
        action="append",
        default=[],
        help="Local env file to load. Defaults to .ogcoin-secrets/distribution.env and role-wallets.env.",
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_XDR_DIR), help="Directory for signed XDR files.")
    parser.add_argument("--submit", action="store_true", help="Broadcast the signed payment transaction.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        env_files = [Path(path).expanduser() for path in args.env_file] if args.env_file else DEFAULT_ENV_FILES
        for env_file in env_files:
            if not env_file.is_absolute():
                env_file = Path.cwd() / env_file
            load_env_file(env_file)

        output_dir = Path(args.output_dir).expanduser()
        if not output_dir.is_absolute():
            output_dir = Path.cwd() / output_dir
        build_payment(parse_amount(args.amount), args.memo, output_dir, args.submit)
    except InventoryError as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
