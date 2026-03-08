import boto3
import pandas as pd
import json
import sys
import os
from io import BytesIO

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.forecasting import DemandForecaster

s3_client = boto3.client('s3', region_name='ap-south-1')

def generate_forecast(user_id: str, product_id: str, horizon: int = 30, region: str = None) -> dict:
    """
    Generates demand forecast for a product.
    
    Args:
        user_id: User identifier
        product_id: Product to forecast
        horizon: Forecast period in days (7, 14, or 30)
        region: Region name
        
    Returns:
        Forecast result dict
    """
    try:
        # Load processed sales data from S3
        bucket = 'retailiq-processed-data-varun'
        key = f"{user_id}/sales_data.parquet"
        
        response = s3_client.get_object(Bucket=bucket, Key=key)
        df = pd.read_parquet(BytesIO(response['Body'].read()))
        
        # Generate forecast
        result = DemandForecaster.generate_forecast(df, product_id, horizon, region)
        
        # Store forecast results to S3
        if result['status'] == 'success':
            forecast_key = f"{user_id}/forecasts/{product_id}/forecast_{horizon}d.json"
            s3_client.put_object(
                Bucket=bucket,
                Key=forecast_key,
                Body=json.dumps(result, default=str)
            )
        
        return result
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

# For testing
if __name__ == '__main__':
    result = generate_forecast('test_user', 'P001', horizon=7)
    print(json.dumps(result, indent=2, default=str))
