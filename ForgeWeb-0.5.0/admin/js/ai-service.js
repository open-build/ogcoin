/**
 * AI Service Manager for Buildly Content Manager
 * Unified interface for Ollama, OpenAI, and Google Gemini APIs
 */

class AIService {
    constructor() {
        this.providers = new Map();
        this.currentProvider = null;
        this.requestQueue = [];
        this.isProcessing = false;
        
        // Initialize providers
        this.initializeProviders();
    }

    /**
     * Initialize AI providers
     */
    initializeProviders() {
        // Ollama provider
        this.providers.set('ollama', new OllamaProvider());
        
        // OpenAI provider
        this.providers.set('openai', new OpenAIProvider());
        
        // Google Gemini provider
        this.providers.set('gemini', new GeminiProvider());
    }

    /**
     * Check status of all AI providers
     */
    async checkAllProviders() {
        const status = {};
        
        for (const [name, provider] of this.providers) {
            try {
                status[name] = await provider.checkStatus();
            } catch (error) {
                status[name] = {
                    available: false,
                    error: error.message,
                    models: []
                };
            }
        }
        
        return status;
    }

    /**
     * Get the best available provider for a task
     */
    selectBestProvider(taskType = 'general') {
        const enabledProviders = configManager.getEnabledProviders();
        
        // Provider preference based on task type
        const preferences = {
            'draft': ['ollama', 'openai', 'gemini'],
            'edit': ['openai', 'gemini', 'ollama'],
            'research': ['gemini', 'openai', 'ollama'],
            'code': ['ollama', 'openai', 'gemini'],
            'general': ['openai', 'ollama', 'gemini']
        };
        
        const preferredOrder = preferences[taskType] || preferences.general;
        
        for (const provider of preferredOrder) {
            if (enabledProviders.includes(provider)) {
                return provider;
            }
        }
        
        return enabledProviders[0] || null;
    }

    /**
     * Generate content using the best available provider
     */
    async generateContent(prompt, options = {}) {
        const {
            taskType = 'general',
            provider = null,
            model = null,
            maxTokens = 1000,
            temperature = 0.7,
            streaming = false
        } = options;

        const selectedProvider = provider || this.selectBestProvider(taskType);
        
        if (!selectedProvider) {
            throw new Error('No AI providers are configured and enabled');
        }

        const providerInstance = this.providers.get(selectedProvider);
        if (!providerInstance) {
            throw new Error(`Provider ${selectedProvider} not found`);
        }

        const config = await configManager.getProviderConfig(selectedProvider);
        if (!config || !config.enabled) {
            throw new Error(`Provider ${selectedProvider} is not enabled`);
        }

        const selectedModel = model || config.defaultModel;

        try {
            const request = {
                provider: selectedProvider,
                model: selectedModel,
                prompt,
                maxTokens,
                temperature,
                streaming,
                timestamp: Date.now()
            };

            console.log(`🤖 AI Request: ${selectedProvider}/${selectedModel} (${prompt.length} chars)`);
            const startTime = Date.now();

            let result;
            if (streaming) {
                result = providerInstance.generateStreaming(request, config);
            } else {
                result = await Promise.race([
                    providerInstance.generate(request, config),
                    new Promise((_, reject) => 
                        setTimeout(() => reject(new Error('Request timeout after 60 seconds')), 60000)
                    )
                ]);
            }

            const duration = Date.now() - startTime;
            console.log(`✅ AI Response: ${duration}ms (${result.content?.length || 0} chars)`);
            
            return result;
        } catch (error) {
            console.error(`Error generating content with ${selectedProvider}:`, error);
            
            // Try fallback provider if available
            const enabledProviders = configManager.getEnabledProviders();
            const fallbackProviders = enabledProviders.filter(p => p !== selectedProvider);
            
            if (fallbackProviders.length > 0) {
                console.log(`Trying fallback provider: ${fallbackProviders[0]}`);
                return this.generateContent(prompt, {
                    ...options,
                    provider: fallbackProviders[0]
                });
            }
            
            throw error;
        }
    }

    /**
     * Generate content suggestions for editing
     */
    async generateSuggestions(content, suggestionType = 'improve') {
        const prompts = {
            improve: `Please improve the following content while maintaining its meaning and style:\n\n${content}`,
            grammar: `Please fix any grammar and spelling errors in the following content:\n\n${content}`,
            shorten: `Please make the following content more concise while keeping the key points:\n\n${content}`,
            expand: `Please expand on the following content with more details and examples:\n\n${content}`,
            tone: `Please adjust the tone of the following content to be more professional:\n\n${content}`
        };

        const prompt = prompts[suggestionType] || prompts.improve;
        
        return this.generateContent(prompt, {
            taskType: 'edit',
            maxTokens: Math.max(1000, content.length * 1.5),
            temperature: 0.3
        });
    }

    /**
     * Generate social media posts from content
     */
    async generateSocialPosts(content, platform = 'twitter') {
        const prompts = {
            twitter: `Create an engaging Twitter thread (3-5 tweets) based on this content. Use relevant hashtags:\n\n${content}`,
            linkedin: `Create a professional LinkedIn post based on this content. Make it engaging for a business audience:\n\n${content}`,
            facebook: `Create a Facebook post based on this content. Make it conversational and engaging:\n\n${content}`
        };

        const prompt = prompts[platform] || prompts.twitter;
        
        return this.generateContent(prompt, {
            taskType: 'general',
            maxTokens: 500,
            temperature: 0.8
        });
    }

    /**
     * Extract and optimize meta tags from content
     */
    async generateMetaTags(content, title = '') {
        const prompt = `Based on the following content, generate SEO-optimized meta tags including:
- Title (if not provided: "${title}")
- Description (150-160 characters)
- Keywords (10-15 relevant keywords)
- Open Graph title and description

Content:
${content}`;

        return this.generateContent(prompt, {
            taskType: 'general',
            maxTokens: 300,
            temperature: 0.3
        });
    }
}

/**
 * Ollama Provider Implementation
 */
class OllamaProvider {
    async checkStatus() {
        const config = await configManager.getProviderConfig('ollama');
        if (!config) {
            throw new Error('Ollama not configured');
        }

        try {
            const response = await fetch(`${config.endpoint}/api/tags`, {
                method: 'GET',
                timeout: config.timeout || 5000
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            return {
                available: true,
                models: data.models?.map(m => m.name) || [],
                version: data.version || 'unknown'
            };
        } catch (error) {
            throw new Error(`Ollama connection failed: ${error.message}`);
        }
    }

    async generate(request, config) {
        console.log(`🦙 Ollama generate: ${request.model} (${request.prompt.length} chars)`);
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), config.timeout || 60000);

        try {
            const response = await fetch(`${config.endpoint}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: request.model,
                    prompt: request.prompt,
                    stream: false,
                    options: {
                        temperature: request.temperature,
                        num_predict: request.maxTokens
                    }
                }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`Ollama API error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            console.log(`✅ Ollama response: ${data.response?.length || 0} chars`);
            
            return {
                provider: 'ollama',
                model: request.model,
                content: data.response,
                usage: {
                    promptTokens: data.prompt_eval_count || 0,
                    completionTokens: data.eval_count || 0,
                totalTokens: (data.prompt_eval_count || 0) + (data.eval_count || 0)
                },
                finishReason: data.done ? 'stop' : 'length'
            };
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timed out - Ollama may be processing a large request');
            }
            console.error('🚨 Ollama generate error:', error);
            throw error;
        }
    }

    async *generateStreaming(request, config) {
        const response = await fetch(`${config.endpoint}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: request.model,
                prompt: request.prompt,
                stream: true,
                options: {
                    temperature: request.temperature,
                    num_predict: request.maxTokens
                }
            })
        });

        if (!response.ok) {
            throw new Error(`Ollama API error: ${response.status} ${response.statusText}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n').filter(line => line.trim());

                for (const line of lines) {
                    try {
                        const data = JSON.parse(line);
                        if (data.response) {
                            yield {
                                provider: 'ollama',
                                model: request.model,
                                content: data.response,
                                done: data.done
                            };
                        }
                    } catch (e) {
                        console.warn('Failed to parse streaming response:', line);
                    }
                }
            }
        } finally {
            reader.releaseLock();
        }
    }
}

/**
 * OpenAI Provider Implementation
 */
class OpenAIProvider {
    async checkStatus() {
        const config = configManager.getProviderConfig('openai');
        if (!config || !config.apiKey) {
            throw new Error('OpenAI API key not configured');
        }

        try {
            const response = await fetch(`${config.endpoint}/models`, {
                headers: {
                    'Authorization': `Bearer ${config.apiKey}`,
                    'Content-Type': 'application/json'
                },
                timeout: config.timeout || 5000
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            return {
                available: true,
                models: data.data?.map(m => m.id) || [],
                version: 'openai-api'
            };
        } catch (error) {
            throw new Error(`OpenAI connection failed: ${error.message}`);
        }
    }

    async generate(request, config) {
        const response = await fetch(`${config.endpoint}/chat/completions`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${config.apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: request.model,
                messages: [
                    { role: 'user', content: request.prompt }
                ],
                max_tokens: request.maxTokens,
                temperature: request.temperature,
                stream: false
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(`OpenAI API error: ${error.error?.message || response.statusText}`);
        }

        const data = await response.json();
        const choice = data.choices?.[0];
        
        return {
            provider: 'openai',
            model: request.model,
            content: choice?.message?.content || '',
            usage: data.usage || {},
            finishReason: choice?.finish_reason || 'unknown'
        };
    }

    async *generateStreaming(request, config) {
        const response = await fetch(`${config.endpoint}/chat/completions`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${config.apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: request.model,
                messages: [
                    { role: 'user', content: request.prompt }
                ],
                max_tokens: request.maxTokens,
                temperature: request.temperature,
                stream: true
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(`OpenAI API error: ${error.error?.message || response.statusText}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n').filter(line => line.trim());

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') return;

                        try {
                            const parsed = JSON.parse(data);
                            const delta = parsed.choices?.[0]?.delta;
                            if (delta?.content) {
                                yield {
                                    provider: 'openai',
                                    model: request.model,
                                    content: delta.content,
                                    done: false
                                };
                            }
                        } catch (e) {
                            console.warn('Failed to parse streaming response:', data);
                        }
                    }
                }
            }
        } finally {
            reader.releaseLock();
        }
    }
}

/**
 * Google Gemini Provider Implementation
 */
class GeminiProvider {
    async checkStatus() {
        const config = configManager.getProviderConfig('gemini');
        if (!config || !config.apiKey) {
            throw new Error('Gemini API key not configured');
        }

        // For now, return basic status - Gemini doesn't have a models endpoint
        return {
            available: true,
            models: ['gemini-pro', 'gemini-pro-vision'],
            version: 'gemini-api'
        };
    }

    async generate(request, config) {
        const response = await fetch(
            `${config.endpoint}/models/${request.model}:generateContent?key=${config.apiKey}`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    contents: [
                        {
                            parts: [{ text: request.prompt }]
                        }
                    ],
                    generationConfig: {
                        temperature: request.temperature,
                        maxOutputTokens: request.maxTokens
                    }
                })
            }
        );

        if (!response.ok) {
            const error = await response.json();
            throw new Error(`Gemini API error: ${error.error?.message || response.statusText}`);
        }

        const data = await response.json();
        const candidate = data.candidates?.[0];
        const content = candidate?.content?.parts?.[0]?.text || '';
        
        return {
            provider: 'gemini',
            model: request.model,
            content: content,
            usage: data.usageMetadata || {},
            finishReason: candidate?.finishReason || 'unknown'
        };
    }

    // Gemini streaming implementation would go here
    async *generateStreaming(request, config) {
        // For now, fall back to non-streaming
        const result = await this.generate(request, config);
        yield { ...result, done: true };
    }
}

// Global AI service instance
window.aiService = new AIService();

// Utility functions
window.checkAIServiceStatus = async () => {
    return await window.aiService.checkAllProviders();
};

window.generateAIContent = async (prompt, options) => {
    return await window.aiService.generateContent(prompt, options);
};