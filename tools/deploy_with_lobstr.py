#!/usr/bin/env python3
"""
OGC Mainnet Deployment using Existing Lobstr Account
Uses your funded Lobstr account to create issuer and distributor accounts
"""

from stellar_sdk import Keypair, Server, TransactionBuilder, Network, Asset
import time
import os

def deploy_ogc_with_lobstr():
    """Deploy OGC to mainnet using existing Lobstr account for funding"""
    
    print("🚀 OGC MAINNET DEPLOYMENT WITH LOBSTR FUNDING")
    print("=" * 55)
    
    # Your Lobstr account details
    lobstr_secret = os.getenv('LOBSTR_SECRET_KEY')
    if not lobstr_secret:
        raise ValueError("LOBSTR_SECRET_KEY environment variable is required")
    lobstr_keypair = Keypair.from_secret(lobstr_secret)
    lobstr_public = lobstr_keypair.public_key
    
    print(f"💰 Funding Account (Lobstr): {lobstr_public}")
    print(f"💎 Available: 480.32 XLM")
    
    # Confirmation
    confirm = input("\nType 'DEPLOY_MAINNET' to create OGC on mainnet: ")
    if confirm != 'DEPLOY_MAINNET':
        print("❌ Deployment cancelled")
        return None
    
    try:
        server = Server("https://horizon.stellar.org")
        
        # Step 1: Create Issuer Account
        print("\n1. Creating OGC Issuer Account...")
        issuer = Keypair.random()
        print(f"   Public Key: {issuer.public_key}")
        print(f"   Secret Key: {issuer.secret}")
        
        # Fund issuer account (2.5 XLM)
        print("   Funding issuer account...")
        
        # Load account fresh to get current sequence
        lobstr_account = server.load_account(lobstr_public)
        
        create_issuer_tx = (
            TransactionBuilder(
                source_account=lobstr_account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100
            )
            .append_create_account_op(
                destination=issuer.public_key,
                starting_balance="2.5"
            )
            .add_text_memo("Create OGC Issuer Account")
            .set_timeout(300)
            .build()
        )
        
        # Sign with the keypair object, not the string
        create_issuer_tx.sign(lobstr_keypair)
        response = server.submit_transaction(create_issuer_tx)
        print("   ✅ Issuer account created and funded!")
        print(f"   Transaction: {response['hash']}")
        
        # Step 2: Create Distribution Account  
        print("\n2. Creating OGC Distribution Account...")
        distributor = Keypair.random()
        print(f"   Public Key: {distributor.public_key}")
        print(f"   Secret Key: {distributor.secret}")
        
        # Fund distributor account (2.5 XLM)
        print("   Funding distributor account...")
        
        # Reload account for fresh sequence number
        lobstr_account = server.load_account(lobstr_public)
        
        create_dist_tx = (
            TransactionBuilder(
                source_account=lobstr_account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100
            )
            .append_create_account_op(
                destination=distributor.public_key,
                starting_balance="2.5"
            )
            .add_text_memo("Create OGC Distribution Account")
            .set_timeout(300)
            .build()
        )
        
        create_dist_tx.sign(lobstr_keypair)
        response = server.submit_transaction(create_dist_tx)
        print("   ✅ Distribution account created and funded!")
        print(f"   Transaction: {response['hash']}")
        
        # Wait for accounts to be available
        time.sleep(3)
        
        # Step 3: Create OGC Asset and Issue Tokens
        print("\n3. Creating OGC Asset...")
        ogc_asset = Asset("OGC", issuer.public_key)
        
        # Create trustline from distributor to issuer
        print("   Creating trustline...")
        distributor_account = server.load_account(distributor.public_key)
        
        trustline_tx = (
            TransactionBuilder(
                source_account=distributor_account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100
            )
            .append_change_trust_op(asset=ogc_asset, limit="1000000")
            .add_text_memo("OGC Trustline Creation")
            .set_timeout(300)
            .build()
        )
        
        trustline_tx.sign(distributor.secret)
        response = server.submit_transaction(trustline_tx)
        print("   ✅ Trustline created!")
        
        # Issue 1,000,000 OGC tokens
        print("\n4. Issuing 1,000,000 OGC Tokens...")
        issuer_account = server.load_account(issuer.public_key)
        
        issue_tx = (
            TransactionBuilder(
                source_account=issuer_account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100
            )
            .append_payment_op(
                destination=distributor.public_key,
                asset=ogc_asset,
                amount="1000000"
            )
            .add_text_memo("OGC Initial Token Issue - 1M Supply")
            .set_timeout(300)
            .build()
        )
        
        issue_tx.sign(issuer.secret)
        response = server.submit_transaction(issue_tx)
        print("   ✅ 1,000,000 OGC tokens issued!")
        
        # Step 5: Generate .env file
        print("\n5. Generating Mainnet Configuration...")
        env_content = f'''# OGC Token Mainnet Configuration
# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
# ⚠️  KEEP THIS FILE SECURE - NEVER COMMIT TO VERSION CONTROL!

# Stellar Network Configuration
STELLAR_NETWORK=public

# Token Configuration
TOKEN_CODE=OGC
TOTAL_SUPPLY=1000000

# Account Keys
ISSUER_SECRET_KEY={issuer.secret}
ISSUER_PUBLIC_KEY={issuer.public_key}
DISTRIBUTOR_SECRET_KEY={distributor.secret}
DISTRIBUTOR_PUBLIC_KEY={distributor.public_key}

# Your Lobstr Account (for reference)
LOBSTR_SECRET_KEY={lobstr_secret}
LOBSTR_PUBLIC_KEY={lobstr_public}

# Website Integration
WEBSITE_URL=https://open-build.github.io/ogcoin
WEBSITE_REPORTS_DIR=../reports
WEBSITE_API_ENDPOINT=https://open-build.github.io/ogcoin/api

# Tool Settings
GENERATE_REPORTS=true
'''
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("   ✅ .env file created with mainnet configuration!")
        
        # Success Summary
        print("\n" + "=" * 60)
        print("🎉 OGC TOKEN SUCCESSFULLY DEPLOYED TO STELLAR MAINNET!")
        print("=" * 60)
        print(f"💰 Total Cost: ~5.01 XLM (2.5 + 2.5 + fees)")
        print(f"💎 Remaining Lobstr Balance: ~475 XLM")
        print(f"")
        print(f"🪙 Token Details:")
        print(f"   Code: OGC")
        print(f"   Supply: 1,000,000")
        print(f"   Network: Stellar Mainnet")
        print(f"")
        print(f"🔑 Account Details:")
        print(f"   Issuer: {issuer.public_key}")
        print(f"   Distributor: {distributor.public_key}")
        print(f"   Lobstr (Funding): {lobstr_public}")
        
        print(f"\n🔗 Stellar Expert Links:")
        print(f"   Issuer: https://stellar.expert/explorer/public/account/{issuer.public_key}")
        print(f"   Distributor: https://stellar.expert/explorer/public/account/{distributor.public_key}")
        print(f"   OGC Asset: https://stellar.expert/explorer/public/asset/OGC-{issuer.public_key}")
        
        print(f"\n✅ Next Steps:")
        print(f"   1. Run: python cli.py status (should show MAINNET)")
        print(f"   2. Test: python cli.py account info --address {issuer.public_key}")
        print(f"   3. Update website to reflect mainnet status")
        print(f"   4. Announce OGC mainnet launch! 🚀")
        
        return {
            'issuer': {'public': issuer.public_key, 'secret': issuer.secret},
            'distributor': {'public': distributor.public_key, 'secret': distributor.secret},
            'lobstr': {'public': lobstr_public, 'secret': lobstr_secret},
            'asset_code': 'OGC',
            'total_supply': '1000000',
            'network': 'mainnet'
        }
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = deploy_ogc_with_lobstr()
    if result:
        print(f"\n🎉 OGC is now LIVE on Stellar mainnet!")
        print(f"🌍 Welcome to the real cryptocurrency world!")
    else:
        print(f"\n❌ Deployment failed. Check errors above.")