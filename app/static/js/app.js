// PocketSmart AI Global Application Script

document.addEventListener('DOMContentLoaded', () => {
    // Re-run icons
    if (window.lucide) {
        window.lucide.createIcons();
    }
});

// Format currency
function formatCurrency(amount, currency = '$') {
    return `${currency}${Number(amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

// Chart.js reusable doughnut generator
function renderBudgetChart(canvasId, labels, dataValues, backgroundColors) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    // Check if chart instance exists
    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: dataValues,
                backgroundColor: backgroundColors || [
                    '#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899', '#64748b'
                ],
                borderWidth: 2,
                borderColor: '#ffffff',
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        padding: 16,
                        font: {
                            family: "'Plus Jakarta Sans', sans-serif",
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return ` ${context.label}: $${value.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '68%'
        }
    });
}
