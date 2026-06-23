#!/usr/bin/env python3
"""Create OGC trustlines for the public treasury, grant, and liquidity wallets.

Secrets are read from a local gitignored env file or environment variables and
are never printed. By default this writes signed XDR files for review; pass
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
DEFAULT_ENV_FILE = PROJECT_ROOT / ".ogcoin-secrets" / "role-wallets.env"
DEFAULT_XDR_DIR = PROJECT_ROOT / ".ogcoin-xdr"

HORIZON_URL = "https://horizon.stellar.org"
NETWORK_PASSPHRASE = Network.PUBLIC_NETWORK_PASSPHRASE
ASSET_CODE = "OGC"
ISSUER = "GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57"

ROLES = {
    "treasury": {
        "account": "GDMAMIC6SBYCF4NUQ6RBTUIFB5WWWS3TTDHXNCOUOLDFEPK5XOOU525F",
        "env": "OGC_TREASURY_SECRET",
        "limit": "100000",
    },
    "grant": {
        "account": "GAY2LYDC2YSAQ4VBQTG64LFZZHUB52UP3ACBTWLBWBDFBNH3ZCIWYFQV",
        "env": "OGC_GRANT_SECRET",
        "limit": "100000",
    },
    "liquidity": {
        "account": "GAL3OOPQRNZ3MFX3AUR45M7P2DBF5LWSH3XWFI5CN7SZEMQWLOOOCRRC",
        "env": "OGC_LIQUIDITY_SECRET",
        "limit": "1",
    },
}


class TrustlineError(ValueError):
    """Raised when a trustline setup request is malformed or unsafe."""


def decimal_text(value: str, label: str) -> str:
    try:
        amount = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise TrustlineError(f"{label} must be a decimal amount.") from exc
    if amount <= 0:
        raise TrustlineError(f"{label} must be greater than zero.")
    if amount.as_tuple().exponent < -7:
        raise TrustlineError(f"{label} cannot have more than 7 decimal places.")
    return format(amount.normalize(), "f")


def server() -> Server:
    return Server(HORIZON_URL)


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
            raise TrustlineError(f"{path}:{line_number} is not KEY=VALUE format.")
        key, value = line.split("=", 1)
        key = key.strip()
        value = parse_env_value(value)
        if not key:
            raise TrustlineError(f"{path}:{line_number} has an empty key.")
        if key not in os.environ and value:
            os.environ[key] = value


def account_has_trustline(account_record: dict) -> bool:
    return any(
        balance.get("asset_code") == ASSET_CODE and balance.get("asset_issuer") == ISSUER
        for balance in account_record.get("balances", [])
    )


def load_secret(env_name: str, expected_public: str) -> Keypair:
    secret = (os.getenv(env_name) or "").strip()
    if not secret:
        raise TrustlineError(f"{env_name} is not set.")
    try:
        keypair = Keypair.from_secret(secret)
    except Ed25519SecretSeedInvalidError as exc:
        raise TrustlineError(f"{env_name} is not a valid Stellar S... secret.") from exc
    if keypair.public_key != expected_public:
        raise TrustlineError(
            f"{env_name} derives {keypair.public_key}, but expected {expected_public}."
        )
    return keypair


def write_xdr(envelope, role: str, output_dir: Path) -> Path:
    output_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = output_dir / f"{stamp}-{role}-ogc-trustline.xdr"
    path.write_text(envelope.to_xdr() + "\n", encoding="utf-8")
    path.chmod(0o600)
    return path


def build_trustline(role: str, limit: str, base_fee: int, output_dir: Path, submit: bool) -> bool:
    config = ROLES[role]
    account_id = config["account"]
    env_name = config["env"]
    keypair = load_secret(env_name, account_id)
    account_record = server().accounts().account_id(account_id).call()

    print(f"{role}: {account_id}")
    if account_has_trustline(account_record):
        print("  OGC trustline already exists; skipping.")
        return False

    source_account = server().load_account(account_id)
    envelope = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=NETWORK_PASSPHRASE,
            base_fee=base_fee,
        )
        .append_change_trust_op(asset=Asset(ASSET_CODE, ISSUER), limit=limit)
        .set_timeout(300)
        .build()
    )
    envelope.sign(keypair)
    path = write_xdr(envelope, role, output_dir)

    print(f"  Limit: {limit} OGC")
    print(f"  Signed XDR: {path}")
    print(f"  Transaction hash: {envelope.hash_hex()}")
    if not submit:
        print("  Status: signed, not submitted. Rerun with --submit to broadcast.")
        return True

    print("  Submitting to Stellar mainnet...")
    try:
        response = server().submit_transaction(envelope)
    except BadRequestError as exc:
        print("  Submission failed.")
        extras = getattr(exc, "extras", None)
        if extras:
            print(f"  Horizon extras: {extras}")
        raise
    print("  Submission succeeded.")
    print(f"  Hash: {response.get('hash')}")
    print(f"  Ledger: {response.get('ledger')}")
    print(f"  StellarExpert: https://stellar.expert/explorer/public/tx/{response.get('hash')}")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add OGC trustlines to designated role wallets.")
    parser.add_argument(
        "roles",
        nargs="*",
        default=None,
        help="Role wallets to process. Defaults to treasury, grant, and liquidity.",
    )
    parser.add_argument(
        "--treasury-limit",
        default=ROLES["treasury"]["limit"],
        help="Treasury OGC trustline limit.",
    )
    parser.add_argument("--grant-limit", default=ROLES["grant"]["limit"], help="Grant OGC trustline limit.")
    parser.add_argument(
        "--liquidity-limit",
        default=ROLES["liquidity"]["limit"],
        help="Liquidity OGC trustline limit. Default is the tiny-test cap.",
    )
    parser.add_argument(
        "--env-file",
        default=str(DEFAULT_ENV_FILE),
        help="Local env file with OGC_TREASURY_SECRET, OGC_GRANT_SECRET, and OGC_LIQUIDITY_SECRET.",
    )
    parser.add_argument("--base-fee", type=int, default=100, help="Base fee in stroops. Default: 100.")
    parser.add_argument("--output-dir", default=str(DEFAULT_XDR_DIR), help="Directory for signed XDR files.")
    parser.add_argument("--submit", action="store_true", help="Broadcast signed trustline transactions to mainnet.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        env_file = Path(args.env_file).expanduser()
        if not env_file.is_absolute():
            env_file = Path.cwd() / env_file
        load_env_file(env_file)

        limits = {
            "treasury": decimal_text(args.treasury_limit, "--treasury-limit"),
            "grant": decimal_text(args.grant_limit, "--grant-limit"),
            "liquidity": decimal_text(args.liquidity_limit, "--liquidity-limit"),
        }
        output_dir = Path(args.output_dir).expanduser()
        if not output_dir.is_absolute():
            output_dir = Path.cwd() / output_dir

        changed = False
        roles = args.roles or sorted(ROLES)
        invalid_roles = [role for role in roles if role not in ROLES]
        if invalid_roles:
            valid = ", ".join(sorted(ROLES))
            raise TrustlineError(f"unknown role(s): {', '.join(invalid_roles)}. Valid roles: {valid}.")
        for role in roles:
            changed = build_trustline(role, limits[role], args.base_fee, output_dir, args.submit) or changed
    except TrustlineError as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0 if changed or args.roles else 0


if __name__ == "__main__":
    raise SystemExit(main())
