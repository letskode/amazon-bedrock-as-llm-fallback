#!/usr/bin/env python3
"""
Setup script for LLM Fallback Router
"""
import os
import sys
from pathlib import Path

def setup_environment():
    """Set up the development environment"""
    print("🚀 Setting up LLM Fallback Router...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        env_file.write_text(env_example.read_text())
        print("✅ .env file created - please edit with your API keys")
    elif env_file.exists():
        print("✅ .env file already exists")
    
    # Check if virtual environment is active
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not detected")
        print("   Consider running: python -m venv venv && source venv/bin/activate")
    else:
        print("✅ Virtual environment detected")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run tests: python test_litellm_fallback.py")
    print("3. Try examples: python litellm_fallback_router.py")
    print("\nFor more info, see README.md")

if __name__ == "__main__":
    setup_environment()