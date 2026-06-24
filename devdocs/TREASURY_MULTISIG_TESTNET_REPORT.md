# OGCoin Treasury Multisig Testnet Rehearsal

Completed: `2026-06-24T15:21:46Z`

Result: **PASS**

- Testnet source / master signer: `GC3IALDC4H2YXZAEOZZKW6GBM2F7UWDYDMSWDO4P7MGKYMT6ZWCULFR6`
- Approval signer: `GAPBRE2R7EQXWA5DXTI2DNPFFL24DXJ7UQ5AL453CV7M3E2V2B64E473`
- Recovery signer: `GBBFU6277F7XXRI3IF3J4FUE4YZTE5EO4KDNHAWAFSOGKXT6LJKQHVF5`
- Setup transaction: `1a930376927162b7bf4b97bb9a016102c4368b30938b97943e5a82eeb7f0c18a`
- Thresholds: low `1`, medium `2`, high `2`
- Single signer payment result: `op_bad_auth` as expected

## Successful Signer Pairs

| Pair | Transaction hash | Ledger |
| --- | --- | --- |
| master + approval | `9e20fca04cc2b84b4ba6efcba68c3ed41c2f3cf5691a3239abac22590a304500` | `3260112` |
| master + recovery | `5b742f79ae5a4f4cd1b4753d87a92cbb55e24c8b1763ffa9032fe5c48feb0ae0` | `3260113` |
| approval + recovery | `fc013d6bb9ce6cb15e12d03067602502940761c835a8b92494d14074c2910637` | `3260114` |

## Verified On-Chain Signers

- `GAPBRE2R7EQXWA5DXTI2DNPFFL24DXJ7UQ5AL453CV7M3E2V2B64E473`: weight `1`
- `GBBFU6277F7XXRI3IF3J4FUE4YZTE5EO4KDNHAWAFSOGKXT6LJKQHVF5`: weight `1`
- `GC3IALDC4H2YXZAEOZZKW6GBM2F7UWDYDMSWDO4P7MGKYMT6ZWCULFR6`: weight `1`

This rehearsal used Testnet XLM only. It did not sign or submit any Mainnet transaction.
