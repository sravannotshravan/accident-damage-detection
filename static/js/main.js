// ==================== Global Variables ====================
let isLoading = false;

// ==================== Utility Functions ====================

/**
 * Show loading spinner with custom message
 */
function showLoading(message = 'Processing...') {
    if (document.querySelector('.spinner-container')) return;
    
    const spinnerHTML = `
        <div class="spinner-container">
            <div class="spinner"></div>
            <p>${message}</p>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', spinnerHTML);
    isLoading = true;
}

/**
 * Hide loading spinner
 */
function hideLoading() {
    const spinner = document.querySelector('.spinner-container');
    if (spinner) {
        spinner.remove();
        isLoading = false;
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertHTML = `
        <div class="alert alert-${type}">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    const container = document.querySelector('.container') || document.body;
    container.insertAdjacentHTML('afterbegin', alertHTML);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        const alert = document.querySelector('.alert');
        if (alert) {
            alert.style.animation = 'slideDown 0.3s ease reverse';
            setTimeout(() => alert.remove(), 300);
        }
    }, 5000);
}

/**
 * Smooth scroll to element
 */
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * Debounce function for performance
 */
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

// ==================== Navbar Scroll Effect ====================
window.addEventListener('scroll', debounce(() => {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }
}, 10));

// ==================== Form Validation ====================

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate phone number
 */
function isValidPhone(phone) {
    const phoneRegex = /^[\d\s\-\+\(\)]+$/;
    return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10;
}

/**
 * Validate form inputs
 */
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        const value = input.value.trim();
        const errorElement = input.parentElement.querySelector('.error-message');
        
        // Remove existing error
        if (errorElement) {
            errorElement.remove();
        }

        // Validate based on type
        if (!value) {
            showFieldError(input, 'This field is required');
            isValid = false;
        } else if (input.type === 'email' && !isValidEmail(value)) {
            showFieldError(input, 'Please enter a valid email address');
            isValid = false;
        } else if (input.type === 'tel' && !isValidPhone(value)) {
            showFieldError(input, 'Please enter a valid phone number');
            isValid = false;
        } else if (input.type === 'password' && value.length < 6) {
            showFieldError(input, 'Password must be at least 6 characters');
            isValid = false;
        }
    });

    return isValid;
}

/**
 * Show field-specific error
 */
function showFieldError(input, message) {
    input.style.borderColor = '#e74c3c';
    const errorHTML = `<span class="error-message" style="color: #e74c3c; font-size: 0.875rem; margin-top: 0.25rem; display: block;">${message}</span>`;
    input.parentElement.insertAdjacentHTML('beforeend', errorHTML);
}

/**
 * Clear field errors
 */
function clearFieldErrors(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.querySelectorAll('.error-message').forEach(error => error.remove());
        form.querySelectorAll('input, select, textarea').forEach(input => {
            input.style.borderColor = '';
        });
    }
}

// ==================== Image Upload Preview ====================

/**
 * Preview uploaded image
 */
function previewImage(input, previewElementId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const preview = document.getElementById(previewElementId);
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

/**
 * Validate image file
 */
function validateImageFile(file) {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!validTypes.includes(file.type)) {
        showAlert('Please upload a valid image file (JPG, JPEG, or PNG)', 'error');
        return false;
    }

    if (file.size > maxSize) {
        showAlert('Image size should not exceed 10MB', 'error');
        return false;
    }

    return true;
}

// ==================== Drag and Drop Functionality ====================

/**
 * Initialize drag and drop for file upload
 */
function initDragAndDrop(dropZoneId, inputId) {
    const dropZone = document.getElementById(dropZoneId);
    const fileInput = document.getElementById(inputId);

    if (!dropZone || !fileInput) return;

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drag-over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drag-over');
        }, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            fileInput.files = files;
            const event = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(event);
        }
    }, false);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// ==================== Animation on Scroll ====================

/**
 * Add animation class when element is in viewport
 */
function animateOnScroll() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    }, {
        threshold: 0.1
    });

    elements.forEach(element => {
        observer.observe(element);
    });
}

// ==================== Statistics Counter Animation ====================

/**
 * Animate numbers counting up
 */
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = Math.round(target);
            clearInterval(timer);
        } else {
            element.textContent = Math.round(start);
        }
    }, 16);
}

// ==================== Copy to Clipboard ====================

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showAlert('Copied to clipboard!', 'success');
    } catch (err) {
        console.error('Failed to copy:', err);
        showAlert('Failed to copy to clipboard', 'error');
    }
}

// ==================== Print Functionality ====================

/**
 * Print current page
 */
function printPage() {
    window.print();
}

/**
 * Generate PDF (requires additional library)
 */
function generatePDF(elementId, filename = 'document.pdf') {
    showAlert('PDF generation feature coming soon!', 'info');
}

// ==================== Local Storage Helpers ====================

/**
 * Save to local storage
 */
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (e) {
        console.error('Error saving to localStorage:', e);
        return false;
    }
}

/**
 * Get from local storage
 */
function getFromLocalStorage(key) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    } catch (e) {
        console.error('Error reading from localStorage:', e);
        return null;
    }
}

/**
 * Remove from local storage
 */
function removeFromLocalStorage(key) {
    try {
        localStorage.removeItem(key);
        return true;
    } catch (e) {
        console.error('Error removing from localStorage:', e);
        return false;
    }
}

// ==================== Initialize on Page Load ====================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize animations
    animateOnScroll();
    
    // Add smooth scrolling to all links with #
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            smoothScrollTo(targetId);
        });
    });

    // Auto-hide flash messages
    setTimeout(() => {
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(msg => {
            msg.style.animation = 'slideDown 0.3s ease reverse';
            setTimeout(() => msg.remove(), 300);
        });
    }, 5000);

    // Add active class to current nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-links a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

// ==================== Export Functions ====================
window.appUtils = {
    showLoading,
    hideLoading,
    showAlert,
    smoothScrollTo,
    validateForm,
    clearFieldErrors,
    previewImage,
    validateImageFile,
    initDragAndDrop,
    copyToClipboard,
    printPage,
    saveToLocalStorage,
    getFromLocalStorage,
    removeFromLocalStorage
};
