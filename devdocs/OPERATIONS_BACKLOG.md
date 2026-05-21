# OGCoin Operations Backlog

Last updated: 2026-05-21

This is the working list for getting OGCoin from "asset exists" to "credible, distributable, and responsibly tradable." Keep transaction signing, treasury movement, payroll decisions, and liquidity commitments behind explicit human approval.

## Current Status

- Public site: live at `https://www.opengreencoin.com/`.
- SEP-1 metadata: live at `https://www.opengreencoin.com/.well-known/stellar.toml`.
- Asset: `OGC:GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57`.
- Issuer `home_domain`: not set on-chain yet.
- OGC/XLM order book: no bids or asks at last check.
- Liquidity pools: none at last check.
- Trustlines: low adoption; build slowly and transparently.
- Scheduled follow-up: active daily thread monitor for metadata, issuer state, liquidity, trustlines, and StellarExpert rating.

## Immediate Actions

| Status | Priority | Task | Owner | Notes |
| --- | --- | --- | --- | --- |
| Next | P0 | Sign and submit issuer `home_domain=www.opengreencoin.com` XDR | Human signer | Regenerate the XDR immediately before signing because it is time-bounded. |
| Next | P0 | Verify Horizon asset TOML link after `home_domain` lands | Codex/local console | Run `python3 tools/ogcoin_console.py --check`. |
| Next | P0 | Decide issuer governance policy | Project lead + counsel | Current issuer master signer is active. Avoid fixed-supply claims until policy is signed/published. |
| Next | P1 | Create treasury/distribution account policy | Project lead | Define hot wallet, cold wallet, market-making wallet, grant wallet, and signer thresholds. |
| Next | P1 | Draft public risk/disclosure page | Codex | Make investor-style expectations explicitly out of scope. |
| Next | P1 | Draft trustline/onboarding campaign | Codex | Use copy from the local console and publish a clear wallet guide. |
| Next | P2 | Build recipient import workflow into console | Codex | Read Google Sheets CSV and produce validated local CSV for dry-run distribution. |
| Next | P2 | Add transparency report artifact | Codex | Generate public JSON/HTML showing treasury, grants, trustlines, and liquidity policy. |

## Liquidity Readiness

1. Decide whether OGC should trade before legal review is complete.
2. Define market-making limits, wallet address, and maximum exposure.
3. Start with tiny OGC/XLM offers or a small liquidity pool only after disclosures are live.
4. Publish the wallet address and policy before encouraging swaps.
5. Reconcile liquidity wallet balances weekly.

## Distribution Readiness

1. Keep airdrops opt-in and trustline-based.
2. Validate all addresses locally before any transaction.
3. Run dry-run reports before every distribution.
4. Use a distribution account, not the issuer, for regular payments.
5. Record every distribution batch with transaction hashes and purpose.

## Payroll Readiness

1. Do not use OGC as wage replacement until payroll counsel/tax review is complete.
2. If used earlier, treat OGC as a bonus/grant with written consent and USD value documentation.
3. Preserve required USD wages, withholding, FICA/FUTA, W-2 reporting, and state-law compliance.
4. Publish internal custody, valuation, and opt-in policy before any employee distribution.

## Recurring Operations

- Daily: Run public legitimacy monitor and note changes in this thread.
- Weekly: Review this backlog, update priorities, and pick the next three actions.
- Before every campaign: Run `python3 tools/ogcoin_console.py --check` and validate current trustline instructions.
- Before every distribution: Export validated recipients, run dry run, review treasury balances, then sign manually.

## Commands

```bash
# Local dashboard
python3 tools/ogcoin_console.py

# One-shot status report
python3 tools/ogcoin_console.py --check

# JSON status for other automation
python3 tools/ogcoin_console.py --check --format json

# Generate a fresh unsigned home-domain transaction
python3 tools/create_home_domain_xdr.py \
  --issuer GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57 \
  --home-domain www.opengreencoin.com
```
