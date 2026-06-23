#!/usr/bin/env python3
"""Compatibility test for OpenGreenCoin Impact Policy calculations and balance reads."""

import sys
from pathlib import Path

# Add the tools directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from open_build_fund import OpenBuildFund, calculate_transaction_with_fund_fee
from config import Config

def test_fund_calculations():
    """Test fund calculation functionality"""
    print("🧪 Testing Open Build Fund Calculations")
    print("=" * 45)
    
    # Test various transaction amounts
    test_amounts = ["0.000002", "1", "10", "100"]
    
    for amount in test_amounts:
        result = calculate_transaction_with_fund_fee(amount)
        print(f"\nTransaction: {amount} OGC")
        print(f"  Recipient gets: {result['recipient_amount']} OGC")
        print(f"  Fund receives:  {result['fund_fee']} OGC")
        print(f"  Fee rate:       {float(result['fee_rate']) * 100}%")

def test_fund_operations():
    """Test fund operations with configuration"""
    print("\n🏦 Testing Fund Operations")
    print("=" * 30)
    
    try:
        config = Config()
        fund = OpenBuildFund(config)
        
        # Test fund balance (will work even without real accounts)
        print("Testing fund balance retrieval...")
        balance_info = fund.get_fund_balance()
        
        if 'error' not in balance_info:
            print(f"✅ Fund account: {balance_info['fund_account']}")
            print(f"✅ Balance: {balance_info['ogc_balance']} OGC")
        else:
            print(f"⚠️  Expected error (no real fund account yet): {balance_info['error']}")
        
        # Test allocation calculations
        print("\nTesting allocation calculations...")
        allocations = fund.calculate_allocation_amounts("1000")
        print(f"✅ For 1000 OGC fund:")
        print(f"  Awaiting approved allocation: {allocations['unallocated']} OGC")
        
    except Exception as e:
        print(f"❌ Error in fund operations: {e}")

if __name__ == "__main__":
    print("🚀 Open Build Fund System Test")
    print("=" * 35)
    print("This demonstrates how OGC transactions contribute to open source funding")
    print()
    
    # Run tests
    test_fund_calculations()
    test_fund_operations()
    
    print("\n🎯 Key Benefits:")
    print("  • Atomic recipient and treasury routing")
    print("  • Payer review before wallet authorization")
    print("  • Public treasury and transaction records")
    print("  • Explicit 5% contribution on official routed flows only")
    print("  • No change to direct peer-to-peer transfers")
    print("\nOfficial routed OGC payments can support open source while peer-to-peer transfers remain unchanged.")
