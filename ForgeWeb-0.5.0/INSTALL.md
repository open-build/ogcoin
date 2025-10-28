# ForgeWeb Installation Guide

This guide will walk you through installing and setting up ForgeWeb for local development and deployment to GitHub Pages.

## 📋 Prerequisites

Before installing ForgeWeb, ensure you have:

### Required Software
- **Python 3.8 or higher** - [Download Python](https://python.org/downloads/)
- **Git** - [Install Git](https://git-scm.com/downloads)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

### Optional but Recommended
- **Node.js 16+** - For additional development tools
- **VS Code** - With Python and Git extensions
- **GitHub account** - For deployment to GitHub Pages

### System Requirements
- **CPU**: 1+ cores
- **RAM**: 1GB+ available
- **Storage**: 500MB+ free space
- **Operating System**: Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+)

## 🚀 Quick Installation

### Method 1: Download Release (Recommended)

1. **Download ForgeWeb**
   - Go to [ForgeWeb Releases](https://github.com/buildlyio/forgeweb/releases)
   - Download the latest `forgeweb-v0.5.0.zip`
   - Extract to your desired location

2. **Start ForgeWeb**
   ```bash
   cd forgeweb
   cd admin
   python file-api.py
   ```

3. **Open Admin Interface**
   - Open your browser to `http://localhost:8000/admin/`
   - You should see the ForgeWeb dashboard

### Method 2: Clone from GitHub

1. **Clone Repository**
   ```bash
   git clone https://github.com/buildlyio/forgeweb.git
   cd forgeweb
   ```

2. **Start the Admin Server**
   ```bash
   cd admin
   python file-api.py
   ```

3. **Access ForgeWeb**
   - Navigate to `http://localhost:8000/admin/`

## 🔧 Detailed Setup

### 1. Verify Python Installation

Check your Python version:
```bash
python --version
# or
python3 --version
```

You should see Python 3.8.0 or higher. If not, install Python from [python.org](https://python.org).

### 2. Configure ForgeWeb

#### Site Configuration
Edit `admin/site-config.json` to customize your site:

```json
{
  "site": {
    "name": "Your Website Name",
    "url": "https://yourusername.github.io/your-repo",
    "description": "Your website description",
    "logo": "/media/your-logo.svg",
    "favicon": "/favicon.ico"
  },
  "content": {
    "articlesFolder": "articles/",
    "indexFile": "articles.html",
    "defaultCategory": "General",
    "categories": [
      {"id": "tech", "name": "Technology", "color": "blue-500"},
      {"id": "business", "name": "Business", "color": "green-500"},
      {"id": "design", "name": "Design", "color": "purple-500"}
    ],
    "folders": [
      {"id": "articles/", "name": "articles/", "description": "Main articles"},
      {"id": "blog/", "name": "blog/", "description": "Blog posts"},
      {"id": "", "name": "root folder", "description": "Website root"}
    ]
  },
  "branding": {
    "primaryColor": "#1b5fa3",
    "secondaryColor": "#144a84",
    "accentColor": "#f9943b",
    "darkColor": "#1F2937",
    "lightColor": "#F3F4F6",
    "font": "Inter"
  }
}
```

#### AI Configuration (Optional)
To enable AI features, add your API keys to the admin settings:

1. Open ForgeWeb admin (`http://localhost:8000/admin/`)
2. Go to **Settings** → **AI Configuration**
3. Choose your AI provider:
   - **OpenAI**: Add your OpenAI API key
   - **Anthropic**: Add your Anthropic API key
   - **Local LLM**: Configure local endpoint
   - **Custom**: Add custom API endpoint

### 3. Create Your First Content

#### Create an Article
1. In the admin dashboard, click **Article Editor**
2. Enter a title: "Welcome to My Site"
3. Write your content using the rich text editor
4. Use AI assistance (if configured) for content enhancement
5. Click **Publish** to generate the HTML file

#### Create a Page
1. Click **Page Editor**
2. Choose a page type (Landing, About, Contact, etc.)
3. Fill in the page details
4. Customize the template as needed
5. Save to generate the page

## 🌐 GitHub Pages Deployment

### Setup Repository

1. **Create GitHub Repository**
   ```bash
   # In your ForgeWeb directory
   git init
   git add .
   git commit -m "Initial ForgeWeb setup"
   git branch -M main
   git remote add origin https://github.com/yourusername/your-site.git
   git push -u origin main
   ```

2. **Enable GitHub Pages**
   - Go to your repository on GitHub
   - Click **Settings** → **Pages**
   - Source: **Deploy from a branch**
   - Branch: **main** (or **gh-pages** if using automated deployment)
   - Folder: **/ (root)** or **/docs** (if you organize files in docs folder)

### Automated Deployment (Recommended)

1. **Copy GitHub Actions Workflow**
   ```bash
   mkdir -p .github/workflows
   cp ci/github-pages-deploy.yml .github/workflows/
   ```

2. **Configure Repository Secrets** (if using AI features)
   - Go to **Settings** → **Secrets and variables** → **Actions**
   - Add secrets for AI API keys if needed

3. **Push Changes**
   ```bash
   git add .
   git commit -m "Add GitHub Actions deployment"
   git push
   ```

Your site will be automatically deployed to `https://yourusername.github.io/repository-name/`

### Manual Deployment

1. **Generate Site Content**
   - Create articles and pages in ForgeWeb admin
   - Ensure all content is published

2. **Commit and Push**
   ```bash
   git add .
   git commit -m "Update site content"
   git push
   ```

3. **Verify Deployment**
   - Visit your GitHub Pages URL
   - Check that content appears correctly

## 🐳 Docker Installation (Alternative)

For containerized deployment:

### Using Docker

1. **Pull ForgeWeb Image**
   ```bash
   docker pull ghcr.io/buildlyio/forgeweb:latest
   ```

2. **Run Container**
   ```bash
   docker run -d \
     --name forgeweb \
     -p 8000:8000 \
     -v $(pwd)/content:/app/content \
     ghcr.io/buildlyio/forgeweb:latest
   ```

3. **Access Admin**
   - Open `http://localhost:8000/admin/`

### Using Docker Compose

1. **Copy docker-compose.yml**
   ```bash
   cp ops/docker-compose.yml .
   ```

2. **Start Services**
   ```bash
   docker-compose up -d
   ```

## 🛠️ Development Setup

For ForgeWeb development and customization:

### Install Development Dependencies

```bash
# Install Python development dependencies
pip install -r admin/requirements-dev.txt

# Install Node.js dependencies (for build tools)
npm install -g tailwindcss
```

### File Structure Overview

```
ForgeWeb/
├── admin/                 # Admin interface
│   ├── index.html        # Dashboard
│   ├── editor.html       # Article editor
│   ├── page-editor.html  # Page editor
│   ├── settings.html     # Configuration
│   ├── file-api.py       # Local server
│   ├── site-config.json  # Site configuration
│   ├── css/              # Admin styles
│   └── js/               # Admin functionality
├── articles/             # Generated articles (created automatically)
├── assets/              # Site assets (logo, screenshots)
├── ops/                 # Docker and deployment files
├── ci/                  # GitHub Actions workflows
├── BUILDLY.yaml         # Buildly metadata
├── README.md            # Project overview
├── INSTALL.md           # This file
└── LICENSE.md           # License information
```

### Customizing Templates

1. **Article Template**: Modify `admin/js/file-manager.js` → `generateArticleFromTemplate()`
2. **Page Templates**: Edit templates in the page editor
3. **Styling**: Customize Tailwind CSS classes or add custom CSS
4. **Branding**: Update `admin/site-config.json` branding section

## 📱 Mobile Development

ForgeWeb admin works on mobile devices:

- **Responsive Design**: Automatically adapts to screen size
- **Touch-Friendly**: Optimized for touch interactions
- **Offline Capable**: Works without internet connection for local editing

## ⚡ Performance Optimization

### Optimize Images
```bash
# Use optimized images for better performance
# Recommended: WebP format, compressed images
# Tools: ImageOptim (Mac), TinyPNG (Web), Squoosh (Web)
```

### Minimize CSS/JS
ForgeWeb uses CDN-hosted libraries for optimal performance:
- Tailwind CSS via CDN
- Minimal custom JavaScript
- Optimized for fast loading

## 🔍 Troubleshooting

### Common Issues

**Python not found**
```bash
# On Windows, try:
py --version
# or install from Microsoft Store

# On macOS with Homebrew:
brew install python@3.9

# On Linux:
sudo apt update && sudo apt install python3 python3-pip
```

**Port 8000 already in use**
```bash
# Check what's using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
python file-api.py --port 8001
```

**Permission denied errors**
```bash
# On macOS/Linux, you might need:
chmod +x admin/file-api.py
# or
python3 admin/file-api.py
```

**GitHub Pages not updating**
- Check GitHub Actions tab for deployment status
- Verify GitHub Pages settings point to correct branch
- Clear browser cache and try again
- Check repository permissions and GitHub Pages quota

### Getting Help

1. **Check Documentation**: [docs.buildly.io/forgeweb](https://docs.buildly.io/forgeweb)
2. **Community Support**: [GitHub Discussions](https://github.com/buildlyio/forgeweb/discussions)
3. **Report Bugs**: [GitHub Issues](https://github.com/buildlyio/forgeweb/issues)
4. **Priority Support**: Available with Buildly Labs subscription

## 🚀 Next Steps

After installation:

1. **Explore the Admin Interface**
   - Try creating different types of content
   - Experiment with AI assistance features
   - Customize your site configuration

2. **Create Your Content**
   - Write your first article
   - Create essential pages (About, Contact)
   - Set up your navigation structure

3. **Deploy to GitHub Pages**
   - Push your content to GitHub
   - Configure automated deployment
   - Test your live site

4. **Optimize and Customize**
   - Add your branding and colors
   - Customize templates
   - Set up analytics

## 📚 Additional Resources

- **[User Guide](docs/USER_GUIDE.md)**: Complete feature documentation
- **[API Reference](docs/API.md)**: For custom integrations
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Advanced hosting options
- **[Contributing](CONTRIBUTING.md)**: How to contribute to ForgeWeb
- **[Changelog](CHANGELOG.md)**: Version history and updates

---

**Need help?** Join the [Buildly community](https://github.com/buildlyio/forgeweb/discussions) or get [priority support](https://collab.buildly.io/marketplace) for faster assistance!