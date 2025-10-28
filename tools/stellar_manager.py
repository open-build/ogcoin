"""
Stellar blockchain operations for OGCoin management
Handles account creation, payments, trustlines, and monitoring
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

# Import with fallback for missing dependencies
try:
    from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Asset
    from stellar_sdk.exceptions import SdkError
    STELLAR_SDK_AVAILABLE = True
except ImportError:
    STELLAR_SDK_AVAILABLE = False
    print("Warning: stellar-sdk not installed. Install with: pip install stellar-sdk")

from config import Config as OGCConfig
from validators import validate_stellar_address, validate_amount, validate_memo
from formatters import format_account_info, format_transaction_result

class StellarManager:
    """Main class for managing Stellar operations for OGC token"""
    
    def __init__(self, config: OGCConfig):
        """Initialize Stellar manager
        Args:
            config: OGCConfig instance with configuration settings
        """
        if not STELLAR_SDK_AVAILABLE:
            raise ImportError("stellar-sdk is required. Install with: pip install stellar-sdk")
        
        self.config = config
        self.server = Server(self.config.get_horizon_url())
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"Connected to Stellar Horizon at {self.server.horizon_url}")
        
        # Get issuer keypair if secret is available
        issuer_secret = self.config.get('issuer_secret')
        if issuer_secret:
            self.issuer_keypair = Keypair.from_secret(issuer_secret)
            self.logger.info(f"Issuer account: {self.issuer_keypair.public_key}")
            
            # Configure the OGC asset
            self.ogc_asset = Asset(
                self.config.get('token_code', 'OGC'), 
                self.issuer_keypair.public_key
            )
        else:
            self.issuer_keypair = None
            self.ogc_asset = None
            self.logger.warning("Issuer secret not configured - some operations will be limited")
        
        self.logger.info(f"Initialized StellarManager for {self.config.get('network', 'testnet')} network")
    
    def create_account(self) -> Dict[str, Any]:
        """Create a new Stellar account pair
        
        Returns:
            Dictionary with public and secret keys
        """
        try:
            keypair = Keypair.random()
            
            result = {
                'successful': True,
                'public_key': keypair.public_key,
                'secret_key': keypair.secret,
                'created_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"Created new account: {keypair.public_key}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create account: {e}")
            return {
                'successful': False,
                'error': str(e)
            }
    
    def fund_account_testnet(self, account_id: str) -> Dict[str, Any]:
        """Fund an account on testnet using Friendbot
        
        Args:
            account_id: Account public key to fund
            
        Returns:
            Operation result
        """
        if not validate_stellar_address(account_id):
            return {
                'successful': False,
                'error': 'Invalid Stellar address'
            }
        
        try:
            # Only works on testnet
            if self.config.get('network', 'testnet') != 'testnet':
                return {
                    'successful': False,
                    'error': 'Account funding only available on testnet'
                }
            
            import requests
            # Use Friendbot directly via HTTP request
            friendbot_url = f"https://friendbot.stellar.org?addr={account_id}"
            response = requests.get(friendbot_url)
            response.raise_for_status()
            
            self.logger.info(f"Funded testnet account: {account_id}")
            return {
                'successful': True,
                'transaction_hash': response.json().get('hash') if response.status_code == 200 else 'N/A',
                'account_id': account_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to fund account {account_id}: {e}")
            return {
                'successful': False,
                'error': str(e)
            }
    
    def get_account_info(self, account_id: str) -> Dict[str, Any]:
        """Get account information from Stellar
        
        Args:
            account_id: Account public key
            
        Returns:
            Account information or error
        """
        if not validate_stellar_address(account_id):
            return {
                'successful': False,
                'error': 'Invalid Stellar address'
            }
        
        try:
            account = self.server.accounts().account_id(account_id).call()
            
            self.logger.info(f"Retrieved account info for: {account_id}")
            return {
                'successful': True,
                'account_data': account,
                'account_id': account_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get account info for {account_id}: {e}")
            return {
                'successful': False,
                'error': str(e)
            }
    
    def create_trustline(self, account_secret: str, limit: Optional[str] = None) -> Dict[str, Any]:
        """Create trustline for OGC token
        
        Args:
            account_secret: Account secret key
            limit: Optional trust limit
            
        Returns:
            Transaction result
        """
        if not self.ogc_asset:
            return {
                'successful': False,
                'error': 'OGC asset not configured - issuer secret required'
            }
        
        try:
            account_keypair = Keypair.from_secret(account_secret)
            account = self.server.load_account(account_keypair.public_key)
            
            # Build transaction
            transaction = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.config.get_network_passphrase(),
                    base_fee=self.server.fetch_base_fee()
                )
                .add_change_trust_op(asset=self.ogc_asset, limit=limit)
                .set_timeout(30)
                .build()
            )
            
            transaction.sign(account_keypair)
            response = self.server.submit_transaction(transaction)
            
            self.logger.info(f"Created trustline for {account_keypair.public_key}")
            return {
                'successful': True,
                'hash': response['hash'],
                'account_id': account_keypair.public_key,
                'asset_code': self.config.get('token_code', 'OGC')
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create trustline: {e}")
            return {
                'successful': False,
                'error': str(e)
            }
    
    def remove_trustline(self, account_secret: str) -> Dict[str, Any]:
        """Remove trustline for OGC token
        
        Args:
            account_secret: Account secret key
            
        Returns:
            Transaction result
        """
        if not self.ogc_asset:
            return {
                'successful': False,
                'error': 'OGC asset not configured - issuer secret required'
            }
        
        try:
            account_keypair = Keypair.from_secret(account_secret)
            account = self.server.load_account(account_keypair.public_key)
            
            # Build transaction to remove trust (limit = "0")
            transaction = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.config.get_network_passphrase(),
                    base_fee=self.server.fetch_base_fee()
                )
                .add_change_trust_op(asset=self.ogc_asset, limit="0")
                .set_timeout(30)
                .build()
            )
            
            transaction.sign(account_keypair)
            response = self.server.submit_transaction(transaction)
            
            self.logger.info(f"Removed trustline for {account_keypair.public_key}")
            return {
                'successful': True,
                'hash': response['hash'],
                'account_id': account_keypair.public_key,
                'asset_code': self.config.get('token_code', 'OGC')
            }
            
        except Exception as e:
            self.logger.error(f"Failed to remove trustline: {e}")
            return {
                'successful': False,
                'error': str(e)
            }
    
    def send_payment(self, source_secret: str, destination: str, amount: str, 
                    memo: Optional[str] = None) -> Dict[str, Any]:
        """Send OGC payment
        
        Args:
            source_secret: Source account secret key
            destination: Destination account public key
            amount: Payment amount
            memo: Optional memo
            
        Returns:
            Transaction result
        """
        # Validate inputs
        if not validate_stellar_address(destination):
            return {'successful': False, 'error': 'Invalid destination address'}
        
        if not validate_amount(amount):
            return {'successful': False, 'error': 'Invalid amount'}
        
        if memo and not validate_memo(memo):
            return {'successful': False, 'error': 'Invalid memo'}
        
        if not self.ogc_asset:
            return {
                'successful': False,
                'error': 'OGC asset not configured - issuer secret required'
            }
        
        try:
            source_keypair = Keypair.from_secret(source_secret)
            source_account = self.server.load_account(source_keypair.public_key)
            
            # Build transaction
            transaction_builder = TransactionBuilder(
                source_account=source_account,
                network_passphrase=self.config.get_network_passphrase(),
                base_fee=self.server.fetch_base_fee()
            )
            
            # Add memo if provided
            if memo:
                transaction_builder.add_text_memo(memo)
            
            # Add payment operation
            transaction_builder.add_payment_op(
                destination=destination,
                asset=self.ogc_asset,
                amount=amount
            )
            
            transaction = transaction_builder.set_timeout(30).build()
            transaction.sign(source_keypair)
            
            response = self.server.submit_transaction(transaction)
            
            self.logger.info(f"Sent {amount} OGC from {source_keypair.public_key} to {destination}")
            return {
                'successful': True,
                'hash': response['hash'],
                'from': source_keypair.public_key,
                'to': destination,
                'amount': amount,
                'asset_code': self.config.get('token_code', 'OGC'),
                'memo': memo,
                'fee_charged': response.get('fee_charged', 'Unknown')
            }
            
        except Exception as e:
            self.logger.error(f"Payment failed: {e}")
            return {
                'successful': False,
                'error': str(e),
                'from': Keypair.from_secret(source_secret).public_key if source_secret else 'Unknown',
                'to': destination,
                'amount': amount
            }
    
    def get_account_transactions(self, account_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get recent transactions for an account
        
        Args:
            account_id: Account public key
            limit: Number of transactions to fetch
            
        Returns:
            List of transactions
        """
        if not validate_stellar_address(account_id):
            return {
                'successful': False,
                'error': 'Invalid Stellar address'
            }
        
        try:
            response = (
                self.server.transactions()
                .for_account(account_id)
                .limit(limit)
                .order(desc=True)
                .call()
            )
            
            transactions = response.get('_embedded', {}).get('records', [])
            
            self.logger.info(f"Retrieved {len(transactions)} transactions for {account_id}")
            return {
                'successful': True,
                'transactions': transactions,
                'account_id': account_id,
                'count': len(transactions)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get transactions for {account_id}: {e}")
            return {
                'successful': False,
                'error': str(e),
                'account_id': account_id
            }
    
    def monitor_payments(self, account_id: str, callback_func=None) -> Dict[str, Any]:
        """Monitor payments for an account (basic implementation)
        
        Args:
            account_id: Account to monitor
            callback_func: Optional callback for new payments
            
        Returns:
            Monitoring result
        """
        if not validate_stellar_address(account_id):
            return {
                'successful': False,
                'error': 'Invalid Stellar address'
            }
        
        try:
            # Get recent payments
            payments_response = (
                self.server.payments()
                .for_account(account_id)
                .limit(20)
                .order(desc=True)
                .call()
            )
            
            payments = payments_response.get('_embedded', {}).get('records', [])
            
            # Filter for OGC payments
            ogc_payments = []
            for payment in payments:
                if (payment.get('type') == 'payment' and 
                    payment.get('asset_code') == self.config.get('token_code', 'OGC')):
                    ogc_payments.append(payment)
            
            self.logger.info(f"Found {len(ogc_payments)} OGC payments for {account_id}")
            return {
                'successful': True,
                'account_id': account_id,
                'ogc_payments': ogc_payments,
                'total_payments': len(payments)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to monitor payments for {account_id}: {e}")
            return {
                'successful': False,
                'error': str(e),
                'account_id': account_id
            }
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information and health status
        
        Returns:
            Network status information
        """
        try:
            # Get ledger info
            ledger = self.server.ledgers().order(desc=True).limit(1).call()
            latest_ledger = ledger['_embedded']['records'][0] if ledger['_embedded']['records'] else {}
            
            health_status = {
                'network': self.config.get('network', 'testnet'),
                'horizon_url': self.config.get_horizon_url(),
                'latest_ledger': latest_ledger.get('sequence', 'Unknown'),
                'ledger_time': latest_ledger.get('closed_at', 'Unknown'),
                'base_fee': self.server.fetch_base_fee(),
                'ogc_configured': self.ogc_asset is not None
            }
            
            # Add issuer info if available
            if self.issuer_keypair:
                health_status['issuer_address'] = self.issuer_keypair.public_key
                
                # Try to get issuer account info
                try:
                    issuer_info = self.get_account_info(self.issuer_keypair.public_key)
                    if issuer_info['successful']:
                        health_status['issuer_account_exists'] = True
                        health_status['issuer_sequence'] = issuer_info['account_data'].get('sequence')
                except:
                    health_status['issuer_account_exists'] = False
            
            return {
                'successful': True,
                'network_info': health_status
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get network info: {e}")
            return {
                'successful': False,
                'error': str(e)
            }

# Utility functions for standalone use
def create_new_account() -> Dict[str, Any]:
    """Create a new Stellar account (utility function)
    
    Returns:
        New account keypair
    """
    try:
        keypair = Keypair.random()
        return {
            'successful': True,
            'public_key': keypair.public_key,
            'secret_key': keypair.secret
        }
    except Exception as e:
        return {
            'successful': False,
            'error': str(e)
        }

def validate_account_address(address: str) -> bool:
    """Validate a Stellar account address (utility function)
    
    Args:
        address: Stellar public key
        
    Returns:
        True if valid
    """
    return validate_stellar_address(address)