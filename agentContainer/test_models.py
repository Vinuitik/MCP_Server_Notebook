#!/usr/bin/env python3
"""
Script to list available Claude models and test model initialization
"""
import os
from dotenv import load_dotenv

def list_available_models():
    """List available Claude models"""
    print("🔍 Checking available Claude models...")
    
    # Load environment variables
    load_dotenv()
    
    # Common Claude model names
    common_models = [
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229", 
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-3-5-haiku-20241022"
    ]
    
    print("📋 Available Claude models:")
    for model in common_models:
        print(f"  📝 {model}")
    
    # Test with LangChain
    print("\n🧪 Testing LangChain integration:")
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        return
    
    test_models = ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]
    
    for model in test_models:
        try:
            from langchain_anthropic import ChatAnthropic
            
            llm = ChatAnthropic(
                model=model,
                anthropic_api_key=api_key,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Try a simple call
            response = llm.invoke("Hello! Respond with just 'OK' if you can hear me.")
            print(f"  ✅ {model} - Working! Response: {response.content[:50]}...")
            
        except ImportError:
            print(f"  ❌ {model} - langchain-anthropic not installed")
        except Exception as e:
            print(f"  ❌ {model} - Failed: {str(e)[:100]}...")

def test_current_model():
    """Test the currently configured model"""
    load_dotenv()
    
    model_name = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    print(f"\n🎯 Testing current model: {model_name}")
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        return False
    
    try:
        from langchain_anthropic import ChatAnthropic
        
        llm = ChatAnthropic(
            model=model_name,
            anthropic_api_key=api_key,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Test with a simple prompt
        test_prompt = "You are an AI assistant for creating Jupyter notebooks. Respond with 'READY' if you can help create notebooks."
        response = llm.invoke(test_prompt)
        
        print(f"✅ Model {model_name} is working!")
        print(f"📋 Response: {response.content}")
        
        return True
        
    except ImportError:
        print("❌ langchain-anthropic package not installed. Run: pip install langchain-anthropic")
        return False
    except Exception as e:
        print(f"❌ Model {model_name} failed: {e}")
        return False

if __name__ == "__main__":
    list_available_models()
    success = test_current_model()
    exit(0 if success else 1)