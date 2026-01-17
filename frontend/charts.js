

let lineChart, barChart, pieChart, areaChart, radarChart, horizontalBarChart;

const chartColors = {
    primary: 'rgb(6, 182, 212)',
    primaryLight: 'rgba(6, 182, 212, 0.8)',
    primaryTransparent: 'rgba(6, 182, 212, 0.2)',
    secondary: 'rgb(59, 130, 246)',
    secondaryLight: 'rgba(59, 130, 246, 0.8)',
    success: 'rgb(16, 185, 129)',
    warning: 'rgb(245, 158, 11)',
    danger: 'rgb(239, 68, 68)',
    info: 'rgb(59, 130, 246)',
    teal: 'rgb(20, 184, 166)',
    text: '#f1f5f9',
    grid: 'rgba(255, 255, 255, 0.1)'
};

const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                color: chartColors.text,
                font: {
                    family: 'Inter',
                    size: 12
                },
                padding: 15
            }
        },
        tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            titleColor: chartColors.text,
            bodyColor: chartColors.text,
            borderColor: chartColors.primary,
            borderWidth: 1,
            padding: 12,
            cornerRadius: 8,
            titleFont: {
                size: 14,
                weight: 'bold'
            },
            bodyFont: {
                size: 13
            }
        }
    },
    scales: {}
};

function initLineChart(data) {
    const ctx = document.getElementById('line-chart').getContext('2d');

    if (lineChart) {
        lineChart.destroy();
    }

    lineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Average Annual Cost ($)',
                data: data.data,
                borderColor: chartColors.primary,
                backgroundColor: chartColors.primaryTransparent,
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointBackgroundColor: chartColors.primary,
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            ...defaultOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: chartColors.grid
                    },
                    ticks: {
                        color: chartColors.text,
                        callback: function (value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        color: chartColors.grid
                    },
                    ticks: {
                        color: chartColors.text
                    }
                }
            }
        }
    });
}

function initBarChart(data) {
    const ctx = document.getElementById('bar-chart').getContext('2d');

    if (barChart) {
        barChart.destroy();
    }

    const gradientColors = [
        chartColors.primary,
        chartColors.secondary,
        chartColors.success,
        chartColors.warning
    ];

    barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Average Cost ($)',
                data: data.data,
                backgroundColor: gradientColors.slice(0, data.labels.length),
                borderColor: gradientColors.slice(0, data.labels.length),
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            ...defaultOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: chartColors.grid
                    },
                    ticks: {
                        color: chartColors.text,
                        callback: function (value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: chartColors.text
                    }
                }
            }
        }
    });
}

function initPieChart(data) {
    const ctx = document.getElementById('pie-chart').getContext('2d');

    if (pieChart) {
        pieChart.destroy();
    }

    pieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: [
                    chartColors.danger,
                    chartColors.warning,
                    chartColors.secondary,
                    chartColors.info,
                    chartColors.success
                ],
                borderColor: '#1e293b',
                borderWidth: 3,
                hoverOffset: 10
            }]
        },
        options: {
            ...defaultOptions,
            cutout: '60%',
            plugins: {
                ...defaultOptions.plugins,
                legend: {
                    ...defaultOptions.plugins.legend,
                    position: 'bottom'
                }
            }
        }
    });
}

function initAreaChart(data) {
    const ctx = document.getElementById('area-chart').getContext('2d');

    if (areaChart) {
        areaChart.destroy();
    }

    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(236, 72, 153, 0.4)');
    gradient.addColorStop(0.5, 'rgba(99, 102, 241, 0.3)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0.1)');

    areaChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Average Cost ($)',
                data: data.data,
                borderColor: chartColors.secondary,
                backgroundColor: gradient,
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 6,
                pointHoverRadius: 8,
                pointBackgroundColor: chartColors.secondary,
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            ...defaultOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: chartColors.grid
                    },
                    ticks: {
                        color: chartColors.text,
                        callback: function (value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        color: chartColors.grid
                    },
                    ticks: {
                        color: chartColors.text
                    }
                }
            }
        }
    });
}

function initScatterChart(data) {
    const ctx = document.getElementById('scatter-chart').getContext('2d');

    if (window.scatterChart) {
        window.scatterChart.destroy();
    }

    window.scatterChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Average Cost per Visit Frequency',
                data: data.x_data.map((x, i) => ({ x: x, y: data.y_data[i] })),
                backgroundColor: chartColors.primaryTransparent,
                borderColor: chartColors.primary,
                borderWidth: 2,
                pointRadius: data.sizes ? data.sizes.map(s => Math.min(s / 10, 15)) : 8,
                pointHoverRadius: 12
            }]
        },
        options: {
            ...defaultOptions,
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Doctor Visits Per Year',
                        color: chartColors.text
                    },
                    grid: {
                        color: chartColors.grid
                    },
                    ticks: {
                        color: chartColors.text
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Average Annual Cost ($)',
                        color: chartColors.text
                    },
                    grid: {
                        color: chartColors.grid
                    },
                    ticks: {
                        color: chartColors.text,
                        callback: function (value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

function initPolarChart(data) {
    const ctx = document.getElementById('polar-chart').getContext('2d');

    if (window.polarChart) {
        window.polarChart.destroy();
    }

    window.polarChart = new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: [
                    'rgba(239, 68, 68, 0.6)',    // Male Smokers - Red
                    'rgba(16, 185, 129, 0.6)',    // Male Non-Smokers - Green
                    'rgba(245, 158, 11, 0.6)',    // Female Smokers - Orange
                    'rgba(6, 182, 212, 0.6)'      // Female Non-Smokers - Cyan
                ],
                borderColor: [
                    'rgba(239, 68, 68, 1)',
                    'rgba(16, 185, 129, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(6, 182, 212, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            ...defaultOptions,
            scales: {
                r: {
                    beginAtZero: true,
                    grid: {
                        color: chartColors.grid
                    },
                    angleLines: {
                        color: chartColors.grid
                    },
                    pointLabels: {
                        color: chartColors.text,
                        font: {
                            size: 11
                        }
                    },
                    ticks: {
                        color: chartColors.text,
                        backdropColor: 'transparent',
                        callback: function (value) {
                            return '$' + (value / 1000).toFixed(0) + 'k';
                        }
                    }
                }
            }
        }
    });
}

async function loadVisualizationData() {
    try {
        const response = await fetch('http://localhost:5000/api/visualizations');
        const data = await response.json();

        initLineChart(data.line_chart);
        initBarChart(data.bar_chart);
        initPieChart(data.pie_chart);
        initAreaChart(data.area_chart);
        initScatterChart(data.scatter_chart);
        initPolarChart(data.polar_chart);

        console.log('All 6 charts initialized successfully');
    } catch (error) {
        console.error('Error loading visualization data:', error);

        loadSampleData();
    }
}

function loadSampleData() {
    console.log('Loading sample data...');

    initLineChart({
        labels: ['<20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80+'],
        data: [5000, 6000, 7500, 9000, 11000, 13000, 15000, 17000]
    });

    initBarChart({
        labels: ['Private', 'Government', 'None'],
        data: [5500, 8000, 18000]
    });

    initPieChart({
        labels: ['Diabetes', 'Hypertension', 'Heart Disease', 'Asthma', 'No Conditions'],
        data: [500, 600, 300, 400, 3200]
    });

    initAreaChart({
        labels: ['Rural', 'Semi-Urban', 'Urban'],
        data: [9500, 8500, 7500]
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadVisualizationData);
} else {
    loadVisualizationData();
}
