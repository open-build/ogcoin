#!/usr/bin/env python3
"""
OGC Airdrop Distribution - DRY RUN
Test the airdrop process without actually sending tokens.
"""

import os
import time
import random
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

def dry_run_airdrop():
    """Simulate the airdrop process without sending actual transactions."""
    print("🧪 OGC AIRDROP - DRY RUN")
    print("=" * 40)
    print("⚠️  This is a simulation - no actual tokens will be sent")
    
    # Load configuration
    config = Config()
    
    print(f"🌍 Network: {config.STELLAR_NETWORK.upper()}")
    print(f"💰 Issuer: {config.ISSUER_PUBLIC_KEY}")
    
    # Load recipients
    recipients = load_recipients('airdrop_recipients.txt')
    if not recipients:
        print("❌ No recipients found!")
        return
    
    print(f"👥 Recipients: {len(recipients)}")
    
    # Airdrop parameters
    min_amount = "1"
    max_amount = "3"
    chunk_size = 5
    chunk_delay = 10
    tx_delay = 2
    
    print(f"🎯 Airdrop Amount: {min_amount}-{max_amount} OGC per recipient")
    print(f"⏱️  Rate Limiting: {chunk_size} tx/chunk, {chunk_delay}s between chunks")
    
    # Calculate chunks
    chunks = [recipients[i:i + chunk_size] for i in range(0, len(recipients), chunk_size)]
    total_time_estimate = len(chunks) * chunk_delay + len(recipients) * tx_delay
    
    print(f"\\n📋 AIRDROP SIMULATION SUMMARY:")
    print(f"   • Recipients: {len(recipients)}")
    print(f"   • Amount Range: {min_amount}-{max_amount} OGC each")
    print(f"   • Estimated Total: {len(recipients) * 2} OGC (average)")
    print(f"   • Processing Chunks: {len(chunks)} chunks of {chunk_size}")
    print(f"   • Estimated Time: {total_time_estimate//60}m {total_time_estimate%60}s")
    
    confirm = input("\\n🧪 Run simulation? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Simulation cancelled")
        return
    
    print(f"\\n🚀 Starting airdrop simulation...")
    
    successful = 0
    total_distributed = 0
    
    for chunk_num, chunk in enumerate(chunks, 1):
        print(f"\\n📦 Simulating Chunk {chunk_num}/{len(chunks)} ({len(chunk)} recipients)")
        
        for i, recipient in enumerate(chunk, 1):
            # Random amount between min and max
            amount = random.uniform(float(min_amount), float(max_amount))
            amount = round(amount, 2)
            
            print(f"[{successful + 1}/{len(recipients)}] 🎁 Would send {amount} OGC to {recipient[:8]}...")
            
            # Simulate successful transaction
            fake_hash = f"{''.join(random.choices('0123456789abcdef', k=16))}"
            print(f"   ✅ Simulated! Hash: {fake_hash}...")
            
            successful += 1
            total_distributed += amount
            
            # Simulate delay between transactions
            if i < len(chunk):
                print(f"   ⏳ Simulated {tx_delay}s delay...")
                time.sleep(0.1)  # Quick simulation delay
        
        # Simulate delay between chunks
        if chunk_num < len(chunks):
            print(f"⏳ Simulated {chunk_delay}s delay between chunks...")
            time.sleep(0.2)  # Quick simulation delay
    
    print(f"\\n🎉 AIRDROP SIMULATION COMPLETE!")
    print(f"   ✅ Would succeed: {successful}")
    print(f"   📊 Success Rate: 100%")
    print(f"   💰 Total OGC: {total_distributed:.2f}")
    print(f"   📈 Average per recipient: {total_distributed/successful:.2f} OGC")
    
    print(f"\\n🌟 Ready to distribute {total_distributed:.2f} OGC to {successful} early adopters!")
    print(f"💡 Run 'python airdrop_distribution.py' to execute the real airdrop.")

if __name__ == "__main__":
    dry_run_airdrop()