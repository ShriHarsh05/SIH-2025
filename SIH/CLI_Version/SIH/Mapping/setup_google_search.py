#!/usr/bin/env python3
"""
Setup script for Google Custom Search API configuration
Helps users configure the .env file for autocomplete fallback
"""

import os
from pathlib import Path

def setup_google_search():
    """Interactive setup for Google Search API"""
    
    print("=" * 60)
    print("Google Custom Search API Setup")
    print("=" * 60)
    print()
    print("This feature enables web search fallback when no local results")
    print("are found in the autocomplete.")
    print()
    print("To get your credentials:")
    print("1. API Key: https://console.cloud.google.com/apis/credentials")
    print("2. Search Engine ID: https://programmablesearchengine.google.com/")
    print()
    print("See GOOGLE_SEARCH_FALLBACK_GUIDE.md for detailed instructions.")
    print()
    
    # Check if .env already exists
    env_path = Path(__file__).parent / ".env"
    env_exists = env_path.exists()
    
    if env_exists:
        print(f"⚠️  .env file already exists at: {env_path}")
        overwrite = input("Do you want to update it? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
        print()
    
    # Get API credentials
    print("Enter your Google API credentials:")
    print("(Press Enter to skip and disable Google Search fallback)")
    print()
    
    api_key = input("Google API Key: ").strip()
    search_engine_id = input("Search Engine ID: ").strip()
    
    if not api_key or not search_engine_id:
        print()
        print("⚠️  No credentials provided. Google Search fallback will be disabled.")
        print("   You can configure it later by editing the .env file.")
        api_key = ""
        search_engine_id = ""
    
    # Create or update .env file
    env_content = f"""# Google Custom Search API Configuration
# Used for autocomplete fallback when no local results are found
# Get your API key from: https://console.cloud.google.com/apis/credentials
# Create a Custom Search Engine at: https://programmablesearchengine.google.com/

GOOGLE_API_KEY={api_key}
GOOGLE_SEARCH_ENGINE_ID={search_engine_id}
"""
    
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print()
        print("=" * 60)
        print("✅ Configuration saved successfully!")
        print("=" * 60)
        print()
        print(f"Configuration file: {env_path}")
        print()
        
        if api_key and search_engine_id:
            print("✅ Google Search fallback is ENABLED")
            print("   Autocomplete will search Google when no local results found.")
        else:
            print("⚠️  Google Search fallback is DISABLED")
            print("   Only local dataset results will be shown.")
        
        print()
        print("Next steps:")
        print("1. Install httpx: pip install httpx")
        print("2. Restart the API server")
        print("3. Test autocomplete with unknown terms")
        print()
        
    except Exception as e:
        print()
        print(f"❌ Error saving configuration: {e}")
        print()

def test_configuration():
    """Test if Google Search API is configured"""
    
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print("❌ .env file not found")
        print("   Run this script to configure Google Search API")
        return False
    
    # Try to load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        
        api_key = os.getenv("GOOGLE_API_KEY", "")
        search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
        
        if api_key and search_engine_id:
            print("✅ Google Search API is configured")
            print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
            print(f"   Search Engine ID: {search_engine_id}")
            return True
        else:
            print("⚠️  Google Search API is not configured")
            print("   Fallback search is disabled")
            return False
            
    except ImportError:
        print("⚠️  python-dotenv not installed")
        print("   Install it with: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_configuration()
    else:
        setup_google_search()
