# RetailIQ Deployment Guide

---

## Quick Start (Local Testing)

### 1. Start the API Server

```bash
python api/main.py
```

API will run at:
http://localhost:8000


---

### 2. Start the Frontend

Open another terminal:

cd frontend
python -m http.server 3000

Frontend runs at:
http://localhost:3000


---

### 3. Test the Complete Flow

Open:
http://localhost:3000

Then:

- Upload sample_sales.csv
- Generate forecast for P001
- Get inventory recommendations
- Ask AI Copilot questions


---

## AWS Production Deployment

### Prerequisites

- AWS account
- AWS CLI configured
- Bedrock model access enabled

---

### Step 1 — Deploy Lambda Functions

#### Package Lambda

Run:

pip install -t lambda_package boto3 pandas numpy prophet scikit-learn

cp -r lambda_functions/* lambda_package/
cp -r utils lambda_package/

cd lambda_package
zip -r ../retailiq_lambda.zip .
cd ..

---

#### Create Lambda Functions

Go to:

https://console.aws.amazon.com/lambda/

Create 4 functions:

Function Name: retailiq-data-ingestion  
Runtime: Python 3.12  
Handler:
lambda_functions.data_ingestion.handler.lambda_handler  
Memory: 512 MB  
Timeout: 5 minutes  

Upload:
retailiq_lambda.zip  

---

Repeat same for:

retailiq-forecasting  
retailiq-inventory  
retailiq-copilot  

(Use the handlers you already defined)

---

#### Add IAM Permissions

Attach:

- AmazonS3FullAccess
- AmazonDynamoDBFullAccess
- AmazonBedrockFullAccess

---

### Step 2 — Deploy API Gateway

Go to:

https://console.aws.amazon.com/apigateway/

Create REST API.

Create endpoints:

POST /data/upload  
POST /forecast  
POST /inventory/recommendations  
POST /copilot/chat  
GET /health (mock)

Enable CORS.

Deploy to stage:

prod

---

### Step 3 — Deploy Frontend to S3

Edit:

frontend/app.js

Change:

const API_BASE_URL = "YOUR_API_GATEWAY_URL/prod";

---

Deploy:

aws s3 mb s3://retailiq-frontend-varun --region ap-south-1

aws s3 website s3://retailiq-frontend-varun --index-document index.html

aws s3 sync frontend/ s3://retailiq-frontend-varun --acl public-read

---

Website URL:

http://retailiq-frontend-varun.s3-website.ap-south-1.amazonaws.com

---

## Cost Optimization

Lambda – Free Tier  
S3 – Free Tier  
DynamoDB – Free Tier  
API Gateway – Free Tier  

Bedrock:
Nova Lite = Cheap  
Claude = Slightly Expensive  

Hackathon cost ≈ $5–10

---

## Troubleshooting

Bedrock error → Enable model access  

Lambda timeout → Increase memory + timeout  

CORS error → Enable CORS in API Gateway  
