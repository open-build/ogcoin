#!/usr/bin/env python3
"""
Deploy OGC on Mainnet - Post Funding
Run this after the mainnet accounts have been funded with XLM.
"""

from stellar_sdk import Keypair, Server, TransactionBuilder, Network, Asset
import json
import time

def deploy_ogc_mainnet():
    print("🚀 OGC MAINNET DEPLOYMENT")
    print("=" * 30)
    
    # Load account details
    try:
        with open("mainnet_accounts.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ mainnet_accounts.json not found. Run mainnet_funding_plan.py first.")
        return
    
    # Extract account information
    issuer_secret = data["accounts"]["issuer"]["secret"]
    distributor_secret = data["accounts"]["distributor"]["secret"] 
    personal_secret = data["accounts"]["personal"]["secret"]
    
    issuer = Keypair.from_secret(issuer_secret)
    distributor = Keypair.from_secret(distributor_secret)
    personal = Keypair.from_secret(personal_secret)
    
    print(f"Issuer: {issuer.public_key}")
    print(f"Distributor: {distributor.public_key}")
    print(f"Personal: {personal.public_key}")
    print()
    
    # Connect to mainnet
    server = Server("https://horizon.stellar.org")
    
    # Check if accounts are funded
    print("🔍 CHECKING ACCOUNT FUNDING:")
    for name, keypair in [("Issuer", issuer), ("Distributor", distributor), ("Personal", personal)]:
        try:
            account_data = server.accounts().account_id(keypair.public_key).call()
            # Find XLM balance
            xlm_balance = None
            for balance in account_data["balances"]:
                if balance["asset_type"] == "native":
                    xlm_balance = balance["balance"]
                    break
            print(f"   ✅ {name}: {xlm_balance} XLM")
        except Exception as e:
            if "404" in str(e):
                print(f"   ❌ {name}: NOT FUNDED")
                print(f"      Please send XLM to: {keypair.public_key}")
                return
            else:
                print(f"   ❌ {name}: Error - {e}")
                return
    
    print()
    print("🏗️  BEGINNING OGC DEPLOYMENT:")
    
    try:
        # Create OGC asset
        ogc_asset = Asset("OGC", issuer.public_key)
        
        # Step 1: Distributor creates trustline
        print("   Step 1: Setting up distributor trustline...")
        distributor_account = server.load_account(distributor.public_key)
        
        trustline_tx = (
            TransactionBuilder(
                source_account=distributor_account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100000
            )
            .append_change_trust_op(asset=ogc_asset, limit="1000000000")
            .set_timeout(300)
            .build()
        )
        trustline_tx.sign(distributor)
        
        response = server.submit_transaction(trustline_tx)
        print(f"   ✅ Distributor trustline: {response['hash'][:20]}...")
        
        # Step 2: Issue 1 billion OGC tokens
        print("   Step 2: Issuing 1 billion OGC tokens...")
        issuer_account = server.load_account(issuer.public_key)
        
        issue_tx = (
            TransactionBuilder(
                source_account=issuer_account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100000
            )
            .append_payment_op(
                destination=distributor.public_key,
                asset=ogc_asset,
                amount="1000000000"
            )
            .set_timeout(300)
            .build()
        )
        issue_tx.sign(issuer)
        
        response = server.submit_transaction(issue_tx)
        print(f"   ✅ 1B OGC tokens issued: {response['hash'][:20]}...")
        
        # Step 3: Personal account trustline
        print("   Step 3: Setting up your personal account...")
        personal_account = server.load_account(personal.public_key)
        
        personal_trustline_tx = (
            TransactionBuilder(
                source_account=personal_account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100000
            )
            .append_change_trust_op(asset=ogc_asset, limit="1000000")
            .set_timeout(300)
            .build()
        )
        personal_trustline_tx.sign(personal)
        
        response = server.submit_transaction(personal_trustline_tx)
        print(f"   ✅ Personal trustline: {response['hash'][:20]}...")
        
        # Step 4: Transfer OGC to personal account
        print("   Step 4: Transferring OGC to your account...")
        distributor_account = server.load_account(distributor.public_key)
        
        transfer_tx = (
            TransactionBuilder(
                source_account=distributor_account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100000
            )
            .append_payment_op(
                destination=personal.public_key,
                asset=ogc_asset,
                amount="10000"
            )
            .set_timeout(300)
            .build()
        )
        transfer_tx.sign(distributor)
        
        response = server.submit_transaction(transfer_tx)
        print(f"   ✅ 10,000 OGC transferred: {response['hash'][:20]}...")
        
        print()
        print("🎉 OGC SUCCESSFULLY DEPLOYED ON MAINNET!")
        print("=" * 45)
        print(f"🪙 Token: OGC")
        print(f"🏭 Issuer: {issuer.public_key}")
        print(f"👤 Your Account: {personal.public_key}")
        print(f"💰 Your Balance: 10,000 OGC")
        print(f"📊 Total Supply: 1,000,000,000 OGC")
        print(f"🌐 Network: Stellar Mainnet")
        print()
        print(f"🔗 View on StellarExpert:")
        print(f"https://stellar.expert/explorer/public/asset/OGC-{issuer.public_key}")
        print()
        print(f"👤 Your account on StellarExpert:")
        print(f"https://stellar.expert/explorer/public/account/{personal.public_key}")
        
        # Save mainnet deployment info
        mainnet_info = {
            "status": "deployed",
            "network": "mainnet",
            "token": "OGC",
            "issuer": issuer.public_key,
            "personal_account": personal.public_key,
            "personal_balance": "10000",
            "total_supply": "1000000000",
            "deployment_time": time.time(),
            "stellar_expert_token": f"https://stellar.expert/explorer/public/asset/OGC-{issuer.public_key}",
            "stellar_expert_account": f"https://stellar.expert/explorer/public/account/{personal.public_key}"
        }
        
        with open("mainnet_deployment_success.json", "w") as f:
            json.dump(mainnet_info, f, indent=2)
        
        # Create .env file for CLI tools
        with open("mainnet.env", "w") as f:
            f.write("# OGC Mainnet Deployment\\n")
            f.write("NETWORK=mainnet\\n")
            f.write(f"ISSUER_PUBLIC={issuer.public_key}\\n")
            f.write(f"ISSUER_SECRET={issuer.secret}\\n")
            f.write(f"DISTRIBUTOR_PUBLIC={distributor.public_key}\\n")
            f.write(f"DISTRIBUTOR_SECRET={distributor.secret}\\n")
            f.write(f"PERSONAL_PUBLIC={personal.public_key}\\n")
            f.write(f"PERSONAL_SECRET={personal.secret}\\n")
            f.write(f"OGC_ASSET_CODE=OGC\\n")
            f.write(f"OGC_ISSUER={issuer.public_key}\\n")
        
        print("💾 Files created:")
        print("   • mainnet_deployment_success.json")
        print("   • mainnet.env (for CLI tools)")
        print()
        print("✅ READY FOR:")
        print("   • Website update to mainnet")
        print("   • CLI tool configuration")
        print("   • OGC payments and transfers")
        print("   • Full mainnet functionality")
        
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    deploy_ogc_mainnet()