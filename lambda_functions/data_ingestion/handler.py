import boto3
import pandas as pd
import io
import json
from datetime import datetime
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.csv_validator import CSVValidator

s3_client = boto3.client('s3', region_name='ap-south-1')

def upload_sales_data(csv_file_path: str, user_id: str) -> dict:
    """
    Validates and stores sales data from CSV upload.
    
    Args:
        csv_file_path: Path to CSV file
        user_id: Authenticated user identifier
        
    Returns:
        UploadResult dict with status, record_count, and validation errors
    """
    start_time = datetime.now()
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        
        # Validate CSV schema
        is_valid, validation_errors = CSVValidator.validate_csv(df)
        if not is_valid:
            return {
                'status': 'error',
                'record_count': 0,
                'validation_errors': validation_errors,
                'upload_id': None,
                'processing_time_ms': int((datetime.now() - start_time).total_seconds() * 1000)
            }
        
        # Parse dates
        df, date_errors = CSVValidator.parse_dates(df)
        if date_errors:
            return {
                'status': 'error',
                'record_count': 0,
                'validation_errors': date_errors,
                'upload_id': None,
                'processing_time_ms': int((datetime.now() - start_time).total_seconds() * 1000)
            }
        
        # Deduplicate
        original_count = len(df)
        df = CSVValidator.deduplicate(df)
        deduplicated_count = original_count - len(df)
        
        # Add user_id and created_at
        df['user_id'] = user_id
        df['created_at'] = datetime.now().isoformat()
        
        # Generate upload ID
        upload_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store raw CSV to S3
        raw_bucket = 'retailiq-raw-data-varun'
        raw_key = f"{user_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}/sales_data.csv"
        
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        s3_client.put_object(
            Bucket=raw_bucket,
            Key=raw_key,
            Body=csv_buffer.getvalue()
        )
        
        # Store processed data as Parquet
        processed_bucket = 'retailiq-processed-data-varun'
        processed_key = f"{user_id}/sales_data.parquet"
        
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        s3_client.put_object(
            Bucket=processed_bucket,
            Key=processed_key,
            Body=parquet_buffer.getvalue()
        )
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return {
            'status': 'success',
            'record_count': len(df),
            'validation_errors': [],
            'upload_id': upload_id,
            'processing_time_ms': processing_time,
            'deduplicated_records': deduplicated_count
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'record_count': 0,
            'validation_errors': [str(e)],
            'upload_id': None,
            'processing_time_ms': int((datetime.now() - start_time).total_seconds() * 1000)
        }

# For testing
if __name__ == '__main__':
    # Test with sample data
    result = upload_sales_data('data/sample_sales.csv', 'test_user')
    print(json.dumps(result, indent=2))
