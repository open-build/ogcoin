"""Legacy compatibility helpers for impact contribution calculations.

Direct signing and submission from this module are disabled. Official routed
payments must use create_impact_payment_xdr.py so the payer can review and sign
an atomic 95/5 transaction without sharing a secret key.
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
from impact_policy import calculate_split, load_policy

IMPACT_TREASURY = "GDMAMIC6SBYCF4NUQ6RBTUIFB5WWWS3TTDHXNCOUOLDFEPK5XOOU525F"


class OpenBuildFund:
    """Legacy read-only interface for the Open Source Impact Treasury."""
    
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
        
        # Policy v0.1 does not promise fixed allocation percentages.
        self.ALLOCATION = {}
        
        # OpenGreenCoin Impact Policy v0.1 contribution rate.
        self.TRANSACTION_FEE_RATE = Decimal('0.05')
        
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
            split = calculate_split(transaction_amount, load_policy())
            
            return {
                'fund_amount': split['contribution_amount'],
                'remaining_amount': split['recipient_amount'],
                'fee_rate': split['contribution_rate']
            }
        except Exception as e:
            self.logger.error(f"Error calculating fund contribution: {e}")
            raise
    
    def create_fund_transaction(self, source_secret: str, recipient: str, 
                              amount: str, memo: str = "") -> Dict[str, Any]:
        """Refuse legacy secret-key submission and direct operators to the safe builder."""
        return {
            "success": False,
            "error": (
                "Direct impact-payment signing is disabled. Use "
                "tools/create_impact_payment_xdr.py to build an unsigned, "
                "reviewable 95/5 transaction."
            ),
        }
    
    def get_fund_balance(self) -> Dict[str, Any]:
        """Get current balance of the Open Build fund
        
        Returns:
            Fund balance information
        """
        try:
            fund_account = IMPACT_TREASURY
            account_info = self.server.accounts().account_id(fund_account).call()
            
            ogc_balance = "0"
            for balance in account_info['balances']:
                if (balance['asset_type'] != 'native' and 
                    balance.get('asset_code') == self.config.get('token_code', 'OGC')):
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
                'unallocated': str(total),
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
            
            # Contributions are reconciled from Horizon and reviewed manifests.
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
        # Reporting must be derived from Horizon and reviewed manifests.
        return []
    
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
                'status': 'pending_review',
                'created_at': datetime.now().isoformat(),
                'review_deadline': (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            # In production, this would be stored in a database or distributed ledger
            self.logger.info(f"Created distribution proposal: {proposal_id}")
            
            return proposal
            
        except Exception as e:
            self.logger.error(f"Error creating distribution proposal: {e}")
            return {
                'error': str(e)
            }

def calculate_transaction_with_fund_fee(amount: str, fee_rate: str = "0.05") -> Dict[str, str]:
    """Utility function to calculate transaction amounts including fund fee
    
    Args:
        amount: Original transaction amount
        fee_rate: Fee rate as decimal string
        
    Returns:
        Dict with calculated amounts
    """
    try:
        if Decimal(fee_rate) != Decimal("0.05"):
            raise ValueError("OpenGreenCoin Impact Policy v0.1 requires a 0.05 contribution rate")
        split = calculate_split(amount, load_policy())
        
        return {
            'original_amount': split['gross_amount'],
            'fund_fee': split['contribution_amount'],
            'recipient_amount': split['recipient_amount'],
            'fee_rate': split['contribution_rate']
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
