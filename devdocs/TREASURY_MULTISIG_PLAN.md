# OGCoin Impact Treasury Multisig Plan

Generated: `2026-06-24T15:20:07Z`

Status: **Active on Mainnet.**

Mainnet activation transaction: `e89ac511c4a0ad764d8e2703b372f556c204a873c35f29f9969f9d1e84f4c493`, ledger `63223971`.

## Proposed 2-of-3 Policy

- Production treasury / master signer: `GDMAMIC6SBYCF4NUQ6RBTUIFB5WWWS3TTDHXNCOUOLDFEPK5XOOU525F` (weight 1)
- Approval signer: `GAPBRE2R7EQXWA5DXTI2DNPFFL24DXJ7UQ5AL453CV7M3E2V2B64E473` (weight 1)
- Recovery signer: `GBBFU6277F7XXRI3IF3J4FUE4YZTE5EO4KDNHAWAFSOGKXT6LJKQHVF5` (weight 1)
- Low threshold: `1`
- Medium threshold: `2`
- High threshold: `2`

Any two of the three signers can authorize treasury payments or signer-policy changes. One signer alone cannot.

## Custody Requirements

1. Keep the treasury master seed, approval seed, and recovery seed in separate custody locations.
2. Do not put all three seeds in one password-manager entry, computer, or physical envelope.
3. Confirm the approval and recovery seeds can be restored before creating the Mainnet XDR.
4. Record who may use each signer and under what approval process.
5. Never use LOBSTR Vault or an unknown custom signer for this policy.

## Local Secret File

The generated secrets are in the gitignored owner-readable file `.ogcoin-secrets/treasury-multisig.env`.
Move the approval and recovery seeds into their separate durable custody locations. Delete the plaintext file only after the Mainnet transition and recovery materials have been independently verified.

## Activation Sequence

1. Testnet rehearsal confirmed all three signer pairs succeed.
2. Approval and recovery seeds were restore-checked separately.
3. Unsigned Mainnet XDR was created with the explicit backup acknowledgement.
4. Exact signer addresses and thresholds were reviewed before signing.
5. Transaction was signed with the current treasury master key and submitted once.
6. On-chain signer policy was verified.
7. Transaction hash and updated policy are published in the transparency log.
