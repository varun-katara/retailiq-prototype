import boto3
import json
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.inventory_optimizer import InventoryOptimizer

s3_client = boto3.client('s3', region_name='ap-south-1')

def get_reorder_recommendations(
    user_id: str,
    current_inventory: dict,
    lead_time_days: int = 7
) -> dict:
    """
    Generates inventory reorder recommendations.
    
    Args:
        user_id: User identifier
        current_inventory: Dict mapping product_id to current stock level
        lead_time_days: Supplier lead time
        
    Returns:
        Dict with recommendations list
    """
    try:
        # Load forecast data from S3
        bucket = 'retailiq-processed-data-varun'
        forecast_data = {}
        
        for product_id in current_inventory.keys():
            try:
                # Try to load forecast for this product
                forecast_key = f"{user_id}/forecasts/{product_id}/forecast_7d.json"
                response = s3_client.get_object(Bucket=bucket, Key=forecast_key)
                forecast = json.loads(response['Body'].read())
                forecast_data[product_id] = forecast
            except:
                # Skip if forecast not found
                continue
        
        if not forecast_data:
            return {
                'status': 'error',
                'error': 'No forecast data found. Please generate forecasts first.',
                'recommendations': []
            }
        
        # Generate recommendations
        recommendations = InventoryOptimizer.generate_recommendations(
            current_inventory,
            forecast_data,
            lead_time_days
        )
        
        return {
            'status': 'success',
            'recommendations': recommendations,
            'total_products_analyzed': len(current_inventory),
            'products_needing_reorder': len(recommendations)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'recommendations': []
        }

# For testing
if __name__ == '__main__':
    # Sample current inventory
    test_inventory = {
        'P001': 20,  # Low stock
        'P002': 50,  # Medium stock
        'P003': 10,  # Very low stock
        'P004': 100  # High stock
    }
    
    result = get_reorder_recommendations('test_user', test_inventory)
    print(json.dumps(result, indent=2))
