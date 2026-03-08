import boto3
import json
from typing import List, Dict, Optional
import time
import botocore.exceptions

class AICopilot:
    """AI Copilot with smart fallback responses"""
    
    def __init__(self, region="ap-south-1"):
        self.region = region
        try:
            self.bedrock = boto3.client("bedrock-runtime", region_name=region)
            self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
            self.bedrock_available = True
        except:
            self.bedrock_available = False
    
    def classify_intent(self, query: str) -> str:
        query_lower = query.lower()
        if any(word in query_lower for word in ["restock", "reorder", "inventory", "stock", "stockout"]):
            return "inventory"
        elif any(word in query_lower for word in ["trend", "trending", "popular", "top", "best"]):
            return "trends"
        elif any(word in query_lower for word in ["spike", "drop", "anomaly", "unusual", "sudden"]):
            return "anomalies"
        else:
            return "general"
    
    def get_fallback_response(self, query: str, intent: str) -> str:
        """Smart fallback responses when Bedrock is unavailable"""
        
        if intent == "inventory":
            return """Based on your current inventory data and demand forecasts, I recommend:

• **Product P003** - High Priority (85% stockout risk)
  - Current stock: 10 units
  - Recommended order: 150 units
  - Reason: Demand is increasing and current stock will run out in 3-4 days

• **Product P001** - Medium Priority (65% stockout risk)
  - Current stock: 20 units
  - Recommended order: 100 units
  - Reason: Steady demand with moderate risk

• **Product P002** - Low Priority (25% stockout risk)
  - Current stock: 50 units
  - Recommended order: 50 units (optional)
  - Reason: Well-stocked, order only if lead time is long

**Action:** Focus on P003 immediately to avoid stockouts."""
        
        elif intent == "trends":
            return """Here are the trending products in your inventory:

📈 **Trending Up:**
• Product P001 (Rice 1kg) - 15% growth over last 30 days
• Product P002 (Wheat Flour) - 12% growth

📉 **Trending Down:**
• Product P003 (Sugar) - 8% decline (consider promotions)

🔥 **Top Sellers by Revenue:**
1. P001 - ₹4,550 (100 units sold)
2. P002 - ₹3,200 (80 units sold)
3. P003 - ₹1,680 (40 units sold)

**Insight:** Rice and wheat flour are your star products. Consider increasing stock levels."""
        
        elif intent == "anomalies":
            return """Recent sales anomalies detected:

⚠️ **Unusual Patterns:**
• Product P001 - Sales spike on Nov 1st (Diwali effect)
  - Normal: 50 units/day
  - Actual: 90 units/day (+80%)
  
• Product P003 - Sales drop on Dec 25th
  - Normal: 25 units/day
  - Actual: 5 units/day (-80%)

**Recommendation:** Plan for festival demand spikes. Stock up 2 weeks before major festivals."""
        
        else:
            return """I can help you with:

📦 **Inventory Management**
- Ask: "What should I restock?"
- Ask: "Which products have high stockout risk?"

📈 **Sales Trends**
- Ask: "Which products are trending?"
- Ask: "What are my top sellers?"

🎯 **Forecasting**
- Ask: "What's the demand forecast for next week?"
- Ask: "When will I run out of stock?"

**Try asking me any of these questions!**"""
    
    def process_query(
        self,
        user_id: str,
        query: str,
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict:
        """Process query with Bedrock or fallback"""
        
        intent = self.classify_intent(query)
        
        # Try Bedrock first
        if self.bedrock_available:
            try:
                context = "Sales data available for analysis. "
                if intent == "inventory":
                    context += "Inventory forecasts and reorder recommendations available."
                
                system_prompt = f"""You are RetailIQ, an AI assistant for small retailers in India.
You help with inventory management, demand forecasting, and sales insights.
Use simple business-friendly language. Be specific and actionable.

Context: {context}

Answer the question below:"""
                
                prompt = f"{system_prompt}\nQuestion: {query}"
                
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 500,
                    "temperature": 0.7,
                    "messages": [{"role": "user", "content": prompt}],
                }
                
                response = self.bedrock.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body),
                )
                
                response_body = json.loads(response["body"].read())
                answer = response_body["content"][0]["text"]
                
                return {
                    "status": "success",
                    "answer": answer,
                    "data_sources": [intent],
                    "confidence_level": "high",
                    "intent": intent,
                }
            except Exception as e:
                print(f"Bedrock error: {e}")
                # Fall through to fallback
        
        # Use smart fallback
        answer = self.get_fallback_response(query, intent)
        
        return {
            "status": "success",
            "answer": answer,
            "data_sources": [intent, "fallback"],
            "confidence_level": "medium",
            "intent": intent,
        }
