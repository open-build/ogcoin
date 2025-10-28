# ForgeWeb Site Generator Templates

This directory contains HTML templates for generating different types of pages and sites with ForgeWeb.

## Template Variables

All templates use a simple variable replacement system with `{{VARIABLE_NAME}}` placeholders:

### Site-wide Variables
- `{{SITE_NAME}}` - Site title/name
- `{{SITE_DESCRIPTION}}` - Site description for SEO
- `{{SITE_AUTHOR}}` - Author/organization name  
- `{{SITE_URL}}` - Full site URL
- `{{GITHUB_REPO}}` - GitHub repository name
- `{{CURRENT_YEAR}}` - Current year for copyright

### Navigation Variables
- `{{NAV_LINKS}}` - Desktop navigation links
- `{{MOBILE_NAV_LINKS}}` - Mobile navigation links
- `{{FOOTER_LINKS}}` - Footer navigation links

### Content Variables
- `{{MAIN_CONTENT}}` - Main page content area
- `{{CTA_BUTTONS}}` - Call-to-action buttons
- `{{HERO_CONTENT}}` - Hero section content
- `{{SIDEBAR_CONTENT}}` - Sidebar content

## Template Files

### Core Templates
- **`base.html`** - Base template with navigation, footer, and common elements
- **`home.html`** - Homepage template with hero section
- **`about.html`** - About page template
- **`contact.html`** - Contact page with form
- **`blog.html`** - Blog listing page
- **`article.html`** - Individual article template

### Specialized Templates  
- **`portfolio.html`** - Portfolio/projects showcase
- **`services.html`** - Services or offerings page
- **`404.html`** - Error page template

### Content Blocks
- **`blocks/`** directory with reusable components:
  - `hero-sections.html` - Different hero section styles
  - `feature-sections.html` - Feature highlight sections
  - `testimonials.html` - Customer testimonial blocks
  - `contact-forms.html` - Various contact form layouts

## Usage

Templates are processed by the site generator in `site-generator.js`. Variables are replaced using a simple string replacement system:

```javascript
function processTemplate(template, variables) {
    let processed = template;
    for (const [key, value] of Object.entries(variables)) {
        const placeholder = `{{${key}}}`;
        processed = processed.replaceAll(placeholder, value);
    }
    return processed;
}
```

## Customization

### Adding New Templates
1. Create new `.html` file in this directory
2. Use `{{VARIABLE_NAME}}` placeholders for dynamic content
3. Update the site generator to recognize the new template

### Styling
- Templates use Tailwind CSS for styling
- Custom CSS can be added in `<style>` blocks
- Color scheme uses consistent brand colors:
  - Primary: `#1b5fa3`
  - Secondary: `#144a84` 
  - Accent: `#f9943b`

### Responsive Design
- All templates are mobile-first responsive
- Use Tailwind responsive prefixes (`sm:`, `md:`, `lg:`, `xl:`)
- Test on different screen sizes

## Template Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Meta tags, SEO, favicon -->
    <title>{{SITE_NAME}}</title>
    <meta name="description" content="{{SITE_DESCRIPTION}}">
    <!-- Tailwind CSS and custom styles -->
</head>
<body>
    <!-- Navigation component -->
    <nav>{{NAV_CONTENT}}</nav>
    
    <!-- Main content area -->
    <main>{{MAIN_CONTENT}}</main>
    
    <!-- Footer component -->
    <footer>{{FOOTER_CONTENT}}</footer>
</body>
</html>
```

This ensures consistent structure across all generated pages while allowing for customization of specific content areas.