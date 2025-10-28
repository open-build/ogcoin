"""
Output formatting utilities for OGCoin Stellar tools
Formats data for console output, reports, and web display
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from decimal import Decimal

def format_stellar_amount(amount: str, decimals: int = 7) -> str:
    """Format amount for display with proper precision
    
    Args:
        amount: Raw amount string
        decimals: Number of decimal places to show
        
    Returns:
        Formatted amount string
    """
    try:
        decimal_amount = Decimal(amount)
        return f"{decimal_amount:.{decimals}f}".rstrip('0').rstrip('.')
    except:
        return str(amount)

def format_account_info(account_info: Dict[str, Any]) -> str:
    """Format account information for console display
    
    Args:
        account_info: Account data from Stellar
        
    Returns:
        Formatted account information
    """
    lines = []
    lines.append("Account Information:")
    lines.append("=" * 50)
    
    # Basic info
    lines.append(f"Account ID: {account_info.get('account_id', 'N/A')}")
    lines.append(f"Sequence: {account_info.get('sequence', 'N/A')}")
    
    # Balances
    balances = account_info.get('balances', [])
    if balances:
        lines.append("\nBalances:")
        for balance in balances:
            asset_type = balance.get('asset_type', 'native')
            if asset_type == 'native':
                asset_name = 'XLM (Native)'
            else:
                asset_code = balance.get('asset_code', 'Unknown')
                asset_issuer = balance.get('asset_issuer', 'Unknown')
                asset_name = f"{asset_code} ({asset_issuer[:8]}...)"
            
            amount = format_stellar_amount(balance.get('balance', '0'))
            lines.append(f"  {asset_name}: {amount}")
    
    # Signers
    signers = account_info.get('signers', [])
    if len(signers) > 1:  # More than just the account itself
        lines.append("\nSigners:")
        for signer in signers:
            key = signer.get('key', 'Unknown')
            weight = signer.get('weight', 0)
            lines.append(f"  {key[:8]}... (weight: {weight})")
    
    # Thresholds
    thresholds = account_info.get('thresholds', {})
    if thresholds:
        lines.append("\nThresholds:")
        lines.append(f"  Low: {thresholds.get('low_threshold', 0)}")
        lines.append(f"  Medium: {thresholds.get('med_threshold', 0)}")
        lines.append(f"  High: {thresholds.get('high_threshold', 0)}")
    
    return "\n".join(lines)

def format_transaction_result(result: Dict[str, Any]) -> str:
    """Format transaction result for console display
    
    Args:
        result: Transaction result data
        
    Returns:
        Formatted transaction result
    """
    lines = []
    lines.append("Transaction Result:")
    lines.append("=" * 40)
    
    lines.append(f"Hash: {result.get('hash', 'N/A')}")
    lines.append(f"Status: {result.get('status', 'Unknown')}")
    
    if result.get('successful'):
        lines.append("✅ Transaction successful")
    else:
        lines.append("❌ Transaction failed")
        
        # Show error details if available
        if 'error' in result:
            lines.append(f"Error: {result['error']}")
    
    # Show operation details
    operations = result.get('operations', [])
    if operations:
        lines.append(f"\nOperations ({len(operations)}):")
        for i, op in enumerate(operations):
            op_type = op.get('type_i', 'Unknown')
            lines.append(f"  {i+1}. Type: {op_type}")
            
            # Payment operation details
            if op_type == 1:  # Payment
                amount = format_stellar_amount(op.get('amount', '0'))
                asset = op.get('asset_code', 'XLM')
                destination = op.get('to', 'Unknown')
                lines.append(f"     Payment: {amount} {asset} to {destination[:8]}...")
    
    # Network and fees
    if 'fee_charged' in result:
        fee = format_stellar_amount(result['fee_charged'])
        lines.append(f"\nFee Charged: {fee} XLM")
    
    return "\n".join(lines)

def format_payment_batch_result(results: List[Dict[str, Any]]) -> str:
    """Format batch payment results
    
    Args:
        results: List of payment results
        
    Returns:
        Formatted batch results summary
    """
    lines = []
    lines.append("Batch Payment Results:")
    lines.append("=" * 50)
    
    successful = sum(1 for r in results if r.get('successful', False))
    failed = len(results) - successful
    
    lines.append(f"Total Payments: {len(results)}")
    lines.append(f"Successful: {successful} ✅")
    lines.append(f"Failed: {failed} ❌")
    
    if failed > 0:
        lines.append("\nFailed Payments:")
        for i, result in enumerate(results):
            if not result.get('successful', False):
                recipient = result.get('recipient', 'Unknown')
                amount = result.get('amount', '0')
                error = result.get('error', 'Unknown error')
                lines.append(f"  {i+1}. {recipient[:8]}... - {amount} - {error}")
    
    return "\n".join(lines)

def format_csv_validation_result(validation: Dict[str, Any]) -> str:
    """Format CSV validation results
    
    Args:
        validation: Validation result from validators.py
        
    Returns:
        Formatted validation report
    """
    lines = []
    lines.append("CSV Validation Report:")
    lines.append("=" * 40)
    
    if validation['valid']:
        lines.append("✅ File is valid")
    else:
        lines.append("❌ File has errors")
    
    lines.append(f"Total Rows: {validation['total_rows']}")
    lines.append(f"Valid Rows: {validation['valid_rows']}")
    lines.append(f"Invalid Rows: {validation['invalid_rows']}")
    
    # Show general errors
    if validation.get('errors'):
        lines.append("\nGeneral Errors:")
        for error in validation['errors']:
            lines.append(f"  • {error}")
    
    # Show row-specific errors
    if validation.get('row_errors'):
        lines.append("\nRow Errors:")
        for row_error in validation['row_errors'][:10]:  # Limit to first 10
            lines.append(f"  Row {row_error['row']}:")
            for error in row_error['errors']:
                lines.append(f"    • {error}")
        
        if len(validation['row_errors']) > 10:
            lines.append(f"  ... and {len(validation['row_errors']) - 10} more rows with errors")
    
    # Show warnings
    if validation.get('warnings'):
        lines.append("\nWarnings:")
        for warning in validation['warnings'][:10]:  # Limit to first 10
            lines.append(f"  ⚠️  {warning}")
        
        if len(validation['warnings']) > 10:
            lines.append(f"  ... and {len(validation['warnings']) - 10} more warnings")
    
    return "\n".join(lines)

def format_balance_report(balances: List[Dict[str, Any]]) -> str:
    """Format balance report for multiple accounts
    
    Args:
        balances: List of account balance data
        
    Returns:
        Formatted balance report
    """
    lines = []
    lines.append("Balance Report:")
    lines.append("=" * 60)
    
    # Group by asset
    asset_totals = {}
    
    for account_balance in balances:
        account_id = account_balance.get('account_id', 'Unknown')
        account_balances = account_balance.get('balances', [])
        
        lines.append(f"\n{account_id[:8]}...{account_id[-8:]}:")
        
        for balance in account_balances:
            asset_type = balance.get('asset_type', 'native')
            amount = balance.get('balance', '0')
            
            if asset_type == 'native':
                asset_key = 'XLM'
                asset_display = 'XLM (Native)'
            else:
                asset_code = balance.get('asset_code', 'Unknown')
                asset_issuer = balance.get('asset_issuer', 'Unknown')
                asset_key = f"{asset_code}:{asset_issuer}"
                asset_display = f"{asset_code}"
            
            formatted_amount = format_stellar_amount(amount)
            lines.append(f"  {asset_display}: {formatted_amount}")
            
            # Track totals
            if asset_key not in asset_totals:
                asset_totals[asset_key] = Decimal('0')
            asset_totals[asset_key] += Decimal(amount)
    
    # Show totals
    if len(balances) > 1:
        lines.append("\nTotals Across All Accounts:")
        for asset_key, total in asset_totals.items():
            if ':' in asset_key:
                asset_display = asset_key.split(':')[0]
            else:
                asset_display = asset_key
            
            formatted_total = format_stellar_amount(str(total))
            lines.append(f"  {asset_display}: {formatted_total}")
    
    return "\n".join(lines)

def format_transparency_report(data: Dict[str, Any]) -> str:
    """Format transparency report for monthly publication
    
    Args:
        data: Report data with transactions, balances, etc.
        
    Returns:
        Formatted HTML report
    """
    # Generate timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OGC Transparency Report - {data.get('period', 'Unknown')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: #1f2937; color: white; padding: 20px; border-radius: 8px; }}
        .section {{ margin: 20px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f3f4f6; font-weight: bold; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-value {{ font-size: 1.5em; font-weight: bold; color: #059669; }}
        .metric-label {{ font-size: 0.9em; color: #6b7280; }}
        .footer {{ margin-top: 40px; font-size: 0.9em; color: #6b7280; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>OGC Token Transparency Report</h1>
        <p>Reporting Period: {data.get('period', 'Unknown')}</p>
        <p>Generated: {timestamp}</p>
    </div>
    
    <div class="section">
        <h2>Token Overview</h2>
        <div class="metric">
            <div class="metric-value">{format_stellar_amount(str(data.get('total_supply', 0)))}</div>
            <div class="metric-label">Total Supply</div>
        </div>
        <div class="metric">
            <div class="metric-value">{format_stellar_amount(str(data.get('circulating_supply', 0)))}</div>
            <div class="metric-label">Circulating Supply</div>
        </div>
        <div class="metric">
            <div class="metric-value">{data.get('holder_count', 0):,}</div>
            <div class="metric-label">Token Holders</div>
        </div>
    </div>
    
    <div class="section">
        <h2>Transaction Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Total Transactions</td>
                <td>{data.get('transaction_count', 0):,}</td>
            </tr>
            <tr>
                <td>Payment Transactions</td>
                <td>{data.get('payment_count', 0):,}</td>
            </tr>
            <tr>
                <td>Total Volume</td>
                <td>{format_stellar_amount(str(data.get('total_volume', 0)))} OGC</td>
            </tr>
            <tr>
                <td>Average Transaction Size</td>
                <td>{format_stellar_amount(str(data.get('avg_transaction_size', 0)))} OGC</td>
            </tr>
        </table>
    </div>
"""
    
    # Add top holders if available
    if data.get('top_holders'):
        html += """
    <div class="section">
        <h2>Top Token Holders</h2>
        <table>
            <tr>
                <th>Rank</th>
                <th>Account</th>
                <th>Balance</th>
                <th>% of Supply</th>
            </tr>
"""
        for i, holder in enumerate(data['top_holders'][:10]):  # Top 10
            address = holder.get('address', 'Unknown')
            balance = format_stellar_amount(str(holder.get('balance', 0)))
            percentage = holder.get('percentage', 0)
            
            html += f"""
            <tr>
                <td>{i+1}</td>
                <td>{address[:8]}...{address[-8:]}</td>
                <td>{balance} OGC</td>
                <td>{percentage:.2f}%</td>
            </tr>
"""
        
        html += "        </table>\n    </div>\n"
    
    # Add recent transactions if available
    if data.get('recent_transactions'):
        html += """
    <div class="section">
        <h2>Recent Large Transactions</h2>
        <table>
            <tr>
                <th>Date</th>
                <th>From</th>
                <th>To</th>
                <th>Amount</th>
                <th>Transaction</th>
            </tr>
"""
        for tx in data['recent_transactions'][:20]:  # Last 20 large transactions
            date = tx.get('created_at', 'Unknown')
            from_addr = tx.get('from', 'Unknown')
            to_addr = tx.get('to', 'Unknown')
            amount = format_stellar_amount(str(tx.get('amount', 0)))
            tx_hash = tx.get('hash', 'Unknown')
            
            html += f"""
            <tr>
                <td>{date[:10]}</td>
                <td>{from_addr[:8]}...{from_addr[-6:]}</td>
                <td>{to_addr[:8]}...{to_addr[-6:]}</td>
                <td>{amount} OGC</td>
                <td><a href="https://stellarchain.io/tx/{tx_hash}" target="_blank">{tx_hash[:8]}...</a></td>
            </tr>
"""
        
        html += "        </table>\n    </div>\n"
    
    html += f"""
    <div class="footer">
        <p>This report is automatically generated from the Stellar blockchain. All data is publicly verifiable.</p>
        <p>OGC Token Issuer: {data.get('issuer_address', 'Unknown')}</p>
        <p>Report generated at: {timestamp}</p>
    </div>
</body>
</html>
"""
    
    return html

def format_json_report(data: Dict[str, Any], indent: int = 2) -> str:
    """Format data as pretty JSON for API responses
    
    Args:
        data: Data to format
        indent: JSON indentation
        
    Returns:
        Pretty formatted JSON string
    """
    def decimal_serializer(obj):
        if isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    return json.dumps(data, indent=indent, default=decimal_serializer)

def format_table(data: List[Dict[str, Any]], headers: Optional[List[str]] = None) -> str:
    """Format data as ASCII table
    
    Args:
        data: List of dictionaries to format
        headers: Optional list of headers to use
        
    Returns:
        Formatted ASCII table
    """
    if not data:
        return "No data to display"
    
    # Use provided headers or extract from first row
    if headers is None:
        headers = list(data[0].keys()) if data else []
    
    # Calculate column widths
    col_widths = {}
    for header in headers:
        col_widths[header] = len(header)
        for row in data:
            value = str(row.get(header, ''))
            col_widths[header] = max(col_widths[header], len(value))
    
    lines = []
    
    # Header row
    header_line = "| " + " | ".join(h.ljust(col_widths[h]) for h in headers) + " |"
    lines.append(header_line)
    
    # Separator
    separator = "|-" + "-|-".join("-" * col_widths[h] for h in headers) + "-|"
    lines.append(separator)
    
    # Data rows
    for row in data:
        data_line = "| " + " | ".join(str(row.get(h, '')).ljust(col_widths[h]) for h in headers) + " |"
        lines.append(data_line)
    
    return "\n".join(lines)

def format_progress_bar(current: int, total: int, width: int = 50) -> str:
    """Format progress bar for long operations
    
    Args:
        current: Current progress
        total: Total items
        width: Progress bar width
        
    Returns:
        Formatted progress bar
    """
    if total == 0:
        percentage = 0
    else:
        percentage = min(100, int((current / total) * 100))
    
    filled = int((percentage / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    
    return f"[{bar}] {percentage:3d}% ({current}/{total})"

def format_file_size(bytes_size: int) -> str:
    """Format file size in human readable format
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def format_duration(seconds: float) -> str:
    """Format duration in human readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"