"""
TLE Data Loader

This module handles fetching and parsing Two-Line Element (TLE) data
from various sources including CelesTrak and Space-Track.
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TLEData:
    """Data class for TLE information."""
    catalog_id: str
    name: str
    line1: str
    line2: str
    epoch: datetime
    source: str
    
    def to_dict(self) -> Dict:
        """Convert TLE data to dictionary."""
        return {
            'catalog_id': self.catalog_id,
            'name': self.name,
            'line1': self.line1,
            'line2': self.line2,
            'epoch': self.epoch.isoformat(),
            'source': self.source
        }

class TLELoader:
    """
    TLE data loader with support for multiple data sources.
    
    Supports fetching TLE data from:
    - CelesTrak (public, no authentication required)
    - Space-Track (requires registration and authentication)
    - Local cache for offline operation
    """
    
    def __init__(self, cache_duration_hours: int = 6):
        """
        Initialize TLE loader.
        
        Args:
            cache_duration_hours: How long to cache TLE data before refreshing
        """
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.cache = {}
        self.celestrak_base_url = "https://celestrak.org/NORAD/elements/gp.php"
        self.spacetrack_base_url = "https://www.space-track.org"
        
    def fetch_tle(self, catalog_id: str, source: str = "celestrak") -> TLEData:
        """
        Fetch TLE data for a specific satellite.
        
        Args:
            catalog_id: NORAD catalog ID
            source: Data source ('celestrak' or 'spacetrack')
            
        Returns:
            TLEData object
        """
        # Check cache first
        cache_key = f"{source}_{catalog_id}"
        if cache_key in self.cache:
            cached_data, cache_time = self.cache[cache_key]
            if datetime.utcnow() - cache_time < self.cache_duration:
                logger.debug(f"Using cached TLE for {catalog_id}")
                return cached_data
        
        # Fetch fresh data
        if source == "celestrak":
            tle_data = self._fetch_from_celestrak(catalog_id)
        elif source == "spacetrack":
            tle_data = self._fetch_from_spacetrack(catalog_id)
        else:
            raise ValueError(f"Unsupported source: {source}")
        
        # Cache the result
        self.cache[cache_key] = (tle_data, datetime.utcnow())
        
        return tle_data
    
    def fetch_tle_batch(self, catalog_ids: List[str], source: str = "celestrak") -> List[TLEData]:
        """
        Fetch TLE data for multiple satellites.
        
        Args:
            catalog_ids: List of NORAD catalog IDs
            source: Data source
            
        Returns:
            List of TLEData objects
        """
        results = []
        
        for catalog_id in catalog_ids:
            try:
                tle_data = self.fetch_tle(catalog_id, source)
                results.append(tle_data)
                
                # Add small delay to be respectful to the API
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed to fetch TLE for {catalog_id}: {e}")
        
        return results
    
    def fetch_debris_group(self, group_name: str = "cosmos-2251-debris") -> List[TLEData]:
        """
        Fetch TLE data for a specific debris group.
        
        Args:
            group_name: Name of the debris group (e.g., 'cosmos-2251-debris')
            
        Returns:
            List of TLEData objects
        """
        url = f"{self.celestrak_base_url}?GROUP={group_name}&FORMAT=tle"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            return self._parse_tle_text(response.text, source="celestrak_group")
            
        except Exception as e:
            logger.error(f"Failed to fetch debris group {group_name}: {e}")
            raise
    
    def _fetch_from_celestrak(self, catalog_id: str) -> TLEData:
        """Fetch TLE from CelesTrak by catalog ID."""
        url = f"{self.celestrak_base_url}?CATNR={catalog_id}&FORMAT=tle"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            tle_objects = self._parse_tle_text(response.text, source="celestrak")
            
            if not tle_objects:
                raise ValueError(f"No TLE data found for catalog ID {catalog_id}")
            
            # Return the first (and should be only) TLE object
            return tle_objects[0]
            
        except Exception as e:
            logger.error(f"Failed to fetch TLE from CelesTrak for {catalog_id}: {e}")
            raise
    
    def _fetch_from_spacetrack(self, catalog_id: str) -> TLEData:
        """
        Fetch TLE from Space-Track.org (requires authentication).
        
        Note: This is a placeholder implementation. Full implementation
        would require Space-Track authentication setup.
        """
        # This would require implementing Space-Track authentication
        # and API calls. For now, fall back to CelesTrak
        logger.warning("Space-Track integration not implemented, falling back to CelesTrak")
        return self._fetch_from_celestrak(catalog_id)
    
    def _parse_tle_text(self, tle_text: str, source: str) -> List[TLEData]:
        """
        Parse TLE text format into TLEData objects.
        
        Args:
            tle_text: Raw TLE text (3-line format)
            source: Source identifier
            
        Returns:
            List of parsed TLEData objects
        """
        lines = tle_text.strip().split('\n')
        tle_objects = []
        
        # Process TLE data in groups of 3 lines (name, line1, line2)
        for i in range(0, len(lines), 3):
            if i + 2 >= len(lines):
                break
                
            name = lines[i].strip()
            line1 = lines[i + 1].strip()
            line2 = lines[i + 2].strip()
            
            # Validate TLE format
            if not self._validate_tle_lines(line1, line2):
                logger.warning(f"Invalid TLE format for {name}")
                continue
            
            # Extract catalog ID from line1
            catalog_id = line1[2:7].strip()
            
            # Extract epoch from line1
            epoch = self._parse_tle_epoch(line1)
            
            tle_data = TLEData(
                catalog_id=catalog_id,
                name=name,
                line1=line1,
                line2=line2,
                epoch=epoch,
                source=source
            )
            
            tle_objects.append(tle_data)
        
        return tle_objects
    
    def _validate_tle_lines(self, line1: str, line2: str) -> bool:
        """
        Validate TLE line format.
        
        Args:
            line1: First line of TLE
            line2: Second line of TLE
            
        Returns:
            True if valid, False otherwise
        """
        # Check line length
        if len(line1) != 69 or len(line2) != 69:
            return False
        
        # Check line identifiers
        if line1[0] != '1' or line2[0] != '2':
            return False
        
        # Check that catalog numbers match
        cat_num1 = line1[2:7]
        cat_num2 = line2[2:7]
        if cat_num1 != cat_num2:
            return False
        
        return True
    
    def _parse_tle_epoch(self, line1: str) -> datetime:
        """
        Parse epoch from TLE line 1.
        
        Args:
            line1: First line of TLE
            
        Returns:
            Epoch as datetime object
        """
        try:
            # Extract epoch from positions 18-32 in line1
            epoch_str = line1[18:32]
            
            # Parse year (2-digit)
            year_2digit = int(epoch_str[0:2])
            year = 2000 + year_2digit if year_2digit < 57 else 1900 + year_2digit
            
            # Parse day of year (with fractional part)
            day_of_year = float(epoch_str[2:])
            
            # Convert to datetime
            epoch = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
            
            return epoch
            
        except Exception as e:
            logger.error(f"Failed to parse TLE epoch: {e}")
            return datetime.utcnow()  # Fallback to current time
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        total_entries = len(self.cache)
        valid_entries = 0
        current_time = datetime.utcnow()
        
        for _, (_, cache_time) in self.cache.items():
            if current_time - cache_time < self.cache_duration:
                valid_entries += 1
        
        return {
            'total_cached': total_entries,
            'valid_cached': valid_entries,
            'cache_hit_rate': valid_entries / total_entries if total_entries > 0 else 0,
            'cache_duration_hours': self.cache_duration.total_seconds() / 3600
        }
    
    def clear_cache(self) -> None:
        """Clear the TLE cache."""
        self.cache.clear()
        logger.info("TLE cache cleared")