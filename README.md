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

The public SEP-1 file is in `.well-known/stellar.toml`. After deployment, sign a mainnet `set_options` transaction from the issuer account to set `home_domain=www.opengreencoin.com`:

```bash
python tools/create_home_domain_xdr.py \
  --issuer GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57 \
  --home-domain www.opengreencoin.com
```

Sign the generated XDR with the issuer account in Stellar Lab or your wallet, then submit it.

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
