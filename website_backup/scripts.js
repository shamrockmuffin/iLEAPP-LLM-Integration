// JavaScript for iLEAPP AI Website

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Offset for header
                    behavior: 'smooth'
                });
            }
        });
    });

    // Mobile navigation toggle
    const createMobileNav = () => {
        const header = document.querySelector('header');
        const nav = document.querySelector('nav');
        
        // Create mobile nav toggle button
        const mobileToggle = document.createElement('button');
        mobileToggle.classList.add('mobile-nav-toggle');
        mobileToggle.innerHTML = '<i class="fas fa-bars"></i>';
        header.insertBefore(mobileToggle, nav);
        
        // Add mobile nav class to nav
        nav.classList.add('desktop-nav');
        
        // Toggle mobile nav
        mobileToggle.addEventListener('click', function() {
            nav.classList.toggle('active');
            if (nav.classList.contains('active')) {
                mobileToggle.innerHTML = '<i class="fas fa-times"></i>';
            } else {
                mobileToggle.innerHTML = '<i class="fas fa-bars"></i>';
            }
        });
        
        // Close mobile nav when clicking outside
        document.addEventListener('click', function(e) {
            if (!nav.contains(e.target) && !mobileToggle.contains(e.target)) {
                nav.classList.remove('active');
                mobileToggle.innerHTML = '<i class="fas fa-bars"></i>';
            }
        });
    };
    
    // Only create mobile nav on smaller screens
    if (window.innerWidth < 992) {
        createMobileNav();
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth < 992) {
            if (!document.querySelector('.mobile-nav-toggle')) {
                createMobileNav();
            }
        }
    });

    // Screenshot lightbox functionality
    const screenshots = document.querySelectorAll('.screenshot');
    
    screenshots.forEach(screenshot => {
        screenshot.addEventListener('click', function() {
            const img = this.querySelector('img');
            const caption = this.querySelector('p').textContent;
            
            // Create lightbox
            const lightbox = document.createElement('div');
            lightbox.classList.add('lightbox');
            
            // Create lightbox content
            lightbox.innerHTML = `
                <div class="lightbox-content">
                    <span class="close">&times;</span>
                    <img src="${img.src}" alt="${img.alt}">
                    <p>${caption}</p>
                </div>
            `;
            
            // Add lightbox to body
            document.body.appendChild(lightbox);
            
            // Prevent scrolling
            document.body.style.overflow = 'hidden';
            
            // Close lightbox
            lightbox.querySelector('.close').addEventListener('click', function() {
                document.body.removeChild(lightbox);
                document.body.style.overflow = '';
            });
            
            // Close lightbox when clicking outside
            lightbox.addEventListener('click', function(e) {
                if (e.target === lightbox) {
                    document.body.removeChild(lightbox);
                    document.body.style.overflow = '';
                }
            });
        });
    });

    // Video placeholder functionality
    const videoPlaceholder = document.querySelector('.video-placeholder');
    
    if (videoPlaceholder) {
        videoPlaceholder.addEventListener('click', function() {
            // Replace with actual video embed
            const videoEmbed = document.createElement('div');
            videoEmbed.classList.add('video-embed');
            videoEmbed.innerHTML = `
                <iframe width="100%" height="350" src="https://www.youtube.com/embed/dQw4w9WgXcQ" 
                frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; 
                gyroscope; picture-in-picture" allowfullscreen></iframe>
            `;
            
            // Replace placeholder with embed
            this.parentNode.replaceChild(videoEmbed, this);
        });
    }

    // Animate elements on scroll
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.feature-card, .workflow-step, .integration-card, .doc-card, .resource-card');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.3;
            
            if (elementPosition < screenPosition) {
                element.classList.add('animate');
            }
        });
    };
    
    // Add animation class to CSS
    const style = document.createElement('style');
    style.textContent = `
        .feature-card, .workflow-step, .integration-card, .doc-card, .resource-card {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.5s ease, transform 0.5s ease;
        }
        
        .feature-card.animate, .workflow-step.animate, .integration-card.animate, .doc-card.animate, .resource-card.animate {
            opacity: 1;
            transform: translateY(0);
        }
        
        .lightbox {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1001;
        }
        
        .lightbox-content {
            position: relative;
            max-width: 80%;
            max-height: 80%;
        }
        
        .lightbox-content img {
            max-width: 100%;
            max-height: 80vh;
            border-radius: 8px;
        }
        
        .lightbox-content p {
            color: white;
            text-align: center;
            margin-top: 1rem;
        }
        
        .close {
            position: absolute;
            top: -30px;
            right: 0;
            color: white;
            font-size: 30px;
            cursor: pointer;
        }
        
        @media (max-width: 992px) {
            header {
                position: relative;
            }
            
            .mobile-nav-toggle {
                display: block;
                background: none;
                border: none;
                font-size: 1.5rem;
                cursor: pointer;
                color: var(--dark-color);
            }
            
            .desktop-nav {
                display: none;
                width: 100%;
                padding: 1rem 0;
            }
            
            .desktop-nav.active {
                display: block;
            }
            
            .desktop-nav ul {
                flex-direction: column;
                align-items: center;
            }
            
            .desktop-nav ul li {
                margin: 0.5rem 0;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Run animation on scroll
    window.addEventListener('scroll', animateOnScroll);
    
    // Run animation on load
    animateOnScroll();
});
