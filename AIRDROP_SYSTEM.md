# OGC Airdrop + Open Source Funding Program

## 🎯 Overview

We've created a comprehensive airdrop system that not only distributes OGC tokens but also identifies and supports open source projects for ongoing funding.

## 🌐 Website Integration

### New Pages Created:
- **`airdrop.html`** - Complete airdrop landing page with:
  - Trustline setup instructions
  - Project submission form
  - FAQ section
  - Open source funding incentives

### Main Site Updates:
- Added prominent airdrop banner section
- Updated navigation with airdrop link
- Integrated project funding promises

## 🛠️ Technical Components

### Backend Tools:
1. **`airdrop_handler.py`** - Processes submissions
   - Validates Stellar addresses
   - Checks account existence
   - Verifies OGC trustlines
   - Manages recipient lists
   - Tracks funding candidates

2. **`establish_trustlines.py`** - Trustline management
   - Instructions generation
   - Test account creation
   - Manual trustline setup

3. **`airdrop_distribution.py`** - Token distribution (existing, enhanced)

### Data Files Generated:
- `airdrop_submissions.jsonl` - All submission records
- `funding_candidate_projects.csv` - Projects for funding review
- `airdrop_recipients.txt` - Valid recipients list

## 🪂 How It Works

### For Users:
1. **Visit** `airdrop.html`
2. **Setup** OGC trustline in Stellar wallet
3. **Submit** project information
4. **Receive** free OGC tokens + funding consideration

### For Administrators:
1. **Collect** submissions via `airdrop_handler.py`
2. **Review** projects in `funding_candidate_projects.csv`  
3. **Run** airdrops to validated recipients
4. **Select** projects for ongoing funding

## 💰 Funding Incentive Structure

### What We Offer:
- **Immediate**: 1-3 free OGC tokens per participant
- **Featured**: Project listing on website
- **Ongoing**: 5-15% of treasury allocation for selected projects

### Selection Criteria:
- Active open source project
- Clear community value
- Cryptocurrency funding utility
- Development team engagement

## 🔧 Usage Examples

### Process Demo Submission:
```bash
python3 airdrop_handler.py demo
```

### Generate Reports:
```bash
python3 airdrop_handler.py report
```

### Run Airdrop Distribution:
```bash
python3 airdrop_distribution.py
```

### Check Account Trustlines:
```bash
python3 establish_trustlines.py
```

## 📊 Current Status

### ✅ Completed:
- Website integration with airdrop page
- Complete trustline setup system
- Automated submission processing
- Recipient validation and management
- Project funding candidate tracking
- Working airdrop distribution (tested with 1 successful drop)

### 🎯 Next Steps:
1. **Deploy** website with airdrop page
2. **Share** airdrop link with developers
3. **Process** incoming submissions
4. **Review** projects for funding
5. **Execute** larger airdrop distributions

## 🌟 Impact

This system transforms a simple token airdrop into a **comprehensive open source funding discovery and support mechanism**, creating value for both token distribution and the broader developer community.

### Key Benefits:
- **For Recipients**: Free tokens + funding opportunities
- **For Projects**: Exposure + financial support
- **For OGC**: Community building + ecosystem growth
- **For Open Source**: New funding model demonstration

## 📝 Files Structure

```
tools/
├── airdrop_handler.py              # Submission processing
├── establish_trustlines.py         # Trustline management  
├── airdrop_distribution.py         # Token distribution
├── airdrop_recipients.txt          # Current recipients
├── airdrop_submissions.jsonl       # All submissions
├── funding_candidate_projects.csv  # Projects for review
└── trustline_instructions.txt      # User instructions

website/
├── airdrop.html                    # Main airdrop page
└── index.html                      # Updated with airdrop integration
```

Ready to launch! 🚀