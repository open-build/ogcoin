#!/usr/bin/env python3
"""
Simple Single Account Test
Create just the issuer account first to test Lobstr submission.
"""

import os
from stellar_sdk import Keypair, Server, TransactionBuilder, Network

def create_test_transaction():
    print("🧪 SIMPLE TEST - CREATE ONE ACCOUNT ONLY")
    print("=" * 45)
    
    source_secret = os.getenv('LOBSTR_SECRET_KEY')
    if not source_secret:
        raise ValueError("LOBSTR_SECRET_KEY environment variable is required")
    source_keypair = Keypair.from_secret(source_secret)
    
    server = Server("https://horizon.stellar.org")
    
    try:
        source_account = server.load_account(source_keypair.public_key)
        
        print(f"✅ Source: {source_keypair.public_key}")
        print(f"✅ Sequence: {source_account.sequence}")
        print()
        
        # Create simple single-account transaction
        transaction = (
            TransactionBuilder(
                source_account=source_account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100000
            )
            .append_create_account_op(
                destination="GABZZWBBQA4OMJ7LOPYBB445NZZFYALQQO5KOF6GB4RREYYNEBHSJR5N",
                starting_balance="3"
            )
            .set_timeout(300)
            .build()
        )
        
        transaction.sign(source_keypair)
        xdr = transaction.to_xdr()
        
        print("📋 SIMPLE TEST XDR (Just Issuer Account):")
        print("=" * 45)
        print(f"Destination: GABZZWBBQA4OMJ7LOPYBB445NZZFYALQQO5KOF6GB4RREYYNEBHSJR5N")
        print(f"Amount: 3 XLM")
        print(f"Fee: 0.01 XLM")
        print(f"Total Cost: 3.01 XLM")
        print()
        print(f"XDR: {xdr}")
        print()
        print("🎯 TRY THIS FIRST:")
        print("1. Copy the XDR above")
        print("2. Go to lobstr.co (web interface)")
        print("3. Find 'Submit Transaction' or 'XDR' tool")
        print("4. Paste and submit")
        print("5. If successful, we'll create the other accounts")
        print()
        print("💡 ALTERNATIVE IF LOBSTR FAILS:")
        print("We can try using StellarLab.org or other tools")
        
        # Save simple version
        with open("test_single_account.txt", "w") as f:
            f.write("Test Transaction - Single Account Creation\\n")
            f.write("="*40 + "\\n\\n")
            f.write(f"Creates: GABZZWBBQA4OMJ7LOPYBB445NZZFYALQQO5KOF6GB4RREYYNEBHSJR5N\\n")
            f.write(f"Amount: 3 XLM\\n")
            f.write(f"XDR: {xdr}\\n")
        
        print("💾 Saved to test_single_account.txt")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_test_transaction()