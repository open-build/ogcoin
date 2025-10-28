/**
 * ForgeWeb Site Generator
 * Generates complete websites from templates and configuration
 */

class SiteGenerator {
    constructor() {
        this.templates = {};
        this.siteConfig = {};
    }

    /**
     * Initialize the site generator with configuration
     */
    async initialize(siteData) {
        this.siteConfig = {
            siteName: siteData.siteName || 'My Website',
            siteDescription: siteData.siteDescription || 'A website built with ForgeWeb',
            siteAuthor: siteData.siteAuthor || 'Website Owner',
            siteUrl: `https://${siteData.githubUsername}.github.io/${siteData.githubRepo}`,
            githubUsername: siteData.githubUsername,
            githubRepo: siteData.githubRepo,
            siteType: siteData.siteType || 'blog',
            currentYear: new Date().getFullYear(),
            includeAbout: siteData.includeAbout !== false,
            includeContact: siteData.includeContact !== false,
            includeBlog: siteData.includeBlog !== false,
            includePortfolio: siteData.includePortfolio === true,
            includeServices: siteData.includeServices === true,
            includeSampleContent: siteData.includeSampleContent !== false
        };

        // Load templates
        await this.loadTemplates();
    }

    /**
     * Load all template files
     */
    async loadTemplates() {
        const templateFiles = [
            'base.html',
            'home-content.html',
            'about-content.html',
            'contact-content.html'
        ];

        for (const file of templateFiles) {
            try {
                const response = await fetch(`/admin/templates/${file}`);
                this.templates[file] = await response.text();
            } catch (error) {
                console.warn(`Could not load template ${file}:`, error);
            }
        }
    }

    /**
     * Generate the complete website
     */
    async generateSite() {
        const pages = [];

        // Generate homepage
        pages.push(this.generateHomePage());

        // Generate additional pages based on configuration
        if (this.siteConfig.includeAbout) {
            pages.push(this.generateAboutPage());
        }

        if (this.siteConfig.includeContact) {
            pages.push(this.generateContactPage());
        }

        if (this.siteConfig.includeBlog) {
            pages.push(this.generateBlogPage());
            
            // Generate sample articles if requested
            if (this.siteConfig.includeSampleContent) {
                pages.push(...this.generateSampleArticles());
            }
        }

        if (this.siteConfig.includePortfolio) {
            pages.push(this.generatePortfolioPage());
        }

        if (this.siteConfig.includeServices) {
            pages.push(this.generateServicesPage());
        }

        // Generate 404 page
        pages.push(this.generate404Page());

        // Generate additional files
        pages.push(this.generateRobotsFile());
        pages.push(this.generateSitemapFile());

        return pages;
    }

    /**
     * Generate homepage
     */
    generateHomePage() {
        const navLinks = this.generateNavLinks();
        const mobileNavLinks = this.generateMobileNavLinks();
        const footerLinks = this.generateFooterLinks();
        const ctaButtons = this.generateCTAButtons();
        const featureCards = this.generateFeatureCards();
        const recentContent = this.generateRecentContent();

        const variables = {
            ...this.siteConfig,
            NAV_LINKS: navLinks,
            MOBILE_NAV_LINKS: mobileNavLinks,
            FOOTER_LINKS: footerLinks,
            CTA_BUTTONS: ctaButtons,
            FEATURE_CARDS: featureCards,
            RECENT_CONTENT: recentContent,
            MAIN_CONTENT: this.processTemplate(this.templates['home-content.html'], {
                FEATURE_CARDS: featureCards,
                RECENT_CONTENT: recentContent
            })
        };

        return {
            filename: 'index.html',
            content: this.processTemplate(this.templates['base.html'], variables)
        };
    }

    /**
     * Generate about page
     */
    generateAboutPage() {
        const navLinks = this.generateNavLinks('about.html');
        const mobileNavLinks = this.generateMobileNavLinks('about.html');
        const footerLinks = this.generateFooterLinks();

        const variables = {
            ...this.siteConfig,
            NAV_LINKS: navLinks,
            MOBILE_NAV_LINKS: mobileNavLinks,
            FOOTER_LINKS: footerLinks,
            CTA_BUTTONS: '<a href="contact.html" class="bg-accent hover:bg-orange-600 text-white font-bold py-3 px-8 rounded-lg">Contact Us</a>',
            MAIN_CONTENT: this.processTemplate(this.templates['about-content.html'], this.siteConfig)
        };

        return {
            filename: 'about.html',
            content: this.processTemplate(this.templates['base.html'], variables)
        };
    }

    /**
     * Generate contact page
     */
    generateContactPage() {
        const navLinks = this.generateNavLinks('contact.html');
        const mobileNavLinks = this.generateMobileNavLinks('contact.html');
        const footerLinks = this.generateFooterLinks();

        const variables = {
            ...this.siteConfig,
            NAV_LINKS: navLinks,
            MOBILE_NAV_LINKS: mobileNavLinks,
            FOOTER_LINKS: footerLinks,
            CTA_BUTTONS: '<a href="about.html" class="bg-primary hover:bg-secondary text-white font-bold py-3 px-8 rounded-lg">Learn More</a>',
            MAIN_CONTENT: this.processTemplate(this.templates['contact-content.html'], this.siteConfig)
        };

        return {
            filename: 'contact.html',
            content: this.processTemplate(this.templates['base.html'], variables)
        };
    }

    /**
     * Generate blog/articles page
     */
    generateBlogPage() {
        const navLinks = this.generateNavLinks('articles.html');
        const mobileNavLinks = this.generateMobileNavLinks('articles.html');
        const footerLinks = this.generateFooterLinks();

        const articlesContent = this.generateArticlesListContent();

        const variables = {
            ...this.siteConfig,
            NAV_LINKS: navLinks,
            MOBILE_NAV_LINKS: mobileNavLinks,
            FOOTER_LINKS: footerLinks,
            CTA_BUTTONS: '<a href="contact.html" class="bg-accent hover:bg-orange-600 text-white font-bold py-3 px-8 rounded-lg">Start Writing</a>',
            MAIN_CONTENT: articlesContent
        };

        return {
            filename: 'articles.html',
            content: this.processTemplate(this.templates['base.html'], variables)
        };
    }

    /**
     * Generate portfolio page
     */
    generatePortfolioPage() {
        const navLinks = this.generateNavLinks('portfolio.html');
        const mobileNavLinks = this.generateMobileNavLinks('portfolio.html');
        const footerLinks = this.generateFooterLinks();

        const portfolioContent = this.generatePortfolioContent();

        const variables = {
            ...this.siteConfig,
            NAV_LINKS: navLinks,
            MOBILE_NAV_LINKS: mobileNavLinks,
            FOOTER_LINKS: footerLinks,
            CTA_BUTTONS: '<a href="contact.html" class="bg-accent hover:bg-orange-600 text-white font-bold py-3 px-8 rounded-lg">Hire Me</a>',
            MAIN_CONTENT: portfolioContent
        };

        return {
            filename: 'portfolio.html',
            content: this.processTemplate(this.templates['base.html'], variables)
        };
    }

    /**
     * Generate services page
     */
    generateServicesPage() {
        const navLinks = this.generateNavLinks('services.html');
        const mobileNavLinks = this.generateMobileNavLinks('services.html');
        const footerLinks = this.generateFooterLinks();

        const servicesContent = this.generateServicesContent();

        const variables = {
            ...this.siteConfig,
            NAV_LINKS: navLinks,
            MOBILE_NAV_LINKS: mobileNavLinks,
            FOOTER_LINKS: footerLinks,
            CTA_BUTTONS: '<a href="contact.html" class="bg-accent hover:bg-orange-600 text-white font-bold py-3 px-8 rounded-lg">Get Started</a>',
            MAIN_CONTENT: servicesContent
        };

        return {
            filename: 'services.html',
            content: this.processTemplate(this.templates['base.html'], variables)
        };
    }

    /**
     * Generate sample articles
     */
    generateSampleArticles() {
        const articles = [];
        const sampleArticles = this.getSampleArticlesData();

        sampleArticles.forEach(article => {
            articles.push({
                filename: `articles/${article.slug}.html`,
                content: this.generateArticleContent(article)
            });
        });

        return articles;
    }

    /**
     * Generate 404 error page
     */
    generate404Page() {
        const navLinks = this.generateNavLinks();
        const mobileNavLinks = this.generateMobileNavLinks();
        const footerLinks = this.generateFooterLinks();

        const notFoundContent = `
        <section class="py-16 bg-white">
            <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                <div class="mb-8">
                    <h1 class="text-6xl font-bold text-primary mb-4">404</h1>
                    <h2 class="text-3xl font-bold text-gray-900 mb-4">Page Not Found</h2>
                    <p class="text-xl text-gray-600 mb-8">
                        The page you're looking for doesn't exist or has been moved.
                    </p>
                    <div class="flex flex-col sm:flex-row gap-4 justify-center">
                        <a href="/" class="bg-primary hover:bg-secondary text-white font-bold py-3 px-8 rounded-lg">
                            Go Home
                        </a>
                        <a href="contact.html" class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-3 px-8 rounded-lg">
                            Contact Us
                        </a>
                    </div>
                </div>
            </div>
        </section>`;

        const variables = {
            ...this.siteConfig,
            NAV_LINKS: navLinks,
            MOBILE_NAV_LINKS: mobileNavLinks,
            FOOTER_LINKS: footerLinks,
            CTA_BUTTONS: '',
            MAIN_CONTENT: notFoundContent
        };

        return {
            filename: '404.html',
            content: this.processTemplate(this.templates['base.html'], variables)
        };
    }

    /**
     * Generate robots.txt file
     */
    generateRobotsFile() {
        const robotsContent = `User-agent: *
Allow: /

Sitemap: ${this.siteConfig.siteUrl}/sitemap.xml`;

        return {
            filename: 'robots.txt',
            content: robotsContent
        };
    }

    /**
     * Generate sitemap.xml file
     */
    generateSitemapFile() {
        const pages = ['', 'about.html', 'contact.html'];
        
        if (this.siteConfig.includeBlog) pages.push('articles.html');
        if (this.siteConfig.includePortfolio) pages.push('portfolio.html');
        if (this.siteConfig.includeServices) pages.push('services.html');

        const urls = pages.map(page => {
            const url = page ? `${this.siteConfig.siteUrl}/${page}` : this.siteConfig.siteUrl;
            return `  <url>
    <loc>${url}</loc>
    <changefreq>weekly</changefreq>
    <priority>${page === '' ? '1.0' : '0.8'}</priority>
  </url>`;
        }).join('\n');

        const sitemapContent = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`;

        return {
            filename: 'sitemap.xml',
            content: sitemapContent
        };
    }

    /**
     * Generate navigation links
     */
    generateNavLinks(currentPage = 'index.html') {
        const links = [];
        
        if (this.siteConfig.includeAbout) {
            const isActive = currentPage === 'about.html';
            links.push(`<a href="about.html" class="text-gray-700 hover:text-primary px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'border-b-2 border-primary text-primary' : ''}">About</a>`);
        }
        
        if (this.siteConfig.includeBlog) {
            const isActive = currentPage === 'articles.html';
            links.push(`<a href="articles.html" class="text-gray-700 hover:text-primary px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'border-b-2 border-primary text-primary' : ''}">Articles</a>`);
        }
        
        if (this.siteConfig.includePortfolio) {
            const isActive = currentPage === 'portfolio.html';
            links.push(`<a href="portfolio.html" class="text-gray-700 hover:text-primary px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'border-b-2 border-primary text-primary' : ''}">Portfolio</a>`);
        }
        
        if (this.siteConfig.includeServices) {
            const isActive = currentPage === 'services.html';
            links.push(`<a href="services.html" class="text-gray-700 hover:text-primary px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'border-b-2 border-primary text-primary' : ''}">Services</a>`);
        }
        
        if (this.siteConfig.includeContact) {
            const isActive = currentPage === 'contact.html';
            links.push(`<a href="contact.html" class="text-gray-700 hover:text-primary px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'border-b-2 border-primary text-primary' : ''}">Contact</a>`);
        }
        
        return links.join('\n                        ');
    }

    /**
     * Generate mobile navigation links
     */
    generateMobileNavLinks(currentPage = 'index.html') {
        const links = [];
        
        if (this.siteConfig.includeAbout) {
            const isActive = currentPage === 'about.html';
            links.push(`<a href="about.html" class="text-gray-700 hover:text-primary block px-3 py-2 rounded-md text-base font-medium ${isActive ? 'text-primary' : ''}">About</a>`);
        }
        
        if (this.siteConfig.includeBlog) {
            const isActive = currentPage === 'articles.html';
            links.push(`<a href="articles.html" class="text-gray-700 hover:text-primary block px-3 py-2 rounded-md text-base font-medium ${isActive ? 'text-primary' : ''}">Articles</a>`);
        }
        
        if (this.siteConfig.includePortfolio) {
            const isActive = currentPage === 'portfolio.html';
            links.push(`<a href="portfolio.html" class="text-gray-700 hover:text-primary block px-3 py-2 rounded-md text-base font-medium ${isActive ? 'text-primary' : ''}">Portfolio</a>`);
        }
        
        if (this.siteConfig.includeServices) {
            const isActive = currentPage === 'services.html';
            links.push(`<a href="services.html" class="text-gray-700 hover:text-primary block px-3 py-2 rounded-md text-base font-medium ${isActive ? 'text-primary' : ''}">Services</a>`);
        }
        
        if (this.siteConfig.includeContact) {
            const isActive = currentPage === 'contact.html';
            links.push(`<a href="contact.html" class="text-gray-700 hover:text-primary block px-3 py-2 rounded-md text-base font-medium ${isActive ? 'text-primary' : ''}">Contact</a>`);
        }
        
        return links.join('\n                ');
    }

    /**
     * Generate footer links
     */
    generateFooterLinks() {
        const links = [];
        
        links.push('<li><a href="index.html" class="hover:text-accent">Home</a></li>');
        
        if (this.siteConfig.includeAbout) {
            links.push('<li><a href="about.html" class="hover:text-accent">About</a></li>');
        }
        
        if (this.siteConfig.includeBlog) {
            links.push('<li><a href="articles.html" class="hover:text-accent">Articles</a></li>');
        }
        
        if (this.siteConfig.includeContact) {
            links.push('<li><a href="contact.html" class="hover:text-accent">Contact</a></li>');
        }
        
        return links.join('\n                        ');
    }

    /**
     * Generate call-to-action buttons for homepage
     */
    generateCTAButtons() {
        const buttons = [];
        
        if (this.siteConfig.includeContact) {
            buttons.push('<a href="contact.html" class="bg-accent hover:bg-orange-600 text-white font-bold py-3 px-8 rounded-lg">Get Started</a>');
        }
        
        if (this.siteConfig.includeAbout) {
            buttons.push('<a href="about.html" class="bg-white hover:bg-gray-100 text-primary font-bold py-3 px-8 rounded-lg border-2 border-white">Learn More</a>');
        }
        
        return buttons.join('\n                    ');
    }

    /**
     * Generate feature cards for homepage
     */
    generateFeatureCards() {
        const features = this.getFeaturesByType();
        
        return features.map(feature => `
            <div class="card-hover bg-white p-6 rounded-lg shadow-md">
                <div class="w-12 h-12 bg-primary rounded-lg flex items-center justify-center mb-4">
                    ${feature.icon}
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-2">${feature.title}</h3>
                <p class="text-gray-600">${feature.description}</p>
            </div>
        `).join('\n            ');
    }

    /**
     * Generate recent content section
     */
    generateRecentContent() {
        if (!this.siteConfig.includeBlog || !this.siteConfig.includeSampleContent) {
            return '';
        }

        const articles = this.getSampleArticlesData().slice(0, 3);
        
        const articleCards = articles.map(article => `
            <div class="card-hover bg-white rounded-lg shadow-md overflow-hidden">
                <div class="p-6">
                    <div class="flex items-center text-sm text-gray-500 mb-2">
                        <span>${article.category}</span>
                        <span class="mx-2">•</span>
                        <span>${article.date}</span>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-900 mb-2">
                        <a href="articles/${article.slug}.html" class="hover:text-primary">${article.title}</a>
                    </h3>
                    <p class="text-gray-600 mb-4">${article.excerpt}</p>
                    <a href="articles/${article.slug}.html" class="text-primary hover:text-secondary font-medium">
                        Read more →
                    </a>
                </div>
            </div>
        `).join('\n            ');

        return `
        <div class="mb-16">
            <div class="text-center mb-12">
                <h2 class="text-3xl font-bold text-gray-900 mb-4">Latest Articles</h2>
                <p class="text-xl text-gray-600">Discover insights, tips, and stories from our team.</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                ${articleCards}
            </div>
            <div class="text-center mt-8">
                <a href="articles.html" class="bg-primary hover:bg-secondary text-white font-bold py-3 px-8 rounded-lg">
                    View All Articles
                </a>
            </div>
        </div>`;
    }

    /**
     * Get features based on site type
     */
    getFeaturesByType() {
        const featuresByType = {
            blog: [
                {
                    title: 'Quality Content',
                    description: 'Well-researched articles and insights that provide real value to our readers.',
                    icon: '<svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
                },
                {
                    title: 'Regular Updates',
                    description: 'Fresh content published regularly to keep you informed and engaged.',
                    icon: '<svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"></path></svg>'
                },
                {
                    title: 'Community Focus',
                    description: 'Building a community around shared interests and meaningful discussions.',
                    icon: '<svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20"><path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"></path></svg>'
                }
            ],
            business: [
                {
                    title: 'Expert Solutions',
                    description: 'Professional services tailored to meet your specific business needs.',
                    icon: '<svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.243.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>'
                },
                {
                    title: 'Proven Results',
                    description: 'Track record of success helping businesses achieve their goals.',
                    icon: '<svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>'
                },
                {
                    title: 'Customer Support',
                    description: 'Dedicated support team ready to help you succeed every step of the way.',
                    icon: '<svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"></path></svg>'
                }
            ],
            portfolio: [
                {
                    title: 'Creative Design',
                    description: 'Innovative and visually stunning designs that capture attention and engage audiences.',
                    icon: '<svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd"></path></svg>'
                },
                {
                    title: 'Technical Skills',
                    description: 'Proficient in the latest technologies and best practices for modern development.',
                    icon: '<svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>'
                },
                {
                    title: 'Client Focus',
                    description: 'Dedicated to understanding client needs and delivering solutions that exceed expectations.',
                    icon: '<svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20"><path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z"></path></svg>'
                }
            ]
        };

        return featuresByType[this.siteConfig.siteType] || featuresByType.blog;
    }

    /**
     * Get sample articles data
     */
    getSampleArticlesData() {
        const currentDate = new Date();
        
        return [
            {
                title: 'Getting Started with ForgeWeb',
                slug: 'getting-started-with-forgeweb',
                excerpt: 'Learn how to create amazing websites with ForgeWeb\'s AI-powered site generator.',
                content: 'ForgeWeb makes it easy to create professional websites with AI assistance...',
                category: 'Tutorial',
                date: new Date(currentDate.setDate(currentDate.getDate() - 1)).toLocaleDateString(),
                author: this.siteConfig.siteAuthor
            },
            {
                title: 'The Power of Static Sites',
                slug: 'power-of-static-sites',
                excerpt: 'Discover why static sites are the future of web development and how they can benefit your project.',
                content: 'Static sites offer unparalleled performance, security, and simplicity...',
                category: 'Web Development',
                date: new Date(currentDate.setDate(currentDate.getDate() - 5)).toLocaleDateString(),
                author: this.siteConfig.siteAuthor
            },
            {
                title: 'AI-Assisted Content Creation',
                slug: 'ai-assisted-content-creation',
                excerpt: 'How artificial intelligence is revolutionizing the way we create and manage website content.',
                content: 'AI tools are transforming content creation by providing intelligent suggestions...',
                category: 'Technology',
                date: new Date(currentDate.setDate(currentDate.getDate() - 10)).toLocaleDateString(),
                author: this.siteConfig.siteAuthor
            }
        ];
    }

    /**
     * Process template with variables
     */
    processTemplate(template, variables) {
        if (!template) return '';
        
        let processed = template;
        for (const [key, value] of Object.entries(variables)) {
            const placeholder = new RegExp(`{{${key}}}`, 'g');
            processed = processed.replace(placeholder, value || '');
        }
        return processed;
    }

    /**
     * Generate articles list content
     */
    generateArticlesListContent() {
        if (!this.siteConfig.includeSampleContent) {
            return `
            <section class="py-16 bg-white">
                <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="text-center">
                        <h1 class="text-4xl font-bold text-gray-900 mb-6">Articles</h1>
                        <p class="text-xl text-gray-600 mb-12">Welcome to our blog. Start creating amazing content!</p>
                        <div class="bg-gray-50 rounded-lg p-12">
                            <p class="text-gray-500">No articles yet. Use the ForgeWeb admin to create your first post!</p>
                        </div>
                    </div>
                </div>
            </section>`;
        }

        const articles = this.getSampleArticlesData();
        const articleList = articles.map(article => `
            <article class="card-hover bg-white rounded-lg shadow-md overflow-hidden">
                <div class="p-6">
                    <div class="flex items-center text-sm text-gray-500 mb-2">
                        <span>${article.category}</span>
                        <span class="mx-2">•</span>
                        <span>${article.date}</span>
                        <span class="mx-2">•</span>
                        <span>By ${article.author}</span>
                    </div>
                    <h2 class="text-2xl font-bold text-gray-900 mb-3">
                        <a href="articles/${article.slug}.html" class="hover:text-primary">${article.title}</a>
                    </h2>
                    <p class="text-gray-600 mb-4">${article.excerpt}</p>
                    <a href="articles/${article.slug}.html" class="text-primary hover:text-secondary font-medium">
                        Read more →
                    </a>
                </div>
            </article>
        `).join('\n            ');

        return `
        <section class="py-16 bg-white">
            <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="text-center mb-12">
                    <h1 class="text-4xl font-bold text-gray-900 mb-6">Articles</h1>
                    <p class="text-xl text-gray-600">Insights, tutorials, and stories from our team.</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    ${articleList}
                </div>
            </div>
        </section>`;
    }

    /**
     * Generate individual article content
     */
    generateArticleContent(article) {
        const navLinks = this.generateNavLinks();
        const mobileNavLinks = this.generateMobileNavLinks();
        const footerLinks = this.generateFooterLinks();

        const articleContent = `
        <article class="py-16 bg-white">
            <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                <header class="mb-8">
                    <div class="text-center">
                        <div class="flex items-center justify-center text-sm text-gray-500 mb-4">
                            <span>${article.category}</span>
                            <span class="mx-2">•</span>
                            <span>${article.date}</span>
                            <span class="mx-2">•</span>
                            <span>By ${article.author}</span>
                        </div>
                        <h1 class="text-4xl font-bold text-gray-900 mb-4">${article.title}</h1>
                        <p class="text-xl text-gray-600">${article.excerpt}</p>
                    </div>
                </header>
                
                <div class="prose prose-lg max-w-none">
                    <p>Welcome to this comprehensive guide on ${article.title.toLowerCase()}. In this article, we'll explore the key concepts, best practices, and practical examples that will help you understand and implement these ideas effectively.</p>
                    
                    <h2>Introduction</h2>
                    <p>${article.content}</p>
                    
                    <h2>Key Benefits</h2>
                    <ul>
                        <li>Improved performance and user experience</li>
                        <li>Better security and reliability</li>
                        <li>Easier maintenance and updates</li>
                        <li>Cost-effective solutions</li>
                    </ul>
                    
                    <h2>Getting Started</h2>
                    <p>To begin implementing these concepts, follow these steps:</p>
                    <ol>
                        <li>Assess your current situation and requirements</li>
                        <li>Plan your approach and timeline</li>
                        <li>Start with small, manageable changes</li>
                        <li>Monitor progress and adjust as needed</li>
                    </ol>
                    
                    <h2>Conclusion</h2>
                    <p>By following the principles outlined in this article, you'll be well-equipped to tackle your next project with confidence. Remember that success comes from consistent effort and continuous learning.</p>
                </div>
                
                <div class="mt-12 pt-8 border-t border-gray-200">
                    <div class="flex items-center justify-between">
                        <a href="../articles.html" class="text-primary hover:text-secondary font-medium">
                            ← Back to Articles
                        </a>
                        <div class="flex space-x-4">
                            <a href="../contact.html" class="bg-primary hover:bg-secondary text-white px-4 py-2 rounded">
                                Contact Author
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </article>`;

        const variables = {
            ...this.siteConfig,
            NAV_LINKS: navLinks,
            MOBILE_NAV_LINKS: mobileNavLinks,
            FOOTER_LINKS: footerLinks,
            CTA_BUTTONS: '',
            MAIN_CONTENT: articleContent
        };

        return this.processTemplate(this.templates['base.html'], variables);
    }

    /**
     * Generate portfolio content
     */
    generatePortfolioContent() {
        return `
        <section class="py-16 bg-white">
            <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="text-center mb-12">
                    <h1 class="text-4xl font-bold text-gray-900 mb-6">Portfolio</h1>
                    <p class="text-xl text-gray-600">A showcase of our work and projects.</p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <!-- Project 1 -->
                    <div class="card-hover bg-white rounded-lg shadow-md overflow-hidden">
                        <div class="h-48 bg-gray-200 flex items-center justify-center">
                            <span class="text-gray-500">Project Image</span>
                        </div>
                        <div class="p-6">
                            <h3 class="text-xl font-semibold text-gray-900 mb-2">Website Redesign</h3>
                            <p class="text-gray-600 mb-4">Complete redesign of a corporate website with modern UI/UX principles.</p>
                            <div class="flex flex-wrap gap-2 mb-4">
                                <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">Design</span>
                                <span class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Development</span>
                            </div>
                            <a href="#" class="text-primary hover:text-secondary font-medium">View Project →</a>
                        </div>
                    </div>
                    
                    <!-- Project 2 -->
                    <div class="card-hover bg-white rounded-lg shadow-md overflow-hidden">
                        <div class="h-48 bg-gray-200 flex items-center justify-center">
                            <span class="text-gray-500">Project Image</span>
                        </div>
                        <div class="p-6">
                            <h3 class="text-xl font-semibold text-gray-900 mb-2">E-commerce Platform</h3>
                            <p class="text-gray-600 mb-4">Custom e-commerce solution with advanced features and integrations.</p>
                            <div class="flex flex-wrap gap-2 mb-4">
                                <span class="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">E-commerce</span>
                                <span class="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">JavaScript</span>
                            </div>
                            <a href="#" class="text-primary hover:text-secondary font-medium">View Project →</a>
                        </div>
                    </div>
                    
                    <!-- Project 3 -->
                    <div class="card-hover bg-white rounded-lg shadow-md overflow-hidden">
                        <div class="h-48 bg-gray-200 flex items-center justify-center">
                            <span class="text-gray-500">Project Image</span>
                        </div>
                        <div class="p-6">
                            <h3 class="text-xl font-semibold text-gray-900 mb-2">Mobile App</h3>
                            <p class="text-gray-600 mb-4">Cross-platform mobile application with real-time features.</p>
                            <div class="flex flex-wrap gap-2 mb-4">
                                <span class="px-2 py-1 bg-red-100 text-red-800 text-xs rounded">Mobile</span>
                                <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">React Native</span>
                            </div>
                            <a href="#" class="text-primary hover:text-secondary font-medium">View Project →</a>
                        </div>
                    </div>
                </div>
            </div>
        </section>`;
    }

    /**
     * Generate services content
     */
    generateServicesContent() {
        return `
        <section class="py-16 bg-white">
            <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="text-center mb-12">
                    <h1 class="text-4xl font-bold text-gray-900 mb-6">Our Services</h1>
                    <p class="text-xl text-gray-600">Professional solutions tailored to your needs.</p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <!-- Service 1 -->
                    <div class="text-center">
                        <div class="w-16 h-16 bg-primary rounded-lg flex items-center justify-center mx-auto mb-4">
                            <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path>
                            </svg>
                        </div>
                        <h3 class="text-xl font-semibold text-gray-900 mb-2">Web Development</h3>
                        <p class="text-gray-600 mb-4">Custom websites and web applications built with modern technologies.</p>
                        <ul class="text-sm text-gray-500 space-y-1 mb-6">
                            <li>Responsive design</li>
                            <li>Modern frameworks</li>
                            <li>SEO optimization</li>
                        </ul>
                        <a href="contact.html" class="text-primary hover:text-secondary font-medium">Learn More →</a>
                    </div>
                    
                    <!-- Service 2 -->
                    <div class="text-center">
                        <div class="w-16 h-16 bg-primary rounded-lg flex items-center justify-center mx-auto mb-4">
                            <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd"></path>
                            </svg>
                        </div>
                        <h3 class="text-xl font-semibold text-gray-900 mb-2">Design Services</h3>
                        <p class="text-gray-600 mb-4">Creative design solutions that capture attention and engage users.</p>
                        <ul class="text-sm text-gray-500 space-y-1 mb-6">
                            <li>Brand identity</li>
                            <li>UI/UX design</li>
                            <li>Graphic design</li>
                        </ul>
                        <a href="contact.html" class="text-primary hover:text-secondary font-medium">Learn More →</a>
                    </div>
                    
                    <!-- Service 3 -->
                    <div class="text-center">
                        <div class="w-16 h-16 bg-primary rounded-lg flex items-center justify-center mx-auto mb-4">
                            <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"></path>
                            </svg>
                        </div>
                        <h3 class="text-xl font-semibold text-gray-900 mb-2">Consulting</h3>
                        <p class="text-gray-600 mb-4">Expert guidance to help you make the right technology decisions.</p>
                        <ul class="text-sm text-gray-500 space-y-1 mb-6">
                            <li>Strategy planning</li>
                            <li>Technical audits</li>
                            <li>Performance optimization</li>
                        </ul>
                        <a href="contact.html" class="text-primary hover:text-secondary font-medium">Learn More →</a>
                    </div>
                </div>
            </div>
        </section>`;
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SiteGenerator;
}