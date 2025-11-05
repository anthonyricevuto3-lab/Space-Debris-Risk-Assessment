# Space Debris Earth Impact Risk Assessment

A high-performance Flask web application for assessing the Earth impact probability of orbital debris using real TLE (Two-Line Element) data from CelesTrak.

**Ultra-Fast Processing**: Analyzes 598+ space debris objects in under 1 second using optimized vectorized calculations and real-time CelesTrak data integration.

## Features

- **Real-time TLE Data**: Loads current orbital debris data from CelesTrak (Cosmos 2251 debris)
- **Earth Impact Assessment**: 0-5 scale probability assessment (0=No risk, 5=100% Earth impact)
- **Ultra-High Performance**: Processes 598 objects in ~0.8 seconds using optimized algorithms
- **Top Risk Identification**: Shows the top 3 highest risk objects with detailed analysis
- **RESTful API**: `/api/top-risks` endpoint for JSON responses
- **Web Interface**: Simple HTML interface for interactive risk assessment
- **Scalable Processing**: Vectorized calculations for maximum performance

## Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app_standalone.py

# Access web interface
# Open browser to http://localhost:5000

# API endpoint
# GET http://localhost:5000/api/top-risks
```

### Azure Deployment
```bash
# The app is ready for Azure App Service deployment
# Use app.py as the entry point for Azure
```

## API Usage

### Get Top Risk Objects
```bash
# Get top 3 risk objects as JSON
curl http://localhost:5000/api/top-risks

# Example response:
{
  "top_risks": [
    {
      "object_name": "COSMOS 2251 DEB",
      "norad_id": "34454",
      "impact_probability": 85.2,
      "risk_score": 4,
      "altitude": 776.5,
      "risk_factors": {...}
    }
  ],
  "total_objects": 598,
  "processing_time": 0.831
}
```

## Risk Assessment Scale

- **EXTREME (4.5-5.0)**: 90-100% Earth impact probability
- **CRITICAL (3.5-4.5)**: 70-90% Earth impact probability 
- **HIGH (2.5-3.5)**: 50-70% Earth impact probability
- **MEDIUM (1.5-2.5)**: 30-50% Earth impact probability
- **LOW (0.5-1.5)**: 10-30% Earth impact probability
- **MINIMAL (0-0.5)**: 0-10% Earth impact probability

## 📂 Project Structure

```
orbital-debris-ml/
├── app_standalone.py   # Main Flask application with optimized TLE parser
├── app.py             # Azure App Service entry point
├── requirements.txt   # Python dependencies (Flask, requests, gunicorn)
├── .github/
│  └── workflows/      # GitHub Actions CI/CD pipelines
│     ├── ci-cd.yml        # Main CI/CD with Azure deployment
│     ├── cross-platform.yml  # Multi-OS testing
│     └── release.yml      # Release automation
└── README.md          # This file
```

## GitHub Actions CI/CD

This project includes automated CI/CD pipelines:

- **CI/CD Pipeline**: Automated testing, building, and Azure deployment
- **Cross-Platform Testing**: Tests on Ubuntu, Windows, and macOS with Python 3.9-3.11
- **Release Automation**: Automated release packaging and deployment

### Required GitHub Secrets (for Azure deployment):
- `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID
- `AZURE_CREDENTIALS`: Azure service principal credentials

## Data Source

This application uses real orbital debris data from CelesTrak, specifically the Cosmos-2251 debris catalog, which contains data for 598+ debris objects from: 
`https://celestrak.org/NORAD/elements/gp.php?GROUP=cosmos-2251-debris&FORMAT=tle`

## Risk Calculation

The Earth impact probability is calculated using weighted factors:

- **Altitude Risk (30%)**: Lower altitude = higher atmospheric drag
- **Atmospheric Drag Factor (25%)**: Orbital decay acceleration  
- **Collision Probability (20%)**: Potential for fragmentation events
- **Orbital Eccentricity (15%)**: Elliptical orbits increase instability
- **Decay Rate (10%)**: Rate of orbital degradation

## 📈 Sample Output

```
🚨 TOP 3 HIGHEST EARTH IMPACT RISK OBJECTS:
#1 HIGHEST RISK:
  Object: COSMOS 2251 DEB (ID: 34454)
  Risk Score: 4.2/5.0
  Impact Probability: 85.2%
  Risk Level: EXTREME
  Altitude: 776.5 km
```

## 🚨 Important Notes

- This is a simulation/research tool, not operational space surveillance
- Risk assessments are based on simplified models for demonstration purposes
- Real space surveillance requires specialized orbital analysis software and radar tracking
- TLE data accuracy depends on NORAD tracking network updates
- Processing optimized for speed - 598 objects processed in ~0.8 seconds

## Technologies Used

- **Flask**: Web framework for API and interface
- **Python 3.11**: Core programming language
- **Requests**: HTTP client for CelesTrak data fetching
- **NumPy-style calculations**: Vectorized mathematical operations for performance
- **GitHub Actions**: CI/CD automation
- **Azure App Service**: Cloud deployment platform

## Performance Metrics

- **Objects Processed**: 598 Cosmos 2251 debris objects
- **Processing Time**: ~0.8 seconds for full dataset
- **Memory Efficient**: Optimized TLE parsing and risk calculations
- **Real-time Data**: Live CelesTrak integration

## Dependencies

### Core Requirements
- Python 3.8+
- requests, numpy, scipy

### Enhanced Functionality (Optional)
- sgp4, poliastro, astropy (orbital mechanics)
- scikit-learn, tensorflow (machine learning)
- matplotlib, plotly (visualization)

## 📄 License

This project is for educational and research purposes.
