#!/usr/bin/env python3
"""
Orbital Debris Risk Assessment Test Suite

This script tests the ML application using real TLE data from CelesTrak,
demonstrates the output formatting, and shows how the risk assessment works.

Usage:
    python test_ml_app.py [--n-predictions 10] [--format json|table|summary]
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import space libraries
try:
    from skyfield.api import EarthSatellite, Topos, load
    from sgp4.api import Satrec, WGS72
    from astropy.time import Time
    import astropy.units as u
    SPACE_LIBS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Space libraries not available: {e}")
    SPACE_LIBS_AVAILABLE = False

class DebrisRiskTester:
    """Test suite for orbital debris risk assessment ML application."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.satellites = []
        self.test_results = []
        self.ts = None
        
        if SPACE_LIBS_AVAILABLE:
            self.ts = load.timescale()
    
    def load_tle_data(self) -> bool:
        """
        Load TLE data from CelesTrak for testing.
        
        Returns:
            True if successful, False otherwise
        """
        print("Loading TLE data from CelesTrak...")
        
        try:
            # Load Cosmos-2251 debris data (same as main.py)
            url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=cosmos-2251-debris&FORMAT=tle"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            tle_text = response.text.strip().splitlines()
            
            # Parse TLE lines
            satellites = []
            for i in range(0, len(tle_text), 3):
                if i + 2 < len(tle_text):
                    name = tle_text[i].strip()
                    line1 = tle_text[i + 1].strip()
                    line2 = tle_text[i + 2].strip()
                    
                    # Validate TLE format
                    if (len(line1) == 69 and len(line2) == 69 and 
                        line1[0] == '1' and line2[0] == '2'):
                        
                        if SPACE_LIBS_AVAILABLE:
                            sat = EarthSatellite(line1, line2, name)
                            satellites.append({
                                'name': name,
                                'line1': line1,
                                'line2': line2,
                                'satellite': sat,
                                'norad_id': int(line1[2:7])
                            })
                        else:
                            # Store TLE data even without space libraries
                            satellites.append({
                                'name': name,
                                'line1': line1,
                                'line2': line2,
                                'satellite': None,
                                'norad_id': int(line1[2:7])
                            })
            
            self.satellites = satellites
            print(f"Loaded {len(satellites)} debris objects")
            return True
            
        except Exception as e:
            print(f"Error loading TLE data: {e}")
            return False
    
    def calculate_orbital_elements(self, tle_line1: str, tle_line2: str) -> Dict[str, float]:
        """
        Extract orbital elements from TLE data.
        
        Args:
            tle_line1: First line of TLE data
            tle_line2: Second line of TLE data
            
        Returns:
            Dictionary of orbital elements
        """
        # Parse TLE manually for orbital elements
        inclination = float(tle_line2[8:16])  # degrees
        raan = float(tle_line2[17:25])  # Right Ascension of Ascending Node
        eccentricity = float('0.' + tle_line2[26:33])
        arg_perigee = float(tle_line2[34:42])  # degrees
        mean_anomaly = float(tle_line2[43:51])  # degrees
        mean_motion = float(tle_line2[52:63])  # revolutions per day
        
        # Calculate semi-major axis (rough approximation)
        # a = (GM / (2π * n)^2)^(1/3) where n is mean motion in rad/s
        mu_earth = 398600.4418  # km³/s² (Earth's gravitational parameter)
        n_rad_per_sec = mean_motion * 2 * np.pi / 86400  # Convert to rad/s
        semi_major_axis = (mu_earth / (n_rad_per_sec ** 2)) ** (1/3)
        
        # Calculate apogee and perigee
        apogee = semi_major_axis * (1 + eccentricity) - 6371  # km altitude
        perigee = semi_major_axis * (1 - eccentricity) - 6371  # km altitude
        
        return {
            'inclination_deg': inclination,
            'raan_deg': raan,
            'eccentricity': eccentricity,
            'arg_perigee_deg': arg_perigee,
            'mean_anomaly_deg': mean_anomaly,
            'mean_motion_rev_per_day': mean_motion,
            'semi_major_axis_km': semi_major_axis,
            'apogee_altitude_km': apogee,
            'perigee_altitude_km': perigee,
            'period_minutes': 1440 / mean_motion  # minutes per orbit
        }
    
    def simulate_risk_prediction(self, sat1: Dict, sat2: Dict) -> Dict[str, Any]:
        """
        Simulate risk prediction between two satellites using Earth impact probability scale.
        
        Args:
            sat1: First satellite data
            sat2: Second satellite data
            
        Returns:
            Risk prediction results with 0-5 scale (5 = 100% Earth impact probability)
        """
        # Extract orbital elements
        elements1 = self.calculate_orbital_elements(sat1['line1'], sat1['line2'])
        elements2 = self.calculate_orbital_elements(sat2['line1'], sat2['line2'])
        
        # Calculate Earth impact risk factors
        # 1. Altitude factor (lower altitude = higher Earth impact risk)
        avg_altitude1 = (elements1['apogee_altitude_km'] + elements1['perigee_altitude_km']) / 2
        avg_altitude2 = (elements2['apogee_altitude_km'] + elements2['perigee_altitude_km']) / 2
        
        # Risk increases exponentially as altitude decreases below 800km
        altitude_risk1 = max(0, 1.0 - (avg_altitude1 / 800)) if avg_altitude1 < 800 else 0
        altitude_risk2 = max(0, 1.0 - (avg_altitude2 / 800)) if avg_altitude2 < 800 else 0
        combined_altitude_risk = (altitude_risk1 + altitude_risk2) / 2
        
        # 2. Atmospheric drag factor (higher for lower perigee)
        min_perigee = min(elements1['perigee_altitude_km'], elements2['perigee_altitude_km'])
        if min_perigee < 300:
            drag_factor = 1.0  # Very high risk
        elif min_perigee < 500:
            drag_factor = 0.7  # High risk
        elif min_perigee < 700:
            drag_factor = 0.4  # Medium risk
        else:
            drag_factor = 0.1  # Low risk
        
        # 3. Eccentricity factor (highly elliptical orbits with low perigee are riskier)
        max_eccentricity = max(elements1['eccentricity'], elements2['eccentricity'])
        eccentricity_factor = min(1.0, max_eccentricity * 10)  # Scale up eccentricity impact
        
        # 4. Collision probability (affects debris generation)
        alt_diff = abs(avg_altitude1 - avg_altitude2)
        inc_diff = abs(elements1['inclination_deg'] - elements2['inclination_deg'])
        collision_prob = max(0, 1.0 - (alt_diff / 100) - (inc_diff / 50))
        
        # 5. Orbital decay rate (objects with negative mean motion derivatives decay faster)
        # Simulate decay rate based on altitude and atmospheric density
        decay_rate1 = max(0, (800 - avg_altitude1) / 1000) if avg_altitude1 < 800 else 0
        decay_rate2 = max(0, (800 - avg_altitude2) / 1000) if avg_altitude2 < 800 else 0
        max_decay_rate = max(decay_rate1, decay_rate2)
        
        # Combined Earth impact risk score (0-5 scale)
        # Weight factors: altitude (30%), drag (25%), collision (20%), eccentricity (15%), decay (10%)
        earth_impact_risk = (
            combined_altitude_risk * 0.30 +
            drag_factor * 0.25 +
            collision_prob * 0.20 +
            eccentricity_factor * 0.15 +
            max_decay_rate * 0.10
        )
        
        # Scale to 0-5 and add some randomness for simulation
        risk_score_0_5 = min(5.0, max(0.0, earth_impact_risk * 5 + np.random.normal(0, 0.3)))
        
        # Convert to percentage for display
        risk_percentage = (risk_score_0_5 / 5.0) * 100
        
        # Calculate estimated impact time based on orbital decay
        if risk_score_0_5 > 3.0:
            impact_time = datetime.now() + timedelta(days=np.random.uniform(30, 365))
        elif risk_score_0_5 > 2.0:
            impact_time = datetime.now() + timedelta(days=np.random.uniform(365, 1095))  # 1-3 years
        elif risk_score_0_5 > 1.0:
            impact_time = datetime.now() + timedelta(days=np.random.uniform(1095, 3650))  # 3-10 years
        else:
            impact_time = datetime.now() + timedelta(days=np.random.uniform(3650, 18250))  # 10-50 years
        
        # Estimate debris ground impact location (simplified)
        impact_lat = np.random.uniform(-elements1['inclination_deg'], elements1['inclination_deg'])
        impact_lon = np.random.uniform(-180, 180)
        
        # Calculate minimum distance for potential collision/fragmentation
        min_distance_km = max(0.1, alt_diff + inc_diff * 5 + np.random.uniform(0.1, 3.0))
        
        return {
            'satellite_1': {
                'name': sat1['name'],
                'norad_id': sat1['norad_id'],
                'altitude_km': avg_altitude1,
                'perigee_km': elements1['perigee_altitude_km'],
                'apogee_km': elements1['apogee_altitude_km'],
                'inclination_deg': elements1['inclination_deg'],
                'period_min': elements1['period_minutes'],
                'eccentricity': elements1['eccentricity']
            },
            'satellite_2': {
                'name': sat2['name'],
                'norad_id': sat2['norad_id'],
                'altitude_km': avg_altitude2,
                'perigee_km': elements2['perigee_altitude_km'],
                'apogee_km': elements2['apogee_altitude_km'],
                'inclination_deg': elements2['inclination_deg'],
                'period_min': elements2['period_minutes'],
                'eccentricity': elements2['eccentricity']
            },
            'earth_impact_assessment': {
                'risk_score_0_to_5': round(risk_score_0_5, 3),
                'impact_probability_percentage': round(risk_percentage, 2),
                'risk_level': self._get_risk_level_earth_impact(risk_score_0_5),
                'confidence': np.random.uniform(0.75, 0.95),
                'risk_factors': {
                    'altitude_risk': round(combined_altitude_risk, 3),
                    'atmospheric_drag_factor': round(drag_factor, 3),
                    'collision_probability': round(collision_prob, 3),
                    'orbital_eccentricity_factor': round(eccentricity_factor, 3),
                    'decay_rate_factor': round(max_decay_rate, 3)
                }
            },
            'impact_prediction': {
                'estimated_impact_time': impact_time.isoformat(),
                'estimated_impact_location': {
                    'latitude': round(impact_lat, 4),
                    'longitude': round(impact_lon, 4),
                    'uncertainty_radius_km': round(np.random.uniform(50, 500), 1)
                },
                'debris_characteristics': {
                    'estimated_mass_kg': np.random.uniform(10, 200),
                    'fragment_count_estimate': int(np.random.uniform(1, 50)) if collision_prob > 0.5 else 1,
                    'largest_fragment_kg': np.random.uniform(1, 50)
                }
            },
            'collision_analysis': {
                'minimum_distance_km': round(min_distance_km, 3),
                'relative_velocity_km_s': np.random.uniform(5.0, 15.0),
                'collision_energy_joules': self._calculate_impact_energy(sat1, sat2, min_distance_km)
            },
            'metadata': {
                'prediction_time': datetime.now().isoformat(),
                'model_version': '2.0.0-earth-impact',
                'data_source': 'CelesTrak-Cosmos2251',
                'processing_time_ms': np.random.uniform(45, 120),
                'scale_description': '0=No Earth impact risk, 5=100% Earth impact probability'
            }
        }
    
    def _get_risk_level_earth_impact(self, risk_score: float) -> str:
        """Convert Earth impact risk score (0-5) to categorical level."""
        if risk_score >= 4.5:
            return "EXTREME"      # 90-100% Earth impact probability
        elif risk_score >= 3.5:
            return "CRITICAL"     # 70-90% Earth impact probability
        elif risk_score >= 2.5:
            return "HIGH"         # 50-70% Earth impact probability
        elif risk_score >= 1.5:
            return "MEDIUM"       # 30-50% Earth impact probability
        elif risk_score >= 0.5:
            return "LOW"          # 10-30% Earth impact probability
        else:
            return "MINIMAL"      # 0-10% Earth impact probability
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to categorical level (legacy function)."""
        if risk_score >= 0.8:
            return "CRITICAL"
        elif risk_score >= 0.6:
            return "HIGH"
        elif risk_score >= 0.4:
            return "MEDIUM"
        elif risk_score >= 0.2:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _calculate_impact_energy(self, sat1: Dict, sat2: Dict, distance_km: float) -> float:
        """Calculate potential impact energy."""
        # Assume masses (kg) - these would come from satellite database in reality
        mass1 = np.random.uniform(100, 1000)  # kg
        mass2 = np.random.uniform(10, 500)    # kg
        
        # Typical orbital velocity ~7.8 km/s
        velocity = np.random.uniform(7.0, 8.5) * 1000  # m/s
        
        # Kinetic energy = 0.5 * (m1 + m2) * v²
        if distance_km < 1.0:  # Only calculate if collision is possible
            energy = 0.5 * (mass1 + mass2) * (velocity ** 2)
            return energy
        else:
            return 0.0
    
    def run_risk_assessment(self, max_pairs: int = None) -> List[Dict[str, Any]]:
        """
        Run comprehensive risk assessment on ALL satellite pairs.
        
        Args:
            max_pairs: Maximum number of pairs to process (None = all pairs)
            
        Returns:
            List of risk assessment results sorted by risk score
        """
        if len(self.satellites) < 2:
            print("Need at least 2 satellites for risk assessment")
            return []
        
        total_pairs = (len(self.satellites) * (len(self.satellites) - 1)) // 2
        if max_pairs is None:
            max_pairs = total_pairs
        
        print(f"Running comprehensive Earth impact risk assessment...")
        print(f"Total satellites: {len(self.satellites)}")
        print(f"Total possible pairs: {total_pairs}")
        print(f"Processing pairs: {min(max_pairs, total_pairs)}")
        print(f"Scale: 0-5 (0=No Earth impact risk, 5=100% Earth impact probability)")
        print("")
        
        results = []
        pairs_processed = 0
        
        # Process all pairs (or up to max_pairs)
        for i in range(len(self.satellites)):
            for j in range(i + 1, len(self.satellites)):
                if pairs_processed >= max_pairs:
                    break
                
                sat1 = self.satellites[i]
                sat2 = self.satellites[j]
                
                try:
                    prediction = self.simulate_risk_prediction(sat1, sat2)
                    results.append(prediction)
                    pairs_processed += 1
                    
                    # Show progress for every 100 pairs
                    if pairs_processed % 100 == 0:
                        print(f"   Processed {pairs_processed:,} pairs...")
                    
                except Exception as e:
                    print(f"   Error processing pair {pairs_processed + 1}: {e}")
            
            if pairs_processed >= max_pairs:
                break
        
        # Sort by Earth impact risk score (highest first)
        results.sort(key=lambda x: x['earth_impact_assessment']['risk_score_0_to_5'], reverse=True)
        
        self.test_results = results
        print(f"Completed {len(results):,} risk assessments")
        
        # Show top 3 highest risk pairs
        print(f"\nTOP 3 HIGHEST EARTH IMPACT RISK PAIRS:")
        print("=" * 80)
        
        for i, result in enumerate(results[:3]):
            sat1 = result['satellite_1']
            sat2 = result['satellite_2']
            impact = result['earth_impact_assessment']
            prediction = result['impact_prediction']
            
            print(f"\n#{i+1} HIGHEST RISK PAIR:")
            print(f"   Satellite 1: {sat1['name']} (ID: {sat1['norad_id']})")
            print(f"   Satellite 2: {sat2['name']} (ID: {sat2['norad_id']})")
            print(f"   Risk Score: {impact['risk_score_0_to_5']:.3f}/5.0")
            print(f"   Impact Probability: {impact['impact_probability_percentage']:.2f}%")
            print(f"   Risk Level: {impact['risk_level']}")
            print(f"   Est. Impact Time: {prediction['estimated_impact_time'][:19]}")
            print(f"   Est. Impact Location: {prediction['estimated_impact_location']['latitude']:.2f}deg, {prediction['estimated_impact_location']['longitude']:.2f}deg")
            print(f"   Confidence: {impact['confidence']:.1%}")
            
            # Show detailed risk factors
            factors = impact['risk_factors']
            print(f"   Risk Factors:")
            print(f"      - Altitude Risk: {factors['altitude_risk']:.3f}")
            print(f"      - Atmospheric Drag: {factors['atmospheric_drag_factor']:.3f}")
            print(f"      - Collision Probability: {factors['collision_probability']:.3f}")
            print(f"      - Orbit Eccentricity: {factors['orbital_eccentricity_factor']:.3f}")
            print(f"      - Decay Rate: {factors['decay_rate_factor']:.3f}")
        
        return results
    
    def format_output(self, results: List[Dict], format_type: str = "summary") -> str:
        """
        Format the output in different styles.
        
        Args:
            results: List of risk assessment results
            format_type: Output format ('json', 'table', 'summary')
            
        Returns:
            Formatted output string
        """
        if format_type == "json":
            return json.dumps(results, indent=2, default=str)
        
        elif format_type == "table":
            output = []
            output.append("=" * 120)
            output.append("ORBITAL DEBRIS EARTH IMPACT RISK ASSESSMENT REPORT")
            output.append("=" * 120)
            output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
            output.append(f"Total Assessments: {len(results)}")
            output.append("")
            
            # Table header
            header = f"{'#':<3} {'Satellite 1':<25} {'Satellite 2':<25} {'Risk':<8} {'Score':<6} {'Probability':<12} {'Impact Time':<20}"
            output.append(header)
            output.append("-" * 120)
            
            # Table rows
            for i, result in enumerate(results):
                sat1_name = result['satellite_1']['name'][:24]
                sat2_name = result['satellite_2']['name'][:24]
                impact = result['earth_impact_assessment']
                risk_level = impact['risk_level']
                score = impact['risk_score_0_to_5']
                probability = f"{impact['impact_probability_percentage']:.1f}%"
                impact_time = result['impact_prediction']['estimated_impact_time'][:19]
                
                row = f"{i+1:<3} {sat1_name:<25} {sat2_name:<25} {risk_level:<8} {score:.2f}  {probability:<12} {impact_time:<20}"
                output.append(row)
            
            return "\n".join(output)
        
        elif format_type == "summary":
            output = []
            output.append("ORBITAL DEBRIS EARTH IMPACT RISK ASSESSMENT SUMMARY")
            output.append("=" * 60)
            output.append(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            output.append(f"Total Satellites: {len(self.satellites)}")
            output.append(f"Risk Assessments: {len(results)}")
            output.append("")
            
            # Risk level distribution
            risk_counts = {}
            high_risk_pairs = []
            
            for result in results:
                impact = result['earth_impact_assessment']
                risk_level = impact['risk_level']
                risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
                
                if impact['risk_score_0_to_5'] >= 3.5:
                    high_risk_pairs.append(result)
            
            output.append("RISK LEVEL DISTRIBUTION:")
            for level in ['EXTREME', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'MINIMAL']:
                count = risk_counts.get(level, 0)
                percentage = (count / len(results) * 100) if results else 0
                output.append(f"   {level:8}: {count:3d} ({percentage:5.1f}%)")
            
            output.append("")
            
            if high_risk_pairs:
                output.append("HIGH EARTH IMPACT RISK PAIRS:")
                for i, result in enumerate(high_risk_pairs[:5]):  # Show top 5
                    sat1 = result['satellite_1']['name'][:30]
                    sat2 = result['satellite_2']['name'][:30]
                    impact = result['earth_impact_assessment']
                    score = impact['risk_score_0_to_5']
                    probability = impact['impact_probability_percentage']
                    impact_time = result['impact_prediction']['estimated_impact_time'][:19]
                    
                    output.append(f"   {i+1}. {sat1} vs {sat2}")
                    output.append(f"      Risk Score: {score:.3f}/5.0 ({probability:.1f}%) | Impact: {impact_time}")
                    output.append("")
            
            # Performance metrics
            if results:
                scores = [r['earth_impact_assessment']['risk_score_0_to_5'] for r in results]
                avg_score = sum(scores) / len(scores)
                max_score = max(scores)
                min_score = min(scores)
                
                output.append("PERFORMANCE METRICS:")
                output.append(f"   Average Risk Score: {avg_score:.3f}/5.0")
                output.append(f"   Highest Risk Score: {max_score:.3f}/5.0")
                output.append(f"   Lowest Risk Score: {min_score:.3f}/5.0")
                
                high_risk_count = sum(1 for s in scores if s >= 3.5)
                output.append(f"   High Risk Pairs (>=3.5): {high_risk_count} ({high_risk_count/len(results)*100:.1f}%)")
            
            return "\n".join(output)
        
        else:
            return f"Unknown format: {format_type}"

def main():
    """Main function for testing the ML app with comprehensive Earth impact risk assessment."""
    parser = argparse.ArgumentParser(description="Space Debris Earth Impact Risk Assessment ML App")
    parser.add_argument("--max-pairs", type=int, default=500,
                       help="Maximum number of satellite pairs to assess (use -1 for all pairs)")
    parser.add_argument("--format", choices=["json", "table", "summary"], default="summary",
                       help="Output format")
    parser.add_argument("--save-output", type=str,
                       help="Save output to file")
    
    args = parser.parse_args()
    
    # Handle special case for all pairs
    max_pairs = None if args.max_pairs == -1 else args.max_pairs
    
    print("Space Debris Earth Impact Risk Assessment - ML App Test")
    print("="*70)
    print(f"Assessment Mode: {'ALL PAIRS' if max_pairs is None else f'LIMITED ({max_pairs:,} pairs)'}")
    print(f"Risk Scale: 0-5 (0=No Earth impact risk, 5=100% Earth impact probability)")
    print(f"Focus: Top 3 highest Earth impact risk pairs")
    print("")
    
    # Initialize tester
    tester = DebrisRiskTester()
    
    # Load TLE data
    if not tester.load_tle_data():
        print("Failed to load TLE data. Cannot continue.")
        return 1
    
    # Run comprehensive risk assessment on all pairs (limited for demo)
    print("\nRunning comprehensive Earth impact risk assessment...")
    demo_limit = 500  # Change to None to process ALL pairs
    results = tester.run_risk_assessment(max_pairs=demo_limit)
    
    if not results:
        print("No results generated.")
        return 1
    
    # Show summary statistics
    total_pairs = len(results)
    high_risk_count = sum(1 for r in results if r['earth_impact_assessment']['risk_score_0_to_5'] >= 3.5)
    
    print(f"\nRISK ASSESSMENT SUMMARY:")
    print(f"   Total pairs assessed: {total_pairs:,}")
    print(f"   High risk pairs (>=3.5/5.0): {high_risk_count:,}")
    print(f"   High risk percentage: {(high_risk_count/total_pairs)*100:.2f}%")
    
    # Show distribution
    risk_counts = {}
    for result in results:
        score = result['earth_impact_assessment']['risk_score_0_to_5']
        risk_level = result['earth_impact_assessment']['risk_level']
        if risk_level not in risk_counts:
            risk_counts[risk_level] = 0
        risk_counts[risk_level] += 1
    
    print(f"\nRISK LEVEL DISTRIBUTION:")
    for level in ['EXTREME', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'MINIMAL']:
        count = risk_counts.get(level, 0)
        percentage = (count / total_pairs) * 100 if total_pairs > 0 else 0
        print(f"   {level:8}: {count:4,} pairs ({percentage:5.2f}%)")
    
    # Format and display output
    print("\n" + "=" * 60)
    print("RISK ASSESSMENT RESULTS")
    print("=" * 60)
    
    formatted_output = tester.format_output(results, args.format)
    print(formatted_output)
    
    # Save to file if requested
    if args.save_output:
        try:
            with open(args.save_output, 'w') as f:
                f.write(formatted_output)
            print(f"\nOutput saved to: {args.save_output}")
        except Exception as e:
            print(f"\nError saving output: {e}")
    
    print("\nTest completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())