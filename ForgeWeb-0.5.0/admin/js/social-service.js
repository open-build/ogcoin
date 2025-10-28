/**
 * Social Media Service for Buildly AI Content Manager
 * Generates sharing links and social media content from articles
 */

class SocialMediaService {
    constructor() {
        this.platforms = {
            twitter: {
                name: 'Twitter/X',
                icon: 'X',
                color: '#000000',
                maxLength: 280,
                hashtagLimit: 5,
                baseUrl: 'https://twitter.com/intent/tweet'
            },
            linkedin: {
                name: 'LinkedIn',
                icon: 'LI',
                color: '#0077B5',
                maxLength: 3000,
                hashtagLimit: 3,
                baseUrl: 'https://www.linkedin.com/sharing/share-offsite'
            },
            facebook: {
                name: 'Facebook',
                icon: 'FB',
                color: '#1877F2',
                maxLength: 63206,
                hashtagLimit: 10,
                baseUrl: 'https://www.facebook.com/sharer/sharer.php'
            }
        };
    }

    /**
     * Generate social media posts for all platforms
     */
    async generateAllPosts(content, metadata = {}) {
        const posts = {};
        
        for (const platform of Object.keys(this.platforms)) {
            try {
                posts[platform] = await this.generatePost(content, platform, metadata);
            } catch (error) {
                console.error(`Error generating ${platform} post:`, error);
                posts[platform] = {
                    error: error.message,
                    fallback: this.generateFallbackPost(content, platform, metadata)
                };
            }
        }
        
        return posts;
    }

    /**
     * Generate platform-specific social media post
     */
    async generatePost(content, platform, metadata = {}) {
        const platformConfig = this.platforms[platform];
        if (!platformConfig) {
            throw new Error(`Unsupported platform: ${platform}`);
        }

        // Extract key information from content
        const contentInfo = this.extractContentInfo(content, metadata);
        
        // Generate AI-powered post content
        const aiContent = await this.generateAIPost(contentInfo, platform);
        
        // Create sharing links
        const sharingLink = this.createSharingLink(aiContent, platform, contentInfo.url);
        
        return {
            platform: platform,
            content: aiContent.text,
            hashtags: aiContent.hashtags,
            url: sharingLink,
            characterCount: aiContent.text.length,
            maxLength: platformConfig.maxLength,
            isValid: aiContent.text.length <= platformConfig.maxLength,
            generated: new Date().toISOString()
        };
    }

    /**
     * Extract key information from content
     */
    extractContentInfo(content, metadata = {}) {
        // Extract title
        const title = metadata.title || this.extractTitle(content) || 'Untitled';
        
        // Extract description
        const description = metadata.description || this.extractDescription(content) || '';
        
        // Extract key points
        const keyPoints = this.extractKeyPoints(content);
        
        // Extract URL
        const url = metadata.url || this.extractCanonicalUrl(content) || window.location.href;
        
        // Extract image
        const image = metadata.image || this.extractFeaturedImage(content);
        
        return {
            title,
            description,
            keyPoints,
            url,
            image,
            content: this.stripHtml(content),
            wordCount: this.countWords(content)
        };
    }

    /**
     * Generate AI-powered social media post
     */
    async generateAIPost(contentInfo, platform) {
        const platformConfig = this.platforms[platform];
        
        const prompt = this.createPrompt(contentInfo, platform);
        
        try {
            const response = await aiService.generateContent(prompt, {
                taskType: 'general',
                maxTokens: 200,
                temperature: 0.8
            });
            
            return this.parseAIResponse(response.content, platform);
        } catch (error) {
            console.error('AI generation failed, using fallback:', error);
            return this.generateFallbackPost(contentInfo, platform);
        }
    }

    /**
     * Create platform-specific prompt
     */
    createPrompt(contentInfo, platform) {
        const prompts = {
            twitter: `Create an engaging Twitter thread (2-3 tweets) about "${contentInfo.title}". 
                     Key points: ${contentInfo.keyPoints.join(', ')}
                     Make it conversational and include relevant hashtags.
                     Keep each tweet under 280 characters.
                     Format: Tweet 1: [content] | Tweet 2: [content] | Hashtags: #tag1 #tag2`,
            
            linkedin: `Create a professional LinkedIn post about "${contentInfo.title}".
                      Description: ${contentInfo.description}
                      Key insights: ${contentInfo.keyPoints.join(', ')}
                      Make it engaging for business professionals with industry insights.
                      Include 2-3 relevant hashtags.
                      Format: [Post content] | Hashtags: #tag1 #tag2`,
            
            facebook: `Create a Facebook post about "${contentInfo.title}".
                      Make it conversational and community-focused.
                      Key points: ${contentInfo.keyPoints.join(', ')}
                      Encourage engagement with questions or calls-to-action.
                      Include relevant hashtags.
                      Format: [Post content] | Hashtags: #tag1 #tag2`
        };

        return prompts[platform] || prompts.twitter;
    }

    /**
     * Parse AI response into structured format
     */
    parseAIResponse(response, platform) {
        // Split response into content and hashtags
        const parts = response.split('|');
        const content = parts[0]?.trim() || response;
        const hashtagsPart = parts.find(part => part.toLowerCase().includes('hashtags:'));
        
        // Extract hashtags
        const hashtags = this.extractHashtags(hashtagsPart || content);
        
        // Clean content (remove hashtag lines)
        const cleanContent = content
            .replace(/hashtags?:\s*#\w+(\s+#\w+)*/gi, '')
            .trim();
        
        return {
            text: cleanContent,
            hashtags: hashtags,
            platform: platform
        };
    }

    /**
     * Generate fallback post when AI fails
     */
    generateFallbackPost(contentInfo, platform) {
        const templates = {
            twitter: `New article: "${contentInfo.title}" 

${contentInfo.description ? contentInfo.description.substring(0, 150) + '...' : ''}

#BuildlyAI #ContentManagement #AI`,
            
            linkedin: `Just published: "${contentInfo.title}"

${contentInfo.description || 'Exploring innovative approaches to AI-powered content management and development workflows.'}

What are your thoughts on integrating AI into content workflows?

#AI #ContentManagement #BuildlyAI`,
            
            facebook: `Check out our latest article: "${contentInfo.title}"

${contentInfo.description || 'We dive deep into how AI is transforming content management and development workflows.'}

What's your experience with AI-powered tools? Share your thoughts below!

#AI #ContentManagement #BuildlyAI`
        };

        const text = templates[platform] || templates.twitter;
        const hashtags = this.extractHashtags(text);
        
        return {
            text: text.replace(/#\w+/g, '').trim(),
            hashtags: hashtags,
            platform: platform
        };
    }

    /**
     * Create sharing link for platform
     */
    createSharingLink(postContent, platform, url) {
        const platformConfig = this.platforms[platform];
        const encodedUrl = encodeURIComponent(url);
        const encodedText = encodeURIComponent(postContent.text);
        
        switch (platform) {
            case 'twitter':
                const hashtags = postContent.hashtags.map(tag => tag.replace('#', '')).join(',');
                return `${platformConfig.baseUrl}?text=${encodedText}&url=${encodedUrl}&hashtags=${hashtags}`;
                
            case 'linkedin':
                return `${platformConfig.baseUrl}?url=${encodedUrl}`;
                
            case 'facebook':
                return `${platformConfig.baseUrl}?u=${encodedUrl}`;
                
            default:
                return url;
        }
    }

    /**
     * Extract hashtags from text
     */
    extractHashtags(text) {
        if (!text) return [];
        
        const hashtagRegex = /#[a-zA-Z0-9_]+/g;
        const matches = text.match(hashtagRegex) || [];
        
        // Remove duplicates and limit count
        const uniqueHashtags = [...new Set(matches)];
        return uniqueHashtags.slice(0, 10);
    }

    /**
     * Generate relevant hashtags for content
     */
    generateHashtags(contentInfo, platform, count = 5) {
        const baseHashtags = ['#BuildlyAI', '#AI', '#ContentManagement'];
        const topicHashtags = [];
        
        // Extract topic-based hashtags from title and content
        const text = (contentInfo.title + ' ' + contentInfo.description).toLowerCase();
        
        const hashtagMap = {
            'ai': '#ArtificialIntelligence',
            'automation': '#Automation',
            'development': '#SoftwareDevelopment',
            'devops': '#DevOps',
            'startup': '#Startup',
            'product': '#ProductManagement',
            'management': '#ProjectManagement',
            'content': '#ContentStrategy',
            'social': '#SocialMedia',
            'marketing': '#DigitalMarketing',
            'tech': '#Technology',
            'innovation': '#Innovation',
            'productivity': '#Productivity',
            'efficiency': '#Efficiency'
        };
        
        for (const [keyword, hashtag] of Object.entries(hashtagMap)) {
            if (text.includes(keyword) && !topicHashtags.includes(hashtag)) {
                topicHashtags.push(hashtag);
            }
        }
        
        // Combine and limit
        const allHashtags = [...baseHashtags, ...topicHashtags];
        return allHashtags.slice(0, count);
    }

    /**
     * Extract title from HTML content
     */
    extractTitle(content) {
        const titleMatch = content.match(/<title[^>]*>([^<]+)<\/title>/i);
        if (titleMatch) {
            return titleMatch[1].replace(' - Buildly', '').trim();
        }
        
        const h1Match = content.match(/<h1[^>]*>([^<]+)<\/h1>/i);
        if (h1Match) {
            return this.stripHtml(h1Match[1]).trim();
        }
        
        return null;
    }

    /**
     * Extract description from HTML content
     */
    extractDescription(content) {
        const descMatch = content.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']+)["'][^>]*>/i);
        if (descMatch) {
            return descMatch[1];
        }
        
        // Try to extract first paragraph
        const pMatch = content.match(/<p[^>]*>([^<]+)<\/p>/i);
        if (pMatch) {
            const desc = this.stripHtml(pMatch[1]).trim();
            return desc.length > 160 ? desc.substring(0, 157) + '...' : desc;
        }
        
        return null;
    }

    /**
     * Extract key points from content
     */
    extractKeyPoints(content) {
        const points = [];
        
        // Extract from list items
        const listMatches = content.matchAll(/<li[^>]*>([^<]+)<\/li>/gi);
        for (const match of listMatches) {
            const point = this.stripHtml(match[1]).trim();
            if (point && point.length < 100) {
                points.push(point);
            }
        }
        
        // Extract from headings
        const headingMatches = content.matchAll(/<h[2-6][^>]*>([^<]+)<\/h[2-6]>/gi);
        for (const match of headingMatches) {
            const heading = this.stripHtml(match[1]).trim();
            if (heading && heading.length < 80) {
                points.push(heading);
            }
        }
        
        return points.slice(0, 5);
    }

    /**
     * Extract canonical URL from content
     */
    extractCanonicalUrl(content) {
        const canonicalMatch = content.match(/<link[^>]*rel=["']canonical["'][^>]*href=["']([^"']+)["'][^>]*>/i);
        return canonicalMatch ? canonicalMatch[1] : null;
    }

    /**
     * Extract featured image from content
     */
    extractFeaturedImage(content) {
        const ogImageMatch = content.match(/<meta[^>]*property=["']og:image["'][^>]*content=["']([^"']+)["'][^>]*>/i);
        return ogImageMatch ? ogImageMatch[1] : null;
    }

    /**
     * Strip HTML tags from text
     */
    stripHtml(html) {
        const div = document.createElement('div');
        div.innerHTML = html;
        return div.textContent || div.innerText || '';
    }

    /**
     * Count words in text
     */
    countWords(text) {
        const cleanText = this.stripHtml(text);
        return cleanText.split(/\s+/).filter(word => word.length > 0).length;
    }

    /**
     * Preview post for platform
     */
    previewPost(postData, platform) {
        const platformConfig = this.platforms[platform];
        
        return {
            platform: platformConfig.name,
            icon: platformConfig.icon,
            color: platformConfig.color,
            content: postData.content,
            hashtags: postData.hashtags,
            characterCount: postData.characterCount,
            maxLength: platformConfig.maxLength,
            isValid: postData.isValid,
            url: postData.url
        };
    }

    /**
     * Get sharing statistics
     */
    getSharingStats(posts) {
        const stats = {
            totalPosts: Object.keys(posts).length,
            validPosts: 0,
            totalCharacters: 0,
            totalHashtags: 0,
            platforms: []
        };
        
        for (const [platform, post] of Object.entries(posts)) {
            if (!post.error) {
                stats.validPosts++;
                stats.totalCharacters += post.characterCount;
                stats.totalHashtags += post.hashtags.length;
                stats.platforms.push(platform);
            }
        }
        
        return stats;
    }
}

// Global social media service instance
window.socialMediaService = new SocialMediaService();

// Utility functions
window.generateSocialPosts = async (content, metadata) => {
    return await window.socialMediaService.generateAllPosts(content, metadata);
};

window.createSharingLink = (postContent, platform, url) => {
    return window.socialMediaService.createSharingLink(postContent, platform, url);
};