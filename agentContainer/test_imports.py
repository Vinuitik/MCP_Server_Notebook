#!/usr/bin/env python3
"""
Quick test script to validate the agent imports work correctly
"""

def test_imports():
    """Test that all agent imports work correctly"""
    try:
        print("🔍 Testing agent imports...")
        
        # Test basic imports
        from typing import Dict, Any, List, Optional
        print("✅ Typing imports work")
        
        import json
        print("✅ JSON import works")
        
        import asyncio
        print("✅ Asyncio import works")
        
        # Test LangChain imports
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            print("✅ LangChain Google Gemini import works")
        except ImportError as e:
            print(f"❌ LangChain Google Gemini import failed: {e}")
        
        # Test LangGraph imports
        try:
            from langgraph.graph import StateGraph, END
            print("✅ LangGraph imports work")
        except ImportError as e:
            print(f"❌ LangGraph import failed: {e}")
        
        # Test agent module
        try:
            from agent import AgenticState, run_agent
            print("✅ Agent module imports work")
            
            # Test basic state creation
            state = AgenticState()
            print("✅ AgenticState creation works")
            
        except ImportError as e:
            print(f"❌ Agent import failed: {e}")
        except Exception as e:
            print(f"❌ Agent functionality test failed: {e}")
        
        print("\n🎉 Import testing completed!")
        
    except Exception as e:
        print(f"❌ Critical import error: {e}")

if __name__ == "__main__":
    test_imports()