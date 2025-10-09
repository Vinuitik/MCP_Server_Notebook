#!/usr/bin/env python3
"""
Simple installation and health check script for the MCP Agent
"""
import subprocess
import sys
import os
from dotenv import load_dotenv

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_credentials():
    """Check if Google credentials are configured"""
    load_dotenv()
    google_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not google_creds:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not found in .env file")
        print("💡 Please add your service account key path to the .env file:")
        print("   GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json")
        return False
    
    if not os.path.exists(google_creds):
        print(f"❌ Google service account key file not found: {google_creds}")
        print("💡 Please ensure the service account key file exists at the specified path")
        return False
    
    print(f"✅ Google credentials found: {google_creds}")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up MCP Agent...")
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Check credentials
    if not check_credentials():
        return False
    
    print("\n🎉 Setup complete! You can now run the application:")
    print("   python main.py")
    print("\nOr using Docker:")
    print("   docker-compose up --build")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)