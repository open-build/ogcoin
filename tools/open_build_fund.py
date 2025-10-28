"""
Open Build Fund Manager
Handles automatic collection and distribution of transaction fees to support open source projects
"""

import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta
import json

# Import with fallback for missing dependencies
try:
    from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Asset, Payment
    from stellar_sdk.exceptions import SdkError
    STELLAR_SDK_AVAILABLE = True
except ImportError:
    STELLAR_SDK_AVAILABLE = False
    print("Warning: stellar-sdk not installed. Install with: pip install stellar-sdk")

from config import Config as OGCConfig

class OpenBuildFund:
    """Manages the Open Build fund that receives transaction fees"""
    
    def __init__(self, config: OGCConfig):
        """Initialize fund manager with configuration
        
        Args:
            config: OGCConfig instance
        """
        if not STELLAR_SDK_AVAILABLE:
            raise ImportError("stellar-sdk is required. Install with: pip install stellar-sdk")
        
        self.config = config
        self.server = Server(config.get_horizon_url())
        self.network_passphrase = config.get_network_passphrase()
        
        # Fund allocation percentages
        self.ALLOCATION = {
            'open_source_projects': 0.50,  # 50% to open source projects
            'developer_training': 0.30,    # 30% to developer education
            'operations': 0.20             # 20% to operations and governance
        }
        
        # Transaction fee percentage (0.1% of transaction amount)
        self.TRANSACTION_FEE_RATE = Decimal('0.001')
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def calculate_fund_contribution(self, transaction_amount: str) -> Dict[str, str]:
        """Calculate how much should go to the fund from a transaction
        
        Args:
            transaction_amount: Amount of OGC being transacted
            
        Returns:
            Dict with fund_amount and remaining_amount
        """
        try:
            amount = Decimal(transaction_amount)
            fund_contribution = amount * self.TRANSACTION_FEE_RATE
            remaining_amount = amount - fund_contribution
            
            return {
                'fund_amount': str(fund_contribution),
                'remaining_amount': str(remaining_amount),
                'fee_rate': str(self.TRANSACTION_FEE_RATE)
            }
        except Exception as e:
            self.logger.error(f"Error calculating fund contribution: {e}")
            raise
    
    def create_fund_transaction(self, source_secret: str, recipient: str, 
                              amount: str, memo: str = "") -> Dict[str, Any]:
        """Create a transaction that includes fund contribution
        
        Args:
            source_secret: Secret key of the sender
            recipient: Public key of the recipient
            amount: Amount to send (before fund deduction)
            memo: Optional memo for the transaction
            
        Returns:
            Transaction result with fund contribution details
        """
        try:
            # Calculate amounts
            amounts = self.calculate_fund_contribution(amount)
            fund_amount = amounts['fund_amount']
            send_amount = amounts['remaining_amount']
            
            # Get accounts
            source_keypair = Keypair.from_secret(source_secret)
            source_account = self.server.load_account(source_keypair.public_key)
            
            # Get fund account (in production, this would be a dedicated fund account)
            fund_account = self.config.get_issuer_public_key()  # For now, use issuer as fund
            
            # Create asset
            ogc_asset = Asset(self.config.get_token_code(), self.config.get_issuer_public_key())
            
            # Build transaction with two payments: one to recipient, one to fund
            transaction_builder = TransactionBuilder(
                source_account=source_account,
                network_passphrase=self.network_passphrase,
                base_fee=100
            )
            
            # Payment to recipient
            transaction_builder.append_payment_op(
                destination=recipient,
                asset=ogc_asset,
                amount=send_amount
            )
            
            # Payment to fund (only if fund amount is significant)
            if Decimal(fund_amount) > Decimal('0.0000001'):
                transaction_builder.append_payment_op(
                    destination=fund_account,
                    asset=ogc_asset,
                    amount=fund_amount
                )
            
            # Add memo if provided
            if memo:
                transaction_builder.add_text_memo(memo)
            
            # Build and sign transaction
            transaction = transaction_builder.set_timeout(300).build()
            transaction.sign(source_secret)
            
            # Submit transaction
            response = self.server.submit_transaction(transaction)
            
            self.logger.info(f"Fund transaction successful: {response['hash']}")
            
            return {
                'success': True,
                'transaction_hash': response['hash'],
                'recipient_amount': send_amount,
                'fund_contribution': fund_amount,
                'fund_account': fund_account,
                'fee_rate': amounts['fee_rate']
            }
            
        except Exception as e:
            self.logger.error(f"Error creating fund transaction: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_fund_balance(self) -> Dict[str, Any]:
        """Get current balance of the Open Build fund
        
        Returns:
            Fund balance information
        """
        try:
            fund_account = self.config.get_issuer_public_key()  # For now, use issuer as fund
            account_info = self.server.load_account(fund_account).load()
            
            ogc_balance = "0"
            for balance in account_info['balances']:
                if (balance['asset_type'] != 'native' and 
                    balance.get('asset_code') == self.config.get_token_code()):
                    ogc_balance = balance['balance']
                    break
            
            return {
                'fund_account': fund_account,
                'ogc_balance': ogc_balance,
                'allocation': self.ALLOCATION,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting fund balance: {e}")
            return {
                'error': str(e)
            }
    
    def calculate_allocation_amounts(self, total_fund_balance: str) -> Dict[str, str]:
        """Calculate how much should be allocated to each category
        
        Args:
            total_fund_balance: Total OGC in the fund
            
        Returns:
            Dict with allocation amounts for each category
        """
        try:
            total = Decimal(total_fund_balance)
            
            return {
                'open_source_projects': str(total * Decimal(str(self.ALLOCATION['open_source_projects']))),
                'developer_training': str(total * Decimal(str(self.ALLOCATION['developer_training']))),
                'operations': str(total * Decimal(str(self.ALLOCATION['operations']))),
                'total': str(total)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating allocations: {e}")
            raise
    
    def generate_fund_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report on fund status
        
        Returns:
            Detailed fund report
        """
        try:
            fund_info = self.get_fund_balance()
            
            if 'error' in fund_info:
                return fund_info
            
            allocations = self.calculate_allocation_amounts(fund_info['ogc_balance'])
            
            # Get recent transactions (simplified - in production would query fund account)
            recent_contributions = self._get_recent_contributions()
            
            return {
                'fund_balance': fund_info,
                'allocations': allocations,
                'recent_contributions': recent_contributions,
                'fee_rate': str(self.TRANSACTION_FEE_RATE),
                'allocation_policy': self.ALLOCATION,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating fund report: {e}")
            return {
                'error': str(e)
            }
    
    def _get_recent_contributions(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent contributions to the fund
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of recent contributions
        """
        # Simplified implementation - in production would query actual transactions
        # For now, return placeholder data
        return [
            {
                'date': (datetime.now() - timedelta(days=1)).isoformat(),
                'amount': '10.5000000',
                'transaction_hash': 'placeholder_hash_1',
                'contributor': 'Anonymous'
            }
        ]
    
    def create_distribution_proposal(self, proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a proposal for fund distribution
        
        Args:
            proposals: List of funding proposals with recipient, amount, description
            
        Returns:
            Distribution proposal details
        """
        try:
            fund_info = self.get_fund_balance()
            available_balance = Decimal(fund_info['ogc_balance'])
            
            total_requested = sum(Decimal(p['amount']) for p in proposals)
            
            if total_requested > available_balance:
                return {
                    'error': f'Total requested ({total_requested}) exceeds available balance ({available_balance})'
                }
            
            # Create proposal ID (in production would use proper ID generation)
            proposal_id = f"proposal_{int(datetime.now().timestamp())}"
            
            proposal = {
                'id': proposal_id,
                'proposals': proposals,
                'total_requested': str(total_requested),
                'available_balance': str(available_balance),
                'status': 'pending_community_vote',
                'created_at': datetime.now().isoformat(),
                'voting_deadline': (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            # In production, this would be stored in a database or distributed ledger
            self.logger.info(f"Created distribution proposal: {proposal_id}")
            
            return proposal
            
        except Exception as e:
            self.logger.error(f"Error creating distribution proposal: {e}")
            return {
                'error': str(e)
            }

def calculate_transaction_with_fund_fee(amount: str, fee_rate: str = "0.001") -> Dict[str, str]:
    """Utility function to calculate transaction amounts including fund fee
    
    Args:
        amount: Original transaction amount
        fee_rate: Fee rate as decimal string
        
    Returns:
        Dict with calculated amounts
    """
    try:
        original = Decimal(amount)
        rate = Decimal(fee_rate)
        
        fund_fee = original * rate
        recipient_amount = original - fund_fee
        
        return {
            'original_amount': str(original),
            'fund_fee': str(fund_fee),
            'recipient_amount': str(recipient_amount),
            'fee_rate': str(rate)
        }
        
    except Exception as e:
        return {
            'error': str(e)
        }

if __name__ == "__main__":
    # Example usage
    from config import Config
    
    config = Config()
    fund = OpenBuildFund(config)
    
    # Example: Calculate fund contribution for a 100 OGC transaction
    amounts = fund.calculate_fund_contribution("100")
    print("Fund Contribution Example:")
    print(f"  Original Amount: 100 OGC")
    print(f"  Fund Contribution: {amounts['fund_amount']} OGC")
    print(f"  Recipient Receives: {amounts['remaining_amount']} OGC")
    print(f"  Fee Rate: {amounts['fee_rate']} ({float(amounts['fee_rate']) * 100}%)")
    
    # Example: Generate fund report
    report = fund.generate_fund_report()
    print("\nFund Report:")
    print(json.dumps(report, indent=2, default=str))