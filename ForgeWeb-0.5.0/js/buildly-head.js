/**
 * Buildly Head JavaScript
 * Common utilities and global configuration for ForgeWeb
 * Version: 0.5.0
 */

(function() {
    'use strict';

    // Global ForgeWeb configuration
    window.ForgeWeb = window.ForgeWeb || {};
    
    // Set version and basic config
    window.ForgeWeb.version = '0.5.0';
    window.ForgeWeb.appName = 'ForgeWeb';
    window.ForgeWeb.apiBase = '/api';
    
    // Buildly branding colors
    window.ForgeWeb.colors = {
        primary: '#1b5fa3',
        secondary: '#f9943b', 
        accent: '#f9943b',
        dark: '#1F2937'
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
         * Show notification to user
         */
        notify: function(message, type = 'info') {
            console.log(`[${type.toUpperCase()}] ${message}`);
            
            // Try to show in UI if notification area exists
            const notificationArea = document.getElementById('notifications');
            if (notificationArea) {
                const notification = document.createElement('div');
                notification.className = `notification notification-${type}`;
                notification.textContent = message;
                notificationArea.appendChild(notification);
                
                // Auto-remove after 5 seconds
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 5000);
            }
        },

        /**
         * Format file sizes
         */
        formatBytes: function(bytes, decimals = 2) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const dm = decimals < 0 ? 0 : decimals;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
        },

        /**
         * Debounce function calls
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
        }
    };

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log(`ForgeWeb ${window.ForgeWeb.version} initialized`);
        
        // Set up global error handling
        window.addEventListener('error', function(e) {
            console.error('ForgeWeb Error:', e.error);
        });

        // Add ForgeWeb CSS variables to root
        const root = document.documentElement;
        Object.entries(window.ForgeWeb.colors).forEach(([key, value]) => {
            root.style.setProperty(`--forgeweb-${key}`, value);
        });
    });

})();