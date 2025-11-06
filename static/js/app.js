// Space Debris Risk Assessment - Interactive Features
class SpaceDebrisApp {
    constructor() {
        this.initializeApp();
        this.createStarField();
        this.setupEventListeners();
        this.updateSystemStatus();
    }

    initializeApp() {
        console.log('🚀 Space Debris Risk Assessment Dashboard Initialized');
        this.setupTabNavigation();
        this.setupAutoRefresh();
        this.initializeAnimations();
    }

    createStarField() {
        // Create animated star background
        const starContainer = document.createElement('div');
        starContainer.className = 'space-background';
        
        for (let i = 0; i < 3; i++) {
            const stars = document.createElement('div');
            stars.className = `stars${i === 0 ? '' : i + 1}`;
            starContainer.appendChild(stars);
        }
        
        document.body.insertBefore(starContainer, document.body.firstChild);
    }

    setupTabNavigation() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');
                
                // Remove active class from all tabs and contents
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                // Add active class to clicked tab and corresponding content
                button.classList.add('active');
                const targetContent = document.getElementById(targetTab);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
            });
        });

        // Set first tab as active by default
        if (tabButtons.length > 0) {
            tabButtons[0].click();
        }
    }

    setupAutoRefresh() {
        const refreshToggle = document.getElementById('autoRefresh');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        if (refreshToggle) {
            refreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startAutoRefresh();
                    console.log('🔄 Auto-refresh enabled');
                } else {
                    this.stopAutoRefresh();
                    console.log('⏹️ Auto-refresh disabled');
                }
            });
        }

        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => {
                this.performAnalysis();
            });
        }
    }

    startAutoRefresh() {
        this.autoRefreshInterval = setInterval(() => {
            this.updateData();
        }, 30000); // Refresh every 30 seconds
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
    }

    async performAnalysis() {
        const analyzeBtn = document.getElementById('analyzeBtn');
        const originalText = analyzeBtn.textContent;
        
        // Show loading state
        analyzeBtn.innerHTML = '<span class="loading-spinner"></span> Analyzing...';
        analyzeBtn.disabled = true;

        try {
            // Simulate analysis - in real app this would call your API
            await this.simulateAnalysis();
            
            // Update UI with results
            this.updateDashboard();
            
            console.log('✅ Analysis completed successfully');
        } catch (error) {
            console.error('❌ Analysis failed:', error);
            this.showError('Analysis failed. Please try again.');
        } finally {
            // Restore button state
            analyzeBtn.textContent = originalText;
            analyzeBtn.disabled = false;
        }
    }

    async simulateAnalysis() {
        // Simulate API call delay
        return new Promise(resolve => {
            setTimeout(resolve, 2000);
        });
    }

    updateData() {
        console.log('🔄 Updating space debris data...');
        this.updateSystemStatus();
        this.updateMetrics();
    }

    updateSystemStatus() {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.system-status .status-text');
        
        if (statusDot && statusText) {
            // Simulate system health check
            const isHealthy = Math.random() > 0.1; // 90% chance of healthy status
            
            if (isHealthy) {
                statusDot.style.background = 'var(--success-green)';
                statusText.textContent = 'Systems Operational';
            } else {
                statusDot.style.background = 'var(--warning-orange)';
                statusText.textContent = 'Partial Service';
            }
        }
    }

    updateMetrics() {
        // Update performance metrics with realistic values
        const metrics = {
            'tracking-accuracy': Math.random() * 5 + 95, // 95-100%
            'collision-predictions': Math.floor(Math.random() * 1000) + 5000, // 5000-6000
            'active-objects': Math.floor(Math.random() * 5000) + 25000, // 25000-30000
            'risk-assessments': Math.floor(Math.random() * 100) + 200 // 200-300
        };

        Object.entries(metrics).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                if (id === 'tracking-accuracy') {
                    element.textContent = value.toFixed(2) + '%';
                } else {
                    element.textContent = value.toLocaleString();
                }
            }
        });
    }

    updateDashboard() {
        // Update all dashboard components
        this.updateMetrics();
        this.loadDebrisData();
        this.updateRiskScale();
    }

    loadDebrisData() {
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabContents.forEach(content => {
            if (content.id !== 'overview') {
                // Show loading state
                content.innerHTML = `
                    <div class="loading-state">
                        <div class="loading-spinner"></div>
                        <p class="loading-text">Loading ${content.id} data...</p>
                    </div>
                `;
                
                // Simulate data loading
                setTimeout(() => {
                    this.populateTabContent(content);
                }, 1000 + Math.random() * 2000);
            }
        });
    }

    populateTabContent(tabElement) {
        const tabId = tabElement.id;
        let content = '';

        switch (tabId) {
            case 'satellites':
                content = this.generateSatelliteData();
                break;
            case 'debris':
                content = this.generateDebrisData();
                break;
            case 'conjunctions':
                content = this.generateConjunctionData();
                break;
            case 'analysis':
                content = this.generateAnalysisData();
                break;
            default:
                content = '<p>No data available</p>';
        }

        tabElement.innerHTML = content;
    }

    generateSatelliteData() {
        return `
            <div class="content-header">
                <h3>🛰️ Active Satellites</h3>
                <p>Currently tracked operational satellites</p>
            </div>
            <div class="data-grid">
                <div class="data-item">
                    <span class="data-label">Total Active</span>
                    <span class="data-value">${Math.floor(Math.random() * 1000) + 4000}</span>
                </div>
                <div class="data-item">
                    <span class="data-label">LEO Satellites</span>
                    <span class="data-value">${Math.floor(Math.random() * 500) + 3000}</span>
                </div>
                <div class="data-item">
                    <span class="data-label">GEO Satellites</span>
                    <span class="data-value">${Math.floor(Math.random() * 200) + 800}</span>
                </div>
                <div class="data-item">
                    <span class="data-label">Risk Level</span>
                    <span class="data-value risk-low">Moderate</span>
                </div>
            </div>
        `;
    }

    generateDebrisData() {
        return `
            <div class="content-header">
                <h3>🌌 Space Debris</h3>
                <p>Tracked orbital debris objects</p>
            </div>
            <div class="data-grid">
                <div class="data-item">
                    <span class="data-label">Total Objects</span>
                    <span class="data-value">${Math.floor(Math.random() * 10000) + 25000}</span>
                </div>
                <div class="data-item">
                    <span class="data-label">High Risk</span>
                    <span class="data-value">${Math.floor(Math.random() * 100) + 50}</span>
                </div>
                <div class="data-item">
                    <span class="data-label">New Detections</span>
                    <span class="data-value">${Math.floor(Math.random() * 20) + 5}</span>
                </div>
                <div class="data-item">
                    <span class="data-label">Decay Rate</span>
                    <span class="data-value">${Math.floor(Math.random() * 10) + 15}/day</span>
                </div>
            </div>
        `;
    }

    generateConjunctionData() {
        return `
            <div class="content-header">
                <h3>⚠️ Conjunction Alerts</h3>
                <p>Potential collision warnings</p>
            </div>
            <div class="data-grid">
                <div class="data-item">
                    <span class="data-label">Active Alerts</span>
                    <span class="data-value">${Math.floor(Math.random() * 20) + 5}</span>
                </div>
                <div class="data-item">
                    <span class="data-label">High Priority</span>
                    <span class="data-value">${Math.floor(Math.random() * 5) + 1}</span>
                </div>
                <div class="data-item">
                    <span class="data-label">24h Forecast</span>
                    <span class="data-value">${Math.floor(Math.random() * 10) + 2}</span>
                </div>
                <div class="data-item">
                    <span class="data-label">Success Rate</span>
                    <span class="data-value">${(Math.random() * 5 + 95).toFixed(1)}%</span>
                </div>
            </div>
        `;
    }

    generateAnalysisData() {
        return `
            <div class="content-header">
                <h3>📊 Risk Analysis</h3>
                <p>AI-powered collision risk assessment</p>
            </div>
            <div class="data-grid">
                <div class="data-item">
                    <span class="data-label">Model Accuracy</span>
                    <span class="data-value">${(Math.random() * 3 + 97).toFixed(2)}%</span>
                </div>
                <div class="data-item">
                    <span class="data-label">Predictions</span>
                    <span class="data-value">${Math.floor(Math.random() * 1000) + 5000}</span>
                </div>
                <div class="data-item">
                    <span class="data-label">Processing Time</span>
                    <span class="data-value">${(Math.random() * 2 + 0.5).toFixed(1)}s</span>
                </div>
                <div class="data-item">
                    <span class="data-label">Confidence</span>
                    <span class="data-value">${(Math.random() * 10 + 90).toFixed(1)}%</span>
                </div>
            </div>
        `;
    }

    updateRiskScale() {
        const scaleItems = document.querySelectorAll('.scale-item');
        scaleItems.forEach(item => {
            // Add subtle animation when hovering
            item.addEventListener('mouseenter', () => {
                item.style.transform = 'scale(1.05) translateY(-2px)';
            });
            
            item.addEventListener('mouseleave', () => {
                item.style.transform = 'scale(1.0) translateY(0px)';
            });
        });
    }

    initializeAnimations() {
        // Add smooth scrolling to navigation links
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

        // Add intersection observer for fade-in animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Observe all cards and sections
        document.querySelectorAll('.explanation-card, .scale-item, .tab-content').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });
    }

    showError(message) {
        // Create and show error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.innerHTML = `
            <div class="error-content">
                <span class="error-icon">❌</span>
                <span class="error-message">${message}</span>
            </div>
        `;
        
        document.body.appendChild(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }

    // Cleanup method
    destroy() {
        this.stopAutoRefresh();
        console.log('🧹 Space Debris App cleanup completed');
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.spaceDebrisApp = new SpaceDebrisApp();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.spaceDebrisApp) {
        window.spaceDebrisApp.destroy();
    }
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SpaceDebrisApp;
}