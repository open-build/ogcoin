#!/usr/bin/env python3
"""
Check OGC Token Network Status
Shows current configuration and network status
"""

from config import Config
from stellar_manager import StellarManager
import sys

def check_network_status():
    """Check current network configuration and status"""
    print("🔍 OGC Token Network Status")
    print("=" * 40)
    
    config = Config()
    
    print(f"Network: {config.STELLAR_NETWORK.upper()}")
    print(f"Horizon URL: {config.HORIZON_URL}")
    print(f"Network Passphrase: {config.NETWORK_PASSPHRASE[:20]}...")
    print(f"Token Code: {config.TOKEN_CODE}")
    print(f"Total Supply: {config.TOTAL_SUPPLY:,}")
    
    if config.ISSUER_PUBLIC_KEY:
        print(f"\nIssuer: {config.ISSUER_PUBLIC_KEY}")
        
        # Check if we can connect to the network
        try:
            stellar = StellarManager()
            # Try to load the issuer account to verify it exists
            account = stellar.server.load_account(config.ISSUER_PUBLIC_KEY)
            print(f"✅ Issuer account exists and is funded")
            
            # Check for OGC asset
            for balance in account.balances:
                if balance.asset_code == config.TOKEN_CODE:
                    print(f"✅ OGC asset found - Balance: {balance.balance}")
                    break
            else:
                print(f"⚠️  OGC asset not found in issuer account")
                
        except Exception as e:
            print(f"❌ Error connecting to network: {e}")
    else:
        print(f"⚠️  No issuer account configured")
    
    # Network-specific information
    if config.STELLAR_NETWORK == 'testnet':
        print(f"\n🧪 TESTNET MODE")
        print(f"• This is for testing only")
        print(f"• Tokens have no real value")
        print(f"• Free XLM available via Friendbot")
        print(f"• To move to mainnet, run: python deploy_mainnet.py")
    else:
        print(f"\n🌍 MAINNET MODE")  
        print(f"• This is LIVE production network")
        print(f"• Tokens have REAL value")
        print(f"• Real XLM required for transactions")
        print(f"• View on Stellar Expert: https://stellar.expert/explorer/public/account/{config.ISSUER_PUBLIC_KEY}")

if __name__ == "__main__":
    check_network_status()