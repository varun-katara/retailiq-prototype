from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
from lambda_functions.copilot.handler import process_copilot_query
import sys
import os
import tempfile

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lambda_functions.data_ingestion.handler import upload_sales_data
from lambda_functions.forecasting.handler import generate_forecast
from lambda_functions.inventory.handler import get_reorder_recommendations

app = FastAPI(
    title="RetailIQ API",
    description="AI-powered demand forecasting and inventory optimization for Bharat retailers",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ForecastRequest(BaseModel):
    product_id: str
    horizon: int = 30
    region: Optional[str] = None

class InventoryRequest(BaseModel):
    current_inventory: Dict[str, int]
    lead_time_days: int = 7

class CopilotRequest(BaseModel):
    query: str
    conversation_history: Optional[List[Dict]] = []

# Simple API key validation (for hackathon - use proper auth in production)
def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key missing")
    # For hackathon, accept any non-empty key
    # In production, validate against database
    return x_api_key

@app.get("/")
def root():
    """API health check"""
    return {
        "status": "healthy",
        "service": "RetailIQ API",
        "version": "1.0.0"
    }

@app.post("/data/upload")
async def upload_data(
    file: UploadFile = File(...),
    user_id: str = "demo_user",
    api_key: str = Header(None, alias="X-API-Key")
):
    """
    Upload sales data CSV file.
    
    - **file**: CSV file with columns: product_id, product_name, quantity, price, date, region
    - **user_id**: User identifier (default: demo_user)
    """
    verify_api_key(api_key)
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Process the file
        result = upload_sales_data(tmp_file_path, user_id)
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result)
        
        return result
    except Exception as e:
        # Clean up temp file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/forecast")
def create_forecast(
    request: ForecastRequest,
    user_id: str = "demo_user",
    api_key: str = Header(None, alias="X-API-Key")
):
    """
    Generate demand forecast for a product.
    
    - **product_id**: Product identifier
    - **horizon**: Forecast period in days (7, 14, or 30)
    - **region**: Optional region name for regional factors
    """
    verify_api_key(api_key)
    
    if request.horizon not in [7, 14, 30]:
        raise HTTPException(
            status_code=400,
            detail="Invalid forecast horizon. Must be 7, 14, or 30 days."
        )
    
    result = generate_forecast(
        user_id,
        request.product_id,
        request.horizon,
        request.region
    )
    
    if result.get('status') == 'error':
        raise HTTPException(status_code=404, detail=result)
    
    return result

@app.post("/inventory/recommendations")
def inventory_recommendations(
    request: InventoryRequest,
    user_id: str = "demo_user",
    api_key: str = Header(None, alias="X-API-Key")
):
    """
    Get inventory reorder recommendations.
    
    - **current_inventory**: Dict mapping product_id to current stock level
    - **lead_time_days**: Supplier lead time in days (default: 7)
    """
    verify_api_key(api_key)
    
    result = get_reorder_recommendations(
        user_id,
        request.current_inventory,
        request.lead_time_days
    )
    
    if result.get('status') == 'error':
        raise HTTPException(status_code=400, detail=result)
    
    return result

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "RetailIQ"}

@app.post("/copilot/chat")
def copilot_chat(
    request: CopilotRequest,
    user_id: str = "demo_user",
    api_key: str = Header(None, alias="X-API-Key")
):
    """
    AI Copilot chat endpoint.
    
    - **query**: Natural language question
    - **conversation_history**: Optional previous messages
    """
    verify_api_key(api_key)
    
    result = process_copilot_query(
        user_id,
        request.query,
        request.conversation_history
    )
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
