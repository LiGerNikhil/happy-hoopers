// ══════════════════════════════════════════
// MAIN JAVASCRIPT FUNCTIONALITY
// ══════════════════════════════════════════

// Toast notification system
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    
    toast.textContent = message;
    toast.className = 'show';
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Reveal animations on scroll
function attachReveal() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.reveal, .reveal-l, .reveal-r').forEach(el => {
        observer.observe(el);
    });
}

// Counter animations
function attachCounters() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersectable && !entry.target.dataset.animated) {
                entry.target.dataset.animated = 'true';
                const target = parseInt(entry.target.dataset.target);
                const start = performance.now();
                
                function updateCounter(now) {
                    const progress = Math.min((now - start) / 1800, 1);
                    const easeOut = 1 - Math.pow(1 - progress, 3);
                    const current = Math.round(easeOut * target);
                    
                    entry.target.textContent = current.toLocaleString('en-IN');
                    
                    if (progress < 1) {
                        requestAnimationFrame(updateCounter);
                    }
                }
                
                requestAnimationFrame(updateCounter);
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.stat-num').forEach(el => {
        observer.observe(el);
    });
}

// Header scroll effect
function initHeaderScroll() {
    const header = document.getElementById('site-header');
    if (!header) return;

    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
        
        lastScroll = currentScroll;
    });
}

// Smooth scroll for anchor links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Slot selection for cricket booking
function selectSlot(element, duration, price) {
    document.querySelectorAll('.slot-card').forEach(card => {
        card.classList.remove('active');
    });
    element.classList.add('active');
    
    // Update hidden form fields if they exist
    const durationField = document.getElementById('id_duration_minutes');
    const costField = document.getElementById('id_cost');
    
    if (durationField) durationField.value = duration;
    if (costField) costField.value = price;
}

// Cafe filtering
function filterCafe(category, btn) {
    document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    const cards = document.querySelectorAll('.cafe-card');
    cards.forEach(card => {
        const cardCategory = card.dataset.category || 'All';
        if (category === 'All' || cardCategory === category) {
            card.style.display = 'block';
            setTimeout(() => card.classList.add('visible'), 100);
        } else {
            card.style.display = 'none';
        }
    });
}

// Gallery image modal
function initGalleryModal() {
    const modal = document.createElement('div');
    modal.className = 'gallery-modal';
    modal.innerHTML = `
        <div class="gallery-modal-content">
            <span class="gallery-modal-close">&times;</span>
            <img src="" alt="">
            <div class="gallery-modal-caption"></div>
        </div>
    `;
    
    // Add modal styles
    const style = document.createElement('style');
    style.textContent = `
        .gallery-modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
            animation: fadeIn 0.3s;
        }
        .gallery-modal-content {
            position: relative;
            margin: auto;
            padding: 20px;
            width: 90%;
            max-width: 800px;
            top: 50%;
            transform: translateY(-50%);
        }
        .gallery-modal-close {
            position: absolute;
            top: 10px;
            right: 25px;
            color: white;
            font-size: 35px;
            font-weight: bold;
            cursor: pointer;
        }
        .gallery-modal img {
            width: 100%;
            height: auto;
            border-radius: 8px;
        }
        .gallery-modal-caption {
            color: white;
            text-align: center;
            margin-top: 15px;
            font-size: 16px;
        }
        @keyframes fadeIn {
            from {opacity: 0}
            to {opacity: 1}
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(modal);
    
    // Add click handlers
    const modalImg = modal.querySelector('img');
    const caption = modal.querySelector('.gallery-modal-caption');
    const closeBtn = modal.querySelector('.gallery-modal-close');
    
    document.querySelectorAll('.gal-item').forEach(item => {
        item.addEventListener('click', () => {
            const img = item.querySelector('img');
            const label = item.querySelector('.gal-label');
            
            modal.style.display = 'block';
            modalImg.src = img.src;
            caption.textContent = label ? label.textContent : '';
        });
    });
    
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Form validation helpers
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('error');
            
            // Add error message if not exists
            if (!input.nextElementSibling || !input.nextElementSibling.classList.contains('error-message')) {
                const errorMsg = document.createElement('span');
                errorMsg.className = 'error-message';
                errorMsg.textContent = 'This field is required';
                errorMsg.style.color = '#EF4444';
                errorMsg.style.fontSize = '12px';
                errorMsg.style.marginTop = '4px';
                input.parentNode.insertBefore(errorMsg, input.nextSibling);
            }
        } else {
            input.classList.remove('error');
            const errorMsg = input.nextElementSibling;
            if (errorMsg && errorMsg.classList.contains('error-message')) {
                errorMsg.remove();
            }
        }
    });
    
    return isValid;
}

// Phone number validation
function validatePhone(input) {
    const phone = input.value.replace(/\D/g, '');
    if (phone.length !== 10) {
        input.classList.add('error');
        return false;
    }
    input.classList.remove('error');
    return true;
}

// Email validation
function validateEmail(input) {
    const email = input.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!emailRegex.test(email)) {
        input.classList.add('error');
        return false;
    }
    input.classList.remove('error');
    return true;
}

// Dynamic content loading via AJAX
async function loadContent(url, targetId) {
    try {
        const response = await fetch(url);
        const html = await response.text();
        const target = document.getElementById(targetId);
        if (target) {
            target.innerHTML = html;
            // Re-initialize any scripts that might be needed
            if (typeof attachReveal === 'function') attachReveal();
        }
    } catch (error) {
        console.error('Error loading content:', error);
        showToast('Failed to load content', 'error');
    }
}

// Cricket availability checker
async function checkCricketAvailability(date) {
    try {
        const formData = new FormData();
        formData.append('date', date);
        
        const response = await fetch('/check-cricket-availability/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        
        const data = await response.json();
        return data.available_slots || [];
    } catch (error) {
        console.error('Error checking availability:', error);
        return [];
    }
}

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    attachReveal();
    attachCounters();
    initHeaderScroll();
    initSmoothScroll();
    initGalleryModal();
    
    // Add form validation listeners
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form.id)) {
                e.preventDefault();
                showToast('Please fill in all required fields', 'error');
            }
        });
    });
    
    // Phone number validation
    document.querySelectorAll('input[type="tel"]').forEach(input => {
        input.addEventListener('blur', () => validatePhone(input));
        input.addEventListener('input', (e) => {
            // Only allow numbers
            e.target.value = e.target.value.replace(/\D/g, '');
        });
    });
    
    // Email validation
    document.querySelectorAll('input[type="email"]').forEach(input => {
        input.addEventListener('blur', () => validateEmail(input));
    });
    
    // Auto-hide messages after 5 seconds
    setTimeout(() => {
        document.querySelectorAll('.message').forEach(msg => {
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 300);
        });
    }, 5000);
    
    // Initialize any dynamic content
    if (typeof loadGames === 'function') {
        loadGames();
    }
});

// Utility functions
function formatTime(time) {
    if (!time) return '';
    const [hours, minutes] = time.split(':').map(Number);
    const period = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;
    const displayMinutes = minutes < 10 ? '0' + minutes : minutes;
    return `${displayHours}:${displayMinutes} ${period}`;
}

function formatDate(date) {
    const options = { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' };
    return new Date(date).toLocaleDateString('en-IN', options);
}

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

// Mobile menu toggle (if needed)
function toggleMobileMenu() {
    const nav = document.querySelector('.nav-links');
    if (nav) {
        nav.classList.toggle('mobile-open');
    }
}

// Print functionality
function printPage() {
    window.print();
}

// Share functionality
function sharePage(title, url) {
    if (navigator.share) {
        navigator.share({
            title: title,
            url: url
        });
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(url).then(() => {
            showToast('Link copied to clipboard!', 'success');
        });
    }
}

// Export functions for global access
window.showToast = showToast;
window.selectSlot = selectSlot;
window.filterCafe = filterCafe;
window.validateForm = validateForm;
window.checkCricketAvailability = checkCricketAvailability;
window.loadContent = loadContent;
window.formatTime = formatTime;
window.formatDate = formatDate;
window.sharePage = sharePage;
window.printPage = printPage;
