import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
import dateutil.parser as date_parser

class CSVValidator:
    """Validates CSV files for RetailIQ data ingestion"""
    
    REQUIRED_COLUMNS = ['product_id', 'product_name', 'quantity', 'price', 'date', 'region']
    
    @staticmethod
    def validate_csv(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validates CSV schema and data types.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for missing columns
        missing_cols = set(CSVValidator.REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return False, errors
        
        # Validate data types
        if not pd.api.types.is_numeric_dtype(df['quantity']):
            errors.append("Invalid data type in column 'quantity': expected numeric")
        
        if not pd.api.types.is_numeric_dtype(df['price']):
            errors.append("Invalid data type in column 'price': expected numeric")
        
        # Validate positive values
        if (df['quantity'] <= 0).any():
            errors.append("Column 'quantity' contains non-positive values")
        
        if (df['price'] <= 0).any():
            errors.append("Column 'price' contains non-positive values")
        
        # Validate string columns are not empty
        if df['product_id'].isna().any() or (df['product_id'] == '').any():
            errors.append("Column 'product_id' contains empty values")
        
        if df['product_name'].isna().any() or (df['product_name'] == '').any():
            errors.append("Column 'product_name' contains empty values")
        
        if df['region'].isna().any() or (df['region'] == '').any():
            errors.append("Column 'region' contains empty values")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def parse_dates(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Parses dates in multiple formats (YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY).
        
        Returns:
            Tuple of (dataframe_with_parsed_dates, list_of_errors)
        """
        errors = []
        parsed_dates = []
        
        for idx, date_str in enumerate(df['date']):
            try:
                # Try parsing with dateutil (handles multiple formats)
                parsed_date = date_parser.parse(str(date_str))
                parsed_dates.append(parsed_date)
            except Exception as e:
                errors.append(f"Invalid date format in row {idx + 1}: {date_str}")
                parsed_dates.append(None)
        
        df['date'] = parsed_dates
        return df, errors
    
    @staticmethod
    def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
        """
        Deduplicates records based on (product_id, date) composite key.
        Keeps the first occurrence.
        """
        return df.drop_duplicates(subset=['product_id', 'date'], keep='first')
