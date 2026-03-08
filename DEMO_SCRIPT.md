# RetailIQ Hackathon Demo Script

## Demo Flow (5 minutes)

### 1. Introduction (30 seconds)
"RetailIQ is an AI-powered platform that helps small retailers in Bharat with demand forecasting and inventory optimization."

**Show:** Landing page

---

### 2. Data Upload (1 minute)
"Retailers can upload their sales data as a simple CSV file."

**Demo:**
1. Click "Choose File"
2. Select `sample_sales.csv`
3. Click "Upload CSV"
4. Show success message with record count

**Say:** "The system validates the data, removes duplicates, and stores it securely in AWS S3."

---

### 3. Demand Forecasting (1.5 minutes)
"Our AI generates demand forecasts for the next 7, 14, or 30 days."

**Demo:**
1. Enter Product ID: `P001`
2. Select horizon: `7 days`
3. Click "Generate Forecast"
4. Show the forecast chart and table

**Say:** "The system uses Prophet ML algorithm with Indian festival dates. It shows predicted demand with confidence intervals."

**Highlight:** 
- Chart visualization
- Confidence intervals
- Festival impact

---

### 4. Inventory Recommendations (1 minute)
"RetailIQ calculates stockout risk and tells you what to reorder."

**Demo:**
1. Click "Get Recommendations"
2. Show the recommendations table

**Say:** "Products are sorted by stockout risk. High-priority items are flagged in red. The system tells you exactly how much to order."

**Highlight:**
- Risk scores
- Priority levels
- Recommended quantities

---

### 5. AI Copilot (1.5 minutes)
"Retailers can ask questions in natural language."

**Demo:**
1. Type: "What should I restock next week?"
2. Show AI response
3. Type: "Which products are trending?"
4. Show AI response

**Say:** "The AI Copilot uses Amazon Bedrock to answer questions about inventory, trends, and sales patterns in simple business language."

---

### 6. Closing (30 seconds)
"RetailIQ helps small retailers make data-driven decisions, reduce stockouts, and optimize inventory - all powered by AWS AI services."

**Show:** Architecture diagram (optional)

**Key Points:**
- Serverless architecture (AWS Lambda, S3, DynamoDB)
- AI-powered forecasting (Prophet + Bedrock)
- Built for Bharat (festival dates, regional factors)
- Affordable for small retailers (AWS Free Tier)

---

## Key Talking Points

### Problem
- Small retailers face stockouts and overstocking
- Lack affordable forecasting tools
- Need to account for Indian festivals and seasonality

### Solution
- AI-powered demand forecasting
- Automated reorder recommendations
- Conversational AI copilot
- Built on AWS serverless architecture

### Impact
- Reduce stockouts by 30-40%
- Optimize inventory costs
- Data-driven decision making
- Accessible to small retailers

### Tech Stack
- **ML**: Prophet, Isolation Forest, Amazon Bedrock
- **AWS**: Lambda, S3, DynamoDB, API Gateway
- **Backend**: Python, FastAPI
- **Frontend**: HTML/CSS/JavaScript, Chart.js

---

## Sample Questions to Prepare For

**Q: How accurate are the forecasts?**
A: We use Prophet algorithm which typically achieves 70-85% accuracy. The system shows confidence intervals and warns users when accuracy is low.

**Q: How much does it cost?**
A: Built on AWS Free Tier - costs less than ₹500/month for small retailers. Scales automatically as business grows.

**Q: How does it handle Indian festivals?**
A: We've built in festival calendars (Diwali, Holi, Eid, etc.) as external factors in the forecasting model.

**Q: Can it integrate with existing systems?**
A: Yes! We provide REST APIs for all functionality - easy to integrate with POS systems or e-commerce platforms.

**Q: What about data privacy?**
A: All data is encrypted (AES-256), stored in India region (ap-south-1), and isolated per user. RBAC ensures users only see their own data.

---

## Pre-Demo Checklist

### Day Before Demo
- [ ] Test complete flow end-to-end
- [ ] Prepare sample data with realistic patterns
- [ ] Test AI Copilot with 5-10 sample questions
- [ ] Take screenshots of key features
- [ ] Prepare backup slides (in case of internet issues)
- [ ] Charge laptop fully

### 1 Hour Before Demo
- [ ] Test internet connection
- [ ] Start API server
- [ ] Start frontend server
- [ ] Upload sample data
- [ ] Generate forecasts for demo products
- [ ] Test AI Copilot responses
- [ ] Open all browser tabs needed

### During Demo
- [ ] Keep API logs visible (shows real-time processing)
- [ ] Have backup responses ready if Bedrock is slow
- [ ] Smile and be confident!

---

## Bonus Features to Mention

- Real-time anomaly detection
- Multi-language support (English, Hindi)
- Indian currency formatting (₹ with lakhs/crores)
- Regional trend analysis
- Responsible AI (explainable recommendations)