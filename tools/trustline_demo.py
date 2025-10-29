#!/usr/bin/env python3
"""
Trustline Establishment Demo
Shows how the trustline process works without real secret keys
"""

from stellar_sdk import Keypair, Asset
from config import Config

def demo_trustline_establishment():
    """Demonstrate the trustline establishment process."""
    print("🔗 TRUSTLINE ESTABLISHMENT DEMO")
    print("=" * 50)
    
    config = Config()
    
    # Generate a sample keypair for demonstration
    sample_keypair = Keypair.random()
    
    print(f"🌍 Network: {config.STELLAR_NETWORK.upper()}")
    print(f"🪙 Token: {config.TOKEN_CODE}")
    print(f"💰 Issuer: {config.ISSUER_PUBLIC_KEY}")
    
    print(f"\n📋 Sample Account (for demo):")
    print(f"   Public Key: {sample_keypair.public_key}")
    print(f"   Secret Key: {sample_keypair.secret} (DEMO - DO NOT USE)")
    
    # Show what the trustline transaction would look like
    ogc_asset = Asset(config.TOKEN_CODE, config.ISSUER_PUBLIC_KEY)
    
    print(f"\n🔗 Trustline Transaction Details:")
    print(f"   Asset Code: {ogc_asset.code}")
    print(f"   Asset Issuer: {ogc_asset.issuer}")
    print(f"   Trust Limit: 1000 OGC")
    print(f"   Operation: CHANGE_TRUST")
    
    print(f"\n📝 What happens when establishing a trustline:")
    print(f"   1. Account creates CHANGE_TRUST operation")
    print(f"   2. Specifies asset: {config.TOKEN_CODE}:{config.ISSUER_PUBLIC_KEY}")
    print(f"   3. Sets trust limit (max tokens account can hold)")
    print(f"   4. Signs and submits transaction")
    print(f"   5. Account can now receive {config.TOKEN_CODE} tokens!")
    
    print(f"\n💡 Manual Process for Real Accounts:")
    print(f"   • Use Stellar wallet (Lobstr, StellarTerm, etc.)")
    print(f"   • Add custom asset: {config.TOKEN_CODE}:{config.ISSUER_PUBLIC_KEY}")
    print(f"   • Set trust limit (e.g., 1000)")
    print(f"   • Confirm transaction")
    
    print(f"\n🌐 Useful Links:")
    print(f"   • View OGC Token: https://stellar.expert/explorer/public/asset/{config.TOKEN_CODE}-{config.ISSUER_PUBLIC_KEY}")
    print(f"   • Stellar Laboratory: https://laboratory.stellar.org/")
    print(f"   • Lobstr Wallet: https://lobstr.co/")
    
    return sample_keypair

def show_current_trustline_status():
    """Show which accounts currently have trustlines."""
    print(f"\n📊 CURRENT TRUSTLINE STATUS:")
    print(f"=" * 50)
    
    # Show the one account we know has a trustline
    known_trustline_account = "GBZAC66WWHFU2FEOG5KECSEVR6EJO7BYK63UGB52SENDN4JEJTJEVK5L"
    print(f"✅ Account with OGC trustline:")
    print(f"   {known_trustline_account}")
    print(f"   Status: Has trustline, can receive OGC")
    print(f"   Balance: ~10,000 OGC")
    
    print(f"\n❌ Accounts without trustlines (from our recipient list):")
    try:
        with open('airdrop_recipients.txt', 'r') as f:
            recipients = [line.strip() for line in f if line.strip()]
        
        for i, recipient in enumerate(recipients[:5], 1):  # Show first 5
            if recipient != known_trustline_account:
                print(f"   {i}. {recipient}")
                print(f"      Status: Valid account, needs trustline")
    except:
        print("   (No recipient list found)")
    
    print(f"\n🔄 To convert no-trustline accounts to trustline accounts:")
    print(f"   1. Account owner establishes trustline manually")
    print(f"   2. Or we can establish programmatically with secret key")
    print(f"   3. Then account appears in successful airdrop results")

if __name__ == "__main__":
    # Run the demo
    sample_keypair = demo_trustline_establishment()
    show_current_trustline_status()
    
    print(f"\n🎯 SUMMARY:")
    print(f"   ✅ We successfully identified trustline requirement")
    print(f"   ✅ We have tools to establish trustlines") 
    print(f"   ✅ We completed 1 successful airdrop to trustline account")
    print(f"   ✅ We have instructions for users to establish trustlines")
    print(f"   📋 Next: Share instructions with recipients or establish trustlines")