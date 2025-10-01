#!/usr/bin/env python3
"""
Script to verify Google credentials are properly configured
"""
import os
import json
from dotenv import load_dotenv

def verify_credentials():
    """Verify that Google credentials are properly configured"""
    print("🔍 Verifying Google Cloud credentials...")
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variable
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    print(f"📍 GOOGLE_APPLICATION_CREDENTIALS = {credentials_path}")
    
    if not credentials_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
        return False
    
    # Check if file exists
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found at: {credentials_path}")
        print(f"📁 Current directory: {os.getcwd()}")
        print(f"📁 Directory contents: {os.listdir('.')}")
        return False
    
    # Check file contents
    try:
        with open(credentials_path, 'r') as f:
            creds_data = json.load(f)
        
        print(f"✅ Credentials file found and readable")
        print(f"📋 Project ID: {creds_data.get('project_id', 'N/A')}")
        print(f"📋 Client email: {creds_data.get('client_email', 'N/A')}")
        print(f"📋 Type: {creds_data.get('type', 'N/A')}")
        
        # Test Google Auth
        try:
            import google.auth
            credentials, project = google.auth.default()
            print(f"✅ Google Auth successfully loaded credentials")
            print(f"📋 Detected project: {project}")
            
        except Exception as e:
            print(f"❌ Google Auth failed: {e}")
            return False
        
        # Test LangChain Google GenAI
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            model = ChatGoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=None,
                convert_system_message_to_human=True
            )
            print("✅ ChatGoogleGenerativeAI initialized successfully")
            
        except Exception as e:
            print(f"❌ ChatGoogleGenerativeAI initialization failed: {e}")
            return False
        
        print("🎉 All credential checks passed!")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in credentials file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials file: {e}")
        return False

if __name__ == "__main__":
    success = verify_credentials()
    exit(0 if success else 1)