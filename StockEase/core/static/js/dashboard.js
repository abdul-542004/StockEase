document.addEventListener('DOMContentLoaded', function () {
    // Pie Chart for Category Distribution
    const pieCtx = document.getElementById('categoryPieChart').getContext('2d');
    const pieColors = [
        '#6366F1', '#60A5FA', '#34D399', '#FBBF24', '#F87171', '#A78BFA', '#F472B6', '#FCD34D', '#6EE7B7', '#93C5FD'
    ];
    if (window.dashboardData && pieCtx) {
        new Chart(pieCtx, {
            type: 'pie',
            data: {
                labels: window.dashboardData.categories,
                datasets: [{
                    data: window.dashboardData.categoryCounts,
                    backgroundColor: pieColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#374151', font: { size: 14 } }
                    }
                }
            }
        });
    }

    // Line Chart for Sales Order Graph
    const salesCtx = document.getElementById('salesOrderGraph').getContext('2d');
    if (window.dashboardData && salesCtx) {
        new Chart(salesCtx, {
            type: 'line',
            data: {
                labels: window.dashboardData.salesDates,
                datasets: [{
                    label: 'Sales (PKR)',
                    data: window.dashboardData.salesAmounts,
                    fill: true,
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderColor: '#6366F1',
                    tension: 0.3,
                    pointBackgroundColor: '#6366F1',
                    pointBorderColor: '#fff',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#6B7280' },
                        grid: { color: '#F3F4F6' }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#6B7280' },
                        grid: { color: '#F3F4F6' }
                    }
                }
            }
        });
    }
});