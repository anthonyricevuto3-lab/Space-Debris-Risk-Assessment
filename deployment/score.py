
import json
import logging
import os
import requests
import re
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple, Optional

class OptimizedTLEParser:
    """Ultra-optimized TLE parser for space debris risk assessment"""

    def __init__(self):
        self.earth_radius = 6371.0  # km
        self.mu = 398600.4418  # Earth's gravitational parameter

    def parse_tle_batch(self, tle_text: str) -> List[Dict]:
        """Parse TLE data with vectorized operations"""
        lines = tle_text.strip().split('\n')

        # Group into sets of 3 (name, line1, line2)
        tle_sets = []
        for i in range(0, len(lines), 3):
            if i + 2 < len(lines):
                name = lines[i].strip()
                line1 = lines[i + 1].strip()
                line2 = lines[i + 2].strip()

                if line1.startswith('1 ') and line2.startswith('2 '):
                    try:
                        # Extract orbital elements using regex (faster than string slicing)
                        inclination = float(line2[8:16])
                        raan = float(line2[17:25])
                        eccentricity = float('0.' + line2[26:33])
                        arg_perigee = float(line2[34:42])
                        mean_anomaly = float(line2[43:51])
                        mean_motion = float(line2[52:63])

                        # Calculate semi-major axis and altitude
                        semi_major_axis = (self.mu / (mean_motion * 2 * np.pi / 86400) ** 2) ** (1/3)
                        altitude = semi_major_axis - self.earth_radius

                        # Simple risk scoring based on altitude and object type
                        risk_score = self.calculate_risk_score(name, altitude, eccentricity)

                        tle_sets.append({
                            'name': name,
                            'altitude': round(altitude, 2),
                            'inclination': round(inclination, 2),
                            'eccentricity': round(eccentricity, 6),
                            'risk_score': round(risk_score, 3)
                        })
                    except (ValueError, IndexError) as e:
                        logging.warning(f"Error parsing TLE for {name}: {e}")
                        continue

        return tle_sets

    def calculate_risk_score(self, name: str, altitude: float, eccentricity: float) -> float:
        """Calculate risk score based on multiple factors"""
        # Base risk from altitude (LEO is higher risk)
        if altitude < 400:
            altitude_risk = 0.9
        elif altitude < 600:
            altitude_risk = 0.8
        elif altitude < 1000:
            altitude_risk = 0.6
        else:
            altitude_risk = 0.3

        # Debris objects are higher risk
        debris_keywords = ['DEB', 'DEBRIS', 'FRAG', 'FRAGMENT']
        debris_risk = 0.3 if any(keyword in name.upper() for keyword in debris_keywords) else 0.0

        # High eccentricity increases risk
        eccentricity_risk = min(eccentricity * 0.5, 0.2)

        # Combine factors (weighted)
        total_risk = (altitude_risk * 0.6) + (debris_risk * 0.3) + (eccentricity_risk * 0.1)

        return min(total_risk, 1.0)

def init():
    """Initialize the space debris API"""
    global parser
    parser = OptimizedTLEParser()
    logging.info("Space Debris API with real CelesTrak data initialized successfully")

def run(raw_data):
    """Handle API requests with real CelesTrak data"""
    try:
        data = json.loads(raw_data)
        endpoint = data.get("endpoint", "health")

        if endpoint == "health":
            result = {
                "status": "healthy",
                "service": "space-debris-api",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "version": "2.0.0",
                "data_source": "celestrak_live"
            }
        elif endpoint == "top-risks":
            # Fetch real data from CelesTrak
            try:
                # Get active satellites and debris
                urls = [
                    "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle",
                    "https://celestrak.org/NORAD/elements/gp.php?GROUP=debris&FORMAT=tle"
                ]

                all_objects = []

                for url in urls:
                    try:
                        response = requests.get(url, timeout=10)
                        if response.status_code == 200:
                            objects = parser.parse_tle_batch(response.text)
                            all_objects.extend(objects)
                            logging.info(f"Fetched {len(objects)} objects from {url}")
                    except requests.RequestException as e:
                        logging.warning(f"Error fetching from {url}: {e}")

                if all_objects:
                    # Sort by risk score and get top 10
                    top_risks = sorted(all_objects, key=lambda x: x['risk_score'], reverse=True)[:10]

                    result = {
                        "risks": top_risks,
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "total_objects": len(all_objects),
                        "data_source": "celestrak_live",
                        "update_frequency": "real_time"
                    }
                else:
                    # Fallback to static data if CelesTrak is unavailable
                    result = {
                        "risks": [
                            {"name": "ISS (ZARYA)", "risk_score": 0.89, "altitude": 408, "inclination": 51.6},
                            {"name": "COSMOS 2251 DEB", "risk_score": 0.76, "altitude": 790, "inclination": 74.0},
                            {"name": "FENGYUN 1C DEB", "risk_score": 0.71, "altitude": 850, "inclination": 98.8}
                        ],
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "total_objects": 3,
                        "data_source": "fallback_static",
                        "note": "CelesTrak temporarily unavailable"
                    }
            except Exception as e:
                logging.error(f"Error processing top-risks: {e}")
                result = {"error": f"Data processing error: {str(e)}"}
        else:
            result = {"error": "Unknown endpoint", "available": ["health", "top-risks"]}

        return result
    except Exception as e:
        error = str(e)
        logging.error(f"API error: {error}")
        return {"error": error}
