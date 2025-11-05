# Space Debris Risk Assessment Dashboard

## Overview
Modern web dashboard for space debris risk assessment using hybrid AI models and real-time data from Azure APIs.

## Features
- **Real-time Tracking**: Live space debris tracking and risk assessment
- **Modern UI**: Glass-morphism design with responsive layout
- **Azure Integration**: Connects to Azure space-debris-api-v2 for live data
- **Professional Interface**: Space-themed dashboard with interactive elements
- **Hybrid AI System**: Combines physics-based SGP4 propagation with ensemble machine learning models
- **Top 3 Risk Display**: Shows highest risk objects with detailed predictions
- **Reentry Predictions**: When and where predictions with uncertainty bounds
- **Professional Output**: Clean, emoji-free interface for production use

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run Application
```bash
python main.py
```

### Access Interface
- **Web Interface**: http://localhost:5000 (Top 3 risks with detailed predictions)
- **JSON API**: http://localhost:5000/api/top-risks
- **All Risks**: http://localhost:5000/api/all-risks
- **Health Check**: http://localhost:5000/health

## API Endpoints

### GET /
Main interface showing top 3 highest risk objects with:
- Risk scores (0-5 scale)
- Reentry predictions with dates and probabilities
- Orbital decay analysis
- Uncertainty bounds

### GET /api/top-risks
JSON API returning top 3 highest risk objects with complete analysis

### GET /api/all-risks
JSON API returning all analyzed objects sorted by risk score

### GET /health
System health and feature status

## Risk Assessment Methodology

### Risk Score (0-5 Scale)
- **0**: No immediate risk
- **1-2**: Low risk, stable orbit
- **3**: Moderate risk, monitoring required
- **4**: High risk, reentry likely within year
- **5**: Critical risk, immediate reentry threat

### Hybrid AI Components
1. **SGP4 Physics**: Orbital mechanics and propagation
2. **Random Forest**: Ensemble learning for decay prediction
3. **Gradient Boosting**: Advanced pattern recognition
4. **Neural Network**: Complex orbital dynamics modeling

### Data Sources
- **CelesTrak Active Satellites**: Current operational satellites
- **CelesTrak Space Stations**: ISS and other stations
- **CelesTrak Recent Objects**: Objects launched in last 30 days

## Technical Architecture

### Core Components
- `HybridOrbitDecayPredictor`: ML ensemble for decay rate prediction
- `ReentryAnalyzer`: Advanced reentry window and location prediction
- `OptimizedTLEParser`: Real-time CelesTrak data processing

### Model Performance
- Decay Rate Prediction: R² = 1.000
- Reentry Probability: R² = 0.999
- Spatial Risk Assessment: R² = 1.000

## Deployment

### Local Development
```bash
python main.py
```

### Production Deployment
1. Set environment variables for production
2. Use production WSGI server (gunicorn, uWSGI)
3. Configure reverse proxy (nginx, Apache)
4. Set up monitoring and logging

### Azure ML Integration
- Trained models can be deployed to Azure ML workspace
- Real-time inference endpoints available
- Batch processing for large-scale analysis

## Project Structure
```
Space Debris Risk Assessment/
├── main.py                 # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── azure_ml_deployment.ipynb  # Model development notebook
└── deployment/            # Deployment assets
    ├── hybrid_models/     # Trained AI models
    └── hybrid_ai_integration.py  # Integration code
```

## License
This project is for educational and research purposes. Space debris tracking data is provided by CelesTrak.org under their terms of service.

## Acknowledgments
- **CelesTrak.org**: Real-time TLE data source
- **SGP4 Library**: Orbital mechanics calculations
- **Azure ML**: Model training and deployment platform
- **Flask**: Web application framework