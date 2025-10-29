# 🏗️ OGC Development Standards

> Buildly.io standards for Open.Build projects

These standards ensure consistent, maintainable, and secure development across all OGC project contributions.

## 🎯 Core Principles

### 1. **Security First**
- ✅ Never commit secrets, private keys, or sensitive data
- ✅ Use environment variables for all configuration
- ✅ Provide `.env.example` files with documentation
- ✅ All secrets must be in `.gitignore`

### 2. **Simple & Maintainable**
- ✅ Write clear, readable code over clever code
- ✅ Use descriptive variable and function names
- ✅ Keep functions small and focused
- ✅ Prefer composition over inheritance

### 3. **Test-Driven Development**
- ✅ Write simple, low-maintenance tests
- ✅ Test critical paths and edge cases
- ✅ Use descriptive test names
- ✅ Keep tests fast and independent

## 📁 Project Structure

```
project/
├── devdocs/              # Developer documentation
│   ├── README.md         # Documentation index
│   └── *.md             # Technical docs
├── .github/
│   └── prompts/         # Development standards & AI prompts
├── tools/               # Python utilities
├── tests/               # Test files
├── .env.example         # Environment template
├── .gitignore          # Security and cleanup
├── requirements.txt     # Dependencies
└── README.md           # Public documentation
```

## 🐍 Python Style Guide

### Code Formatting
```python
#!/usr/bin/env python3
"""
Module docstring describing purpose.
Clear, concise description of what this module does.
"""

import os
import sys
from typing import Optional, Dict, List

# Constants in UPPER_CASE
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://api.example.com"

def process_data(input_data: List[Dict], timeout: int = DEFAULT_TIMEOUT) -> Optional[Dict]:
    """
    Process input data and return results.
    
    Args:
        input_data: List of dictionaries to process
        timeout: Request timeout in seconds
        
    Returns:
        Processed data dictionary or None if failed
        
    Raises:
        ValueError: If input_data is empty
        TimeoutError: If processing exceeds timeout
    """
    if not input_data:
        raise ValueError("Input data cannot be empty")
    
    try:
        # Clear, descriptive variable names
        processed_results = []
        
        for item in input_data:
            result = _process_single_item(item)
            if result:
                processed_results.append(result)
        
        return {
            'results': processed_results,
            'count': len(processed_results),
            'timestamp': time.time()
        }
        
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        return None

def _process_single_item(item: Dict) -> Optional[Dict]:
    """Private helper function for processing individual items."""
    # Implementation here
    pass
```

### Key Standards
- ✅ Use type hints for function parameters and returns
- ✅ Write comprehensive docstrings
- ✅ Use descriptive variable names (`user_data` not `ud`)
- ✅ Handle errors gracefully with try/except
- ✅ Use emoji in user-facing output (✅❌🔍💡)
- ✅ Private functions start with underscore `_private_function()`

## 🌍 Environment Configuration

### .env.example Template
```bash
#!/usr/bin/env bash
# OGC Environment Configuration
# Copy this file to .env and fill in your values

# =============================================================================
# STELLAR NETWORK CONFIGURATION
# =============================================================================
# Network: 'testnet' for development, 'public' for production
STELLAR_NETWORK=testnet

# Horizon API URLs
TESTNET_HORIZON_URL=https://horizon-testnet.stellar.org
MAINNET_HORIZON_URL=https://horizon.stellar.org

# =============================================================================  
# OGC TOKEN CONFIGURATION
# =============================================================================
TOKEN_CODE=OGC
TOTAL_SUPPLY=1000000000

# Token issuer account (public key only)
ISSUER_PUBLIC_KEY=your_issuer_public_key_here

# =============================================================================
# SECRETS (DO NOT COMMIT - USE SECURE STORAGE)
# =============================================================================
# Distribution account secret key
DISTRIBUTOR_SECRET_KEY=your_secret_key_here

# Optional: Telegram notifications
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# =============================================================================
# WEBSITE CONFIGURATION
# =============================================================================
WEBSITE_URL=https://open-build.github.io/ogcoin
GOOGLE_FORM_URL=https://forms.gle/your_form_id

# =============================================================================
# DEVELOPMENT SETTINGS
# =============================================================================
DEBUG=true
LOG_LEVEL=INFO
ENABLE_TESTING=true
```

### Configuration Loading
```python
import os
from typing import Optional

class Config:
    """Application configuration loaded from environment variables."""
    
    def __init__(self):
        # Network configuration
        self.STELLAR_NETWORK = os.getenv('STELLAR_NETWORK', 'testnet')
        self.TOKEN_CODE = os.getenv('TOKEN_CODE', 'OGC')
        
        # Validate required settings
        self._validate_config()
    
    def _validate_config(self):
        """Validate that required configuration is present."""
        required_vars = ['ISSUER_PUBLIC_KEY', 'DISTRIBUTOR_SECRET_KEY']
        
        for var in required_vars:
            if not os.getenv(var):
                raise ValueError(f"Required environment variable {var} is not set")
    
    @property
    def is_mainnet(self) -> bool:
        """Check if running on mainnet."""
        return self.STELLAR_NETWORK == 'public'
```

## 🧪 Testing Standards

### Test Structure
```python
#!/usr/bin/env python3
"""
Tests for airdrop distribution functionality.
Simple, focused tests that validate core functionality.
"""

import unittest
from unittest.mock import Mock, patch
from tools.airdrop_distribution import distribute_tokens, validate_address

class TestAirdropDistribution(unittest.TestCase):
    """Test airdrop distribution functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_address = "GBZAC66WWHFU2FEOG5KECSEVR6EJO7BYK63UGB52SENDN4JEJTJEVK5L"
        self.invalid_address = "INVALID_ADDRESS"
    
    def test_validate_address_success(self):
        """Test that valid Stellar addresses pass validation."""
        is_valid, message = validate_address(self.valid_address)
        
        self.assertTrue(is_valid)
        self.assertEqual(message, "Valid address")
    
    def test_validate_address_failure(self):
        """Test that invalid addresses fail validation."""
        is_valid, message = validate_address(self.invalid_address)
        
        self.assertFalse(is_valid)
        self.assertIn("Invalid", message)
    
    @patch('tools.airdrop_distribution.stellar_manager')
    def test_distribute_tokens_success(self, mock_stellar):
        """Test successful token distribution."""
        # Setup mock
        mock_stellar.send_payment.return_value = {'status': 'success', 'hash': 'abc123'}
        
        # Test distribution
        result = distribute_tokens(self.valid_address, 100)
        
        # Verify results
        self.assertTrue(result['success'])
        self.assertEqual(result['amount'], 100)
        mock_stellar.send_payment.assert_called_once()

if __name__ == '__main__':
    unittest.main()
```

### Testing Guidelines
- ✅ One test file per module (`test_module_name.py`)
- ✅ Use descriptive test method names
- ✅ Test one thing per test method
- ✅ Use mocks for external dependencies
- ✅ Include both success and failure test cases
- ✅ Keep tests fast (< 1 second each)

## 📁 File Organization

### Python Modules
```python
# Good: Clear, descriptive naming
airdrop_distribution.py      # Core distribution logic
google_sheets_handler.py     # Google Sheets integration
stellar_manager.py           # Stellar blockchain operations
config.py                    # Configuration management

# Avoid: Unclear abbreviations
airdrop_dist.py             # Too abbreviated
gs_handler.py               # Unclear abbreviation
```

### Documentation
```
devdocs/
├── README.md               # Documentation index
├── SYSTEM_OVERVIEW.md      # Architecture overview
├── API_REFERENCE.md        # API documentation
└── DEPLOYMENT.md           # Deployment procedures
```

## 🔒 Security Standards

### Environment Variables
```python
# ✅ Good: Environment variables with defaults
SECRET_KEY = os.getenv('SECRET_KEY', '')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

# ❌ Bad: Hardcoded secrets
SECRET_KEY = "hardcoded_secret_here"  # Never do this!
```

### Logging
```python
import logging

# ✅ Good: Structured logging without secrets
logging.info(f"Processing submission for account: {account_id[:8]}...")
logging.error(f"Failed to process submission: {error}")

# ❌ Bad: Logging sensitive data
logging.info(f"Using secret key: {secret_key}")  # Never log secrets!
```

## 🚀 Deployment Standards

### Version Control
- ✅ Use semantic versioning (v1.2.3)
- ✅ Tag releases in git
- ✅ Write clear commit messages
- ✅ Use conventional commits format

### Release Process
1. **Update version** in relevant files
2. **Update CHANGELOG.md** with changes
3. **Run full test suite**
4. **Create git tag** for release
5. **Deploy to staging** first
6. **Verify functionality** in staging
7. **Deploy to production**

## 📚 Documentation Standards

### Code Comments
```python
# ✅ Good: Explain why, not what
def calculate_airdrop_amount(account_balance: float) -> float:
    # Use tiered distribution to incentivize larger holders
    if account_balance > 1000:
        return min(account_balance * 0.1, 500)  # Cap at 500 tokens
    return account_balance * 0.05

# ❌ Bad: Obvious comments
def add_numbers(a, b):
    return a + b  # This adds two numbers
```

### README Structure
```markdown
# Project Name

Brief description of what the project does.

## Quick Start
- Installation steps
- Basic usage example

## Features
- List of key features

## Documentation
- Link to detailed docs

## Contributing
- Development setup
- Coding standards
- Pull request process
```

---

## 💡 AI Development Guidelines

When working with AI assistants on this project:

1. **Reference these standards** in every development session
2. **Ask for code reviews** against these guidelines  
3. **Request test coverage** for new functionality
4. **Verify security practices** are followed
5. **Maintain documentation** as code evolves

Remember: **Code is written once but read many times. Optimize for readability and maintainability.**

---

**Buildly.io Standards • Open.Build Community • Version 1.0**