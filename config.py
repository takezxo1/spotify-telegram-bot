"""
Configuration settings for the Telegram bot.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Spotify API Configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# Download Settings
DOWNLOAD_FOLDER = 'downloads'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit for Telegram

# Quality options for YouTube downloads
YOUTUBE_QUALITIES = {
    '144p': 'worst[height<=144]',
    '240p': 'worst[height<=240]',
    '360p': 'best[height<=360]',
    '480p': 'best[height<=480]',
    '720p': 'best[height<=720]',
    '1080p': 'best[height<=1080]',
    'best': 'best'
}

AUDIO_QUALITIES = {
    '64kbps': 'worstaudio[abr<=64]',
    '128kbps': 'bestaudio[abr<=128]',
    '192kbps': 'bestaudio[abr<=192]',
    '320kbps': 'bestaudio[abr<=320]',
    'best': 'bestaudio'
}

# Bot Messages
WELCOME_MESSAGE = """
🎵 **Welcome to Premium Media Downloader Bot** 🎵

I can help you download content from:
🎶 **Spotify** (via YouTube search)
📹 **YouTube** (Video/Audio)
📱 **Instagram** (Posts/Stories/Reels)

Simply send me a link and I'll handle the rest!

✨ *Premium features with beautiful interface* ✨
"""

HELP_MESSAGE = """
🔗 **Supported Links:**

🎵 **Spotify:**
• Song links
• Album links
• Playlist links

📹 **YouTube:**
• Video links
• Playlist links
• Shorts links

📱 **Instagram:**
• Post links
• Reel links
• Story links

Just paste any supported link and enjoy! 🚀
"""
