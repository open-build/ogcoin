# OGCoin - Open Build Project

A modern cryptocurrency project built with open-source principles and powered by community innovation.

## 🌐 Live Site

Visit the live site at: [https://open-build.github.io/ogcoin/](https://open-build.github.io/ogcoin/)

## 🚀 Built with ForgeWeb

This site is built using ForgeWeb v0.5.0, an AI-powered static site generator with local admin interface. The ForgeWeb tooling is included in the `ForgeWeb-0.5.0/` directory.

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
└── ForgeWeb-0.5.0/        # ForgeWeb tooling (not deployed)
    ├── admin/             # Local admin interface
    ├── templates/         # HTML templates
    └── ...               # Other ForgeWeb files
```

## 🛠️ Development

### Local Development with ForgeWeb

1. **Start the ForgeWeb Admin Interface**:
   ```bash
   cd ForgeWeb-0.5.0/admin
   python file-api.py
   ```

2. **Open Admin Interface**:
   - Navigate to `http://localhost:8000/admin/`
   - Use the interface to edit content and manage the site

3. **Preview Changes**:
   - Open `index.html` in your browser to preview changes
   - Or use a local server like `python -m http.server 8080`

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

### ForgeWeb Integration

This site is fully compatible with ForgeWeb's:

- Template system (templates are in `ForgeWeb-0.5.0/templates/`)
- Branding system (colors, fonts, etc.)
- Admin interface for content management
- AI-powered content generation (if enabled)

## 🚀 Deployment

The site automatically deploys to GitHub Pages when you push to the `main` branch.

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

- **Framework**: ForgeWeb v0.5.0 compatible
- **CSS**: Tailwind CSS + Custom CSS
- **JavaScript**: Vanilla JS with ForgeWeb utilities
- **Build**: GitHub Actions
- **Hosting**: GitHub Pages

---

Built with ❤️ using [ForgeWeb](https://buildly.io) by the Open Build community.