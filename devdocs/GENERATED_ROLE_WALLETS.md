# OGCoin Generated Role Wallets

Generated: `2026-05-23T15:57:12Z`

This file contains public Stellar account addresses only. These accounts are not active on Stellar mainnet until they are funded with XLM.

## Public Addresses

| Role | Public address | Purpose | First step |
| --- | --- | --- | --- |
| `treasury` | `GDMAMIC6SBYCF4NUQ6RBTUIFB5WWWS3TTDHXNCOUOLDFEPK5XOOU525F` | Cold or low-frequency reserves and approved program funding. | Fund with minimum XLM reserve; keep cold unless an approved movement is needed. |
| `grant` | `GAY2LYDC2YSAQ4VBQTG64LFZZHUB52UP3ACBTWLBWBDFBNH3ZCIWYFQV` | Approved open source project grants and community allocations. | Fund with minimum XLM reserve and add OGC trustline before receiving OGC inventory. |
| `liquidity` | `GAL3OOPQRNZ3MFX3AUR45M7P2DBF5LWSH3XWFI5CN7SZEMQWLOOOCRRC` | Tiny, policy-limited OGC/XLM test activity after approval. | Fund with minimum XLM reserve, add OGC trustline, then keep market activity blocked until limits are approved. |

## Designation Dry Run

Run this after the seed keys have been secured and the public addresses are approved:

```bash
python3 tools/ogcoin_next_steps.py wallet-designation \
  --treasury GDMAMIC6SBYCF4NUQ6RBTUIFB5WWWS3TTDHXNCOUOLDFEPK5XOOU525F \
  --grant GAY2LYDC2YSAQ4VBQTG64LFZZHUB52UP3ACBTWLBWBDFBNH3ZCIWYFQV \
  --liquidity GAL3OOPQRNZ3MFX3AUR45M7P2DBF5LWSH3XWFI5CN7SZEMQWLOOOCRRC
```

Then run each printed `tools/transparency_log.py designate-account` command with `--dry-run`, review the output, remove `--dry-run` only after approval, and commit the transparency log update.

## Activation Checklist

1. Move seed keys into a password manager, hardware signer, or other approved custody process.
2. Delete any plaintext seed file after custody is confirmed.
3. Fund each public account with enough XLM for minimum balance, trustlines, and fees.
4. Add OGC trustlines for grant and liquidity wallets before sending OGC to them.
5. Keep liquidity activity blocked until exposure limits and approval are public.
6. Never use the issuer, distribution wallet, or personal issuer signer as these operating wallets.

## Existing Accounts Not To Reuse

- Issuer: `GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57`
- Distribution: `GDD6IVZJVY3ZFWJ5T5BCZDURLF64ZTQJDDR5X5A7XEDJYTEC6ISDGWZB`
- Issuer signer / personal signer: `GBZAC66WWHFU2FEOG5KECSEVR6EJO7BYK63UGB52SENDN4JEJTJEVK5L`

## Private Seed Location

The generated seed keys were written to local gitignored file `.ogcoin-secrets/20260523T155712Z-role-wallet-seeds.md`, copied out by the operator, and the plaintext local file was deleted on 2026-05-23.

Keep the copied seed keys in durable secure custody. Do not commit, paste, email, or chat the `S...` seed values.
