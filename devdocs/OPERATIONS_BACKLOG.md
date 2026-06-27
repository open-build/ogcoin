# OGCoin Operations Backlog

Last updated: 2026-06-27

This is the working list for getting OGCoin from "asset exists" to "credible, distributable, and responsibly tradable." Keep transaction signing, treasury movement, payroll decisions, and liquidity commitments behind explicit human approval.

## Current Status

- Public site: live at `https://www.opengreencoin.com/`.
- Sponsor: Open.Build, a nonprofit supporting open source projects and developer education.
- SEP-1 metadata: live at `https://www.opengreencoin.com/.well-known/stellar.toml`.
- Asset: `OGC:GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57`.
- Issuer `home_domain`: set to `www.opengreencoin.com` on-chain in ledger `62686761`.
- Issuer signer policy: hardened in transaction `f4deef4595aef811db59d173df37714b232886954b8dc885579b8a0095d12ca0`, ledger `62691902`; high-threshold issuer changes now require both issuer and personal signer.
- Distribution wallet: `GDD6IVZJVY3ZFWJ5T5BCZDURLF64ZTQJDDR5X5A7XEDJYTEC6ISDGWZB` designated for opt-in airdrops and reviewed distribution batches.
- Governance policy: interim issuer and treasury policy published at `https://www.opengreencoin.com/governance.html`.
- Transparency log: public page at `https://www.opengreencoin.com/transparency.html` with machine-readable records in `data/transparency-log.json`.
- Trustline guide: public onboarding page at `https://www.opengreencoin.com/trustline.html`.
- Liquidity policy: public guardrails page at `https://www.opengreencoin.com/liquidity-policy.html`.
- Impact checkout: static non-custodial checkout at `https://www.opengreencoin.com/checkout.html` with Freighter authorization and manual unsigned-XDR export.
- Sponsor disclosure: published in SEP-1 metadata, public trust/governance pages, and the transparency log.
- Treasury multisig preparation: guarded 2-of-3 workflow is implemented; Testnet rejected one signer and accepted all three two-signer combinations. Mainnet remains unchanged pending separate backup verification.
- Next-step runbook: `devdocs/NEXT_STEPS_RUNBOOK.md` with `tools/create_role_wallets.py`, `tools/ogcoin_next_steps.py`, and `tools/run_next_steps_report.py` for wallet generation, trustline, wallet, liquidity preparation, and outcome reporting.
- OGC/XLM order book: one policy-limited ask for `1 OGC` at `1 XLM`; no bids at last check.
- Liquidity pools: none at last check.
- Trustlines: 5 authorized accounts; adoption remains low and should grow slowly and transparently.
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
| Done | P1 | Publish trustline onboarding guide | Codex | `trustline.html` gives wallet-specific setup paths for LOBSTR, Freighter, StellarTerm, and Stellar Lab. |
| Done | P1 | Publish liquidity policy before market activity | Codex | `liquidity-policy.html` defines wallet, exposure, pause, and transparency requirements before OGC/XLM activity. |
| Done | P1 | Publish OpenGreenCoin Impact Policy v0.1 | Project lead + Codex | `impact-policy.html` and `data/impact-policy.json` define the disclosed 95/5 split for official routed OGC payments; peer-to-peer transfers are excluded. |
| Done | P1 | Add non-custodial impact payment builder | Codex | `tools/create_impact_payment_xdr.py` validates balances, trustlines, pilot caps, and creates an unsigned atomic two-payment XDR plus reconciliation manifest. |
| Done | P1 | Add next-step runbook and prep helper | Codex | `devdocs/NEXT_STEPS_RUNBOOK.md`, `tools/create_role_wallets.py`, `tools/ogcoin_next_steps.py`, and `tools/run_next_steps_report.py` turn wallet generation, trustline growth, wallet designation, liquidity readiness, and outcome reporting into repeatable local commands. |
| Done | P0 | Build guarded impact treasury multisig workflow | Codex | `tools/treasury_multisig.py` generates independent signers, enforces a local restore-check marker, and creates only unsigned Mainnet XDR artifacts. |
| Done | P0 | Rehearse treasury 2-of-3 recovery on Testnet | Codex | One signer was rejected with `op_bad_auth`; master+approval, master+recovery, and approval+recovery all succeeded. See `devdocs/TREASURY_MULTISIG_TESTNET_REPORT.md`. |
| Next | P0 | Review governance policy with counsel and project leadership | Project lead + counsel | Current issuer master signer is active. Avoid fixed-supply claims until signer hardening or stronger signed policy is complete. |
| Next | P0 | Back up and activate impact treasury multisig | Project lead + signer | Separately secure and restore-check the approval and recovery seeds, create the unsigned XDR, review it, then sign once with the current treasury key. Keep the 100 OGC caps until on-chain verification is published. |
| Done | P1 | Publish static impact checkout alongside ForgeWeb output | Codex | `checkout.html` displays the gross, recipient, contribution, treasury, reference, and refund terms; validates mainnet accounts and caps; and supports Freighter or unsigned-XDR authorization without a server. |
| Next | P1 | Add reviewed impact receipt import | Codex | Import signed transaction hashes and manifests into a public-safe reconciliation report without payer secrets or private customer data. |
| Done | P1 | Designate treasury, grant, and liquidity wallets | Project lead + Codex | All three public roles are published; treasury, grant, and liquidity wallets are active with bounded OGC trustlines. |
| Next | P1 | Grow opt-in trustlines to 10-25 testers | Project lead + Codex | Share `trustline.html`, collect public Stellar addresses only, then validate with the local console. |
| Next | P2 | Build recipient import workflow into console | Codex | Read Google Sheets CSV and produce validated local CSV for dry-run distribution. |
| Done | P2 | Add first wallet designation record | Codex + project lead | Treasury, grant, and liquidity designations and activation records are published in `data/transparency-log.json`. |

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
