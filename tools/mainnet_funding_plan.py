#!/usr/bin/env python3
"""
Mainnet OGC Deployment with Alternative Funding
Generate new accounts and provide multiple funding options since Lobstr is locked.
"""

from stellar_sdk import Keypair, Server
import json

def create_mainnet_deployment_plan():
    print("🌐 MAINNET OGC DEPLOYMENT - ALTERNATIVE FUNDING")
    print("=" * 55)
    print("Since your Lobstr account is locked by multi-signature,")
    print("let's create new accounts and fund them differently.")
    print()
    
    # Generate new mainnet accounts
    issuer = Keypair.random()
    distributor = Keypair.random() 
    personal = Keypair.random()
    
    print("🔑 NEW MAINNET ACCOUNTS GENERATED:")
    print("=" * 38)
    print(f"ISSUER ACCOUNT:")
    print(f"   Public:  {issuer.public_key}")
    print(f"   Secret:  {issuer.secret}")
    print()
    print(f"DISTRIBUTOR ACCOUNT:")
    print(f"   Public:  {distributor.public_key}")
    print(f"   Secret:  {distributor.secret}")
    print()
    print(f"YOUR PERSONAL ACCOUNT:")
    print(f"   Public:  {personal.public_key}")
    print(f"   Secret:  {personal.secret}")
    print()
    
    print("💰 FUNDING OPTIONS FOR MAINNET:")
    print("=" * 35)
    print()
    print("OPTION 1: CRYPTOCURRENCY EXCHANGE")
    print("   🏦 Use Coinbase, Kraken, Binance, etc.")
    print("   • Buy XLM on exchange")
    print("   • Withdraw XLM to each account address")
    print("   • Need: 3 + 3 + 2 = 8 XLM total (~$0.80)")
    print()
    print("OPTION 2: STELLAR WALLET (NOT LOBSTR)")
    print("   📱 Use Solar Wallet, Albedo, or XBULL")
    print("   • Create new wallet")
    print("   • Buy XLM through wallet")
    print("   • Send to generated accounts")
    print()
    print("OPTION 3: P2P PURCHASE")
    print("   👥 Buy XLM from someone directly")
    print("   • LocalBitcoins, P2P platforms")
    print("   • Have them send to accounts")
    print()
    print("OPTION 4: XLM FROM FRIEND/COLLEAGUE")
    print("   🤝 Ask someone with XLM to help")
    print("   • They send 8 XLM to accounts")
    print("   • Pay them back in USD/other crypto")
    print()
    
    # Create deployment script
    deployment_data = {
        "network": "mainnet",
        "accounts": {
            "issuer": {
                "public": issuer.public_key,
                "secret": issuer.secret,
                "funding_needed": "3 XLM"
            },
            "distributor": {
                "public": distributor.public_key,
                "secret": distributor.secret,
                "funding_needed": "3 XLM"
            },
            "personal": {
                "public": personal.public_key,
                "secret": personal.secret,
                "funding_needed": "2 XLM"
            }
        },
        "total_funding_needed": "8 XLM",
        "estimated_cost_usd": "$0.80"
    }
    
    # Save to files
    with open("mainnet_accounts.json", "w") as f:
        json.dump(deployment_data, f, indent=2)
    
    with open("mainnet_funding_instructions.txt", "w") as f:
        f.write("OGC MAINNET DEPLOYMENT - FUNDING INSTRUCTIONS\\n")
        f.write("="*50 + "\\n\\n")
        f.write("ACCOUNTS TO FUND:\\n")
        f.write(f"1. ISSUER: {issuer.public_key} (3 XLM)\\n")
        f.write(f"2. DISTRIBUTOR: {distributor.public_key} (3 XLM)\\n")
        f.write(f"3. PERSONAL: {personal.public_key} (2 XLM)\\n\\n")
        f.write("TOTAL NEEDED: 8 XLM (~$0.80)\\n\\n")
        f.write("FUNDING OPTIONS:\\n")
        f.write("• Coinbase/Kraken: Buy XLM, withdraw to addresses\\n")
        f.write("• Solar Wallet: Alternative to Lobstr\\n")
        f.write("• P2P purchase: Buy from individual\\n")
        f.write("• Friend with XLM: Ask for help\\n\\n")
        f.write("AFTER FUNDING:\\n")
        f.write("• Run: python deploy_mainnet_funded.py\\n")
        f.write("• This will deploy OGC token\\n")
        f.write("• Transfer tokens to your account\\n")
        f.write("• Update website to mainnet\\n")
    
    print("📋 SPECIFIC EXCHANGE INSTRUCTIONS:")
    print("=" * 35)
    print()
    print("COINBASE EXAMPLE:")
    print("1. Login to Coinbase")
    print("2. Buy $1 worth of XLM (gets you ~10 XLM)")
    print("3. Go to 'Send/Receive'")
    print("4. Send 3 XLM to issuer address")
    print("5. Send 3 XLM to distributor address")
    print("6. Send 2 XLM to personal address")
    print()
    print("KRAKEN EXAMPLE:")
    print("1. Login to Kraken")
    print("2. Buy XLM (minimum $10)")
    print("3. Go to 'Funding' > 'Withdraw'")
    print("4. Withdraw XLM to each address")
    print()
    
    print("💾 SAVED FILES:")
    print("   • mainnet_accounts.json - Account details")
    print("   • mainnet_funding_instructions.txt - Step by step")
    print()
    print("🚀 NEXT STEPS:")
    print("1. Choose a funding method above")
    print("2. Fund the three accounts (8 XLM total)")
    print("3. Let me know when funded")
    print("4. I'll deploy OGC to mainnet immediately")
    print()
    print("💡 CHEAPEST OPTION:")
    print("   Buy $1 of XLM on Coinbase = plenty for deployment")

if __name__ == "__main__":
    create_mainnet_deployment_plan()