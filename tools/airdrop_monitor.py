#!/usr/bin/env python3
"""
Automated OGC Airdrop Monitor
Runs regularly to process new submissions and execute airdrops
"""

import os
import sys
import json
from datetime import datetime
import subprocess

# Configuration
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"  # Update this
TELEGRAM_BOT_TOKEN = ""  # Optional: for notifications
TELEGRAM_CHAT_ID = ""    # Optional: for notifications

def log_message(message, level="INFO"):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def send_telegram_notification(message):
    """Send notification via Telegram (optional)."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    
    try:
        import requests
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": f"🪂 OGC Airdrop Monitor\n\n{message}",
            "parse_mode": "Markdown"
        }
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        log_message(f"Failed to send Telegram notification: {e}", "WARNING")

def run_command(command, description):
    """Run a command and return success status."""
    try:
        log_message(f"Running: {description}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            log_message(f"Success: {description}")
            return True, result.stdout
        else:
            log_message(f"Failed: {description} - {result.stderr}", "ERROR")
            return False, result.stderr
            
    except Exception as e:
        log_message(f"Exception in {description}: {e}", "ERROR")
        return False, str(e)

def process_new_submissions():
    """Download and process new submissions from Google Sheets."""
    log_message("Processing new submissions...")
    
    if "YOUR_SHEET_ID" in GOOGLE_SHEET_URL:
        log_message("Google Sheet URL not configured", "ERROR")
        return False
    
    # Process submissions
    command = f"python3 google_sheets_handler.py process '{GOOGLE_SHEET_URL}'"
    success, output = run_command(command, "Processing Google Sheets submissions")
    
    if success:
        # Parse output for statistics
        lines = output.split('\n')
        approved = 0
        pending = 0
        rejected = 0
        
        for line in lines:
            if "Approved (ready for airdrop):" in line:
                approved = int(line.split(':')[1].strip())
            elif "Pending (need trustlines):" in line:
                pending = int(line.split(':')[1].strip())
            elif "Rejected (invalid):" in line:
                rejected = int(line.split(':')[1].strip())
        
        log_message(f"Processing complete: {approved} approved, {pending} pending, {rejected} rejected")
        
        # Send notification if there are new approved submissions
        if approved > 0:
            message = f"📊 *New Submissions Processed*\n\n✅ Approved: {approved}\n⏳ Pending: {pending}\n❌ Rejected: {rejected}"
            send_telegram_notification(message)
        
        return approved > 0
    
    return False

def run_airdrop():
    """Execute airdrop for approved recipients."""
    log_message("Checking for approved recipients...")
    
    # Check if there are recipients ready for airdrop
    try:
        with open('airdrop_recipients.txt', 'r') as f:
            recipients = [line.strip() for line in f if line.strip()]
            
        if not recipients:
            log_message("No recipients found for airdrop")
            return False
            
        log_message(f"Found {len(recipients)} recipients for airdrop")
        
        # Run airdrop (with confirmation bypass)
        command = "echo 'yes' | python3 airdrop_distribution.py"
        success, output = run_command(command, "Executing airdrop distribution")
        
        if success:
            # Parse results
            successful = 0
            failed = 0
            
            for line in output.split('\n'):
                if "Successful:" in line:
                    successful = int(line.split(':')[1].strip())
                elif "Failed:" in line:
                    failed = int(line.split(':')[1].strip())
            
            log_message(f"Airdrop complete: {successful} successful, {failed} failed")
            
            # Send notification
            message = f"🪂 *Airdrop Complete*\n\n✅ Successful: {successful}\n❌ Failed: {failed}"
            send_telegram_notification(message)
            
            return successful > 0
        
    except FileNotFoundError:
        log_message("airdrop_recipients.txt not found")
    except Exception as e:
        log_message(f"Error in airdrop execution: {e}", "ERROR")
    
    return False

def generate_daily_report():
    """Generate and send daily activity report."""
    try:
        # Get submission stats
        if os.path.exists('airdrop_submissions.jsonl'):
            with open('airdrop_submissions.jsonl', 'r') as f:
                submissions = [json.loads(line) for line in f]
            
            # Count today's submissions
            today = datetime.now().strftime("%Y-%m-%d")
            today_submissions = [s for s in submissions if s['timestamp'].startswith(today)]
            
        else:
            submissions = []
            today_submissions = []
        
        # Get recipient count
        recipient_count = 0
        if os.path.exists('airdrop_recipients.txt'):
            with open('airdrop_recipients.txt', 'r') as f:
                recipient_count = len([line for line in f if line.strip()])
        
        # Generate report
        report = f"""📊 *Daily OGC Airdrop Report*
        
📅 Date: {datetime.now().strftime("%Y-%m-%d")}

📋 *Submissions*
• Today: {len(today_submissions)}
• Total: {len(submissions)}

🎯 *Recipients*
• Ready for airdrop: {recipient_count}

🚀 *Status*
• System: Running
• Last check: {datetime.now().strftime("%H:%M:%S")}"""
        
        send_telegram_notification(report)
        log_message("Daily report sent")
        
    except Exception as e:
        log_message(f"Error generating daily report: {e}", "ERROR")

def main():
    """Main monitoring function."""
    log_message("OGC Airdrop Monitor Starting")
    
    try:
        # Process new submissions
        has_new_approved = process_new_submissions()
        
        # Run airdrop if there are approved submissions
        if has_new_approved:
            run_airdrop()
        
        # Generate daily report (if it's the first run of the day)
        if datetime.now().hour == 9:  # 9 AM daily report
            generate_daily_report()
            
        log_message("Monitor cycle complete")
        
    except Exception as e:
        log_message(f"Monitor error: {e}", "ERROR")
        send_telegram_notification(f"❌ *Monitor Error*\n\n{str(e)}")

if __name__ == "__main__":
    # Support different modes
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "process":
            process_new_submissions()
        elif mode == "airdrop":
            run_airdrop()
        elif mode == "report":
            generate_daily_report()
        elif mode == "full":
            main()
        else:
            print("Usage: python3 airdrop_monitor.py [process|airdrop|report|full]")
    else:
        # Default: run full monitoring cycle
        main()