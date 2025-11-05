#!/usr/bin/env python3
"""
Space Debris Risk Assessment System - Production Version
Hybrid AI system with SGP4 physics-based propagation and machine learning
Displays top 3 highest risk objects with detailed predictions
"""

import json
import time
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from flask import Flask, jsonify, request, render_template
import joblib
import os
import warnings
from sgp4.earth_gravity import wgs84
from sgp4.io import twoline2rv
from sgp4 import exporter
import re

warnings.filterwarnings('ignore')

# Import ML models
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder

app = Flask(__name__)

# Production configuration
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Set proper CORS headers for Azure API integration
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

class HybridOrbitDecayPredictor:
    """Hybrid AI predictor combining SGP4 physics with machine learning"""
    
    def __init__(self):
        self.earth_radius = 6371.0  # km
        self.mu = 398600.4418  # Earth's gravitational parameter
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.nn_model = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
        self.is_trained = False
        
    def _generate_training_data(self, n_samples=2000):
        """Generate physics-based training data"""
        np.random.seed(42)
        
        # Realistic orbital parameters
        altitudes = np.random.uniform(200, 2000, n_samples)
        inclinations = np.random.uniform(0, 180, n_samples)
        eccentricities = np.random.exponential(0.05, n_samples)
        eccentricities = np.clip(eccentricities, 0, 0.8)
        
        # Object characteristics
        masses = np.random.lognormal(5, 2, n_samples)
        cross_sectional_areas = np.random.lognormal(1, 1, n_samples)
        
        # Solar activity proxy
        solar_flux = np.random.uniform(70, 300, n_samples)
        
        features = np.column_stack([
            altitudes, inclinations, eccentricities, masses,
            cross_sectional_areas, solar_flux
        ])
        
        # Physics-based decay rate calculation
        decay_rates = []
        for i in range(n_samples):
            alt, inc, ecc, mass, area, flux = features[i]
            
            # Atmospheric density model (simplified)
            if alt < 300:
                base_density = 1e-12 * np.exp(-(alt - 200) / 50)
            elif alt < 600:
                base_density = 1e-14 * np.exp(-(alt - 300) / 80)
            else:
                base_density = 1e-16 * np.exp(-(alt - 600) / 120)
            
            # Solar activity effect
            density = base_density * (1 + (flux - 150) / 300)
            
            # Ballistic coefficient
            bc = mass / area
            
            # Decay rate (km/day)
            decay_rate = max(0.001, density * area / mass * 1000)
            decay_rates.append(decay_rate)
        
        return features, np.array(decay_rates)
    
    def train(self):
        """Train the hybrid models"""
        if self.is_trained:
            return
            
        X, y = self._generate_training_data()
        
        # Train ensemble models
        self.rf_model.fit(X, y)
        self.gb_model.fit(X, y)
        self.nn_model.fit(X, y)
        
        self.is_trained = True
        print("Hybrid Orbital Decay Predictor trained successfully")
    
    def predict_decay_rate(self, altitude, inclination, eccentricity, 
                          mass=1000, area=10, solar_flux=150):
        """Predict orbital decay rate"""
        if not self.is_trained:
            self.train()
        
        features = np.array([[altitude, inclination, eccentricity, 
                            mass, area, solar_flux]])
        
        # Ensemble prediction
        rf_pred = self.rf_model.predict(features)[0]
        gb_pred = self.gb_model.predict(features)[0]
        nn_pred = self.nn_model.predict(features)[0]
        
        # Weighted average
        decay_rate = (rf_pred * 0.4 + gb_pred * 0.4 + nn_pred * 0.2)
        
        return max(0.001, decay_rate)

class ReentryAnalyzer:
    """Advanced reentry prediction and risk analysis"""
    
    def __init__(self):
        self.predictor = HybridOrbitDecayPredictor()
        self.earth_radius = 6371.0
        
    def predict_reentry_window(self, tle_line1, tle_line2, forecast_days=30):
        """Predict reentry time window and location"""
        try:
            # Parse TLE
            satellite = twoline2rv(tle_line1, tle_line2, wgs84)
            
            # Extract orbital elements
            altitude = satellite.a * 6371.0 - 6371.0  # Convert to altitude
            inclination = np.degrees(satellite.inclo)
            eccentricity = satellite.ecco
            
            # Predict decay rate
            decay_rate = self.predictor.predict_decay_rate(
                altitude, inclination, eccentricity
            )
            
            # Calculate reentry time
            if decay_rate > 0:
                days_to_reentry = max(altitude - 100, 0) / decay_rate
                reentry_date = datetime.utcnow() + timedelta(days=days_to_reentry)
            else:
                days_to_reentry = 365 * 100  # Very stable orbit
                reentry_date = None
            
            # Risk assessment
            if days_to_reentry < 30:
                reentry_risk = 0.9
                spatial_risk = 0.8
            elif days_to_reentry < 365:
                reentry_risk = 0.6
                spatial_risk = 0.5
            else:
                reentry_risk = 0.2
                spatial_risk = 0.2
            
            # Prediction uncertainty
            uncertainty_days = max(1, days_to_reentry * 0.1)
            
            return {
                'reentry_window': {
                    'predicted_date': reentry_date.isoformat() if reentry_date else None,
                    'days_from_now': round(days_to_reentry, 1),
                    'uncertainty_days': round(uncertainty_days, 1)
                },
                'risk_assessment': {
                    'overall_reentry_risk': reentry_risk,
                    'peak_spatial_risk': spatial_risk,
                    'uncertainty_bounds': {
                        'lower': max(0, reentry_risk - 0.1),
                        'upper': min(1, reentry_risk + 0.1)
                    }
                },
                'orbital_parameters': {
                    'current_altitude_km': round(altitude, 1),
                    'inclination_deg': round(inclination, 1),
                    'eccentricity': round(eccentricity, 4),
                    'predicted_decay_rate_km_per_day': round(decay_rate, 4)
                }
            }
            
        except Exception as e:
            print(f"Reentry analysis error: {e}")
            return None

class OptimizedTLEParser:
    """Enhanced TLE parser with hybrid AI integration"""
    
    def __init__(self):
        self.celestrak_urls = [
            'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle',
            'https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle',
            'https://celestrak.org/NORAD/elements/gp.php?GROUP=last-30-days&FORMAT=tle'
        ]
        self.reentry_analyzer = ReentryAnalyzer()
        
    def fetch_celestrak_data(self):
        """Fetch real TLE data from CelesTrak"""
        all_objects = []
        
        for url in self.celestrak_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    tle_data = response.text.strip()
                    objects = self.parse_tle_data(tle_data)
                    all_objects.extend(objects)
                    time.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"Error fetching from {url}: {e}")
                continue
        
        return all_objects
    
    def parse_tle_data(self, tle_data):
        """Parse TLE data into structured format"""
        lines = tle_data.strip().split('\\n')
        objects = []
        
        i = 0
        while i < len(lines) - 2:
            # Look for valid TLE set
            if (i + 2 < len(lines) and 
                lines[i + 1].startswith('1') and 
                lines[i + 2].startswith('2')):
                
                name = lines[i].strip()
                line1 = lines[i + 1].strip()
                line2 = lines[i + 2].strip()
                
                try:
                    # Parse orbital elements
                    satellite = twoline2rv(line1, line2, wgs84)
                    
                    # Calculate current position
                    now = datetime.utcnow()
                    position, velocity = satellite.propagate(
                        now.year, now.month, now.day,
                        now.hour, now.minute, now.second
                    )
                    
                    if position[0] is not None:  # Valid propagation
                        # Calculate altitude
                        r = np.sqrt(sum(x**2 for x in position))
                        altitude = r - 6371.0
                        
                        # Extract orbital parameters
                        inclination = np.degrees(satellite.inclo)
                        eccentricity = satellite.ecco
                        
                        # Classify object type
                        object_type = self.classify_object(name)
                        
                        # Perform reentry analysis
                        reentry_prediction = self.reentry_analyzer.predict_reentry_window(
                            line1, line2
                        )
                        
                        if reentry_prediction:
                            # Calculate overall risk score (0-5 scale)
                            risk_factors = reentry_prediction['risk_assessment']
                            
                            # Combine risks into overall score
                            reentry_risk = risk_factors['overall_reentry_risk']
                            spatial_risk = risk_factors['peak_spatial_risk']
                            
                            # Altitude factor (lower = higher risk)
                            altitude_factor = max(0, min(1, (1000 - altitude) / 800))
                            
                            # Object type factor
                            type_factors = {
                                'DEBRIS': 0.8,
                                'ROCKET BODY': 0.7,
                                'PAYLOAD': 0.5,
                                'UNKNOWN': 0.6
                            }
                            type_factor = type_factors.get(object_type, 0.6)
                            
                            # Calculate final risk score (0-5)
                            overall_risk = (
                                reentry_risk * 0.4 +
                                spatial_risk * 0.3 +
                                altitude_factor * 0.2 +
                                type_factor * 0.1
                            ) * 5
                            
                            risk_score = round(min(5, max(0, overall_risk)), 1)
                            
                            # Extract reentry prediction details
                            reentry_window = reentry_prediction['reentry_window']
                            orbital_params = reentry_prediction['orbital_parameters']
                            
                            objects.append({
                                'name': name,
                                'object_type': object_type,
                                'current_altitude_km': round(altitude, 1),
                                'inclination_deg': round(inclination, 1),
                                'eccentricity': round(eccentricity, 4),
                                'risk_score': risk_score,
                                'reentry_prediction': {
                                    'days_to_reentry': reentry_window['days_from_now'],
                                    'predicted_date': reentry_window['predicted_date'],
                                    'uncertainty_days': reentry_window['uncertainty_days'],
                                    'reentry_probability_percent': round(reentry_risk * 100, 1),
                                    'spatial_risk_percent': round(spatial_risk * 100, 1)
                                },
                                'orbital_decay': {
                                    'decay_rate_km_per_day': orbital_params['predicted_decay_rate_km_per_day'],
                                    'altitude_loss_30_days': round(orbital_params['predicted_decay_rate_km_per_day'] * 30, 1)
                                }
                            })
                
                except Exception as e:
                    print(f"Error parsing object {name}: {e}")
                    continue
                
                i += 3
            else:
                i += 1
        
        return objects
    
    def classify_object(self, name):
        """Classify space object by name"""
        name_upper = name.upper()
        
        if any(word in name_upper for word in ['DEB', 'DEBRIS', 'FRAG']):
            return 'DEBRIS'
        elif any(word in name_upper for word in ['R/B', 'ROCKET BODY', 'BOOSTER']):
            return 'ROCKET BODY'
        elif any(word in name_upper for word in ['PAYLOAD', 'SATELLITE', 'COSMOS', 'FENGYUN']):
            return 'PAYLOAD'
        else:
            return 'UNKNOWN'

# Global parser instance
parser = OptimizedTLEParser()

@app.route('/')
def dashboard():
    """Main dashboard with modern UI"""
    return render_template('index.html')

@app.route('/api/top-risks')
def api_top_risks():
    """JSON API for top 3 risks"""
    try:
        objects = parser.fetch_celestrak_data()
        
        if not objects:
            return jsonify({
                "error": "No data available",
                "timestamp": datetime.utcnow().isoformat()
            }), 503
        
        top_3 = sorted(objects, key=lambda x: x['risk_score'], reverse=True)[:3]
        
        return jsonify({
            "top_3_risks": top_3,
            "total_objects_analyzed": len(objects),
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": "celestrak_live",
            "assessment_method": "hybrid_ai_sgp4_ml"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"API error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/all-risks')
def all_risks():
    """Get all analyzed objects sorted by risk"""
    try:
        objects = parser.fetch_celestrak_data()
        
        if not objects:
            return jsonify({
                "error": "No data available",
                "timestamp": datetime.utcnow().isoformat()
            }), 503
        
        # Sort by risk score
        sorted_objects = sorted(objects, key=lambda x: x['risk_score'], reverse=True)
        
        return jsonify({
            "all_risks": sorted_objects,
            "total_objects": len(sorted_objects),
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": "celestrak_live",
            "assessment_method": "hybrid_ai_sgp4_ml"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "2.0",
        "features": [
            "hybrid_ai_system",
            "sgp4_orbital_mechanics", 
            "machine_learning_ensemble",
            "real_celestrak_data",
            "top_3_risk_display"
        ],
        "timestamp": datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    print("Starting Space Debris Risk Assessment Dashboard")
    print("Features: Modern UI + Hybrid AI + Azure Integration")
    print("Access: http://localhost:5000")
    
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)