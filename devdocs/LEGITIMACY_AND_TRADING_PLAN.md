# OGCoin Legitimacy and Trading Readiness

Last checked: 2026-05-21

This is the practical path for making OGCoin easier for wallets, traders, employees, and open source contributors to verify. It is not legal or tax advice; token sales, fundraising, and payroll need review by qualified counsel and payroll/tax professionals.

## Current Mainnet State

- Asset: `OGC:GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57`
- Issuer account: active on Stellar public network.
- Distribution account observed on-chain: `GDD6IVZJVY3ZFWJ5T5BCZDURLF64ZTQJDDR5X5A7XEDJYTEC6ISDGWZB`.
- Personal/operations account observed on-chain: `GBZAC66WWHFU2FEOG5KECSEVR6EJO7BYK63UGB52SENDN4JEJTJEVK5L`.
- Supply observed through Horizon: `999999501.3700000` OGC in authorized balances plus `500.0000000` OGC in claimable balances.
- Liquidity observed through Horizon: no OGC/XLM order book bids or asks and no liquidity pools.
- Stellar metadata gap: the live site did not expose `/.well-known/stellar.toml`, and the issuer account did not have `home_domain` set.

## Legitimacy Checklist

1. Publish `https://www.opengreencoin.com/.well-known/stellar.toml`.
   The repo now includes `.well-known/stellar.toml`, but GitHub Pages must deploy it and the contact email/logo must be real.

2. Set issuer `home_domain` to `www.opengreencoin.com`.
   This requires a signed mainnet `set_options` transaction from the issuer account. Use `tools/create_home_domain_xdr.py` to create an unsigned XDR, then sign it with the issuer key in a wallet or Stellar Lab.

3. Confirm public org details.
   `support@opengreencoin.com` and `assets/logo.png` must exist before treating the TOML as production-grade. Replace the placeholder city/country level address with the correct public business address if you want stronger exchange/wallet trust.

4. Separate hot and cold accounts.
   Keep the issuer account cold. Use a distribution or treasury account for airdrops, grants, payroll, market making, and liquidity. Add multisig and sane thresholds before moving meaningful value.

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
   Publish treasury balances, distribution wallets, liquidity wallet addresses, grant disbursements, and any market-making policy.

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

1. Deploy this repo so `/.well-known/stellar.toml` and `/assets/logo.png` are live.
2. Run `python tools/create_home_domain_xdr.py --issuer GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57 --home-domain www.opengreencoin.com`.
3. Sign and submit the generated XDR with the issuer account.
4. Re-check Horizon: the asset record should expose a non-empty TOML link.
5. Create a small OGC/XLM market-making transaction or liquidity pool only after legal, treasury, and disclosure decisions are settled.
