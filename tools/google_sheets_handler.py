#!/usr/bin/env python3
"""
Google Sheets Integration for OGC Airdrop Submissions
Reads submissions from Google Sheets and processes them locally
"""

import csv
import json
import os
import requests
from datetime import datetime
from airdrop_handler import (
    validate_stellar_address, 
    check_account_exists, 
    check_ogc_trustline,
    add_to_recipient_list,
    save_submission_record
)

def download_google_sheet_as_csv(sheet_url, output_file='submissions.csv'):
    """
    Download Google Sheet as CSV.
    sheet_url should be in format: https://docs.google.com/spreadsheets/d/SHEET_ID/edit#gid=0
    """
    
    # Convert Google Sheets URL to CSV export URL
    if '/edit' in sheet_url:
        sheet_id = sheet_url.split('/d/')[1].split('/')[0]
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    else:
        print("❌ Invalid Google Sheets URL format")
        return False
    
    try:
        print(f"📥 Downloading submissions from Google Sheets...")
        response = requests.get(csv_url)
        response.raise_for_status()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"✅ Downloaded to {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading sheet: {e}")
        return False

def process_google_sheet_submissions(csv_file='submissions.csv'):
    """Process submissions from downloaded Google Sheet CSV."""
    
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return
    
    print(f"🔄 Processing submissions from {csv_file}")
    print("=" * 60)
    
    # Read and track processed submissions to avoid duplicates
    processed_addresses = set()
    processed_file = 'processed_submissions.txt'
    
    if os.path.exists(processed_file):
        with open(processed_file, 'r') as f:
            processed_addresses = {line.strip() for line in f}
    
    approved_count = 0
    pending_count = 0
    rejected_count = 0
    duplicate_count = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, 1):
                print(f"\n[{row_num}] Processing submission...")
                
                # Extract data (mapped to actual Google Form column names)
                submission_data = {
                    'timestamp': row.get('Timestamp', ''),
                    'stellarAddress': row.get('Your Stellar Address (Public Key)', '').strip(),
                    'projectName': row.get('Open Source Project Name', ''),
                    'projectUrl': row.get('Project Repository URL', ''),
                    'projectDescription': row.get('Project Description', ''),
                    'fundingRequest': row.get('How would OGC funding help your project?', ''),
                    'contactInfo': row.get('Contact Information', ''),
                    'trustlineConfirm': row.get('OGC Trustline Confirmation', '').lower().startswith('yes')
                }
                
                stellar_address = submission_data['stellarAddress']
                project_name = submission_data['projectName']
                
                print(f"   Address: {stellar_address[:8] if stellar_address else 'N/A'}...")
                print(f"   Project: {project_name[:30] if project_name else 'N/A'}...")
                
                # Skip if already processed
                if stellar_address in processed_addresses:
                    print(f"   ⏭️  Already processed, skipping")
                    duplicate_count += 1
                    continue
                
                # Validate submission
                if not stellar_address or not project_name:
                    print(f"   ❌ Missing required fields")
                    rejected_count += 1
                    continue
                
                # Process the submission
                result = process_submission(submission_data)
                
                # Print result
                status_emoji = {
                    'approved': '✅',
                    'pending_trustline': '⏳',
                    'pending_funding': '💰',
                    'rejected': '❌'
                }
                
                emoji = status_emoji.get(result['status'], '❓')
                print(f"   {emoji} {result['status'].upper()}: {result['reason']}")
                
                # Count results
                if result['status'] == 'approved':
                    approved_count += 1
                    # Add to recipient list
                    add_to_recipient_list(stellar_address, project_name)
                elif result['status'] in ['pending_trustline', 'pending_funding']:
                    pending_count += 1
                else:
                    rejected_count += 1
                
                # Save record
                save_submission_record(result)
                
                # Mark as processed
                processed_addresses.add(stellar_address)
                
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")
        return
    
    # Update processed addresses file
    with open(processed_file, 'w') as f:
        for addr in processed_addresses:
            f.write(f"{addr}\n")
    
    # Print summary
    print(f"\n📊 PROCESSING SUMMARY")
    print(f"=" * 60)
    print(f"   ✅ Approved (ready for airdrop): {approved_count}")
    print(f"   ⏳ Pending (need trustlines): {pending_count}")
    print(f"   ❌ Rejected (invalid): {rejected_count}")
    print(f"   ⏭️  Duplicates (skipped): {duplicate_count}")
    print(f"   📋 Total processed: {approved_count + pending_count + rejected_count}")

def process_submission(submission_data):
    """Process a single submission (same logic as airdrop_handler)."""
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

def create_google_form_template():
    """Generate instructions for creating the Google Form."""
    
    template = """
📝 GOOGLE FORM SETUP INSTRUCTIONS
==================================

1. Go to https://forms.google.com
2. Create a new form titled: "OGC Airdrop + Open Source Project Funding"
3. Add these questions:

QUESTION 1: Stellar Address (Required)
- Type: Short answer
- Title: "Your Stellar Address (Public Key)"
- Description: "Must start with 'G' and be 56 characters long"
- Required: Yes
- Validation: Regular expression: ^G[A-Z2-7]{55}$

QUESTION 2: Project Name (Required)
- Type: Short answer  
- Title: "Open Source Project Name"
- Required: Yes

QUESTION 3: Project URL (Required)
- Type: Short answer
- Title: "Project Repository URL"
- Description: "GitHub, GitLab, or other repository link"
- Required: Yes
- Validation: Regular expression: ^https?://.*

QUESTION 4: Project Description (Required)
- Type: Paragraph
- Title: "Project Description"
- Description: "Brief description of your open source project and its goals"
- Required: Yes

QUESTION 5: Funding Request (Required)
- Type: Paragraph
- Title: "How would OGC funding help your project?"
- Description: "Describe how OGC funding would support your project development"
- Required: Yes

QUESTION 6: Contact Info (Optional)
- Type: Short answer
- Title: "Contact Information"
- Description: "Email, Twitter, Discord, etc. (optional)"
- Required: No

QUESTION 7: Trustline Confirmation (Required)
- Type: Multiple choice
- Title: "OGC Trustline Confirmation"
- Description: "I confirm that I have established an OGC trustline in my Stellar wallet"
- Options: "Yes, I have established the OGC trustline" / "No, I need help setting it up"
- Required: Yes

4. Form Settings:
   - Collect email addresses: Yes
   - Limit to 1 response: Yes
   - Response receipts: Always

5. After creating, get the shareable link and the sheet URL

6. Configure the response sheet:
   - Go to Responses tab → Create Spreadsheet
   - Note the Google Sheets URL for our script

FORM DESCRIPTION TEXT:
======================
"Join our OGC airdrop and get your open source project featured for funding support! 

🪙 Get 1-3 free OGC tokens
🚀 Feature your project on our website  
💰 Qualify for ongoing funding (5-15% treasury allocation)

Before submitting, please establish an OGC trustline in your Stellar wallet:
- Asset Code: OGC
- Issuer: GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57
- Trust Limit: 1000 (recommended)

Instructions: https://open-build.github.io/ogcoin/airdrop.html"

AFTER SETUP:
============
1. Share the form link publicly
2. Use the Google Sheets URL with our processing script
3. Run processing script regularly to handle submissions
"""
    
    with open('google_form_setup.txt', 'w') as f:
        f.write(template)
    
    print("📝 Google Form setup instructions saved to google_form_setup.txt")
    return template

def demo_csv_processing():
    """Create a demo CSV and process it."""
    
    demo_csv = """Timestamp,Stellar Address,Project Name,Project URL,Project Description,Funding Request,Contact Info,Trustline Confirmed
2025-10-29 10:00:00,GBZAC66WWHFU2FEOG5KECSEVR6EJO7BYK63UGB52SENDN4JEJTJEVK5L,Demo Project 1,https://github.com/demo/project1,A sample open source project,Would help with development costs,demo1@example.com,Yes
2025-10-29 10:05:00,GDE5AB2VQC5PEAKMC6GSD5D3Z27EQBM4PQF7P7KSIWSGZXZURMD4HN5N,Demo Project 2,https://github.com/demo/project2,Another sample project,Need funding for hosting,demo2@example.com,Yes
2025-10-29 10:10:00,INVALID_ADDRESS,Demo Project 3,https://github.com/demo/project3,Invalid address test,Testing validation,demo3@example.com,Yes"""
    
    with open('demo_submissions.csv', 'w') as f:
        f.write(demo_csv)
    
    print("🧪 Created demo_submissions.csv")
    process_google_sheet_submissions('demo_submissions.csv')

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'setup':
            print(create_google_form_template())
            
        elif command == 'demo':
            demo_csv_processing()
            
        elif command == 'process' and len(sys.argv) > 2:
            sheet_url = sys.argv[2]
            if download_google_sheet_as_csv(sheet_url):
                process_google_sheet_submissions()
            
        elif command == 'process-csv' and len(sys.argv) > 2:
            csv_file = sys.argv[2]
            process_google_sheet_submissions(csv_file)
            
        else:
            print("❌ Invalid command or missing parameters")
    
    else:
        print("🔗 GOOGLE SHEETS AIRDROP PROCESSOR")
        print("=" * 50)
        print("Commands:")
        print("  setup                           - Generate Google Form setup instructions")
        print("  demo                           - Process demo CSV data")
        print("  process [SHEET_URL]            - Download and process Google Sheet")
        print("  process-csv [CSV_FILE]         - Process local CSV file")
        print()
        print("Example:")
        print("  python3 google_sheets_handler.py setup")
        print("  python3 google_sheets_handler.py process 'https://docs.google.com/spreadsheets/d/ABC123/edit'")
        print()
        print("💡 This integrates with Google Forms for easy submission collection")