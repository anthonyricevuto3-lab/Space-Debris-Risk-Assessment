// Space Debris Risk Assessment - Frontend JavaScript

class SpaceDebrisApp {
    constructor() {
        this.currentData = null;
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('autoRefresh');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startAutoRefresh();
                } else {
                    this.stopAutoRefresh();
                }
            });
        }
    }

    switchTab(tabName) {
        // Update active tab
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Show corresponding content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-content`).classList.add('active');

        // Load data based on tab
        this.loadTabData(tabName);
    }

    async loadTabData(tabName) {
        try {
            const baseUrl = 'https://space-debris-api-v2.azurewebsites.net';
            let endpoint;
            switch (tabName) {
                case 'top3':
                    endpoint = `${baseUrl}/api/top-risks`;
                    break;
                case 'all':
                    endpoint = `${baseUrl}/api/all-risks`;
                    break;
                case 'stats':
                    endpoint = `${baseUrl}/api/all-risks`; // We'll calculate stats from all data
                    break;
                default:
                    return;
            }

            const response = await fetch(endpoint);
            const data = await response.json();

            if (response.ok) {
                this.currentData = data;
                this.renderTabContent(tabName, data);
                this.updateTimestamp(data.timestamp);
            } else {
                this.showError(data.error || 'Failed to load data');
            }
        } catch (error) {
            this.showError('Network error: ' + error.message);
        }
    }

    renderTabContent(tabName, data) {
        const contentDiv = document.getElementById(`${tabName}-content`);
        
        switch (tabName) {
            case 'top3':
                this.renderTop3Risks(contentDiv, data.top_3_risks || []);
                break;
            case 'all':
                this.renderAllRisks(contentDiv, data.all_risks || []);
                break;
            case 'stats':
                this.renderStatistics(contentDiv, data.all_risks || []);
                break;
        }
    }

    renderTop3Risks(container, risks) {
        if (!risks || risks.length === 0) {
            container.innerHTML = '<div class="text-center">No risk data available</div>';
            return;
        }

        const html = risks.map((risk, index) => `
            <div class="risk-item ${this.getRiskClass(risk.risk_score)} fade-in" style="animation-delay: ${index * 0.1}s">
                <div class="risk-header">
                    <h3 class="risk-title">${index + 1}. ${risk.name}</h3>
                    <div class="risk-score">${risk.risk_score}/5.0</div>
                </div>
                
                <div class="risk-badge ${this.getRiskLevel(risk.risk_score)}">${this.getRiskLevel(risk.risk_score)} Risk</div>
                
                <div class="details-grid">
                    <div class="detail-item">
                        <div class="detail-label">Object Type</div>
                        <div class="detail-value">${risk.object_type}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Altitude</div>
                        <div class="detail-value">${risk.current_altitude_km} km</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Inclination</div>
                        <div class="detail-value">${risk.inclination_deg}°</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Eccentricity</div>
                        <div class="detail-value">${risk.eccentricity}</div>
                    </div>
                </div>

                <div class="prediction-panel">
                    <div class="prediction-title">Reentry Prediction Analysis</div>
                    <div class="prediction-grid">
                        <div class="prediction-item">
                            <div class="prediction-label">Days to Reentry</div>
                            <div class="prediction-value">${risk.reentry_prediction.days_to_reentry}</div>
                        </div>
                        <div class="prediction-item">
                            <div class="prediction-label">Reentry Probability</div>
                            <div class="prediction-value">${risk.reentry_prediction.reentry_probability_percent}%</div>
                        </div>
                        <div class="prediction-item">
                            <div class="prediction-label">Spatial Risk</div>
                            <div class="prediction-value">${risk.reentry_prediction.spatial_risk_percent}%</div>
                        </div>
                        <div class="prediction-item">
                            <div class="prediction-label">Uncertainty</div>
                            <div class="prediction-value">± ${risk.reentry_prediction.uncertainty_days} days</div>
                        </div>
                        <div class="prediction-item">
                            <div class="prediction-label">Decay Rate</div>
                            <div class="prediction-value">${risk.orbital_decay.decay_rate_km_per_day} km/day</div>
                        </div>
                        <div class="prediction-item">
                            <div class="prediction-label">30-Day Altitude Loss</div>
                            <div class="prediction-value">${risk.orbital_decay.altitude_loss_30_days} km</div>
                        </div>
                    </div>
                    ${risk.reentry_prediction.predicted_date ? `
                        <div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px;">
                            <strong>Predicted Reentry Date:</strong> ${new Date(risk.reentry_prediction.predicted_date).toLocaleDateString()}
                        </div>
                    ` : ''}
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    renderAllRisks(container, risks) {
        if (!risks || risks.length === 0) {
            container.innerHTML = '<div class="text-center">No risk data available</div>';
            return;
        }

        const html = `
            <div class="stats-panel mb-20">
                <h3>Quick Statistics</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value">${risks.length}</div>
                        <div class="stat-label">Total Objects</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${risks.filter(r => r.risk_score >= 4).length}</div>
                        <div class="stat-label">High Risk</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${risks.filter(r => r.risk_score >= 2 && r.risk_score < 4).length}</div>
                        <div class="stat-label">Medium Risk</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${risks.filter(r => r.risk_score < 2).length}</div>
                        <div class="stat-label">Low Risk</div>
                    </div>
                </div>
            </div>
            
            <div class="risk-grid">
                ${risks.slice(0, 20).map((risk, index) => `
                    <div class="risk-item ${this.getRiskClass(risk.risk_score)} fade-in" style="animation-delay: ${index * 0.05}s">
                        <div class="risk-header">
                            <h4 class="risk-title">${risk.name}</h4>
                            <div class="risk-score">${risk.risk_score}/5</div>
                        </div>
                        <div class="risk-badge ${this.getRiskLevel(risk.risk_score)}">${this.getRiskLevel(risk.risk_score)}</div>
                        <div style="margin-top: 10px; font-size: 0.9em; color: #666;">
                            ${risk.object_type} • ${risk.current_altitude_km}km altitude • 
                            ${risk.reentry_prediction.days_to_reentry} days to reentry
                        </div>
                    </div>
                `).join('')}
            </div>
            
            ${risks.length > 20 ? `<div class="text-center mt-20" style="color: white;">Showing top 20 of ${risks.length} objects</div>` : ''}
        `;

        container.innerHTML = html;
    }

    renderStatistics(container, risks) {
        if (!risks || risks.length === 0) {
            container.innerHTML = '<div class="text-center">No data available for statistics</div>';
            return;
        }

        const stats = this.calculateStatistics(risks);
        
        const html = `
            <div class="stats-panel">
                <h3>Comprehensive Risk Analysis</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value">${stats.totalObjects}</div>
                        <div class="stat-label">Total Objects Tracked</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${stats.averageRisk}</div>
                        <div class="stat-label">Average Risk Score</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${stats.averageAltitude}km</div>
                        <div class="stat-label">Average Altitude</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${stats.objectsReentryingSoon}</div>
                        <div class="stat-label">Reentry Within 30 Days</div>
                    </div>
                </div>
            </div>

            <div class="stats-panel">
                <h3>Object Type Distribution</h3>
                <div class="details-grid">
                    ${Object.entries(stats.objectTypes).map(([type, count]) => `
                        <div class="detail-item">
                            <div class="detail-label">${type}</div>
                            <div class="detail-value">${count} objects</div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="stats-panel">
                <h3>Risk Level Distribution</h3>
                <div class="details-grid">
                    <div class="detail-item">
                        <div class="detail-label">Critical Risk (4.0-5.0)</div>
                        <div class="detail-value">${stats.riskLevels.critical} objects</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">High Risk (3.0-3.9)</div>
                        <div class="detail-value">${stats.riskLevels.high} objects</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Medium Risk (2.0-2.9)</div>
                        <div class="detail-value">${stats.riskLevels.medium} objects</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Low Risk (0.0-1.9)</div>
                        <div class="detail-value">${stats.riskLevels.low} objects</div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    calculateStatistics(risks) {
        const totalObjects = risks.length;
        const averageRisk = (risks.reduce((sum, r) => sum + r.risk_score, 0) / totalObjects).toFixed(1);
        const averageAltitude = Math.round(risks.reduce((sum, r) => sum + r.current_altitude_km, 0) / totalObjects);
        const objectsReentryingSoon = risks.filter(r => r.reentry_prediction.days_to_reentry <= 30).length;

        const objectTypes = {};
        const riskLevels = { critical: 0, high: 0, medium: 0, low: 0 };

        risks.forEach(risk => {
            // Object types
            objectTypes[risk.object_type] = (objectTypes[risk.object_type] || 0) + 1;

            // Risk levels
            if (risk.risk_score >= 4.0) riskLevels.critical++;
            else if (risk.risk_score >= 3.0) riskLevels.high++;
            else if (risk.risk_score >= 2.0) riskLevels.medium++;
            else riskLevels.low++;
        });

        return {
            totalObjects,
            averageRisk,
            averageAltitude,
            objectsReentryingSoon,
            objectTypes,
            riskLevels
        };
    }

    getRiskClass(score) {
        if (score >= 4) return 'high-risk';
        if (score >= 2) return 'medium-risk';
        return 'low-risk';
    }

    getRiskLevel(score) {
        if (score >= 4) return 'high';
        if (score >= 2) return 'medium';
        return 'low';
    }

    showLoading(container) {
        container.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <div>Loading space debris data...</div>
            </div>
        `;
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-error';
        errorDiv.textContent = message;
        document.body.appendChild(errorDiv);
        
        setTimeout(() => errorDiv.remove(), 5000);
    }

    updateTimestamp(timestamp) {
        const timestampEl = document.getElementById('timestamp');
        if (timestampEl && timestamp) {
            const date = new Date(timestamp);
            timestampEl.textContent = `Data updated: ${date.toLocaleString()}`;
        }
    }

    async loadInitialData() {
        await this.loadTabData('top3');
    }

    async refreshData() {
        const activeTab = document.querySelector('.nav-tab.active');
        if (activeTab) {
            const tabName = activeTab.dataset.tab;
            this.showLoading(document.getElementById(`${tabName}-content`));
            await this.loadTabData(tabName);
        }
    }

    startAutoRefresh() {
        this.stopAutoRefresh();
        this.refreshInterval = setInterval(() => {
            this.refreshData();
        }, 300000); // Refresh every 5 minutes
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SpaceDebrisApp();
});