"""
Bulk payment processor for OGCoin
Processes CSV files for batch token distributions
"""

import csv
import time
from typing import Dict, List, Any, Optional, Generator
from pathlib import Path
from decimal import Decimal
import logging

# Import with fallback for missing dependencies
try:
    from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Asset
    from stellar_sdk.exceptions import SdkError
    STELLAR_SDK_AVAILABLE = True
except ImportError:
    STELLAR_SDK_AVAILABLE = False
    print("Warning: stellar-sdk not installed. Install with: pip install stellar-sdk")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from config import Config as OGCConfig
from validators import validate_csv_row, validate_bulk_payment_file
from formatters import format_progress_bar, format_payment_batch_result, format_stellar_amount

class BulkPaymentProcessor:
    """Process bulk payments from CSV files"""
    
    def __init__(self, config: OGCConfig):
        """Initialize processor with configuration
        
        Args:
            config: OGCConfig instance
        """
        if not STELLAR_SDK_AVAILABLE:
            raise ImportError("stellar-sdk is required. Install with: pip install stellar-sdk")
        
        self.config = config
        self.server = Server(config.get_horizon_url())
        self.network_passphrase = config.get_network_passphrase()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_csv_file(self, file_path: str, validate: bool = True) -> List[Dict[str, Any]]:
        """Load and parse CSV file
        
        Args:
            file_path: Path to CSV file
            validate: Whether to validate the file first
            
        Returns:
            List of payment records
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Validate file if requested
        if validate:
            validation = validate_bulk_payment_file(str(file_path))
            if not validation['valid']:
                error_msg = "CSV validation failed:\n" + "\n".join(validation['errors'])
                raise ValueError(error_msg)
        
        # Load the file
        payments = []
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                # Auto-detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):
                    # Clean up the row data
                    cleaned_row = {k.strip(): v.strip() for k, v in row.items() if v.strip()}
                    
                    # Add row number for error tracking
                    cleaned_row['_row_number'] = row_num
                    
                    payments.append(cleaned_row)
        
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")
        
        self.logger.info(f"Loaded {len(payments)} payment records from {file_path}")
        return payments
    
    def validate_payments(self, payments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate all payments in the list
        
        Args:
            payments: List of payment records
            
        Returns:
            Validation summary
        """
        valid_payments = []
        invalid_payments = []
        total_amount = Decimal('0')
        
        for payment in payments:
            validation = validate_csv_row(payment)
            
            if validation['valid']:
                valid_payments.append(payment)
                try:
                    total_amount += Decimal(payment['amount'])
                except:
                    pass
            else:
                payment['_validation_errors'] = validation['errors']
                invalid_payments.append(payment)
        
        return {
            'total_payments': len(payments),
            'valid_payments': len(valid_payments),
            'invalid_payments': len(invalid_payments),
            'total_amount': str(total_amount),
            'valid_records': valid_payments,
            'invalid_records': invalid_payments
        }
    
    def estimate_fees(self, payment_count: int) -> Dict[str, str]:
        """Estimate transaction fees for bulk payments
        
        Args:
            payment_count: Number of payments
            
        Returns:
            Fee estimates in XLM
        """
        # Stellar base fee is typically 100 stroops (0.00001 XLM) per operation
        base_fee = Decimal('0.00001')
        
        # Batch payments can be grouped into transactions
        # Each transaction can have up to 100 operations
        max_ops_per_tx = 100
        
        # Calculate number of transactions needed
        tx_count = (payment_count + max_ops_per_tx - 1) // max_ops_per_tx
        
        # Estimate fees (conservative estimate with 2x multiplier for network congestion)
        estimated_fee_per_tx = base_fee * max_ops_per_tx * 2
        total_estimated_fee = estimated_fee_per_tx * tx_count
        
        return {
            'payment_count': str(payment_count),
            'transaction_count': str(tx_count),
            'estimated_fee_per_tx': str(estimated_fee_per_tx),
            'total_estimated_fee': str(total_estimated_fee),
            'max_operations_per_tx': str(max_ops_per_tx)
        }
    
    def prepare_payment_batches(self, payments: List[Dict[str, Any]], batch_size: int = 50) -> List[List[Dict[str, Any]]]:
        """Split payments into batches for processing
        
        Args:
            payments: List of payment records
            batch_size: Number of payments per batch (max 100 for Stellar)
            
        Returns:
            List of payment batches
        """
        if batch_size > 100:
            batch_size = 100  # Stellar limit
        
        batches = []
        for i in range(0, len(payments), batch_size):
            batch = payments[i:i + batch_size]
            batches.append(batch)
        
        self.logger.info(f"Created {len(batches)} batches with up to {batch_size} payments each")
        return batches
    
    def execute_payment_batch(self, payments: List[Dict[str, Any]], source_keypair: Keypair, 
                            memo: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
        """Execute a batch of payments in a single transaction
        
        Args:
            payments: List of payment records for this batch
            source_keypair: Source account keypair
            memo: Optional transaction memo
            dry_run: If True, don't actually submit transaction
            
        Returns:
            Batch execution result
        """
        if not payments:
            return {'successful': False, 'error': 'No payments provided'}
        
        try:
            # Load source account
            source_account = self.server.load_account(source_keypair.public_key)
            
            # Get OGC asset
            ogc_asset = Asset(
                code=self.config.get('token_code', 'OGC'),
                issuer=self.config.get('issuer_address')
            )
            
            # Build transaction
            transaction_builder = TransactionBuilder(
                source_account=source_account,
                network_passphrase=self.network_passphrase,
                base_fee=self.server.fetch_base_fee()
            )
            
            # Add memo if provided
            if memo:
                transaction_builder.add_text_memo(memo[:28])  # Stellar memo limit
            
            # Add payment operations
            for payment in payments:
                transaction_builder.add_payment_op(
                    destination=payment['address'],
                    asset=ogc_asset,
                    amount=payment['amount']
                )
            
            # Build and sign transaction
            transaction = transaction_builder.build()
            transaction.sign(source_keypair)
            
            if dry_run:
                return {
                    'successful': True,
                    'dry_run': True,
                    'operation_count': len(payments),
                    'estimated_fee': transaction.fee,
                    'transaction_xdr': transaction.to_xdr()
                }
            
            # Submit transaction
            response = self.server.submit_transaction(transaction)
            
            return {
                'successful': True,
                'hash': response['hash'],
                'fee_charged': response.get('fee_charged', transaction.fee),
                'operation_count': len(payments),
                'ledger': response.get('ledger'),
                'payments': payments
            }
            
        except Exception as e:
            self.logger.error(f"Batch payment failed: {e}")
            return {
                'successful': False,
                'error': str(e),
                'operation_count': len(payments),
                'payments': payments
            }
    
    def process_bulk_payments(self, file_path: str, source_secret: str, 
                            batch_size: int = 50, delay_between_batches: float = 1.0,
                            memo: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
        """Process bulk payments from CSV file
        
        Args:
            file_path: Path to CSV file
            source_secret: Source account secret key
            batch_size: Number of payments per transaction
            delay_between_batches: Delay in seconds between batches
            memo: Optional memo for all transactions
            dry_run: If True, don't actually submit transactions
            
        Returns:
            Processing results
        """
        start_time = time.time()
        
        try:
            # Load and validate payments
            payments = self.load_csv_file(file_path)
            validation = self.validate_payments(payments)
            
            if validation['invalid_payments'] > 0:
                self.logger.warning(f"Found {validation['invalid_payments']} invalid payments")
                if not dry_run:
                    # In production, we might want to stop here
                    raise ValueError(f"Cannot process file with {validation['invalid_payments']} invalid payments")
            
            valid_payments = validation['valid_records']
            
            # Estimate fees
            fee_estimate = self.estimate_fees(len(valid_payments))
            self.logger.info(f"Processing {len(valid_payments)} payments in ~{fee_estimate['transaction_count']} transactions")
            self.logger.info(f"Estimated total fees: {fee_estimate['total_estimated_fee']} XLM")
            
            # Create source keypair
            source_keypair = Keypair.from_secret(source_secret)
            
            # Split into batches
            batches = self.prepare_payment_batches(valid_payments, batch_size)
            
            # Process each batch
            batch_results = []
            successful_payments = 0
            failed_payments = 0
            total_fees = Decimal('0')
            
            for i, batch in enumerate(batches):
                self.logger.info(f"Processing batch {i+1}/{len(batches)} ({len(batch)} payments)")
                
                # Show progress
                progress = format_progress_bar(i, len(batches))
                print(f"\rProgress: {progress}", end='', flush=True)
                
                # Execute batch
                batch_memo = f"{memo} (batch {i+1})" if memo else f"Bulk payment batch {i+1}"
                result = self.execute_payment_batch(batch, source_keypair, batch_memo, dry_run)
                
                batch_results.append(result)
                
                if result['successful']:
                    successful_payments += len(batch)
                    if not dry_run:
                        total_fees += Decimal(str(result.get('fee_charged', 0)))
                else:
                    failed_payments += len(batch)
                    self.logger.error(f"Batch {i+1} failed: {result.get('error', 'Unknown error')}")
                
                # Delay between batches to avoid rate limiting
                if i < len(batches) - 1 and delay_between_batches > 0:
                    time.sleep(delay_between_batches)
            
            # Final progress
            progress = format_progress_bar(len(batches), len(batches))
            print(f"\rProgress: {progress}")
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Compile results
            results = {
                'successful': failed_payments == 0,
                'total_payments': validation['total_payments'],
                'valid_payments': validation['valid_payments'],
                'invalid_payments': validation['invalid_payments'],
                'successful_payments': successful_payments,
                'failed_payments': failed_payments,
                'total_batches': len(batches),
                'successful_batches': sum(1 for r in batch_results if r['successful']),
                'failed_batches': sum(1 for r in batch_results if not r['successful']),
                'total_amount': validation['total_amount'],
                'total_fees': str(total_fees),
                'duration': duration,
                'dry_run': dry_run,
                'batch_results': batch_results
            }
            
            self.logger.info(f"Bulk payment processing completed in {duration:.1f}s")
            self.logger.info(f"Successful: {successful_payments}, Failed: {failed_payments}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Bulk payment processing failed: {e}")
            return {
                'successful': False,
                'error': str(e),
                'duration': time.time() - start_time
            }
    
    def generate_payment_report(self, results: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Generate a payment report
        
        Args:
            results: Results from process_bulk_payments
            output_file: Optional file to save report to
            
        Returns:
            Report text
        """
        lines = []
        lines.append("Bulk Payment Report")
        lines.append("=" * 50)
        lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
        lines.append("")
        
        # Summary
        lines.append("Summary:")
        lines.append(f"  Total Payments: {results['total_payments']}")
        lines.append(f"  Valid Payments: {results['valid_payments']}")
        lines.append(f"  Invalid Payments: {results['invalid_payments']}")
        lines.append(f"  Successful Payments: {results['successful_payments']}")
        lines.append(f"  Failed Payments: {results['failed_payments']}")
        lines.append(f"  Total Amount: {format_stellar_amount(results['total_amount'])} OGC")
        lines.append(f"  Total Fees: {format_stellar_amount(results['total_fees'])} XLM")
        lines.append(f"  Duration: {results['duration']:.2f} seconds")
        
        if results.get('dry_run'):
            lines.append("  Mode: DRY RUN (no actual transactions)")
        
        lines.append("")
        
        # Batch details
        lines.append("Batch Results:")
        batch_results = results.get('batch_results', [])
        
        for i, batch_result in enumerate(batch_results):
            status = "✅ SUCCESS" if batch_result['successful'] else "❌ FAILED"
            lines.append(f"  Batch {i+1}: {status}")
            
            if batch_result['successful']:
                if not results.get('dry_run'):
                    lines.append(f"    Hash: {batch_result.get('hash', 'N/A')}")
                    lines.append(f"    Fee: {format_stellar_amount(str(batch_result.get('fee_charged', 0)))} XLM")
                lines.append(f"    Operations: {batch_result.get('operation_count', 0)}")
            else:
                lines.append(f"    Error: {batch_result.get('error', 'Unknown')}")
        
        # Failed payment details
        failed_batches = [r for r in batch_results if not r['successful']]
        if failed_batches:
            lines.append("")
            lines.append("Failed Payment Details:")
            
            for batch_result in failed_batches:
                if 'payments' in batch_result:
                    for payment in batch_result['payments']:
                        recipient = payment.get('address', 'Unknown')
                        amount = payment.get('amount', '0')
                        lines.append(f"  {recipient[:8]}...{recipient[-8:]}: {amount} OGC")
        
        report_text = "\n".join(lines)
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            self.logger.info(f"Report saved to {output_file}")
        
        return report_text
    
    def create_template_csv(self, output_file: str, sample_count: int = 5) -> None:
        """Create a template CSV file for bulk payments
        
        Args:
            output_file: Path for output file
            sample_count: Number of sample rows to include
        """
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['address', 'amount', 'memo'])
            
            # Write sample rows
            for i in range(sample_count):
                sample_address = f"GXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX{i:02d}"
                sample_amount = f"{(i + 1) * 10}.00"
                sample_memo = f"Payment {i + 1}"
                
                writer.writerow([sample_address, sample_amount, sample_memo])
        
        self.logger.info(f"Template CSV created: {output_file}")

# Utility functions for use outside the class
def quick_validate_csv(file_path: str) -> None:
    """Quick validation of CSV file with formatted output
    
    Args:
        file_path: Path to CSV file
    """
    from formatters import format_csv_validation_result
    
    validation = validate_bulk_payment_file(file_path)
    print(format_csv_validation_result(validation))

def create_payment_template(output_file: str = "payment_template.csv", samples: int = 5) -> None:
    """Create a payment template CSV file
    
    Args:
        output_file: Output file path
        samples: Number of sample rows
    """
    # Create a minimal config for the processor
    config = OGCConfig()
    processor = BulkPaymentProcessor(config)
    processor.create_template_csv(output_file, samples)
    print(f"Payment template created: {output_file}")

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python bulk_payments.py validate <csv_file>")
        print("  python bulk_payments.py template [output_file] [sample_count]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "validate":
        if len(sys.argv) < 3:
            print("Please provide CSV file path")
            sys.exit(1)
        quick_validate_csv(sys.argv[2])
    
    elif command == "template":
        output_file = sys.argv[2] if len(sys.argv) > 2 else "payment_template.csv"
        sample_count = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        create_payment_template(output_file, sample_count)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)