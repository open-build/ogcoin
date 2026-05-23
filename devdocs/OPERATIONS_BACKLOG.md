# OGCoin Operations Backlog

Last updated: 2026-05-22

This is the working list for getting OGCoin from "asset exists" to "credible, distributable, and responsibly tradable." Keep transaction signing, treasury movement, payroll decisions, and liquidity commitments behind explicit human approval.

## Current Status

- Public site: live at `https://www.opengreencoin.com/`.
- SEP-1 metadata: live at `https://www.opengreencoin.com/.well-known/stellar.toml`.
- Asset: `OGC:GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57`.
- Issuer `home_domain`: set to `www.opengreencoin.com` on-chain in ledger `62686761`.
- Issuer signer policy: hardened in transaction `f4deef4595aef811db59d173df37714b232886954b8dc885579b8a0095d12ca0`, ledger `62691902`; high-threshold issuer changes now require both issuer and personal signer.
- Distribution wallet: `GDD6IVZJVY3ZFWJ5T5BCZDURLF64ZTQJDDR5X5A7XEDJYTEC6ISDGWZB` designated for opt-in airdrops and reviewed distribution batches.
- Governance policy: interim issuer and treasury policy published at `https://www.opengreencoin.com/governance.html`.
- Transparency log: public page at `https://www.opengreencoin.com/transparency.html` with machine-readable records in `data/transparency-log.json`.
- OGC/XLM order book: no bids or asks at last check.
- Liquidity pools: none at last check.
- Trustlines: low adoption; build slowly and transparently.
- Scheduled follow-up: active daily thread monitor for metadata, issuer state, liquidity, trustlines, and StellarExpert rating.

## Immediate Actions

| Status | Priority | Task | Owner | Notes |
| --- | --- | --- | --- | --- |
| Done | P0 | Sign and submit issuer `home_domain=www.opengreencoin.com` XDR | Human signer | Transaction `8b17b271d53bd8f9df817648acd3aa80169005d0be9a032bcbe7467c06f3eb01`, ledger `62686761`. |
| Done | P0 | Verify Horizon asset TOML link after `home_domain` lands | Codex/local console | `python3 tools/ogcoin_console.py --check` reports the issuer home domain as good. |
| Done | P1 | Draft public risk/disclosure page | Codex | `trust.html` covers verification, risk boundaries, governance status, liquidity readiness, and payroll limitations. |
| Done | P0 | Publish interim issuer and treasury governance policy | Codex | `governance.html` defines issuer, supply, signer, treasury, distribution, liquidity, and review guardrails. |
| Done | P2 | Add transparency report artifact | Codex | `transparency.html` renders `data/transparency-log.json` for public records and future batch logging. |
| Done | P2 | Add transparency log update helper | Codex | `tools/transparency_log.py` validates and appends reviewed records without signing or submitting transactions. |
| Done | P2 | Add wallet designation workflow | Codex | `devdocs/WALLET_DESIGNATION_WORKSHEET.md` and `tools/transparency_log.py designate-account` support public wallet role updates. |
| Done | P1 | Designate public distribution wallet | Project lead + Codex | `GDD6IVZJVY3ZFWJ5T5BCZDURLF64ZTQJDDR5X5A7XEDJYTEC6ISDGWZB` is published for opt-in airdrops and reviewed distribution batches only. |
| Done | P1 | Add blocker removal plan and issuer hardening XDR helper | Codex | `devdocs/BLOCKER_REMOVAL_PLAN.md` and `tools/create_issuer_signer_xdr.py` define the next signer, trustline, and liquidity path. |
| Done | P0 | Harden issuer signer policy | Human signer + Codex | Transaction `f4deef4595aef811db59d173df37714b232886954b8dc885579b8a0095d12ca0`, ledger `62691902`, set low `1`, medium `2`, high `2`, with issuer and personal signer weight `1` each. |
| Next | P0 | Review governance policy with counsel and project leadership | Project lead + counsel | Current issuer master signer is active. Avoid fixed-supply claims until signer hardening or stronger signed policy is complete. |
| Next | P1 | Designate treasury, grant, and liquidity wallets | Project lead | Choose public `G...` addresses, custody owners, signer thresholds, and routine movement limits using `devdocs/WALLET_DESIGNATION_WORKSHEET.md`. |
| Next | P1 | Draft trustline/onboarding campaign | Codex | Use copy from the local console and publish a clear wallet guide. |
| Next | P2 | Build recipient import workflow into console | Codex | Read Google Sheets CSV and produce validated local CSV for dry-run distribution. |
| Next | P2 | Add first wallet designation record | Codex + project lead | Use `tools/transparency_log.py designate-account` after a wallet role is approved. |

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

# Validate current public transparency records
python3 tools/transparency_log.py validate

# List public account roles
python3 tools/transparency_log.py accounts

# Draft a reviewed public transparency record without editing the file
python3 tools/transparency_log.py add \
  --id 2026-05-22-example-record \
  --date 2026-05-22 \
  --category policy \
  --status published \
  --title "Example record" \
  --summary "Short public summary with no private recipient or payroll data." \
  --link https://www.opengreencoin.com/transparency.html \
  --dry-run

# Draft an approved wallet designation without editing the file
TREASURY_PUBLIC_KEY=G...PUBLIC_ACCOUNT

python3 tools/transparency_log.py designate-account \
  --role treasury \
  --address "$TREASURY_PUBLIC_KEY" \
  --date 2026-05-22 \
  --policy "Cold or low-frequency account for approved OGCoin treasury activity; no routine airdrops, payroll, or liquidity operations." \
  --summary "Designated the public treasury wallet for approved OGCoin reserve and program funding activity." \
  --dry-run

# Generate a fresh unsigned home-domain transaction if the domain ever needs to change
python3 tools/create_home_domain_xdr.py \
  --issuer GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57 \
  --home-domain www.opengreencoin.com \
  --timeout 3600

# Draft an unsigned issuer signer hardening XDR after signer public keys are approved
SIGNER_A=G...PUBLIC_SIGNER_ONE
SIGNER_B=G...PUBLIC_SIGNER_TWO

python3 tools/create_issuer_signer_xdr.py \
  --signer "$SIGNER_A:1" \
  --signer "$SIGNER_B:1" \
  --master-weight 1 \
  --low-threshold 1 \
  --med-threshold 2 \
  --high-threshold 2
```
