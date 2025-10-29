#!/usr/bin/env python3
"""
OGC Token Mainnet Deployment Script
Creates the issuer account and token on Stellar mainnet

⚠️  MAINNET DEPLOYMENT CHECKLIST:
    □ You have real XLM (minimum 4-5 XLM recommended)
    □ You've secured your private keys properly  
    □ You understand this creates a REAL cryptocurrency
    □ You've tested all operations on testnet first
    □ You have backup of all keys and recovery phrases
"""

from stellar_sdk import Keypair, Server, TransactionBuilder, Network, Asset
from stellar_sdk.exceptions import Ed25519SecretSeedInvalidError
import time
import os
from getpass import getpass

def create_account():
    """Create a new Stellar account"""
    keypair = Keypair.random()
    return {
        'secret_key': keypair.secret,
        'public_key': keypair.public_key
    }

def check_account_funded(server, public_key):
    """Check if account exists and is funded on mainnet"""
    try:
        account = server.load_account(public_key)
        print(f"✅ Account {public_key} exists and is funded")
        print(f"   Balance: {[b.balance for b in account.balances if b.asset_type == 'native'][0]} XLM")
        return True
    except Exception as e:
        print(f"❌ Account {public_key} not found or not funded")
        print(f"   Error: {e}")
        return False

def manual_fund_instructions(public_key):
    """Provide instructions for manually funding the account"""
    print(f"\n🏦 MANUAL FUNDING REQUIRED")
    print(f"═" * 50)
    print(f"Account Public Key: {public_key}")
    print(f"\nTo fund this account, you can:")
    print(f"1. Send XLM from another wallet to: {public_key}")
    print(f"2. Use a Stellar wallet (Lobstr, StellarTerm, etc.)")
    print(f"3. Purchase XLM on an exchange and send to this address")
    print(f"\nMinimum required: 2.5 XLM (2 XLM minimum + fees)")
    print(f"Recommended: 5 XLM (for safety margin)")
    print(f"\n⚠️  IMPORTANT: This is MAINNET - use real XLM only!")
    
    input("\nPress Enter after you've funded the account...")

def create_ogc_mainnet_token():
    """Complete OGC token creation process on MAINNET"""
    print("🚀 CREATING OGC TOKEN ON STELLAR MAINNET")
    print("=" * 50)
    print("⚠️  WARNING: This creates a REAL cryptocurrency with REAL value!")
    print("⚠️  Make sure you have XLM and understand the implications!")
    
    # Confirmation
    confirm = input("\nType 'DEPLOY_MAINNET' to continue: ")
    if confirm != 'DEPLOY_MAINNET':
        print("❌ Deployment cancelled")
        return None
    
    # Step 1: Create or Use Existing Issuer Account
    print("\n1. Issuer Account Setup...")
    use_existing = input("Do you have an existing issuer account? (y/n): ").lower()
    
    if use_existing == 'y':
        issuer_secret = getpass("Enter issuer secret key: ")
        try:
            issuer_keypair = Keypair.from_secret(issuer_secret)
            issuer = {
                'secret_key': issuer_secret,
                'public_key': issuer_keypair.public_key
            }
            print(f"✅ Using existing issuer: {issuer['public_key']}")
        except:
            print("❌ Invalid secret key")
            return None
    else:
        issuer = create_account()
        print(f"🔑 NEW ISSUER ACCOUNT CREATED:")
        print(f"   Secret Key: {issuer['secret_key']}")
        print(f"   Public Key: {issuer['public_key']}")
        print(f"⚠️  SAVE THESE KEYS SECURELY - THEY CONTROL YOUR TOKEN!")
    
    # Step 2: Check/Fund Issuer Account
    print("\n2. Checking Issuer Account Funding...")
    server = Server("https://horizon.stellar.org")
    
    if not check_account_funded(server, issuer['public_key']):
        manual_fund_instructions(issuer['public_key'])
        if not check_account_funded(server, issuer['public_key']):
            print("❌ Account still not funded. Aborting.")
            return None
    
    # Step 3: Create or Use Distribution Account
    print("\n3. Distribution Account Setup...")
    use_existing_dist = input("Do you have an existing distribution account? (y/n): ").lower()
    
    if use_existing_dist == 'y':
        distributor_secret = getpass("Enter distributor secret key: ")
        try:
            distributor_keypair = Keypair.from_secret(distributor_secret)
            distributor = {
                'secret_key': distributor_secret,
                'public_key': distributor_keypair.public_key
            }
            print(f"✅ Using existing distributor: {distributor['public_key']}")
        except:
            print("❌ Invalid secret key")
            return None
    else:
        distributor = create_account()
        print(f"🔑 NEW DISTRIBUTOR ACCOUNT CREATED:")
        print(f"   Secret Key: {distributor['secret_key']}")
        print(f"   Public Key: {distributor['public_key']}")
    
    # Step 4: Check/Fund Distribution Account
    print("\n4. Checking Distribution Account Funding...")
    if not check_account_funded(server, distributor['public_key']):
        manual_fund_instructions(distributor['public_key'])
        if not check_account_funded(server, distributor['public_key']):
            print("❌ Account still not funded. Aborting.")
            return None
    
    # Step 5: Create OGC Asset and Issue Tokens
    print("\n5. Creating OGC Asset and Issuing 1,000,000 Tokens...")
    try:
        # Create asset
        ogc_asset = Asset("OGC", issuer['public_key'])
        
        # Get accounts
        issuer_account = server.load_account(issuer['public_key'])
        distributor_account = server.load_account(distributor['public_key'])
        
        # Create trustline from distributor to issuer for OGC
        print("   Creating trustline...")
        trustline_tx = (
            TransactionBuilder(
                source_account=distributor_account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100
            )
            .append_change_trust_op(asset=ogc_asset, limit="1000000")
            .set_timeout(300)
            .build()
        )
        
        trustline_tx.sign(distributor['secret_key'])
        trustline_response = server.submit_transaction(trustline_tx)
        print("   ✅ Trustline created")
        
        # Reload issuer account for sequence number
        issuer_account = server.load_account(issuer['public_key'])
        
        # Issue 1,000,000 OGC tokens to distribution account
        print("   Issuing 1,000,000 OGC tokens...")
        payment_tx = (
            TransactionBuilder(
                source_account=issuer_account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100
            )
            .append_payment_op(
                destination=distributor['public_key'],
                asset=ogc_asset,
                amount="1000000"
            )
            .add_text_memo("OGC Token Initial Issue - Open Build Fund")
            .set_timeout(300)
            .build()
        )
        
        payment_tx.sign(issuer['secret_key'])
        payment_response = server.submit_transaction(payment_tx)
        print("   ✅ 1,000,000 OGC tokens issued!")
        
        # Step 6: Generate .env file
        print("\n6. Generating .env configuration...")
        env_content = f"""# OGC Token Mainnet Configuration
# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
# ⚠️  KEEP THIS FILE SECURE - NEVER COMMIT TO VERSION CONTROL!

# Stellar Network Configuration
STELLAR_NETWORK=public

# Token Configuration
TOKEN_CODE=OGC
TOTAL_SUPPLY=1000000

# Account Keys
ISSUER_SECRET_KEY={issuer['secret_key']}
ISSUER_PUBLIC_KEY={issuer['public_key']}
DISTRIBUTOR_SECRET_KEY={distributor['secret_key']}
DISTRIBUTOR_PUBLIC_KEY={distributor['public_key']}

# Website Integration
WEBSITE_URL=https://open-build.github.io/ogcoin
WEBSITE_REPORTS_DIR=../reports
WEBSITE_API_ENDPOINT=https://open-build.github.io/ogcoin/api

# Tool Settings
GENERATE_REPORTS=true
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("   ✅ .env file created")
        
        # Step 7: Success Summary
        print("\n" + "=" * 50)
        print("🎉 OGC TOKEN SUCCESSFULLY DEPLOYED TO MAINNET!")
        print("=" * 50)
        print(f"Token Code: OGC")
        print(f"Issuer: {issuer['public_key']}")
        print(f"Total Supply: 1,000,000 OGC")
        print(f"Distribution Account: {distributor['public_key']}")
        print(f"Network: Stellar Mainnet")
        
        print(f"\n🔗 Stellar Expert Links:")
        print(f"Issuer: https://stellar.expert/explorer/public/account/{issuer['public_key']}")
        print(f"Distributor: https://stellar.expert/explorer/public/account/{distributor['public_key']}")
        print(f"Asset: https://stellar.expert/explorer/public/asset/OGC-{issuer['public_key']}")
        
        print(f"\n⚠️  SECURITY REMINDERS:")
        print(f"• Your keys are saved in .env - keep this file secure!")
        print(f"• Make backup copies of your keys in a safe place")
        print(f"• Never share your secret keys with anyone")
        print(f"• Consider using hardware wallets for large amounts")
        
        return {
            'issuer': issuer,
            'distributor': distributor,
            'asset_code': 'OGC',
            'total_supply': '1000000',
            'network': 'mainnet'
        }
        
    except Exception as e:
        print(f"❌ Error creating token: {e}")
        return None

if __name__ == "__main__":
    result = create_ogc_mainnet_token()
    if result:
        print(f"\n✅ Deployment completed successfully!")
        print(f"You can now use the CLI tools with STELLAR_NETWORK=public")
    else:
        print(f"\n❌ Deployment failed or cancelled")