#!/usr/bin/env python3
"""
Airdrop Submission Handler
Processes submissions from the website form and manages the recipient list
"""

import json
import csv
import os
from datetime import datetime
from stellar_sdk import Server, Keypair

def validate_stellar_address(address):
    """Validate that a Stellar address is properly formatted."""
    if not address or not isinstance(address, str):
        return False, "Address is required"
    
    if not address.startswith('G'):
        return False, "Stellar address must start with 'G'"
    
    if len(address) != 56:
        return False, "Stellar address must be exactly 56 characters"
    
    try:
        # Try to decode the address to verify it's valid
        Keypair.from_public_key(address)
        return True, "Valid address"
    except Exception as e:
        return False, f"Invalid address format: {str(e)}"

def check_account_exists(address):
    """Check if the Stellar account exists and is active."""
    try:
        server = Server("https://horizon.stellar.org")
        account = server.load_account(address)
        return True, "Account exists and is active"
    except Exception as e:
        if "404" in str(e):
            return False, "Account not found - needs to be funded first"
        return False, f"Error checking account: {str(e)}"

def check_ogc_trustline(address):
    """Check if the account has established an OGC trustline."""
    try:
        server = Server("https://horizon.stellar.org")
        account = server.load_account(address)
        
        # Get account data from server response
        account_data = account.raw_data if hasattr(account, 'raw_data') else account
        balances = account_data.get('balances', [])
        
        # Check balances for OGC trustline
        for balance in balances:
            if (balance.get('asset_code') == 'OGC' and 
                balance.get('asset_issuer') == 'GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57'):
                return True, f"OGC trustline established (limit: {balance.get('limit', 'unlimited')})"
        
        return False, "No OGC trustline found"
    except Exception as e:
        return False, f"Error checking trustline: {str(e)}"

def process_airdrop_submission(submission_data):
    """Process a new airdrop submission."""
    result = {
        'timestamp': datetime.now().isoformat(),
        'status': 'pending',
        'validations': {},
        'submission': submission_data
    }
    
    # Validate Stellar address
    stellar_address = submission_data.get('stellarAddress', '').strip()
    is_valid, msg = validate_stellar_address(stellar_address)
    result['validations']['address_format'] = {'valid': is_valid, 'message': msg}
    
    if not is_valid:
        result['status'] = 'rejected'
        result['reason'] = msg
        return result
    
    # Check if account exists
    exists, msg = check_account_exists(stellar_address)
    result['validations']['account_exists'] = {'valid': exists, 'message': msg}
    
    if not exists:
        result['status'] = 'pending_funding'
        result['reason'] = msg
        return result
    
    # Check OGC trustline
    has_trustline, msg = check_ogc_trustline(stellar_address)
    result['validations']['ogc_trustline'] = {'valid': has_trustline, 'message': msg}
    
    if not has_trustline:
        result['status'] = 'pending_trustline'
        result['reason'] = msg
        return result
    
    # All validations passed
    result['status'] = 'approved'
    result['reason'] = 'Ready for airdrop'
    
    return result

def add_to_recipient_list(stellar_address, project_name):
    """Add approved address to the recipient list."""
    
    # Read existing recipients
    recipients_file = 'airdrop_recipients.txt'
    existing_recipients = set()
    
    if os.path.exists(recipients_file):
        with open(recipients_file, 'r') as f:
            existing_recipients = {line.strip() for line in f if line.strip()}
    
    # Add new recipient if not already present
    if stellar_address not in existing_recipients:
        with open(recipients_file, 'a') as f:
            f.write(f"{stellar_address}\n")
        return True, "Added to recipient list"
    else:
        return False, "Address already in recipient list"

def save_submission_record(submission_result):
    """Save the submission record to a file."""
    submissions_file = 'airdrop_submissions.jsonl'
    
    with open(submissions_file, 'a') as f:
        f.write(json.dumps(submission_result) + '\n')

def save_project_for_funding_review(submission_data):
    """Save project information for funding review."""
    projects_file = 'funding_candidate_projects.csv'
    
    # Check if file exists, create headers if not
    file_exists = os.path.exists(projects_file)
    
    with open(projects_file, 'a', newline='') as f:
        writer = csv.writer(f)
        
        # Write headers if new file
        if not file_exists:
            writer.writerow([
                'timestamp', 'stellar_address', 'project_name', 'project_url', 
                'description', 'funding_request', 'contact_info', 'status'
            ])
        
        # Write project data
        writer.writerow([
            datetime.now().isoformat(),
            submission_data.get('stellarAddress', ''),
            submission_data.get('projectName', ''),
            submission_data.get('projectUrl', ''),
            submission_data.get('projectDescription', ''),
            submission_data.get('fundingRequest', ''),
            submission_data.get('contactInfo', ''),
            'pending_review'
        ])

def generate_submission_report():
    """Generate a report of all submissions."""
    if not os.path.exists('airdrop_submissions.jsonl'):
        print("No submissions found.")
        return
    
    submissions = []
    with open('airdrop_submissions.jsonl', 'r') as f:
        for line in f:
            submissions.append(json.loads(line.strip()))
    
    print(f"\n📊 AIRDROP SUBMISSIONS REPORT")
    print(f"=" * 50)
    print(f"Total submissions: {len(submissions)}")
    
    # Count by status
    status_counts = {}
    for sub in submissions:
        status = sub['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    
    # Show recent submissions
    print(f"\n📋 Recent Submissions:")
    for sub in submissions[-5:]:  # Last 5
        addr = sub['submission'].get('stellarAddress', 'N/A')[:8]
        project = sub['submission'].get('projectName', 'N/A')[:20]
        status = sub['status']
        print(f"  {addr}... | {project:<20} | {status}")

def demo_submission():
    """Demo function to test the submission process."""
    print("🧪 DEMO AIRDROP SUBMISSION PROCESSING")
    print("=" * 50)
    
    # Sample submission data
    demo_data = {
        'stellarAddress': 'GBZAC66WWHFU2FEOG5KECSEVR6EJO7BYK63UGB52SENDN4JEJTJEVK5L',  # Known good address
        'projectName': 'Demo Open Source Project',
        'projectUrl': 'https://github.com/demo/project',
        'projectDescription': 'A sample open source project for testing',
        'fundingRequest': 'Would help fund development and maintenance',
        'contactInfo': 'demo@example.com',
        'trustlineConfirm': True
    }
    
    print("Processing demo submission...")
    result = process_airdrop_submission(demo_data)
    
    print(f"\nResult: {result['status']}")
    print(f"Reason: {result['reason']}")
    
    print(f"\nValidations:")
    for check, details in result['validations'].items():
        status = "✅" if details['valid'] else "❌"
        print(f"  {status} {check}: {details['message']}")
    
    if result['status'] == 'approved':
        added, msg = add_to_recipient_list(demo_data['stellarAddress'], demo_data['projectName'])
        print(f"\nRecipient list: {'✅' if added else '⚠️'} {msg}")
        
        save_project_for_funding_review(demo_data)
        print("✅ Project saved for funding review")
    
    save_submission_record(result)
    print("✅ Submission record saved")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        demo_submission()
    elif len(sys.argv) > 1 and sys.argv[1] == 'report':
        generate_submission_report()
    else:
        print("🎯 AIRDROP SUBMISSION HANDLER")
        print("=" * 50)
        print("Usage:")
        print("  python3 airdrop_handler.py demo    - Run demo submission")
        print("  python3 airdrop_handler.py report  - Generate submissions report")
        print()
        print("💡 This script processes airdrop submissions and:")
        print("  • Validates Stellar addresses")
        print("  • Checks account existence and trustlines")
        print("  • Adds approved addresses to recipient list")
        print("  • Saves project info for funding review")
        print("  • Tracks all submissions for reporting")