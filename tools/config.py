"""
Configuration management for OGCoin Stellar tools
Handles environment variables, network settings, and tool configuration
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from stellar_sdk import Network

# Load environment variables
load_dotenv()

class Config:
    """Configuration manager for OGCoin Stellar tools"""
    
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """Load configuration from environment variables"""
        
        # Stellar Network Configuration
        self.STELLAR_NETWORK = os.getenv('STELLAR_NETWORK', 'testnet').lower()
        self.NETWORK_PASSPHRASE = (
            Network.PUBLIC_NETWORK_PASSPHRASE 
            if self.STELLAR_NETWORK == 'public' 
            else Network.TESTNET_NETWORK_PASSPHRASE
        )
        self.HORIZON_URL = (
            'https://horizon.stellar.org'
            if self.STELLAR_NETWORK == 'public'
            else 'https://horizon-testnet.stellar.org'
        )
        
        # Account Configuration
        self.ISSUER_SECRET_KEY = os.getenv('ISSUER_SECRET_KEY')
        self.ISSUER_PUBLIC_KEY = os.getenv('ISSUER_PUBLIC_KEY')
        
        # Token Configuration
        self.TOKEN_CODE = os.getenv('TOKEN_CODE', 'OGC')
        self.TOTAL_SUPPLY = int(os.getenv('TOTAL_SUPPLY', '1000000'))
        
        # Website Integration
        self.WEBSITE_URL = os.getenv('WEBSITE_URL', 'https://open-build.github.io/ogcoin')
        self.WEBSITE_REPORTS_DIR = os.getenv('WEBSITE_REPORTS_DIR', '../reports')
        self.WEBSITE_API_ENDPOINT = os.getenv('WEBSITE_API_ENDPOINT', 'https://open-build.github.io/ogcoin/api')
        
        # Tool Settings
        self.GENERATE_REPORTS = os.getenv('GENERATE_REPORTS', 'true').lower() == 'true'
        self.AUTO_UPDATE_WEBSITE = os.getenv('AUTO_UPDATE_WEBSITE', 'true').lower() == 'true'
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
        
        # Transaction Settings
        self.BASE_FEE = int(os.getenv('BASE_FEE', '100'))  # stroops
        self.TIMEOUT = int(os.getenv('TIMEOUT', '30'))  # seconds
        
        # Batch Processing Settings
        self.BATCH_SIZE = int(os.getenv('BATCH_SIZE', '100'))
        self.RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '0.5'))  # seconds
        
        # Validation Settings
        self.STRICT_VALIDATION = os.getenv('STRICT_VALIDATION', 'true').lower() == 'true'
        self.ALLOW_TESTNET_IN_PRODUCTION = os.getenv('ALLOW_TESTNET_IN_PRODUCTION', 'false').lower() == 'true'
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        errors = []
        warnings = []
        
        # Check required keys
        if not self.ISSUER_SECRET_KEY:
            errors.append("ISSUER_SECRET_KEY is required")
        if not self.ISSUER_PUBLIC_KEY:
            errors.append("ISSUER_PUBLIC_KEY is required")
        
        # Check network configuration
        if self.STELLAR_NETWORK not in ['public', 'testnet']:
            errors.append(f"Invalid STELLAR_NETWORK: {self.STELLAR_NETWORK}")
        
        # Production warnings
        if self.STELLAR_NETWORK == 'testnet' and not self.ALLOW_TESTNET_IN_PRODUCTION:
            warnings.append("Using testnet - ensure this is intentional for production")
        
        # Security warnings
        if self.ISSUER_SECRET_KEY and self.ISSUER_SECRET_KEY.startswith('S') == False:
            errors.append("Invalid ISSUER_SECRET_KEY format")
        
        if self.ISSUER_PUBLIC_KEY and self.ISSUER_PUBLIC_KEY.startswith('G') == False:
            errors.append("Invalid ISSUER_PUBLIC_KEY format")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def get_stellar_config(self) -> Dict[str, str]:
        """Get Stellar-specific configuration"""
        return {
            'network': self.STELLAR_NETWORK,
            'passphrase': self.NETWORK_PASSPHRASE,
            'horizon_url': self.HORIZON_URL,
            'issuer_public': self.ISSUER_PUBLIC_KEY,
            'token_code': self.TOKEN_CODE
        }
    
    def get_website_config(self) -> Dict[str, Any]:
        """Get website integration configuration"""
        return {
            'reports_dir': self.WEBSITE_REPORTS_DIR,
            'api_endpoint': self.WEBSITE_API_ENDPOINT,
            'generate_reports': self.GENERATE_REPORTS,
            'auto_update': self.AUTO_UPDATE_WEBSITE
        }
    
    def get_horizon_url(self) -> str:
        """Get Horizon URL for current network"""
        return self.HORIZON_URL
    
    def get_network_passphrase(self) -> str:
        """Get network passphrase for current network"""
        return self.NETWORK_PASSPHRASE
    
    def get(self, key: str, default=None):
        """Get configuration value by key"""
        key_upper = key.upper()
        return getattr(self, key_upper, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        key_upper = key.upper()
        setattr(self, key_upper, value)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings"""
        return {
            'network': self.STELLAR_NETWORK,
            'horizon_url': self.HORIZON_URL,
            'token_code': self.TOKEN_CODE,
            'total_supply': self.TOTAL_SUPPLY,
            'issuer_address': self.ISSUER_PUBLIC_KEY,
            'issuer_secret': self.ISSUER_SECRET_KEY,
            'website_url': self.WEBSITE_URL,
            'base_fee': self.BASE_FEE,
            'timeout': self.TIMEOUT,
            'batch_size': self.BATCH_SIZE,
            'rate_limit_delay': self.RATE_LIMIT_DELAY
        }
    
    def save(self):
        """Save current configuration to .env file"""
        env_content = []
        
        # Add all current configuration
        for key, value in self.get_all_settings().items():
            if value is not None:
                env_content.append(f"{key.upper()}={value}")
        
        with open('.env', 'w') as f:
            f.write('\n'.join(env_content))
        
        print(f"Configuration saved to .env")
    
    def print_config_summary(self):
        """Print a summary of current configuration"""
        print("🔧 OGCoin Stellar Tools Configuration")
        print("=" * 40)
        print(f"Network: {self.STELLAR_NETWORK.upper()}")
        print(f"Token Code: {self.TOKEN_CODE}")
        print(f"Total Supply: {self.TOTAL_SUPPLY:,}")
        print(f"Issuer: {self.ISSUER_PUBLIC_KEY[:8]}...{self.ISSUER_PUBLIC_KEY[-8:] if self.ISSUER_PUBLIC_KEY else 'Not Set'}")
        print(f"Horizon URL: {self.HORIZON_URL}")
        print(f"Reports: {'Enabled' if self.GENERATE_REPORTS else 'Disabled'}")
        print(f"Auto-Update Website: {'Enabled' if self.AUTO_UPDATE_WEBSITE else 'Disabled'}")
        print()
        
        # Validation
        validation = self.validate_config()
        if validation['valid']:
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration has errors:")
            for error in validation['errors']:
                print(f"  - {error}")
        
        if validation['warnings']:
            print("⚠️  Warnings:")
            for warning in validation['warnings']:
                print(f"  - {warning}")

# Global configuration instance
config = Config()

# Configuration validation function
def validate_environment() -> bool:
    """Validate the current environment configuration"""
    validation = config.validate_config()
    
    if not validation['valid']:
        print("❌ Environment configuration is invalid:")
        for error in validation['errors']:
            print(f"  - {error}")
        return False
    
    if validation['warnings']:
        print("⚠️  Configuration warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    return True

# Environment setup helper
def setup_environment():
    """Setup environment with default .env file"""
    env_template = """# OGCoin Stellar Tools Configuration

# Stellar Network Configuration
STELLAR_NETWORK=testnet
ISSUER_SECRET_KEY=S...  # Your issuer account secret key
ISSUER_PUBLIC_KEY=G...  # Your issuer account public key

# OGC Token Configuration
TOKEN_CODE=OGC
TOTAL_SUPPLY=1000000

# Website Integration
WEBSITE_REPORTS_DIR=../reports
WEBSITE_API_ENDPOINT=https://open-build.github.io/ogcoin/api

# Tool Settings
GENERATE_REPORTS=true
AUTO_UPDATE_WEBSITE=true
LOG_LEVEL=INFO

# Transaction Settings
BASE_FEE=100
TIMEOUT=30

# Batch Processing
BATCH_SIZE=100
RATE_LIMIT_DELAY=0.5

# Validation
STRICT_VALIDATION=true
ALLOW_TESTNET_IN_PRODUCTION=false
"""
    
    env_file = '.env'
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write(env_template)
        print(f"✅ Created {env_file} template")
        print("🔧 Please edit the .env file with your configuration")
        return True
    else:
        print(f"⚠️  {env_file} already exists")
        return False

if __name__ == "__main__":
    # Print configuration summary when run directly
    config.print_config_summary()