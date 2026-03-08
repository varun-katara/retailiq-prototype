# 🛒 RetailIQ - AI Copilot for Demand Forecasting

AI-powered demand forecasting and inventory optimization platform for small retailers in Bharat.

## Features

- 📤 **CSV Data Upload** - Easy sales data ingestion
- 📈 **Demand Forecasting** - 7/14/30 day predictions with Prophet ML
- 📦 **Inventory Optimization** - Automated reorder recommendations
- 🎯 **Stockout Risk Scoring** - Prioritized alerts (0-100 scale)
- 🤖 **AI Copilot** - Natural language Q&A with Amazon Bedrock
- 🇮🇳 **Bharat-Specific** - Festival dates, regional factors, ₹ formatting

## Tech Stack

- **Backend**: Python, FastAPI, boto3
- **ML**: Prophet, scikit-learn, pandas, numpy
- **AI**: Amazon Bedrock (Claude 3 Sonnet)
- **AWS**: Lambda, S3, DynamoDB, API Gateway
- **Frontend**: HTML/CSS/JavaScript, Bootstrap, Chart.js

## Quick Start

---

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 2. Configure AWS
**aws configure**
1. Enter your AWS credentials
2. Region: ap-south-1

---

### 3. Setup AWS Resources
```bash
python config/aws_setup.py
```

---

### 4. Run API Server4. Run API Server
```bash
python -m api.main
```

---

### 5. Run Frontend
- Open the terminal:

cd frontend
python -m http.server 3000

---

### 6. Open Browser
http://localhost:3000

---

## Project Structure

retailiq-prototype/
├── api/                    # FastAPI application
├── lambda_functions/       # AWS Lambda handlers
│   ├── data_ingestion/
│   ├── forecasting/
│   ├── inventory/
│   └── copilot/
├── utils/                  # Shared utilities
│   ├── csv_validator.py
│   ├── forecasting.py
│   ├── inventory_optimizer.py
│   ├── regional_factors.py
│   └── copilot.py
├── config/                 # AWS setup scripts
├── frontend/               # Web dashboard
├── data/                   # Sample data
└── tests/                  # Test files


## API Endpoints

POST /data/upload - Upload sales CSV
POST /forecast - Generate demand forecast
POST /inventory/recommendations - Get reorder recommendations
POST /copilot/chat - AI Copilot Q&A
GET /health - Health check

## Demo Credentials

User ID: demo_user
API Key: test-key-123

## AWS Resources Created

**S3 Buckets:**
- retailiq-raw-data-varun
- retailiq-processed-data-varun
- retailiq-model-artifacts-varun

**DynamoDB Tables:**
- retailiq-metadata
- retailiq-model-registry

## Cost Estimate

**Free Tier:** Lambda, S3, DynamoDB, API Gateway (covered)
**Bedrock:** ~$0.03-0.10 for hackathon testing
**Total:** < $1 for 3-day hackathon

## Hackathon Submission

**Team:** Coding Gladiators
**Event:** AI for Bharat Hackathon  
**Category:** Retail AI Solutions

## Key Highlights

- Solves real problem for Bharat retailers
- Uses AWS AI services (Bedrock)
- Serverless architecture (scalable, cost-effective)
- Regional customization (festivals, languages)
- Production-ready architecture
- Responsible AI practices

## Future Enhancements

- Mobile app (React Native)
- WhatsApp alerts for retailers
- Multi-language UI (Hindi, Tamil, Telugu)
- Advanced ML models (XGBoost, LSTM)
- POS system integration
- Pricing optimization recommendations