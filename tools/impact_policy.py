#!/usr/bin/env python3
"""Load and calculate the OpenGreenCoin Impact Policy split."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_PATH = PROJECT_ROOT / "data" / "impact-policy.json"
STELLAR_QUANTUM = Decimal("0.0000001")


class ImpactPolicyError(ValueError):
    """Raised when policy data or an impact payment amount is invalid."""


def load_policy(path: Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ImpactPolicyError(f"Impact policy file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ImpactPolicyError(f"Impact policy file is invalid JSON: {exc}") from exc

    required = {
        "schema_version",
        "policy_version",
        "status",
        "effective_date",
        "policy_url",
        "asset",
        "routing",
        "included_flows",
        "excluded_flows",
        "eligible_uses",
        "required_disclosures",
        "restrictions",
    }
    missing = sorted(required - set(policy))
    if missing:
        raise ImpactPolicyError(f"Impact policy is missing keys: {', '.join(missing)}")

    routing = policy["routing"]
    for key in (
        "recipient_rate",
        "contribution_rate",
        "treasury",
        "maximum_gross_per_transaction_ogc",
        "maximum_pilot_treasury_balance_ogc",
    ):
        if key not in routing:
            raise ImpactPolicyError(f"Impact policy routing is missing {key}")

    recipient_rate = Decimal(str(routing["recipient_rate"]))
    contribution_rate = Decimal(str(routing["contribution_rate"]))
    if recipient_rate + contribution_rate != Decimal("1"):
        raise ImpactPolicyError("Recipient and contribution rates must total 1")
    if contribution_rate != Decimal("0.05"):
        raise ImpactPolicyError("Policy v0.1 contribution rate must be 0.05")
    return policy


def parse_stellar_amount(value: str, label: str = "amount") -> Decimal:
    try:
        amount = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ImpactPolicyError(f"{label} must be a decimal amount") from exc
    if not amount.is_finite() or amount <= 0:
        raise ImpactPolicyError(f"{label} must be greater than zero")
    if amount.as_tuple().exponent < -7:
        raise ImpactPolicyError(f"{label} cannot have more than 7 decimal places")
    return amount


def amount_text(amount: Decimal) -> str:
    return format(amount.quantize(STELLAR_QUANTUM).normalize(), "f")


def calculate_split(gross_value: str, policy: dict[str, Any]) -> dict[str, str]:
    gross = parse_stellar_amount(gross_value, "gross amount")
    routing = policy["routing"]
    max_gross = parse_stellar_amount(
        str(routing["maximum_gross_per_transaction_ogc"]),
        "maximum gross amount",
    )
    if gross > max_gross:
        raise ImpactPolicyError(
            f"gross amount exceeds the pilot limit of {amount_text(max_gross)} OGC"
        )

    contribution_rate = Decimal(str(routing["contribution_rate"]))
    contribution = (gross * contribution_rate).quantize(STELLAR_QUANTUM, rounding=ROUND_HALF_UP)
    if contribution < STELLAR_QUANTUM:
        raise ImpactPolicyError("gross amount is too small to produce a 5 percent Stellar payment")
    recipient = gross - contribution
    if recipient < STELLAR_QUANTUM:
        raise ImpactPolicyError("recipient amount would be below one Stellar stroop")

    return {
        "gross_amount": amount_text(gross),
        "recipient_amount": amount_text(recipient),
        "contribution_amount": amount_text(contribution),
        "recipient_rate": str(routing["recipient_rate"]),
        "contribution_rate": str(routing["contribution_rate"]),
    }
