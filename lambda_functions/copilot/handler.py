import sys
import os
import json

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.copilot import AICopilot

copilot = AICopilot()

def process_copilot_query(user_id: str, query: str, conversation_history: list = None) -> dict:
    """
    Processes AI Copilot query.
    
    Args:
        user_id: User identifier
        query: Natural language question
        conversation_history: Previous messages
        
    Returns:
        Copilot response dict
    """
    return copilot.process_query(user_id, query, conversation_history)

# For testing
if __name__ == '__main__':
    test_queries = [
        "What should I restock next week?",
        "Which products are trending up?",
        "Show me products with high stockout risk"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = process_copilot_query('test_user', query)
        print(f"Response: {result['answer']}")
        print(f"Intent: {result['intent']}")
        print("-" * 50)
