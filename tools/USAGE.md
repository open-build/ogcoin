# OGCoin Python Management Tools

Complete toolkit for managing OGC (Open Green Coin) tokens on the Stellar blockchain.

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install stellar-sdk python-dotenv pandas tabulate
   ```

2. **Configuration Setup**
   ```bash
   python cli.py config --interactive
   ```

3. **Create and Fund Account (Testnet)**
   ```bash
   python cli.py account create
   python cli.py account fund --address GXXXXX...
   ```

4. **Send Payment**
   ```bash
   python cli.py payment --secret SXXXXX... --destination GXXXXX... --amount 100.0
   ```

## Tools Overview

### Core Components

- **`config.py`** - Configuration management with .env support
- **`stellar_manager.py`** - Core Stellar blockchain operations
- **`validators.py`** - Input validation and security checks
- **`formatters.py`** - Output formatting for console and reports
- **`bulk_payments.py`** - CSV-based bulk payment processing
- **`transparency_reporter.py`** - Monthly transparency reports
- **`cli.py`** - Command-line interface for all operations

## Configuration

Create a `.env` file in the tools directory:

```env
# Network Configuration
STELLAR_NETWORK=testnet
HORIZON_URL=https://horizon-testnet.stellar.org

# Token Configuration
TOKEN_CODE=OGC
ISSUER_ADDRESS=GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ISSUER_SECRET=SXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TOTAL_SUPPLY=1000000000

# Optional Settings
DEFAULT_BATCH_SIZE=50
DEFAULT_DELAY=1.0
REPORTS_DIR=reports
```

## Command Line Usage

### Account Management

```bash
# Create new account
python cli.py account create

# Get account information
python cli.py account info --address GXXXXX...

# Fund testnet account
python cli.py account fund --address GXXXXX...
```

### Trustline Operations

```bash
# Create trustline for OGC token
python cli.py trustline create --secret SXXXXX...

# Remove trustline
python cli.py trustline remove --secret SXXXXX...
```

### Payments

```bash
# Single payment
python cli.py payment --secret SXXXXX... --destination GXXXXX... --amount 100.5 --memo "Payment"

# Validate bulk payment CSV
python cli.py bulk validate --file payments.csv

# Create payment template
python cli.py bulk template --output template.csv --samples 10

# Process bulk payments (dry run)
python cli.py bulk process --file payments.csv --secret SXXXXX... --dry-run

# Process bulk payments (live)
python cli.py bulk process --file payments.csv --secret SXXXXX... --batch-size 25 --delay 2.0
```

### Transparency Reports

```bash
# Current token statistics
python cli.py report stats

# Monthly report for specific month
python cli.py report monthly --year 2024 --month 1

# Previous month report
python cli.py report previous
```

## CSV Format for Bulk Payments

Create CSV files with the following format:

```csv
address,amount,memo
GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX,100.0000000,Payment 1
GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX,250.5000000,Payment 2
GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX,75.2500000,Payment 3
```

Required columns:
- `address` - Stellar account public key
- `amount` - Payment amount (up to 7 decimal places)

Optional columns:
- `memo` - Payment memo (max 28 characters)

## Programmatic Usage

### Basic Operations

```python
from config import OGCConfig
from stellar_manager import StellarManager

# Initialize
config = OGCConfig()
manager = StellarManager(config)

# Create account
result = manager.create_account()
if result['successful']:
    print(f"New account: {result['public_key']}")

# Send payment
result = manager.send_payment(
    source_secret="SXXXXX...",
    destination="GXXXXX...",
    amount="100.0",
    memo="Test payment"
)
```

### Bulk Payments

```python
from bulk_payments import BulkPaymentProcessor

processor = BulkPaymentProcessor(config)

# Process CSV file
result = processor.process_bulk_payments(
    file_path="payments.csv",
    source_secret="SXXXXX...",
    batch_size=50,
    dry_run=True  # Test first
)

print(f"Processed {result['successful_payments']} payments")
```

### Transparency Reports

```python
from transparency_reporter import TransparencyReporter

reporter = TransparencyReporter(config)

# Generate monthly report
result = reporter.generate_monthly_report(2024, 1)
if result['successful']:
    print(f"Report saved: {result['html_file']}")

# Get current stats
stats = reporter.get_real_time_stats()
print(f"Circulating supply: {stats['supply_info']['circulating_supply']}")
```

## Security Features

- **Input Validation**: All addresses, amounts, and memos are validated
- **Safe Error Handling**: Graceful failure with detailed error messages
- **Dry Run Support**: Test operations before execution
- **Rate Limiting**: Configurable delays between batch operations
- **Environment Variables**: Sensitive data stored in .env files

## Error Handling

All tools include comprehensive error handling:

```python
result = manager.send_payment(...)
if result['successful']:
    print("Payment sent!")
    print(f"Transaction hash: {result['hash']}")
else:
    print(f"Payment failed: {result['error']}")
    # Continue with error handling
```

## Network Support

- **Testnet**: Development and testing (default)
- **Public**: Production mainnet
- **Custom**: Any Stellar-compatible network

Configure via environment variables or interactive setup.

## Report Generation

The transparency reporter generates:

- **HTML Reports**: User-friendly web pages
- **JSON Data**: Machine-readable format
- **Console Output**: Quick statistics display

Reports include:
- Token supply information
- Transaction summaries
- Top holder analysis
- Historical data

## Best Practices

1. **Always test on testnet first**
2. **Use dry-run mode for bulk operations**
3. **Validate CSV files before processing**
4. **Keep secret keys secure and never commit them**
5. **Monitor transaction fees on mainnet**
6. **Generate regular transparency reports**

## Troubleshooting

### Common Issues

1. **Import Errors**: Install required packages
   ```bash
   pip install stellar-sdk python-dotenv pandas tabulate
   ```

2. **Network Errors**: Check Horizon URL in configuration

3. **Account Not Found**: Fund testnet accounts or check addresses

4. **Trustline Required**: Create trustline before receiving tokens

5. **Insufficient Balance**: Check XLM balance for fees

### Getting Help

- Check error messages for specific guidance
- Use `--help` flag with CLI commands
- Review configuration with `python cli.py config`
- Test operations with dry-run mode first

## License

This toolkit is part of the OGCoin project. See the main project for license information.

## Contributing

1. Follow existing code style and patterns
2. Add comprehensive error handling
3. Include input validation
4. Test on both testnet and mainnet
5. Update documentation for new features