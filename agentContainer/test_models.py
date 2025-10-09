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
    
    # Common Gemini model names
    common_models = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.0-pro"
    ]
    
    print("📋 Available Gemini models:")
    for model in common_models:
        print(f"  📝 {model}")
    
    # Test with LangChain
    print("\n🧪 Testing LangChain integration:")
    
    google_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not google_creds or not os.path.exists(google_creds):
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set or file not found")
        return
    
    test_models = ["gemini-2.0-flash-exp", "gemini-1.5-flash"]
    
    for model in test_models:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            llm = ChatGoogleGenerativeAI(
                model=model,
                temperature=0.7,
                max_tokens=1000,
                convert_system_message_to_human=True
            )
            
            # Try a simple call
            response = llm.invoke("Hello! Respond with just 'OK' if you can hear me.")
            print(f"  ✅ {model} - Working! Response: {response.content[:50]}...")
            
        except ImportError:
            print(f"  ❌ {model} - langchain-google-genai not installed")
        except Exception as e:
            print(f"  ❌ {model} - Failed: {str(e)[:100]}...")

def test_current_model():
    """Test the currently configured model"""
    load_dotenv()
    
    model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
    google_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    print(f"\n🎯 Testing current model: {model_name}")
    
    if not google_creds or not os.path.exists(google_creds):
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set or file not found")
        return False
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.7,
            max_tokens=1000,
            convert_system_message_to_human=True
        )
        
        # Test with a simple prompt
        test_prompt = "You are an AI assistant for creating Jupyter notebooks. Respond with 'READY' if you can help create notebooks."
        response = llm.invoke(test_prompt)
        
        print(f"✅ Model {model_name} is working!")
        print(f"📋 Response: {response.content}")
        
        return True
        
    except ImportError:
        print("❌ langchain-google-genai package not installed. Run: pip install langchain-google-genai")
        return False
    except Exception as e:
        print(f"❌ Model {model_name} failed: {e}")
        return False

if __name__ == "__main__":
    list_available_models()
    success = test_current_model()
    exit(0 if success else 1)