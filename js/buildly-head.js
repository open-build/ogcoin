/**
 * ForgeWeb Head JavaScript - Adapted for OGCoin
 * Common utilities and global configuration
 * Version: 0.5.0 (Compatible)
 */

(function() {
    'use strict';

    // Global ForgeWeb configuration for OGCoin
    window.ForgeWeb = window.ForgeWeb || {};
    
    // Set version and basic config
    window.ForgeWeb.version = '0.5.0';
    window.ForgeWeb.appName = 'OGCoin';
    window.ForgeWeb.siteName = 'OGCoin - Open Build Project';
    window.ForgeWeb.apiBase = '/api';
    
    // OGCoin branding colors (compatible with ForgeWeb)
    window.ForgeWeb.colors = {
        primary: '#1b5fa3',
        secondary: '#144a84', 
        accent: '#f9943b',
        dark: '#1F2937',
        light: '#F3F4F6'
    };

    // Site configuration
    window.ForgeWeb.config = {
        github: {
            owner: 'open-build',
            repo: 'ogcoin',
            url: 'https://github.com/open-build/ogcoin'
        },
        social: {
            twitter: '#',
            discord: '#',
            github: 'https://github.com/open-build/ogcoin'
        },
        features: {
            aiEnabled: false,
            socialEnabled: true,
            contactForm: true,
            analytics: false
        }
    };

    // Common utilities
    window.ForgeWeb.utils = {
        
        /**
         * Make API requests with proper error handling
         */
        apiCall: function(endpoint, options = {}) {
            const url = `${window.ForgeWeb.apiBase}/${endpoint}`;
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            
            const config = { ...defaultOptions, ...options };
            
            return fetch(url, config)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`API Error: ${response.status}`);
                    }
                    return response.json();
                })
                .catch(error => {
                    console.error('ForgeWeb API Error:', error);
                    throw error;
                });
        },

        /**
         * Smooth scroll to element
         */
        scrollTo: function(elementId, offset = 80) {
            const element = document.getElementById(elementId.replace('#', ''));
            if (element) {
                const elementTop = element.offsetTop - offset;
                window.scrollTo({
                    top: elementTop,
                    behavior: 'smooth'
                });
            }
        },

        /**
         * Debounce function for performance
         */
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        /**
         * Check if element is in viewport
         */
        isInViewport: function(element) {
            const rect = element.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        },

        /**
         * Format date for display
         */
        formatDate: function(date) {
            return new Date(date).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        },

        /**
         * Copy text to clipboard
         */
        copyToClipboard: function(text) {
            if (navigator.clipboard) {
                return navigator.clipboard.writeText(text);
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                return Promise.resolve();
            }
        }
    };

    // Animation utilities
    window.ForgeWeb.animations = {
        
        /**
         * Fade in elements when they come into view
         */
        observeElements: function(selector = '.fade-in-up') {
            if ('IntersectionObserver' in window) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('fade-in-up');
                            observer.unobserve(entry.target);
                        }
                    });
                }, {
                    threshold: 0.1,
                    rootMargin: '50px'
                });

                document.querySelectorAll(selector).forEach(el => {
                    observer.observe(el);
                });
            }
        },

        /**
         * Animate counter numbers
         */
        animateCounter: function(element, start = 0, end, duration = 2000) {
            const startTime = performance.now();
            const animate = (currentTime) => {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const current = Math.floor(start + (end - start) * progress);
                
                element.textContent = current.toLocaleString();
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                }
            };
            requestAnimationFrame(animate);
        }
    };

    // Initialize ForgeWeb when DOM is ready
    function initForgeWeb() {
        console.log(`🔧 ForgeWeb ${window.ForgeWeb.version} initialized for ${window.ForgeWeb.siteName}`);
        
        // Initialize animations
        window.ForgeWeb.animations.observeElements();
        
        // Log configuration (development only)
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.log('ForgeWeb Config:', window.ForgeWeb.config);
        }
    }

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initForgeWeb);
    } else {
        initForgeWeb();
    }

})();