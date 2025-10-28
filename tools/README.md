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

### Utility Scripts

- **`config.py`** - Configuration management
- **`validators.py`** - Input validation utilities
- **`formatters.py`** - Output formatting helpers

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
WEBSITE_API_ENDPOINT=https://open-build.github.io/ogcoin/api

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

## Support

- Documentation: See individual tool files for detailed usage
- Issues: Report on GitHub repository
- Community: Join discussions in the Open Build community