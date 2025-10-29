#!/usr/bin/env python3
"""
OGC Airdrop Distribution
Sends initial OGC tokens to early adopters to bootstrap the ecosystem.
"""

import os
import time
import random
from decimal import Decimal
from stellar_sdk import Keypair, Server, TransactionBuilder, Network, Asset
from config import Config

def load_recipients(file_path):
    """Load recipient addresses from file."""
    recipients = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                address = line.strip()
                if address and address.startswith('G'):
                    recipients.append(address)
        return recipients
    except FileNotFoundError:
        print(f"❌ Recipients file not found: {file_path}")
        return []

def send_airdrop():
    """Send OGC tokens to airdrop recipients with rate limiting."""
    print("🪂 OGC AIRDROP DISTRIBUTION")
    print("=" * 40)
    
    # Load configuration
    config = Config()
    
    # Connect to network
    server = Server(config.HORIZON_URL)
    print(f"🌍 Network: {config.STELLAR_NETWORK.upper()}")
    print(f"🔗 Connected to: {config.HORIZON_URL}")
    
    # Load issuer account
    issuer_keypair = Keypair.from_secret(config.ISSUER_SECRET_KEY)
    print(f"💰 Issuer: {issuer_keypair.public_key}")
    
    # Load recipients
    recipients = load_recipients('airdrop_recipients.txt')
    if not recipients:
        print("❌ No recipients found!")
        return
    
    print(f"👥 Recipients: {len(recipients)}")
    
    # Define OGC asset
    ogc_asset = Asset(config.TOKEN_CODE, issuer_keypair.public_key)
    
    # Airdrop parameters
    min_amount = "1"  # Minimum 1 OGC
    max_amount = "3"  # Maximum 3 OGC
    chunk_size = 5    # Process 5 recipients at a time
    chunk_delay = 10  # Wait 10 seconds between chunks
    tx_delay = 2      # Wait 2 seconds between individual transactions
    
    print(f"🎯 Airdrop Amount: {min_amount}-{max_amount} OGC per recipient")
    print(f"⏱️  Rate Limiting: {chunk_size} tx/chunk, {chunk_delay}s between chunks")
    
    # Calculate chunks
    chunks = [recipients[i:i + chunk_size] for i in range(0, len(recipients), chunk_size)]
    total_time_estimate = len(chunks) * chunk_delay + len(recipients) * tx_delay
    
    # Confirmation
    print(f"\n📋 AIRDROP SUMMARY:")
    print(f"   • Recipients: {len(recipients)}")
    print(f"   • Amount Range: {min_amount}-{max_amount} OGC each")
    print(f"   • Estimated Total: {len(recipients) * 2} OGC (average)")
    print(f"   • Processing Chunks: {len(chunks)} chunks of {chunk_size}")
    print(f"   • Estimated Time: {total_time_estimate//60}m {total_time_estimate%60}s")
    print(f"   • Asset: {config.TOKEN_CODE}")
    
    confirm = input("\n🚀 Proceed with airdrop? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Airdrop cancelled")
        return
    
    print(f"\n🚀 Starting airdrop with rate limiting...")
    
    successful = 0
    failed = 0
    total_processed = 0
    
    for chunk_num, chunk in enumerate(chunks, 1):
        print(f"\n📦 Processing Chunk {chunk_num}/{len(chunks)} ({len(chunk)} recipients)")
        
        for i, recipient in enumerate(chunk, 1):
            total_processed += 1
            try:
                # Random amount between min and max
                amount = str(random.uniform(float(min_amount), float(max_amount)))
                amount = f"{float(amount):.2f}"  # Round to 2 decimal places
                
                print(f"[{total_processed}/{len(recipients)}] 🎁 Sending {amount} OGC to {recipient[:8]}...")
                
                # First check if recipient account exists
                try:
                    recipient_account = server.load_account(recipient)
                    print(f"   ✅ Account exists and is active")
                except Exception as e:
                    print(f"   ⚠️  Account not found or inactive: {str(e)}")
                    failed += 1
                    continue
                
                # Load issuer account for current transaction
                issuer_account = server.load_account(issuer_keypair.public_key)
                
                # Build transaction
                transaction = (
                    TransactionBuilder(
                        source_account=issuer_account,
                        network_passphrase=config.NETWORK_PASSPHRASE,
                        base_fee=100
                    )
                    .append_payment_op(
                        destination=recipient,
                        asset=ogc_asset,
                        amount=amount
                    )
                    .set_timeout(30)
                    .build()
                )
                
                # Sign and submit
                transaction.sign(issuer_keypair)
                response = server.submit_transaction(transaction)
                
                print(f"   ✅ Success! Hash: {response['hash'][:16]}...")
                successful += 1
                
                # Delay between individual transactions
                if i < len(chunk):  # Don't delay after last item in chunk
                    time.sleep(tx_delay)
                
            except Exception as e:
                error_msg = str(e)
                if "no trustline" in error_msg.lower() or "trustline" in error_msg.lower():
                    print(f"   ⚠️  Account needs to establish OGC trustline first: {recipient[:8]}...")
                else:
                    print(f"   ❌ Failed: {error_msg}")
                failed += 1
                continue
        
        # Delay between chunks (except after the last chunk)
        if chunk_num < len(chunks):
            print(f"⏳ Waiting {chunk_delay}s before next chunk to respect rate limits...")
            time.sleep(chunk_delay)
    
    print(f"\n🎉 AIRDROP COMPLETE!")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📊 Success Rate: {(successful/(successful+failed)*100):.1f}%")
    
    if successful > 0:
        estimated_distributed = successful * 2  # Average amount
        print(f"\n🌟 Successfully distributed ~{estimated_distributed} OGC to {successful} early adopters!")
        print(f"💡 This helps bootstrap the OGC ecosystem and creates initial adoption.")
        print(f"🔗 View on StellarExpert: https://stellar.expert/explorer/public/account/{issuer_keypair.public_key}")

if __name__ == "__main__":
    send_airdrop()