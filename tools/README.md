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
- **`ogcoin_console.py`** - Local web console for legitimacy checks, recipient prep, unsigned XDR generation, and promotion copy
- **`ogcoin_next_steps.py`** - Non-custodial helper for trustline campaigns, wallet designation commands, and tiny liquidity readiness checks
- **`run_next_steps_report.py`** - Run next-step commands and write `devdocs/NEXT_STEPS_OUTCOME.md`
- **`transparency_log.py`** - Validate and append reviewed public records to `data/transparency-log.json`

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
