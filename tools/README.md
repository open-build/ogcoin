# OGCoin Stellar Management Tools

Python tools for managing OGC (Open Green Coin) on the Stellar network.

## Overview

This toolkit provides Python scripts and utilities for:
- Token issuance and management
- Bulk payments to multiple recipients
- Account creation and management
- Transaction monitoring and reporting
- Integration with the website for transparency

## Tools

### Core Scripts

- **`stellar_manager.py`** - Main class for Stellar operations
- **`bulk_payments.py`** - Process CSV files for bulk payments
- **`account_manager.py`** - Create and manage Stellar accounts
- **`token_issuer.py`** - Issue and manage OGC tokens
- **`transaction_monitor.py`** - Monitor and report on transactions
- **`transparency_reporter.py`** - Generate reports for website integration
- **`open_build_fund.py`** - Open Build fund management and transaction fees

### Utility Scripts

- **`config.py`** - Configuration management
- **`validators.py`** - Input validation utilities
- **`formatters.py`** - Output formatting helpers
- **`test_fund.py`** - Test and demonstrate Open Build fund functionality
- **`create_home_domain_xdr.py`** - Build an unsigned issuer `home_domain` XDR for SEP-1 verification
- **`create_issuer_signer_xdr.py`** - Build an unsigned issuer signer and threshold hardening XDR
- **`create_role_wallets.py`** - Generate public role wallet addresses and a local gitignored seed file
- **`create_tiny_liquidity_offer.py`** - Build and submit one explicitly priced, policy-limited OGC/XLM sell offer
- **`add_role_trustlines.py`** - Add OGC trustlines to the grant and liquidity wallets from local environment secrets
- **`lobstr_recovery.py`** - Diagnose Stellar multisig blockers, build role-wallet funding XDRs, and submit fully signed XDRs
- **`ogcoin_console.py`** - Local web console for legitimacy checks, recipient prep, unsigned XDR generation, and promotion copy
- **`ogcoin_next_steps.py`** - Non-custodial helper for trustline campaigns, wallet designation commands, and tiny liquidity readiness checks
- **`run_next_steps_report.py`** - Run next-step commands and write `devdocs/NEXT_STEPS_OUTCOME.md`
- **`send_liquidity_inventory.py`** - Send up to 1 OGC from distribution to the liquidity wallet for the first market test
- **`stellar_secret_inventory.py`** - Inventory local Stellar secret keys by derived public key without printing secrets
- **`transparency_log.py`** - Validate and append reviewed public records to `data/transparency-log.json`
- **`vault_phrase_inventory.py`** - Inventory local BIP39 recovery phrase candidates without printing phrase words

## Setup

### Prerequisites

```bash
pip install stellar-sdk python-dotenv pandas tabulate
```

### Environment Configuration

Create a `.env` file:

```env
# Stellar Configuration
STELLAR_NETWORK=public  # or 'testnet' for testing
ISSUER_SECRET_KEY=S...  # Your issuer account secret key
ISSUER_PUBLIC_KEY=G...  # Your issuer account public key

# OGC Token Configuration
TOKEN_CODE=OGC
TOTAL_SUPPLY=100000000

# Website Integration
WEBSITE_REPORTS_DIR=../reports
WEBSITE_API_ENDPOINT=https://www.opengreencoin.com/api

# Transparency Settings
GENERATE_REPORTS=true
AUTO_UPDATE_WEBSITE=true
```

## Usage Examples

### Bulk Payments

```python
from tools.bulk_payments import BulkPaymentProcessor

processor = BulkPaymentProcessor()
results = processor.process_csv('samples/recipients.csv')
print(f"Processed {len(results)} payments")
```

### Token Management

```python
from tools.token_issuer import TokenIssuer

issuer = TokenIssuer()
issuer.issue_tokens(amount=1000, destination_account='G...')
```

### Generate Transparency Report

```python
from tools.transparency_reporter import TransparencyReporter

reporter = TransparencyReporter()
report = reporter.generate_monthly_report()
reporter.save_to_website(report)
```

### Link Issuer to Website

Create an unsigned XDR that sets the issuer account `home_domain` to the domain hosting `/.well-known/stellar.toml`:

```bash
python create_home_domain_xdr.py \
  --issuer GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57 \
  --home-domain www.opengreencoin.com
```

Sign the generated XDR with the issuer account in Stellar Lab or your wallet. This script does not handle secret keys.

### Harden Issuer Signers

Create an unsigned XDR that adds approved issuer signers and updates thresholds:

```bash
SIGNER_A=G...PUBLIC_SIGNER_ONE
SIGNER_B=G...PUBLIC_SIGNER_TWO

python create_issuer_signer_xdr.py \
  --signer "$SIGNER_A:1" \
  --signer "$SIGNER_B:1" \
  --master-weight 1 \
  --low-threshold 1 \
  --med-threshold 2 \
  --high-threshold 2
```

This creates a 2-of-3 issuer-control pattern after signing and submission. It does not lock the issuer or create a fixed-supply guarantee.

### Local Console

Start the local console:

```bash
python3 ogcoin_console.py
```

Then open `http://localhost:8787/`. The console combines live public checks, recipient validation, and campaign copy generation. It does not handle secret keys or submit transactions.

For scheduled checks or CI:

```bash
python3 ogcoin_console.py --check
python3 ogcoin_console.py --check --format json
```

### Next-Step Operations

Prepare the remaining blocker work without handling secret keys:

```bash
python3 create_role_wallets.py
python3 ogcoin_next_steps.py status
python3 ogcoin_next_steps.py trustline-campaign --target 25
python3 ogcoin_next_steps.py wallet-designation --treasury G... --grant G... --liquidity G...
python3 ogcoin_next_steps.py liquidity-checklist --online
```

`create_role_wallets.py` writes public addresses to Markdown and private seeds to `.ogcoin-secrets/`, which is gitignored. Move the seeds into secure custody and delete the plaintext seed file. Use `../devdocs/NEXT_STEPS_RUNBOOK.md` for the full operating sequence.

Write a full outcome report:

```bash
python3 run_next_steps_report.py
```

### Add Grant and Liquidity Trustlines

After the role wallets are funded, add OGC trustlines from the wallet seeds without putting secrets in command history. From the repository root, first edit the local gitignored file:

```bash
open .ogcoin-secrets/role-wallets.env
```

Paste the matching `S...` secret seed values into `OGC_GRANT_SECRET=` and `OGC_LIQUIDITY_SECRET=`, then run:

```bash
python3 tools/add_role_trustlines.py
python3 tools/add_role_trustlines.py --submit
```

The first command signs reviewable XDRs into `.ogcoin-xdr/` without broadcasting them. The second broadcasts only if each loaded secret derives the expected public role wallet:

- grant: `GAY2LYDC2YSAQ4VBQTG64LFZZHUB52UP3ACBTWLBWBDFBNH3ZCIWYFQV`
- liquidity: `GAL3OOPQRNZ3MFX3AUR45M7P2DBF5LWSH3XWFI5CN7SZEMQWLOOOCRRC`

Default trustline limits are `100000` OGC for the grant wallet and `1` OGC for the liquidity wallet. Override them with `--grant-limit` or `--liquidity-limit` only after approval.

### Send Liquidity Inventory

Before the first tiny OGC/XLM test, the liquidity wallet needs up to `1 OGC`. From the repository root, first edit the local gitignored distribution signer file:

```bash
open .ogcoin-secrets/distribution.env
```

Paste the matching `S...` secret seed into `OGC_DISTRIBUTION_SECRET=`, then run:

```bash
python3 tools/send_liquidity_inventory.py
python3 tools/send_liquidity_inventory.py --submit
```

The helper verifies the secret derives the public distribution wallet, verifies the liquidity wallet trustline limit, refuses to exceed the published `1 OGC` cap, writes a signed XDR into `.ogcoin-xdr/`, and submits only with `--submit`.

### Create The Tiny OGC/XLM Offer

After the liquidity wallet holds its approved OGC inventory, provide an explicit test price in XLM per OGC:

```bash
python3 tools/create_tiny_liquidity_offer.py --price-xlm PRICE
python3 tools/create_tiny_liquidity_offer.py --price-xlm PRICE --submit
```

The helper requires the price rather than implying a valuation. It refuses amounts over `1 OGC`, notional exposure over `1 XLM`, missing OGC inventory, incorrect signer keys, and duplicate open offers from the liquidity wallet.

### Lobstr Recovery and Funding XDRs

Inspect a stuck Lobstr account and see which signer weight is still required:

```bash
python3 lobstr_recovery.py inspect \
  --account GC5PRFNWGGWTKVH5DLIO3QL5DV4FPBFAE26Q77BPSXCPQQWGJQVHSW7U
```

Build a reviewable XDR to fund the currently designated role wallets from a working source account:

```bash
python3 lobstr_recovery.py build-role-funding \
  --source G...SOURCE_ACCOUNT \
  --grant-amount 3 \
  --liquidity-amount 5 \
  --treasury-amount 0
```

If you have the needed secret key locally, keep it in an environment variable and sign without printing it:

```bash
export OGC_SIGNER_SECRET='S...'
python3 lobstr_recovery.py build-role-funding \
  --source G...SOURCE_ACCOUNT \
  --grant-amount 3 \
  --liquidity-amount 5 \
  --signer-secret-env OGC_SIGNER_SECRET
```

The helper cannot bypass Stellar multisig. For a custom multisig Lobstr account, the transaction must still be signed by enough signer weight before submission. Generated XDR files are written to `.ogcoin-xdr/`, which is gitignored.

Inventory local Stellar secret keys without exposing the `S...` values:

```bash
python3 stellar_secret_inventory.py \
  ~/Projects/me/mytrader \
  ~/Documents \
  ~/Desktop \
  ~/Downloads
```

The report lists derived public keys, file paths, and whether any key matches the missing custom signer or signer set for the locked accounts.

Inventory possible Lobstr/Vault recovery phrases without exposing the phrase words:

```bash
python3 vault_phrase_inventory.py \
  ~/Projects/me/mytrader \
  ~/Documents \
  ~/Desktop \
  ~/Downloads \
  --index-max 20
```

The report lists only candidate IDs, file paths, line ranges, derived public keys, and whether a candidate derives to the missing signer.

To check a phrase manually without echoing it to the terminal:

```bash
python3 vault_phrase_inventory.py --interactive --index-max 100
```

### Transparency Log Helper

Validate the public transparency data:

```bash
python3 transparency_log.py validate
python3 transparency_log.py list
python3 transparency_log.py accounts
```

Draft a reviewed governance, distribution, grant, treasury, or liquidity record:

```bash
python3 transparency_log.py add \
  --id 2026-05-22-example-record \
  --date 2026-05-22 \
  --category policy \
  --status published \
  --title "Example record" \
  --summary "Short public summary with no private recipient or payroll data." \
  --link https://www.opengreencoin.com/transparency.html \
  --dry-run
```

Remove `--dry-run` only after the record is approved for public release. The helper only edits JSON and never handles secret keys, signs transactions, or submits XDR.

Publish an approved public wallet role:

```bash
TREASURY_PUBLIC_KEY=G...PUBLIC_ACCOUNT

python3 transparency_log.py designate-account \
  --role treasury \
  --address "$TREASURY_PUBLIC_KEY" \
  --date 2026-05-22 \
  --policy "Cold or low-frequency account for approved OGCoin treasury activity; no routine airdrops, payroll, or liquidity operations." \
  --summary "Designated the public treasury wallet for approved OGCoin reserve and program funding activity." \
  --dry-run
```

Use `devdocs/WALLET_DESIGNATION_WORKSHEET.md` before publishing treasury, grant, distribution, or liquidity wallet addresses.

## Integration with ForgeWeb

The tools are designed to integrate seamlessly with your ForgeWeb-powered website:

1. **Automated Reports** - Generate JSON data for website consumption
2. **Transaction Logs** - Create formatted logs for display
3. **API Integration** - Provide data endpoints for real-time info
4. **GitHub Actions** - Automate reporting and updates

## File Structure

```
ogcoin/
├── tools/
│   ├── __init__.py
│   ├── stellar_manager.py
│   ├── bulk_payments.py
│   ├── account_manager.py
│   ├── token_issuer.py
│   ├── transaction_monitor.py
│   ├── transparency_reporter.py
│   ├── config.py
│   ├── validators.py
│   └── formatters.py
├── samples/
│   ├── recipients.csv
│   └── stellar.toml
├── reports/
│   └── (generated reports)
├── scripts/
│   ├── setup.py
│   ├── bulk_payment.py
│   └── generate_report.py
└── .env
```

## Security Best Practices

- Store secret keys in environment variables only
- Use testnet for development and testing
- Validate all inputs before processing
- Log all operations for audit trails
- Implement rate limiting for API calls
- Regular backup of configuration and reports

## Monitoring and Transparency

The toolkit includes built-in transparency features:
- Monthly transaction reports
- Real-time balance tracking  
- Public API endpoints for community verification
- Integration with website for public display

## Open Build Fund System

### Overview

OGCoin includes tooling for participating payments to include an explicit contribution to the Open Build fund. This fund supports:

- **Open Source Projects** (50%) - Direct funding for critical infrastructure and innovative projects
- **Developer Training** (30%) - Bootcamps, mentorship programs, and educational resources  
- **Operations** (20%) - Platform maintenance, governance, and community management

### How It Works

1. **Contribution Collection**: Participating payment tools can route a contribution to the fund
2. **Community Governance**: OGC holders vote on fund distribution proposals
3. **Transparent Distribution**: All allocations are publicly tracked and reported

### Fund Commands

```bash
# Check current fund balance and allocations
python cli.py fund balance

# Calculate fund contribution for a participating transaction
python cli.py fund calculate --amount 100

# Send transaction with an explicit fund contribution
python cli.py fund send --source-secret SXXXXX... --destination GXXXXX... --amount 50

# Generate comprehensive fund report
python cli.py fund report

# View community proposal system
python cli.py fund proposal
```

### Testing the Fund System

```bash
# Run comprehensive fund system tests
python test_fund.py

# Test different transaction scenarios
python cli.py fund calculate --amount 10
python cli.py fund calculate --amount 1000
```

### Impact Projections

With moderate adoption (1,000 daily transactions averaging 25 OGC):
- **Daily Fund Collection**: 25 OGC
- **Annual Impact**: 9,125 OGC allocated to open source support
- **Projects Funded**: Estimated 10-20 critical projects per year
- **Developers Trained**: 50-100 developers through funded programs

### Transparency Features

- All fund transactions are publicly visible on Stellar
- Monthly allocation reports published automatically
- Community voting records maintained on-chain
- Real-time fund balance available via API

## Support

- Documentation: See individual tool files for detailed usage
- Issues: Report on GitHub repository
- Community: Join discussions in the Open Build community
