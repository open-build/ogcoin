# Google Form + Sheets Integration Guide

## 🎯 Overview

This system replaces the embedded HTML form with a Google Form that feeds into Google Sheets, making it much easier to manage submissions and run processing scripts locally.

## 📝 Step 1: Create Google Form

### Follow the instructions in `google_form_setup.txt`:

1. **Go to**: https://forms.google.com
2. **Create new form**: "OGC Airdrop + Open Source Project Funding"
3. **Add the 7 questions** as specified in the setup file
4. **Set validation** for Stellar addresses and URLs
5. **Configure settings**:
   - Collect email addresses: Yes
   - Limit to 1 response: Yes
   - Response receipts: Always

### Important Form Settings:
- **Title**: OGC Airdrop + Open Source Project Funding
- **Description**: Use the provided text with trustline instructions
- **Response destination**: Create new spreadsheet

## 📊 Step 2: Configure Google Sheets

1. **Go to Responses tab** in your Google Form
2. **Click "Create Spreadsheet"**
3. **Note the Google Sheets URL** (you'll need this for processing)
4. **Optional**: Set up notifications for new responses

## 🔗 Step 3: Update Website

1. **Get your Google Form link**:
   - In Google Forms, click "Send"
   - Copy the shortened link (forms.gle/...)

2. **Update airdrop.html**:
   ```javascript
   const GOOGLE_FORM_URL = 'https://forms.gle/YOUR_ACTUAL_FORM_ID';
   ```

3. **Deploy updated website** with new form integration

## 🤖 Step 4: Set Up Local Processing

### Install Dependencies:
```bash
pip install requests
```

### Processing Commands:

#### Download and Process Submissions:
```bash
python3 google_sheets_handler.py process 'https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit'
```

#### Process Local CSV File:
```bash
python3 google_sheets_handler.py process-csv submissions.csv
```

#### Test with Demo Data:
```bash
python3 google_sheets_handler.py demo
```

## 📋 Step 5: Regular Management Workflow

### Daily/Weekly Process:
1. **Download latest submissions**:
   ```bash
   python3 google_sheets_handler.py process '[YOUR_SHEET_URL]'
   ```

2. **Review processing results**:
   - ✅ Approved: Ready for airdrop
   - ⏳ Pending: Need trustlines (send instructions)
   - ❌ Rejected: Invalid data (follow up if needed)

3. **Run airdrop for approved recipients**:
   ```bash
   python3 airdrop_distribution.py
   ```

4. **Review funding candidates**:
   - Check `funding_candidate_projects.csv`
   - Select projects for funding support
   - Update website with featured projects

## 📁 File Structure

```
tools/
├── google_sheets_handler.py        # Main processing script
├── google_form_setup.txt          # Form creation instructions
├── airdrop_handler.py              # Core validation logic
├── airdrop_distribution.py         # Token distribution
├── submissions.csv                 # Downloaded from Google Sheets
├── processed_submissions.txt       # Tracking processed addresses
├── airdrop_submissions.jsonl       # All submission records
├── funding_candidate_projects.csv  # Projects for review
└── airdrop_recipients.txt          # Final recipient list
```

## 🔧 Advanced Features

### Custom Processing Rules:
You can modify `google_sheets_handler.py` to add:
- Custom validation rules
- Priority processing for certain projects
- Automatic project categorization
- Integration with other tools

### Monitoring:
- Set up Google Sheets notifications
- Create dashboard for submission stats
- Add automated reporting

### Backup:
- Regular CSV exports from Google Sheets
- Backup processed files
- Version control for recipient lists

## 🚨 Security Considerations

1. **Google Sheets Access**:
   - Use "Anyone with link can view" for public CSV access
   - Or set up Google Sheets API for private access

2. **Data Protection**:
   - Don't commit actual submission data to git
   - Use `.gitignore` for sensitive files
   - Regular backups of important data

3. **Address Validation**:
   - Always validate Stellar addresses
   - Check account existence before sending
   - Verify trustlines are established

## 📊 Analytics & Reporting

The system tracks:
- Submission timestamps
- Validation results
- Processing status
- Project categories
- Success/failure rates

### Generate Reports:
```bash
python3 airdrop_handler.py report
```

## 🎯 Benefits of Google Form Integration

1. **Easy Management**: No backend infrastructure needed
2. **Professional**: Clean, mobile-friendly submission process
3. **Scalable**: Handles unlimited submissions
4. **Trackable**: Built-in analytics and notifications
5. **Reliable**: Google's infrastructure, 99.9% uptime
6. **Flexible**: Easy to modify questions or add new fields

## 🚀 Launch Checklist

- [ ] Google Form created with all questions
- [ ] Form validation rules configured
- [ ] Google Sheets response destination set up  
- [ ] Website updated with correct form URL
- [ ] Processing script tested with demo data
- [ ] Backup procedures established
- [ ] Team trained on processing workflow
- [ ] Form link shared publicly

## 💡 Tips for Success

1. **Test thoroughly** with dummy data before launch
2. **Monitor submissions** regularly for processing
3. **Respond quickly** to approved participants
4. **Follow up** with pending trustline cases
5. **Feature successful projects** to encourage participation
6. **Keep statistics** on conversion rates and project quality

This system transforms the airdrop from a simple token distribution into a comprehensive open source project discovery and funding pipeline! 🌟