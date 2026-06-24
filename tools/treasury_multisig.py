#!/usr/bin/env python3
"""Prepare and rehearse OGCoin impact treasury 2-of-3 multisig.

This workflow keeps generated seeds in a gitignored, owner-readable env file.
It can exercise the complete signer policy on Stellar Testnet and create an
unsigned Mainnet Set Options XDR. It never signs or submits Mainnet activity.
"""

from __future__ import annotations

import argparse
import datetime as dt
import getpass
import json
import os
import stat
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

try:
    from stellar_sdk import Asset, Keypair, Network, Server, Signer, TransactionBuilder
    from stellar_sdk.exceptions import BadRequestError, NotFoundError
    from stellar_sdk.strkey import StrKey
except ImportError:
    print("ERROR: stellar-sdk is required. Install with: pip install -r requirements.txt", file=sys.stderr)
    raise


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TREASURY = "GDMAMIC6SBYCF4NUQ6RBTUIFB5WWWS3TTDHXNCOUOLDFEPK5XOOU525F"

DEFAULT_SECRET_FILE = PROJECT_ROOT / ".ogcoin-secrets" / "treasury-multisig.env"
DEFAULT_BACKUP_MARKER = PROJECT_ROOT / ".ogcoin-secrets" / "treasury-multisig-backup-confirmed.json"
DEFAULT_PLAN_FILE = PROJECT_ROOT / "devdocs" / "TREASURY_MULTISIG_PLAN.md"
DEFAULT_TESTNET_REPORT = PROJECT_ROOT / "devdocs" / "TREASURY_MULTISIG_TESTNET_REPORT.md"
DEFAULT_XDR_DIR = PROJECT_ROOT / ".ogcoin-xdr"

APPROVAL_SECRET_ENV = "OGC_TREASURY_APPROVAL_SIGNER_SECRET"
RECOVERY_SECRET_ENV = "OGC_TREASURY_RECOVERY_SIGNER_SECRET"
TESTNET_SOURCE_SECRET_ENV = "OGC_TREASURY_TESTNET_SOURCE_SECRET"

PUBLIC_NETWORK = {
    "name": "public",
    "horizon": "https://horizon.stellar.org",
    "passphrase": Network.PUBLIC_NETWORK_PASSPHRASE,
}
TESTNET_NETWORK = {
    "name": "testnet",
    "horizon": "https://horizon-testnet.stellar.org",
    "passphrase": Network.TESTNET_NETWORK_PASSPHRASE,
}

EXPECTED_THRESHOLDS = {"low_threshold": 1, "med_threshold": 2, "high_threshold": 2}
EXPECTED_WEIGHT = 1


class TreasuryMultisigError(ValueError):
    """Raised when a treasury multisig action would be unsafe."""


@dataclass(frozen=True)
class SignerKeys:
    approval: Keypair
    recovery: Keypair
    testnet_source: Keypair


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def timestamp_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path


def validate_public_key(value: str, label: str) -> str:
    value = value.strip()
    if not StrKey.is_valid_ed25519_public_key(value):
        raise TreasuryMultisigError(f"{label} must be a valid Stellar public key")
    return value


def write_private_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, stat.S_IRUSR | stat.S_IWUSR)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(content)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def write_public_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        raise TreasuryMultisigError(f"Missing local signer file: {relative(path)}")

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        values[name.strip()] = value.strip().strip("\"'")
    return values


def keypair_from_env(values: dict[str, str], name: str) -> Keypair:
    secret = values.get(name, "")
    if not secret:
        raise TreasuryMultisigError(f"{name} is missing from the local signer file")
    try:
        return Keypair.from_secret(secret)
    except Exception as exc:
        raise TreasuryMultisigError(f"{name} is not a valid Stellar secret seed") from exc


def load_signer_keys(path: Path) -> SignerKeys:
    values = parse_env(path)
    keys = SignerKeys(
        approval=keypair_from_env(values, APPROVAL_SECRET_ENV),
        recovery=keypair_from_env(values, RECOVERY_SECRET_ENV),
        testnet_source=keypair_from_env(values, TESTNET_SOURCE_SECRET_ENV),
    )
    public_keys = {
        keys.approval.public_key,
        keys.recovery.public_key,
        keys.testnet_source.public_key,
    }
    if len(public_keys) != 3:
        raise TreasuryMultisigError("Approval, recovery, and Testnet source keys must all be distinct")
    if TREASURY in public_keys:
        raise TreasuryMultisigError("Generated signer keys must not reuse the production treasury account")
    return keys


def secret_env_content(keys: SignerKeys) -> str:
    return "\n".join(
        [
            "# OGCoin impact treasury multisig secrets.",
            "# Gitignored. Owner-readable only. Never commit, email, or paste these S... values.",
            "# Back up approval and recovery seeds in separate custody locations before Mainnet.",
            "",
            f"# Approval signer public key: {keys.approval.public_key}",
            f"{APPROVAL_SECRET_ENV}={keys.approval.secret}",
            "",
            f"# Recovery signer public key: {keys.recovery.public_key}",
            f"{RECOVERY_SECRET_ENV}={keys.recovery.secret}",
            "",
            f"# Testnet rehearsal source public key: {keys.testnet_source.public_key}",
            f"{TESTNET_SOURCE_SECRET_ENV}={keys.testnet_source.secret}",
            "",
        ]
    )


def plan_markdown(keys: SignerKeys, secret_file: Path) -> str:
    return "\n".join(
        [
            "# OGCoin Impact Treasury Multisig Plan",
            "",
            f"Generated: `{now_utc()}`",
            "",
            "Status: **Mainnet not changed. See the Testnet report for rehearsal status.**",
            "",
            "## Proposed 2-of-3 Policy",
            "",
            f"- Production treasury / master signer: `{TREASURY}` (weight 1)",
            f"- Approval signer: `{keys.approval.public_key}` (weight 1)",
            f"- Recovery signer: `{keys.recovery.public_key}` (weight 1)",
            "- Low threshold: `1`",
            "- Medium threshold: `2`",
            "- High threshold: `2`",
            "",
            "Any two of the three signers can authorize treasury payments or signer-policy changes. One signer alone cannot.",
            "",
            "## Custody Requirements",
            "",
            "1. Keep the treasury master seed, approval seed, and recovery seed in separate custody locations.",
            "2. Do not put all three seeds in one password-manager entry, computer, or physical envelope.",
            "3. Confirm the approval and recovery seeds can be restored before creating the Mainnet XDR.",
            "4. Record who may use each signer and under what approval process.",
            "5. Never use LOBSTR Vault or an unknown custom signer for this policy.",
            "",
            "## Local Secret File",
            "",
            f"The generated secrets are in the gitignored owner-readable file `{relative(secret_file)}`.",
            "Move the approval and recovery seeds into their separate durable custody locations. Delete the plaintext file only after the Mainnet transition and recovery materials have been independently verified.",
            "",
            "## Required Sequence",
            "",
            "1. Run the Testnet rehearsal and confirm all three signer pairs succeed.",
            "2. Back up and restore-check the approval and recovery seeds separately.",
            "3. Create the unsigned Mainnet XDR with the explicit backup acknowledgement.",
            "4. Review the exact signer addresses and thresholds in Stellar Lab.",
            "5. Sign with the current treasury master key and submit once.",
            "6. Verify the on-chain signer policy before receiving meaningful OGC.",
            "7. Publish the transaction hash and updated policy in the transparency log.",
            "",
        ]
    )


def generate(secret_file: Path, plan_file: Path) -> SignerKeys:
    if secret_file.exists():
        raise TreasuryMultisigError(
            f"{relative(secret_file)} already exists; refusing to rotate signer keys implicitly"
        )

    keys = SignerKeys(
        approval=Keypair.random(),
        recovery=Keypair.random(),
        testnet_source=Keypair.random(),
    )
    write_private_file(secret_file, secret_env_content(keys))
    write_public_file(plan_file, plan_markdown(keys, secret_file))
    return keys


def signer_weights(account_data: dict[str, Any]) -> dict[str, int]:
    return {
        signer["key"]: int(signer["weight"])
        for signer in account_data.get("signers", [])
        if signer.get("type") == "ed25519_public_key"
    }


def expected_signer_weights(source: str, keys: SignerKeys) -> dict[str, int]:
    return {
        source: EXPECTED_WEIGHT,
        keys.approval.public_key: EXPECTED_WEIGHT,
        keys.recovery.public_key: EXPECTED_WEIGHT,
    }


def policy_matches(account_data: dict[str, Any], source: str, keys: SignerKeys) -> bool:
    thresholds = account_data.get("thresholds", {})
    return (
        signer_weights(account_data) == expected_signer_weights(source, keys)
        and all(int(thresholds.get(name, -1)) == value for name, value in EXPECTED_THRESHOLDS.items())
    )


def stroops_to_xlm(value: int | str) -> Decimal:
    return Decimal(str(value)) / Decimal("10000000")


def native_balance(account_data: dict[str, Any]) -> Decimal:
    for balance in account_data.get("balances", []):
        if balance.get("asset_type") == "native":
            return Decimal(balance["balance"])
    return Decimal("0")


def latest_base_reserve(server: Server) -> Decimal:
    ledger = server.ledgers().order(desc=True).limit(1).call()["_embedded"]["records"][0]
    return stroops_to_xlm(ledger["base_reserve_in_stroops"])


def validate_reserve(account_data: dict[str, Any], base_reserve: Decimal, added_signers: int) -> Decimal:
    current_subentries = int(account_data.get("subentry_count", 0))
    future_minimum = Decimal(2 + current_subentries + added_signers) * base_reserve
    projected = native_balance(account_data) - Decimal("0.00003")
    if projected < future_minimum:
        raise TreasuryMultisigError(
            f"Account has {native_balance(account_data)} XLM; proposed signer entries need "
            f"about {future_minimum} XLM minimum balance"
        )
    return future_minimum


def append_policy_operations(builder: TransactionBuilder, keys: SignerKeys) -> TransactionBuilder:
    builder.append_set_options_op(
        signer=Signer.ed25519_public_key(keys.approval.public_key, EXPECTED_WEIGHT)
    )
    builder.append_set_options_op(
        signer=Signer.ed25519_public_key(keys.recovery.public_key, EXPECTED_WEIGHT)
    )
    builder.append_set_options_op(
        master_weight=EXPECTED_WEIGHT,
        low_threshold=EXPECTED_THRESHOLDS["low_threshold"],
        med_threshold=EXPECTED_THRESHOLDS["med_threshold"],
        high_threshold=EXPECTED_THRESHOLDS["high_threshold"],
    )
    return builder


def fund_testnet_account(public_key: str) -> None:
    url = f"https://friendbot.stellar.org/?addr={quote(public_key)}"
    request = Request(url, headers={"User-Agent": "OGCoin-Treasury-Multisig/0.1"})
    try:
        with urlopen(request, timeout=30) as response:
            if response.status >= 300:
                raise TreasuryMultisigError(f"Friendbot returned HTTP {response.status}")
    except HTTPError as exc:
        raise TreasuryMultisigError(f"Friendbot returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise TreasuryMultisigError(f"Friendbot request failed: {exc.reason}") from exc


def ensure_testnet_account(server: Server, keypair: Keypair) -> Any:
    try:
        return server.load_account(keypair.public_key)
    except NotFoundError:
        fund_testnet_account(keypair.public_key)
        return server.load_account(keypair.public_key)


def bad_auth_codes(error: BadRequestError) -> dict[str, Any]:
    extras = getattr(error, "extras", None)
    if isinstance(extras, dict):
        return extras.get("result_codes", {})
    response = getattr(error, "response", None)
    payload = getattr(response, "json", lambda: {})()
    return payload.get("extras", {}).get("result_codes", {}) if isinstance(payload, dict) else {}


def create_testnet_policy(server: Server, source: Keypair, keys: SignerKeys) -> str | None:
    account = ensure_testnet_account(server, source)
    account_data = account.raw_data

    if policy_matches(account_data, source.public_key, keys):
        transactions = (
            server.transactions()
            .for_account(source.public_key)
            .order(desc=False)
            .limit(20)
            .call()["_embedded"]["records"]
        )
        for transaction in transactions:
            operations = (
                server.operations()
                .for_transaction(transaction["hash"])
                .call()["_embedded"]["records"]
            )
            if [operation.get("type") for operation in operations] == [
                "set_options",
                "set_options",
                "set_options",
            ]:
                return transaction["hash"]
        return None

    current_weights = signer_weights(account_data)
    current_thresholds = account_data.get("thresholds", {})
    pristine = (
        current_weights == {source.public_key: 1}
        and all(int(current_thresholds.get(name, -1)) == 0 for name in EXPECTED_THRESHOLDS)
    )
    if not pristine:
        raise TreasuryMultisigError(
            "Testnet source already has an unexpected signer policy; generate a fresh signer file"
        )

    validate_reserve(account_data, latest_base_reserve(server), added_signers=2)
    builder = TransactionBuilder(
        source_account=account,
        network_passphrase=TESTNET_NETWORK["passphrase"],
        base_fee=100,
    )
    transaction = append_policy_operations(builder, keys).set_timeout(300).build()
    transaction.sign(source)
    result = server.submit_transaction(transaction)
    return result["hash"]


def build_self_payment(server: Server, source_public: str) -> Any:
    account = server.load_account(source_public)
    return (
        TransactionBuilder(
            source_account=account,
            network_passphrase=TESTNET_NETWORK["passphrase"],
            base_fee=100,
        )
        .append_payment_op(destination=source_public, amount="0.0000001", asset=Asset.native())
        .set_timeout(300)
        .build()
    )


def submit_pair_test(
    server: Server,
    source_public: str,
    pair_name: str,
    signers: list[Keypair],
) -> dict[str, str]:
    transaction = build_self_payment(server, source_public)
    for signer in signers:
        transaction.sign(signer)
    result = server.submit_transaction(transaction)
    return {"pair": pair_name, "hash": result["hash"], "ledger": str(result["ledger"])}


def prove_single_signer_rejected(
    server: Server,
    source: Keypair,
    approval: Keypair,
) -> dict[str, str]:
    transaction = build_self_payment(server, source.public_key)
    transaction.sign(source)
    try:
        server.submit_transaction(transaction)
    except BadRequestError as exc:
        codes = bad_auth_codes(exc)
        transaction_code = codes.get("transaction")
        operation_codes = codes.get("operations", [])
        rejected_for_auth = transaction_code == "tx_bad_auth" or (
            transaction_code == "tx_failed" and "op_bad_auth" in operation_codes
        )
        if not rejected_for_auth:
            raise TreasuryMultisigError(
                f"Single-signer rehearsal failed for an unexpected reason: {codes}"
            ) from exc
    else:
        raise TreasuryMultisigError("Single signer unexpectedly authorized a medium-threshold payment")

    transaction.sign(approval)
    result = server.submit_transaction(transaction)
    return {
        "pair": "master + approval",
        "hash": result["hash"],
        "ledger": str(result["ledger"]),
        "single_signer_result": "op_bad_auth",
    }


def testnet_report_markdown(
    keys: SignerKeys,
    setup_hash: str | None,
    pair_results: list[dict[str, str]],
    account_data: dict[str, Any],
) -> str:
    lines = [
        "# OGCoin Treasury Multisig Testnet Rehearsal",
        "",
        f"Completed: `{now_utc()}`",
        "",
        "Result: **PASS**",
        "",
        f"- Testnet source / master signer: `{keys.testnet_source.public_key}`",
        f"- Approval signer: `{keys.approval.public_key}`",
        f"- Recovery signer: `{keys.recovery.public_key}`",
        f"- Setup transaction: `{setup_hash or 'already configured in an earlier rehearsal'}`",
        "- Thresholds: low `1`, medium `2`, high `2`",
        "- Single signer payment result: `op_bad_auth` as expected",
        "",
        "## Successful Signer Pairs",
        "",
        "| Pair | Transaction hash | Ledger |",
        "| --- | --- | --- |",
    ]
    for result in pair_results:
        lines.append(f"| {result['pair']} | `{result['hash']}` | `{result['ledger']}` |")

    lines.extend(
        [
            "",
            "## Verified On-Chain Signers",
            "",
        ]
    )
    for public_key, weight in sorted(signer_weights(account_data).items()):
        lines.append(f"- `{public_key}`: weight `{weight}`")

    lines.extend(
        [
            "",
            "This rehearsal used Testnet XLM only. It did not sign or submit any Mainnet transaction.",
            "",
        ]
    )
    return "\n".join(lines)


def rehearse_testnet(secret_file: Path, report_file: Path) -> dict[str, Any]:
    keys = load_signer_keys(secret_file)
    server = Server(TESTNET_NETWORK["horizon"])
    setup_hash = create_testnet_policy(server, keys.testnet_source, keys)

    pair_results = [
        prove_single_signer_rejected(server, keys.testnet_source, keys.approval),
        submit_pair_test(
            server,
            keys.testnet_source.public_key,
            "master + recovery",
            [keys.testnet_source, keys.recovery],
        ),
        submit_pair_test(
            server,
            keys.testnet_source.public_key,
            "approval + recovery",
            [keys.approval, keys.recovery],
        ),
    ]

    final_account = server.load_account(keys.testnet_source.public_key).raw_data
    if not policy_matches(final_account, keys.testnet_source.public_key, keys):
        raise TreasuryMultisigError("Testnet signer policy does not match the proposed 2-of-3 plan")

    write_public_file(
        report_file,
        testnet_report_markdown(keys, setup_hash, pair_results, final_account),
    )
    return {
        "testnet_source": keys.testnet_source.public_key,
        "setup_hash": setup_hash,
        "pair_results": pair_results,
        "report": relative(report_file),
    }


def backup_marker_data(keys: SignerKeys) -> dict[str, str]:
    return {
        "schema_version": "0.1",
        "verified_at": now_utc(),
        "approval_signer": keys.approval.public_key,
        "recovery_signer": keys.recovery.public_key,
        "method": "secret seeds re-entered from separate backup copies and matched locally",
    }


def verify_backup_seeds(keys: SignerKeys, approval_seed: str, recovery_seed: str) -> None:
    try:
        approval = Keypair.from_secret(approval_seed.strip())
        recovery = Keypair.from_secret(recovery_seed.strip())
    except Exception as exc:
        raise TreasuryMultisigError("One or both backup values are not valid Stellar secret seeds") from exc

    if approval.public_key != keys.approval.public_key:
        raise TreasuryMultisigError("Approval backup does not match the planned approval signer")
    if recovery.public_key != keys.recovery.public_key:
        raise TreasuryMultisigError("Recovery backup does not match the planned recovery signer")
    if approval.public_key == recovery.public_key:
        raise TreasuryMultisigError("Approval and recovery backups must be different keys")


def write_backup_marker(path: Path, keys: SignerKeys) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(backup_marker_data(keys), indent=2)}\n", encoding="utf-8")
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def require_backup_marker(path: Path, keys: SignerKeys) -> dict[str, Any]:
    if not path.exists():
        raise TreasuryMultisigError(
            f"Missing backup verification marker {relative(path)}; run verify-backups first"
        )
    try:
        marker = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TreasuryMultisigError("Backup verification marker is unreadable") from exc
    if marker.get("approval_signer") != keys.approval.public_key:
        raise TreasuryMultisigError("Backup marker approval signer does not match the current plan")
    if marker.get("recovery_signer") != keys.recovery.public_key:
        raise TreasuryMultisigError("Backup marker recovery signer does not match the current plan")
    return marker


def build_mainnet_xdr(
    secret_file: Path,
    backup_marker: Path,
    output_dir: Path,
    timeout: int,
) -> tuple[Path, Path, dict[str, Any]]:
    keys = load_signer_keys(secret_file)
    backup_verification = require_backup_marker(backup_marker, keys)
    server = Server(PUBLIC_NETWORK["horizon"])
    try:
        account = server.load_account(TREASURY)
    except NotFoundError as exc:
        raise TreasuryMultisigError("Production treasury account does not exist on Mainnet") from exc

    account_data = account.raw_data
    if policy_matches(account_data, TREASURY, keys):
        raise TreasuryMultisigError("Production treasury already has the proposed multisig policy")

    current_weights = signer_weights(account_data)
    current_thresholds = account_data.get("thresholds", {})
    expected_current = {TREASURY: 1}
    if current_weights != expected_current or any(
        int(current_thresholds.get(name, -1)) != 0 for name in EXPECTED_THRESHOLDS
    ):
        raise TreasuryMultisigError(
            "Production treasury signer policy changed; inspect it before creating another XDR"
        )

    future_minimum = validate_reserve(
        account_data,
        latest_base_reserve(server),
        added_signers=2,
    )
    builder = TransactionBuilder(
        source_account=account,
        network_passphrase=PUBLIC_NETWORK["passphrase"],
        base_fee=100,
    )
    transaction = append_policy_operations(builder, keys).set_timeout(timeout).build()
    xdr = transaction.to_xdr()

    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{timestamp_utc()}-treasury-multisig"
    xdr_path = output_dir / f"{stem}.xdr.txt"
    manifest_path = output_dir / f"{stem}.json"
    xdr_path.write_text(f"{xdr}\n", encoding="utf-8")

    manifest = {
        "schema_version": "0.1",
        "created_at": now_utc(),
        "network": "Stellar Public Network",
        "source": TREASURY,
        "operations": [
            {"type": "set_options", "signer": keys.approval.public_key, "weight": 1},
            {"type": "set_options", "signer": keys.recovery.public_key, "weight": 1},
            {
                "type": "set_options",
                "master_weight": 1,
                "low_threshold": 1,
                "medium_threshold": 2,
                "high_threshold": 2,
            },
        ],
        "current_native_balance_xlm": str(native_balance(account_data)),
        "estimated_future_minimum_balance_xlm": str(future_minimum),
        "unsigned": True,
        "submitted": False,
        "backups_verified_at": backup_verification["verified_at"],
        "xdr_file": relative(xdr_path),
    }
    manifest_path.write_text(f"{json.dumps(manifest, indent=2)}\n", encoding="utf-8")
    return xdr_path, manifest_path, manifest


def inspect_account(network: dict[str, str], account_id: str) -> dict[str, Any]:
    account_id = validate_public_key(account_id, "account")
    server = Server(network["horizon"])
    try:
        account_data = server.accounts().account_id(account_id).call()
    except NotFoundError as exc:
        raise TreasuryMultisigError(f"Account not found on {network['name']}") from exc
    return {
        "network": network["name"],
        "account": account_id,
        "thresholds": account_data.get("thresholds", {}),
        "signers": signer_weights(account_data),
        "native_balance_xlm": str(native_balance(account_data)),
        "subentry_count": int(account_data.get("subentry_count", 0)),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--secret-file",
        type=Path,
        default=DEFAULT_SECRET_FILE,
        help=f"Gitignored signer env file. Default: {relative(DEFAULT_SECRET_FILE)}",
    )
    parser.add_argument(
        "--backup-marker",
        type=Path,
        default=DEFAULT_BACKUP_MARKER,
        help=f"Local backup verification marker. Default: {relative(DEFAULT_BACKUP_MARKER)}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Generate approval, recovery, and Testnet keys")
    generate_parser.add_argument("--plan-file", type=Path, default=DEFAULT_PLAN_FILE)

    rehearse_parser = subparsers.add_parser(
        "rehearse-testnet",
        help="Configure and prove the proposed 2-of-3 policy on Testnet",
    )
    rehearse_parser.add_argument("--report-file", type=Path, default=DEFAULT_TESTNET_REPORT)

    subparsers.add_parser(
        "verify-backups",
        help="Securely re-enter separately copied signer seeds and record a local confirmation",
    )

    mainnet_parser = subparsers.add_parser(
        "create-mainnet-xdr",
        help="Create an unsigned Mainnet hardening XDR after backup verification",
    )
    mainnet_parser.add_argument("--output-dir", type=Path, default=DEFAULT_XDR_DIR)
    mainnet_parser.add_argument("--timeout", type=int, default=3600)
    mainnet_parser.add_argument(
        "--confirm-separate-backups",
        action="store_true",
        help="Required acknowledgement that approval and recovery seeds were separately backed up and restore-checked",
    )

    inspect_parser = subparsers.add_parser("inspect", help="Inspect a public account signer policy")
    inspect_parser.add_argument("--network", choices=("public", "testnet"), default="public")
    inspect_parser.add_argument("--account", default=TREASURY)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    secret_file = resolve_path(args.secret_file)
    backup_marker = resolve_path(args.backup_marker)

    try:
        if args.command == "generate":
            plan_file = resolve_path(args.plan_file)
            keys = generate(secret_file, plan_file)
            print("Generated treasury multisig signer material.")
            print(f"Private signer file: {relative(secret_file)} (mode 600)")
            print(f"Public plan: {relative(plan_file)}")
            print(f"Approval signer: {keys.approval.public_key}")
            print(f"Recovery signer: {keys.recovery.public_key}")
            print("No Stellar account, transaction, or Mainnet state was changed.")
            return 0

        if args.command == "rehearse-testnet":
            report_file = resolve_path(args.report_file)
            result = rehearse_testnet(secret_file, report_file)
            print("Testnet 2-of-3 rehearsal passed.")
            print(f"Testnet source: {result['testnet_source']}")
            print(f"Report: {result['report']}")
            for pair in result["pair_results"]:
                print(f"- {pair['pair']}: {pair['hash']}")
            print("No Mainnet transaction was signed or submitted.")
            return 0

        if args.command == "verify-backups":
            keys = load_signer_keys(secret_file)
            print("Enter the approval seed from its separate backup copy.")
            approval_seed = getpass.getpass("Approval backup seed (hidden): ")
            print("Enter the recovery seed from its separate backup copy.")
            recovery_seed = getpass.getpass("Recovery backup seed (hidden): ")
            verify_backup_seeds(keys, approval_seed, recovery_seed)
            write_backup_marker(backup_marker, keys)
            print("Backup restore-check passed.")
            print(f"Local confirmation marker: {relative(backup_marker)}")
            print("No seed was printed or added to the confirmation marker.")
            return 0

        if args.command == "create-mainnet-xdr":
            if not args.confirm_separate_backups:
                raise TreasuryMultisigError(
                    "Refusing to create the Mainnet XDR until --confirm-separate-backups is provided"
                )
            if args.timeout < 60 or args.timeout > 86400:
                raise TreasuryMultisigError("timeout must be between 60 and 86400 seconds")
            xdr_path, manifest_path, manifest = build_mainnet_xdr(
                secret_file,
                backup_marker,
                resolve_path(args.output_dir),
                args.timeout,
            )
            print("Created unsigned Mainnet treasury multisig XDR.")
            print(f"XDR: {relative(xdr_path)}")
            print(f"Manifest: {relative(manifest_path)}")
            print(f"Approval signer: {manifest['operations'][0]['signer']}")
            print(f"Recovery signer: {manifest['operations'][1]['signer']}")
            print("This command did not sign or submit the transaction.")
            return 0

        network = PUBLIC_NETWORK if args.network == "public" else TESTNET_NETWORK
        print(json.dumps(inspect_account(network, args.account), indent=2, sort_keys=True))
        return 0
    except TreasuryMultisigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
