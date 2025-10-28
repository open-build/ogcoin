/**
 * File Manager for Buildly AI Content Manager
 * Handles file operations, content parsing, and Git integration
 */

class FileManager {
    constructor() {
        this.baseUrl = window.location.origin;
        this.websiteRoot = '/';
        this.allowedExtensions = ['.html', '.md', '.txt'];
        this.contentDirs = ['articles/', '', 'templates/', 'includes/'];
        this.cache = new Map();
        this.cacheTimeout = 300000; // 5 minutes
    }

    /**
        /**
     * Write file using modern File System Access API
     */
    async writeFileModern(filePath, content) {
        try {
            const fileName = this.getFileName(filePath);
            const fileHandle = await window.showSaveFilePicker({
                suggestedName: fileName,
                types: [
                    {
                        description: 'HTML files',
                        accept: {
                            'text/html': ['.html'],
                        },
                    },
                ],
            });
            
            const writable = await fileHandle.createWritable();
            await writable.write(content);
            await writable.close();
            
            return {
                success: true,
                message: `File ${filePath} saved successfully`,
                path: filePath,
                size: content.length,
                downloaded: false
            };
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Save cancelled by user');
            }
            throw error;
        }
    }

    /**
     * Download file content as a file
     */
    /**
     * Write file locally using a simple method
     */
    async writeFileLocal(filePath, content) {
        try {
            // First try to save via API call to our dev server
            try {
                const response = await fetch('/save-file', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        path: filePath,
                        content: content
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    console.log(`✓ File saved locally via API: ${filePath}`);
                    return {
                        success: true,
                        message: `File ${filePath} saved successfully to local filesystem`,
                        path: filePath,
                        size: content.length,
                        method: 'local-api'
                    };
                }
            } catch (apiError) {
                console.log('Local API save not available, will fall back to download');
                return false; // Signal that local save failed
            }
            
            return false; // Local save not successful
            
        } catch (error) {
            console.error('Local write failed:', error);
            return false;
        }
    }

    downloadFile(filePath, content) {
        const blob = new Blob([content], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = this.getFileName(filePath);
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        URL.revokeObjectURL(url);
    }

    /**
     * Get list of all content files
     */
    async getFileList() {
        const cacheKey = 'fileList';
        const cached = this.getFromCache(cacheKey);
        if (cached) return cached;

        try {
            const files = [];
            
            // Since we're running in browser, we need to simulate file discovery
            // In a real implementation, this would call a backend API
            const knownFiles = await this.discoverFiles();
            
            for (const file of knownFiles) {
                try {
                    const info = await this.getFileInfo(file);
                    files.push(info);
                } catch (error) {
                    console.warn(`Error getting info for ${file}:`, error);
                }
            }
            
            this.setCache(cacheKey, files);
            return files;
        } catch (error) {
            console.error('Error getting file list:', error);
            throw new Error('Failed to load file list');
        }
    }

    /**
     * Discover files by attempting to load known patterns
     */
    async discoverFiles() {
        const files = [];
        
        // Try to get dynamic file list from our API first
        try {
            const response = await fetch('/api/list-html-files');
            if (response.ok) {
                const data = await response.json();
                const knownFiles = data.files.map(file => file.filename);
                
                console.log(`📁 Discovered ${knownFiles.length} HTML files from API`);
                files.push(...knownFiles);
                
                // Get article files
                const articleFiles = await this.discoverArticleFiles();
                files.push(...articleFiles);
                
                return files;
            }
        } catch (error) {
            console.warn('Failed to get dynamic file list, falling back to static list:', error);
        }
        
        // Fallback to known HTML files from the workspace structure
        const knownFiles = [
            'index.html',
            'labs.html',
            'pricing.html',
            'use-cases.html',
            'team.html',
            'developer.html',
            'product-manager.html',
            'articles.html',
            'rad-core.html'
        ];

        // Get articles using fallback method
        const articleFiles = await this.discoverArticleFiles();
        
        // Fallback to static list if dynamic doesn't work
        if (articleFiles.length === 0) {
            articleFiles = [
                'articles/ai-powered-product-management.html',
                'articles/ai-powered-content-management-local-vs-cloud.html',
                'articles/ai-powered-devops.html',
                'articles/ai-powered-release-planning.html',
                'articles/future-of-software-development.html',
                'articles/startup-scaling.html',
                'articles/product-lifecycle.html',
                'articles/feature-prioritization.html',
                'articles/building-ethical-ai.html',
                'articles/10x-engineer-myth-diverse-teams.html',
                'articles/it-s-time-to-kill-agile-for-most-use-cases.html'
            ];
        }

        files.push(...knownFiles, ...articleFiles);
        
        return files;
    }

    /**
     * Discover article files using various methods
     */
    async discoverArticleFiles() {
        let articleFiles = [];
        
        try {
            // Try to get dynamic file list from server
            const response = await fetch('/articles', {
                method: 'GET',
                headers: { 'Accept': 'application/json' }
            });
            
            if (response.ok) {
                const fileList = await response.text();
                // Parse directory listing for .html files
                const htmlFiles = fileList.match(/href="([^"]+\.html)"/g);
                if (htmlFiles) {
                    articleFiles = htmlFiles
                        .map(match => match.match(/href="([^"]+\.html)"/)[1])
                        .filter(file => !file.includes('..') && file.endsWith('.html'))
                        .map(file => `articles/${file}`);
                }
            }
        } catch (error) {
            console.log('Could not fetch dynamic article list, using static list');
        }
        
        // Fallback to static list if dynamic doesn't work
        if (articleFiles.length === 0) {
            articleFiles = [
                'articles/ai-powered-product-management.html',
                'articles/ai-powered-content-management-local-vs-cloud.html',
                'articles/ai-powered-devops.html',
                'articles/ai-powered-release-planning.html',
                'articles/future-of-software-development.html',
                'articles/startup-scaling.html',
                'articles/product-lifecycle.html',
                'articles/feature-prioritization.html',
                'articles/building-ethical-ai.html',
                'articles/it-s-time-to-kill-agile-for-most-use-cases.html'
            ];
        }

        return articleFiles;
    }

    /**
     * Get file information and metadata
     */
    async getFileInfo(filePath) {
        try {
            const content = await this.readFile(filePath);
            const metadata = this.extractMetadata(content);
            const stats = this.getFileStats(content);
            
            return {
                path: filePath,
                name: this.getFileName(filePath),
                type: this.getFileType(filePath),
                size: content.length,
                modified: new Date().toISOString(), // Placeholder
                metadata: metadata,
                stats: stats,
                isArticle: filePath.startsWith('articles/'),
                isTemplate: filePath.startsWith('templates/')
            };
        } catch (error) {
            throw new Error(`Failed to get file info for ${filePath}: ${error.message}`);
        }
    }

    /**
     * Read file content
     */
    async readFile(filePath) {
        const cacheKey = `file:${filePath}`;
        const cached = this.getFromCache(cacheKey);
        if (cached) return cached;

        try {
            // Use the API endpoint for reading files for editing
            const url = `/api/read-file?file=${encodeURIComponent(filePath)}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const content = await response.text();
            this.setCache(cacheKey, content);
            return content;
        } catch (error) {
            throw new Error(`Failed to read ${filePath}: ${error.message}`);
        }
    }

    /**
     * Write file content to local filesystem
     */
    async writeFile(filePath, content) {
        try {
            // Convert relative path for admin folder context
            const relativePath = '../' + filePath;
            
            console.log(`Writing ${content.length} characters to ${relativePath}`);
            
            // First try to use local server save (when running dev-server.py)
            const success = await this.writeFileLocal(relativePath, content);
            
            if (success) {
                return success;
            }
            
            // If local server isn't available, use File System Access API (modern browsers)
            if ('showSaveFilePicker' in window) {
                console.log('Local server not available, using File System Access API');
                return await this.writeFileModern(filePath, content);
            }
            
            // If neither method works, fall back to download
            console.log('No save method available, falling back to download');
            this.downloadFile(filePath, content);
            return {
                success: true,
                message: `File ${filePath} downloaded (no save method available)`,
                path: filePath,
                size: content.length,
                downloaded: true
            };
            
            // Update cache
            this.setCache(`file:${filePath}`, content);
            
            return {
                success: true,
                message: `File ${filePath} saved successfully`,
                path: filePath,
                size: content.length,
                downloaded: false
            };
        } catch (error) {
            console.error('Write failed, falling back to download:', error);
            // Fallback to download if save fails
            this.downloadFile(filePath, content);
            return {
                success: true,
                message: `File ${filePath} downloaded (save failed: ${error.message})`,
                path: filePath,
                size: content.length,
                downloaded: true
            };
        }
    }

    /**
     * Create new article file
     */
    async createArticle(title, content = '') {
        const fileName = this.generateFileName(title);
        const filePath = `articles/${fileName}`;
        
        // Generate article content from template
        const articleContent = this.generateArticleFromTemplate(title, content);
        
        return this.writeFile(filePath, articleContent);
    }

    /**
     * Generate article content from template
     */
    generateArticleFromTemplate(title, content) {
        const currentDate = new Date().toISOString().split('T')[0];
        const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
        
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Load common elements -->
    <script src="/js/buildly-head.js"></script>
    
    <!-- Page-specific customization -->
    <title>${title} - Buildly</title>
    <meta name="description" content="TODO: Add description for ${title}">
    <meta name="keywords" content="TODO: Add keywords">
    <link rel="canonical" href="https://www.buildly.io/articles/${slug}.html">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://www.buildly.io/articles/${slug}.html">
    <meta property="og:title" content="${title}">
    <meta property="og:description" content="TODO: Add description for ${title}">
    <meta property="og:image" content="https://www.buildly.io/media/buildly-logo.svg">
    <meta property="og:site_name" content="Buildly">
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://www.buildly.io/articles/${slug}.html">
    <meta property="twitter:title" content="${title}">
    <meta property="twitter:description" content="TODO: Add description for ${title}">
    <meta property="twitter:image" content="https://www.buildly.io/media/buildly-logo.svg">
    
    <!-- Structured Data -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "${title}",
      "description": "TODO: Add description for ${title}",
      "image": "https://www.buildly.io/media/buildly-logo.svg",
      "author": {
        "@type": "Person",
        "name": "Buildly Team",
        "url": "https://www.buildly.io/team.html"
      },
      "publisher": {
        "@type": "Organization",
        "name": "Buildly",
        "logo": {
          "@type": "ImageObject",
          "url": "https://www.buildly.io/media/buildly-logo.svg"
        }
      },
      "datePublished": "${currentDate}",
      "dateModified": "${currentDate}",
      "url": "https://www.buildly.io/articles/${slug}.html"
    }
    </script>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        'buildly': {
                            primary: '#1b5fa3',
                            secondary: '#144a84', 
                            accent: '#f9943b',
                            dark: '#1F2937',
                            light: '#F3F4F6',
                        }
                    },
                    fontFamily: {
                        sans: ['Inter', 'system-ui', 'sans-serif'],
                    },
                }
            }
        }
    </script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../css/style.css">
</head>
<body class="font-sans">
    <!-- Include Navigation -->
    <script>
        // Load navigation include
        fetch('../includes/nav.html')
            .then(response => response.text())
            .then(data => {
                document.body.insertAdjacentHTML('afterbegin', data);
            })
            .catch(error => console.error('Error loading navigation:', error));
    </script>

    <!-- Article Header -->
    <header class="bg-gradient-to-br from-buildly-primary to-buildly-secondary pt-32 pb-16">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center">
                <h1 class="text-4xl md:text-5xl font-bold text-white mb-6">
                    ${title}
                </h1>
                <div class="flex flex-col sm:flex-row items-center justify-center gap-4 text-blue-100">
                    <span class="flex items-center">
                        <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
                        </svg>
                        Buildly Team
                    </span>
                    <span class="flex items-center">
                        <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"></path>
                        </svg>
                        ${currentDate}
                    </span>
                </div>
            </div>
        </div>
    </header>

    <!-- Article Content -->
    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <article class="prose prose-lg max-w-none prose-headings:text-buildly-dark prose-a:text-buildly-primary hover:prose-a:text-buildly-secondary prose-strong:text-buildly-dark prose-p:text-gray-700 prose-p:leading-relaxed">
            
            <!-- Author Byline -->
            <div class="mb-12 pb-8 border-b border-gray-200">
                <h3 class="text-xl font-semibold text-buildly-dark mb-2">By <a href="https://www.buildly.io/team.html" class="text-buildly-primary hover:text-buildly-secondary">Buildly Team</a></h3>
                <p class="text-gray-600 italic">AI-powered product development platform providing superior alternatives to vibe coding with intelligent automation and developer oversight.</p>
            </div>

            <!-- Article Body -->
            <div class="space-y-6">
                ${content || `
                <p class="text-lg text-gray-700 leading-relaxed">Your article content goes here. This template provides a professional, consistent design that matches the Buildly brand with proper paragraph structure.</p>
                
                <p class="text-lg text-gray-700 leading-relaxed">Each paragraph should contain multiple related sentences to create logical content blocks. This improves readability and reduces excessive white space between individual sentences.</p>
                
                <h2 class="text-3xl font-bold text-buildly-dark mb-6 mt-8">Section Heading</h2>
                
                <p class="text-lg text-gray-700 leading-relaxed">Use this structure for well-formatted articles with proper typography and spacing. Remember to group related sentences together into coherent paragraphs rather than breaking every sentence into its own paragraph element.</p>
                
                <blockquote class="border-l-4 border-buildly-accent pl-6 py-4 bg-buildly-light rounded-r-lg my-8">
                    <p class="text-lg text-gray-800 italic">Use blockquotes for important quotes or callouts that deserve special emphasis.</p>
                </blockquote>
                
                <div class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm my-8">
                    <h4 class="text-xl font-semibold text-buildly-dark mb-3">💡 Key Point</h4>
                    <p class="text-gray-700 leading-relaxed">Use cards like this to highlight important information or key takeaways that readers should pay special attention to.</p>
                </div>
                
                <ul class="space-y-3 my-6">
                    <li class="flex items-start">
                        <span class="text-buildly-accent font-bold mr-3">•</span>
                        <span class="text-gray-700">Styled bullet points using Buildly colors</span>
                    </li>
                    <li class="flex items-start">
                        <span class="text-buildly-accent font-bold mr-3">•</span>
                        <span class="text-gray-700">Consistent spacing and typography throughout</span>
                    </li>
                    <li class="flex items-start">
                        <span class="text-buildly-accent font-bold mr-3">•</span>
                        <span class="text-gray-700">Professional design that matches the Buildly brand</span>
                    </li>
                </ul>
                `}
            </div>

            <!-- Call-to-Action Section -->
            <div class="bg-gradient-to-r from-buildly-primary to-buildly-secondary rounded-lg p-8 text-white my-12">
                <h3 class="text-2xl font-semibold mb-4">Ready to Transform Your Development Process?</h3>
                <p class="text-lg leading-relaxed mb-6">Discover how Buildly can help your team build faster with AI-powered automation and intelligent architecture.</p>
                <div class="flex flex-col sm:flex-row gap-4">
                    <a href="https://labs.buildly.io" class="inline-flex items-center justify-center bg-white text-buildly-primary px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors">
                        Try Buildly Labs Free
                    </a>
                    <a href="https://www.buildly.io/use-cases.html" class="inline-flex items-center justify-center border border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-buildly-primary transition-colors">
                        Explore Use Cases
                    </a>
                </div>
            </div>
        </article>
    </main>

    <!-- Footer -->
    <footer class="bg-buildly-dark text-white py-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
                <div class="col-span-1 md:col-span-2">
                    <div class="flex items-center mb-4">
                        <img class="h-8 w-auto" src="../media/buildly-logo.svg" alt="Buildly">
                        <span class="ml-2 text-xl font-bold">Buildly</span>
                    </div>
                    <p class="text-gray-300 mb-4">
                        AI-powered product development platform providing superior alternatives to vibe coding with intelligent automation and developer oversight.
                    </p>
                </div>
                <div>
                    <h3 class="text-lg font-semibold mb-4">Products</h3>
                    <ul class="space-y-2 text-gray-300">
                        <li><a href="../labs.html" class="hover:text-white">Buildly Labs</a></li>
                        <li><a href="../rad-core.html" class="hover:text-white">RAD Core</a></li>
                        <li><a href="https://collab.buildly.io" class="hover:text-white">Collab Hub</a></li>
                    </ul>
                </div>
                <div>
                    <h3 class="text-lg font-semibold mb-4">Resources</h3>
                    <ul class="space-y-2 text-gray-300">
                        <li><a href="../articles.html" class="hover:text-white">Articles</a></li>
                        <li><a href="https://docs.buildly.io" class="hover:text-white">Documentation</a></li>
                        <li><a href="../use-cases.html" class="hover:text-white">Use Cases</a></li>
                    </ul>
                </div>
            </div>
            <div class="border-t border-gray-700 mt-8 pt-8 text-center text-gray-300">
                <p>&copy; 2025 Buildly. All rights reserved.</p>
            </div>
        </div>
    </footer>
</body>
</html>`;
    }

    /**
     * Extract metadata from HTML content
     */
    extractMetadata(content) {
        const metadata = {};
        
        // Extract title
        const titleMatch = content.match(/<title[^>]*>([^<]+)<\/title>/i);
        if (titleMatch) {
            // Remove " - Buildly" suffix if present
            metadata.title = titleMatch[1].replace(/ - Buildly$/, '').trim();
            console.log('📋 Extracted title:', metadata.title);
        } else {
            console.log('⚠️ No title found in content');
        }

        // Extract meta description
        const descMatch = content.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']+)["'][^>]*>/i);
        if (descMatch) {
            // Skip placeholder descriptions
            if (!descMatch[1].startsWith('TODO:')) {
                metadata.description = descMatch[1];
                console.log('📋 Extracted description:', metadata.description);
            }
        } else {
            console.log('⚠️ No description found in content');
        }

        // Extract meta keywords
        const keywordsMatch = content.match(/<meta[^>]*name=["']keywords["'][^>]*content=["']([^"']+)["'][^>]*>/i);
        if (keywordsMatch) {
            // Skip placeholder keywords
            if (!keywordsMatch[1].startsWith('TODO:')) {
                metadata.keywords = keywordsMatch[1].split(',').map(k => k.trim());
                console.log('📋 Extracted keywords:', metadata.keywords);
            }
        } else {
            console.log('⚠️ No keywords found in content');
        }

        // Extract Open Graph data
        const ogTitleMatch = content.match(/<meta[^>]*property=["']og:title["'][^>]*content=["']([^"']+)["'][^>]*>/i);
        if (ogTitleMatch) {
            metadata.ogTitle = ogTitleMatch[1];
        }

        const ogDescMatch = content.match(/<meta[^>]*property=["']og:description["'][^>]*content=["']([^"']+)["'][^>]*>/i);
        if (ogDescMatch) {
            metadata.ogDescription = ogDescMatch[1];
        }

        // Extract article headings
        const headings = [];
        const headingMatches = content.matchAll(/<h([1-6])[^>]*>([^<]+)<\/h[1-6]>/gi);
        for (const match of headingMatches) {
            headings.push({
                level: parseInt(match[1]),
                text: match[2].trim()
            });
        }
        metadata.headings = headings;

        return metadata;
    }

    /**
     * Get file statistics
     */
    getFileStats(content) {
        // Remove HTML tags for word count
        const textContent = content.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
        const words = textContent.split(' ').filter(word => word.length > 0);
        
        return {
            size: content.length,
            words: words.length,
            characters: textContent.length,
            readingTime: Math.ceil(words.length / 200) // Assuming 200 WPM reading speed
        };
    }

    /**
     * Generate filename from title
     */
    generateFileName(title) {
        return title
            .toLowerCase()
            .replace(/[^a-z0-9\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .replace(/^-+|-+$/g, '') + '.html';
    }

    /**
     * Get file name from path
     */
    getFileName(filePath) {
        return filePath.split('/').pop();
    }

    /**
     * Get file type
     */
    getFileType(filePath) {
        const extension = filePath.split('.').pop().toLowerCase();
        return extension || 'unknown';
    }

    /**
     * Resolve URL for file
     */
    resolveUrl(filePath) {
        if (filePath.startsWith('http')) {
            return filePath;
        }
        return `${this.baseUrl}${filePath.startsWith('/') ? '' : '/'}${filePath}`;
    }

    /**
     * Download file
     */
    downloadFile(fileName, content) {
        const blob = new Blob([content], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Cache management
     */
    getFromCache(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }
        return null;
    }

    setCache(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }

    clearCache() {
        this.cache.clear();
    }

    /**
     * Search files by content or metadata
     */
    async searchFiles(query) {
        const files = await this.getFileList();
        const results = [];
        
        const searchQuery = query.toLowerCase();
        
        for (const file of files) {
            let score = 0;
            const matches = [];
            
            // Search in filename
            if (file.name.toLowerCase().includes(searchQuery)) {
                score += 3;
                matches.push('filename');
            }
            
            // Search in title
            if (file.metadata.title && file.metadata.title.toLowerCase().includes(searchQuery)) {
                score += 2;
                matches.push('title');
            }
            
            // Search in description
            if (file.metadata.description && file.metadata.description.toLowerCase().includes(searchQuery)) {
                score += 2;
                matches.push('description');
            }
            
            // Search in keywords
            if (file.metadata.keywords) {
                for (const keyword of file.metadata.keywords) {
                    if (keyword.toLowerCase().includes(searchQuery)) {
                        score += 1;
                        matches.push('keywords');
                        break;
                    }
                }
            }
            
            if (score > 0) {
                results.push({
                    file: file,
                    score: score,
                    matches: matches
                });
            }
        }
        
        // Sort by score (highest first)
        results.sort((a, b) => b.score - a.score);
        
        return results.map(result => result.file);
    }
}

// Global file manager instance
window.fileManager = new FileManager();

// Utility functions
window.loadFiles = async () => {
    return await window.fileManager.getFileList();
};

window.readFileContent = async (filePath) => {
    return await window.fileManager.readFile(filePath);
};

window.saveFileContent = async (filePath, content) => {
    return await window.fileManager.writeFile(filePath, content);
};