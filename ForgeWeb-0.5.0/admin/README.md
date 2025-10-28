# Buildly AI Content Manager Architecture

## Overview
A local web-based AI content management system for the Buildly website that supports multiple AI providers (Ollama, OpenAI, Google Gemini) for content creation, editing, and social media distribution.

## System Architecture

### Frontend Components
- **Admin Dashboard** (`/admin/index.html`) - Main interface with file listing and management
- **Content Editor** (`/admin/editor.html`) - Rich text editor with AI assistance
- **Settings Panel** (`/admin/settings.html`) - AI provider configuration and preferences
- **Social Media Manager** (`/admin/social.html`) - Share link generation and scheduling

### Backend Components
- **AI Service Manager** (`/admin/js/ai-service.js`) - Unified API for all AI providers
- **File Manager** (`/admin/js/file-manager.js`) - File operations and Git integration
- **Content Processor** (`/admin/js/content-processor.js`) - HTML parsing and generation
- **Social Media Service** (`/admin/js/social-service.js`) - Share link generation

### Data Storage
- **Local Configuration** - Settings stored in localStorage
- **File System** - Direct file operations for content management
- **Git Integration** - Version control for all changes

## AI Provider Integration

### Ollama (Local)
- **Endpoint**: `http://localhost:11434/api/generate`
- **Models**: llama2, codellama, mistral
- **Use Cases**: Draft generation, privacy-sensitive content
- **Offline**: Full functionality without internet

### OpenAI
- **Endpoint**: `https://api.openai.com/v1/chat/completions`
- **Models**: gpt-4-turbo, gpt-3.5-turbo
- **Use Cases**: High-quality editing, complex analysis
- **Features**: Function calling, vision capabilities

### Google Gemini
- **Endpoint**: `https://generativelanguage.googleapis.com/v1/models/`
- **Models**: gemini-pro, gemini-pro-vision
- **Use Cases**: Research integration, multimodal content
- **Features**: Long context, real-time data

## Core Features

### Content Management
1. **File Browser**
   - Navigate website structure
   - Filter by file type (HTML, articles)
   - Preview content summaries
   - Search functionality

2. **Content Editor**
   - Rich text editing with live preview
   - AI-powered suggestions and completions
   - Template support for consistent formatting
   - SEO optimization hints

3. **AI Assistance**
   - Content generation from prompts
   - Editing suggestions and improvements
   - Style consistency checking
   - Grammar and tone optimization

### Social Media Integration
1. **Auto Share Link Generation**
   - Twitter/X optimized posts with threading
   - LinkedIn professional formatting
   - Facebook engagement-focused content
   - Platform-specific hashtag suggestions

2. **Meta Tag Management**
   - Extract and optimize Open Graph tags
   - Generate Twitter Card metadata
   - SEO-friendly descriptions
   - Image optimization suggestions

### Security & Privacy
1. **Local-First Design**
   - No data sent to external services without consent
   - Encrypted API key storage
   - User permission prompts for external calls

2. **Access Control**
   - Simple authentication for admin access
   - Role-based permissions (future)
   - Audit logging for all changes

## Implementation Plan

### Phase 1: Core Infrastructure
- [ ] Admin dashboard with file browser
- [ ] Basic content editor interface
- [ ] AI service abstraction layer
- [ ] Local configuration management

### Phase 2: AI Integration
- [ ] Ollama local integration
- [ ] OpenAI API integration
- [ ] Google Gemini API integration
- [ ] Provider selection and fallback logic

### Phase 3: Content Features
- [ ] File read/write operations
- [ ] Content generation workflows
- [ ] Template management
- [ ] Preview and publishing

### Phase 4: Social Media
- [ ] Share link generation
- [ ] Platform-specific optimization
- [ ] Meta tag extraction and editing
- [ ] Scheduling interface (future)

### Phase 5: Advanced Features
- [ ] Git integration for version control
- [ ] Collaborative editing
- [ ] Analytics integration
- [ ] Performance monitoring

## File Structure
```
/admin/
├── index.html              # Main dashboard
├── editor.html            # Content editor
├── settings.html          # Configuration
├── social.html            # Social media manager
├── css/
│   ├── admin.css         # Admin interface styles
│   └── editor.css        # Editor-specific styles
├── js/
│   ├── app.js            # Main application
│   ├── ai-service.js     # AI provider management
│   ├── file-manager.js   # File operations
│   ├── content-processor.js # Content parsing
│   ├── social-service.js # Social media integration
│   ├── editor.js         # Rich text editor
│   └── config.js         # Configuration management
└── README.md             # This file
```

## Configuration Format
```javascript
{
  "aiProviders": {
    "ollama": {
      "enabled": true,
      "endpoint": "http://localhost:11434",
      "defaultModel": "llama2",
      "models": ["llama2", "codellama", "mistral"]
    },
    "openai": {
      "enabled": false,
      "apiKey": "",
      "defaultModel": "gpt-4-turbo",
      "models": ["gpt-4-turbo", "gpt-3.5-turbo"]
    },
    "gemini": {
      "enabled": false,
      "apiKey": "",
      "defaultModel": "gemini-pro",
      "models": ["gemini-pro", "gemini-pro-vision"]
    }
  },
  "content": {
    "defaultTemplate": "article",
    "autoSave": true,
    "backupEnabled": true
  },
  "social": {
    "autoGenerate": true,
    "platforms": ["twitter", "linkedin", "facebook"],
    "hashtagSuggestions": true
  }
}
```

## Security Considerations
- API keys encrypted in localStorage
- CORS policies for local development
- Input sanitization for all user content
- Rate limiting for AI API calls
- Audit logging for all file modifications

## Usage Workflow
1. **Access Admin**: Navigate to `/admin/` (localhost only)
2. **Configure AI**: Set up preferred AI providers in settings
3. **Browse Content**: Use file browser to find content to edit
4. **Edit/Create**: Use AI-assisted editor for content creation
5. **Generate Social**: Create social media posts from content
6. **Publish**: Save changes and optionally commit to Git

## Future Enhancements
- Multi-user collaboration
- Workflow approval processes
- Analytics dashboard
- A/B testing integration
- Advanced AI fine-tuning
- Plugin system for extensions