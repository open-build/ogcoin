"""
Transparency reporting for OGCoin
Generates monthly reports for public transparency
"""

import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from decimal import Decimal
import logging

# Import with fallback for missing dependencies
try:
    from stellar_sdk import Server, Asset
    STELLAR_SDK_AVAILABLE = True
except ImportError:
    STELLAR_SDK_AVAILABLE = False
    print("Warning: stellar-sdk not installed. Install with: pip install stellar-sdk")

from config import Config as OGCConfig
from formatters import format_transparency_report, format_json_report, format_stellar_amount

class TransparencyReporter:
    """Generate transparency reports for OGC token"""
    
    def __init__(self, config: OGCConfig):
        """Initialize reporter with configuration
        
        Args:
            config: OGCConfig instance
        """
        if not STELLAR_SDK_AVAILABLE:
            raise ImportError("stellar-sdk is required. Install with: pip install stellar-sdk")
        
        self.config = config
        self.server = Server(config.get_horizon_url())
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_token_supply_info(self) -> Dict[str, Any]:
        """Get current token supply information
        
        Returns:
            Supply information
        """
        try:
            issuer_address = self.config.get('issuer_address')
            token_code = self.config.get('token_code', 'OGC')
            
            # Get issuer account info
            issuer_account = self.server.accounts().account_id(issuer_address).call()
            
            # Find OGC balance in issuer account (this represents unissued tokens)
            issuer_balance = Decimal('0')
            for balance in issuer_account.get('balances', []):
                if (balance.get('asset_code') == token_code and 
                    balance.get('asset_issuer') == issuer_address):
                    issuer_balance = Decimal(balance['balance'])
                    break
            
            # Get asset information from Stellar
            ogc_asset = Asset(token_code, issuer_address)
            
            # For now, we'll use configured total supply
            # In practice, you might track this differently
            total_supply = Decimal(self.config.get('total_supply', '1000000000'))
            circulating_supply = total_supply - issuer_balance
            
            return {
                'token_code': token_code,
                'issuer_address': issuer_address,
                'total_supply': str(total_supply),
                'circulating_supply': str(circulating_supply),
                'issuer_balance': str(issuer_balance),
                'supply_percentage': float((circulating_supply / total_supply) * 100) if total_supply > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting supply info: {e}")
            return {
                'error': str(e),
                'token_code': self.config.get('token_code', 'OGC'),
                'issuer_address': self.config.get('issuer_address', 'Unknown')
            }
    
    def get_account_transactions(self, account_id: str, limit: int = 200, 
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get transactions for an account in time range
        
        Args:
            account_id: Account public key
            limit: Maximum transactions to fetch
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of transactions
        """
        try:
            # Build query
            transactions_call = self.server.transactions().for_account(account_id).limit(limit).order(desc=True)
            
            all_transactions = []
            
            # Fetch transactions
            response = transactions_call.call()
            transactions = response.get('_embedded', {}).get('records', [])
            
            for tx in transactions:
                tx_time = datetime.fromisoformat(tx['created_at'].replace('Z', '+00:00'))
                
                # Filter by time range if provided
                if start_time and tx_time < start_time:
                    continue
                if end_time and tx_time > end_time:
                    break
                
                all_transactions.append(tx)
            
            return all_transactions
            
        except Exception as e:
            self.logger.error(f"Error fetching transactions for {account_id}: {e}")
            return []
    
    def analyze_token_transactions(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Analyze OGC token transactions in time period
        
        Args:
            start_time: Start of analysis period
            end_time: End of analysis period
            
        Returns:
            Transaction analysis
        """
        try:
            token_code = self.config.get('token_code', 'OGC')
            issuer_address = self.config.get('issuer_address')
            
            # Get issuer transactions (most token activity flows through here)
            issuer_transactions = self.get_account_transactions(
                issuer_address, limit=1000, start_time=start_time, end_time=end_time
            )
            
            # Analyze transactions
            payment_count = 0
            total_volume = Decimal('0')
            large_transactions = []
            transaction_sizes = []
            
            for tx in issuer_transactions:
                # Get operations for this transaction
                try:
                    ops_response = self.server.operations().for_transaction(tx['hash']).call()
                    operations = ops_response.get('_embedded', {}).get('records', [])
                    
                    for op in operations:
                        # Look for payment operations involving OGC
                        if op.get('type') == 'payment':
                            asset_code = op.get('asset_code')
                            asset_issuer = op.get('asset_issuer')
                            
                            if asset_code == token_code and asset_issuer == issuer_address:
                                payment_count += 1
                                amount = Decimal(op.get('amount', '0'))
                                total_volume += amount
                                transaction_sizes.append(amount)
                                
                                # Track large transactions (>1000 OGC)
                                if amount > 1000:
                                    large_transactions.append({
                                        'hash': tx['hash'],
                                        'created_at': tx['created_at'],
                                        'from': op.get('from'),
                                        'to': op.get('to'),
                                        'amount': str(amount)
                                    })
                    
                except Exception as e:
                    self.logger.warning(f"Error analyzing transaction {tx['hash']}: {e}")
                    continue
            
            # Calculate statistics
            avg_transaction_size = total_volume / payment_count if payment_count > 0 else Decimal('0')
            
            return {
                'period_start': start_time.isoformat(),
                'period_end': end_time.isoformat(),
                'transaction_count': len(issuer_transactions),
                'payment_count': payment_count,
                'total_volume': str(total_volume),
                'avg_transaction_size': str(avg_transaction_size),
                'large_transactions': large_transactions[:20],  # Top 20
                'max_transaction': str(max(transaction_sizes)) if transaction_sizes else '0',
                'min_transaction': str(min(transaction_sizes)) if transaction_sizes else '0'
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing transactions: {e}")
            return {
                'error': str(e),
                'period_start': start_time.isoformat() if start_time else None,
                'period_end': end_time.isoformat() if end_time else None
            }
    
    def get_top_token_holders(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get top token holders (this is challenging on Stellar without indexing)
        
        Args:
            limit: Maximum holders to return
            
        Returns:
            List of top holders
        """
        # Note: Getting all token holders on Stellar requires scanning all accounts
        # This is computationally expensive and typically done by indexing services
        # For this example, we'll return a placeholder
        
        self.logger.warning("Top holders analysis requires comprehensive account scanning")
        self.logger.warning("Consider using a Stellar indexing service for production use")
        
        return [
            {
                'address': 'PLACEHOLDER_ADDRESS_1',
                'balance': '1000000.0000000',
                'percentage': 10.0,
                'note': 'Data not available - requires account scanning'
            }
        ]
    
    def generate_monthly_report(self, year: int, month: int, 
                              output_dir: str = "reports") -> Dict[str, Any]:
        """Generate monthly transparency report
        
        Args:
            year: Report year
            month: Report month (1-12)
            output_dir: Directory to save reports
            
        Returns:
            Report data and file paths
        """
        try:
            # Calculate time range for the month
            start_time = datetime(year, month, 1, tzinfo=timezone.utc)
            if month == 12:
                end_time = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                end_time = datetime(year, month + 1, 1, tzinfo=timezone.utc)
            
            self.logger.info(f"Generating report for {year}-{month:02d}")
            
            # Gather data
            supply_info = self.get_token_supply_info()
            transaction_analysis = self.analyze_token_transactions(start_time, end_time)
            top_holders = self.get_top_token_holders()
            
            # Compile report data
            report_data = {
                'report_type': 'monthly_transparency',
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'period': f"{year}-{month:02d}",
                'period_start': start_time.isoformat(),
                'period_end': end_time.isoformat(),
                
                # Token information
                'token_code': supply_info.get('token_code', 'OGC'),
                'issuer_address': supply_info.get('issuer_address'),
                'total_supply': supply_info.get('total_supply', '0'),
                'circulating_supply': supply_info.get('circulating_supply', '0'),
                'holder_count': len(top_holders),
                
                # Transaction data
                'transaction_count': transaction_analysis.get('transaction_count', 0),
                'payment_count': transaction_analysis.get('payment_count', 0),
                'total_volume': transaction_analysis.get('total_volume', '0'),
                'avg_transaction_size': transaction_analysis.get('avg_transaction_size', '0'),
                'recent_transactions': transaction_analysis.get('large_transactions', []),
                
                # Top holders
                'top_holders': top_holders,
                
                # Network information
                'network': self.config.get('network', 'public'),
                'horizon_url': self.config.get_horizon_url()
            }
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Generate file names
            date_str = f"{year}-{month:02d}"
            json_file = output_path / f"ogc_transparency_{date_str}.json"
            html_file = output_path / f"ogc_transparency_{date_str}.html"
            
            # Save JSON report
            with open(json_file, 'w', encoding='utf-8') as f:
                f.write(format_json_report(report_data))
            
            # Generate and save HTML report
            html_content = format_transparency_report(report_data)
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Reports saved:")
            self.logger.info(f"  JSON: {json_file}")
            self.logger.info(f"  HTML: {html_file}")
            
            return {
                'successful': True,
                'report_data': report_data,
                'json_file': str(json_file),
                'html_file': str(html_file),
                'period': date_str
            }
            
        except Exception as e:
            self.logger.error(f"Error generating monthly report: {e}")
            return {
                'successful': False,
                'error': str(e),
                'period': f"{year}-{month:02d}"
            }
    
    def generate_current_month_report(self, output_dir: str = "reports") -> Dict[str, Any]:
        """Generate report for current month
        
        Args:
            output_dir: Directory to save reports
            
        Returns:
            Report result
        """
        now = datetime.now(timezone.utc)
        return self.generate_monthly_report(now.year, now.month, output_dir)
    
    def generate_previous_month_report(self, output_dir: str = "reports") -> Dict[str, Any]:
        """Generate report for previous month
        
        Args:
            output_dir: Directory to save reports
            
        Returns:
            Report result
        """
        now = datetime.now(timezone.utc)
        
        # Calculate previous month
        if now.month == 1:
            prev_year = now.year - 1
            prev_month = 12
        else:
            prev_year = now.year
            prev_month = now.month - 1
        
        return self.generate_monthly_report(prev_year, prev_month, output_dir)
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time token statistics
        
        Returns:
            Current statistics
        """
        try:
            supply_info = self.get_token_supply_info()
            
            # Get recent transactions (last 24 hours)
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=1)
            
            recent_analysis = self.analyze_token_transactions(start_time, end_time)
            
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'supply_info': supply_info,
                'last_24h': {
                    'transaction_count': recent_analysis.get('transaction_count', 0),
                    'payment_count': recent_analysis.get('payment_count', 0),
                    'total_volume': recent_analysis.get('total_volume', '0'),
                    'avg_transaction_size': recent_analysis.get('avg_transaction_size', '0')
                },
                'network': self.config.get('network', 'public')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting real-time stats: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def create_annual_summary(self, year: int, output_dir: str = "reports") -> Dict[str, Any]:
        """Create annual summary report
        
        Args:
            year: Year to summarize
            output_dir: Output directory
            
        Returns:
            Annual summary result
        """
        try:
            self.logger.info(f"Creating annual summary for {year}")
            
            # Calculate year range
            start_time = datetime(year, 1, 1, tzinfo=timezone.utc)
            end_time = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
            
            # Get annual data
            supply_info = self.get_token_supply_info()
            annual_analysis = self.analyze_token_transactions(start_time, end_time)
            
            # Compile annual data
            annual_data = {
                'report_type': 'annual_summary',
                'year': year,
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'token_code': supply_info.get('token_code', 'OGC'),
                'issuer_address': supply_info.get('issuer_address'),
                'total_supply': supply_info.get('total_supply', '0'),
                'circulating_supply': supply_info.get('circulating_supply', '0'),
                'annual_transactions': annual_analysis.get('transaction_count', 0),
                'annual_payments': annual_analysis.get('payment_count', 0),
                'annual_volume': annual_analysis.get('total_volume', '0'),
                'largest_transaction': annual_analysis.get('max_transaction', '0'),
                'network': self.config.get('network', 'public')
            }
            
            # Save annual report
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            json_file = output_path / f"ogc_annual_summary_{year}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                f.write(format_json_report(annual_data))
            
            self.logger.info(f"Annual summary saved: {json_file}")
            
            return {
                'successful': True,
                'annual_data': annual_data,
                'json_file': str(json_file),
                'year': year
            }
            
        except Exception as e:
            self.logger.error(f"Error creating annual summary: {e}")
            return {
                'successful': False,
                'error': str(e),
                'year': year
            }

# Utility functions
def generate_report_for_month(year: int, month: int) -> None:
    """Generate transparency report for specific month
    
    Args:
        year: Report year
        month: Report month
    """
    try:
        config = OGCConfig()
        reporter = TransparencyReporter(config)
        
        result = reporter.generate_monthly_report(year, month)
        
        if result['successful']:
            print(f"✅ Report generated for {result['period']}")
            print(f"HTML: {result['html_file']}")
            print(f"JSON: {result['json_file']}")
        else:
            print(f"❌ Report generation failed: {result['error']}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def generate_current_stats() -> None:
    """Generate current token statistics"""
    try:
        config = OGCConfig()
        reporter = TransparencyReporter(config)
        
        stats = reporter.get_real_time_stats()
        
        if 'error' in stats:
            print(f"❌ Error: {stats['error']}")
            return
        
        supply_info = stats['supply_info']
        last_24h = stats['last_24h']
        
        print("OGC Token Statistics")
        print("=" * 30)
        print(f"Total Supply: {format_stellar_amount(supply_info.get('total_supply', '0'))} OGC")
        print(f"Circulating: {format_stellar_amount(supply_info.get('circulating_supply', '0'))} OGC")
        print(f"Supply %: {supply_info.get('supply_percentage', 0):.2f}%")
        print("")
        print("Last 24 Hours:")
        print(f"  Transactions: {last_24h['transaction_count']}")
        print(f"  Payments: {last_24h['payment_count']}")
        print(f"  Volume: {format_stellar_amount(last_24h['total_volume'])} OGC")
        print(f"  Avg Size: {format_stellar_amount(last_24h['avg_transaction_size'])} OGC")
        print("")
        print(f"Network: {stats['network']}")
        print(f"Updated: {stats['timestamp']}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python transparency_reporter.py stats")
        print("  python transparency_reporter.py report <year> <month>")
        print("  python transparency_reporter.py current")
        print("  python transparency_reporter.py previous")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "stats":
        generate_current_stats()
    
    elif command == "report":
        if len(sys.argv) < 4:
            print("Please provide year and month")
            sys.exit(1)
        year = int(sys.argv[2])
        month = int(sys.argv[3])
        generate_report_for_month(year, month)
    
    elif command == "current":
        now = datetime.now()
        generate_report_for_month(now.year, now.month)
    
    elif command == "previous":
        now = datetime.now()
        if now.month == 1:
            prev_year = now.year - 1
            prev_month = 12
        else:
            prev_year = now.year
            prev_month = now.month - 1
        generate_report_for_month(prev_year, prev_month)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)