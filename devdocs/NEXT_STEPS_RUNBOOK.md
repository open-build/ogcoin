# OGCoin Next Steps Runbook

Last updated: 2026-05-23

This runbook turns the current blockers into operator actions. It is intentionally conservative: collect public addresses only, keep secret keys out of the repo, and do not create OGC/XLM market activity until the liquidity wallet and exposure limit are public.

## 1. Build Trustlines Beyond 2

Goal: 10 to 25 known testers with active OGC trustlines before the next distribution batch.

1. Share the public guide: `https://www.opengreencoin.com/trustline.html`.
2. Ask testers for only their public Stellar `G...` address.
3. Do not collect secret keys, recovery phrases, private payroll data, or exchange deposit addresses unless the exchange clearly supports custom Stellar assets.
4. Paste collected rows into the local console recipient validator with online checks enabled.
5. Count only rows marked ready: account exists and has OGC trustline.

Helpful command:

```bash
python3 tools/ogcoin_next_steps.py trustline-campaign --target 25 --amount 1
```

CSV intake template:

```csv
address,amount,memo
G...PUBLIC_ACCOUNT,1,trustline-pilot
```

Validation command:

```bash
python3 tools/ogcoin_console.py
```

Open `http://localhost:8787/`, paste the CSV, enable online checks, and export the ready rows for dry-run review.

To run the command set and write the latest outcome:

```bash
python3 tools/run_next_steps_report.py
```

The report is written to `devdocs/NEXT_STEPS_OUTCOME.md`.

## 2. Designate Treasury, Grant, And Liquidity Wallets

Goal: three separate public Stellar accounts, each with a clear role and operating limit.

Do not use the issuer for operations. Do not reuse the distribution wallet. Your personal account can remain an issuer co-signer or recovery participant, but it should not be the public operating wallet for treasury, grant, or liquidity activity.

Recommended split:

| Role | Use | First requirement |
| --- | --- | --- |
| `treasury` | reserves and approved program funding | cold or low-frequency custody |
| `grant` | approved project/community disbursements | OGC trustline before grant sending |
| `liquidity` | tiny OGC/XLM test activity | OGC trustline, XLM reserve, public exposure cap |

Draft the transparency commands:

```bash
python3 tools/create_role_wallets.py

python3 tools/ogcoin_next_steps.py wallet-designation \
  --treasury G...TREASURY_PUBLIC \
  --grant G...GRANT_PUBLIC \
  --liquidity G...LIQUIDITY_PUBLIC
```

`create_role_wallets.py` writes public addresses to `devdocs/GENERATED_ROLE_WALLETS.md` and private seed keys to `.ogcoin-secrets/`. The seed file is gitignored, but it is still plaintext. Move those seeds into secure custody and delete the plaintext file.

The next-step helper prints `tools/transparency_log.py designate-account` commands with `--dry-run`. Run those first, review the proposed JSON, then remove `--dry-run` only after the wallet roles are approved.

After applying approved designations:

```bash
python3 tools/transparency_log.py validate
git diff data/transparency-log.json
```

Commit and push the transparency update so the public site shows the wallet roles.

## 3. Add Tiny OGC/XLM Liquidity

Goal: one tiny, documented test only after the liquidity wallet is public and funded with approved limits.

Preconditions:

1. Liquidity wallet is designated in `data/transparency-log.json`.
2. Liquidity wallet has enough XLM for reserve and fees.
3. Liquidity wallet has an OGC trustline.
4. Project leadership approves a maximum OGC amount, maximum XLM exposure, and test price/range.
5. The test is recorded after settlement with transaction hash and ledger.

Check readiness:

```bash
python3 tools/ogcoin_next_steps.py liquidity-checklist \
  --ogc-amount 1 \
  --xlm-exposure 1 \
  --online
```

Conservative first test:

1. Use Stellar Lab on public network.
2. Source account: designated liquidity wallet.
3. Operation: one small Manage Sell Offer or Manage Buy Offer for OGC/XLM.
4. Sign with the liquidity wallet only.
5. Submit, copy the transaction hash and ledger.
6. Record the action with `tools/transparency_log.py add`.

Do not create both an order-book offer and a liquidity-pool deposit at the same time. A pool deposit adds more moving parts because the wallet must handle reserve assets and a pool-share trustline.

## 4. Stop Conditions

Pause before any distribution or market action if:

- A tester sends a secret key or recovery phrase.
- A wallet address is not a Stellar public `G...` account.
- A role reuses the issuer or distribution wallet.
- The liquidity wallet is not published.
- The liquidity wallet lacks an OGC trustline.
- Legal, tax, payroll, or treasury review changes the approved scope.
- The transaction cannot be reconciled publicly.
