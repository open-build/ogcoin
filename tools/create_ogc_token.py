#!/usr/bin/env python3
"""
Simple OGC Token Creation Script
Creates the issuer account and token on Stellar testnet
"""

from stellar_sdk import Keypair, Server, TransactionBuilder, Network, Asset
from stellar_sdk.exceptions import Ed25519SecretSeedInvalidError
import requests
import time

def create_account():
    """Create a new Stellar account"""
    keypair = Keypair.random()
    return {
        'secret_key': keypair.secret,
        'public_key': keypair.public_key
    }

def fund_testnet_account(public_key):
    """Fund account on testnet using Friendbot"""
    try:
        response = requests.get(f'https://friendbot.stellar.org?addr={public_key}')
        if response.status_code == 200:
            print(f"✅ Account {public_key} funded successfully!")
            return True
        else:
            print(f"❌ Failed to fund account: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error funding account: {e}")
        return False

def create_ogc_token():
    """Complete OGC token creation process"""
    print("🚀 Creating OGC Token on Stellar Testnet")
    print("=" * 50)
    
    # Step 1: Create Issuer Account
    print("\n1. Creating Issuer Account...")
    issuer = create_account()
    print(f"   Secret Key: {issuer['secret_key']}")
    print(f"   Public Key: {issuer['public_key']}")
    
    # Step 2: Fund Issuer Account
    print("\n2. Funding Issuer Account...")
    if not fund_testnet_account(issuer['public_key']):
        return None
    
    # Wait for funding to process
    time.sleep(5)
    
    # Step 3: Create Distribution Account
    print("\n3. Creating Distribution Account...")
    distributor = create_account()
    print(f"   Secret Key: {distributor['secret_key']}")
    print(f"   Public Key: {distributor['public_key']}")
    
    # Step 4: Fund Distribution Account
    print("\n4. Funding Distribution Account...")
    if not fund_testnet_account(distributor['public_key']):
        return None
    
    time.sleep(5)
    
    # Step 5: Create OGC Asset and Initial Distribution
    print("\n5. Creating OGC Asset and Initial Distribution...")
    try:
        server = Server("https://horizon-testnet.stellar.org")
        
        # Create asset
        ogc_asset = Asset("OGC", issuer['public_key'])
        
        # Get accounts
        issuer_account = server.load_account(issuer['public_key'])
        distributor_account = server.load_account(distributor['public_key'])
        
        # Create trustline from distributor to issuer for OGC
        trustline_tx = (
            TransactionBuilder(
                source_account=distributor_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=100
            )
            .append_change_trust_op(asset=ogc_asset, limit="1000000")
            .set_timeout(300)
            .build()
        )
        
        trustline_tx.sign(distributor['secret_key'])
        trustline_response = server.submit_transaction(trustline_tx)
        print("   ✅ Trustline created")
        
        # Issue 1,000,000 OGC tokens to distribution account
        payment_tx = (
            TransactionBuilder(
                source_account=issuer_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=100
            )
            .append_payment_op(
                destination=distributor['public_key'],
                asset=ogc_asset,
                amount="1000000"
            )
            .set_timeout(300)
            .build()
        )
        
        payment_tx.sign(issuer['secret_key'])
        payment_response = server.submit_transaction(payment_tx)
        print("   ✅ 1,000,000 OGC tokens issued!")
        
        print("\n🎉 OGC Token Created Successfully!")
        print("=" * 50)
        print(f"Token Code: OGC")
        print(f"Issuer: {issuer['public_key']}")
        print(f"Total Supply: 1,000,000 OGC")
        print(f"Network: Stellar Testnet")
        print(f"Distribution Account: {distributor['public_key']}")
        
        # Save configuration
        env_content = f"""# OGC Token Configuration
STELLAR_NETWORK=testnet
TOKEN_CODE=OGC
TOTAL_SUPPLY=1000000

# Account Keys
ISSUER_SECRET_KEY={issuer['secret_key']}
ISSUER_PUBLIC_KEY={issuer['public_key']}
DISTRIBUTOR_SECRET_KEY={distributor['secret_key']}
DISTRIBUTOR_PUBLIC_KEY={distributor['public_key']}

# Website Integration
WEBSITE_URL=https://greglind.github.io/ogcoin
WEBSITE_REPORTS_DIR=../reports
WEBSITE_API_ENDPOINT=https://greglind.github.io/ogcoin/api
GENERATE_REPORTS=true
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("\n💾 Configuration saved to .env file")
        
        return {
            'issuer': issuer,
            'distributor': distributor,
            'asset_code': 'OGC',
            'total_supply': '1000000'
        }
        
    except Exception as e:
        print(f"❌ Error creating token: {e}")
        return None

if __name__ == "__main__":
    result = create_ogc_token()
    if result:
        print("\n🔗 Next Steps:")
        print("1. Test your token with: python cli.py account balance")
        print("2. Create bulk payments with: python cli.py payments process test_payments.csv")
        print("3. Generate transparency reports with: python cli.py reports generate")
        print("4. When ready, switch to mainnet in .env file")