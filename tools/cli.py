"""
Command-line interface for OGCoin management tools
Provides easy access to all OGC token operations
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

# Add the tools directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from config import Config as OGCConfig
from stellar_manager import StellarManager
from bulk_payments import BulkPaymentProcessor, quick_validate_csv, create_payment_template
from transparency_reporter import TransparencyReporter, generate_current_stats, generate_report_for_month
from formatters import format_account_info, format_transaction_result, format_table
from open_build_fund import OpenBuildFund, calculate_transaction_with_fund_fee

def setup_config_command(args):
    """Handle config setup command"""
    config = OGCConfig()
    
    if args.interactive:
        print("OGCoin Configuration Setup")
        print("=" * 30)
        
        # Network selection
        network = input("Network (public/testnet) [testnet]: ").strip() or "testnet"
        config.set('network', network)
        
        # Issuer configuration
        issuer_address = input("Issuer address: ").strip()
        if issuer_address:
            config.set('issuer_address', issuer_address)
        
        issuer_secret = input("Issuer secret (will be stored in .env): ").strip()
        if issuer_secret:
            config.set('issuer_secret', issuer_secret)
        
        # Token configuration
        token_code = input("Token code [OGC]: ").strip() or "OGC"
        config.set('token_code', token_code)
        
        total_supply = input("Total supply [1000000000]: ").strip() or "1000000000"
        config.set('total_supply', total_supply)
        
        # Save configuration
        config.save()
        print(f"\n✅ Configuration saved to {config.config_file}")
        
    else:
        # Show current configuration
        print("Current OGCoin Configuration:")
        print("=" * 30)
        config_data = config.get_all_settings()
        
        for key, value in config_data.items():
            if 'secret' in key.lower():
                value = "***" if value else "Not set"
            print(f"{key}: {value}")

def account_command(args):
    """Handle account operations"""
    config = OGCConfig()
    manager = StellarManager(config)
    
    if args.action == "create":
        print("Creating new Stellar account...")
        result = manager.create_account()
        
        if result['successful']:
            print("✅ Account created successfully!")
            print(f"Public Key: {result['public_key']}")
            print(f"Secret Key: {result['secret_key']}")
            print("⚠️  Save the secret key securely!")
        else:
            print(f"❌ Account creation failed: {result['error']}")
    
    elif args.action == "info":
        if not args.address:
            print("Please provide account address with --address")
            return
        
        print(f"Getting account information for {args.address}")
        result = manager.get_account_info(args.address)
        
        if result['successful']:
            print(format_account_info(result['account_data']))
        else:
            print(f"❌ Failed to get account info: {result['error']}")
    
    elif args.action == "fund":
        if not args.address:
            print("Please provide account address with --address")
            return
        
        print(f"Funding account {args.address} on testnet...")
        result = manager.fund_account_testnet(args.address)
        
        if result['successful']:
            print("✅ Account funded successfully!")
        else:
            print(f"❌ Account funding failed: {result['error']}")

def trustline_command(args):
    """Handle trustline operations"""
    config = OGCConfig()
    manager = StellarManager(config)
    
    if not args.secret:
        print("Please provide account secret key with --secret")
        return
    
    if args.action == "create":
        print(f"Creating trustline for {config.get('token_code')} token...")
        result = manager.create_trustline(args.secret)
        
        if result['successful']:
            print("✅ Trustline created successfully!")
            print(format_transaction_result(result))
        else:
            print(f"❌ Trustline creation failed: {result['error']}")
    
    elif args.action == "remove":
        print(f"Removing trustline for {config.get('token_code')} token...")
        result = manager.remove_trustline(args.secret)
        
        if result['successful']:
            print("✅ Trustline removed successfully!")
            print(format_transaction_result(result))
        else:
            print(f"❌ Trustline removal failed: {result['error']}")

def payment_command(args):
    """Handle payment operations"""
    config = OGCConfig()
    manager = StellarManager(config)
    
    if not args.secret:
        print("Please provide source account secret key with --secret")
        return
    
    if not args.destination:
        print("Please provide destination address with --destination")
        return
    
    if not args.amount:
        print("Please provide amount with --amount")
        return
    
    print(f"Sending {args.amount} {config.get('token_code')} to {args.destination}")
    
    result = manager.send_payment(
        source_secret=args.secret,
        destination=args.destination,
        amount=args.amount,
        memo=args.memo
    )
    
    if result['successful']:
        print("✅ Payment sent successfully!")
        print(format_transaction_result(result))
    else:
        print(f"❌ Payment failed: {result['error']}")

def bulk_command(args):
    """Handle bulk payment operations"""
    config = OGCConfig()
    processor = BulkPaymentProcessor(config)
    
    if args.action == "validate":
        if not args.file:
            print("Please provide CSV file with --file")
            return
        
        print(f"Validating CSV file: {args.file}")
        quick_validate_csv(args.file)
    
    elif args.action == "template":
        output_file = args.output or "payment_template.csv"
        sample_count = args.samples or 5
        
        create_payment_template(output_file, sample_count)
    
    elif args.action == "process":
        if not args.file:
            print("Please provide CSV file with --file")
            return
        
        if not args.secret:
            print("Please provide source account secret key with --secret")
            return
        
        print(f"Processing bulk payments from: {args.file}")
        
        result = processor.process_bulk_payments(
            file_path=args.file,
            source_secret=args.secret,
            batch_size=args.batch_size or 50,
            delay_between_batches=args.delay or 1.0,
            memo=args.memo,
            dry_run=args.dry_run
        )
        
        if result['successful']:
            print("✅ Bulk payment processing completed!")
        else:
            print(f"❌ Bulk payment processing failed: {result['error']}")
        
        # Generate report
        if args.report:
            report = processor.generate_payment_report(result, args.report)
            print(f"📊 Report saved to: {args.report}")

def report_command(args):
    """Handle transparency reporting"""
    config = OGCConfig()
    reporter = TransparencyReporter(config)
    
    if args.action == "stats":
        generate_current_stats()
    
    elif args.action == "monthly":
        if args.year and args.month:
            generate_report_for_month(args.year, args.month)
        else:
            # Generate for current month
            from datetime import datetime
            now = datetime.now()
            generate_report_for_month(now.year, now.month)
    
    elif args.action == "previous":
        from datetime import datetime
        now = datetime.now()
        if now.month == 1:
            prev_year = now.year - 1
            prev_month = 12
        else:
            prev_year = now.year
            prev_month = now.month - 1
        generate_report_for_month(prev_year, prev_month)

def fund_command(args):
    """Handle fund operations"""
    try:
        fund = OpenBuildFund()
        
        if args.action == "balance":
            result = fund.get_fund_account_balance()
            if result['success']:
                print("Open Build Fund Balance:")
                for balance in result['balances']:
                    print(f"  {balance['asset_code']}: {balance['balance']}")
            else:
                print(f"❌ Error getting fund balance: {result['error']}")
        
        elif args.action == "calculate":
            if not args.amount:
                print("Please provide --amount for calculation")
                return
            
            result = calculate_transaction_with_fund_fee(float(args.amount))
            print(f"Transaction Amount: {args.amount} OGC")
            print(f"Fund Fee (0.1%): {result['fund_fee']} OGC")
            print(f"Net Amount: {result['net_amount']} OGC")
            
        elif args.action == "send":
            if not all([args.amount, args.source_secret, args.destination]):
                print("Please provide --amount, --source-secret, and --destination")
                return
            
            result = fund.send_payment_with_fund_fee(
                args.source_secret, 
                args.destination, 
                float(args.amount),
                memo=args.memo
            )
            
            if result['success']:
                print("✅ Payment sent successfully!")
                print(f"Net amount sent: {result['net_amount']} OGC")
                print(f"Fund fee: {result['fund_fee']} OGC")
            else:
                print(f"❌ Payment failed: {result['error']}")
        
        elif args.action == "report":
            print("Generating fund report...")
            fund.generate_fund_report()
            print("✅ Fund report generated")
        
        elif args.action == "proposal":
            print(fund.create_funding_proposal())
    
    except Exception as e:
        print(f"❌ Fund operation failed: {str(e)}")

def status_command(args):
    """Handle status command"""
    print("🔍 OGC Token Network Status")
    print("=" * 40)
    
    config = OGCConfig()
    
    # Network information
    network_emoji = "🌍" if config.STELLAR_NETWORK in ["public", "mainnet"] else "🧪"
    print(f"{network_emoji} Network: {config.STELLAR_NETWORK.upper()}")
    print(f"🔗 Horizon URL: {config.HORIZON_URL}")
    print(f"🔑 Network: {config.NETWORK_PASSPHRASE[:30]}...")
    print(f"🪙 Token Code: {config.TOKEN_CODE}")
    print(f"💰 Total Supply: {config.TOTAL_SUPPLY:,}")
    
    if config.ISSUER_PUBLIC_KEY:
        print(f"\n📋 Issuer: {config.ISSUER_PUBLIC_KEY}")
        
        # Check if we can connect to the network
        try:
            manager = StellarManager(config)
            # Try to load the issuer account to verify it exists
            account_data = manager.server.accounts().account_id(config.ISSUER_PUBLIC_KEY).call()
            print(f"✅ Issuer account exists and is funded")
            
            # Check native balance
            for balance in account_data['balances']:
                if balance['asset_type'] == 'native':
                    print(f"💎 XLM Balance: {balance['balance']}")
                    break
            
            # Check for OGC asset
            ogc_found = False
            for balance in account_data['balances']:
                if balance.get('asset_code') == config.TOKEN_CODE:
                    print(f"🪙 {config.TOKEN_CODE} Balance: {balance['balance']}")
                    ogc_found = True
                    break
            
            if not ogc_found:
                print(f"⚠️  {config.TOKEN_CODE} asset not found in issuer account")
                
        except Exception as e:
            print(f"❌ Error connecting to network: {e}")
    else:
        print(f"⚠️  No issuer account configured")
    
    # Network-specific information
    if config.STELLAR_NETWORK == 'testnet':
        print(f"\n🧪 TESTNET MODE")
        print(f"• This is for testing only")
        print(f"• Tokens have no real value")
        print(f"• Free XLM available via Friendbot")
        print(f"• To move to mainnet: python deploy_mainnet.py")
    else:
        print(f"\n🌍 MAINNET MODE - LIVE PRODUCTION")  
        print(f"• This is the LIVE production network")
        print(f"• Tokens have REAL value")
        print(f"• Real XLM required for transactions")
        if config.ISSUER_PUBLIC_KEY:
            print(f"• Stellar Expert: https://stellar.expert/explorer/public/account/{config.ISSUER_PUBLIC_KEY}")
    
    print(f"\n� Use 'python cli.py --help' to see all available commands")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="OGCoin Management Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup configuration
  python cli.py config --interactive

  # Create new account
  python cli.py account create

  # Get account info
  python cli.py account info --address GXXXXX...

  # Fund testnet account
  python cli.py account fund --address GXXXXX...

  # Create trustline
  python cli.py trustline create --secret SXXXXX...

  # Send payment
  python cli.py payment --secret SXXXXX... --destination GXXXXX... --amount 100.5

  # Validate bulk payment file
  python cli.py bulk validate --file payments.csv

  # Process bulk payments (dry run)
  python cli.py bulk process --file payments.csv --secret SXXXXX... --dry-run

  # Generate transparency report
  python cli.py report monthly --year 2024 --month 1

  # Get current stats
  python cli.py report stats

  # Check Open Build fund balance
  python cli.py fund balance

  # Calculate transaction fee for 100 OGC
  python cli.py fund calculate --amount 100

  # Send transaction with fund contribution
  python cli.py fund send --source-secret SXXXXX... --destination GXXXXX... --amount 50

  # Generate fund report
  python cli.py fund report
        """
    )
    
    parser.add_argument(
        '--config', 
        help='Configuration file path'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('--interactive', action='store_true', help='Interactive setup')
    config_parser.set_defaults(func=setup_config_command)
    
    # Account command
    account_parser = subparsers.add_parser('account', help='Account operations')
    account_parser.add_argument('action', choices=['create', 'info', 'fund'], help='Account action')
    account_parser.add_argument('--address', help='Account address')
    account_parser.set_defaults(func=account_command)
    
    # Trustline command
    trustline_parser = subparsers.add_parser('trustline', help='Trustline operations')
    trustline_parser.add_argument('action', choices=['create', 'remove'], help='Trustline action')
    trustline_parser.add_argument('--secret', help='Account secret key')
    trustline_parser.set_defaults(func=trustline_command)
    
    # Payment command
    payment_parser = subparsers.add_parser('payment', help='Send payments')
    payment_parser.add_argument('--secret', required=True, help='Source account secret key')
    payment_parser.add_argument('--destination', required=True, help='Destination address')
    payment_parser.add_argument('--amount', required=True, help='Payment amount')
    payment_parser.add_argument('--memo', help='Payment memo')
    payment_parser.set_defaults(func=payment_command)
    
    # Bulk payment command
    bulk_parser = subparsers.add_parser('bulk', help='Bulk payment operations')
    bulk_parser.add_argument('action', choices=['validate', 'template', 'process'], help='Bulk action')
    bulk_parser.add_argument('--file', help='CSV file path')
    bulk_parser.add_argument('--secret', help='Source account secret key')
    bulk_parser.add_argument('--output', help='Output file path')
    bulk_parser.add_argument('--samples', type=int, help='Number of template samples')
    bulk_parser.add_argument('--batch-size', type=int, help='Batch size for processing')
    bulk_parser.add_argument('--delay', type=float, help='Delay between batches (seconds)')
    bulk_parser.add_argument('--memo', help='Transaction memo')
    bulk_parser.add_argument('--dry-run', action='store_true', help='Simulate without executing')
    bulk_parser.add_argument('--report', help='Generate report to file')
    bulk_parser.set_defaults(func=bulk_command)
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Transparency reporting')
    report_parser.add_argument('action', choices=['stats', 'monthly', 'previous'], help='Report action')
    report_parser.add_argument('--year', type=int, help='Report year')
    report_parser.add_argument('--month', type=int, help='Report month')
    report_parser.set_defaults(func=report_command)
    
    # Fund command
    fund_parser = subparsers.add_parser('fund', help='Open Build fund operations')
    fund_parser.add_argument('action', choices=['balance', 'calculate', 'send', 'report', 'proposal'], help='Fund action')
    fund_parser.add_argument('--amount', help='Amount for calculations or transactions')
    fund_parser.add_argument('--source-secret', help='Source account secret key for fund transactions')
    fund_parser.add_argument('--destination', help='Destination address for fund transactions')
    fund_parser.add_argument('--memo', help='Transaction memo')
    fund_parser.set_defaults(func=fund_command)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check network and configuration status')
    status_parser.set_defaults(func=status_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    try:
        # Call the appropriate command function
        args.func(args)
    
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()