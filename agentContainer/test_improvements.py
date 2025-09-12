"""
Test script to demonstrate the improved LangChain-based MCP agent
"""

import asyncio
import requests
import json
from typing import Dict, Any


def test_legacy_endpoint():
    """Test the legacy chat endpoint"""
    print("🧪 Testing Legacy Endpoint...")
    
    url = "http://localhost:9001/chat"
    test_messages = [
        "create markdown cell with content hello world",
        "create code cell with print hello",
        "show history"
    ]
    
    for message in test_messages:
        payload = {"message": message}
        try:
            response = requests.post(url, json=payload, timeout=30)
            result = response.json()
            print(f"📤 Input: {message}")
            print(f"📥 Output: {result.get('response', 'No response')}")
            print("-" * 50)
        except Exception as e:
            print(f"❌ Error: {e}")


def test_improved_endpoint():
    """Test the improved LangChain-based endpoint"""
    print("🚀 Testing Improved LangChain Endpoint...")
    
    url = "http://localhost:9001/v2/chat"
    test_messages = [
        "I need to create a data analysis notebook. Start with a markdown cell explaining the purpose.",
        "Add a code cell that imports the essential data science libraries.",
        "Create another cell that loads a CSV file called 'sales_data.csv' into a DataFrame.",
        "Show me what's in the notebook so far.",
        "Run the imports cell."
    ]
    
    for message in test_messages:
        payload = {"message": message}
        try:
            response = requests.post(url, json=payload, timeout=30)
            result = response.json()
            print(f"📤 Input: {message}")
            print(f"📥 Output: {result.get('response', 'No response')}")
            print("=" * 80)
        except Exception as e:
            print(f"❌ Error: {e}")


def test_conversation_memory():
    """Test conversation memory functionality"""
    print("🧠 Testing Conversation Memory...")
    
    url = "http://localhost:9001/v2/chat"
    
    # First message
    response1 = requests.post(url, json={"message": "Create a code cell with x = 5"})
    print(f"📤 First: Create a code cell with x = 5")
    print(f"📥 Response: {response1.json().get('response', '')[:100]}...")
    
    # Follow-up message that references previous context
    response2 = requests.post(url, json={"message": "Now create another cell that prints x"})
    print(f"📤 Follow-up: Now create another cell that prints x")
    print(f"📥 Response: {response2.json().get('response', '')[:100]}...")
    
    # Get history
    history_response = requests.get("http://localhost:9001/v2/chat/history")
    print(f"📜 Conversation history length: {len(history_response.json().get('history', []))}")


def test_status_endpoints():
    """Test status and health endpoints"""
    print("💊 Testing Status Endpoints...")
    
    endpoints = [
        "http://localhost:9001/health",
        "http://localhost:9001/v2/chat/health",
        "http://localhost:9001/v2/chat/status",
        "http://localhost:9001/mcp/health"
    ]
    
    for url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {url}: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ {url}: Error - {e}")


def compare_responses():
    """Compare legacy vs improved responses"""
    print("⚖️ Comparing Legacy vs Improved Responses...")
    
    test_message = "I want to create a markdown cell that explains data preprocessing steps"
    
    # Legacy
    try:
        legacy_response = requests.post(
            "http://localhost:9001/chat", 
            json={"message": test_message},
            timeout=30
        )
        legacy_result = legacy_response.json().get('response', 'No response')
    except Exception as e:
        legacy_result = f"Error: {e}"
    
    # Improved
    try:
        improved_response = requests.post(
            "http://localhost:9001/v2/chat", 
            json={"message": test_message},
            timeout=30
        )
        improved_result = improved_response.json().get('response', 'No response')
    except Exception as e:
        improved_result = f"Error: {e}"
    
    print(f"📤 Input: {test_message}")
    print(f"🏚️ Legacy: {legacy_result}")
    print(f"🚀 Improved: {improved_result}")


if __name__ == "__main__":
    print("🎯 MCP Agent Container Test Suite")
    print("=" * 80)
    
    try:
        # Check if servers are running
        health_check = requests.get("http://localhost:9001/health", timeout=5)
        print(f"✅ Agent Container is running: {health_check.json()}")
        
        mcp_health = requests.get("http://localhost:9001/mcp/health", timeout=5)
        print(f"✅ MCP Server status: {mcp_health.json()}")
        print("=" * 80)
        
        # Run tests
        test_status_endpoints()
        print("\n")
        
        test_legacy_endpoint()
        print("\n")
        
        test_improved_endpoint()
        print("\n")
        
        test_conversation_memory()
        print("\n")
        
        compare_responses()
        
    except Exception as e:
        print(f"❌ Cannot connect to services. Make sure the containers are running: {e}")
        print("Run: docker-compose up --build")