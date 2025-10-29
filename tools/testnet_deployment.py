#!/usr/bin/env python3
"""
Emergency Testnet Deployment
Deploy OGC on Stellar testnet since mainnet account is locked.
"""

from stellar_sdk import Keypair, Server, Network
import requests

def deploy_ogc_testnet():
    print("🚨 EMERGENCY TESTNET OGC DEPLOYMENT")
    print("=" * 40)
    print("Since your mainnet account is locked by multi-sig,")
    print("let's deploy OGC on testnet for now.")
    print()
    
    # Create new testnet accounts
    issuer_keypair = Keypair.random()
    distributor_keypair = Keypair.random()
    personal_keypair = Keypair.random()
    
    print("🔑 GENERATED TESTNET ACCOUNTS:")
    print(f"ISSUER:")
    print(f"   Public:  {issuer_keypair.public_key}")
    print(f"   Secret:  {issuer_keypair.secret}")
    print()
    print(f"DISTRIBUTOR:")
    print(f"   Public:  {distributor_keypair.public_key}")
    print(f"   Secret:  {distributor_keypair.secret}")
    print()
    print(f"PERSONAL:")
    print(f"   Public:  {personal_keypair.public_key}")
    print(f"   Secret:  {personal_keypair.secret}")
    print()
    
    # Fund accounts using Stellar testnet friendbot
    accounts = [
        ("ISSUER", issuer_keypair.public_key),
        ("DISTRIBUTOR", distributor_keypair.public_key),
        ("PERSONAL", personal_keypair.public_key)
    ]
    
    print("💰 FUNDING ACCOUNTS WITH TESTNET XLM:")
    for name, public_key in accounts:
        try:
            response = requests.get(f"https://friendbot.stellar.org?addr={public_key}")
            if response.status_code == 200:
                print(f"   ✅ {name}: {public_key} funded with 10,000 testnet XLM")
            else:
                print(f"   ❌ Failed to fund {name}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error funding {name}: {e}")
    
    # Save testnet accounts
    with open("testnet_accounts.txt", "w") as f:
        f.write("OGC TESTNET DEPLOYMENT ACCOUNTS\\n")
        f.write("="*35 + "\\n\\n")
        f.write("Network: Stellar Testnet\\n")
        f.write("Purpose: Emergency deployment due to mainnet account lockout\\n\\n")
        
        f.write(f"ISSUER ACCOUNT:\\n")
        f.write(f"Public:  {issuer_keypair.public_key}\\n")
        f.write(f"Secret:  {issuer_keypair.secret}\\n\\n")
        
        f.write(f"DISTRIBUTOR ACCOUNT:\\n")
        f.write(f"Public:  {distributor_keypair.public_key}\\n")
        f.write(f"Secret:  {distributor_keypair.secret}\\n\\n")
        
        f.write(f"PERSONAL ACCOUNT:\\n")
        f.write(f"Public:  {personal_keypair.public_key}\\n")
        f.write(f"Secret:  {personal_keypair.secret}\\n\\n")
        
        f.write("NEXT STEPS:\\n")
        f.write("1. Update config.py to use testnet\\n")
        f.write("2. Run OGC deployment on testnet\\n")
        f.write("3. Test all functionality\\n")
        f.write("4. Migrate to mainnet when account access is restored\\n")
    
    print("💾 Testnet accounts saved to testnet_accounts.txt")
    print()
    print("🎯 ADVANTAGES OF TESTNET DEPLOYMENT:")
    print("   ✅ No real money required")
    print("   ✅ Full OGC functionality")
    print("   ✅ Perfect for testing and demonstration")
    print("   ✅ Can migrate to mainnet later")
    print("   ✅ Website can show testnet status")
    print()
    print("📋 NEXT STEPS:")
    print("   1. I'll update your config to use testnet")
    print("   2. Deploy OGC token on testnet")
    print("   3. Transfer tokens to your personal account")
    print("   4. Update website to show testnet status")
    print("   5. Later: migrate to mainnet when account is resolved")

if __name__ == "__main__":
    deploy_ogc_testnet()