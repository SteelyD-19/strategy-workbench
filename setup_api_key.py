#!/usr/bin/env python3
"""
Setup script for OpenAI API key configuration
"""

import os

def setup_api_key():
    print("=== OpenAI API Key Setup ===")
    print()
    
    # Check if API key is already set
    current_key = os.getenv("OPENAI_API_KEY")
    if current_key:
        print(f"✅ API key is already set: {current_key[:8]}...")
        return True
    
    print("No API key found. You have several options:")
    print()
    print("Option 1: Set environment variable (temporary)")
    print("  In PowerShell: $env:OPENAI_API_KEY='your-key-here'")
    print()
    print("Option 2: Edit config.env file (recommended)")
    print("  Edit the 'config.env' file in this directory and replace:")
    print("  'your-openai-api-key-here' with your actual API key")
    print()
    
    # Check if config.env file exists
    config_file = os.path.join(os.path.dirname(__file__), 'config.env')
    if os.path.exists(config_file):
        print("✅ config.env file exists")
        try:
            with open(config_file, 'r') as f:
                content = f.read()
                # Check if there's a real API key (starts with sk-)
                lines = content.split('\n')
                api_key_line = None
                for line in lines:
                    if line.strip().startswith('OPENAI_API_KEY='):
                        api_key_line = line.strip()
                        break
                
                if api_key_line and api_key_line.startswith('OPENAI_API_KEY=sk-'):
                    print("✅ config.env file contains a real OPENAI_API_KEY")
                    return True
                elif api_key_line and 'your-openai-api-key-here' in api_key_line:
                    print("⚠️  config.env file exists but contains placeholder API key")
                    print("   Please edit config.env and replace 'your-openai-api-key-here' with your actual API key")
                else:
                    print("❌ config.env file exists but doesn't contain OPENAI_API_KEY")
        except Exception as e:
            print(f"❌ Error reading config.env file: {e}")
    else:
        print("❌ No config.env file found")
    
    print()
    print("After setting up your API key, restart Streamlit to see the changes.")
    return False

if __name__ == "__main__":
    setup_api_key()
