// ============================================
// Diabetes Track AI - JavaScript Functions
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all features
    initializeFormHandling();
    initializeScrollAnimations();
    initializeTooltips();
    initializeSmoothTransitions();
    
    // Set up navigation highlights
    updateActiveNavLink();
    window.addEventListener('load', updateActiveNavLink);
});

// ============================================
// FORM HANDLING
// ============================================

function initializeFormHandling() {
    const assessmentForm = document.getElementById('assessmentForm');
    
    if (assessmentForm) {
        assessmentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate form
            if (!this.checkValidity()) {
                e.stopPropagation();
                this.classList.add('was-validated');
                return;
            }
            
            // Show loading modal
            const loadingModal = document.getElementById('loadingModal');
            if (loadingModal) {
                const modal = new bootstrap.Modal(loadingModal);
                modal.show();
                
                // Add small delay for visual effect
                setTimeout(() => {
                    this.submit();
                }, 500);
            } else {
                this.submit();
            }
        });

        // Add smooth input focus effects
        const inputs = assessmentForm.querySelectorAll('.form-control, .form-select');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.classList.add('shadow-sm');
            });
            
            input.addEventListener('blur', function() {
                this.classList.remove('shadow-sm');
            });
        });
    }
}

// ============================================
// SCROLL ANIMATIONS
// ============================================

function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fadeInUp');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all cards and feature boxes
    document.querySelectorAll('.card, .health-card, .stat-box, .feature-box').forEach(element => {
        observer.observe(element);
    });
}

// ============================================
// NAVIGATION HIGHLIGHTING
// ============================================

function updateActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        
        if ((currentPath === '/' && href === '/') ||
            (currentPath !== '/' && href === currentPath)) {
            link.classList.add('active');
        }
    });
}

// ============================================
// TOOLTIPS INITIALIZATION
// ============================================

function initializeTooltips() {
    // Initialize Bootstrap tooltips if present
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// ============================================
// SMOOTH TRANSITIONS
// ============================================

function initializeSmoothTransitions() {
    // Add smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Add button ripple effect
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            this.appendChild(ripple);
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

// ============================================
// CHART UTILITIES
// ============================================

function generateChartGradient(ctx, color1, color2) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, color1);
    gradient.addColorStop(1, color2);
    return gradient;
}

// ============================================
// EXPORT FUNCTIONS
// ============================================

function exportToPDF() {
    window.print();
    return false;
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

// Format date to readable string
function formatDate(date) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(date).toLocaleDateString(undefined, options);
}

// Show notification
function showNotification(message, type = 'success', duration = 3000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    if (duration) {
        setTimeout(() => {
            alertDiv.remove();
        }, duration);
    }
}

// ============================================
// LOADING STATE
// ============================================

function setLoadingState(element, isLoading) {
    if (isLoading) {
        element.disabled = true;
        element.classList.add('disabled');
        element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    } else {
        element.disabled = false;
        element.classList.remove('disabled');
    }
}

// ============================================
// KEYBOARD SHORTCUTS
// ============================================

document.addEventListener('keydown', function(event) {
    // Alt + A: Go to Assessment
    if (event.altKey && event.key === 'a') {
        window.location.href = '/assessment';
    }
    // Alt + H: Go to Home
    if (event.altKey && event.key === 'h') {
        window.location.href = '/';
    }
    // Escape: Close modals
    if (event.key === 'Escape') {
        const modals = bootstrap.Modal.getInstance(document.querySelector('.modal.show'));
        if (modals) {
            modals.hide();
        }
    }
});

// ============================================
// PERFORMANCE OPTIMIZATION
// ============================================

// Debounce function for resize/scroll events
function debounce(func, wait) {
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

// Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ============================================
// PAGE VISIBILITY HANDLER
// ============================================

document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        console.log('Page hidden - pausing animations');
    } else {
        console.log('Page visible - resuming animations');
    }
});

// ============================================
// CONSOLE MESSAGES
// ============================================

console.log('%c🏥 Diabetes Track AI', 'font-size: 20px; font-weight: bold; color: #1e3a8a;');
console.log('%cWelcome to the Diabetes Risk Assessment System', 'font-size: 14px; color: #3b82f6;');
console.log('%cFor educational and research purposes only.', 'font-size: 12px; color: #666;');