// Dashboard JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Set today's date as default for all date inputs
    const today = new Date().toISOString().split('T')[0];
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = today;
        }
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            // Validate numeric fields
            const numericFields = form.querySelectorAll('input[type="number"]');
            numericFields.forEach(field => {
                if (field.value && parseFloat(field.value) <= 0) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    showToast('مقادیر عددی باید بزرگتر از صفر باشند', 'error');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showToast('لطفا تمام فیلدهای الزامی را تکمیل کنید', 'error');
            }
        });
    });
    
    // Auto-complete functionality for datalists
    const dataListInputs = document.querySelectorAll('input[list]');
    dataListInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Add some visual feedback for auto-complete
            this.classList.add('autocomplete-active');
            setTimeout(() => {
                this.classList.remove('autocomplete-active');
            }, 1000);
        });
    });
    
    // Number formatting for currency inputs
    const currencyInputs = document.querySelectorAll('input[type="number"]');
    currencyInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                // Format the number with Persian separators
                const formatted = parseFloat(this.value).toLocaleString('fa-IR');
                this.setAttribute('data-formatted', formatted);
            }
        });
    });
    
    // Delete confirmation
    const deleteButtons = document.querySelectorAll('a[onclick*="confirm"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const confirmDelete = confirm('آیا از حذف این رکورد مطمئن هستید؟');
            if (confirmDelete) {
                window.location.href = this.href;
            }
        });
    });
    
    // Responsive table wrapper
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
    
    // Auto-refresh stats every 5 minutes
    setInterval(function() {
        const statsCards = document.querySelectorAll('.stats-card');
        if (statsCards.length > 0) {
            // Add a subtle animation to indicate refresh
            statsCards.forEach(card => {
                card.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    card.style.transform = 'scale(1)';
                }, 200);
            });
        }
    }, 300000); // 5 minutes
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+S to focus on first form
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const firstForm = document.querySelector('form');
            if (firstForm) {
                const firstInput = firstForm.querySelector('input, select, textarea');
                if (firstInput) {
                    firstInput.focus();
                }
            }
        }
        
        // Escape to clear all form fields
        if (e.key === 'Escape') {
            const activeElement = document.activeElement;
            if (activeElement && activeElement.tagName === 'INPUT') {
                activeElement.blur();
            }
        }
    });
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

// Utility functions
function showToast(message, type = 'info') {
    // Create toast notification
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'success'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Show toast
    if (typeof bootstrap !== 'undefined') {
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    } else {
        // Fallback for when Bootstrap JS is not available
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

function formatPersianNumber(number) {
    const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    return number.toString().replace(/\d/g, (digit) => persianDigits[digit]);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('fa-IR').format(amount) + ' تومان';
}

// Export functions for use in other modules
window.dashboardUtils = {
    showToast,
    formatPersianNumber,
    formatCurrency
};
