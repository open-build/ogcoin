# 🚀 OGC Mainnet Deployment Guide

## ⚠️ CRITICAL PREREQUISITES

Before deploying OGC to mainnet, ensure you have:

### 1. **Real XLM (Stellar Lumens)**
- **Minimum Required**: 4-5 XLM 
- **Recommended**: 10+ XLM for safety margin
- **Purpose**: Account creation (2 XLM minimum per account) + transaction fees

### 2. **Security Setup**
- [ ] Secure computer (not shared/public)
- [ ] Updated antivirus software
- [ ] Backup storage ready (hardware wallet, encrypted USB, etc.)
- [ ] Password manager for key storage
- [ ] Understanding that mainnet keys control REAL value

### 3. **Testing Complete**
- [ ] All operations tested on testnet
- [ ] CLI tools working properly
- [ ] Bulk payment system tested
- [ ] Fund distribution system verified

## 🔧 DEPLOYMENT PROCESS

### Step 1: Get XLM
Purchase XLM from exchanges like:
- Coinbase
- Kraken  
- Binance
- StellarTerm DEX

### Step 2: Run Deployment Script
```bash
cd tools
python deploy_mainnet.py
```

The script will:
1. Create or use existing issuer account
2. Create or use existing distribution account  
3. Guide you through funding accounts manually
4. Create OGC asset on mainnet
5. Issue 1,000,000 OGC tokens
6. Generate production .env file

### Step 3: Verify Deployment
After successful deployment, verify on Stellar Expert:
- Check issuer account exists
- Verify 1M OGC tokens issued
- Confirm asset details are correct

### Step 4: Update Website
Update website to reflect mainnet status:
- Change references from "testnet" to "mainnet"
- Update wallet instructions
- Add mainnet asset information

## 🔒 SECURITY BEST PRACTICES

### Immediate Actions After Deployment
1. **Backup Keys**: Store secret keys in multiple secure locations
2. **Test Small Amount**: Send small test transactions first
3. **Document Everything**: Record all account addresses and transaction IDs
4. **Secure .env**: Ensure .env file is in .gitignore and never committed

### Long-term Security
1. **Hardware Wallets**: Consider moving large amounts to hardware wallets
2. **Multi-signature**: Implement multi-sig for additional security
3. **Regular Backups**: Keep multiple encrypted backups
4. **Access Controls**: Limit who has access to production keys

## 🌐 POST-DEPLOYMENT UPDATES

### Website Updates Needed
- [ ] Update asset information to mainnet
- [ ] Change wallet instructions  
- [ ] Update CLI documentation
- [ ] Add mainnet Stellar Expert links
- [ ] Update roadmap status

### Tool Updates
- [ ] Update .env to use STELLAR_NETWORK=public
- [ ] Test all CLI commands on mainnet
- [ ] Verify bulk payment system
- [ ] Test fund distribution

### Community Communication
- [ ] Announce mainnet launch
- [ ] Provide migration instructions
- [ ] Update GitHub documentation
- [ ] Share mainnet asset details

## 🚨 EMERGENCY PROCEDURES

### If Something Goes Wrong
1. **Don't Panic**: Most issues are recoverable
2. **Check Transaction History**: Use Stellar Expert to trace transactions
3. **Verify Account Status**: Ensure accounts aren't locked/frozen
4. **Community Support**: Reach out to Stellar community if needed

### Backup Recovery
If you lose access to keys:
1. Check all backup locations
2. Try password recovery methods
3. Contact exchange if keys are there
4. **Remember**: Lost keys = lost tokens (no recovery possible)

## 📊 MAINNET VS TESTNET DIFFERENCES

| Aspect | Testnet | Mainnet |
|--------|---------|---------|
| **Cost** | Free | Real XLM required |
| **Value** | No real value | Real cryptocurrency |
| **Accounts** | Free via Friendbot | Must fund manually |
| **Reversibility** | Can reset/recreate | Permanent |
| **URL** | horizon-testnet.stellar.org | horizon.stellar.org |
| **Network** | TESTNET_NETWORK_PASSPHRASE | PUBLIC_NETWORK_PASSPHRASE |

## 🎯 SUCCESS CHECKLIST

After deployment, you should have:
- [ ] OGC asset created on mainnet
- [ ] 1,000,000 OGC tokens issued
- [ ] Issuer and distributor accounts funded
- [ ] .env file with mainnet configuration
- [ ] All keys backed up securely
- [ ] Website updated to reflect mainnet status
- [ ] CLI tools working with mainnet
- [ ] Community notified of mainnet launch

## 🔗 USEFUL LINKS

- **Stellar Expert**: https://stellar.expert/explorer/public
- **StellarTerm DEX**: https://stellarterm.com
- **Stellar Account Viewer**: https://accountviewer.stellar.org
- **Stellar Laboratory**: https://laboratory.stellar.org
- **OGC Asset Page**: https://stellar.expert/explorer/public/asset/OGC-[ISSUER_ADDRESS]

---

**⚠️ FINAL WARNING**: Mainnet deployment creates a real cryptocurrency with real value. Ensure you understand the implications and have proper security measures in place before proceeding.