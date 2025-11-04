# 🛰️ Space Debris Earth Impact Risk Assessment

A machine learning application for assessing the Earth impact probability of orbital debris using real TLE (Two-Line Element) data from CelesTrak.

Built a FastAPI backend that analyzes and predicts orbital debris collision risks using Kalman filters, TLE data parsing, and machine learning models for trajectory prediction. Designed APIs for satellite data ingestion, debris risk computation, and real-time alert generation to support scalable aerospace applications.

## 🎯 Features

- **Real-time TLE Data**: Loads current orbital debris data from CelesTrak
- **Earth Impact Assessment**: 0-5 scale probability assessment (0=No risk, 5=100% Earth impact)
- **Comprehensive Risk Factors**: Altitude, atmospheric drag, collision probability, eccentricity, decay rate
- **Top Risk Identification**: Shows the highest risk satellite pairs with detailed analysis
- **Multiple Output Formats**: Summary, table, and JSON formats
- **Scalable Processing**: Configure from small demos to full dataset analysis

## 🚀 Quick Start

### Option 1: Run Risk Assessment
```bash
# Install dependencies
pip install -r requirements.txt

# Run risk assessment
python test_ml_app.py
```

### Option 2: Azure ML Deployment (Requires Azure Setup)
```bash
# Deploy to Azure ML
python deploy_simple_v1.py
```

## 📊 Usage Examples

```bash
# Run basic risk assessment
python test_ml_app.py

# Test the scoring script locally
python -c "
import score
score.init()
result = score.run('{\"data\": [{\"name\": \"Test Satellite\", \"norad_id\": \"12345\", \"mean_motion\": 15.5, \"inclination\": 98.0, \"eccentricity\": 0.001}]}')
print(result)
"
```

## 🔬 Risk Assessment Scale

- **EXTREME (4.5-5.0)**: 90-100% Earth impact probability
- **CRITICAL (3.5-4.5)**: 70-90% Earth impact probability  
- **HIGH (2.5-3.5)**: 50-70% Earth impact probability
- **MEDIUM (1.5-2.5)**: 30-50% Earth impact probability
- **LOW (0.5-1.5)**: 10-30% Earth impact probability
- **MINIMAL (0-0.5)**: 0-10% Earth impact probability

## 📂 Project Structure

```
orbital-debris-ml/
├── test_ml_app.py          # Main application
├── src/
│   ├── risk_model.py       # Core ML model
│   ├── tle_loader.py       # TLE data loading
│   ├── utils.py            # Utility functions
│   └── __init__.py         # Package initialization
├── env/
│   └── conda.yml           # Conda environment
├── requirements.txt        # Python dependencies
├── deploy.py              # Deployment script
└── README.md              # This file
```

## 🛰️ Data Source

This application uses real orbital debris data from CelesTrak, specifically the Cosmos-2251 debris catalog, which contains data for 598+ debris objects.

## 🔧 Risk Calculation

The Earth impact probability is calculated using weighted factors:

- **Altitude Risk (30%)**: Lower altitude = higher atmospheric drag
- **Atmospheric Drag Factor (25%)**: Orbital decay acceleration
- **Collision Probability (20%)**: Potential for fragmentation events
- **Orbital Eccentricity (15%)**: Elliptical orbits increase instability
- **Decay Rate (10%)**: Rate of orbital degradation

## 📈 Sample Output

```
🚨 TOP 3 HIGHEST EARTH IMPACT RISK PAIRS:
#1 HIGHEST RISK PAIR:
   Satellite 1: COSMOS 2251 (ID: 22675)
   Satellite 2: COSMOS 2251 DEB (ID: 34958)
   🎯 Risk Score: 2.291/5.0
   📊 Impact Probability: 45.81%
   ⚠️  Risk Level: MEDIUM
   🌍 Est. Impact Time: 2028-01-05T15:44:09
   📍 Est. Impact Location: -60.50°, 55.29°
```

## 🚨 Important Notes

- This is a simulation/research tool, not operational space surveillance
- Risk assessments are based on simplified models for demonstration
- Real space surveillance requires specialized orbital analysis software
- TLE data accuracy depends on tracking network updates

## 🔬 Dependencies

### Core Requirements
- Python 3.8+
- requests, numpy, scipy

### Enhanced Functionality (Optional)
- sgp4, poliastro, astropy (orbital mechanics)
- scikit-learn, tensorflow (machine learning)
- matplotlib, plotly (visualization)

## 📄 License

This project is for educational and research purposes.
