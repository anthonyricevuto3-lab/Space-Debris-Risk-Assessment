#!/usr/bin/env python3
"""
Azure ML scoring script for Space Debris Risk Assessment.
This script handles inference requests for the deployed model.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Any
import logging

# Import our application modules
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.risk_model import DebrisRiskModel
from test_ml_app import DebrisRiskTester

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init():
    """
    Initialize the model for Azure ML inference.
    This function is called when the container is initialized/started.
    """
    global model, tester
    
    try:
        logger.info("Initializing Space Debris Risk Assessment model...")
        
        # Initialize the risk assessment components
        model = DebrisRiskModel()
        tester = DebrisRiskTester()
        
        # Load TLE data
        success = tester.load_tle_data()
        if not success:
            raise Exception("Failed to load TLE data")
        
        logger.info(f"Model initialized successfully with {len(tester.satellites)} satellites")
        
    except Exception as e:
        logger.error(f"Error initializing model: {str(e)}")
        raise

def run(raw_data: str) -> str:
    """
    Run inference on the input data.
    
    Args:
        raw_data: JSON string containing the request data
        
    Returns:
        JSON string containing the prediction results
    """
    try:
        logger.info("Processing inference request...")
        
        # Parse input data
        data = json.loads(raw_data)
        
        # Extract parameters
        max_pairs = data.get('max_pairs', 50)
        format_type = data.get('format', 'summary')
        satellite_ids = data.get('satellite_ids', None)  # Optional: specific satellites
        
        logger.info(f"Running assessment for max_pairs={max_pairs}, format={format_type}")
        
        # Run risk assessment
        if satellite_ids:
            # Filter satellites if specific IDs provided
            filtered_satellites = [s for s in tester.satellites if s['norad_id'] in satellite_ids]
            original_satellites = tester.satellites
            tester.satellites = filtered_satellites
            results = tester.run_risk_assessment(max_pairs=max_pairs)
            tester.satellites = original_satellites
        else:
            results = tester.run_risk_assessment(max_pairs=max_pairs)
        
        # Format output
        if format_type == 'json':
            formatted_output = results
        else:
            formatted_output = tester.format_output(results, format_type)
        
        # Prepare response
        response = {
            'status': 'success',
            'total_assessments': len(results),
            'satellites_loaded': len(tester.satellites),
            'format': format_type,
            'results': formatted_output,
            'metadata': {
                'model_version': '1.0.0',
                'assessment_time': pd.Timestamp.now().isoformat(),
                'max_pairs_processed': max_pairs
            }
        }
        
        # Add top risks summary
        if results:
            top_3 = results[:3]
            response['top_risks'] = [
                {
                    'rank': i + 1,
                    'satellite_1': r['satellite_1']['name'],
                    'satellite_2': r['satellite_2']['name'],
                    'risk_score': r['earth_impact_assessment']['risk_score_0_to_5'],
                    'impact_probability_percent': r['earth_impact_assessment']['impact_probability_percentage'],
                    'risk_level': r['earth_impact_assessment']['risk_level']
                }
                for i, r in enumerate(top_3)
            ]
        
        logger.info(f"Successfully processed {len(results)} assessments")
        return json.dumps(response)
        
    except Exception as e:
        logger.error(f"Error during inference: {str(e)}")
        error_response = {
            'status': 'error',
            'error_message': str(e),
            'error_type': type(e).__name__
        }
        return json.dumps(error_response)

def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Returns:
        Dict containing health status
    """
    try:
        return {
            'status': 'healthy',
            'model_loaded': 'model' in globals() and 'tester' in globals(),
            'satellites_loaded': len(tester.satellites) if 'tester' in globals() else 0,
            'timestamp': pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': pd.Timestamp.now().isoformat()
        }

if __name__ == "__main__":
    # For local testing
    init()
    
    # Test with sample data
    test_data = {
        'max_pairs': 10,
        'format': 'summary'
    }
    
    result = run(json.dumps(test_data))
    print("Test Result:")
    print(result)