// ===== StockPulse AI - Interactive JavaScript =====

// Sample stock data for demo
const stockData = {
    GOOGL: {
        name: 'Alphabet Inc.',
        price: 175.42,
        change: 2.34,
        changePercent: 1.35,
        sentiment: { score: 78, label: 'Bullish' },
        technical: { score: 72, rsi: 42, macd: 0.85 },
        prediction: { percent: 5.2, target: 184.54 },
        confidence: 87,
        rating: 'STRONG BUY',
        history: generatePriceHistory(175.42, 30),
        forecast: generateForecast(175.42, 7, 5.2)
    },
    AAPL: {
        name: 'Apple Inc.',
        price: 198.56,
        change: -1.23,
        changePercent: -0.62,
        sentiment: { score: 65, label: 'Neutral' },
        technical: { score: 58, rsi: 55, macd: -0.32 },
        prediction: { percent: 2.1, target: 202.73 },
        confidence: 72,
        rating: 'BUY',
        history: generatePriceHistory(198.56, 30),
        forecast: generateForecast(198.56, 7, 2.1)
    },
    MSFT: {
        name: 'Microsoft Corporation',
        price: 425.89,
        change: 5.67,
        changePercent: 1.35,
        sentiment: { score: 82, label: 'Bullish' },
        technical: { score: 75, rsi: 38, macd: 1.24 },
        prediction: { percent: 6.8, target: 454.85 },
        confidence: 91,
        rating: 'STRONG BUY',
        history: generatePriceHistory(425.89, 30),
        forecast: generateForecast(425.89, 7, 6.8)
    },
    TSLA: {
        name: 'Tesla, Inc.',
        price: 245.32,
        change: -8.45,
        changePercent: -3.33,
        sentiment: { score: 42, label: 'Bearish' },
        technical: { score: 35, rsi: 72, macd: -2.15 },
        prediction: { percent: -4.2, target: 235.01 },
        confidence: 68,
        rating: 'SELL',
        history: generatePriceHistory(245.32, 30),
        forecast: generateForecast(245.32, 7, -4.2)
    },
    NVDA: {
        name: 'NVIDIA Corporation',
        price: 142.58,
        change: 4.21,
        changePercent: 3.04,
        sentiment: { score: 88, label: 'Bullish' },
        technical: { score: 85, rsi: 35, macd: 2.45 },
        prediction: { percent: 8.5, target: 154.70 },
        confidence: 94,
        rating: 'STRONG BUY',
        history: generatePriceHistory(142.58, 30),
        forecast: generateForecast(142.58, 7, 8.5)
    },
    AMZN: {
        name: 'Amazon.com, Inc.',
        price: 186.75,
        change: 2.89,
        changePercent: 1.57,
        sentiment: { score: 71, label: 'Bullish' },
        technical: { score: 68, rsi: 48, macd: 0.95 },
        prediction: { percent: 4.3, target: 194.78 },
        confidence: 79,
        rating: 'BUY',
        history: generatePriceHistory(186.75, 30),
        forecast: generateForecast(186.75, 7, 4.3)
    }
};

// Generate random price history
function generatePriceHistory(currentPrice, days) {
    const prices = [];
    let price = currentPrice * (1 - Math.random() * 0.15);

    for (let i = 0; i < days; i++) {
        const change = (Math.random() - 0.48) * 3;
        price = price * (1 + change / 100);
        prices.push(price);
    }

    // Adjust last price to match current
    const adjustment = currentPrice / prices[prices.length - 1];
    return prices.map(p => p * adjustment);
}

// Generate forecast data
function generateForecast(currentPrice, days, percentChange) {
    const prices = [currentPrice];
    const dailyChange = percentChange / days;

    for (let i = 1; i <= days; i++) {
        const randomFactor = 1 + (Math.random() - 0.5) * 0.01;
        const newPrice = prices[i - 1] * (1 + dailyChange / 100) * randomFactor;
        prices.push(newPrice);
    }

    return prices;
}

// Chart instances
let heroChart, technicalChart, predictionChart, mainChart, sentimentMiniChart;

// Initialize Hero Chart
function initHeroChart() {
    const ctx = document.getElementById('heroChart');
    if (!ctx) return;

    const labels = Array.from({ length: 50 }, (_, i) => i);
    const data = generatePriceHistory(100, 50);

    heroChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { display: false },
                y: { display: false }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// Initialize Technical Analysis Chart
function initTechnicalChart() {
    const ctx = document.getElementById('technicalChart');
    if (!ctx) return;

    const labels = Array.from({ length: 20 }, (_, i) => `Day ${i + 1}`);
    const rsiData = Array.from({ length: 20 }, () => 30 + Math.random() * 40);
    const priceData = generatePriceHistory(100, 20);

    technicalChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Price',
                    data: priceData,
                    borderColor: '#3b82f6',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    tension: 0.4,
                    yAxisID: 'y'
                },
                {
                    label: 'RSI',
                    data: rsiData,
                    borderColor: '#8b5cf6',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    tension: 0.4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: { color: '#94a3b8' }
                }
            },
            scales: {
                x: {
                    display: false
                },
                y: {
                    display: false,
                    position: 'left'
                },
                y1: {
                    display: false,
                    position: 'right',
                    min: 0,
                    max: 100
                }
            }
        }
    });
}

// Initialize Prediction Chart
function initPredictionChart() {
    const ctx = document.getElementById('predictionChart');
    if (!ctx) return;

    const historyLabels = Array.from({ length: 7 }, (_, i) => `Day ${i - 6}`);
    const forecastLabels = Array.from({ length: 7 }, (_, i) => `Day +${i + 1}`);
    const labels = [...historyLabels, 'Today', ...forecastLabels];

    const historyData = generatePriceHistory(100, 7);
    const forecastData = generateForecast(historyData[6], 7, 5);

    predictionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Historical',
                    data: [...historyData, historyData[6], ...Array(7).fill(null)],
                    borderColor: '#3b82f6',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 0
                },
                {
                    label: 'Predicted',
                    data: [...Array(7).fill(null), historyData[6], ...forecastData.slice(1)],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: { color: '#94a3b8', boxWidth: 20 }
                }
            },
            scales: {
                x: { display: false },
                y: { display: false }
            }
        }
    });
}

// Initialize Main Demo Chart
function initMainChart(stock) {
    const ctx = document.getElementById('mainChart');
    if (!ctx) return;

    const historyLabels = Array.from({ length: 30 }, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() - (30 - i));
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });

    const forecastLabels = Array.from({ length: 7 }, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() + i + 1);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });

    const labels = [...historyLabels, ...forecastLabels];

    if (mainChart) {
        mainChart.destroy();
    }

    mainChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Historical Price',
                    data: [...stock.history, ...Array(7).fill(null)],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 5
                },
                {
                    label: 'AI Prediction',
                    data: [...Array(29).fill(null), stock.history[29], ...stock.forecast.slice(1)],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    borderDash: [5, 5],
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#94a3b8',
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#1a2235',
                    titleColor: '#fff',
                    bodyColor: '#94a3b8',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.parsed.y.toFixed(2);
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#64748b',
                        maxRotation: 45
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#64748b',
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// Initialize Sentiment Mini Chart
function initSentimentMiniChart() {
    const ctx = document.getElementById('sentimentMiniChart');
    if (!ctx) return;

    sentimentMiniChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Bullish', 'Bearish', 'Neutral'],
            datasets: [{
                data: [78, 12, 10],
                backgroundColor: ['#10b981', '#ef4444', '#f59e0b'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            cutout: '70%'
        }
    });
}

// Update Demo Results
function updateDemoResults(symbol) {
    const stock = stockData[symbol.toUpperCase()];

    if (!stock) {
        // Generate random data for unknown stocks
        const randomStock = {
            name: symbol.toUpperCase() + ' Corporation',
            price: 50 + Math.random() * 200,
            change: (Math.random() - 0.5) * 10,
            changePercent: (Math.random() - 0.5) * 5,
            sentiment: {
                score: 30 + Math.random() * 60,
                label: Math.random() > 0.5 ? 'Bullish' : 'Neutral'
            },
            technical: {
                score: 30 + Math.random() * 60,
                rsi: 20 + Math.random() * 60,
                macd: (Math.random() - 0.5) * 3
            },
            prediction: {
                percent: (Math.random() - 0.3) * 10,
                target: 0
            },
            confidence: 50 + Math.random() * 40,
            rating: 'HOLD',
            history: [],
            forecast: []
        };

        randomStock.prediction.target = randomStock.price * (1 + randomStock.prediction.percent / 100);
        randomStock.history = generatePriceHistory(randomStock.price, 30);
        randomStock.forecast = generateForecast(randomStock.price, 7, randomStock.prediction.percent);

        // Determine rating based on scores
        const avgScore = (randomStock.sentiment.score + randomStock.technical.score) / 2;
        if (avgScore > 75) randomStock.rating = 'STRONG BUY';
        else if (avgScore > 60) randomStock.rating = 'BUY';
        else if (avgScore > 40) randomStock.rating = 'HOLD';
        else if (avgScore > 25) randomStock.rating = 'SELL';
        else randomStock.rating = 'STRONG SELL';

        updateUI(randomStock, symbol.toUpperCase());
        return;
    }

    updateUI(stock, symbol.toUpperCase());
}

function updateUI(stock, symbol) {
    // Update stock info
    document.getElementById('stockName').textContent = stock.name;
    document.getElementById('stockSymbol').textContent = symbol;
    document.getElementById('currentPrice').textContent = '$' + stock.price.toFixed(2);

    const changeEl = document.getElementById('priceChange');
    const changeSign = stock.change >= 0 ? '+' : '';
    changeEl.textContent = `${changeSign}${stock.change.toFixed(2)} (${changeSign}${stock.changePercent.toFixed(2)}%)`;
    changeEl.className = 'price-change ' + (stock.change >= 0 ? 'positive' : 'negative');

    // Update sentiment
    document.getElementById('sentimentScore').textContent = Math.round(stock.sentiment.score) + '%';
    document.getElementById('sentimentLabel').textContent = stock.sentiment.label;

    // Update technical
    document.getElementById('technicalScore').textContent = Math.round(stock.technical.score) + '%';

    // Update prediction
    const predSign = stock.prediction.percent >= 0 ? '+' : '';
    document.getElementById('predictionScore').textContent = predSign + stock.prediction.percent.toFixed(1) + '%';
    document.getElementById('priceTarget').textContent = '$' + stock.prediction.target.toFixed(2);

    // Update final rating
    const ratingEl = document.getElementById('finalRating');
    ratingEl.innerHTML = `<i class="fas fa-arrow-trend-${stock.prediction.percent >= 0 ? 'up' : 'down'}"></i><span>${stock.rating}</span>`;
    ratingEl.className = 'final-rating ' + stock.rating.toLowerCase().replace(' ', '-');

    // Update confidence
    document.getElementById('confidenceScore').textContent = Math.round(stock.confidence) + '%';
    document.querySelector('.confidence-fill').style.width = stock.confidence + '%';

    // Update main chart
    initMainChart(stock);

    // Animate results
    animateResults();
}

function animateResults() {
    const cards = document.querySelectorAll('.analysis-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Scroll animations for pipeline steps
function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, {
        threshold: 0.2
    });

    document.querySelectorAll('.pipeline-step').forEach(step => {
        observer.observe(step);
    });
}

// Smooth scroll for navigation
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
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

// Navbar background on scroll
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(10, 14, 23, 0.98)';
        } else {
            navbar.style.background = 'rgba(10, 14, 23, 0.9)';
        }
    });
}

// Counter animation
function animateCounter(element, target, suffix = '') {
    const duration = 2000;
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.round(current) + suffix;
    }, 16);
}

// Initialize everything on DOM load
document.addEventListener('DOMContentLoaded', () => {
    // Initialize charts
    initHeroChart();
    initTechnicalChart();
    initPredictionChart();
    initSentimentMiniChart();

    // Initialize with default stock
    updateDemoResults('GOOGL');

    // Initialize animations and interactions
    initScrollAnimations();
    initSmoothScroll();
    initNavbarScroll();

    // Analyze button click handler
    const analyzeBtn = document.getElementById('analyzeBtn');
    const stockInput = document.getElementById('stockInput');

    if (analyzeBtn && stockInput) {
        analyzeBtn.addEventListener('click', () => {
            const symbol = stockInput.value.trim();
            if (symbol) {
                analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
                analyzeBtn.disabled = true;

                // Simulate API call delay
                setTimeout(() => {
                    updateDemoResults(symbol);
                    analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze';
                    analyzeBtn.disabled = false;
                }, 1500);
            }
        });

        stockInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                analyzeBtn.click();
            }
        });
    }

    // Hero buttons
    const tryDemoBtn = document.querySelector('.primary-btn');
    if (tryDemoBtn) {
        tryDemoBtn.addEventListener('click', () => {
            document.getElementById('demo').scrollIntoView({ behavior: 'smooth' });
        });
    }

    const learnMoreBtn = document.querySelector('.secondary-btn');
    if (learnMoreBtn) {
        learnMoreBtn.addEventListener('click', () => {
            document.getElementById('features').scrollIntoView({ behavior: 'smooth' });
        });
    }

    // CTA button
    const ctaBtn = document.querySelector('.cta-button');
    if (ctaBtn) {
        ctaBtn.addEventListener('click', () => {
            document.getElementById('demo').scrollIntoView({ behavior: 'smooth' });
        });
    }

    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        .pipeline-step {
            opacity: 0;
            transform: translateX(-50px);
            transition: all 0.6s ease;
        }
        .pipeline-step.animate-in {
            opacity: 1;
            transform: translateX(0);
        }
    `;
    document.head.appendChild(style);
});

// Console Easter Egg
console.log(`
%c StockPulse AI %c
%c Intelligent Stock Analysis Platform %c

Built with:
- FinBERT for Sentiment Analysis
- LSTM Neural Networks for Price Prediction
- Technical Indicators (RSI, MACD, Bollinger Bands)
- Weighted Ensemble Recommendations

`,
'background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; font-size: 20px; padding: 10px 20px; border-radius: 5px;',
'',
'color: #94a3b8; font-size: 14px;',
''
);
