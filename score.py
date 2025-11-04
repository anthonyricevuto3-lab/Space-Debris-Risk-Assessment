"""
Simple Azure ML Score Script for Space Debris Risk Assessment
No complex dependencies - just basic Python libraries
"""

import json

def init():
    """Initialize the model"""
    global model_initialized
    model_initialized = True
    print("Space Debris Risk Assessment model initialized")

def run(raw_data: str) -> str:
    """
    Run inference on input data
    Args:
        raw_data: JSON string containing satellite data
    Returns:
        JSON string with risk assessment results
    """
    try:
        # Parse input data
        data = json.loads(raw_data)
        
        # Extract satellite parameters
        satellites = data.get('data', [])
        if not satellites:
            return json.dumps({"error": "No satellite data provided"})
        
        results = []
        
        for satellite in satellites:
            # Simple risk calculation based on key parameters
            risk_score = calculate_simple_risk(satellite)
            
            result = {
                "satellite_name": satellite.get("name", "Unknown"),
                "norad_id": satellite.get("norad_id", "Unknown"),
                "earth_impact_risk": min(risk_score, 5.0),  # Cap at 5
                "risk_level": get_risk_level(risk_score),
                "factors": get_risk_factors(satellite)
            }
            results.append(result)
        
        # Sort by risk score (highest first)
        results.sort(key=lambda x: x["earth_impact_risk"], reverse=True)
        
        # Return top 3 highest risk
        top_risks = results[:3]
        
        return json.dumps({
            "status": "success",
            "top_risk_satellites": top_risks,
            "total_analyzed": len(satellites),
            "model_version": "1.0-simple"
        })
        
    except Exception as e:
        return json.dumps({"error": f"Processing error: {str(e)}"})

def calculate_simple_risk(satellite):
    """Calculate risk score using simple algorithms - no external dependencies"""
    
    # Default risk factors
    altitude_risk = 0.0
    inclination_risk = 0.0
    eccentricity_risk = 0.0
    
    # Altitude risk (lower altitude = higher risk)
    try:
        # Try to get altitude from mean motion or direct altitude
        mean_motion = satellite.get("mean_motion", 0)
        if mean_motion > 0:
            # Convert mean motion to approximate altitude
            # Higher mean motion = lower altitude = higher risk
            if mean_motion > 15:  # Very low orbit
                altitude_risk = 2.0
            elif mean_motion > 10:  # Low orbit
                altitude_risk = 1.5
            elif mean_motion > 5:  # Medium orbit
                altitude_risk = 1.0
            else:  # High orbit
                altitude_risk = 0.5
    except:
        altitude_risk = 1.0  # Default moderate risk
    
    # Inclination risk (certain inclinations more dangerous)
    try:
        inclination = satellite.get("inclination", 0)
        if 95 <= inclination <= 105:  # Polar/sun-synchronous orbits
            inclination_risk = 1.5
        elif 50 <= inclination <= 70:  # Common collision-prone inclinations
            inclination_risk = 1.2
        else:
            inclination_risk = 0.8
    except:
        inclination_risk = 1.0
    
    # Eccentricity risk (higher eccentricity = more unpredictable)
    try:
        eccentricity = satellite.get("eccentricity", 0)
        if eccentricity > 0.1:  # Highly elliptical
            eccentricity_risk = 1.5
        elif eccentricity > 0.05:  # Moderately elliptical
            eccentricity_risk = 1.2
        else:  # Nearly circular
            eccentricity_risk = 0.8
    except:
        eccentricity_risk = 1.0
    
    # Age factor (older debris more unpredictable)
    age_risk = 0.0
    try:
        epoch = satellite.get("epoch", "")
        if epoch:
            # Simple age estimation based on epoch year
            current_year = 2025
            epoch_year = int(epoch.split("-")[0]) if "-" in epoch else 2020
            age = current_year - epoch_year
            if age > 20:
                age_risk = 1.5
            elif age > 10:
                age_risk = 1.2
            else:
                age_risk = 0.8
    except:
        age_risk = 1.0
    
    # Combine risk factors
    total_risk = altitude_risk + inclination_risk + eccentricity_risk + age_risk
    
    # Add some variation based on satellite ID (deterministic but varies per satellite)
    satellite_id = str(satellite.get("norad_id", "0"))
    try:
        variation = (hash(satellite_id) % 100) / 200.0  # -0.25 to +0.25
    except:
        variation = 0.0
    
    final_risk = total_risk + variation
    return max(0.0, min(5.0, final_risk))  # Clamp between 0 and 5

def get_risk_level(risk_score):
    """Convert risk score to descriptive level"""
    if risk_score >= 4.0:
        return "CRITICAL"
    elif risk_score >= 3.0:
        return "HIGH"
    elif risk_score >= 2.0:
        return "MODERATE"
    elif risk_score >= 1.0:
        return "LOW"
    else:
        return "MINIMAL"

def get_risk_factors(satellite):
    """Get list of contributing risk factors"""
    factors = []
    
    try:
        mean_motion = satellite.get("mean_motion", 0)
        if mean_motion > 15:
            factors.append("Very low altitude orbit")
        elif mean_motion > 10:
            factors.append("Low Earth orbit")
    except:
        pass
    
    try:
        inclination = satellite.get("inclination", 0)
        if 95 <= inclination <= 105:
            factors.append("Polar/sun-synchronous orbit")
    except:
        pass
    
    try:
        eccentricity = satellite.get("eccentricity", 0)
        if eccentricity > 0.1:
            factors.append("Highly elliptical orbit")
    except:
        pass
    
    try:
        epoch = satellite.get("epoch", "")
        if epoch:
            current_year = 2025
            epoch_year = int(epoch.split("-")[0]) if "-" in epoch else 2020
            age = current_year - epoch_year
            if age > 20:
                factors.append("Very old debris (>20 years)")
            elif age > 10:
                factors.append("Old debris (>10 years)")
    except:
        pass
    
    if not factors:
        factors.append("Standard orbital parameters")
    
    return factors