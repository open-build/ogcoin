/**
 * Main Application Controller for Buildly AI Content Manager
 * Coordinates between different modules and manages UI state
 */

class App {
    constructor() {
        this.isInitialized = false;
        this.currentView = 'dashboard';
        this.notifications = [];
        this.recentActivity = [];
        
        // Bind methods
        this.showNotification = this.showNotification.bind(this);
        this.hideNotification = this.hideNotification.bind(this);
    }

    /**
     * Initialize the application
     */
    async initialize() {
        if (this.isInitialized) return;
        
        try {
            console.log('Initializing Buildly AI Content Manager...');
            
            // Load configuration
            await this.loadConfiguration();
            
            // Discover available AI models
            await this.discoverAIModels();
            
            // Initialize UI components
            this.initializeUI();
            
            // Check AI service status
            await this.checkAIServiceStatus();
            
            // Load recent activity
            await this.loadRecentActivity();
            
            this.isInitialized = true;
            console.log('Application initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize application:', error);
            this.showNotification('Failed to initialize application', 'error');
        }
    }

    /**
     * Load application configuration
     */
    async loadConfiguration() {
        try {
            const config = configManager.load();
            console.log('Configuration loaded:', config);
            
            // Validate configuration
            const validation = configManager.validate(config);
            if (!validation.isValid) {
                console.warn('Configuration validation warnings:', validation.errors);
            }
            
            return config;
        } catch (error) {
            console.error('Error loading configuration:', error);
            throw error;
        }
    }

    /**
     * Discover available AI models from providers
     */
    async discoverAIModels() {
        try {
            console.log('🔍 Discovering available AI models...');
            
            // Discover Ollama models
            const ollamaModels = await configManager.discoverOllamaModels();
            if (ollamaModels.length > 0) {
                console.log(`✅ Found ${ollamaModels.length} Ollama models:`, ollamaModels);
            } else {
                console.log('ℹ️ No Ollama models found or Ollama not available');
            }
            
        } catch (error) {
            console.warn('Error discovering AI models:', error.message);
        }
    }

    /**
     * Initialize UI components
     */
    initializeUI() {
        // Initialize tooltips, dropdowns, etc.
        this.initializeNotificationSystem();
        this.initializeKeyboardShortcuts();
        this.updateLastUpdateTime();
    }

    /**
     * Initialize notification system
     */
    initializeNotificationSystem() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 1000;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
    }

    /**
     * Initialize keyboard shortcuts
     */
    initializeKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + S: Save current content
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                this.handleSaveShortcut();
            }
            
            // Ctrl/Cmd + N: New article
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                this.createNewArticle();
            }
            
            // Ctrl/Cmd + F: Focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                this.focusSearch();
            }
        });
    }

    /**
     * Check AI service status
     */
    async checkAIServiceStatus() {
        try {
            const status = await aiService.checkAllProviders();
            this.updateAIStatusDisplay(status);
            return status;
        } catch (error) {
            console.error('Error checking AI service status:', error);
            this.showNotification('Failed to check AI service status', 'error');
            return {};
        }
    }

    /**
     * Update AI status display in UI
     */
    updateAIStatusDisplay(status) {
        for (const [provider, providerStatus] of Object.entries(status)) {
            const statusElement = document.getElementById(`${provider}-status`);
            const infoElement = document.getElementById(`${provider}-info`);
            
            if (statusElement && infoElement) {
                if (providerStatus.available) {
                    statusElement.className = 'status-indicator status-online';
                    infoElement.textContent = `${providerStatus.models?.length || 0} models available`;
                } else {
                    statusElement.className = 'status-indicator status-offline';
                    infoElement.textContent = providerStatus.error || 'Not available';
                }
            }
        }
    }

    /**
     * Load recent activity
     */
    async loadRecentActivity() {
        try {
            // Simulate recent activity data
            // In a real implementation, this would come from a backend API
            const activity = [
                {
                    type: 'file_created',
                    file: 'articles/ai-powered-content-management.html',
                    timestamp: new Date(Date.now() - 60000),
                    description: 'Created new article'
                },
                {
                    type: 'file_edited',
                    file: 'index.html',
                    timestamp: new Date(Date.now() - 300000),
                    description: 'Updated homepage content'
                },
                {
                    type: 'social_generated',
                    file: 'articles/startup-scaling.html',
                    timestamp: new Date(Date.now() - 600000),
                    description: 'Generated social media posts'
                }
            ];
            
            this.recentActivity = activity;
            this.updateRecentActivityDisplay();
            
        } catch (error) {
            console.error('Error loading recent activity:', error);
            const activityElement = document.getElementById('recent-activity');
            if (activityElement) {
                activityElement.innerHTML = '<p class="text-red-500">Failed to load recent activity</p>';
            }
        }
    }

    /**
     * Update recent activity display
     */
    updateRecentActivityDisplay() {
        const activityElement = document.getElementById('recent-activity');
        if (!activityElement) return;

        if (this.recentActivity.length === 0) {
            activityElement.innerHTML = '<p class="text-gray-500">No recent activity</p>';
            return;
        }

        const activityHtml = this.recentActivity.map(activity => `
            <div class="file-item">
                <div class="file-icon">
                    ${this.getActivityIcon(activity.type)}
                </div>
                <div class="file-info">
                    <div class="file-name">${activity.description}</div>
                    <div class="file-path">${activity.file} • ${this.formatTimeAgo(activity.timestamp)}</div>
                </div>
            </div>
        `).join('');

        activityElement.innerHTML = activityHtml;
    }

    /**
     * Get icon for activity type
     */
    getActivityIcon(type) {
        const icons = {
            'file_created': '[New]',
            'file_edited': '[Edit]',
            'social_generated': '[Social]',
            'ai_generated': '[AI]'
        };
        return icons[type] || '[File]';
    }

    /**
     * Format time ago
     */
    formatTimeAgo(timestamp) {
        const now = new Date();
        const diff = now - timestamp;
        const minutes = Math.floor(diff / 60000);
        
        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours}h ago`;
        
        const days = Math.floor(hours / 24);
        return `${days}d ago`;
    }

    /**
     * Load files and update file browser
     */
    async loadFiles() {
        const loadingElement = document.getElementById('files-loading');
        const fileListElement = document.getElementById('file-list');
        
        if (loadingElement) loadingElement.style.display = 'block';
        if (fileListElement) fileListElement.innerHTML = '';

        try {
            const files = await fileManager.getFileList();
            this.updateFileListDisplay(files);
        } catch (error) {
            console.error('Error loading files:', error);
            this.showNotification('Failed to load files', 'error');
            if (fileListElement) {
                fileListElement.innerHTML = '<div class="p-6 text-center text-red-500">Failed to load files</div>';
            }
        } finally {
            if (loadingElement) loadingElement.style.display = 'none';
        }
    }

    /**
     * Update file list display
     */
    updateFileListDisplay(files) {
        const fileListElement = document.getElementById('file-list');
        if (!fileListElement) return;

        if (files.length === 0) {
            fileListElement.innerHTML = '<div class="p-6 text-center text-gray-500">No files found</div>';
            return;
        }

        // Separate articles from other files
        const articles = files.filter(file => file.isArticle);
        const otherFiles = files.filter(file => !file.isArticle);

        let filesHtml = '';

        // Show articles section
        if (articles.length > 0) {
            filesHtml += '<div class="file-section"><h3 class="text-lg font-semibold text-gray-800 mb-3">&#128240; Blog Articles</h3>';
            filesHtml += articles.map(file => `
                <div class="file-item" data-file-path="${file.path}">
                    <div class="file-icon">
                        &#128196;
                    </div>
                    <div class="file-info">
                        <div class="file-name">${this.getCleanFileName(file.name)}</div>
                        <div class="file-path">
                            ${file.stats.words} words • ${file.stats.readingTime}min read • Last modified: ${new Date().toLocaleDateString()}
                        </div>
                    </div>
                    <div class="file-actions">
                        <button class="btn btn-secondary" onclick="editFile('${file.path}')">&#9998; Edit</button>
                        <button class="btn btn-accent" onclick="generateSocial('${file.path}')">&#128241; Social</button>
                    </div>
                </div>
            `).join('');
            filesHtml += '</div>';
        }

        // Show other files section
        if (otherFiles.length > 0) {
            filesHtml += '<div class="file-section mt-6"><h3 class="text-lg font-semibold text-gray-800 mb-3">&#128193; Other Files</h3>';
            filesHtml += otherFiles.map(file => `
                <div class="file-item" data-file-path="${file.path}">
                    <div class="file-icon">
                        ${this.getFileIcon(file.type)}
                    </div>
                    <div class="file-info">
                        <div class="file-name">${this.getCleanFileName(file.name)}</div>
                        <div class="file-path">
                            ${file.path} • ${file.stats.words} words
                        </div>
                    </div>
                    <div class="file-actions">
                        <button class="btn btn-secondary" onclick="editFile('${file.path}')">&#9998; Edit</button>
                    </div>
                </div>
            `).join('');
            filesHtml += '</div>';
        }

        fileListElement.innerHTML = filesHtml;
    }

    /**
     * Get clean filename without extension and formatted nicely
     */
    getCleanFileName(fileName) {
        // Remove .html extension and replace hyphens/underscores with spaces
        return fileName
            .replace(/\.html$/, '')
            .replace(/[-_]/g, ' ')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    /**
     * Get icon for file type
     */
    getFileIcon(type) {
        const icons = {
            'html': '&#127760;',  // 🌐
            'md': '&#128221;',    // 📝
            'txt': '&#128196;',   // 📄
            'css': '&#127912;',   // 🎨
            'js': '&#9889;',      // ⚡
            'json': '&#128295;'   // 🔧
        };
        return icons[type] || '&#128196;'; // 📄
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info', duration = 5000) {
        const notification = {
            id: Date.now(),
            message,
            type,
            timestamp: new Date()
        };
        
        this.notifications.push(notification);
        this.renderNotification(notification);
        
        if (duration > 0) {
            setTimeout(() => {
                this.hideNotification(notification.id);
            }, duration);
        }
        
        return notification.id;
    }

    /**
     * Render notification in UI
     */
    renderNotification(notification) {
        const container = document.getElementById('notification-container');
        if (!container) return;

        const colors = {
            'success': 'bg-green-500',
            'error': 'bg-red-500',
            'warning': 'bg-yellow-500',
            'info': 'bg-blue-500'
        };

        const notificationElement = document.createElement('div');
        notificationElement.id = `notification-${notification.id}`;
        notificationElement.className = `${colors[notification.type]} text-white px-4 py-3 rounded-lg mb-2 shadow-lg flex justify-between items-center`;
        
        notificationElement.innerHTML = `
            <span>${notification.message}</span>
            <button onclick="app.hideNotification(${notification.id})" class="ml-4 text-white hover:text-gray-200">
                ✕
            </button>
        `;
        
        container.appendChild(notificationElement);
    }

    /**
     * Hide notification
     */
    hideNotification(notificationId) {
        const element = document.getElementById(`notification-${notificationId}`);
        if (element) {
            element.remove();
        }
        
        this.notifications = this.notifications.filter(n => n.id !== notificationId);
    }

    /**
     * Update last update time
     */
    updateLastUpdateTime() {
        const element = document.getElementById('lastUpdate');
        if (element) {
            element.textContent = new Date().toLocaleTimeString();
        }
    }

    /**
     * Handle save keyboard shortcut
     */
    handleSaveShortcut() {
        // This would be implemented based on current context
        console.log('Save shortcut triggered');
    }

    /**
     * Create new article
     */
    createNewArticle() {
        const title = prompt('Enter article title:');
        if (title) {
            const filename = fileManager.generateFileName(title);
            window.location.href = `editor.html?new=true&title=${encodeURIComponent(title)}&filename=${encodeURIComponent(filename)}`;
        }
    }

    /**
     * Focus search input
     */
    focusSearch() {
        const searchInput = document.getElementById('file-search');
        if (searchInput) {
            searchInput.focus();
        }
    }
}

// Global application instance
window.app = new App();

// Global utility functions
window.initializeApp = async () => {
    await window.app.initialize();
};

window.loadFiles = async () => {
    await window.app.loadFiles();
};

window.loadRecentActivity = async () => {
    await window.app.loadRecentActivity();
};

window.checkAIServiceStatus = async () => {
    return await window.app.checkAIServiceStatus();
};

window.editFile = (filePath) => {
    window.location.href = `editor.html?file=${encodeURIComponent(filePath)}`;
};

window.generateSocial = (filePath) => {
    window.location.href = `social.html?file=${encodeURIComponent(filePath)}`;
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.initializeApp();
});