"""
Utility Functions for Orbital Mechanics and Math

This module provides helper functions for distance calculations,
orbital element conversions, and trajectory propagation.
"""

import numpy as np
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Constants
EARTH_RADIUS_KM = 6371.0
MU_EARTH = 398600.4418  # Earth's gravitational parameter (km³/s²)
J2 = 1.08262668e-3  # Earth's J2 gravitational harmonic

@dataclass
class Position3D:
    """3D position in Cartesian coordinates (km)."""
    x: float
    y: float
    z: float
    
    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

@dataclass
class Velocity3D:
    """3D velocity in Cartesian coordinates (km/s)."""
    x: float
    y: float
    z: float
    
    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

@dataclass
class StateVector:
    """Orbital state vector."""
    position: Position3D
    velocity: Velocity3D
    timestamp: datetime

def calculate_distance(pos1: Dict, pos2: Dict) -> float:
    """
    Calculate Euclidean distance between two 3D positions.
    
    Args:
        pos1: Position 1 as dict with 'x', 'y', 'z' keys (km)
        pos2: Position 2 as dict with 'x', 'y', 'z' keys (km)
        
    Returns:
        Distance in kilometers
    """
    dx = pos1['x'] - pos2['x']
    dy = pos1['y'] - pos2['y']
    dz = pos1['z'] - pos2['z']
    
    return math.sqrt(dx*dx + dy*dy + dz*dz)

def calculate_relative_velocity(vel1: Dict, vel2: Dict) -> float:
    """
    Calculate relative velocity magnitude between two objects.
    
    Args:
        vel1: Velocity 1 as dict with 'x', 'y', 'z' keys (km/s)
        vel2: Velocity 2 as dict with 'x', 'y', 'z' keys (km/s)
        
    Returns:
        Relative velocity magnitude in km/s
    """
    dvx = vel1['x'] - vel2['x']
    dvy = vel1['y'] - vel2['y']
    dvz = vel1['z'] - vel2['z']
    
    return math.sqrt(dvx*dvx + dvy*dvy + dvz*dvz)

def orbital_elements_to_features(tle_data: Dict) -> Dict[str, float]:
    """
    Extract orbital elements from TLE data and convert to ML features.
    
    Args:
        tle_data: TLE data dictionary
        
    Returns:
        Dictionary of orbital element features
    """
    line1 = tle_data['line1']
    line2 = tle_data['line2']
    
    # Parse orbital elements from TLE line 2
    inclination = float(line2[8:16])  # degrees
    raan = float(line2[17:25])  # Right Ascension of Ascending Node (degrees)
    eccentricity = float("0." + line2[26:33])  # dimensionless
    arg_perigee = float(line2[34:42])  # Argument of perigee (degrees)
    mean_anomaly = float(line2[43:51])  # degrees
    mean_motion = float(line2[52:63])  # revolutions per day
    
    # Calculate derived parameters
    # Semi-major axis from mean motion
    n_rad_per_sec = mean_motion * 2 * math.pi / 86400  # Convert to rad/s
    semi_major_axis = (MU_EARTH / (n_rad_per_sec**2))**(1/3)  # km
    
    # Apogee and perigee
    apogee = semi_major_axis * (1 + eccentricity) - EARTH_RADIUS_KM
    perigee = semi_major_axis * (1 - eccentricity) - EARTH_RADIUS_KM
    
    # Orbital period
    period_minutes = 1440 / mean_motion  # minutes
    
    return {
        'semi_major_axis': semi_major_axis,
        'eccentricity': eccentricity,
        'inclination': inclination,
        'raan': raan,
        'arg_perigee': arg_perigee,
        'mean_anomaly': mean_anomaly,
        'mean_motion': mean_motion,
        'apogee': apogee,
        'perigee': perigee,
        'period_minutes': period_minutes
    }

def tle_to_state_vector(tle_data: Dict, timestamp: datetime = None) -> StateVector:
    """
    Convert TLE data to state vector at specified time.
    
    This is a simplified implementation. For production use,
    consider using SGP4 library for accurate propagation.
    
    Args:
        tle_data: TLE data dictionary
        timestamp: Time for state vector (default: current time)
        
    Returns:
        StateVector object
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    # This is a placeholder implementation
    # In practice, use SGP4 for accurate orbital propagation
    orbital_elements = orbital_elements_to_features(tle_data)
    
    # Simplified circular orbit assumption for demonstration
    r = orbital_elements['semi_major_axis']
    v = math.sqrt(MU_EARTH / r)
    
    # Placeholder position and velocity
    position = Position3D(x=r, y=0.0, z=0.0)
    velocity = Velocity3D(x=0.0, y=v, z=0.0)
    
    return StateVector(position=position, velocity=velocity, timestamp=timestamp)

def propagate_orbit(tle_data: Dict, time_delta_hours: float) -> StateVector:
    """
    Propagate orbital state forward in time.
    
    Args:
        tle_data: TLE data dictionary
        time_delta_hours: Time to propagate forward (hours)
        
    Returns:
        Propagated StateVector
    """
    target_time = datetime.utcnow() + timedelta(hours=time_delta_hours)
    return tle_to_state_vector(tle_data, target_time)

def time_to_closest_approach(tle1: Dict, tle2: Dict, 
                           max_hours: float = 24.0, 
                           step_minutes: float = 10.0) -> float:
    """
    Calculate time until closest approach between two objects.
    
    Args:
        tle1: TLE data for first object
        tle2: TLE data for second object
        max_hours: Maximum time to search (hours)
        step_minutes: Time step for search (minutes)
        
    Returns:
        Time to closest approach in hours
    """
    min_distance = float('inf')
    closest_time = 0.0
    
    steps = int(max_hours * 60 / step_minutes)
    
    for i in range(steps):
        time_hours = i * step_minutes / 60.0
        
        # Get positions at this time
        state1 = propagate_orbit(tle1, time_hours)
        state2 = propagate_orbit(tle2, time_hours)
        
        # Calculate distance
        pos1 = {'x': state1.position.x, 'y': state1.position.y, 'z': state1.position.z}
        pos2 = {'x': state2.position.x, 'y': state2.position.y, 'z': state2.position.z}
        
        distance = calculate_distance(pos1, pos2)
        
        if distance < min_distance:
            min_distance = distance
            closest_time = time_hours
    
    return closest_time

def collision_probability(distance: float, velocity: float, 
                         cross_section: float = 10.0) -> float:
    """
    Calculate collision probability based on distance and velocity.
    
    This is a simplified model. Real collision probability calculation
    requires more sophisticated approaches.
    
    Args:
        distance: Minimum distance (km)
        velocity: Relative velocity (km/s)
        cross_section: Combined cross-sectional area (m²)
        
    Returns:
        Collision probability (0-1)
    """
    # Convert cross-section to km²
    cross_section_km2 = cross_section * 1e-6
    
    # Simple probability model based on distance and cross-section
    if distance <= 0.001:  # Very close approach (< 1 m)
        return 1.0
    
    # Probability decreases with distance
    prob = cross_section_km2 / (math.pi * distance**2)
    
    # Adjust for relative velocity (higher velocity = less time to react)
    velocity_factor = min(1.0, velocity / 10.0)  # Normalize around 10 km/s
    prob *= (1 + velocity_factor)
    
    return min(1.0, prob)

def orbital_decay_prediction(tle_data: Dict, days_ahead: int = 30) -> List[float]:
    """
    Predict orbital decay over time.
    
    Args:
        tle_data: TLE data dictionary
        days_ahead: Number of days to predict ahead
        
    Returns:
        List of predicted altitudes (km) for each day
    """
    elements = orbital_elements_to_features(tle_data)
    initial_perigee = elements['perigee']
    
    # Simple atmospheric drag model
    # Real implementation would use atmospheric density models
    decay_rate = 0.1  # km/day (placeholder)
    
    altitudes = []
    for day in range(days_ahead + 1):
        altitude = max(0, initial_perigee - decay_rate * day)
        altitudes.append(altitude)
    
    return altitudes

def spherical_to_cartesian(r: float, lat: float, lon: float) -> Position3D:
    """
    Convert spherical coordinates to Cartesian.
    
    Args:
        r: Radius (km)
        lat: Latitude (degrees)
        lon: Longitude (degrees)
        
    Returns:
        Cartesian position
    """
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    
    x = r * math.cos(lat_rad) * math.cos(lon_rad)
    y = r * math.cos(lat_rad) * math.sin(lon_rad)
    z = r * math.sin(lat_rad)
    
    return Position3D(x=x, y=y, z=z)

def cartesian_to_spherical(position: Position3D) -> Tuple[float, float, float]:
    """
    Convert Cartesian coordinates to spherical.
    
    Args:
        position: Cartesian position
        
    Returns:
        Tuple of (radius, latitude, longitude) in km and degrees
    """
    r = math.sqrt(position.x**2 + position.y**2 + position.z**2)
    lat = math.degrees(math.asin(position.z / r))
    lon = math.degrees(math.atan2(position.y, position.x))
    
    return r, lat, lon

def ground_track_prediction(tle_data: Dict, duration_hours: float = 24.0, 
                          step_minutes: float = 5.0) -> List[Tuple[float, float]]:
    """
    Predict ground track (lat/lon) for an orbit.
    
    Args:
        tle_data: TLE data dictionary
        duration_hours: Duration to predict (hours)
        step_minutes: Time step (minutes)
        
    Returns:
        List of (latitude, longitude) tuples in degrees
    """
    ground_track = []
    steps = int(duration_hours * 60 / step_minutes)
    
    for i in range(steps):
        time_hours = i * step_minutes / 60.0
        state = propagate_orbit(tle_data, time_hours)
        
        r, lat, lon = cartesian_to_spherical(state.position)
        ground_track.append((lat, lon))
    
    return ground_track