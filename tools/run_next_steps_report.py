#!/usr/bin/env python3
"""Run OGCoin next-step checks and write a Markdown outcome report.

This script runs the current non-custodial OGCoin operator commands, captures
their outputs, and writes a concise report with blockers and reminders. It does
not read secret keys, sign transactions, submit XDR, or edit the transparency
log.
"""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "devdocs" / "NEXT_STEPS_OUTCOME.md"

EXPECTED_BLOCKERS = (
    "Blocked: no liquidity wallet is designated yet.",
    "Blocked: this wallet is not published in the transparency log as liquidity yet.",
)


@dataclass
class CommandResult:
    title: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    expected_blocker: bool = False

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0

    @property
    def failed_unexpectedly(self) -> bool:
        return self.returncode != 0 and not self.expected_blocker


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def shell_command(command: list[str]) -> str:
    return " ".join(command)


def run_command(title: str, command: list[str], *, allow_expected_blocker: bool = False) -> CommandResult:
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    combined = f"{completed.stdout}\n{completed.stderr}"
    expected_blocker = allow_expected_blocker and any(marker in combined for marker in EXPECTED_BLOCKERS)
    return CommandResult(
        title=title,
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
        expected_blocker=expected_blocker,
    )


def status_for(result: CommandResult) -> str:
    if result.succeeded:
        return "ok"
    if result.expected_blocker:
        return "blocked"
    return "failed"


def build_commands(args: argparse.Namespace) -> list[tuple[str, list[str], bool]]:
    py = sys.executable
    commands: list[tuple[str, list[str], bool]] = [
        ("Public legitimacy status", [py, "tools/ogcoin_console.py", "--check"], False),
        ("Transparency log validation", [py, "tools/transparency_log.py", "validate"], False),
        ("Public account roles", [py, "tools/transparency_log.py", "accounts"], False),
        ("Next-step status", [py, "tools/ogcoin_next_steps.py", "status"], False),
        (
            "Trustline campaign plan",
            [
                py,
                "tools/ogcoin_next_steps.py",
                "trustline-campaign",
                "--target",
                str(args.target),
                "--amount",
                args.amount,
            ],
            False,
        ),
    ]

    wallet_command = [py, "tools/ogcoin_next_steps.py", "wallet-designation", "--date", args.date]
    if args.treasury:
        wallet_command.extend(["--treasury", args.treasury])
    if args.grant:
        wallet_command.extend(["--grant", args.grant])
    if args.liquidity:
        wallet_command.extend(["--liquidity", args.liquidity])
    commands.append(("Wallet designation dry-run", wallet_command, False))

    liquidity_command = [
        py,
        "tools/ogcoin_next_steps.py",
        "liquidity-checklist",
        "--date",
        args.date,
        "--ogc-amount",
        args.ogc_amount,
        "--xlm-exposure",
        args.xlm_exposure,
    ]
    if args.liquidity:
        liquidity_command.extend(["--wallet", args.liquidity])
    if not args.skip_online:
        liquidity_command.append("--online")
    commands.append(("Tiny liquidity readiness", liquidity_command, True))

    return commands


def output_block(result: CommandResult) -> str:
    parts = [
        f"### {result.title}",
        "",
        f"- Status: `{status_for(result)}`",
        f"- Exit code: `{result.returncode}`",
        "",
        "Command:",
        "",
        "```bash",
        shell_command(result.command),
        "```",
        "",
    ]
    if result.stdout:
        parts.extend(["Output:", "", "```text", result.stdout, "```", ""])
    if result.stderr:
        parts.extend(["Errors:", "", "```text", result.stderr, "```", ""])
    return "\n".join(parts)


def build_report(args: argparse.Namespace, results: list[CommandResult]) -> str:
    unexpected_failures = [result for result in results if result.failed_unexpectedly]
    blocked = [result for result in results if result.expected_blocker]

    wallet_state = "provided" if any([args.treasury, args.grant, args.liquidity]) else "not provided"
    summary_status = "failed" if unexpected_failures else "blocked" if blocked else "ready for review"

    sections = [
        "# OGCoin Next Steps Outcome",
        "",
        f"Generated: `{now_utc()}`",
        f"Summary status: `{summary_status}`",
        f"Wallet addresses: `{wallet_state}`",
        "",
        "## Outcome Summary",
        "",
    ]

    for result in results:
        detail = "expected blocker" if result.expected_blocker else f"exit {result.returncode}"
        sections.append(f"- {result.title}: `{status_for(result)}` ({detail})")

    sections.extend(
        [
            "",
            "## Important Things To Remember",
            "",
            "- Collect public Stellar `G...` addresses only. Never collect secret keys, recovery phrases, or wallet passwords.",
            "- Do not use the issuer, distribution wallet, or personal issuer signer as treasury, grant, or liquidity operating wallets.",
            "- Treat trustline growth as opt-in testing. Avoid profit, redemption, guaranteed liquidity, salary value, or investment claims.",
            "- Keep OGC/XLM market activity blocked until the liquidity wallet is public, funded only within approved limits, and able to hold OGC.",
            "- Use one tiny liquidity test first: either one SDEX offer or one liquidity-pool deposit, not both at once.",
            "- Record every approved distribution, wallet designation, grant, treasury movement, and liquidity action in the transparency log.",
            "- Run dry-run commands first, review the diff, then commit and push public transparency updates.",
            "",
            "## Next Decisions",
            "",
            "1. Choose separate public `G...` accounts for treasury, grant, and liquidity.",
            "2. Send the trustline guide to 10-25 known testers and collect their public addresses.",
            "3. Validate tester addresses in the local console with online checks enabled.",
            "4. After the liquidity wallet is designated, rerun this report with `--liquidity G...`.",
            "",
            "## Command Results",
            "",
        ]
    )

    sections.extend(output_block(result) for result in results)
    return "\n".join(sections).rstrip() + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OGCoin next-step commands and document the outcome.")
    parser.add_argument("--target", type=int, default=25, help="Trustline tester target. Default: 25")
    parser.add_argument("--amount", default="1", help="Default tiny test distribution amount. Default: 1")
    parser.add_argument("--ogc-amount", default="1", help="Tiny liquidity OGC amount for checklist. Default: 1")
    parser.add_argument("--xlm-exposure", default="1", help="Tiny liquidity XLM exposure for checklist. Default: 1")
    parser.add_argument("--treasury", help="Optional public treasury wallet for wallet-designation dry run")
    parser.add_argument("--grant", help="Optional public grant wallet for wallet-designation dry run")
    parser.add_argument("--liquidity", help="Optional public liquidity wallet for wallet-designation and liquidity checks")
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="Record date in YYYY-MM-DD format")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help=f"Report path. Default: {DEFAULT_OUTPUT}")
    parser.add_argument("--skip-online", action="store_true", help="Skip live Horizon checks in the liquidity checklist")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when expected blockers are present")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    results = [
        run_command(title, command, allow_expected_blocker=allow_expected_blocker)
        for title, command, allow_expected_blocker in build_commands(args)
    ]
    report = build_report(args, results)
    output_path = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    print(f"Wrote {output_path}")
    for result in results:
        print(f"- {result.title}: {status_for(result)}")

    if any(result.failed_unexpectedly for result in results):
        return 1
    if args.strict and any(result.expected_blocker for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
