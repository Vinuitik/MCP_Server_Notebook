#!/usr/bin/env python3
"""
Quick test to verify that all required files are accessible in the container
"""

import os
import sys

def check_file_exists(file_path, description):
    """Check if a file exists and print status"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - NOT FOUND")
        return False

def main():
    print("=" * 60)
    print("Docker Container File Check")
    print("=" * 60)
    
    print(f"Current working directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    print()
    
    all_good = True
    
    # Check required files
    files_to_check = [
        (".env", "Environment file"),
        ("service-account-key.json", "Service account key"),
        ("config/config.yaml", "Configuration file"),
        ("config/settings.py", "Settings module"),
        ("config/__init__.py", "Config package init"),
        ("agent.py", "Main agent file"),
    ]
    
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_good = False
    
    print()
    if all_good:
        print("🎉 All required files are present!")
        
        # Try to load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            project_id = os.getenv("PROJECT_ID")
            
            print(f"Environment variables loaded:")
            print(f"  GOOGLE_APPLICATION_CREDENTIALS: {creds_path}")
            print(f"  PROJECT_ID: {project_id}")
            
            if creds_path and os.path.exists(creds_path):
                print(f"✅ Service account key file accessible at: {creds_path}")
            else:
                print(f"❌ Service account key file not accessible")
                all_good = False
                
        except ImportError as e:
            print(f"❌ Failed to import dotenv: {e}")
            all_good = False
        except Exception as e:
            print(f"❌ Error loading environment: {e}")
            all_good = False
    
    if all_good:
        print("\n🚀 Container setup looks good!")
        sys.exit(0)
    else:
        print("\n❌ Container setup has issues!")
        sys.exit(1)

if __name__ == "__main__":
    main()