#!/usr/bin/env python3
"""
Generate valid Stellar test accounts that we can use for testing airdrops
"""

from stellar_sdk import Keypair
import requests
import json
from config import Config

def generate_test_accounts(count=10):
    """Generate new Stellar keypairs for testing."""
    print(f"🔑 Generating {count} test Stellar accounts...")
    
    accounts = []
    for i in range(count):
        keypair = Keypair.random()
        accounts.append({
            'public_key': keypair.public_key,
            'secret_key': keypair.secret,
            'index': i + 1
        })
    
    return accounts

def fund_testnet_accounts(accounts):
    """Fund accounts on testnet using Friendbot."""
    print("💰 Funding accounts on testnet...")
    
    funded_accounts = []
    for account in accounts:
        try:
            # Use Friendbot to fund testnet account
            friendbot_url = f"https://friendbot.stellar.org?addr={account['public_key']}"
            response = requests.get(friendbot_url)
            
            if response.status_code == 200:
                print(f"✅ Funded: {account['public_key'][:8]}...")
                funded_accounts.append(account)
            else:
                print(f"❌ Failed to fund: {account['public_key'][:8]}...")
                
        except Exception as e:
            print(f"❌ Error funding {account['public_key'][:8]}: {e}")
    
    return funded_accounts

def find_random_active_accounts(limit=20):
    """Find some random active Stellar accounts for testing."""
    print(f"🔍 Finding {limit} random active accounts...")
    
    try:
        # Get recent transactions to find active accounts
        url = "https://horizon.stellar.org/transactions"
        params = {
            'limit': limit * 3,  # Get more to filter
            'order': 'desc'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        active_accounts = set()
        
        if '_embedded' in data and 'records' in data['_embedded']:
            for tx in data['_embedded']['records']:
                # Get source account from each transaction
                source_account = tx.get('source_account')
                if source_account and source_account.startswith('G'):
                    active_accounts.add(source_account)
                
                # Stop when we have enough
                if len(active_accounts) >= limit:
                    break
        
        account_list = list(active_accounts)[:limit]
        
        print(f"✅ Found {len(account_list)} active accounts:")
        for i, account in enumerate(account_list, 1):
            print(f"{i:2d}. {account}")
            
        return account_list
        
    except Exception as e:
        print(f"❌ Error finding active accounts: {e}")
        return []

def save_accounts_to_file(accounts, filename="test_airdrop_recipients.txt"):
    """Save account list to file."""
    with open(filename, 'w') as f:
        for account in accounts:
            if isinstance(account, dict):
                f.write(f"{account['public_key']}\n")
            else:
                f.write(f"{account}\n")
    
    print(f"📁 Saved {len(accounts)} accounts to {filename}")

if __name__ == "__main__":
    print("🧪 GENERATING TEST ACCOUNTS FOR AIRDROP")
    print("=" * 50)
    
    config = Config()
    
    choice = input("""
Choose an option:
1. Generate new test accounts (testnet only)
2. Find random active mainnet accounts (for reference)
3. Both

Enter choice (1/2/3): """).strip()
    
    if choice in ['1', '3']:
        print(f"\n🧪 OPTION 1: Generate Test Accounts")
        test_accounts = generate_test_accounts(10)
        
        if config.STELLAR_NETWORK == 'testnet':
            funded_accounts = fund_testnet_accounts(test_accounts)
            if funded_accounts:
                save_accounts_to_file(funded_accounts, "testnet_airdrop_recipients.txt")
        else:
            print("⚠️  Note: Generated accounts are for testnet. Mainnet accounts need funding.")
            save_accounts_to_file(test_accounts, "generated_test_accounts.txt")
    
    if choice in ['2', '3']:
        print(f"\n🌍 OPTION 2: Find Active Mainnet Accounts")
        active_accounts = find_random_active_accounts(15)
        if active_accounts:
            save_accounts_to_file(active_accounts, "active_mainnet_accounts.txt")
            
            # Ask if user wants to replace current recipients
            replace = input(f"\n🔄 Replace current airdrop_recipients.txt with these active accounts? (yes/no): ").strip().lower()
            if replace == 'yes':
                import shutil
                shutil.copy('airdrop_recipients.txt', 'airdrop_recipients_original_backup.txt')
                save_accounts_to_file(active_accounts, "airdrop_recipients.txt")
                print("✅ Updated airdrop_recipients.txt with active accounts")
                print("💾 Original recipients backed up to airdrop_recipients_original_backup.txt")
    
    print(f"\n💡 Remember: For mainnet airdrops, recipients need to establish OGC trustlines first!")
    print(f"   You can ask them to:")
    print(f"   1. Open their Stellar wallet")
    print(f"   2. Add custom asset: {config.TOKEN_CODE}:{config.ISSUER_PUBLIC_KEY}")
    print(f"   3. Set a trust limit (e.g., 1000 OGC)")