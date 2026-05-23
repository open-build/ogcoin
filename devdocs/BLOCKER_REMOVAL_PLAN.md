# OGCoin Blocker Removal Plan

Last updated: 2026-05-22

This plan turns the current warnings into small, reviewable actions. It is operational guidance, not legal, tax, investment, or payroll advice. Keep all signing and funding actions behind human approval.

## Blocker 1: Issuer Signer Hardening

Current state:

- Issuer: `GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57`
- Master signer weight: `1`
- Personal co-signer: `GBZAC66WWHFU2FEOG5KECSEVR6EJO7BYK63UGB52SENDN4JEJTJEVK5L`
- Low / medium / high thresholds: `1 / 2 / 2`
- Hardening transaction: `f4deef4595aef811db59d173df37714b232886954b8dc885579b8a0095d12ca0`, ledger `62691902`

Completed hardening step:

- Added the personal account as an issuer co-signer with weight `1`.
- Kept master weight at `1`.
- Set thresholds to `low=1`, `medium=2`, `high=2`.
- Treat this as 2-of-2 issuer control. This hardens governance, but it does not make the supply fixed.

Why this comes first:

- Stellar signer weights and thresholds are changed with `Set Options`.
- Signer and threshold updates are high-threshold operations.
- Future fixed-supply or issuer-lock claims should wait until the project approves whether to keep a multisig-controlled issuer or permanently lock the issuer.

Command template:

```bash
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

After the XDR is reviewed, sign it with the issuer account in Stellar Lab or an issuer-controlled wallet. After submission, verify with:

```bash
python3 tools/ogcoin_console.py --check
```

Then record the result:

```bash
python3 tools/transparency_log.py add \
  --id 2026-05-22-issuer-signer-hardening \
  --date 2026-05-22 \
  --category governance \
  --status confirmed_on_chain \
  --title "Issuer signer policy hardened" \
  --summary "Added approved issuer signers and updated signer thresholds for stronger OGC issuer governance." \
  --account-role issuer \
  --account GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57 \
  --tx TRANSACTION_HASH \
  --ledger LEDGER_NUMBER \
  --link https://stellar.expert/explorer/public/tx/TRANSACTION_HASH \
  --dry-run
```

## Blocker 2: Trustline Adoption

Current state:

- Only a small number of authorized trustlines are visible.
- The distribution wallet is designated, but recipient adoption is still low.

Next safe step:

- Share the published wallet-specific onboarding guide at `https://www.opengreencoin.com/trustline.html`.
- Use only utility language: no profit, guaranteed liquidity, redemption, or investment claims.
- Collect opt-in public Stellar addresses only.
- Validate every recipient with `tools/ogcoin_console.py` before distribution.

Minimum readiness target:

- 10 to 25 opt-in trustlines from known contributors or testers.
- One small reviewed distribution batch.
- A transparency entry for the batch after settlement.

## Blocker 3: Liquidity

Current state:

- OGC/XLM order book has no bids or asks.
- No OGC liquidity pools are observed.
- Payroll valuation remains blocked without a defensible market reference.

Next safe step:

- Do not create a public market until treasury limits and legal review are approved.
- Designate a separate liquidity wallet, not the distribution wallet.
- Use the published liquidity policy at `https://www.opengreencoin.com/liquidity-policy.html` to set maximum starting exposure, reconciliation cadence, and pause rules.
- Start only with a tiny test offer or tiny pool after approval.

Minimum readiness target:

- Public liquidity wallet designation.
- Public liquidity policy.
- One tiny OGC/XLM test path verified from at least two wallets.
- Transparency entry for the liquidity action after settlement.

## Order Of Work

1. Run a trustline onboarding campaign.
2. Designate treasury, grant, and liquidity wallets.
3. Create one tiny OGC/XLM test path only after liquidity wallet and limits are approved.
4. Record each approved distribution or liquidity action in the transparency log.
