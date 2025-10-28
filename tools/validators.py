"""
Input validation utilities for OGCoin Stellar tools
Validates addresses, amounts, and other inputs for security
"""

import re
from typing import Optional, List, Dict, Any
from decimal import Decimal, InvalidOperation

def validate_stellar_address(address: str) -> bool:
    """Validate Stellar account address format
    
    Args:
        address: Stellar public key to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not address or not isinstance(address, str):
        return False
    
    # Stellar addresses start with G and are 56 characters
    if not address.startswith('G') or len(address) != 56:
        return False
    
    # Check if all characters are valid base32
    valid_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
    return all(c in valid_chars for c in address)

def validate_stellar_secret(secret: str) -> bool:
    """Validate Stellar secret key format
    
    Args:
        secret: Stellar secret key to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not secret or not isinstance(secret, str):
        return False
    
    # Stellar secrets start with S and are 56 characters
    if not secret.startswith('S') or len(secret) != 56:
        return False
    
    # Check if all characters are valid base32
    valid_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
    return all(c in valid_chars for c in secret)

def validate_amount(amount: str) -> bool:
    """Validate amount format for Stellar transactions
    
    Args:
        amount: Amount string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not amount or not isinstance(amount, str):
        return False
    
    try:
        decimal_amount = Decimal(amount)
        
        # Must be positive
        if decimal_amount <= 0:
            return False
        
        # Must have at most 7 decimal places (Stellar precision)
        if decimal_amount.as_tuple().exponent < -7:
            return False
        
        # Must not be too large (prevent overflow)
        if decimal_amount > Decimal('922337203685.4775807'):
            return False
        
        return True
        
    except (InvalidOperation, ValueError):
        return False

def validate_memo(memo: str, memo_type: str = 'text') -> bool:
    """Validate memo format
    
    Args:
        memo: Memo content
        memo_type: Type of memo ('text', 'id', 'hash', 'return')
        
    Returns:
        True if valid, False otherwise
    """
    if not memo:
        return True  # Empty memo is valid
    
    if memo_type == 'text':
        # Text memo max 28 bytes
        return len(memo.encode('utf-8')) <= 28
    elif memo_type == 'id':
        # ID memo must be a number
        try:
            int(memo)
            return True
        except ValueError:
            return False
    elif memo_type in ['hash', 'return']:
        # Hash/return memo must be 32 bytes hex
        return len(memo) == 64 and all(c in '0123456789abcdefABCDEF' for c in memo)
    
    return False

def validate_csv_row(row: Dict[str, str]) -> Dict[str, Any]:
    """Validate a CSV row for bulk payments
    
    Args:
        row: Dictionary representing CSV row
        
    Returns:
        Validation result with errors if any
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Check required fields
    if 'address' not in row or not row['address']:
        result['valid'] = False
        result['errors'].append("Missing address field")
    elif not validate_stellar_address(row['address']):
        result['valid'] = False
        result['errors'].append(f"Invalid Stellar address: {row['address']}")
    
    if 'amount' not in row or not row['amount']:
        result['valid'] = False
        result['errors'].append("Missing amount field")
    elif not validate_amount(row['amount']):
        result['valid'] = False
        result['errors'].append(f"Invalid amount: {row['amount']}")
    else:
        # Check for very small amounts
        try:
            if Decimal(row['amount']) < Decimal('0.0000001'):
                result['warnings'].append(f"Very small amount: {row['amount']}")
        except:
            pass
    
    # Validate optional memo
    if row.get('memo'):
        if not validate_memo(row['memo']):
            result['valid'] = False
            result['errors'].append(f"Invalid memo: {row['memo']}")
    
    return result

def validate_bulk_payment_file(file_path: str) -> Dict[str, Any]:
    """Validate bulk payment CSV file
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        Validation summary
    """
    import csv
    import os
    
    result = {
        'valid': True,
        'total_rows': 0,
        'valid_rows': 0,
        'invalid_rows': 0,
        'errors': [],
        'warnings': [],
        'row_errors': []
    }
    
    # Check file exists
    if not os.path.exists(file_path):
        result['valid'] = False
        result['errors'].append(f"File not found: {file_path}")
        return result
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            # Try to detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            # Check required columns
            required_columns = ['address', 'amount']
            missing_columns = [col for col in required_columns if col not in reader.fieldnames]
            if missing_columns:
                result['valid'] = False
                result['errors'].append(f"Missing required columns: {missing_columns}")
                return result
            
            # Validate each row
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                result['total_rows'] += 1
                
                row_validation = validate_csv_row(row)
                if row_validation['valid']:
                    result['valid_rows'] += 1
                else:
                    result['invalid_rows'] += 1
                    result['row_errors'].append({
                        'row': row_num,
                        'errors': row_validation['errors']
                    })
                
                # Collect warnings
                if row_validation['warnings']:
                    result['warnings'].extend([
                        f"Row {row_num}: {warning}" 
                        for warning in row_validation['warnings']
                    ])
    
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Error reading file: {e}")
    
    # File-level validation
    if result['total_rows'] == 0:
        result['valid'] = False
        result['errors'].append("File is empty")
    elif result['invalid_rows'] > 0:
        result['valid'] = False
        result['errors'].append(f"{result['invalid_rows']} invalid rows found")
    
    return result

def validate_token_config(token_code: str, issuer: str, total_supply: str) -> Dict[str, Any]:
    """Validate token configuration
    
    Args:
        token_code: Token code (e.g., 'OGC')
        issuer: Issuer account public key
        total_supply: Total token supply
        
    Returns:
        Validation result
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Validate token code
    if not token_code or not isinstance(token_code, str):
        result['valid'] = False
        result['errors'].append("Token code is required")
    elif len(token_code) > 12:
        result['valid'] = False
        result['errors'].append("Token code must be 12 characters or less")
    elif not token_code.isalnum():
        result['valid'] = False
        result['errors'].append("Token code must be alphanumeric")
    
    # Validate issuer
    if not validate_stellar_address(issuer):
        result['valid'] = False
        result['errors'].append("Invalid issuer address")
    
    # Validate total supply
    if not validate_amount(total_supply):
        result['valid'] = False
        result['errors'].append("Invalid total supply amount")
    else:
        try:
            supply = Decimal(total_supply)
            if supply > Decimal('922337203685'):  # Practical limit
                result['warnings'].append("Very large total supply")
        except:
            pass
    
    return result

def sanitize_memo(memo: str) -> str:
    """Sanitize memo text for safe use
    
    Args:
        memo: Raw memo text
        
    Returns:
        Sanitized memo text
    """
    if not memo:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[^\w\s\-\.\_\@\#]', '', memo)
    
    # Truncate to safe length (28 bytes max for text memo)
    if len(sanitized.encode('utf-8')) > 28:
        # Truncate by bytes, not characters
        sanitized = sanitized.encode('utf-8')[:28].decode('utf-8', errors='ignore')
    
    return sanitized.strip()

def validate_network_config(network: str, horizon_url: str) -> Dict[str, Any]:
    """Validate network configuration
    
    Args:
        network: Network name ('public' or 'testnet')
        horizon_url: Horizon server URL
        
    Returns:
        Validation result
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Validate network
    if network not in ['public', 'testnet']:
        result['valid'] = False
        result['errors'].append(f"Invalid network: {network}")
    
    # Validate Horizon URL
    if not horizon_url or not isinstance(horizon_url, str):
        result['valid'] = False
        result['errors'].append("Horizon URL is required")
    elif not horizon_url.startswith(('http://', 'https://')):
        result['valid'] = False
        result['errors'].append("Horizon URL must start with http:// or https://")
    
    # Check for testnet in production warning
    if network == 'testnet' and 'testnet' not in horizon_url.lower():
        result['warnings'].append("Network is testnet but URL doesn't contain 'testnet'")
    
    return result

# Batch validation functions
def validate_addresses_batch(addresses: List[str]) -> Dict[str, List[str]]:
    """Validate multiple addresses at once
    
    Args:
        addresses: List of addresses to validate
        
    Returns:
        Dict with 'valid' and 'invalid' lists
    """
    valid = []
    invalid = []
    
    for address in addresses:
        if validate_stellar_address(address):
            valid.append(address)
        else:
            invalid.append(address)
    
    return {'valid': valid, 'invalid': invalid}

def validate_amounts_batch(amounts: List[str]) -> Dict[str, List[str]]:
    """Validate multiple amounts at once
    
    Args:
        amounts: List of amounts to validate
        
    Returns:
        Dict with 'valid' and 'invalid' lists
    """
    valid = []
    invalid = []
    
    for amount in amounts:
        if validate_amount(amount):
            valid.append(amount)
        else:
            invalid.append(amount)
    
    return {'valid': valid, 'invalid': invalid}