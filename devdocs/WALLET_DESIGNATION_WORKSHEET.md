# OGCoin Wallet Designation Worksheet

Last updated: 2026-05-22

Use this worksheet before publishing treasury, grant, distribution, or liquidity wallets. Record public account addresses only. Never paste secret keys, seed phrases, private payroll data, or personal recipient information into this repo.

## Required Roles

| Role | Purpose | Public address | Custody owner | Signer policy | Operating limit | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `treasury` | Holds reserves and funds approved programs | Pending | Pending | Pending | Pending | Pending |
| `grant` | Sends approved project grants or community allocations | Pending | Pending | Pending | Pending | Pending |
| `distribution` | Handles opt-in airdrops and small batch distributions | `GDD6IVZJVY3ZFWJ5T5BCZDURLF64ZTQJDDR5X5A7XEDJYTEC6ISDGWZB` | Pending | Pending | Pending | Designated |
| `liquidity` | Holds market-making funds or liquidity pool inventory | Pending | Pending | Pending | Pending | Pending |

## Approval Checklist

1. Generate or choose the public Stellar account for the role.
2. Confirm the account is controlled by the intended custodian and that the secret key is backed up outside this repository.
3. Define signer thresholds, recovery owners, and who can approve spending.
4. Define the maximum routine movement allowed without a new written approval.
5. Decide whether the role needs OGC trustlines, XLM reserves, or both.
6. Review the public policy text for the account role.
7. Publish the designation with `tools/transparency_log.py designate-account`.

## Suggested Initial Policies

### Treasury

Cold or low-frequency account for reserves and program funding. It should not be used for day-to-day airdrops, market making, or employee activity. Spending should require explicit project lead approval and a public transparency record.

### Grant

Account for approved open source grants, educational distributions, or community allocations. Each batch should have a public purpose, amount, recipient privacy review, and transaction hash after settlement.

### Distribution

Account for opt-in trustline-based airdrops and small community campaigns. It should use dry-run recipient validation before every batch and should avoid private payroll or personal data in public records.

### Liquidity

Account for tiny, policy-limited OGC/XLM offers or liquidity pool activity after legal and treasury review. Publish wallet address, starting exposure, maximum exposure, and reconciliation cadence before encouraging swaps.

## Publish Command Template

Run this first with `--dry-run`:

```bash
TREASURY_PUBLIC_KEY=G...PUBLIC_ACCOUNT

python3 tools/transparency_log.py designate-account \
  --role treasury \
  --address "$TREASURY_PUBLIC_KEY" \
  --date 2026-05-22 \
  --policy "Cold or low-frequency account for approved OGCoin treasury activity; no routine airdrops, payroll, or liquidity operations." \
  --summary "Designated the public treasury wallet for approved OGCoin reserve and program funding activity." \
  --dry-run
```

After review, remove `--dry-run`, then run:

```bash
python3 tools/transparency_log.py validate
```

Commit and push the resulting `data/transparency-log.json` update so the public transparency page reflects the designation.
