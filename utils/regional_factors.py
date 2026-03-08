from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd

class RegionalFactors:
    """Manages festival dates and regional factors for Bharat"""
    
    # Major festivals in India (approximate dates - adjust yearly)
    FESTIVALS_2024 = {
        'Diwali': datetime(2024, 11, 1),
        'Holi': datetime(2024, 3, 25),
        'Eid': datetime(2024, 4, 11),
        'Pongal': datetime(2024, 1, 15),
        'Durga Puja': datetime(2024, 10, 10),
        'Christmas': datetime(2024, 12, 25),
        'New Year': datetime(2024, 1, 1),
        'Raksha Bandhan': datetime(2024, 8, 19),
        'Ganesh Chaturthi': datetime(2024, 9, 7),
        'Onam': datetime(2024, 9, 15)
    }
    
    @staticmethod
    def get_festival_dates(start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Returns festival dates within the specified date range.
        
        Returns:
            DataFrame with columns: holiday, ds (date), lower_window, upper_window
        """
        festivals = []
        
        for festival_name, festival_date in RegionalFactors.FESTIVALS_2024.items():
            if start_date <= festival_date <= end_date:
                festivals.append({
                    'holiday': festival_name,
                    'ds': festival_date,
                    'lower_window': -2,  # 2 days before
                    'upper_window': 2    # 2 days after
                })
        
        return pd.DataFrame(festivals) if festivals else pd.DataFrame(columns=['holiday', 'ds', 'lower_window', 'upper_window'])
    
    @staticmethod
    def get_regional_multipliers(region: str) -> Dict[str, float]:
        """
        Returns seasonal multipliers for different regions.
        
        Args:
            region: Region/state name
            
        Returns:
            Dict with seasonal multipliers
        """
        # Regional patterns (simplified for hackathon)
        regional_patterns = {
            'Maharashtra': {'summer': 1.2, 'monsoon': 0.9, 'winter': 1.1},
            'Karnataka': {'summer': 1.3, 'monsoon': 0.8, 'winter': 1.0},
            'Tamil Nadu': {'summer': 1.4, 'monsoon': 0.85, 'winter': 1.05},
            'Delhi': {'summer': 1.1, 'monsoon': 0.95, 'winter': 1.3},
            'West Bengal': {'summer': 1.0, 'monsoon': 0.9, 'winter': 1.2}
        }
        
        return regional_patterns.get(region, {'summer': 1.0, 'monsoon': 1.0, 'winter': 1.0})
