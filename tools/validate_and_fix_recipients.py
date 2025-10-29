#!/usr/bin/env python3
"""
Account validator and replacer for airdrop distribution
Checks accounts and replaces bad ones automatically
"""

import requests
from stellar_sdk import Server
from config import Config

def check_account_validity(account_id):
    """Check if a Stellar account exists and is active."""
    try:
        server = Server("https://horizon.stellar.org")
        account = server.load_account(account_id)
        return True, "Account exists and is active"
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg.lower():
            return False, "Account not found or inactive"
        else:
            return False, f"Error checking account: {error_msg}"

def find_replacement_accounts(count=5):
    """Find replacement accounts from recent transactions."""
    try:
        url = "https://horizon.stellar.org/transactions"
        params = {
            'limit': count * 5,  # Get more to filter
            'order': 'desc'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        replacement_accounts = set()
        
        if '_embedded' in data and 'records' in data['_embedded']:
            for tx in data['_embedded']['records']:
                source_account = tx.get('source_account')
                if source_account and source_account.startswith('G'):
                    replacement_accounts.add(source_account)
                
                if len(replacement_accounts) >= count:
                    break
        
        return list(replacement_accounts)[:count]
        
    except Exception as e:
        print(f"❌ Error finding replacement accounts: {e}")
        return []

def validate_and_fix_recipients(filename="airdrop_recipients.txt"):
    """Validate all recipients and replace bad ones."""
    print(f"🔍 VALIDATING RECIPIENTS IN {filename}")
    print("=" * 50)
    
    # Read current recipients
    try:
        with open(filename, 'r') as f:
            recipients = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return
    
    print(f"📋 Checking {len(recipients)} recipients...")
    
    valid_recipients = []
    bad_recipients = []
    
    # Check each account
    for i, recipient in enumerate(recipients, 1):
        print(f"[{i:2d}/{len(recipients)}] Checking {recipient[:8]}...", end=" ")
        
        is_valid, reason = check_account_validity(recipient)
        
        if is_valid:
            print("✅")
            valid_recipients.append(recipient)
        else:
            print(f"❌ {reason}")
            bad_recipients.append({
                'account': recipient,
                'reason': reason
            })
    
    print(f"\n📊 VALIDATION RESULTS:")
    print(f"   ✅ Valid accounts: {len(valid_recipients)}")
    print(f"   ❌ Bad accounts: {len(bad_recipients)}")
    
    if bad_recipients:
        print(f"\n🚨 BAD ACCOUNTS FOUND:")
        for i, bad in enumerate(bad_recipients, 1):
            print(f"   {i}. {bad['account'][:8]}... - {bad['reason']}")
        
        # Find replacements
        replace_choice = input(f"\n🔄 Replace {len(bad_recipients)} bad accounts? (yes/no): ").strip().lower()
        
        if replace_choice == 'yes':
            print(f"\n🔍 Finding {len(bad_recipients)} replacement accounts...")
            replacements = find_replacement_accounts(len(bad_recipients) + 2)  # Get a few extra
            
            if len(replacements) >= len(bad_recipients):
                # Backup original file
                import shutil
                backup_filename = f"{filename}.backup"
                shutil.copy(filename, backup_filename)
                print(f"📁 Backed up original to {backup_filename}")
                
                # Create new recipients list
                final_recipients = valid_recipients.copy()
                
                print(f"\n🔄 REPLACEMENTS:")
                for i, bad in enumerate(bad_recipients):
                    replacement = replacements[i]
                    print(f"   ❌ {bad['account'][:8]}... → ✅ {replacement[:8]}...")
                    final_recipients.append(replacement)
                
                # Write updated file
                with open(filename, 'w') as f:
                    for recipient in final_recipients:
                        f.write(f"{recipient}\n")
                
                print(f"\n✅ SUCCESS! Updated {filename}")
                print(f"   📊 Total recipients: {len(final_recipients)}")
                print(f"   🔄 Replaced: {len(bad_recipients)} accounts")
                print(f"   💾 Backup saved: {backup_filename}")
                
            else:
                print(f"❌ Could only find {len(replacements)} replacement accounts")
                print(f"   Need {len(bad_recipients)} replacements")
        
    else:
        print(f"\n🎉 All accounts are valid! No replacements needed.")
    
    return len(bad_recipients) == 0

if __name__ == "__main__":
    validate_and_fix_recipients()