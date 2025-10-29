# 📚 OGC Developer Documentation

> Built in partnership with [Buildly.io](https://buildly.io) for and by [Open.Build](https://open.build)

Welcome to the OGC (Open Build Coin) development documentation. This folder contains all technical documentation for developers working on the OGC ecosystem.

## 📋 Quick Start

1. **Read the setup guide**: [COMPLETE_SYSTEM_OVERVIEW.md](./COMPLETE_SYSTEM_OVERVIEW.md)
2. **Check development standards**: [../.github/prompts/DEVELOPMENT_STANDARDS.md](../.github/prompts/DEVELOPMENT_STANDARDS.md)
3. **Set up your environment**: Copy `.env.example` to `.env` and configure
4. **Run the airdrop system**: Follow [LAUNCH_CHECKLIST.md](./LAUNCH_CHECKLIST.md)

## 📖 Documentation Index

### 🚀 System Overview
- **[COMPLETE_SYSTEM_OVERVIEW.md](./COMPLETE_SYSTEM_OVERVIEW.md)** - Complete system architecture and components
- **[AIRDROP_SYSTEM.md](./AIRDROP_SYSTEM.md)** - Core airdrop distribution system
- **[GOOGLE_FORM_INTEGRATION.md](./GOOGLE_FORM_INTEGRATION.md)** - Google Forms integration guide

### 🎯 Launch & Operations
- **[LAUNCH_CHECKLIST.md](./LAUNCH_CHECKLIST.md)** - Production launch checklist
- **[SYSTEM_READY.md](./SYSTEM_READY.md)** - System status and readiness guide
- **[MAINNET_DEPLOYMENT.md](./MAINNET_DEPLOYMENT.md)** - Mainnet deployment procedures

### 🛠️ Development Standards
- **[../.github/prompts/DEVELOPMENT_STANDARDS.md](../.github/prompts/DEVELOPMENT_STANDARDS.md)** - Coding standards and best practices
- **[../.github/prompts/AI_DEVELOPMENT_GUIDE.md](../.github/prompts/AI_DEVELOPMENT_GUIDE.md)** - AI assistant development guidelines

## 🏗️ Architecture

```
ogcoin/
├── devdocs/              # Developer documentation (this folder)
├── tools/                # Python scripts and utilities
├── css/                  # Website styling
├── js/                   # Frontend JavaScript
├── .github/prompts/      # Development standards and AI prompts
├── airdrop.html          # Airdrop submission page
├── index.html            # Main website
└── README.md             # Public documentation
```

## 🔧 Core Components

### Python Tools (`tools/`)
- **airdrop_distribution.py** - Core token distribution
- **google_sheets_handler.py** - Google Form processing
- **airdrop_monitor.py** - Automated monitoring
- **setup_airdrop_system.py** - Interactive setup

### Web Interface
- **airdrop.html** - User submission form
- **index.html** - Main landing page
- **css/style.css** - Styling

### Configuration
- **.env** - Environment variables (create from .env.example)
- **requirements.txt** - Python dependencies

## 🎯 Development Workflow

1. **Fork and clone** the repository
2. **Set up environment** following development standards
3. **Create feature branch** from main
4. **Follow coding standards** in `.github/prompts/`
5. **Add tests** for new functionality
6. **Update documentation** as needed
7. **Submit pull request**

## 🔐 Security Notes

- Never commit `.env` files or private keys
- All secrets are gitignored automatically
- Follow security guidelines in development standards
- Use environment variables for all configuration

## 🚀 Quick Commands

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env  # Configure your variables

# Run airdrop system
cd tools/
python3 setup_airdrop_system.py

# Process submissions  
python3 google_sheets_handler.py process-csv submissions.csv

# Run distribution
python3 airdrop_distribution.py
```

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/open-build/ogcoin/issues)
- **Discussions**: [GitHub Discussions](https://github.com/open-build/ogcoin/discussions)  
- **Buildly Support**: [Buildly.io](https://buildly.io)
- **Open.Build Community**: [Open.Build](https://open.build)

---

**Built with ❤️ by the Open.Build community in partnership with Buildly.io**