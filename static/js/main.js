// SmartEdu AI Main JavaScript File

// Global Variables
let currentUser = null;
let systemSettings = {};

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Load user data
    loadUserData();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize charts if on dashboard
    if (window.location.pathname.includes('dashboard')) {
        initializeDashboardCharts();
    }
    
    // Auto-refresh functionality
    setupAutoRefresh();
    
    console.log('SmartEdu AI Application Initialized');
}

// User Management
function loadUserData() {
    // This would fetch user data from the API
    const userStr = localStorage.getItem('currentUser');
    if (userStr) {
        currentUser = JSON.parse(userStr);
        updateUserInterface();
    }
}

function updateUserInterface() {
    if (currentUser) {
        // Update UI elements based on user role
        const roleElements = document.querySelectorAll('[data-role]');
        roleElements.forEach(element => {
            const requiredRoles = element.dataset.role.split(',');
            if (!requiredRoles.includes(currentUser.role)) {
                element.style.display = 'none';
            }
        });
    }
}

// UI Components
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function setupEventListeners() {
    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('change', toggleTheme);
    }
    
    // Form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // Dynamic content loading
    const navLinks = document.querySelectorAll('.nav-link[data-load]');
    navLinks.forEach(link => {
        link.addEventListener('click', handleNavigation);
    });
}

// Authentication
function handleLogout(e) {
    e.preventDefault();
    
    // Clear user data
    localStorage.removeItem('currentUser');
    currentUser = null;
    
    // Redirect to login
    window.location.href = '/login';
}

// Theme Management
function toggleTheme(e) {
    const isDark = e.target.checked;
    document.body.classList.toggle('dark-theme', isDark);
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

// Form Handling
function handleFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Show loading state
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    }
    
    // Add AJAX header for JSON response
    const headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json',
        'X-CSRFToken': getCsrfToken()
    };
    
    // Submit form data
    fetch(form.action, {
        method: form.method,
        body: formData,
        headers: headers
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(response => {
        if (response.success) {
            showNotification('success', response.message || 'Login successful');
            // Store user info in localStorage for debugging
            if (response.user) {
                localStorage.setItem('currentUser', JSON.stringify(response.user));
            }
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = response.redirect;
            }, 1000);
        } else {
            showNotification('error', response.message || 'Invalid credentials');
        }
    })
    .catch(error => {
        console.error('Form submission error:', error);
        // More detailed error logging
        console.error('Error details:', {
            message: error.message,
            stack: error.stack,
            status: error.status
        });
        
        // Show specific error messages
        if (error.status === 401) {
            showNotification('error', 'Invalid username or password');
        } else if (error.status === 500) {
            showNotification('error', 'Server error. Please try again later.');
        } else if (error.status === 0) {
            showNotification('error', 'Network error. Please check your connection.');
        } else {
            showNotification('error', 'Network error. Please try again.');
        }
    })
    .finally(() => {
        // Reset button state
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = submitBtn.dataset.originalText || 'Submit';
        }
    });
}

async function submitForm(formData, url, method = 'POST') {
    try {
        const response = await fetch(url, {
            method: method,
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        });
        
        return await response.json();
    } catch (error) {
        throw error;
    }
}

// CSRF Token Helper
function getCsrfToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

// Navigation
function handleNavigation(e) {
    e.preventDefault();
    
    const link = e.target;
    const targetUrl = link.dataset.load;
    
    // Show loading indicator
    showLoadingIndicator();
    
    // Load content dynamically
    loadContent(targetUrl)
        .then(html => {
            const contentContainer = document.getElementById('content-container');
            if (contentContainer) {
                contentContainer.innerHTML = html;
                initializePageComponents();
            }
        })
        .catch(error => {
            console.error('Content loading error:', error);
            showNotification('error', 'Failed to load content');
        })
        .finally(() => {
            hideLoadingIndicator();
        });
}

async function loadContent(url) {
    try {
        const response = await fetch(url);
        return await response.text();
    } catch (error) {
        throw error;
    }
}

// Notifications
function showNotification(type, message, duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-dismiss
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

// Loading Indicators
function showLoadingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'loading-indicator';
    indicator.className = 'position-fixed top-50 start-50 translate-middle';
    indicator.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(indicator);
}

function hideLoadingIndicator() {
    const indicator = document.getElementById('loading-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Dashboard Functions
function initializeDashboardCharts() {
    // Initialize performance charts
    initializePerformanceChart();
    initializeAttendanceChart();
    initializeRiskChart();
}

function initializePerformanceChart() {
    const ctx = document.getElementById('performanceChart');
    if (ctx) {
        // Chart initialization would go here
        console.log('Performance chart initialized');
    }
}

function initializeAttendanceChart() {
    const ctx = document.getElementById('attendanceChart');
    if (ctx) {
        // Chart initialization would go here
        console.log('Attendance chart initialized');
    }
}

function initializeRiskChart() {
    const ctx = document.getElementById('riskChart');
    if (ctx) {
        // Chart initialization would go here
        console.log('Risk chart initialized');
    }
}

// Data Management
function refreshData() {
    const currentPath = window.location.pathname;
    
    if (currentPath.includes('dashboard')) {
        refreshDashboardData();
    } else if (currentPath.includes('analytics')) {
        refreshAnalyticsData();
    } else if (currentPath.includes('attendance')) {
        refreshAttendanceData();
    }
}

function refreshDashboardData() {
    // Fetch latest dashboard data
    fetch('/api/dashboard-data')
        .then(response => response.json())
        .then(data => {
            updateDashboardUI(data);
        })
        .catch(error => {
            console.error('Dashboard data refresh error:', error);
        });
}

function refreshAnalyticsData() {
    // Fetch latest analytics data
    fetch('/api/analytics-data')
        .then(response => response.json())
        .then(data => {
            updateAnalyticsUI(data);
        })
        .catch(error => {
            console.error('Analytics data refresh error:', error);
        });
}

function refreshAttendanceData() {
    // Fetch latest attendance data
    fetch('/api/attendance-data')
        .then(response => response.json())
        .then(data => {
            updateAttendanceUI(data);
        })
        .catch(error => {
            console.error('Attendance data refresh error:', error);
        });
}

function updateDashboardUI(data) {
    // Update dashboard UI with new data
    Object.keys(data).forEach(key => {
        const element = document.getElementById(key);
        if (element) {
            element.textContent = data[key];
        }
    });
}

function updateAnalyticsUI(data) {
    // Update analytics charts with new data
    // This would update Chart.js instances
    console.log('Analytics UI updated with data:', data);
}

function updateAttendanceUI(data) {
    // Update attendance UI with new data
    console.log('Attendance UI updated with data:', data);
}

// Auto-refresh
function setupAutoRefresh() {
    // Set up automatic data refresh
    setInterval(() => {
        if (document.visibilityState === 'visible') {
            refreshData();
        }
    }, 60000); // Refresh every minute
}

// Face Recognition Functions
function startFaceRecognition() {
    const video = document.getElementById('videoElement');
    if (video) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video.srcObject = stream;
                // Start face recognition processing
                processFaceRecognition();
            })
            .catch(error => {
                console.error('Camera access error:', error);
                showNotification('error', 'Unable to access camera');
            });
    }
}

function stopFaceRecognition() {
    const video = document.getElementById('videoElement');
    if (video && video.srcObject) {
        const stream = video.srcObject;
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
        video.srcObject = null;
    }
}

function processFaceRecognition() {
    // Face recognition processing would go here
    // This is a placeholder for the actual face recognition logic
    console.log('Face recognition processing started');
}

// Utility Functions
function getCsrfToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
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

// Error Handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showNotification('error', 'An unexpected error occurred');
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showNotification('error', 'A network error occurred');
});

// Performance Monitoring
function logPerformance() {
    if (window.performance && window.performance.timing) {
        const timing = window.performance.timing;
        const loadTime = timing.loadEventEnd - timing.navigationStart;
        console.log('Page load time:', loadTime + 'ms');
    }
}

// Log performance on page load
window.addEventListener('load', logPerformance);

// Service Worker Registration (for PWA support)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Export functions for use in other scripts
window.SmartEdu = {
    showNotification,
    showLoadingIndicator,
    hideLoadingIndicator,
    refreshData,
    startFaceRecognition,
    stopFaceRecognition,
    formatBytes,
    formatDate,
    debounce
};
