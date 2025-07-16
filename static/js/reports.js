// Reports JavaScript functionality
let expenseChart = null;
let trendChart = null;

function initializeCharts(financialData, materialsData, salesData) {
    // Initialize expense distribution chart
    initializeExpenseChart(financialData);
    
    // Initialize trend chart
    initializeTrendChart(materialsData, salesData);
    
    // Update charts when date filter changes
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.addEventListener('change', function() {
            // Debounce the chart update
            clearTimeout(window.chartUpdateTimeout);
            window.chartUpdateTimeout = setTimeout(updateCharts, 500);
        });
    });
}

function initializeExpenseChart(financialData) {
    const ctx = document.getElementById('expenseChart');
    if (!ctx) return;
    
    const data = {
        labels: ['مواد اولیه', 'تولید', 'سایر هزینه‌ها', 'حقوق کارگران'],
        datasets: [{
            data: [
                financialData.materials_cost,
                financialData.production_cost,
                financialData.expenses,
                financialData.worker_wages
            ],
            backgroundColor: [
                '#FF6384',
                '#36A2EB',
                '#FFCE56',
                '#4BC0C0'
            ],
            borderColor: [
                '#FF6384',
                '#36A2EB',
                '#FFCE56',
                '#4BC0C0'
            ],
            borderWidth: 2
        }]
    };
    
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    usePointStyle: true,
                    padding: 20,
                    font: {
                        family: 'Tahoma',
                        size: 12
                    }
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const value = context.raw;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = ((value / total) * 100).toFixed(1);
                        return `${context.label}: ${formatCurrency(value)} (${percentage}%)`;
                    }
                },
                titleFont: {
                    family: 'Tahoma'
                },
                bodyFont: {
                    family: 'Tahoma'
                }
            }
        }
    };
    
    if (expenseChart) {
        expenseChart.destroy();
    }
    
    expenseChart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: options
    });
}

function initializeTrendChart(materialsData, salesData) {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;
    
    // Combine and sort data by date
    const allDates = new Set();
    materialsData.forEach(item => allDates.add(item.date));
    salesData.forEach(item => allDates.add(item.date));
    
    const sortedDates = Array.from(allDates).sort();
    
    // Create datasets
    const materialsDataset = sortedDates.map(date => {
        const item = materialsData.find(d => d.date === date);
        return item ? item.total_cost : 0;
    });
    
    const salesDataset = sortedDates.map(date => {
        const item = salesData.find(d => d.date === date);
        return item ? item.total_revenue : 0;
    });
    
    // Format dates for display
    const formattedDates = sortedDates.map(date => {
        const dateObj = new Date(date);
        return `${dateObj.getFullYear()}/${(dateObj.getMonth() + 1).toString().padStart(2, '0')}/${dateObj.getDate().toString().padStart(2, '0')}`;
    });
    
    const data = {
        labels: formattedDates,
        datasets: [
            {
                label: 'درآمد',
                data: salesDataset,
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4,
                fill: false
            },
            {
                label: 'هزینه مواد',
                data: materialsDataset,
                borderColor: '#dc3545',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                tension: 0.4,
                fill: false
            }
        ]
    };
    
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 20,
                    font: {
                        family: 'Tahoma',
                        size: 12
                    }
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return `${context.dataset.label}: ${formatCurrency(context.raw)}`;
                    }
                },
                titleFont: {
                    family: 'Tahoma'
                },
                bodyFont: {
                    family: 'Tahoma'
                }
            }
        },
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: 'تاریخ',
                    font: {
                        family: 'Tahoma',
                        size: 12
                    }
                },
                ticks: {
                    font: {
                        family: 'Tahoma',
                        size: 10
                    }
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: 'مبلغ (تومان)',
                    font: {
                        family: 'Tahoma',
                        size: 12
                    }
                },
                ticks: {
                    callback: function(value) {
                        return formatCurrency(value);
                    },
                    font: {
                        family: 'Tahoma',
                        size: 10
                    }
                }
            }
        }
    };
    
    if (trendChart) {
        trendChart.destroy();
    }
    
    trendChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: options
    });
}

function updateCharts() {
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;
    
    // Show loading indicators
    showChartLoading();
    
    // Fetch updated data
    fetch(`/api/chart-data?start_date=${startDate}&end_date=${endDate}`)
        .then(response => response.json())
        .then(data => {
            // Update charts with new data
            updateTrendChartData(data);
            hideChartLoading();
        })
        .catch(error => {
            console.error('Error updating charts:', error);
            hideChartLoading();
            showToast('خطا در به‌روزرسانی نمودارها', 'error');
        });
}

function updateTrendChartData(data) {
    if (!trendChart) return;
    
    // Process revenue data
    const revenueData = data.revenue || [];
    const expenseData = data.expenses || [];
    
    // Get unique months
    const months = new Set();
    revenueData.forEach(item => months.add(item.month));
    expenseData.forEach(item => months.add(item.month));
    
    const sortedMonths = Array.from(months).sort();
    
    // Create datasets
    const revenueDataset = sortedMonths.map(month => {
        const item = revenueData.find(d => d.month === month);
        return item ? item.value : 0;
    });
    
    const expenseDataset = sortedMonths.map(month => {
        const item = expenseData.find(d => d.month === month);
        return item ? item.value : 0;
    });
    
    // Format month labels
    const formattedMonths = sortedMonths.map(month => {
        const date = new Date(month);
        return `${date.getFullYear()}/${(date.getMonth() + 1).toString().padStart(2, '0')}`;
    });
    
    // Update chart data
    trendChart.data.labels = formattedMonths;
    trendChart.data.datasets[0].data = revenueDataset;
    trendChart.data.datasets[1].data = expenseDataset;
    
    trendChart.update();
}

function showChartLoading() {
    const charts = document.querySelectorAll('canvas');
    charts.forEach(chart => {
        chart.style.opacity = '0.5';
    });
}

function hideChartLoading() {
    const charts = document.querySelectorAll('canvas');
    charts.forEach(chart => {
        chart.style.opacity = '1';
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('fa-IR').format(amount);
}

function showToast(message, type = 'info') {
    // Use the same toast function from dashboard.js
    if (window.dashboardUtils && window.dashboardUtils.showToast) {
        window.dashboardUtils.showToast(message, type);
    } else {
        // Fallback alert
        alert(message);
    }
}

// Export PDF functionality
function exportToPDF() {
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;
    
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    window.open(`/export-pdf?${params.toString()}`, '_blank');
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Charts will be initialized by the template script
    
    // Add event listeners for export buttons
    const exportBtn = document.querySelector('a[href*="export-pdf"]');
    if (exportBtn) {
        exportBtn.addEventListener('click', function(e) {
            e.preventDefault();
            exportToPDF();
        });
    }
    
    // Add responsive chart handling
    window.addEventListener('resize', function() {
        if (expenseChart) expenseChart.resize();
        if (trendChart) trendChart.resize();
    });
});
