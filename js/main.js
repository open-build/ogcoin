/**
 * OGCoin Main JavaScript
 * Site-specific functionality and interactions
 * Compatible with ForgeWeb framework
 */

(function() {
    'use strict';

    // Site-specific configuration
    const OGCoin = {
        config: {
            animationDuration: 300,
            scrollOffset: 80,
            mobileBreakpoint: 768
        },
        
        // Initialize all functionality
        init: function() {
            this.initNavigation();
            this.initScrollEffects();
            this.initMobileMenu();
            this.initSmoothScrolling();
            this.initFormHandling();
            this.initAnimations();
            
            console.log('🪙 OGCoin site initialized');
        },

        // Navigation functionality
        initNavigation: function() {
            const nav = document.querySelector('nav');
            if (!nav) return;

            // Add scroll effect to navigation
            let lastScrollY = window.scrollY;
            
            const handleScroll = window.ForgeWeb.utils.debounce(() => {
                const currentScrollY = window.scrollY;
                
                if (currentScrollY > 100) {
                    nav.classList.add('shadow-lg', 'backdrop-blur-sm');
                    nav.classList.remove('shadow-sm');
                } else {
                    nav.classList.remove('shadow-lg', 'backdrop-blur-sm');
                    nav.classList.add('shadow-sm');
                }

                // Hide/show nav on scroll (optional)
                if (currentScrollY > lastScrollY && currentScrollY > 200) {
                    nav.style.transform = 'translateY(-100%)';
                } else {
                    nav.style.transform = 'translateY(0)';
                }
                
                lastScrollY = currentScrollY;
            }, 100);

            window.addEventListener('scroll', handleScroll);
            
            // Add transition to nav
            nav.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
        },

        // Mobile menu functionality
        initMobileMenu: function() {
            const mobileMenuButton = document.getElementById('mobile-menu-button');
            const mobileMenu = document.getElementById('mobile-menu');
            
            if (!mobileMenuButton || !mobileMenu) return;

            let isOpen = false;

            const toggleMenu = () => {
                isOpen = !isOpen;
                
                if (isOpen) {
                    mobileMenu.classList.remove('hidden');
                    mobileMenu.classList.add('show');
                    mobileMenuButton.setAttribute('aria-expanded', 'true');
                    
                    // Change hamburger to X
                    mobileMenuButton.innerHTML = `
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    `;
                } else {
                    mobileMenu.classList.add('hidden');
                    mobileMenu.classList.remove('show');
                    mobileMenuButton.setAttribute('aria-expanded', 'false');
                    
                    // Change X back to hamburger
                    mobileMenuButton.innerHTML = `
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                        </svg>
                    `;
                }
            };

            mobileMenuButton.addEventListener('click', toggleMenu);

            // Close menu when clicking on links
            mobileMenu.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    if (isOpen) toggleMenu();
                });
            });

            // Close menu when clicking outside
            document.addEventListener('click', (e) => {
                if (isOpen && !mobileMenu.contains(e.target) && !mobileMenuButton.contains(e.target)) {
                    toggleMenu();
                }
            });
        },

        // Smooth scrolling for anchor links
        initSmoothScrolling: function() {
            document.querySelectorAll('a[href^="#"]').forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const targetId = link.getAttribute('href');
                    const targetElement = document.querySelector(targetId);
                    
                    if (targetElement) {
                        const offsetTop = targetElement.offsetTop - this.config.scrollOffset;
                        window.scrollTo({
                            top: offsetTop,
                            behavior: 'smooth'
                        });

                        // Update URL without jumping
                        history.pushState(null, null, targetId);
                    }
                });
            });
        },

        // Scroll effects and animations
        initScrollEffects: function() {
            // Parallax effect for hero section (subtle)
            const hero = document.querySelector('.hero-gradient');
            if (hero) {
                const handleParallax = window.ForgeWeb.utils.debounce(() => {
                    const scrolled = window.pageYOffset;
                    const rate = scrolled * -0.5;
                    hero.style.transform = `translateY(${rate}px)`;
                }, 10);

                window.addEventListener('scroll', handleParallax);
            }

            // Highlight active navigation section
            const sections = document.querySelectorAll('section[id]');
            const navLinks = document.querySelectorAll('nav a[href^="#"]');

            const highlightNavigation = window.ForgeWeb.utils.debounce(() => {
                let current = '';
                
                sections.forEach(section => {
                    const sectionTop = section.offsetTop;
                    const sectionHeight = section.clientHeight;
                    
                    if (window.pageYOffset >= (sectionTop - this.config.scrollOffset)) {
                        current = section.getAttribute('id');
                    }
                });

                navLinks.forEach(link => {
                    link.classList.remove('text-primary', 'font-semibold');
                    if (link.getAttribute('href') === `#${current}`) {
                        link.classList.add('text-primary', 'font-semibold');
                    }
                });
            }, 100);

            window.addEventListener('scroll', highlightNavigation);
        },

        // Form handling
        initFormHandling: function() {
            // Handle contact forms (if any are added later)
            const forms = document.querySelectorAll('form');
            
            forms.forEach(form => {
                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const formData = new FormData(form);
                    const data = Object.fromEntries(formData);
                    
                    try {
                        // Show loading state
                        const submitButton = form.querySelector('button[type="submit"]');
                        const originalText = submitButton.textContent;
                        submitButton.textContent = 'Sending...';
                        submitButton.disabled = true;
                        
                        // Here you would typically send to your backend
                        // For now, just simulate success
                        await new Promise(resolve => setTimeout(resolve, 1000));
                        
                        // Show success message
                        this.showNotification('Message sent successfully!', 'success');
                        form.reset();
                        
                        // Restore button
                        submitButton.textContent = originalText;
                        submitButton.disabled = false;
                        
                    } catch (error) {
                        console.error('Form submission error:', error);
                        this.showNotification('Error sending message. Please try again.', 'error');
                        
                        // Restore button
                        const submitButton = form.querySelector('button[type="submit"]');
                        submitButton.textContent = 'Send Message';
                        submitButton.disabled = false;
                    }
                });
            });
        },

        // Animation enhancements
        initAnimations: function() {
            // Animate feature cards on hover
            const cards = document.querySelectorAll('.card-hover');
            
            cards.forEach(card => {
                card.addEventListener('mouseenter', () => {
                    card.style.transform = 'translateY(-8px) scale(1.02)';
                });
                
                card.addEventListener('mouseleave', () => {
                    card.style.transform = 'translateY(0) scale(1)';
                });
            });

            // Add loading animation to external links
            const externalLinks = document.querySelectorAll('a[href^="http"]');
            
            externalLinks.forEach(link => {
                link.addEventListener('click', (e) => {
                    if (link.target === '_blank') {
                        // Add a subtle loading indicator
                        link.style.opacity = '0.7';
                        setTimeout(() => {
                            link.style.opacity = '1';
                        }, 500);
                    }
                });
            });
        },

        // Utility: Show notifications
        showNotification: function(message, type = 'info') {
            // Create notification element
            const notification = document.createElement('div');
            notification.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-lg shadow-lg text-white transition-all duration-500 transform translate-x-full`;
            
            // Set color based on type
            switch(type) {
                case 'success':
                    notification.classList.add('bg-green-500');
                    break;
                case 'error':
                    notification.classList.add('bg-red-500');
                    break;
                default:
                    notification.classList.add('bg-blue-500');
            }
            
            notification.textContent = message;
            document.body.appendChild(notification);
            
            // Animate in
            setTimeout(() => {
                notification.classList.remove('translate-x-full');
            }, 100);
            
            // Auto remove after 3 seconds
            setTimeout(() => {
                notification.classList.add('translate-x-full');
                setTimeout(() => {
                    document.body.removeChild(notification);
                }, 300);
            }, 3000);
        },

        // Utility: Check if mobile
        isMobile: function() {
            return window.innerWidth < this.config.mobileBreakpoint;
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => OGCoin.init());
    } else {
        OGCoin.init();
    }

    // Make OGCoin globally available for debugging
    window.OGCoin = OGCoin;

})();