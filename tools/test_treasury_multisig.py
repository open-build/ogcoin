#!/usr/bin/env python3

from __future__ import annotations

import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from stellar_sdk import Keypair

from treasury_multisig import (
    EXPECTED_THRESHOLDS,
    SignerKeys,
    TreasuryMultisigError,
    expected_signer_weights,
    load_signer_keys,
    policy_matches,
    require_backup_marker,
    secret_env_content,
    validate_reserve,
    verify_backup_seeds,
    write_backup_marker,
    write_private_file,
)


def account_data(source: str, approval: str, recovery: str) -> dict:
    return {
        "subentry_count": 2,
        "thresholds": dict(EXPECTED_THRESHOLDS),
        "signers": [
            {"key": source, "weight": 1, "type": "ed25519_public_key"},
            {"key": approval, "weight": 1, "type": "ed25519_public_key"},
            {"key": recovery, "weight": 1, "type": "ed25519_public_key"},
        ],
        "balances": [{"asset_type": "native", "balance": "5.0000000"}],
    }


class TreasuryMultisigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.keys = SignerKeys(
            approval=Keypair.random(),
            recovery=Keypair.random(),
            testnet_source=Keypair.random(),
        )

    def test_expected_policy_is_two_of_three(self) -> None:
        weights = expected_signer_weights(self.keys.testnet_source.public_key, self.keys)
        self.assertEqual(sum(weights.values()), 3)
        self.assertEqual(EXPECTED_THRESHOLDS["med_threshold"], 2)
        self.assertEqual(EXPECTED_THRESHOLDS["high_threshold"], 2)

    def test_policy_match_rejects_missing_recovery_signer(self) -> None:
        data = account_data(
            self.keys.testnet_source.public_key,
            self.keys.approval.public_key,
            self.keys.recovery.public_key,
        )
        self.assertTrue(policy_matches(data, self.keys.testnet_source.public_key, self.keys))
        data["signers"].pop()
        self.assertFalse(policy_matches(data, self.keys.testnet_source.public_key, self.keys))

    def test_reserve_check_allows_current_treasury_balance(self) -> None:
        data = {
            "subentry_count": 1,
            "balances": [{"asset_type": "native", "balance": "5.1292604"}],
        }
        self.assertEqual(validate_reserve(data, Decimal("0.5"), 2), Decimal("2.5"))

    def test_reserve_check_rejects_underfunded_account(self) -> None:
        data = {
            "subentry_count": 1,
            "balances": [{"asset_type": "native", "balance": "2.0"}],
        }
        with self.assertRaises(TreasuryMultisigError):
            validate_reserve(data, Decimal("0.5"), 2)

    def test_secret_file_round_trip_and_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "signers.env"
            write_private_file(path, secret_env_content(self.keys))
            loaded = load_signer_keys(path)
            self.assertEqual(loaded.approval.public_key, self.keys.approval.public_key)
            self.assertEqual(loaded.recovery.public_key, self.keys.recovery.public_key)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_backup_restore_check_and_marker(self) -> None:
        verify_backup_seeds(
            self.keys,
            self.keys.approval.secret,
            self.keys.recovery.secret,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            marker = Path(temp_dir) / "confirmed.json"
            write_backup_marker(marker, self.keys)
            data = require_backup_marker(marker, self.keys)
            self.assertEqual(data["approval_signer"], self.keys.approval.public_key)
            self.assertEqual(marker.stat().st_mode & 0o777, 0o600)

    def test_backup_restore_check_rejects_swapped_seeds(self) -> None:
        with self.assertRaises(TreasuryMultisigError):
            verify_backup_seeds(
                self.keys,
                self.keys.recovery.secret,
                self.keys.approval.secret,
            )


if __name__ == "__main__":
    unittest.main()
