#!/usr/bin/env python3
"""Create the first policy-limited OGC/XLM SDEX sell offer.

The liquidity secret is loaded from the local gitignored role-wallet env file.
The operator must provide an explicit XLM-per-OGC price. By default the helper
writes a signed XDR for review; pass --submit to broadcast.
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
DEFAULT_ENV_FILE = PROJECT_ROOT / ".ogcoin-secrets" / "role-wallets.env"
DEFAULT_XDR_DIR = PROJECT_ROOT / ".ogcoin-xdr"

HORIZON_URL = "https://horizon.stellar.org"
NETWORK_PASSPHRASE = Network.PUBLIC_NETWORK_PASSPHRASE
ASSET_CODE = "OGC"
ISSUER = "GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57"
LIQUIDITY = "GAL3OOPQRNZ3MFX3AUR45M7P2DBF5LWSH3XWFI5CN7SZEMQWLOOOCRRC"
MAX_OGC = Decimal("1")
MAX_XLM_EXPOSURE = Decimal("1")


class OfferError(ValueError):
    """Raised when an offer request is malformed or outside policy limits."""


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
            raise OfferError(f"{path}:{line_number} is not KEY=VALUE format.")
        key, value = line.split("=", 1)
        key = key.strip()
        value = parse_env_value(value)
        if not key:
            raise OfferError(f"{path}:{line_number} has an empty key.")
        if key not in os.environ and value:
            os.environ[key] = value


def parse_positive_decimal(value: str, label: str) -> Decimal:
    try:
        amount = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise OfferError(f"{label} must be a decimal amount.") from exc
    if amount <= 0:
        raise OfferError(f"{label} must be greater than zero.")
    if amount.as_tuple().exponent < -7:
        raise OfferError(f"{label} cannot have more than 7 decimal places.")
    return amount


def amount_text(amount: Decimal) -> str:
    return format(amount.quantize(Decimal("0.0000001")).normalize(), "f")


def server() -> Server:
    return Server(HORIZON_URL)


def load_liquidity_keypair() -> Keypair:
    secret = (os.getenv("OGC_LIQUIDITY_SECRET") or "").strip()
    if not secret:
        raise OfferError("OGC_LIQUIDITY_SECRET is not set.")
    try:
        keypair = Keypair.from_secret(secret)
    except Ed25519SecretSeedInvalidError as exc:
        raise OfferError("OGC_LIQUIDITY_SECRET is not a valid Stellar S... secret.") from exc
    if keypair.public_key != LIQUIDITY:
        raise OfferError(f"OGC_LIQUIDITY_SECRET derives {keypair.public_key}, but expected {LIQUIDITY}.")
    return keypair


def ogc_balance(account_record: dict) -> Decimal | None:
    for balance in account_record.get("balances", []):
        if balance.get("asset_code") == ASSET_CODE and balance.get("asset_issuer") == ISSUER:
            return Decimal(balance.get("balance", "0"))
    return None


def existing_offers() -> list[dict]:
    response = server().offers().for_account(LIQUIDITY).limit(20).call()
    return response.get("_embedded", {}).get("records", [])


def write_xdr(envelope, output_dir: Path) -> Path:
    output_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = output_dir / f"{stamp}-tiny-ogc-xlm-offer.xdr"
    path.write_text(envelope.to_xdr() + "\n", encoding="utf-8")
    path.chmod(0o600)
    return path


def build_offer(amount: Decimal, price: Decimal, memo: str, output_dir: Path, submit: bool) -> None:
    if amount > MAX_OGC:
        raise OfferError(f"--amount cannot exceed {MAX_OGC} OGC.")
    notional = amount * price
    if notional > MAX_XLM_EXPOSURE:
        raise OfferError(
            f"Offer notional is {amount_text(notional)} XLM and cannot exceed {MAX_XLM_EXPOSURE} XLM."
        )

    keypair = load_liquidity_keypair()
    account_record = server().accounts().account_id(LIQUIDITY).call()
    balance = ogc_balance(account_record)
    if balance is None:
        raise OfferError("Liquidity wallet does not have an OGC trustline.")
    if balance < amount:
        raise OfferError(f"Liquidity wallet only has {amount_text(balance)} OGC.")

    offers = existing_offers()
    if offers:
        raise OfferError(
            f"Liquidity wallet already has {len(offers)} open offer(s). "
            "Review or cancel them before creating the first-test offer."
        )

    print(f"Liquidity wallet: {LIQUIDITY}")
    print(f"Selling: {amount_text(amount)} OGC")
    print(f"Buying: XLM")
    print(f"Price: {amount_text(price)} XLM per OGC")
    print(f"Maximum proceeds/notional: {amount_text(notional)} XLM")
    print("Offer type: Manage Sell Offer")

    source_account = server().load_account(LIQUIDITY)
    envelope = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .add_text_memo(memo[:28])
        .append_manage_sell_offer_op(
            selling=Asset(ASSET_CODE, ISSUER),
            buying=Asset.native(),
            amount=amount_text(amount),
            price=amount_text(price),
        )
        .set_timeout(300)
        .build()
    )
    envelope.sign(keypair)
    path = write_xdr(envelope, output_dir)

    print(f"Signed XDR: {path}")
    print(f"Transaction hash: {envelope.hash_hex()}")
    if not submit:
        print("Status: signed, not submitted. Rerun with the same price and --submit to broadcast.")
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
    parser = argparse.ArgumentParser(description="Create one tiny policy-limited OGC/XLM sell offer.")
    parser.add_argument("--price-xlm", required=True, help="Explicit XLM price for one OGC.")
    parser.add_argument("--amount", default="1", help="OGC amount to sell. Default and max: 1.")
    parser.add_argument("--memo", default="OGC XLM test", help="Text memo. Truncated to 28 bytes.")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_FILE), help="Local role-wallet env file.")
    parser.add_argument("--output-dir", default=str(DEFAULT_XDR_DIR), help="Directory for signed XDR files.")
    parser.add_argument("--submit", action="store_true", help="Broadcast the signed offer transaction.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        env_file = Path(args.env_file).expanduser()
        if not env_file.is_absolute():
            env_file = Path.cwd() / env_file
        load_env_file(env_file)

        output_dir = Path(args.output_dir).expanduser()
        if not output_dir.is_absolute():
            output_dir = Path.cwd() / output_dir

        amount = parse_positive_decimal(args.amount, "--amount")
        price = parse_positive_decimal(args.price_xlm, "--price-xlm")
        build_offer(amount, price, args.memo, output_dir, args.submit)
    except OfferError as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
