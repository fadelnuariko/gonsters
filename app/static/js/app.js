// Global app JavaScript

// Auto-refresh functionality for monitoring pages
let autoRefreshInterval = null;

function startAutoRefresh(callback, interval = 5000) {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    autoRefreshInterval = setInterval(callback, interval);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Confirm delete actions
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// Show loading spinner
function showLoading() {
    const spinner = `
        <div class="spinner-overlay" id="loadingSpinner">
            <div class="spinner-border spinner-border-custom text-light" role="status">
                <span class="sr-only">Loading...</span>
            </div>
        </div>
    `;
    $('body').append(spinner);
}

function hideLoading() {
    $('#loadingSpinner').remove();
}

// Format timestamp
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Auto-dismiss alerts after 5 seconds
$(document).ready(function() {
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Add confirmation to delete buttons
    $('.btn-delete').on('click', function(e) {
        if (!confirmDelete()) {
            e.preventDefault();
            return false;
        }
    });
});

// AJAX helper function
function apiCall(url, method = 'GET', data = null, token = null) {
    const options = {
        url: url,
        method: method,
        dataType: 'json'
    };
    
    if (token) {
        options.headers = {
            'Authorization': `Bearer ${token}`
        };
    }
    
    if (data) {
        options.data = JSON.stringify(data);
        options.contentType = 'application/json';
    }
    
    return $.ajax(options);
}

// Export functions for use in other scripts
window.appUtils = {
    startAutoRefresh,
    stopAutoRefresh,
    confirmDelete,
    showLoading,
    hideLoading,
    formatTimestamp,
    formatNumber,
    apiCall
};
