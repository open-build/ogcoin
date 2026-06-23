# OGCoin - Open Build Project

A modern cryptocurrency project built with open-source principles and powered by community innovation.

## 🌐 Live Site

Visit the live site at: [https://www.opengreencoin.com/](https://www.opengreencoin.com/)

## 🚀 Built with ForgeWeb

This site is built using ForgeWeb, an AI-powered static site generator with a local admin interface.

- `ForgeWeb/` is the editable upstream submodule from `Buildly-Marketplace/ForgeWeb`.
- `ForgeWeb-0.5.0/` is the older vendored copy kept for compatibility while the submodule transition is verified.

### Site Structure

```
ogcoin/
├── index.html              # Main homepage
├── trust.html              # Public verification, risk, and governance page
├── trustline.html          # Wallet-specific OGC trustline onboarding guide
├── governance.html         # Issuer and treasury governance policy
├── impact-policy.html      # Official routed-payment impact policy
├── liquidity-policy.html   # Public OGC/XLM liquidity readiness policy
├── transparency.html       # Public transparency log viewer
├── data/
│   ├── impact-policy.json  # Machine-readable 95/5 routing policy
│   └── transparency-log.json # Machine-readable transparency records
├── roadmap.html            # Development roadmap and progress tracking
├── airdrop.html            # Airdrop pilot and trustline instructions
├── css/
│   └── style.css          # Custom styles (ForgeWeb compatible)
├── js/
│   ├── buildly-head.js    # ForgeWeb utilities
│   └── main.js            # Site-specific functionality
├── .github/
│   └── workflows/
│       └── deploy.yml     # GitHub Pages deployment
├── .well-known/
│   └── stellar.toml       # Stellar SEP-1 issuer metadata
├── ForgeWeb/              # ForgeWeb upstream submodule
└── ForgeWeb-0.5.0/        # Legacy ForgeWeb tooling copy
    ├── admin/             # Local admin interface
    ├── templates/         # HTML templates
    └── ...               # Other ForgeWeb files
```

## 🛠️ Development

### Local Development with ForgeWeb

1. **Start the ForgeWeb Admin Interface**:
   ```bash
   tools/run_forgeweb.sh
   ```

2. **Open Admin Interface**:
   - Navigate to `http://localhost:8000/admin/`
   - Use the interface to edit content and manage the site

3. **Preview Changes**:
   - The same server previews the site at `http://localhost:8000/`
   - The helper script sets `WEBSITE_ROOT=..` so ForgeWeb edits the repo root site files

### Local OGCoin Console

Run the local operator console for legitimacy checks, recipient validation, home-domain XDR generation, and campaign copy:

```bash
python3 tools/ogcoin_console.py
```

Open `http://localhost:8787/`. The console is local-only and does not ask for secret keys or submit transactions.

For a one-shot automation-friendly status report:

```bash
python3 tools/ogcoin_console.py --check
```

### Next-Step Operations

Use the non-custodial next-step helper to prepare trustline campaigns, wallet designation commands, and tiny liquidity readiness checks:

```bash
python3 tools/create_role_wallets.py
python3 tools/ogcoin_next_steps.py status
python3 tools/ogcoin_next_steps.py trustline-campaign --target 25
python3 tools/ogcoin_next_steps.py wallet-designation --treasury G... --grant G... --liquidity G...
python3 tools/ogcoin_next_steps.py liquidity-checklist --online
```

The helpers print reviewable commands only. They do not fund accounts, sign transactions, or submit anything to Stellar. `create_role_wallets.py` writes public addresses to Markdown and private seeds to a gitignored local file for immediate secure custody. See `devdocs/NEXT_STEPS_RUNBOOK.md`.

Build a reviewable official routed payment using OpenGreenCoin Impact Policy v0.1:

```bash
python3 tools/create_impact_payment_xdr.py \
  --source G...PAYER \
  --recipient G...RECIPIENT \
  --gross-amount 100 \
  --flow-type official_marketplace \
  --reference order-123
```

The helper creates an unsigned Stellar transaction with `95%` to the recipient and `5%` to the Open Source Impact Treasury. Direct peer-to-peer transfers are unaffected. It also writes a public-safe reconciliation manifest beside the XDR.

To run the full next-step command set and write a Markdown outcome report:

```bash
python3 tools/run_next_steps_report.py
```

### Transparency Log Updates

Validate the public transparency JSON before a site push:

```bash
python3 tools/transparency_log.py validate
```

Append a reviewed public record with a dry run first:

```bash
python3 tools/transparency_log.py add \
  --id 2026-05-22-example-record \
  --date 2026-05-22 \
  --category policy \
  --status published \
  --title "Example record" \
  --summary "Short public summary with no private recipient or payroll data." \
  --link https://www.opengreencoin.com/transparency.html \
  --dry-run
```

Remove `--dry-run` only after the record has been reviewed. The helper edits `data/transparency-log.json`; it never signs transactions, submits XDR, or reads secret keys.

For wallet role approvals, use the worksheet in `devdocs/WALLET_DESIGNATION_WORKSHEET.md`, then publish the public address with:

```bash
TREASURY_PUBLIC_KEY=G...PUBLIC_ACCOUNT

python3 tools/transparency_log.py designate-account \
  --role treasury \
  --address "$TREASURY_PUBLIC_KEY" \
  --date 2026-05-22 \
  --policy "Cold or low-frequency account for approved OGCoin treasury activity; no routine airdrops, payroll, or liquidity operations." \
  --summary "Designated the public treasury wallet for approved OGCoin reserve and program funding activity." \
  --dry-run
```

### Manual Development

If you prefer to edit files directly:

1. **Edit HTML**: Modify `index.html` for content changes
2. **Edit Styles**: Update `css/style.css` for styling changes  
3. **Edit JavaScript**: Modify `js/main.js` for functionality changes

## 🎨 Customization

### Colors

The site uses ForgeWeb-compatible color variables:

- Primary: `#1b5fa3` (Blue)
- Secondary: `#144a84` (Dark Blue)
- Accent: `#f9943b` (Orange)

Update these in `css/style.css` under the `:root` section.

### Content

- **Hero Section**: Edit the main headline and description in `index.html`
- **About Section**: Update project information and features
- **Features**: Modify the three feature cards
- **Contact**: Update social links and contact information
- **Legitimacy Plan**: See `devdocs/LEGITIMACY_AND_TRADING_PLAN.md`

### ForgeWeb Integration

This site is fully compatible with ForgeWeb's:

- Template system (templates are in `ForgeWeb/templates/`)
- Branding system (colors, fonts, etc.)
- Admin interface for content management
- AI-powered content generation (if enabled)

## 🚀 Deployment

The site automatically deploys to GitHub Pages when you push to the `main` branch.

### Stellar Metadata

The public SEP-1 file is in `.well-known/stellar.toml`. The issuer account has `home_domain=www.opengreencoin.com` set on-chain as of ledger `62686761` with transaction `8b17b271d53bd8f9df817648acd3aa80169005d0be9a032bcbe7467c06f3eb01`.

If the domain ever needs to change, generate a fresh mainnet `set_options` transaction from the issuer account:

```bash
python tools/create_home_domain_xdr.py \
  --issuer GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57 \
  --home-domain www.opengreencoin.com
```

Sign the generated XDR with the issuer account in Stellar Lab or your wallet, then submit it. Never commit or share issuer secret keys.

To harden issuer signer policy, first choose approved public signer accounts, then build an unsigned signer/threshold XDR:

```bash
SIGNER_A=G...PUBLIC_SIGNER_ONE
SIGNER_B=G...PUBLIC_SIGNER_TWO

python tools/create_issuer_signer_xdr.py \
  --signer "$SIGNER_A:1" \
  --signer "$SIGNER_B:1" \
  --master-weight 1 \
  --low-threshold 1 \
  --med-threshold 2 \
  --high-threshold 2
```

See `devdocs/BLOCKER_REMOVAL_PLAN.md` before signing. This helper never handles secret keys.

### Manual Deployment

If you need to deploy manually:

1. Ensure GitHub Pages is enabled in repository settings
2. Set source to "GitHub Actions"
3. Push changes to trigger the workflow

## 📝 Features

- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Smooth Animations**: CSS transitions and JavaScript interactions
- **SEO Optimized**: Meta tags, Open Graph, and structured data ready
- **Accessibility**: WCAG compliant with proper focus states
- **Performance**: Optimized CSS and JavaScript with minimal dependencies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📄 License

This project is open source. See the LICENSE file for details.

## 🔧 Technical Details

- **Framework**: ForgeWeb compatible
- **CSS**: Tailwind CSS + Custom CSS
- **JavaScript**: Vanilla JS with ForgeWeb utilities
- **Build**: GitHub Actions
- **Hosting**: GitHub Pages

---

Built with ❤️ using [ForgeWeb](https://buildly.io) by the Open Build community.
