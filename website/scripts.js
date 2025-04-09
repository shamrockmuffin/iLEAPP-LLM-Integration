// iLEAPP AI Website Scripts - Enhanced for better UX
document.addEventListener('DOMContentLoaded', function() {
    // Mobile Menu Toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mainNav = document.querySelector('.main-nav');
    
    if (mobileMenuToggle && mainNav) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenuToggle.classList.toggle('active');
            mainNav.classList.toggle('active');
            document.body.classList.toggle('menu-open');
        });
    }
    
    // FAQ Accordion
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        if (question) {
            question.addEventListener('click', function() {
                // Close all other items
                faqItems.forEach(otherItem => {
                    if (otherItem !== item) {
                        otherItem.classList.remove('active');
                    }
                });
                
                // Toggle current item
                item.classList.toggle('active');
            });
        }
    });
    
    // Testimonial Slider
    const testimonials = document.querySelectorAll('.testimonial');
    const dots = document.querySelectorAll('.dot');
    const prevButton = document.querySelector('.testimonial-prev');
    const nextButton = document.querySelector('.testimonial-next');
    
    if (testimonials.length > 0 && dots.length > 0) {
        let currentIndex = 0;
        
        // Show only the current testimonial
        function showTestimonial(index) {
            testimonials.forEach((testimonial, i) => {
                testimonial.style.display = i === index ? 'block' : 'none';
            });
            
            dots.forEach((dot, i) => {
                dot.classList.toggle('active', i === index);
            });
        }
        
        // Initialize
        showTestimonial(currentIndex);
        
        // Next button
        if (nextButton) {
            nextButton.addEventListener('click', function() {
                currentIndex = (currentIndex + 1) % testimonials.length;
                showTestimonial(currentIndex);
            });
        }
        
        // Previous button
        if (prevButton) {
            prevButton.addEventListener('click', function() {
                currentIndex = (currentIndex - 1 + testimonials.length) % testimonials.length;
                showTestimonial(currentIndex);
            });
        }
        
        // Dot navigation
        dots.forEach((dot, i) => {
            dot.addEventListener('click', function() {
                currentIndex = i;
                showTestimonial(currentIndex);
            });
        });
        
        // Auto-advance every 5 seconds
        setInterval(function() {
            if (!document.hidden) {
                currentIndex = (currentIndex + 1) % testimonials.length;
                showTestimonial(currentIndex);
            }
        }, 5000);
    }
    
    // Back to Top Button
    const backToTopButton = document.querySelector('.back-to-top');
    
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.classList.add('active');
            } else {
                backToTopButton.classList.remove('active');
            }
        });
        
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Search Functionality
    const searchToggle = document.querySelector('.search-toggle');
    const searchContainer = document.querySelector('.search-container');
    const searchClose = document.querySelector('.search-close');
    const searchForm = document.querySelector('.search-form');
    const searchInput = document.querySelector('.search-form input');
    const searchResults = document.querySelector('.search-results');
    
    if (searchToggle && searchContainer && searchClose) {
        // Open search
        searchToggle.addEventListener('click', function() {
            searchContainer.classList.add('active');
            document.body.style.overflow = 'hidden';
            
            // Focus on input after animation completes
            setTimeout(() => {
                if (searchInput) searchInput.focus();
            }, 300);
        });
        
        // Close search
        searchClose.addEventListener('click', function() {
            searchContainer.classList.remove('active');
            document.body.style.overflow = '';
        });
        
        // Close on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && searchContainer.classList.contains('active')) {
                searchContainer.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
        
        // Prevent clicks inside the search container from closing it
        if (searchContainer) {
            searchContainer.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }
        
        // Search form submission
        if (searchForm && searchResults) {
            searchForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                if (searchInput) {
                    const query = searchInput.value.trim().toLowerCase();
                    
                    if (query.length < 2) {
                        searchResults.innerHTML = '<p>Please enter at least 2 characters to search.</p>';
                        return;
                    }
                    
                    // Show loading state
                    searchResults.innerHTML = '<div class="skeleton" style="height: 30px; margin-bottom: 10px;"></div>'.repeat(3);
                    
                    // Simulate search (in a real implementation, this would query a search API or database)
                    setTimeout(() => {
                        performSearch(query);
                    }, 500);
                }
            });
        }
    }
    
    // Simulated search functionality
    function performSearch(query) {
        if (!searchResults) return;
        
        // This is a simplified search that would be replaced with actual search logic
        const searchableContent = [
            { title: 'Message Analysis', url: '#features', category: 'Feature', description: 'Extract insights from conversations with sentiment analysis and topic extraction.' },
            { title: 'App Usage Analysis', url: '#features', category: 'Feature', description: 'Understand user behavior through app usage patterns and screen time analysis.' },
            { title: 'iTunes Music Analysis', url: '#features', category: 'Feature', description: 'Analyze music preferences and listening patterns to build a comprehensive user profile.' },
            { title: 'Chrome History Analysis', url: '#features', category: 'Feature', description: 'Examine browsing patterns, search interests, and web activity to identify digital footprints.' },
            { title: 'Getting Started Guide', url: 'docs/getting-started.html', category: 'Documentation', description: 'Learn how to install and configure iLEAPP AI for your first investigation.' },
            { title: 'API Reference', url: 'docs/api-reference.html', category: 'Documentation', description: 'Detailed documentation of the iLEAPP AI API for developers and integrators.' },
            { title: 'Integration Guide', url: 'docs/integration-guide.html', category: 'Documentation', description: 'Learn how to integrate iLEAPP AI with your existing forensic workflow.' },
            { title: 'Download iLEAPP AI', url: 'downloads/', category: 'Download', description: 'Download the latest version of iLEAPP AI for your platform.' }
        ];
        
        const results = searchableContent.filter(item => 
            item.title.toLowerCase().includes(query) || 
            item.description.toLowerCase().includes(query)
        );
        
        if (results.length === 0) {
            searchResults.innerHTML = '<p>No results found for "' + query + '". Please try a different search term.</p>';
            return;
        }
        
        // Group results by category
        const groupedResults = results.reduce((acc, item) => {
            if (!acc[item.category]) {
                acc[item.category] = [];
            }
            acc[item.category].push(item);
            return acc;
        }, {});
        
        let resultsHTML = '';
        
        for (const category in groupedResults) {
            resultsHTML += `<h4>${category}</h4><ul class="search-results-list">`;
            
            groupedResults[category].forEach(item => {
                resultsHTML += `
                    <li>
                        <a href="${item.url}">
                            <div class="search-result-title">${item.title}</div>
                            <div class="search-result-description">${item.description}</div>
                        </a>
                    </li>
                `;
            });
            
            resultsHTML += '</ul>';
        }
        
        searchResults.innerHTML = resultsHTML;
    }
    
    // Fade-in animations
    const fadeElements = document.querySelectorAll('.fade-in');
    
    if (fadeElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });
        
        fadeElements.forEach(element => {
            observer.observe(element);
        });
    }
    
    // Video placeholder
    const videoPlaceholder = document.querySelector('.video-placeholder');
    
    if (videoPlaceholder) {
        videoPlaceholder.addEventListener('click', function() {
            // In a real implementation, this would load and play the actual video
            alert('Video would play here in the production version.');
        });
    }
});
