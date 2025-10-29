#!/usr/bin/env python3
"""
OGC Trustline Establishment Tool
Helps accounts establish trustlines for the OGC token so they can receive airdrops.
"""

import os
import time
from stellar_sdk import Keypair, Server, TransactionBuilder, Asset
from config import Config

def establish_trustline_for_account(account_secret_key, trust_limit="1000"):
    """Establish a trustline for OGC token for a specific account."""
    config = Config()
    server = Server(config.HORIZON_URL)
    
    try:
        # Create keypair from secret
        account_keypair = Keypair.from_secret(account_secret_key)
        print(f"📋 Account: {account_keypair.public_key}")
        
        # Load account
        account = server.load_account(account_keypair.public_key)
        
        # Define OGC asset
        ogc_asset = Asset(config.TOKEN_CODE, config.ISSUER_PUBLIC_KEY)
        
        # Build trustline transaction
        transaction = (
            TransactionBuilder(
                source_account=account,
                network_passphrase=config.NETWORK_PASSPHRASE,
                base_fee=100
            )
            .append_change_trust_op(
                asset=ogc_asset,
                limit=trust_limit  # Maximum OGC this account can hold
            )
            .set_timeout(30)
            .build()
        )
        
        # Sign and submit
        transaction.sign(account_keypair)
        response = server.submit_transaction(transaction)
        
        print(f"✅ Trustline established! Hash: {response['hash'][:16]}...")
        print(f"   Limit: {trust_limit} OGC")
        return True, response['hash']
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Failed to establish trustline: {error_msg}")
        return False, error_msg

def generate_trustline_instructions():
    """Generate instructions for users to establish trustlines manually."""
    config = Config()
    
    instructions = f"""
🔗 HOW TO ESTABLISH OGC TRUSTLINE MANUALLY

For users who want to establish trustlines in their own wallets:

1. **Open your Stellar wallet** (Lobstr, StellarTerm, etc.)

2. **Add Custom Asset:**
   • Asset Code: {config.TOKEN_CODE}
   • Issuer: {config.ISSUER_PUBLIC_KEY}
   • Trust Limit: 1000 (or your preferred maximum)

3. **Confirm the trustline transaction**

4. **You're ready to receive OGC tokens!**

📋 COPY-PASTE INFO:
Asset Code: {config.TOKEN_CODE}
Issuer: {config.ISSUER_PUBLIC_KEY}

🌐 View Token Info:
https://stellar.expert/explorer/public/asset/{config.TOKEN_CODE}-{config.ISSUER_PUBLIC_KEY}
"""
    
    return instructions

def create_test_accounts_with_trustlines(count=5):
    """Create test accounts and establish trustlines for testing."""
    config = Config()
    server = Server(config.HORIZON_URL)
    
    print(f"🧪 Creating {count} test accounts with OGC trustlines...")
    
    if config.STELLAR_NETWORK == 'mainnet':
        print("⚠️  WARNING: This will create accounts on MAINNET!")
        print("💡 Consider switching to testnet for testing purposes.")
        confirm = input("Continue on mainnet? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Cancelled")
            return []
    
    test_accounts = []
    
    for i in range(count):
        try:
            # Generate random keypair
            keypair = Keypair.random()
            print(f"\n[{i+1}/{count}] 🔑 Generated: {keypair.public_key[:8]}...")
            
            if config.STELLAR_NETWORK == 'testnet':
                # Fund with Friendbot (testnet only)
                import requests
                friendbot_url = f"https://friendbot.stellar.org?addr={keypair.public_key}"
                response = requests.get(friendbot_url)
                
                if response.status_code != 200:
                    print(f"❌ Failed to fund testnet account")
                    continue
                
                print(f"💰 Funded with XLM")
                
                # Wait a moment for funding to complete
                time.sleep(2)
                
                # Establish trustline
                success, result = establish_trustline_for_account(keypair.secret, "1000")
                
                if success:
                    test_accounts.append({
                        'public_key': keypair.public_key,
                        'secret_key': keypair.secret,
                        'trustline_hash': result
                    })
                    print(f"✅ Test account ready for OGC!")
                    
            else:
                # Mainnet - just save the keypair, user needs to fund it
                test_accounts.append({
                    'public_key': keypair.public_key,
                    'secret_key': keypair.secret,
                    'funded': False,
                    'trustline_established': False
                })
                print(f"📝 Account generated (needs funding and trustline)")
            
        except Exception as e:
            print(f"❌ Failed to create account {i+1}: {e}")
    
    return test_accounts

def save_test_accounts(accounts, filename="test_accounts_with_trustlines.txt"):
    """Save test accounts to file."""
    with open(filename, 'w') as f:
        f.write("# Test Accounts with OGC Trustlines\n")
        f.write("# Format: PUBLIC_KEY,SECRET_KEY,STATUS\n\n")
        
        for account in accounts:
            status = "READY" if account.get('trustline_hash') else "NEEDS_FUNDING"
            f.write(f"{account['public_key']},{account['secret_key']},{status}\n")
    
    print(f"📁 Saved {len(accounts)} test accounts to {filename}")

def update_recipients_with_trustline_accounts():
    """Replace current recipients with accounts that have trustlines."""
    config = Config()
    
    # Use the 2 accounts we found earlier that have trustlines
    trustline_accounts = [
        "GBZAC66WWHFU2FEOG5KECSEVR6EJO7BYK63UGB52SENDN4JEJTJEVK5L",  # 10,000 OGC
        # Skip the treasury account with 999M OGC as it's likely the distribution account
    ]
    
    # Add some of our current valid accounts (they'll get trustline errors but won't break)
    current_accounts = []
    try:
        with open('airdrop_recipients.txt', 'r') as f:
            current_accounts = [line.strip() for line in f if line.strip()][:3]  # Just take 3
    except:
        pass
    
    combined_accounts = trustline_accounts + current_accounts
    
    print(f"📋 Creating recipients list with {len(combined_accounts)} accounts:")
    print(f"   • {len(trustline_accounts)} accounts with established trustlines")
    print(f"   • {len(current_accounts)} valid accounts (will need trustlines)")
    
    # Backup and update
    import shutil
    shutil.copy('airdrop_recipients.txt', 'airdrop_recipients_pre_trustline.txt')
    
    with open('airdrop_recipients_with_trustlines.txt', 'w') as f:
        for account in combined_accounts:
            f.write(f"{account}\n")
    
    print(f"📁 Created airdrop_recipients_with_trustlines.txt")
    print(f"💾 Backed up original to airdrop_recipients_pre_trustline.txt")

if __name__ == "__main__":
    print("🔗 OGC TRUSTLINE ESTABLISHMENT TOOL")
    print("=" * 50)
    
    config = Config()
    print(f"🌍 Network: {config.STELLAR_NETWORK.upper()}")
    print(f"🪙 Token: {config.TOKEN_CODE}")
    print(f"💰 Issuer: {config.ISSUER_PUBLIC_KEY}")
    
    choice = input("""
Choose an option:
1. Generate manual trustline instructions
2. Create test accounts with trustlines (testnet recommended)
3. Create recipients list with known trustline accounts
4. Establish trustline for existing account (need secret key)

Enter choice (1/2/3/4): """).strip()
    
    if choice == '1':
        print(generate_trustline_instructions())
        
        # Save instructions to file
        with open('trustline_instructions.txt', 'w') as f:
            f.write(generate_trustline_instructions())
        print("📁 Instructions saved to trustline_instructions.txt")
        
    elif choice == '2':
        count = int(input("How many test accounts? (default: 5): ") or "5")
        accounts = create_test_accounts_with_trustlines(count)
        
        if accounts:
            save_test_accounts(accounts)
            
            # Ask if user wants to use these for airdrop
            if config.STELLAR_NETWORK == 'testnet':
                use_for_airdrop = input("Use these accounts for airdrop testing? (yes/no): ").strip().lower()
                if use_for_airdrop == 'yes':
                    with open('airdrop_recipients.txt', 'w') as f:
                        for account in accounts:
                            f.write(f"{account['public_key']}\n")
                    print("✅ Updated airdrop_recipients.txt with test accounts")
        
    elif choice == '3':
        update_recipients_with_trustline_accounts()
        
    elif choice == '4':
        secret_key = input("Enter account secret key (starts with 'S'): ").strip()
        if secret_key.startswith('S'):
            trust_limit = input("Trust limit (default: 1000): ").strip() or "1000"
            establish_trustline_for_account(secret_key, trust_limit)
        else:
            print("❌ Invalid secret key format")
    
    else:
        print("❌ Invalid choice")
    
    print(f"\n💡 Remember: Only accounts with established trustlines can receive OGC tokens!")
    print(f"🔗 View OGC token: https://stellar.expert/explorer/public/asset/{config.TOKEN_CODE}-{config.ISSUER_PUBLIC_KEY}")