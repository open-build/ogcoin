#!/usr/bin/env python3
"""
Switch to testnet and create test accounts with trustlines
"""

import os
from config import Config

def switch_to_testnet():
    """Switch configuration to testnet for testing trustlines."""
    
    # Read current .env
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    # Update network to testnet
    updated_lines = []
    for line in lines:
        if line.startswith('STELLAR_NETWORK='):
            updated_lines.append('STELLAR_NETWORK=testnet\n')
            print("🔄 Switched to testnet")
        else:
            updated_lines.append(line)
    
    # Write updated .env
    with open('.env', 'w') as f:
        f.writelines(updated_lines)
    
    print("✅ Configuration updated to testnet")
    print("💡 Now you can create test accounts with trustlines!")

def switch_to_mainnet():
    """Switch configuration back to mainnet."""
    
    # Read current .env
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    # Update network to mainnet
    updated_lines = []
    for line in lines:
        if line.startswith('STELLAR_NETWORK='):
            updated_lines.append('STELLAR_NETWORK=mainnet\n')
            print("🔄 Switched to mainnet")
        else:
            updated_lines.append(line)
    
    # Write updated .env
    with open('.env', 'w') as f:
        f.writelines(updated_lines)
    
    print("✅ Configuration updated to mainnet")

if __name__ == "__main__":
    config = Config()
    current_network = config.STELLAR_NETWORK
    
    print(f"🌍 Current Network: {current_network.upper()}")
    
    if current_network == 'mainnet':
        print("\n💡 To test trustline establishment safely:")
        print("1. Switch to testnet")
        print("2. Create test accounts with trustlines")
        print("3. Test airdrop functionality")
        print("4. Switch back to mainnet")
        
        choice = input("\nSwitch to testnet for testing? (yes/no): ").strip().lower()
        if choice == 'yes':
            switch_to_testnet()
            print("\n🚀 Now run: python3 establish_trustlines.py")
            print("   Choose option 2 to create test accounts with trustlines")
        
    else:
        print("\n🧪 You're on testnet - perfect for testing!")
        choice = input("Switch back to mainnet? (yes/no): ").strip().lower()
        if choice == 'yes':
            switch_to_mainnet()
            print("🔄 Switched back to mainnet")