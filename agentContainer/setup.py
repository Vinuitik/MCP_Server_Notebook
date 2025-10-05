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

def check_api_key():
    """Check if API key is configured"""
    load_dotenv()
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env file")
        print("💡 Please add your API key to the .env file:")
        print("   ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE")
        return False
    
    masked_key = f"{'*' * (len(api_key) - 4)}{api_key[-4:]}" if len(api_key) > 4 else "*" * len(api_key)
    print(f"✅ API key found: {masked_key}")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up MCP Agent...")
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Check API key
    if not check_api_key():
        return False
    
    print("\n🎉 Setup complete! You can now run the application:")
    print("   python main.py")
    print("\nOr using Docker:")
    print("   docker-compose up --build")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)