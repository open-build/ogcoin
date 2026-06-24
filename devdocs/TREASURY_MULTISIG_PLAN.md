# OGCoin Impact Treasury Multisig Plan

Generated: `2026-06-24T15:20:07Z`

Status: **Testnet rehearsal passed; Mainnet not changed.**

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

## Required Sequence

1. Run the Testnet rehearsal and confirm all three signer pairs succeed.
2. Back up and restore-check the approval and recovery seeds separately.
3. Create the unsigned Mainnet XDR with the explicit backup acknowledgement.
4. Review the exact signer addresses and thresholds in Stellar Lab.
5. Sign with the current treasury master key and submit once.
6. Verify the on-chain signer policy before receiving meaningful OGC.
7. Publish the transaction hash and updated policy in the transparency log.
