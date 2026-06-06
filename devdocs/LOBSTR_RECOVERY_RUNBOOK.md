# Lobstr Recovery Runbook

This runbook covers the current OGCoin funding blocker: the old Lobstr funding
account has XLM, but it uses custom Stellar multisig. No script, wallet, or
support team can bypass Stellar signer thresholds.

## Current Stuck Account

- Account: `GC5PRFNWGGWTKVH5DLIO3QL5DV4FPBFAE26Q77BPSXCPQQWGJQVHSW7U`
- Master signer weight: `10`
- Required thresholds: `20 / 20 / 20`
- Required custom signer: `GDJ4HVRGT2OVVL5YFLBR7XAJIHCMWUO6OKLBXWWTVW3OK4VBFRAYQJHV`
- Practical result: the account cannot send XLM or remove the custom signer
  unless the `GDJ4...QJHV` signer also signs.

## Safe Diagnostic Command

```bash
python3 tools/lobstr_recovery.py inspect \
  --account GC5PRFNWGGWTKVH5DLIO3QL5DV4FPBFAE26Q77BPSXCPQQWGJQVHSW7U
```

If a signer secret is recovered, test it locally without printing the secret:

```bash
export OGC_RECOVERED_SIGNER='S...'
python3 tools/lobstr_recovery.py inspect \
  --account GC5PRFNWGGWTKVH5DLIO3QL5DV4FPBFAE26Q77BPSXCPQQWGJQVHSW7U \
  --signer-secret-env OGC_RECOVERED_SIGNER
```

Do not paste the `S...` secret into chat, tickets, forms, or the website.

## Fund OGCoin Without the Stuck Account

Use a working single-signer wallet or fresh XLM instead of waiting on the
custom multisig recovery.

```bash
python3 tools/lobstr_recovery.py build-role-funding \
  --source G...WORKING_SOURCE_ACCOUNT \
  --grant-amount 3 \
  --liquidity-amount 5 \
  --treasury-amount 0
```

This creates a reviewable XDR in `.ogcoin-xdr/`. Sign it with the source wallet
or rerun with a local environment variable:

```bash
export OGC_SOURCE_SECRET='S...'
python3 tools/lobstr_recovery.py build-role-funding \
  --source G...WORKING_SOURCE_ACCOUNT \
  --grant-amount 3 \
  --liquidity-amount 5 \
  --treasury-amount 0 \
  --signer-secret-env OGC_SOURCE_SECRET
```

Submit only after reviewing the destination accounts and amounts:

```bash
python3 tools/lobstr_recovery.py submit-xdr --xdr-file .ogcoin-xdr/FILE.xdr
```

## If the Required Signer Is Recovered

To move some spendable XLM out of the stuck account, build a drain payment and
sign it with the recovered signer. Account merge is not recommended while the
account has subentries.

```bash
export OGC_RECOVERED_SIGNER='S...'
python3 tools/lobstr_recovery.py build-drain \
  --source GC5PRFNWGGWTKVH5DLIO3QL5DV4FPBFAE26Q77BPSXCPQQWGJQVHSW7U \
  --destination G...SAFE_DESTINATION \
  --amount 3 \
  --signer-secret-env OGC_RECOVERED_SIGNER
```

The script will say whether the provided signer weight is enough. If it is
still under-authorized, the XDR will fail on-chain until additional signer
weight is added.
