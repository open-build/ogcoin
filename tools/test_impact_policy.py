#!/usr/bin/env python3
"""Unit tests for the OpenGreenCoin Impact Policy calculations."""

from __future__ import annotations

import unittest
from decimal import Decimal

from impact_policy import ImpactPolicyError, calculate_split, load_policy


class ImpactPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_policy()

    def test_policy_is_exactly_five_percent(self) -> None:
        self.assertEqual(self.policy["routing"]["contribution_rate"], "0.05")
        self.assertEqual(self.policy["routing"]["recipient_rate"], "0.95")

    def test_one_hundred_ogc_split(self) -> None:
        self.assertEqual(
            calculate_split("100", self.policy),
            {
                "gross_amount": "100",
                "recipient_amount": "95",
                "contribution_amount": "5",
                "recipient_rate": "0.95",
                "contribution_rate": "0.05",
            },
        )

    def test_split_conserves_stellar_amount(self) -> None:
        split = calculate_split("17.1234567", self.policy)
        self.assertEqual(
            Decimal(split["gross_amount"]),
            Decimal(split["recipient_amount"]) + Decimal(split["contribution_amount"]),
        )

    def test_rejects_amount_over_pilot_cap(self) -> None:
        with self.assertRaises(ImpactPolicyError):
            calculate_split("100.0000001", self.policy)

    def test_rejects_amount_too_small_for_contribution(self) -> None:
        with self.assertRaises(ImpactPolicyError):
            calculate_split("0.0000001", self.policy)


if __name__ == "__main__":
    unittest.main()
