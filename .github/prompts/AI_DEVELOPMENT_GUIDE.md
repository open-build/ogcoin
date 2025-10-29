# 🤖 AI Development Guide for OGC Project

> Guidelines for AI assistants working on Open.Build projects with Buildly.io standards

This guide helps AI assistants understand project context, follow development standards, and maintain consistency across development sessions.

## 🎯 Project Context

### What is OGC?
- **OGC (Open Build Coin)**: Cryptocurrency for funding open source projects
- **Platform**: Stellar blockchain network
- **Purpose**: Decentralized funding mechanism for developers
- **Community**: Open.Build ecosystem with Buildly.io partnership

### Current System Status
- ✅ **Mainnet deployed**: OGC token live on Stellar
- ✅ **Airdrop system**: Google Form integration working
- ✅ **Distribution tools**: Automated processing and validation
- ✅ **Website**: Public interface at open-build.github.io/ogcoin

## 🏗️ Architecture Overview

```
OGC System Architecture:
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Submit   │───▶│  Google Forms    │───▶│  CSV Export     │
│   via Website   │    │  Validation      │    │  Processing     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Stellar Network │◀───│ Airdrop Distrib  │◀───│ Python Tools    │
│ OGC Payments    │    │ Rate Limited     │    │ Local Processing│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 Development Checklist

### Before Starting Any Work
- [ ] Read current [DEVELOPMENT_STANDARDS.md](./DEVELOPMENT_STANDARDS.md)
- [ ] Understand project structure in [devdocs/README.md](../devdocs/README.md)
- [ ] Check latest system status in [devdocs/SYSTEM_READY.md](../devdocs/SYSTEM_READY.md)
- [ ] Verify no secrets will be committed (check .gitignore)

### For Each Development Session
- [ ] Reference security standards (no secrets in code)
- [ ] Follow Python style guide (type hints, docstrings, error handling)
- [ ] Include simple tests for new functionality
- [ ] Update documentation for changes
- [ ] Use descriptive commit messages

### Code Quality Standards
- [ ] Functions have clear docstrings
- [ ] Error handling with try/catch
- [ ] Type hints on function parameters
- [ ] Environment variables for configuration
- [ ] User-friendly output with emojis (✅❌🔍💡)

## 🔒 Security Reminders

### ⚠️ NEVER COMMIT
```bash
# Secrets and keys
.env
*_SECRET_KEY*
mainnet_accounts.json
*secret*
*private*

# Generated data with personal info  
airdrop_submissions.jsonl
processed_submissions.txt
*_backup.txt

# Transaction files
*_transactions.txt
multisig_transactions.txt
```

### ✅ ALWAYS USE
```python
# Environment variables for config
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable required")

# Partial address display in logs
print(f"Processing account: {address[:8]}...")

# Secure error handling
except Exception as e:
    print(f"❌ Error: {e}")  # Don't log sensitive data
```

## 🐍 Python Development Patterns

### Standard Module Structure
```python
#!/usr/bin/env python3
"""
Module description.
Clear purpose and usage examples.
"""

import os
import sys
from typing import Optional, Dict, List

# Constants
DEFAULT_AMOUNT = 100
OGC_ISSUER = "GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57"

def main_function(param: str, amount: int = DEFAULT_AMOUNT) -> Optional[Dict]:
    """
    Function description.
    
    Args:
        param: Description of parameter
        amount: Token amount (default: 100)
        
    Returns:
        Result dictionary or None if failed
    """
    try:
        # Implementation here
        result = process_data(param, amount)
        return result
        
    except Exception as e:
        print(f"❌ Error in main_function: {e}")
        return None

if __name__ == "__main__":
    # CLI usage
    main_function()
```

### Error Handling Pattern
```python
def robust_function():
    """Example of proper error handling."""
    try:
        # Stellar network operation
        result = stellar_server.load_account(address)
        return True, "Account loaded successfully"
        
    except Exception as e:
        if "404" in str(e):
            return False, "Account not found"
        else:
            return False, f"Network error: {e}"
```

## 🧪 Testing Approach

### Simple Test Pattern
```python
import unittest
from unittest.mock import patch, Mock

class TestFeature(unittest.TestCase):
    """Test new feature functionality."""
    
    def test_happy_path(self):
        """Test successful operation."""
        result = feature_function("valid_input")
        self.assertTrue(result.success)
    
    def test_error_handling(self):
        """Test error conditions."""
        result = feature_function("invalid_input")
        self.assertFalse(result.success)
    
    @patch('module.external_dependency')
    def test_with_mock(self, mock_dep):
        """Test with mocked external dependency."""
        mock_dep.return_value = "expected_response"
        result = feature_function("input")
        self.assertEqual(result, "expected_result")
```

## 📁 File Organization Rules

### New Files Location
```
# Python tools and scripts
tools/new_feature.py

# Documentation  
devdocs/NEW_FEATURE.md

# Tests
tests/test_new_feature.py

# Configuration examples
.env.example (update if needed)
```

### Naming Conventions
```python
# Files: snake_case
airdrop_distribution.py
google_sheets_handler.py

# Functions: snake_case  
def process_submissions():
def validate_stellar_address():

# Classes: PascalCase
class AirdropManager:
class StellarAccountValidator:

# Constants: UPPER_CASE
DEFAULT_TIMEOUT = 30
OGC_TOKEN_CODE = "OGC"
```

## 🔄 Common Development Tasks

### Adding New Feature
1. **Create feature file** in `tools/`
2. **Add configuration** variables to `.env.example`
3. **Write simple tests** in `tests/`
4. **Update documentation** in `devdocs/`
5. **Test manually** before committing

### Modifying Existing Feature  
1. **Read current code** and understand purpose
2. **Check for tests** and update if needed
3. **Maintain backward compatibility** where possible
4. **Update related documentation**
5. **Test all affected functionality**

### Adding New API Integration
1. **Add API credentials** to `.env.example`
2. **Use environment variables** for configuration
3. **Include error handling** for network issues
4. **Add rate limiting** if needed
5. **Document API usage** in devdocs

## 🚀 Deployment Considerations

### Before Production
- [ ] All secrets in environment variables
- [ ] Error handling for network failures
- [ ] Rate limiting for external APIs
- [ ] Logging without sensitive data
- [ ] Simple tests covering critical paths

### Production Safety
```python
# ✅ Production-safe logging
logging.info(f"Processed {count} submissions successfully")
logging.error(f"Failed to process submission: {error_type}")

# ❌ Production-unsafe logging  
logging.info(f"Using secret key: {secret}")  # Never!
logging.debug(f"Full submission data: {submission}")  # Risky!
```

## 💡 AI Assistant Best Practices

### When Starting Work
1. **Ask about current project state** if unclear
2. **Confirm understanding** of requirements
3. **Check for existing similar functionality**
4. **Plan approach** before coding

### During Development
1. **Follow established patterns** in existing code
2. **Ask for clarification** on complex requirements
3. **Suggest improvements** to existing code when appropriate
4. **Point out potential security issues**

### Before Finishing
1. **Review code** against development standards
2. **Check for secrets** or sensitive data
3. **Verify error handling** is comprehensive
4. **Confirm documentation** is updated

## 🎯 Project-Specific Context

### OGC Token Details
- **Issuer**: `GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57`
- **Code**: `OGC`
- **Network**: Stellar Mainnet (public)
- **Supply**: 1 billion tokens
- **Purpose**: Open source project funding

### Key Integration Points
- **Google Forms**: Submission collection
- **Stellar Network**: Token distribution
- **GitHub Pages**: Website hosting
- **Local Processing**: Python tools

### Common User Workflows
1. **User submits** via Google Form
2. **System validates** submission data
3. **Admin processes** submissions locally
4. **Tokens distributed** via Stellar network
5. **Projects featured** on website

---

## 🆘 Quick Reference

### Emergency Contacts
- **Project Issues**: GitHub Issues
- **Development Questions**: Reference these docs
- **Buildly Standards**: [Buildly.io](https://buildly.io)

### Key Commands
```bash
# Setup
pip install -r requirements.txt
cp .env.example .env

# Process submissions
cd tools/
python3 google_sheets_handler.py process-csv submissions.csv

# Run distribution  
python3 airdrop_distribution.py

# Test system
python3 -m pytest tests/
```

---

**Remember: Security first, simplicity always, documentation is code.**

*Built with ❤️ by Open.Build community in partnership with Buildly.io*