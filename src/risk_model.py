"""
ML Model Logic for Debris Risk Assessment

This module contains the machine learning models and logic for predicting
orbital debris collision risks and trajectory propagation.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import os
import logging

# Optional ML dependencies
try:
    import pandas as pd
    import joblib
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_absolute_error, r2_score
    ML_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ML libraries not available: {e}")
    ML_AVAILABLE = False

# MLflow integration
try:
    import mlflow
    import mlflow.sklearn
    from mlflow import log_metric, log_param, log_artifacts
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

from .utils import (
    calculate_distance, 
    propagate_orbit, 
    orbital_elements_to_features,
    time_to_closest_approach
)
from .tle_loader import TLELoader

logger = logging.getLogger(__name__)

# Set MLflow tracking URI if available
if MLFLOW_AVAILABLE:
    MLFLOW_TRACKING_URI = "azureml://westus3.api.azureml.ms/mlflow/v1.0/subscriptions/8d1e82fa-4fb3-48ee-99a2-b3f5784287a2/resourceGroups/Space-Debris-Risk-Assessment-RG/providers/Microsoft.MachineLearningServices/workspaces/Space-Debris-Risk-Assessment"
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    logger.info(f"MLflow tracking URI set to: {MLFLOW_TRACKING_URI}")
else:
    logger.warning("MLflow not available. Model tracking will be disabled.")

class DebrisRiskModel:
    """
    Machine Learning model for predicting orbital debris collision risks.
    
    This class implements various ML algorithms to assess collision probability
    based on orbital parameters, historical data, and propagated trajectories.
    """
    
    def __init__(self, model_type: str = "random_forest"):
        """
        Initialize the debris risk model.
        
        Args:
            model_type: Type of ML model to use ('random_forest', 'gradient_boost', 'neural_net')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.feature_columns = []
        self.is_trained = False
        
        if not ML_AVAILABLE:
            logger.warning("ML libraries not available, using simple fallback calculations")
            return
        
        # Initialize the specified model
        self.scaler = StandardScaler()
        if model_type == "random_forest":
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=20,
                min_samples_split=5,
                random_state=42
            )
        elif model_type == "gradient_boost":
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def prepare_features(self, satellite_data: Dict, target_data: Dict) -> np.ndarray:
        """
        Extract and prepare features from satellite orbital data.
        
        Args:
            satellite_data: Dictionary containing satellite orbital elements and TLE
            target_data: Dictionary containing target satellite data
            
        Returns:
            Feature array for ML model
        """
        features = []
        
        # Extract orbital elements
        sat_elements = orbital_elements_to_features(satellite_data['tle'])
        target_elements = orbital_elements_to_features(target_data['tle'])
        
        # Basic orbital parameters
        features.extend([
            sat_elements['semi_major_axis'],
            sat_elements['eccentricity'],
            sat_elements['inclination'],
            sat_elements['raan'],
            sat_elements['arg_perigee'],
            sat_elements['mean_anomaly'],
            sat_elements['mean_motion']
        ])
        
        # Target orbital parameters
        features.extend([
            target_elements['semi_major_axis'],
            target_elements['eccentricity'],
            target_elements['inclination'],
            target_elements['raan'],
            target_elements['arg_perigee'],
            target_elements['mean_anomaly'],
            target_elements['mean_motion']
        ])
        
        # Relative orbital characteristics
        features.extend([
            abs(sat_elements['semi_major_axis'] - target_elements['semi_major_axis']),
            abs(sat_elements['inclination'] - target_elements['inclination']),
            abs(sat_elements['raan'] - target_elements['raan']),
            abs(sat_elements['mean_motion'] - target_elements['mean_motion'])
        ])
        
        # Current distance (if positions available)
        if 'position' in satellite_data and 'position' in target_data:
            current_distance = calculate_distance(
                satellite_data['position'],
                target_data['position']
            )
            features.append(current_distance)
        else:
            features.append(0.0)  # Default value
        
        # Time-based features
        current_time = datetime.utcnow()
        features.extend([
            current_time.hour,  # Hour of day
            current_time.timetuple().tm_yday,  # Day of year
            current_time.timestamp() % (24 * 3600)  # Seconds since midnight
        ])
        
        return np.array(features).reshape(1, -1)
    
    def train(self, training_data: List[Dict], validation_split: float = 0.2) -> Dict[str, float]:
        """
        Train the risk assessment model.
        
        Args:
            training_data: List of training examples with features and risk labels
            validation_split: Fraction of data to use for validation
            
        Returns:
            Training metrics dictionary
        """
        logger.info(f"Training {self.model_type} model with {len(training_data)} examples")
        
        # Start MLflow run if available
        if MLFLOW_AVAILABLE:
            mlflow.start_run(run_name=f"debris-risk-{self.model_type}-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            
            # Log parameters
            mlflow.log_param("model_type", self.model_type)
            mlflow.log_param("validation_split", validation_split)
            mlflow.log_param("n_training_examples", len(training_data))
            
            # Log model hyperparameters
            if hasattr(self.model, 'get_params'):
                for param, value in self.model.get_params().items():
                    mlflow.log_param(f"model_{param}", value)
        
        # Prepare feature matrix and target vector
        X = []
        y = []
        
        for example in training_data:
            features = self.prepare_features(
                example['satellite'],
                example['target']
            )
            X.append(features.flatten())
            y.append(example['risk_score'])
        
        X = np.array(X)
        y = np.array(y)
        
        # Store feature columns for later use
        self.feature_columns = [f"feature_{i}" for i in range(X.shape[1])]
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_pred = self.model.predict(X_train_scaled)
        val_pred = self.model.predict(X_val_scaled)
        
        metrics = {
            'train_mae': mean_absolute_error(y_train, train_pred),
            'val_mae': mean_absolute_error(y_val, val_pred),
            'train_r2': r2_score(y_train, train_pred),
            'val_r2': r2_score(y_val, val_pred),
            'n_features': X.shape[1],
            'n_samples': X.shape[0]
        }
        
        # Log metrics to MLflow
        if MLFLOW_AVAILABLE:
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # Log model
            mlflow.sklearn.log_model(
                sk_model=self.model,
                artifact_path="model",
                registered_model_name="orbital-debris-risk-model"
            )
            
            # Log scaler
            joblib.dump(self.scaler, "scaler.pkl")
            mlflow.log_artifact("scaler.pkl")
            
            # End MLflow run
            mlflow.end_run()
        
        self.is_trained = True
        logger.info(f"Training completed. Validation MAE: {metrics['val_mae']:.4f}, R²: {metrics['val_r2']:.4f}")
        
        return metrics
    
    def predict_risk(self, satellite: Dict, target: Dict, horizon_hours: int = 24) -> float:
        """
        Predict collision risk for a satellite relative to a target.
        
        Args:
            satellite: Satellite data including TLE
            target: Target satellite data
            horizon_hours: Prediction time horizon in hours
            
        Returns:
            Risk score between 0 and 1
        """
        # If ML libraries not available, use simple heuristic calculation
        if not ML_AVAILABLE:
            return self._simple_risk_calculation(satellite, target)
            
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Prepare features
        features = self.prepare_features(satellite, target)
        features_scaled = self.scaler.transform(features)
        
        # Get base risk prediction
        base_risk = self.model.predict(features_scaled)[0]
        
        # Apply temporal propagation adjustments
        risk_score = self._adjust_risk_for_horizon(
            base_risk, satellite, target, horizon_hours
        )
        
        # Ensure risk score is bounded between 0 and 1
        return np.clip(risk_score, 0.0, 1.0)
        
    def _simple_risk_calculation(self, satellite: Dict, target: Dict) -> float:
        """
        Simple fallback risk calculation when ML libraries are not available.
        
        Args:
            satellite: Satellite data dictionary
            target: Target satellite data dictionary
            
        Returns:
            Risk score between 0 and 1
        """
        # Extract basic orbital parameters with defaults
        sat_alt = satellite.get('altitude', 400)
        sat_ecc = satellite.get('eccentricity', 0.01)
        sat_inc = satellite.get('inclination', 51.6)
        
        tgt_alt = target.get('altitude', 410)
        tgt_ecc = target.get('eccentricity', 0.01)
        tgt_inc = target.get('inclination', 51.6)
        
        # Calculate altitude difference risk (closer altitudes = higher risk)
        alt_diff = abs(sat_alt - tgt_alt)
        alt_risk = max(0, 1 - alt_diff / 100)  # Risk decreases with altitude separation
        
        # Calculate inclination difference risk (similar inclinations = higher risk)
        inc_diff = abs(sat_inc - tgt_inc)
        inc_risk = max(0, 1 - inc_diff / 30)  # Risk decreases with inclination separation
        
        # Eccentricity contribution (higher eccentricity = more unpredictable = higher risk)
        ecc_risk = (sat_ecc + tgt_ecc) / 2
        
        # Low altitude risk (atmosphere drag makes orbits less predictable)
        low_alt_risk = max(0, (500 - min(sat_alt, tgt_alt)) / 500) if min(sat_alt, tgt_alt) < 500 else 0
        
        # Combine factors with weights
        combined_risk = (
            0.4 * alt_risk +
            0.3 * inc_risk +
            0.2 * ecc_risk +
            0.1 * low_alt_risk
        )
        
        # Ensure result is between 0 and 1
        return max(0.0, min(1.0, combined_risk))
    
    def _adjust_risk_for_horizon(self, base_risk: float, satellite: Dict, 
                                target: Dict, horizon_hours: int) -> float:
        """
        Adjust risk score based on prediction horizon and orbital dynamics.
        
        Args:
            base_risk: Base risk score from ML model
            satellite: Satellite data
            target: Target data
            horizon_hours: Prediction horizon
            
        Returns:
            Adjusted risk score
        """
        try:
            # Calculate time to closest approach
            tta = time_to_closest_approach(satellite['tle'], target['tle'])
            
            # Adjust risk based on time horizon
            if tta <= horizon_hours:
                # Increase risk if closest approach is within horizon
                temporal_factor = 1.5 * (1 - tta / horizon_hours)
            else:
                # Decrease risk if closest approach is beyond horizon
                temporal_factor = 0.8 * (horizon_hours / tta)
            
            return base_risk * temporal_factor
            
        except Exception as e:
            logger.warning(f"Could not calculate temporal adjustment: {e}")
            return base_risk
    
    def save(self, filepath: str) -> None:
        """Save the trained model to disk."""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'model_type': self.model_type,
            'feature_columns': self.feature_columns,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'DebrisRiskModel':
        """Load a trained model from disk."""
        model_data = joblib.load(filepath)
        
        instance = cls(model_data['model_type'])
        instance.model = model_data['model']
        instance.scaler = model_data['scaler']
        instance.feature_columns = model_data['feature_columns']
        instance.is_trained = model_data['is_trained']
        
        logger.info(f"Model loaded from {filepath}")
        return instance
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores from the trained model."""
        if not self.is_trained:
            raise ValueError("Model must be trained to get feature importance")
        
        if hasattr(self.model, 'feature_importances_'):
            importance_dict = {}
            for i, importance in enumerate(self.model.feature_importances_):
                feature_name = self.feature_columns[i] if i < len(self.feature_columns) else f"feature_{i}"
                importance_dict[feature_name] = float(importance)
            return importance_dict
        else:
            logger.warning("Model does not support feature importance")
            return {}


class EnsembleRiskModel:
    """
    Ensemble model combining multiple risk assessment approaches.
    """
    
    def __init__(self):
        self.models = []
        self.weights = []
        
    def add_model(self, model: DebrisRiskModel, weight: float = 1.0):
        """Add a model to the ensemble."""
        self.models.append(model)
        self.weights.append(weight)
        
    def predict_risk(self, satellite: Dict, target: Dict, horizon_hours: int = 24) -> float:
        """Predict risk using ensemble of models."""
        if not self.models:
            raise ValueError("No models in ensemble")
        
        predictions = []
        total_weight = 0
        
        for model, weight in zip(self.models, self.weights):
            try:
                pred = model.predict_risk(satellite, target, horizon_hours)
                predictions.append(pred * weight)
                total_weight += weight
            except Exception as e:
                logger.warning(f"Model prediction failed: {e}")
        
        if not predictions:
            raise ValueError("All models failed to predict")
        
        return sum(predictions) / total_weight