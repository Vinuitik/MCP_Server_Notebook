#!/usr/bin/env python3
"""
Script to list available Gemini models and test model initialization
"""
import os
from dotenv import load_dotenv

def list_available_models():
    """List available Gemini models"""
    print("🔍 Checking available Gemini models...")
    
    # Load environment variables
    load_dotenv()
    
    try:
        import google.generativeai as genai
        
        # Configure the API
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        # List models
        print("📋 Available Gemini models:")
        
        # Common model names to try
        common_models = [
            "gemini-1.5-pro",
            "gemini-1.5-flash", 
            "gemini-1.0-pro",
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-1.5-pro-latest",
            "gemini-1.5-flash-latest"
        ]
        
        for model in common_models:
            try:
                # Try to get model info
                model_info = genai.get_model(f"models/{model}")
                print(f"  ✅ {model} - {model_info.display_name}")
            except Exception as e:
                print(f"  ❌ {model} - Not available")
        
        # Test with LangChain
        print("\n🧪 Testing LangChain integration:")
        test_models = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"]
        
        for model in test_models:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                
                llm = ChatGoogleGenerativeAI(
                    model=model,
                    google_api_key=None,
                    convert_system_message_to_human=True
                )
                
                # Try a simple call
                response = llm.invoke("Hello! Respond with just 'OK' if you can hear me.")
                print(f"  ✅ {model} - Working! Response: {response.content[:50]}...")
                
            except Exception as e:
                print(f"  ❌ {model} - Failed: {str(e)[:100]}...")
        
    except ImportError:
        print("❌ google-generativeai package not installed")
    except Exception as e:
        print(f"❌ Error listing models: {e}")

def test_current_model():
    """Test the currently configured model"""
    load_dotenv()
    
    model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-pro')
    print(f"\n🎯 Testing current model: {model_name}")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=None,
            convert_system_message_to_human=True,
            temperature=0.7,
            max_tokens=2048
        )
        
        # Test with a simple prompt
        test_prompt = "You are an AI assistant for creating Jupyter notebooks. Respond with 'READY' if you can help create notebooks."
        response = llm.invoke(test_prompt)
        
        print(f"✅ Model {model_name} is working!")
        print(f"📋 Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model {model_name} failed: {e}")
        return False

if __name__ == "__main__":
    list_available_models()
    success = test_current_model()
    exit(0 if success else 1)