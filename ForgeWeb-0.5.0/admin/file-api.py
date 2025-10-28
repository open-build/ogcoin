#!/usr/bin/env python3
"""
ForgeWeb Local Server
Enhanced server for the admin interface with site generation and preview capabilities.
"""

import json
import os
import sys
import shutil
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime
import threading
import argparse
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None
    print("⚠️  requests library not installed. GitHub integration will be limited.")

try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✓ Loaded environment variables from {env_path}")
except ImportError:
    load_dotenv = None
    print("⚠️  python-dotenv not installed. Using system environment variables only.")

class ForgeWebHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.admin_dir = os.path.dirname(os.path.abspath(__file__))
        # Point to the actual project root (two levels up from admin/)
        self.website_root = os.path.dirname(os.path.dirname(self.admin_dir))
        super().__init__(*args, **kwargs)
    
    def get_config_value(self, key, default=None):
        """Get configuration value from environment or config file"""
        # First check environment variables
        env_value = os.getenv(key)
        if env_value is not None:
            return env_value
        
        # Then check site config
        config_path = os.path.join(self.admin_dir, 'site-config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get(key.lower(), default)
            except:
                pass
        
        return default

    def do_GET(self):
        """Handle GET requests for both admin and preview"""
        parsed_path = urlparse(self.path)
        
        if self.path.startswith('/admin/'):
            # Serve admin files
            self.serve_admin_file(parsed_path.path)
        elif self.path.startswith('/preview/'):
            # Serve preview of generated site
            preview_path = self.path.replace('/preview/', '')
            self.serve_preview_file(preview_path)
        elif self.path.startswith('/api/'):
            # Handle API requests
            self.handle_api_get_request()
        else:
            # Serve generated site files (main website)
            self.serve_site_file(parsed_path.path)

    def do_POST(self):
        """Handle POST requests for API endpoints"""
        if self.path == '/api/save-file':
            self.handle_save_file()
        elif self.path == '/api/setup-site' or self.path == '/api/site-setup':
            self.handle_setup_site()
        elif self.path == '/api/branding':
            self.handle_branding_request()
        elif self.path == '/api/import-html':
            self.handle_html_import()
        elif self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(404, "API endpoint not found")

    def serve_admin_file(self, path):
        """Serve admin interface files"""
        # Remove /admin/ prefix
        file_path = path[7:] if path.startswith('/admin/') else path
        
        if not file_path or file_path == '/':
            file_path = 'index.html'
        
        full_path = os.path.join(self.admin_dir, file_path)
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            self.serve_file(full_path)
        else:
            self.send_error(404, f"Admin file not found: {file_path}")

    def serve_site_file(self, path):
        """Serve generated site files"""
        if not path or path == '/':
            path = 'index.html'
        elif path.startswith('/'):
            path = path[1:]
            
        full_path = os.path.join(self.website_root, path)
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            self.serve_file(full_path)
        else:
            # Try to serve 404.html if it exists
            error_404_path = os.path.join(self.website_root, '404.html')
            if os.path.exists(error_404_path):
                self.send_response(404)
                self.serve_file(error_404_path, send_response=False)
            else:
                self.send_error(404, f"Page not found: {path}")

    def serve_preview_file(self, path):
        """Serve preview files (same as site files but with different URL structure)"""
        self.serve_site_file(path)

    def serve_file(self, file_path, send_response=True):
        """Serve a file with appropriate headers"""
        try:
            # Determine content type
            content_type = self.get_content_type(file_path)
            
            if send_response:
                self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
                
        except Exception as e:
            print(f"Error serving file {file_path}: {e}")
            if send_response:
                self.send_error(500, "Internal server error")

    def get_content_type(self, file_path):
        """Get content type based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        content_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.txt': 'text/plain',
            '.xml': 'application/xml',
        }
        return content_types.get(ext, 'application/octet-stream')

    def handle_save_file(self):
        """Handle file save requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            file_path = data.get('path')
            file_content = data.get('content')
            
            if not file_path or file_content is None:
                self.send_json_error(400, "Missing path or content")
                return
            
            # Clean and validate path
            clean_path = self.clean_path(file_path)
            full_path = os.path.join(self.website_root, clean_path)
            
            # Ensure directory exists
            dir_path = os.path.dirname(full_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            response = {
                'success': True,
                'message': f'File saved to {clean_path}',
                'path': clean_path,
                'size': len(file_content)
            }
            
            self.send_json_response(response)
            print(f"✓ Saved: {clean_path} ({len(file_content)} bytes)")
            
        except Exception as e:
            print(f"✗ Save error: {e}")
            self.send_json_error(500, str(e))

    def handle_setup_site(self):
        """Handle site setup requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Handle both action-based and direct data formats
            action = data.get('action')
            site_data = data.get('data', data)  # Use data directly if no action
            
            if action == 'update-config' or not action:
                result = self.update_site_config(site_data)
            elif action == 'generate-site':
                result = self.generate_site_files(site_data)
            elif action == 'create-github-repo':
                result = self.create_github_repo(site_data)
            else:
                # Handle direct site configuration without action
                result = self.update_site_config(site_data)
                
            self.send_json_response(result)
            
        except Exception as e:
            print(f"✗ Setup error: {e}")
            self.send_json_error(500, str(e))

    def handle_api_get_request(self):
        """Handle GET API requests"""
        try:
            if self.path == '/api/branding':
                branding_config = self.load_branding_config()
                self.send_json_response(branding_config)
            elif self.path == '/api/site-status':
                self.send_json_response({'status': 'running', 'admin_url': '/admin/'})
            elif self.path == '/api/preview-url':
                self.send_json_response({'preview_url': f'http://localhost:{self.server.server_port}/'})
            else:
                endpoint = self.path.replace('/api/', '')
                self.send_json_error(404, f"API endpoint not found: {endpoint}")
                
        except Exception as e:
            self.send_json_error(500, str(e))

    def handle_api_request(self):
        """Handle other API requests"""
        try:
            # Parse the API endpoint
            endpoint = self.path.replace('/api/', '')
            
            if endpoint == 'site-status':
                self.send_json_response({'status': 'running', 'admin_url': '/admin/'})
            elif endpoint == 'preview-url':
                self.send_json_response({'preview_url': f'http://localhost:{self.server.server_port}/'})
            else:
                self.send_json_error(404, f"API endpoint not found: {endpoint}")
                
        except Exception as e:
            self.send_json_error(500, str(e))

    def update_site_config(self, site_data):
        """Update site configuration"""
        config_path = os.path.join(self.admin_dir, 'site-config.json')
        
        # Load existing config
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Update config with new data
        config.update({
            'site': {
                'name': site_data.get('siteName', 'My Website'),
                'url': f"https://{site_data.get('githubUsername', 'username')}.github.io/{site_data.get('githubRepo', 'repository')}",
                'description': site_data.get('siteDescription', 'A website built with ForgeWeb'),
                'author': site_data.get('siteAuthor', 'Website Owner'),
                'generator': 'ForgeWeb v1.0.0',
                'support_url': 'https://docs.buildly.io/forgeweb'
            },
            'github': {
                'username': site_data.get('githubUsername', ''),
                'repository': site_data.get('githubRepo', ''),
                'pages_enabled': True
            },
            'content': {
                'site_type': site_data.get('siteType', 'blog'),
                'include_about': site_data.get('includeAbout', True),
                'include_contact': site_data.get('includeContact', True),
                'include_blog': site_data.get('includeBlog', True),
                'include_portfolio': site_data.get('includePortfolio', False),
                'include_services': site_data.get('includeServices', False),
                'include_sample_content': site_data.get('includeSampleContent', True)
            }
        })
        
        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {'success': True, 'message': 'Site configuration updated'}

    def generate_site_files(self, site_data):
        """Generate site files based on configuration"""
        try:
            # Load templates
            template_dir = os.path.join(self.website_root, 'templates')
            base_template_path = os.path.join(template_dir, 'base.html')
            
            if not os.path.exists(base_template_path):
                return {'success': False, 'error': 'Base template not found'}
            
            with open(base_template_path, 'r', encoding='utf-8') as f:
                base_template = f.read()
            
            # Generate pages based on configuration
            pages_generated = []
            
            # Always generate home page
            home_content = self.load_content_template('home-content.html')
            home_page = self.generate_page(base_template, 'Home', home_content, site_data)
            self.write_page('index.html', home_page)
            pages_generated.append('index.html')
            
            # Generate optional pages
            if site_data.get('includeAbout', True):
                about_content = self.load_content_template('about-content.html')
                about_page = self.generate_page(base_template, 'About', about_content, site_data)
                self.write_page('about.html', about_page)
                pages_generated.append('about.html')
            
            if site_data.get('includeContact', True):
                contact_content = self.load_content_template('contact-content.html')
                contact_page = self.generate_page(base_template, 'Contact', contact_content, site_data)
                self.write_page('contact.html', contact_page)
                pages_generated.append('contact.html')
            
            return {
                'success': True, 
                'message': f'Generated {len(pages_generated)} pages',
                'pages': pages_generated
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def load_content_template(self, template_name):
        """Load content template"""
        template_path = os.path.join(self.website_root, 'templates', template_name)
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        return f"<h1>Content for {template_name}</h1><p>Template not found, but page generated successfully.</p>"

    def generate_page(self, base_template, title, content, site_data):
        """Generate a complete page from template and content"""
        page = base_template.replace('{{TITLE}}', title)
        page = page.replace('{{SITE_NAME}}', site_data.get('siteName', 'My Website'))
        page = page.replace('{{CONTENT}}', content)
        page = page.replace('{{DESCRIPTION}}', site_data.get('siteDescription', 'A website built with ForgeWeb'))
        return page

    def write_page(self, filename, content):
        """Write page content to file"""
        page_path = os.path.join(self.website_root, filename)
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def create_github_repo(self, site_data):
        """Create GitHub repository (placeholder)"""
        # This would require GitHub API integration
        return {
            'success': True, 
            'message': 'GitHub repository creation not yet implemented',
            'note': 'Please create repository manually at GitHub.com'
        }

    def run_site_generator(self, site_data):
        """Run the site generator to create files"""
        from datetime import datetime
        
        # Basic site generator implementation
        files_created = []
        
        # Generate index.html
        index_content = self.generate_basic_page(
            title=site_data.get('siteName', 'My Website'),
            description=site_data.get('siteDescription', 'Welcome to my website'),
            content=f"""
            <div class="text-center py-16">
                <h1 class="text-4xl font-bold text-gray-900 mb-4">{site_data.get('siteName', 'My Website')}</h1>
                <p class="text-xl text-gray-600 mb-8">{site_data.get('siteDescription', 'Welcome to my website')}</p>
                <div class="space-x-4">
                    {"<a href='about.html' class='bg-blue-600 text-white px-6 py-3 rounded-lg'>About</a>" if site_data.get('includeAbout') else ""}
                    {"<a href='contact.html' class='bg-green-600 text-white px-6 py-3 rounded-lg'>Contact</a>" if site_data.get('includeContact') else ""}
                </div>
            </div>
            """,
            site_data=site_data
        )
        
        self.write_file('index.html', index_content)
        files_created.append('index.html')
        
        # Generate additional pages based on configuration
        if site_data.get('includeAbout'):
            about_content = self.generate_about_page(site_data)
            self.write_file('about.html', about_content)
            files_created.append('about.html')
            
        if site_data.get('includeContact'):
            contact_content = self.generate_contact_page(site_data)
            self.write_file('contact.html', contact_content)
            files_created.append('contact.html')
            
        # Generate robots.txt and sitemap.xml
        self.write_file('robots.txt', self.generate_robots_txt(site_data))
        self.write_file('sitemap.xml', self.generate_sitemap(site_data, files_created))
        files_created.extend(['robots.txt', 'sitemap.xml'])
        
        return files_created

    def generate_basic_page(self, title, description, content, site_data):
        """Generate a basic HTML page using template"""
        template_path = os.path.join(self.website_root, 'templates', 'base.html')
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        else:
            # Fallback basic template
            template_content = self.get_fallback_template()
        
        # Prepare template variables
        template_vars = {
            'SITE_TITLE': title,
            'SITE_NAME': site_data.get('siteName', 'My Website'),
            'SITE_DESCRIPTION': description,
            'SITE_AUTHOR': site_data.get('siteAuthor', 'Website Owner'),
            'SITE_URL': f"https://{site_data.get('githubUsername', 'username')}.github.io/{site_data.get('githubRepo', 'repository')}",
            'CURRENT_YEAR': str(datetime.now().year),
            'CONTENT': content,
            'NAV_LINKS': self.generate_nav_links(site_data),
            'LOGO_PATH': self.get_config_value('LOGO_PATH', 'assets/images/logo.png'),
            'TAILWIND_CDN_URL': self.get_config_value('TAILWIND_CDN_URL', 'https://cdn.tailwindcss.com'),
            'CUSTOM_CSS_PATH': self.get_config_value('CUSTOM_CSS_PATH', 'assets/css/custom.css'),
            'BRAND_PRIMARY_COLOR': self.get_config_value('BRAND_PRIMARY_COLOR', '#1b5fa3'),
            'BRAND_SECONDARY_COLOR': self.get_config_value('BRAND_SECONDARY_COLOR', '#144a84'),
            'BRAND_ACCENT_COLOR': self.get_config_value('BRAND_ACCENT_COLOR', '#f9943b'),
            'FAVICON_PATH': '/favicon.ico'
        }
        
        # Replace template variables
        for key, value in template_vars.items():
            # Handle conditional blocks {{#VARIABLE}}...{{/VARIABLE}}
            if value:
                # Show content between conditional tags
                template_content = template_content.replace(f'{{{{#{key}}}}}', '')
                template_content = template_content.replace(f'{{{{/{key}}}}}', '')
            else:
                # Remove content between conditional tags
                import re
                pattern = f'{{{{#{key}}}}}.*?{{{{/{key}}}}}'
                template_content = re.sub(pattern, '', template_content, flags=re.DOTALL)
            
            # Replace simple variables
            template_content = template_content.replace(f'{{{{{key}}}}}', str(value))
        
        return template_content
    
    def get_fallback_template(self):
        """Basic fallback template if base.html is not found"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{SITE_TITLE}}</title>
    <meta name="description" content="{{SITE_DESCRIPTION}}">
    <script src="{{TAILWIND_CDN_URL}}"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '{{BRAND_PRIMARY_COLOR}}',
                        secondary: '{{BRAND_SECONDARY_COLOR}}',
                        accent: '{{BRAND_ACCENT_COLOR}}'
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-sm">
        <div class="max-w-6xl mx-auto px-4 py-4">
            <div class="flex justify-between items-center">
                <h1 class="text-xl font-bold text-primary">{{SITE_NAME}}</h1>
                <div class="space-x-4">{{NAV_LINKS}}</div>
            </div>
        </div>
    </nav>
    <main class="max-w-6xl mx-auto px-4 py-8">{{CONTENT}}</main>
    <footer class="bg-gray-800 text-white py-8 mt-16">
        <div class="max-w-6xl mx-auto px-4 text-center">
            <p>&copy; {{CURRENT_YEAR}} {{SITE_AUTHOR}}. Created with ForgeWeb.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def generate_nav_links(self, site_data):
        """Generate navigation links based on site configuration"""
        links = []
        
        if site_data.get('includeAbout'):
            links.append('<a href="about.html" class="nav-link">About</a>')
        if site_data.get('includeContact'):
            links.append('<a href="contact.html" class="nav-link">Contact</a>')
        if site_data.get('includeBlog'):
            links.append('<a href="blog.html" class="nav-link">Blog</a>')
        if site_data.get('includePortfolio'):
            links.append('<a href="portfolio.html" class="nav-link">Portfolio</a>')
        if site_data.get('includeServices'):
            links.append('<a href="services.html" class="nav-link">Services</a>')
        
        return '\n                    '.join(links)

    def generate_about_page(self, site_data):
        """Generate about page"""
        content = f"""
        <div class="max-w-4xl mx-auto">
            <h1 class="text-4xl font-bold text-gray-900 mb-8">About {site_data.get('siteName', 'Us')}</h1>
            <div class="prose prose-lg">
                <p>Welcome to {site_data.get('siteName', 'our website')}. {site_data.get('siteDescription', 'This is our story.')}</p>
                <p>We're passionate about creating great experiences and building meaningful connections with our community.</p>
                <p>This website was created with ForgeWeb, an AI-powered static site generator by Buildly.</p>
            </div>
        </div>
        """
        return self.generate_basic_page(f"About - {site_data.get('siteName', 'My Website')}", f"Learn more about {site_data.get('siteName', 'us')}", content, site_data)

    def generate_contact_page(self, site_data):
        """Generate contact page"""
        content = f"""
        <div class="max-w-4xl mx-auto">
            <h1 class="text-4xl font-bold text-gray-900 mb-8">Contact Us</h1>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
                <div>
                    <h2 class="text-2xl font-bold mb-4">Get in touch</h2>
                    <form class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium mb-2">Name</label>
                            <input type="text" class="w-full px-3 py-2 border rounded-md" required>
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-2">Email</label>
                            <input type="email" class="w-full px-3 py-2 border rounded-md" required>
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-2">Message</label>
                            <textarea class="w-full px-3 py-2 border rounded-md" rows="4" required></textarea>
                        </div>
                        <button type="submit" class="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700">
                            Send Message
                        </button>
                    </form>
                </div>
                <div>
                    <h2 class="text-2xl font-bold mb-4">Contact Information</h2>
                    <div class="space-y-2">
                        <p><strong>Email:</strong> hello@{site_data.get('githubRepo', 'website')}.com</p>
                        <p><strong>Website:</strong> {site_data.get('siteName', 'My Website')}</p>
                    </div>
                </div>
            </div>
        </div>
        """
        return self.generate_basic_page(f"Contact - {site_data.get('siteName', 'My Website')}", f"Contact {site_data.get('siteName', 'us')}", content, site_data)

    def generate_robots_txt(self, site_data):
        """Generate robots.txt"""
        site_url = f"https://{site_data.get('githubUsername', 'username')}.github.io/{site_data.get('githubRepo', 'repository')}"
        return f"""User-agent: *
Allow: /

Sitemap: {site_url}/sitemap.xml"""

    def generate_sitemap(self, site_data, files):
        """Generate sitemap.xml"""
        site_url = f"https://{site_data.get('githubUsername', 'username')}.github.io/{site_data.get('githubRepo', 'repository')}"
        urls = []
        
        for file in files:
            if file.endswith('.html'):
                if file == 'index.html':
                    url = site_url
                else:
                    url = f"{site_url}/{file}"
                urls.append(f"  <url><loc>{url}</loc><changefreq>weekly</changefreq></url>")
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""

    def handle_branding_request(self):
        """Handle branding configuration requests"""
        try:
            if self.command == 'GET':
                # Return current branding settings
                branding_config = self.load_branding_config()
                self.send_json_response(branding_config)
            
            elif self.command == 'POST':
                # Save new branding settings
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                branding_data = json.loads(post_data.decode('utf-8'))
                
                result = self.save_branding_config(branding_data)
                self.send_json_response(result)
            
            else:
                self.send_json_error(405, "Method not allowed")
                
        except Exception as e:
            print(f"✗ Branding request error: {e}")
            self.send_json_error(500, str(e))

    def load_branding_config(self):
        """Load current branding configuration"""
        try:
            # Check for branding config file
            branding_path = os.path.join(self.admin_dir, 'branding-config.json')
            if os.path.exists(branding_path):
                with open(branding_path, 'r') as f:
                    return json.load(f)
            
            # Return default branding configuration
            return {
                'colors': {
                    'primary': self.get_config_value('BRAND_PRIMARY_COLOR', '#1b5fa3'),
                    'secondary': self.get_config_value('BRAND_SECONDARY_COLOR', '#144a84'),
                    'accent': self.get_config_value('BRAND_ACCENT_COLOR', '#f9943b')
                },
                'typography': {
                    'fontFamily': 'system',
                    'customFontUrl': '',
                    'borderRadius': 'md'
                },
                'assets': {
                    'logoPath': self.get_config_value('LOGO_PATH', ''),
                    'logoAltText': 'Company Logo',
                    'faviconPath': '/favicon.ico'
                },
                'customCSS': ''
            }
            
        except Exception as e:
            print(f"Error loading branding config: {e}")
            return {'error': str(e)}

    def save_branding_config(self, branding_data):
        """Save branding configuration"""
        try:
            branding_path = os.path.join(self.admin_dir, 'branding-config.json')
            
            # Save branding configuration
            with open(branding_path, 'w') as f:
                json.dump(branding_data, f, indent=2)
            
            # Update custom CSS file if provided
            if 'customCSS' in branding_data and branding_data['customCSS']:
                css_path = os.path.join(self.website_root, 'assets', 'css', 'custom.css')
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(css_path), exist_ok=True)
                
                # Update CSS variables with new colors
                css_content = self.generate_custom_css(branding_data)
                with open(css_path, 'w') as f:
                    f.write(css_content)
            
            # Update environment variables if needed
            self.update_env_variables(branding_data)
            
            return {
                'success': True,
                'message': 'Branding configuration saved successfully'
            }
            
        except Exception as e:
            print(f"Error saving branding config: {e}")
            return {'success': False, 'error': str(e)}

    def generate_custom_css(self, branding_data):
        """Generate custom CSS with branding variables"""
        colors = branding_data.get('colors', {})
        typography = branding_data.get('typography', {})
        custom_css = branding_data.get('customCSS', '')
        
        css_content = f"""/* ForgeWeb Custom Styles - Auto-generated */
:root {{
    /* Brand colors */
    --brand-primary: {colors.get('primary', '#1b5fa3')};
    --brand-secondary: {colors.get('secondary', '#144a84')};
    --brand-accent: {colors.get('accent', '#f9943b')};
    
    /* Additional brand variables */
    --brand-text: #1f2937;
    --brand-bg: #f9fafb;
    --brand-border: #e5e7eb;
}}

/* Typography */
{self.get_font_css(typography)}

/* Custom button styles */
.btn-brand {{
    background-color: var(--brand-primary);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: {self.get_border_radius(typography.get('borderRadius', 'md'))};
    font-weight: 500;
    transition: background-color 0.2s;
}}

.btn-brand:hover {{
    background-color: var(--brand-secondary);
}}

.btn-brand-outline {{
    border: 2px solid var(--brand-primary);
    color: var(--brand-primary);
    padding: 0.75rem 1.5rem;
    border-radius: {self.get_border_radius(typography.get('borderRadius', 'md'))};
    font-weight: 500;
    background: transparent;
    transition: all 0.2s;
}}

.btn-brand-outline:hover {{
    background-color: var(--brand-primary);
    color: white;
}}

/* Navigation enhancements */
.nav-link {{
    color: #374151;
    transition: color 0.2s;
}}

.nav-link:hover {{
    color: var(--brand-primary);
}}

.nav-link.active {{
    color: var(--brand-primary);
}}

/* Card hover effects */
.card-hover {{
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

.card-hover:hover {{
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}}

/* Custom CSS from user */
{custom_css}
"""
        return css_content

    def get_font_css(self, typography):
        """Generate font CSS based on typography settings"""
        font_family = typography.get('fontFamily', 'system')
        custom_url = typography.get('customFontUrl', '')
        
        if font_family == 'custom' and custom_url:
            return f"""@import url('{custom_url}');
body {{ font-family: 'Custom Font', system-ui, sans-serif; }}"""
        elif font_family == 'inter':
            return """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
body { font-family: 'Inter', system-ui, sans-serif; }"""
        elif font_family == 'roboto':
            return """@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
body { font-family: 'Roboto', system-ui, sans-serif; }"""
        elif font_family == 'opensans':
            return """@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700&display=swap');
body { font-family: 'Open Sans', system-ui, sans-serif; }"""
        elif font_family == 'lato':
            return """@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap');
body { font-family: 'Lato', system-ui, sans-serif; }"""
        elif font_family == 'montserrat':
            return """@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');
body { font-family: 'Montserrat', system-ui, sans-serif; }"""
        else:
            return """body { font-family: system-ui, -apple-system, sans-serif; }"""

    def get_border_radius(self, radius_setting):
        """Convert border radius setting to CSS value"""
        radius_map = {
            'none': '0px',
            'sm': '4px',
            'md': '8px',
            'lg': '12px',
            'xl': '16px',
            'full': '50%'
        }
        return radius_map.get(radius_setting, '8px')

    def update_env_variables(self, branding_data):
        """Update environment variables with branding data"""
        try:
            colors = branding_data.get('colors', {})
            # Update in-memory configuration (for current session)
            if colors.get('primary'):
                os.environ['BRAND_PRIMARY_COLOR'] = colors['primary']
            if colors.get('secondary'):
                os.environ['BRAND_SECONDARY_COLOR'] = colors['secondary']
            if colors.get('accent'):
                os.environ['BRAND_ACCENT_COLOR'] = colors['accent']
        except Exception as e:
            print(f"Warning: Could not update environment variables: {e}")

    def handle_html_import(self):
        """Handle HTML import requests"""
        try:
            # Placeholder for HTML import functionality
            self.send_json_response({
                'success': False,
                'message': 'HTML import functionality coming soon'
            })
        except Exception as e:
            self.send_json_error(500, str(e))

    def create_github_repo(self, site_data):
        """Create GitHub repository (requires requests library)"""
        if not requests:
            return {'success': False, 'error': 'requests library not available'}
        
        github_token = site_data.get('githubToken')
        if not github_token:
            return {'success': False, 'error': 'No GitHub token provided'}
        
        try:
            # Create repository via GitHub API
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            repo_data = {
                'name': site_data.get('githubRepo'),
                'description': site_data.get('siteDescription', 'Website created with ForgeWeb'),
                'homepage': f"https://{site_data.get('githubUsername')}.github.io/{site_data.get('githubRepo')}",
                'private': False,
                'has_pages': True
            }
            
            response = requests.post(
                'https://api.github.com/user/repos',
                headers=headers,
                json=repo_data
            )
            
            if response.status_code == 201:
                return {'success': True, 'message': 'GitHub repository created successfully'}
            else:
                return {'success': False, 'error': f'GitHub API error: {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': f'GitHub creation failed: {str(e)}'}

    def write_file(self, path, content):
        """Write file to website root"""
        full_path = os.path.join(self.website_root, path)
        dir_path = os.path.dirname(full_path)
        
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def clean_path(self, path):
        """Clean and validate file path"""
        clean_path = path.replace('../', '')
        if clean_path.startswith('/'):
            clean_path = clean_path[1:]
        return clean_path

    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def send_json_error(self, status_code, message):
        """Send JSON error response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_data = {'error': message, 'status': status_code}
        self.wfile.write(json.dumps(error_data).encode('utf-8'))

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def start_forgeweb_server(port=8000, host='localhost'):
    """Start the ForgeWeb server"""
    try:
        server = HTTPServer((host, port), ForgeWebHandler)
        server.server_port = port  # Store port for handlers to access
        
        print(f"""
🚀 ForgeWeb Server Starting...

   Admin Interface: http://{host}:{port}/admin/
   Site Preview:    http://{host}:{port}/
   
   Ready to create amazing websites! 🎨
   
Press Ctrl+C to stop the server.
        """)
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n👋 ForgeWeb server stopped.")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ForgeWeb Local Server')
    parser.add_argument('--port', type=int, default=8000, help='Port number (default: 8000)')
    parser.add_argument('--host', default='localhost', help='Host address (default: localhost)')
    
    args = parser.parse_args()
    start_forgeweb_server(args.port, args.host)