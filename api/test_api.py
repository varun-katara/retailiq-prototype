import requests
import json
import os

BASE_URL = "http://localhost:8000"
API_KEY = "test-key-123"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())

def test_upload():
    """Test data upload"""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(BASE_DIR, 'data', 'sample_sales.csv')

    with open(file_path, 'rb') as f:
        files = {'file': f}
        headers = {'X-API-Key': API_KEY}
        response = requests.post(
            f"{BASE_URL}/data/upload",
            files=files,
            headers=headers
        )
        print("Upload Result:", json.dumps(response.json(), indent=2))

def test_forecast():
    """Test forecast generation"""
    headers = {'X-API-Key': API_KEY, 'Content-Type': 'application/json'}
    data = {
        'product_id': 'P001',
        'horizon': 7,
        'region': 'Maharashtra'
    }
    response = requests.post(
        f"{BASE_URL}/forecast",
        json=data,
        headers=headers
    )
    print("Forecast Result:", json.dumps(response.json(), indent=2, default=str))

def test_inventory():
    """Test inventory recommendations"""
    headers = {'X-API-Key': API_KEY, 'Content-Type': 'application/json'}
    data = {
        'current_inventory': {
            'P001': 20,
            'P002': 50,
            'P003': 10
        },
        'lead_time_days': 7
    }
    response = requests.post(
        f"{BASE_URL}/inventory/recommendations",
        json=data,
        headers=headers
    )
    print("Inventory Recommendations:", json.dumps(response.json(), indent=2))

if __name__ == '__main__':
    print("Testing RetailIQ API...\n")
    test_health()
    print("\n" + "="*50 + "\n")
    test_upload()
    print("\n" + "="*50 + "\n")
    test_forecast()
    print("\n" + "="*50 + "\n")
    test_inventory()
