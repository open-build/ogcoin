/**
 * Configuration Management for Buildly AI Content Manager
 * Handles storing and retrieving user preferences and API keys
 */

class ConfigManager {
    constructor() {
        this.configKey = 'buildly-ai-config';
        this.siteConfigKey = 'site-config';
        this.siteConfig = null;
        this.defaultConfig = {
            aiProviders: {
                ollama: {
                    enabled: true,
                    endpoint: 'http://localhost:11434',
                    defaultModel: 'deepseek-coder-v2:latest',
                    models: [], // Will be populated dynamically
                    timeout: 30000
                },
                openai: {
                    enabled: false,
                    apiKey: '',
                    endpoint: 'https://api.openai.com/v1',
                    defaultModel: 'gpt-3.5-turbo',
                    models: ['gpt-4-turbo-preview', 'gpt-4', 'gpt-3.5-turbo', 'gpt-3.5-turbo-16k'],
                    timeout: 30000
                },
                gemini: {
                    enabled: false,
                    apiKey: '',
                    endpoint: 'https://generativelanguage.googleapis.com/v1',
                    defaultModel: 'gemini-pro',
                    models: ['gemini-pro', 'gemini-pro-vision'],
                    timeout: 30000
                }
            },
            content: {
                defaultTemplate: 'article',
                autoSave: true,
                autoSaveInterval: 30000, // 30 seconds
                backupEnabled: true,
                maxBackups: 10
            },
            social: {
                autoGenerate: true,
                platforms: ['twitter', 'linkedin', 'facebook'],
                hashtagSuggestions: true,
                maxHashtags: 5
            },
            security: {
                encryptApiKeys: true,
                sessionTimeout: 3600000, // 1 hour
                requireAuth: false
            },
            ui: {
                theme: 'light',
                editorFontSize: 14,
                showLineNumbers: true,
                wordWrap: true
            }
        };
    }

    /**
     * Load configuration from localStorage
     */
    load() {
        try {
            const stored = localStorage.getItem(this.configKey);
            if (stored) {
                const config = JSON.parse(stored);
                return this.mergeConfig(this.defaultConfig, config);
            }
        } catch (error) {
            console.error('Error loading configuration:', error);
        }
        return this.defaultConfig;
    }

    /**
     * Save configuration to localStorage  
     */
    save(config) {
        try {
            const configToSave = this.sanitizeConfig(config);
            localStorage.setItem(this.configKey, JSON.stringify(configToSave));
            return true;
        } catch (error) {
            console.error('Error saving configuration:', error);
            return false;
        }
    }

    /**
     * Get a specific configuration value
     */
    get(path) {
        const config = this.load();
        return this.getNestedValue(config, path);
    }

    /**
     * Set a specific configuration value
     */
    set(path, value) {
        const config = this.load();
        this.setNestedValue(config, path, value);
        return this.save(config);
    }

    /**
     * Reset configuration to defaults
     */
    reset() {
        localStorage.removeItem(this.configKey);
        return this.defaultConfig;
    }

    /**
     * Encrypt API keys before storage
     */
    encryptApiKey(key) {
        if (!key || typeof key !== 'string') return '';
        
        // Simple base64 encoding for basic obfuscation
        // In production, use proper encryption
        return btoa(key);
    }

    /**
     * Decrypt API keys after retrieval
     */
    decryptApiKey(encryptedKey) {
        if (!encryptedKey || typeof encryptedKey !== 'string') return '';
        
        try {
            return atob(encryptedKey);
        } catch (error) {
            console.error('Error decrypting API key:', error);
            return '';
        }
    }

    /**
     * Merge default config with user config
     */
    mergeConfig(defaultConfig, userConfig) {
        const merged = JSON.parse(JSON.stringify(defaultConfig));
        
        for (const key in userConfig) {
            if (userConfig.hasOwnProperty(key)) {
                if (typeof userConfig[key] === 'object' && !Array.isArray(userConfig[key])) {
                    merged[key] = this.mergeConfig(merged[key] || {}, userConfig[key]);
                } else {
                    merged[key] = userConfig[key];
                }
            }
        }
        
        return merged;
    }

    /**
     * Sanitize configuration before saving
     */
    sanitizeConfig(config) {
        const sanitized = JSON.parse(JSON.stringify(config));
        
        // Encrypt API keys if encryption is enabled
        if (sanitized.security?.encryptApiKeys) {
            if (sanitized.aiProviders?.openai?.apiKey) {
                sanitized.aiProviders.openai.apiKey = this.encryptApiKey(
                    sanitized.aiProviders.openai.apiKey
                );
            }
            if (sanitized.aiProviders?.gemini?.apiKey) {
                sanitized.aiProviders.gemini.apiKey = this.encryptApiKey(
                    sanitized.aiProviders.gemini.apiKey
                );
            }
        }
        
        return sanitized;
    }

    /**
     * Get nested value from object using dot notation
     */
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => {
            return current && current[key] !== undefined ? current[key] : undefined;
        }, obj);
    }

    /**
     * Set nested value in object using dot notation
     */
    setNestedValue(obj, path, value) {
        const keys = path.split('.');
        const lastKey = keys.pop();
        const target = keys.reduce((current, key) => {
            if (!current[key] || typeof current[key] !== 'object') {
                current[key] = {};
            }
            return current[key];
        }, obj);
        
        target[lastKey] = value;
    }

    /**
     * Validate configuration
     */
    validate(config) {
        const errors = [];

        // Validate AI providers
        if (config.aiProviders) {
            for (const [provider, settings] of Object.entries(config.aiProviders)) {
                if (settings.enabled) {
                    if (!settings.endpoint) {
                        errors.push(`${provider}: endpoint is required`);
                    }
                    if (!settings.defaultModel) {
                        errors.push(`${provider}: defaultModel is required`);
                    }
                    if (provider !== 'ollama' && !settings.apiKey) {
                        errors.push(`${provider}: API key is required when enabled`);
                    }
                }
            }
        }

        // Validate content settings
        if (config.content) {
            if (config.content.autoSaveInterval < 5000) {
                errors.push('autoSaveInterval must be at least 5 seconds');
            }
            if (config.content.maxBackups < 1) {
                errors.push('maxBackups must be at least 1');
            }
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    /**
     * Export configuration for backup
     */
    export() {
        const config = this.load();
        
        // Remove sensitive data from export
        const exportConfig = JSON.parse(JSON.stringify(config));
        if (exportConfig.aiProviders?.openai?.apiKey) {
            exportConfig.aiProviders.openai.apiKey = '[REDACTED]';
        }
        if (exportConfig.aiProviders?.gemini?.apiKey) {
            exportConfig.aiProviders.gemini.apiKey = '[REDACTED]';
        }
        
        return exportConfig;
    }

    /**
     * Import configuration from backup
     */
    import(configData) {
        try {
            const validation = this.validate(configData);
            if (!validation.isValid) {
                throw new Error('Invalid configuration: ' + validation.errors.join(', '));
            }
            
            return this.save(configData);
        } catch (error) {
            console.error('Error importing configuration:', error);
            return false;
        }
    }

    /**
     * Get configuration for a specific AI provider with decrypted keys
     */
    async getProviderConfig(provider) {
        const config = this.load();
        const providerConfig = config.aiProviders?.[provider];
        
        if (!providerConfig) {
            return null;
        }

        // For Ollama, discover models if none are configured
        if (provider === 'ollama' && (!providerConfig.models || providerConfig.models.length === 0)) {
            await this.discoverOllamaModels();
            // Reload config after discovery
            const updatedConfig = this.load();
            const updatedProviderConfig = updatedConfig.aiProviders?.[provider];
            if (updatedProviderConfig) {
                Object.assign(providerConfig, updatedProviderConfig);
            }
        }

        // Decrypt API key if needed
        if (providerConfig.apiKey && config.security?.encryptApiKeys) {
            providerConfig.apiKey = this.decryptApiKey(providerConfig.apiKey);
        }

        return providerConfig;
    }

    /**
     * Discover available Ollama models dynamically
     */
    async discoverOllamaModels() {
        const config = this.load();
        const ollamaConfig = config.aiProviders?.ollama;
        
        if (!ollamaConfig || !ollamaConfig.enabled) {
            return [];
        }

        try {
            const response = await fetch(`${ollamaConfig.endpoint}/api/tags`, {
                method: 'GET',
                timeout: 5000
            });

            if (!response.ok) {
                console.warn('Failed to fetch Ollama models:', response.statusText);
                return [];
            }

            const data = await response.json();
            const models = data.models?.map(m => m.name) || [];
            
            // Update the config with discovered models
            if (models.length > 0) {
                config.aiProviders.ollama.models = models;
                
                // Set a better default model if current default isn't available
                if (!models.includes(ollamaConfig.defaultModel)) {
                    // Prefer DeepSeek Coder for coding tasks, or first available model
                    const preferredModel = models.find(m => m.includes('deepseek-coder')) || models[0];
                    config.aiProviders.ollama.defaultModel = preferredModel;
                }
                
                this.save(config);
                console.log(`✅ Discovered ${models.length} Ollama models:`, models);
            }

            return models;
        } catch (error) {
            console.warn('Error discovering Ollama models:', error.message);
            return [];
        }
    }

    /**
     * Check if any AI provider is configured and enabled
     */
    hasEnabledProvider() {
        const config = this.load();
        return Object.values(config.aiProviders || {}).some(provider => provider.enabled);
    }

    /**
     * Get list of enabled providers
     */
    getEnabledProviders() {
        const config = this.load();
        return Object.entries(config.aiProviders || {})
            .filter(([_, provider]) => provider.enabled)
            .map(([name, _]) => name);
    }

    /**
     * Load site-specific configuration
     */
    async loadSiteConfig() {
        try {
            const response = await fetch('/admin/site-config.json');
            if (response.ok) {
                this.siteConfig = await response.json();
                console.log('✅ Site configuration loaded:', this.siteConfig.site.name);
            } else {
                console.log('⚠️  No site-config.json found, using defaults');
                this.siteConfig = this.getDefaultSiteConfig();
            }
        } catch (error) {
            console.log('⚠️  Failed to load site config:', error);
            this.siteConfig = this.getDefaultSiteConfig();
        }
    }

    /**
     * Get default site configuration
     */
    getDefaultSiteConfig() {
        return {
            site: {
                name: "Website",
                url: window.location.origin,
                description: "Content management system",
                logo: "/favicon.ico"
            },
            content: {
                articlesFolder: "articles/",
                indexFile: "articles.html",
                defaultCategory: "General",
                categories: [
                    {"id": "General", "name": "General", "color": "blue-500"}
                ],
                folders: [
                    {"id": "articles/", "name": "articles/"},
                    {"id": "", "name": "root folder"}
                ]
            },
            branding: {
                primaryColor: "#3b82f6",
                secondaryColor: "#1e40af",
                accentColor: "#f59e0b"
            },
            social: {
                defaultHashtags: ["#Content", "#Blog"],
                platforms: {
                    twitter: { enabled: true },
                    linkedin: { enabled: true },
                    facebook: { enabled: true }
                }
            }
        };
    }

    /**
     * Get site configuration
     */
    getSiteConfig() {
        return this.siteConfig || this.getDefaultSiteConfig();
    }

    /**
     * Initialize configuration (async)
     */
    async initialize() {
        await this.loadSiteConfig();
        console.log('🔧 Configuration initialized');
    }
}

// Global configuration instance
window.configManager = new ConfigManager();

// Utility functions for common operations
window.loadConfiguration = () => window.configManager.load();
window.saveConfiguration = (config) => window.configManager.save(config);
window.getConfig = (path) => window.configManager.get(path);
window.setConfig = (path, value) => window.configManager.set(path, value);