#!/usr/bin/env python3
"""
Find Stellar accounts that have established trustlines for OGC token
"""

import requests
import json
from config import Config

def find_accounts_with_ogc_trustlines(limit=100):
    """Find accounts that have OGC trustlines established."""
    config = Config()
    
    print(f"🔍 Searching for accounts with OGC trustlines...")
    print(f"💰 OGC Issuer: {config.ISSUER_PUBLIC_KEY}")
    print(f"🪙 Token Code: {config.TOKEN_CODE}")
    
    # Use Stellar API to find accounts holding OGC
    url = f"https://horizon.stellar.org/accounts"
    params = {
        'asset': f"{config.TOKEN_CODE}:{config.ISSUER_PUBLIC_KEY}",
        'limit': limit
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        accounts_with_trustlines = []
        
        if '_embedded' in data and 'records' in data['_embedded']:
            for record in data['_embedded']['records']:
                account_id = record['account_id']
                
                # Check if account has OGC balance (meaning trustline exists)
                for balance in record.get('balances', []):
                    if (balance.get('asset_code') == config.TOKEN_CODE and 
                        balance.get('asset_issuer') == config.ISSUER_PUBLIC_KEY):
                        
                        accounts_with_trustlines.append({
                            'account_id': account_id,
                            'balance': balance.get('balance', '0'),
                            'limit': balance.get('limit', 'none')
                        })
                        break
        
        print(f"\n✅ Found {len(accounts_with_trustlines)} accounts with OGC trustlines:")
        
        valid_recipients = []
        for i, account in enumerate(accounts_with_trustlines, 1):
            print(f"{i:2d}. {account['account_id']} (Balance: {account['balance']} OGC)")
            valid_recipients.append(account['account_id'])
            
        return valid_recipients
        
    except requests.RequestException as e:
        print(f"❌ Error querying Stellar API: {e}")
        return []

def update_recipients_file(new_recipients, backup_original=True):
    """Update the recipients file with accounts that have trustlines."""
    
    if backup_original:
        # Backup original file
        import shutil
        shutil.copy('airdrop_recipients.txt', 'airdrop_recipients_backup.txt')
        print(f"📁 Backed up original to airdrop_recipients_backup.txt")
    
    # Write new recipients
    with open('airdrop_recipients.txt', 'w') as f:
        for recipient in new_recipients:
            f.write(f"{recipient}\n")
    
    print(f"✅ Updated airdrop_recipients.txt with {len(new_recipients)} accounts that have OGC trustlines")

if __name__ == "__main__":
    print("🔍 FINDING ACCOUNTS WITH OGC TRUSTLINES")
    print("=" * 50)
    
    # Find accounts with trustlines
    valid_recipients = find_accounts_with_ogc_trustlines(limit=50)
    
    if valid_recipients:
        print(f"\n📝 Found {len(valid_recipients)} accounts ready to receive OGC")
        
        # Ask if user wants to update the recipients file
        if len(valid_recipients) >= 10:  # Need at least 10 for a good airdrop
            update_choice = input("\n🔄 Update airdrop_recipients.txt with these accounts? (yes/no): ").strip().lower()
            if update_choice == 'yes':
                update_recipients_file(valid_recipients[:20])  # Use first 20 accounts
            else:
                print("📋 Recipients file not updated. Here are the accounts for manual copy:")
                for recipient in valid_recipients:
                    print(recipient)
        else:
            print(f"⚠️  Only found {len(valid_recipients)} accounts. Need more for a good airdrop.")
            print("💡 Consider finding more accounts or asking users to establish trustlines first.")
    else:
        print("❌ No accounts found with OGC trustlines established.")
        print("💡 This might mean:")
        print("   • The OGC token is new and no one has trustlines yet")
        print("   • Need to ask recipients to establish trustlines first")
        print("   • Or find accounts that have already opted in to receive OGC")