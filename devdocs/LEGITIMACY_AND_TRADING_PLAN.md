# OGCoin Legitimacy and Trading Readiness

Last checked: 2026-05-22

This is the practical path for making OGCoin easier for wallets, traders, employees, and open source contributors to verify. It is not legal or tax advice; token sales, fundraising, and payroll need review by qualified counsel and payroll/tax professionals.

## Current Mainnet State

- Asset: `OGC:GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57`
- Issuer account: active on Stellar public network.
- Distribution account observed on-chain: `GDD6IVZJVY3ZFWJ5T5BCZDURLF64ZTQJDDR5X5A7XEDJYTEC6ISDGWZB`.
- Personal/operations account observed on-chain: `GBZAC66WWHFU2FEOG5KECSEVR6EJO7BYK63UGB52SENDN4JEJTJEVK5L`.
- Supply observed through Horizon: `999999501.3700000` OGC in authorized balances plus `500.0000000` OGC in claimable balances.
- Liquidity observed through Horizon: no OGC/XLM order book bids or asks and no liquidity pools.
- Stellar metadata status: `/.well-known/stellar.toml` is live and the issuer account has `home_domain=www.opengreencoin.com`.
- Public disclosure status: `trust.html` now documents verification details, risk boundaries, governance status, liquidity readiness, and payroll limitations.
- Governance status: `governance.html` now publishes interim issuer, supply, signer, treasury, distribution, and liquidity guardrails.
- Transparency status: `transparency.html` and `data/transparency-log.json` now publish public governance records and provide a format for future distributions, grants, treasury movement, and liquidity activity.

## Legitimacy Checklist

1. Publish `https://www.opengreencoin.com/.well-known/stellar.toml`.
   Done. Keep the contact email, logo, and public org details current.

2. Set issuer `home_domain` to `www.opengreencoin.com`.
   Done in transaction `8b17b271d53bd8f9df817648acd3aa80169005d0be9a032bcbe7467c06f3eb01`, ledger `62686761`.

3. Confirm public org details.
   `support@opengreencoin.com` and `assets/logo.png` must exist before treating the TOML as production-grade. Replace the placeholder city/country level address with the correct public business address if you want stronger exchange/wallet trust.

4. Separate hot and cold accounts.
   Keep the issuer account cold. Use a distribution or treasury account for airdrops, grants, payroll, market making, and liquidity. The interim policy is published in `governance.html`; use `devdocs/WALLET_DESIGNATION_WORKSHEET.md` and add multisig and sane thresholds before moving meaningful value.

5. Decide supply governance before promising fixed supply.
   The issuer currently can issue more OGC because its master signer is active and no immutable/lockdown policy is documented. If the project promises fixed supply, publish a signed policy and consider locking or multisig-controlling the issuer.

6. Remove investment-style promises from public copy.
   Avoid language that creates an expectation of profit from Open Build's future efforts. Describe utility, grants, community participation, and risks plainly.

## Trading Readiness

1. Create an actual market.
   Current OGC/XLM order books are empty. To become tradeable in practice, fund a market-making account and create conservative buy/sell offers or deposit OGC and XLM into a Stellar liquidity pool.

2. Publish market risk disclosures.
   Explain that early markets may be thin, volatile, and hard to exit. Do not imply a stable price unless there is an actual redemption or reserve program.

3. Add transparency reporting.
   Done at the starter level with `transparency.html` and `data/transparency-log.json`. Use `python3 tools/transparency_log.py validate` before publishing and `python3 tools/transparency_log.py add --dry-run ...` before appending reviewed treasury, distribution, grant, or liquidity records.

4. Test path payments before public launch.
   Verify OGC/XLM swaps from Freighter, StellarTerm, LOBSTR, and Stellar Lab using small amounts only.

## Payroll Readiness

1. Treat employee payments as payroll, not informal transfers.
   In the US, virtual currency wages are generally measured in USD at receipt, subject to withholding, FICA, FUTA, and W-2 reporting.

2. Preserve wage-law compliance.
   Employees still need to receive required minimum wages and overtime under applicable federal, state, and local law. Many employers handle this by paying required wages in USD and offering OGC as an elective bonus or grant.

3. Establish fair market value.
   Payroll needs a defensible USD value at payment time. OGC currently has no trading history or liquid market, so valuation is a blocker for routine wage payments.

4. Get written consent and risk disclosure.
   Employees should understand custody, volatility, tax reporting, and that OGC is not legal tender or a guaranteed redemption instrument.

## Immediate Next Steps

1. Review `governance.html` with counsel and project leadership.
2. Choose treasury, grant, and liquidity public account addresses using `devdocs/WALLET_DESIGNATION_WORKSHEET.md`.
3. Use `tools/transparency_log.py designate-account --dry-run ...` to record approved public wallet designations.
4. Decide whether to start OGC/XLM liquidity with tiny offers or a small liquidity pool after treasury limits are approved.
5. Test OGC/XLM swaps through Stellar Lab, StellarTerm, LOBSTR, and Freighter using small amounts only.
