#!/usr/bin/env python3
"""
Multi-Signature Transaction Builder for Lobstr
This creates transactions that are properly formatted for Lobstr's multi-sig setup.
"""

from stellar_sdk import Keypair, Server, TransactionBuilder, Network
import os

def create_multisig_funding_transactions():
    print("🔐 MULTI-SIGNATURE TRANSACTION BUILDER")
    print("=" * 45)
    
    # Your account details
    source_secret = os.getenv('LOBSTR_SECRET_KEY')
    if not source_secret:
        raise ValueError("LOBSTR_SECRET_KEY environment variable is required")
    source_keypair = Keypair.from_secret(source_secret)
    
    # Lobstr's co-signer
    lobstr_signer = "GDJ4HVRGT2OVVL5YFLBR7XAJIHCMWUO6OKLBXWWTVW3OK4VBFRAYQJHV"
    
    # Target accounts from new_accounts.txt
    accounts = [
        {
            "name": "ISSUER",
            "public": "GABZZWBBQA4OMJ7LOPYBB445NZZFYALQQO5KOF6GB4RREYYNEBHSJR5N",
            "amount": "3"
        },
        {
            "name": "DISTRIBUTOR", 
            "public": "GCDHORR6BPE4UF4TESO4WDKPGBPDPWTP5ZL4UEFD5CARUFHFLSODQRXX",
            "amount": "3"
        },
        {
            "name": "PERSONAL",
            "public": "GBLGFRH6B6PQGO2KHLIZXPD3LAV2CWBYW6AJ4EMGXSNLRLT5KQRKLADA", 
            "amount": "2"
        }
    ]
    
    server = Server("https://horizon.stellar.org")
    
    try:
        # Load source account
        source_account = server.load_account(source_keypair.public_key)
        
        print(f"✅ Source Account: {source_keypair.public_key}")
        print(f"✅ Lobstr Co-Signer: {lobstr_signer}")
        print(f"✅ Current Sequence: {source_account.sequence}")
        print()
        
        # Create all three transactions
        xdrs = []
        
        for i, account in enumerate(accounts):
            print(f"🏗️  Building transaction {i+1}/3: {account['name']} Account")
            
            # Create transaction builder
            transaction = (
                TransactionBuilder(
                    source_account=source_account,
                    network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                    base_fee=100000  # 0.01 XLM fee
                )
                .append_create_account_op(
                    destination=account["public"],
                    starting_balance=account["amount"]
                )
                .set_timeout(300)  # 5 minute timeout
                .build()
            )
            
            # Sign with your key
            transaction.sign(source_keypair)
            
            # Get XDR
            xdr = transaction.to_xdr()
            xdrs.append({
                "name": account["name"],
                "xdr": xdr,
                "destination": account["public"],
                "amount": account["amount"]
            })
            
            print(f"   ✅ XDR created for {account['name']} account")
            
            # Increment sequence for next transaction
            source_account.increment_sequence_number()
        
        print()
        print("📋 TRANSACTION XDRs FOR LOBSTR:")
        print("=" * 40)
        
        for i, tx in enumerate(xdrs):
            print(f"📄 TRANSACTION {i+1}: {tx['name']} ACCOUNT")
            print(f"   Destination: {tx['destination']}")
            print(f"   Amount: {tx['amount']} XLM")
            print(f"   XDR: {tx['xdr']}")
            print()
        
        # Save to file for reference
        with open("multisig_transactions.txt", "w") as f:
            f.write("OGC Mainnet Multi-Sig Funding Transactions\n")
            f.write("="*50 + "\n\n")
            f.write(f"Source Account: {source_keypair.public_key}\n")
            f.write(f"Lobstr Co-Signer: {lobstr_signer}\n\n")
            
            for i, tx in enumerate(xdrs):
                f.write(f"TRANSACTION {i+1}: {tx['name']} ACCOUNT\n")
                f.write(f"Destination: {tx['destination']}\n")
                f.write(f"Amount: {tx['amount']} XLM\n")
                f.write(f"XDR: {tx['xdr']}\n\n")
        
        print("💾 All XDRs saved to multisig_transactions.txt")
        print()
        print("🎯 NEXT STEPS:")
        print("1. Submit TRANSACTION 1 XDR to Lobstr first")
        print("2. Wait for Lobstr to co-sign and submit")
        print("3. Then submit TRANSACTION 2, wait for co-sign") 
        print("4. Then submit TRANSACTION 3, wait for co-sign")
        print("5. All accounts will be funded and ready for OGC deployment!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_multisig_funding_transactions()