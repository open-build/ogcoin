#!/usr/bin/env python3
"""
Sign and Submit XDR Transaction
This script takes an unsigned XDR, signs it with your secret key, and submits it to Stellar mainnet.
"""

import os
from stellar_sdk import Keypair, Server, TransactionEnvelope

def sign_and_submit_xdr():
    # The XDR you copied from Lobstr
    xdr = "AAAAAgAAAABE4Lp3/K2LMIToMgcAidu6IZNv0S/8XXHgLe5W8KZgigABhqACQdKFAABf/QAAAAAAAAAAAAAAAQAAAAEAAAAAROC6d/ytizCE6DIHAInbuiGTb9Ev/F1x4C3uVvCmYIoAAAAAAAAAAAOc2CGAOOYn63PwEPOdbnJcAXCDuqcXxg8jEmMNIE8kAAAAAAHJw4AAAAAAAAAAAfCmYIoAAABAW+/LCaEE8WljK3pD/TkUO9L+DILyCUfyZcjZGuGSxIBHJQ0+KFF5uC9LbCn9gyk4EZsOJY+W+FWwqTKSav1qDw=="
    
    # Your Lobstr secret key
    lobstr_secret = os.getenv('LOBSTR_SECRET_KEY')
    if not lobstr_secret:
        raise ValueError("LOBSTR_SECRET_KEY environment variable is required")
    
    print("🔐 SIGNING AND SUBMITTING TRANSACTION")
    print("=" * 40)
    
    try:
        # Create server connection
        server = Server("https://horizon.stellar.org")
        
        # Create keypair from your secret
        source_keypair = Keypair.from_secret(lobstr_secret)
        print(f"✅ Using account: {source_keypair.public_key}")
        
        # Decode the transaction envelope
        envelope = TransactionEnvelope.from_xdr(xdr, network_passphrase="Public Global Stellar Network ; September 2015")
        
        print("📋 Transaction Details:")
        tx = envelope.transaction
        for i, op in enumerate(tx.operations):
            if hasattr(op, 'destination'):
                dest = str(op.destination).split(':')[-1] if ':' in str(op.destination) else str(op.destination)
                print(f"   Creating account: {dest}")
            if hasattr(op, 'starting_balance'):
                print(f"   Starting balance: {op.starting_balance} XLM")
        
        print("\n🔑 Signing transaction...")
        
        # The XDR appears to already be signed, but let's check if we need additional signatures
        if len(envelope.signatures) > 0:
            print("⚠️  Transaction is already signed!")
            print("   This might be a multi-signature transaction.")
            
            # For multi-sig accounts, we might need to add our signature
            try:
                envelope.sign(source_keypair)
                print("✅ Added your signature to the transaction")
            except Exception as sig_error:
                print(f"⚠️  Could not add signature: {sig_error}")
        else:
            # Sign the transaction
            envelope.sign(source_keypair)
            print("✅ Transaction signed successfully")
        
        print("\n🚀 Submitting to Stellar mainnet...")
        
        # Submit the transaction
        response = server.submit_transaction(envelope)
        
        print("✅ TRANSACTION SUCCESSFUL!")
        print(f"   Transaction Hash: {response['hash']}")
        print(f"   Ledger: {response['ledger']}")
        print(f"   View on StellarExpert: https://stellar.expert/explorer/public/tx/{response['hash']}")
        
        print("\n🎉 ISSUER ACCOUNT FUNDED!")
        print("   Account GABZZWBBQA4OMJ7LOPYBB445NZZFYALQQO5KOF6GB4RREYYNEBHSJR5N is now active with 3 XLM")
        print("\n📋 NEXT STEPS:")
        print("   1. ✅ Fund issuer account (COMPLETED)")
        print("   2. Fund distributor account: GCDHORR6BPE4UF4TESO4WDKPGBPDPWTP5ZL4UEFD5CARUFHFLSODQRXX")
        print("   3. Fund your personal account: GBLGFRH6B6PQGO2KHLIZXPD3LAV2CWBYW6AJ4EMGXSNLRLT5KQRKLADA")
        print("   4. Deploy OGC token to mainnet")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # If it's an already signed transaction error, let's try a different approach
        if "tx_bad_auth" in str(e) or "bad_auth" in str(e):
            print("\n🔍 MULTI-SIGNATURE DETECTED")
            print("The transaction needs to be signed through Lobstr's interface.")
            print("This is likely because your account has multi-signature enabled.")
            print("\nTry this instead:")
            print("1. In Lobstr app, look for pending transactions")
            print("2. Find this transaction and approve/sign it")
            print("3. Or use the 'Submit Transaction' feature in Lobstr with this XDR")

if __name__ == "__main__":
    sign_and_submit_xdr()