#!/usr/bin/env python3
"""
Test script for Open Build Fund functionality
Demonstrates how the transaction fee system works
"""

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
    test_amounts = ["10", "100", "1000", "10000"]
    
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
        print(f"  Open Source Projects: {allocations['open_source_projects']} OGC")
        print(f"  Developer Training:   {allocations['developer_training']} OGC")
        print(f"  Operations:          {allocations['operations']} OGC")
        
    except Exception as e:
        print(f"❌ Error in fund operations: {e}")

def demonstrate_impact():
    """Demonstrate the potential impact of the fund system"""
    print("\n📊 Demonstrating Fund Impact Potential")
    print("=" * 42)
    
    # Simulate different usage scenarios
    scenarios = [
        {"name": "Light Usage", "daily_transactions": 100, "avg_amount": 10},
        {"name": "Moderate Usage", "daily_transactions": 1000, "avg_amount": 25},
        {"name": "Heavy Usage", "daily_transactions": 10000, "avg_amount": 50},
    ]
    
    for scenario in scenarios:
        daily_volume = scenario["daily_transactions"] * scenario["avg_amount"]
        daily_fund = daily_volume * 0.001  # 0.1% fee
        monthly_fund = daily_fund * 30
        yearly_fund = daily_fund * 365
        
        print(f"\n{scenario['name']} Scenario:")
        print(f"  Daily transactions: {scenario['daily_transactions']}")
        print(f"  Average amount: {scenario['avg_amount']} OGC")
        print(f"  Daily fund collection: {daily_fund:.2f} OGC")
        print(f"  Monthly fund: {monthly_fund:.2f} OGC")
        print(f"  Yearly fund: {yearly_fund:.2f} OGC")
        
        # Show allocation breakdown
        os_projects = yearly_fund * 0.5
        dev_training = yearly_fund * 0.3
        operations = yearly_fund * 0.2
        
        print(f"  Yearly allocation:")
        print(f"    Open Source Projects: {os_projects:.2f} OGC")
        print(f"    Developer Training:   {dev_training:.2f} OGC")
        print(f"    Operations:          {operations:.2f} OGC")

if __name__ == "__main__":
    print("🚀 Open Build Fund System Test")
    print("=" * 35)
    print("This demonstrates how OGC transactions contribute to open source funding")
    print()
    
    # Run tests
    test_fund_calculations()
    test_fund_operations()
    demonstrate_impact()
    
    print("\n🎯 Key Benefits:")
    print("  • Automatic funding for open source projects")
    print("  • Developer training programs supported")
    print("  • Transparent, community-governed allocation")
    print("  • Minimal impact on users (0.1% fee)")
    print("  • Sustainable funding model")
    print("\n✨ Every OGC transaction helps build the future of open source!")