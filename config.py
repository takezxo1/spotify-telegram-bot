"""
Configuration settings for the Telegram bot.
"""

import os

class Config:
    """Configuration class for bot settings."""
    
    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your_telegram_bot_token')
    
    # Spotify API credentials
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', 'your_spotify_client_id')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', 'your_spotify_client_secret')
    
    # File settings
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max file size for Telegram
    TEMP_DIR = '/tmp/telegram_bot_downloads'
    
    # Audio settings
    AUDIO_FORMAT = 'mp3'
    AUDIO_QUALITY = '192'  # kbps
    
    # YouTube-DL settings
    YT_DLP_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': AUDIO_FORMAT,
        'audioquality': AUDIO_QUALITY,
        'outtmpl': f'{TEMP_DIR}/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }
