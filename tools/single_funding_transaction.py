#!/usr/bin/env python3
"""
Single Multi-Operation Transaction
Create all three OGC accounts in one transaction to reduce multi-sig complexity.
"""

import os
from stellar_sdk import Keypair, Server, TransactionBuilder, Network

def create_single_funding_transaction():
    print("🚀 SINGLE MULTI-OPERATION FUNDING TRANSACTION")
    print("=" * 50)
    
    # Your account details
    source_secret = os.getenv('LOBSTR_SECRET_KEY')
    if not source_secret:
        raise ValueError("LOBSTR_SECRET_KEY environment variable is required")
    source_keypair = Keypair.from_secret(source_secret)
    
    # Target accounts
    accounts = [
        ("ISSUER", "GABZZWBBQA4OMJ7LOPYBB445NZZFYALQQO5KOF6GB4RREYYNEBHSJR5N", "3"),
        ("DISTRIBUTOR", "GCDHORR6BPE4UF4TESO4WDKPGBPDPWTP5ZL4UEFD5CARUFHFLSODQRXX", "3"),
        ("PERSONAL", "GBLGFRH6B6PQGO2KHLIZXPD3LAV2CWBYW6AJ4EMGXSNLRLT5KQRKLADA", "2")
    ]
    
    server = Server("https://horizon.stellar.org")
    
    try:
        # Load source account
        source_account = server.load_account(source_keypair.public_key)
        
        print(f"✅ Source Account: {source_keypair.public_key}")
        print(f"✅ Current Balance: Check Lobstr app")
        print(f"✅ Current Sequence: {source_account.sequence}")
        print()
        
        # Create single transaction with multiple operations
        print("🏗️  Building single transaction with 3 create account operations...")
        
        transaction_builder = TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
            base_fee=100000  # 0.01 XLM per operation = 0.03 XLM total fee
        )
        
        # Add all three create account operations
        for name, public_key, amount in accounts:
            transaction_builder.append_create_account_op(
                destination=public_key,
                starting_balance=amount
            )
            print(f"   ✅ Added {name}: {amount} XLM to {public_key}")
        
        # Build and sign transaction
        transaction = transaction_builder.set_timeout(300).build()
        transaction.sign(source_keypair)
        
        # Get XDR
        xdr = transaction.to_xdr()
        
        print()
        print("📋 SINGLE TRANSACTION XDR:")
        print("=" * 30)
        print(f"XDR: {xdr}")
        print()
        print("💰 TRANSACTION SUMMARY:")
        print("   • Creates 3 accounts in one transaction")
        print("   • Total funding: 8 XLM (3+3+2)")
        print("   • Transaction fee: 0.03 XLM")
        print("   • Total cost: 8.03 XLM")
        print()
        print("🎯 ADVANTAGES:")
        print("   • Only ONE multi-sig approval needed")
        print("   • All accounts created simultaneously")
        print("   • Lower total transaction fees")
        print("   • Simpler process")
        
        # Save to file
        with open("single_funding_transaction.txt", "w") as f:
            f.write("OGC Mainnet Single Funding Transaction\n")
            f.write("="*40 + "\n\n")
            f.write(f"Source Account: {source_keypair.public_key}\n")
            f.write(f"Total Cost: 8.03 XLM\n")
            f.write(f"Operations: 3 (Create Account)\n\n")
            
            for name, public_key, amount in accounts:
                f.write(f"{name} Account: {public_key} ({amount} XLM)\n")
            
            f.write(f"\nXDR: {xdr}\n")
        
        print("💾 Transaction saved to single_funding_transaction.txt")
        print()
        print("📱 SUBMIT TO LOBSTR:")
        print("   1. Use Lobstr's 'Submit Transaction' feature")
        print("   2. Paste the XDR above")
        print("   3. Review that it creates all 3 accounts")
        print("   4. Submit - Lobstr will co-sign automatically")
        print("   5. All accounts funded in one step!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_single_funding_transaction()