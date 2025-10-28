# Buildly AI Content Manager - Deployment Guide

This admin interface can be deployed to any static website for AI-powered content management.

## Quick Setup

### 1. Copy Admin Files
Copy the entire `/admin/` folder to your website root:
```
your-website/
├── admin/
│   ├── index.html
│   ├── editor.html
│   ├── settings.html
│   ├── social.html
│   ├── site-config.json
│   ├── dev-server.py
│   ├── js/
│   └── css/
├── articles/
├── index.html
└── other-website-files...
```

### 2. Configure for Your Site
Edit `admin/site-config.json`:

```json
{
    "site": {
        "name": "Your Website Name",
        "url": "https://yoursite.com",
        "description": "Your site description",
        "logo": "/path/to/your/logo.svg"
    },
    "content": {
        "articlesFolder": "blog/",        // or "posts/" or "articles/"
        "indexFile": "blog.html",         // or "index.html"
        "defaultCategory": "General",
        "categories": [
            {"id": "Tech", "name": "Technology", "color": "blue-500"},
            {"id": "Business", "name": "Business", "color": "green-500"}
        ],
        "folders": [
            {"id": "blog/", "name": "blog/"},
            {"id": "posts/", "name": "posts/"},
            {"id": "", "name": "root folder"}
        ]
    },
    "branding": {
        "primaryColor": "#your-color",
        "secondaryColor": "#your-secondary", 
        "accentColor": "#your-accent"
    }
}
```

### 3. Start Development Server
```bash
cd your-website
python admin/dev-server.py 8000
```

### 4. Access Admin Interface
- **Admin Dashboard:** http://localhost:8000/admin/
- **Content Editor:** http://localhost:8000/admin/editor.html
- **Settings:** http://localhost:8000/admin/settings.html

## Features

### ✅ Works With Any Static Site
- GitHub Pages
- Netlify
- Vercel
- Custom hosting
- Local development

### ✅ Content Management
- Create new articles with AI assistance
- Edit existing HTML files
- Generate SEO-optimized content
- Auto-generate meta tags and structured data

### ✅ AI Integration
- **Ollama (Local):** Run AI locally with privacy
- **OpenAI:** Use GPT models with API key
- **Google Gemini:** Use Gemini Pro with API key

### ✅ Social Media
- Auto-generate posts for Twitter, LinkedIn, Facebook
- Platform-specific optimization
- Custom hashtag suggestions

### ✅ File Management
- Browse and edit website files
- Save directly to local filesystem
- Smart filename generation from titles

## Customization

### Categories
Add/remove content categories in `site-config.json`:
```json
"categories": [
    {"id": "tutorial", "name": "Tutorials", "color": "purple-500"},
    {"id": "news", "name": "News", "color": "red-500"}
]
```

### Folder Structure
Configure where content gets saved:
```json
"folders": [
    {"id": "content/posts/", "name": "Posts"},
    {"id": "content/pages/", "name": "Pages"}
]
```

### Branding
Match your website's colors:
```json
"branding": {
    "primaryColor": "#1e40af",
    "secondaryColor": "#1e3a8a",
    "accentColor": "#f59e0b",
    "font": "Inter"
}
```

### Social Platforms
Enable/disable platforms:
```json
"social": {
    "platforms": {
        "twitter": {"enabled": true, "characterLimit": 280},
        "linkedin": {"enabled": true, "characterLimit": 3000},
        "facebook": {"enabled": false}
    }
}
```

## GitHub Pages Deployment

### Option 1: Include Admin in Repository
1. Add admin folder to your repo
2. Configure `site-config.json` for your site
3. Push to GitHub
4. Admin available at: `https://yourusername.github.io/yoursite/admin/`

### Option 2: Development Branch
1. Create a `dev` branch with admin tools
2. Use for content creation
3. Generated files get committed to `main` branch

## Production Notes

### Security
- **API Keys:** Stored encrypted in browser localStorage
- **File Access:** Admin only accesses files within website directory
- **CORS:** Configured for localhost development

### Performance
- **Lightweight:** No database required
- **Static:** Works with any static hosting
- **Caching:** Intelligent file caching for better performance

### Compatibility
- **Modern Browsers:** Chrome, Firefox, Safari, Edge
- **Mobile Responsive:** Works on tablets and phones
- **File System:** Requires local development server for file saving

## Troubleshooting

### Files Not Saving
1. Make sure you're using `dev-server.py` instead of `python -m http.server`
2. Check that the admin folder has write permissions
3. Verify the `articlesFolder` path in config

### AI Not Working
1. Check AI provider settings in admin/settings.html
2. For Ollama: ensure it's running on localhost:11434
3. For OpenAI/Gemini: verify API keys are entered

### Styling Issues
1. Update `branding` colors in `site-config.json`
2. Modify `admin/css/admin.css` for advanced customization
3. Check that your site's CSS doesn't conflict

## Support

This admin interface is designed to be:
- **Self-contained:** No external dependencies
- **Portable:** Works with any static site
- **Configurable:** Adapts to your workflow
- **Extensible:** Easy to modify and enhance

For issues or customization help, check the configuration files and console logs for debugging information.