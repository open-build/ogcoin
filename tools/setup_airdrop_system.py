#!/usr/bin/env python3
"""
OGC Airdrop System Setup
Interactive setup script for configuring the Google Form integration
"""

import os
import json

def create_config_file():
    """Create configuration file with user inputs."""
    print("🔧 OGC AIRDROP SYSTEM SETUP")
    print("=" * 50)
    
    config = {}
    
    # Google Sheets URL
    print("\n📊 Google Sheets Configuration:")
    print("1. Create your Google Form following the instructions in google_form_setup.txt")
    print("2. Get your Google Sheets URL from the Responses tab")
    
    sheet_url = input("\nEnter your Google Sheets URL: ").strip()
    if sheet_url:
        config['google_sheet_url'] = sheet_url
    
    # Telegram notifications (optional)  
    print("\n📢 Telegram Notifications (Optional):")
    print("For automated notifications about new submissions and airdrops")
    
    use_telegram = input("Enable Telegram notifications? (y/n): ").lower().startswith('y')
    
    if use_telegram:
        bot_token = input("Enter Telegram Bot Token: ").strip()
        chat_id = input("Enter Telegram Chat ID: ").strip()
        
        if bot_token and chat_id:
            config['telegram_bot_token'] = bot_token
            config['telegram_chat_id'] = chat_id
    
    # Airdrop settings
    print("\n🪂 Airdrop Configuration:")
    auto_airdrop = input("Enable automatic airdrop execution? (y/n): ").lower().startswith('y')
    config['auto_airdrop'] = auto_airdrop
    
    min_amount = input("Minimum airdrop amount (default: 1): ").strip() or "1"
    max_amount = input("Maximum airdrop amount (default: 3): ").strip() or "3"
    
    config['airdrop_min'] = min_amount
    config['airdrop_max'] = max_amount
    
    # Save configuration
    with open('airdrop_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n✅ Configuration saved to airdrop_config.json")
    return config

def update_scripts_with_config(config):
    """Update script files with configuration values."""
    
    # Update monitor script
    if os.path.exists('airdrop_monitor.py'):
        with open('airdrop_monitor.py', 'r') as f:
            content = f.read()
        
        # Replace placeholders
        if 'google_sheet_url' in config:
            content = content.replace(
                'GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"',
                f'GOOGLE_SHEET_URL = "{config["google_sheet_url"]}"'
            )
        
        if 'telegram_bot_token' in config:
            content = content.replace(
                'TELEGRAM_BOT_TOKEN = ""',
                f'TELEGRAM_BOT_TOKEN = "{config["telegram_bot_token"]}"'
            )
            
        if 'telegram_chat_id' in config:
            content = content.replace(
                'TELEGRAM_CHAT_ID = ""',
                f'TELEGRAM_CHAT_ID = "{config["telegram_chat_id"]}"'
            )
        
        with open('airdrop_monitor.py', 'w') as f:
            f.write(content)
        
        print("✅ Updated airdrop_monitor.py")
    
    # Update website if needed
    website_path = '../airdrop.html'
    if os.path.exists(website_path):
        # Extract form URL from sheet URL
        if 'google_sheet_url' in config:
            sheet_url = config['google_sheet_url']
            # This would need the actual Google Form URL, not the sheet URL
            print("⚠️  Remember to update the Google Form URL in airdrop.html")
            print("   Look for: const GOOGLE_FORM_URL = 'https://forms.gle/YOUR_FORM_ID_HERE';")

def create_cron_job():
    """Help user set up cron job for automated monitoring."""
    print("\n⏰ AUTOMATED MONITORING SETUP")
    print("=" * 50)
    
    setup_cron = input("Set up automated monitoring with cron? (y/n): ").lower().startswith('y')
    
    if setup_cron:
        current_dir = os.getcwd()
        
        print("\nAdd this line to your crontab (run 'crontab -e'):")
        print(f"# OGC Airdrop Monitor - runs every 15 minutes")
        print(f"*/15 * * * * cd {current_dir} && python3 airdrop_monitor.py full >> airdrop_monitor.log 2>&1")
        print()
        print("Or for testing, run every hour:")
        print(f"0 * * * * cd {current_dir} && python3 airdrop_monitor.py full >> airdrop_monitor.log 2>&1")
        print()
        print("Manual testing commands:")
        print(f"  cd {current_dir}")
        print("  python3 airdrop_monitor.py process    # Process new submissions")
        print("  python3 airdrop_monitor.py airdrop    # Run airdrop")
        print("  python3 airdrop_monitor.py report     # Generate report")

def test_configuration():
    """Test the configuration with demo data."""
    print("\n🧪 TESTING CONFIGURATION")
    print("=" * 50)
    
    test = input("Run test with demo data? (y/n): ").lower().startswith('y')
    
    if test:
        print("\n1. Testing Google Sheets handler...")
        os.system("python3 google_sheets_handler.py demo")
        
        print("\n2. Testing airdrop handler...")
        os.system("python3 airdrop_handler.py demo")
        
        print("\n✅ Test complete! Check the output above for any errors.")

def main():
    """Main setup function."""
    print("Welcome to the OGC Airdrop System setup!")
    print("This will help you configure the Google Form integration.")
    
    # Check if files exist
    required_files = [
        'google_sheets_handler.py',
        'airdrop_handler.py', 
        'airdrop_distribution.py'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"\n❌ Missing required files: {', '.join(missing_files)}")
        print("Please ensure all airdrop system files are in the current directory.")
        return
    
    # Run setup steps
    config = create_config_file()
    update_scripts_with_config(config)
    create_cron_job()
    test_configuration()
    
    print("\n🎉 SETUP COMPLETE!")
    print("=" * 50)
    print("Next steps:")
    print("1. Create your Google Form using google_form_setup.txt")
    print("2. Update airdrop.html with your Google Form URL")
    print("3. Test the system with: python3 airdrop_monitor.py process")
    print("4. Set up cron job for automated monitoring")
    print("5. Share your Google Form link to start collecting submissions!")
    
    print(f"\nConfiguration saved in: {os.getcwd()}/airdrop_config.json")
    print("Monitor logs will be saved in: airdrop_monitor.log")

if __name__ == "__main__":
    main()