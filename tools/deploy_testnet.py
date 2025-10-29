#!/usr/bin/env python3
"""
Deploy OGC Token on Stellar Testnet
Emergency deployment since mainnet account is locked by multi-signature.
"""

from stellar_sdk import Keypair, Server, TransactionBuilder, Network, Asset
import os

def deploy_ogc_testnet():
    print("🚀 DEPLOYING OGC TOKEN ON STELLAR TESTNET")
    print("=" * 45)
    
    # Testnet accounts (from previous generation)
    issuer_secret = "SDDGAD7SUSVPVCMCTMV7RCB7OMHONGUUUSQPWHFRS2FZT4YPMPYZX5CR"
    distributor_secret = "SAVE2QZL45QT5LTU52EFJCB6CC3E4IRHZEKPIOPW6C2WOKM6CS6DNV6L"
    personal_secret = "SBMH2QWP7JBZUMTVWP7MRE3L4RSNdzpucwant5END4SE5OB4B3DYTSMJ"
    
    issuer_keypair = Keypair.from_secret(issuer_secret)
    distributor_keypair = Keypair.from_secret(distributor_secret)
    personal_keypair = Keypair.from_secret(personal_secret)
    
    # Connect to testnet
    server = Server("https://horizon-testnet.stellar.org")
    
    try:
        print(f"✅ Issuer: {issuer_keypair.public_key}")
        print(f"✅ Distributor: {distributor_keypair.public_key}")
        print(f"✅ Personal: {personal_keypair.public_key}")
        print()
        
        # Create OGC asset
        ogc_asset = Asset("OGC", issuer_keypair.public_key)
        
        print("🏗️  STEP 1: Creating OGC Token...")
        
        # Load distributor account
        distributor_account = server.load_account(distributor_keypair.public_key)
        
        # Create trustline from distributor to OGC
        trustline_tx = (
            TransactionBuilder(
                source_account=distributor_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=100000
            )
            .append_change_trust_op(asset=ogc_asset, limit="1000000000")
            .set_timeout(300)
            .build()
        )
        trustline_tx.sign(distributor_keypair)
        
        response = server.submit_transaction(trustline_tx)
        print(f"   ✅ Trustline created: {response['hash'][:20]}...")
        
        print("🏗️  STEP 2: Minting OGC Tokens...")
        
        # Load issuer account
        issuer_account = server.load_account(issuer_keypair.public_key)
        
        # Issue 1 billion OGC tokens to distributor
        issue_tx = (
            TransactionBuilder(
                source_account=issuer_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=100000
            )
            .append_payment_op(
                destination=distributor_keypair.public_key,
                asset=ogc_asset,
                amount="1000000000"
            )
            .set_timeout(300)
            .build()
        )
        issue_tx.sign(issuer_keypair)
        
        response = server.submit_transaction(issue_tx)
        print(f"   ✅ 1 billion OGC minted: {response['hash'][:20]}...")
        
        print("🏗️  STEP 3: Setting up personal account...")
        
        # Load personal account
        personal_account = server.load_account(personal_keypair.public_key)
        
        # Create trustline from personal to OGC
        personal_trustline_tx = (
            TransactionBuilder(
                source_account=personal_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=100000
            )
            .append_change_trust_op(asset=ogc_asset, limit="1000000")
            .set_timeout(300)
            .build()
        )
        personal_trustline_tx.sign(personal_keypair)
        
        response = server.submit_transaction(personal_trustline_tx)
        print(f"   ✅ Personal trustline: {response['hash'][:20]}...")
        
        print("🏗️  STEP 4: Transferring OGC to your account...")
        
        # Reload distributor account
        distributor_account = server.load_account(distributor_keypair.public_key)
        
        # Send 10,000 OGC to personal account
        transfer_tx = (
            TransactionBuilder(
                source_account=distributor_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=100000
            )
            .append_payment_op(
                destination=personal_keypair.public_key,
                asset=ogc_asset,
                amount="10000"
            )
            .set_timeout(300)
            .build()
        )
        transfer_tx.sign(distributor_keypair)
        
        response = server.submit_transaction(transfer_tx)
        print(f"   ✅ 10,000 OGC transferred: {response['hash'][:20]}...")
        
        print()
        print("🎉 OGC TOKEN SUCCESSFULLY DEPLOYED ON TESTNET!")
        print("=" * 50)
        print(f"Token Code: OGC")
        print(f"Issuer: {issuer_keypair.public_key}")
        print(f"Total Supply: 1,000,000,000 OGC")
        print(f"Your Balance: 10,000 OGC")
        print(f"Network: Stellar Testnet")
        print()
        print("🔗 VIEW ON STELLAR EXPERT:")
        print(f"https://stellar.expert/explorer/testnet/asset/OGC-{issuer_keypair.public_key}")
        print()
        print("✅ NEXT STEPS:")
        print("1. Update website to show testnet deployment")
        print("2. Test all CLI functionality")
        print("3. Demonstrate OGC features")
        print("4. Migrate to mainnet when account access restored")
        
        # Save deployment info
        with open("testnet_deployment_success.txt", "w") as f:
            f.write("OGC TESTNET DEPLOYMENT - SUCCESS\\n")
            f.write("="*35 + "\\n\\n")
            f.write(f"Token: OGC\\n")
            f.write(f"Issuer: {issuer_keypair.public_key}\\n")
            f.write(f"Total Supply: 1,000,000,000\\n")
            f.write(f"Network: Stellar Testnet\\n")
            f.write(f"Your OGC Balance: 10,000\\n\\n")
            f.write(f"Stellar Expert: https://stellar.expert/explorer/testnet/asset/OGC-{issuer_keypair.public_key}\\n")
        
        print("💾 Deployment details saved!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    deploy_ogc_testnet()