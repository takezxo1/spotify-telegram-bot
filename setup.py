#!/usr/bin/env python3
"""
Setup script for Premium Media Downloader Bot
"""

import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install required packages."""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements!")
        return False

def setup_env_file():
    """Set up environment file."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("📝 Creating .env file from template...")
            with open(env_example, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ .env file created!")
            print("⚠️  Please edit .env file and add your API keys before running the bot.")
            return True
        else:
            print("❌ .env.example not found!")
            return False
    else:
        print("ℹ️  .env file already exists.")
        return True

def create_downloads_folder():
    """Create downloads folder."""
    downloads_dir = Path("downloads")
    if not downloads_dir.exists():
        downloads_dir.mkdir()
        print("📁 Created downloads folder.")
    else:
        print("ℹ️  Downloads folder already exists.")

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")
        return True

def main():
    """Main setup function."""
    print("🚀 Setting up Premium Media Downloader Bot...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Setup environment file
    if not setup_env_file():
        sys.exit(1)
    
    # Create downloads folder
    create_downloads_folder()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit the .env file and add your API keys:")
    print("   - TELEGRAM_BOT_TOKEN (from @BotFather)")
    print("   - SPOTIFY_CLIENT_ID (from Spotify Developer Dashboard)")
    print("   - SPOTIFY_CLIENT_SECRET (from Spotify Developer Dashboard)")
    print("\n2. Run the bot:")
    print("   python bot.py")
    print("\n📖 For detailed instructions, see README.md")

if __name__ == "__main__":
    main()