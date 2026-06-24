# OGCoin Impact Checkout Runbook

Last updated: 2026-06-24

## Architecture

ForgeWeb remains the local CMS and static-site editor. `checkout.html` is a static
browser application published with the rest of the site by GitHub Pages.

There is no payment server and no site-held wallet:

1. The browser reads public account data from Stellar Horizon.
2. The browser validates the payer, recipient, treasury, trustlines, balances,
   reserves, and Impact Policy v0.1 pilot caps.
3. The browser builds one transaction with two OGC payment operations.
4. Freighter signs with the payer's selected account, or the payer exports an
   unsigned XDR for another signing tool.
5. Only a fully signed transaction is submitted to Stellar.

Secret keys must never be entered into the site, ForgeWeb, source files, query
parameters, logs, or support messages.

## Local Development

Install pinned dependencies and verify the checkout:

```bash
npm install
npm run check
```

The source files are:

- `src/impact-checkout.js`
- `src/impact-math.js`
- `css/impact-checkout.css`
- `checkout.html`

`npm run build` writes the committed browser bundle to
`js/impact-checkout.js`. GitHub Actions rebuilds it and fails deployment if the
committed bundle is stale.

Preview through the existing static server:

```text
http://127.0.0.1:8765/checkout.html
```

## Supported Authorization Paths

### Freighter

1. Switch Freighter to Stellar Mainnet.
2. Open `checkout.html` and connect the payer account.
3. Enter an approved recipient, gross amount, official flow, and public-safe
   reference.
4. Review the displayed 95/5 split and refund terms.
5. Prepare the transaction.
6. Verify both operations in Freighter before signing.
7. Download the JSON receipt after Stellar accepts the transaction.

The checkout does not submit anything until the payer explicitly signs.

### Manual XDR

1. Select **Manual XDR**.
2. Enter the payer public G-address only.
3. Complete the payment details and prepare the transaction.
4. Copy or download the unsigned XDR.
5. Sign and submit it with a trusted Stellar wallet or signing tool within 15
   minutes.

Preparing another transaction from the same payer may consume the same sequence
number and invalidate the older unsigned XDR.

## Link Parameters

Approved applications and campaigns may prefill public values:

```text
checkout.html?recipient=G...&amount=10&flow=official_campaign&reference=campaign-001
```

Supported `flow` values:

- `official_app_checkout`
- `official_campaign`
- `official_marketplace`
- `official_sponsorship`

Prefilling never bypasses review, account validation, policy caps, or wallet
authorization.

## Current Safeguards

- Stellar Public Network only.
- OGC issuer is fixed in the bundled configuration.
- Gross payment maximum is 100 OGC.
- Impact treasury balance maximum is 100 OGC.
- Recipient receives 95%; treasury receives 5%; any stroop rounding remainder
  stays with the recipient.
- Payer must have enough available OGC and XLM above reserve.
- Recipient and treasury must have authorized OGC trustlines with capacity.
- Issuer and impact treasury cannot be selected as the recipient.
- Public memo references are limited to 20 safe characters.
- Both payments are atomic operations in one Stellar transaction.
- Direct peer-to-peer transfers remain outside this checkout and are not taxed.

Do not raise the pilot caps until treasury multisig is configured, tested, and
reflected in an updated public policy.
