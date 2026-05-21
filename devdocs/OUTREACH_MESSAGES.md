# OGCoin Outreach Messages

Use these as starting points. Keep claims utility-focused and avoid profit, redemption, salary-value, or ownership promises.

## Public Launch Update

OGCoin (OGC) is live as a Stellar mainnet asset for Open Build's open source funding and developer education work. The public asset metadata is available at `https://www.opengreencoin.com/.well-known/stellar.toml`, and the asset can be inspected on StellarExpert:

`https://stellar.expert/explorer/public/asset/OGC-GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57`

OGC is experimental, not anchored to fiat or equity, and early markets may be illiquid.

## Trustline Instructions

To receive OGC, add a custom Stellar asset trustline in your wallet.

- Asset code: `OGC`
- Issuer: `GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57`
- Network: Stellar public network
- Website: `https://www.opengreencoin.com/`

Only use the issuer address above. Anyone can create an asset named OGC, so the issuer address matters.

## Airdrop Invitation

Open Build is preparing OGC airdrops for open source contributors and project maintainers. To participate, create or use a Stellar wallet, add the OGC trustline, and submit your public Stellar address through the official form on `https://www.opengreencoin.com/`.

OGC is intended for community funding experiments and project support. It is not a promise of profit, redemption, or ownership.

## Project Partner Message

We are exploring OGCoin as a transparent funding and participation layer for open source projects. If your project wants to participate, we can list it for community review, validate a Stellar receiving account, and include it in future grant or airdrop batches once governance and distribution criteria are finalized.

## Internal Signer Request

Please sign and submit the latest unsigned Stellar XDR for the OGC issuer `home_domain` update. The transaction sets `home_domain=www.opengreencoin.com` for issuer `GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57`.

Regenerate the XDR immediately before signing:

```bash
python3 tools/create_home_domain_xdr.py \
  --issuer GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57 \
  --home-domain www.opengreencoin.com
```

Do not share issuer secret keys. Sign through a trusted wallet or Stellar Lab.
