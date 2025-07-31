"""
Utility functions for the Telegram bot.
"""

import re
import os
import asyncio
from urllib.parse import urlparse
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def detect_link_type(url):
    """Detect the type of link provided by the user."""
    url = url.strip()
    
    # Spotify patterns
    spotify_patterns = [
        r'open\.spotify\.com/(track|album|playlist)/',
        r'spotify:(track|album|playlist):',
    ]
    
    # YouTube patterns
    youtube_patterns = [
        r'youtube\.com/watch',
        r'youtu\.be/',
        r'youtube\.com/playlist',
        r'youtube\.com/shorts/',
        r'm\.youtube\.com/watch',
    ]
    
    # Instagram patterns
    instagram_patterns = [
        r'instagram\.com/p/',
        r'instagram\.com/reel/',
        r'instagram\.com/stories/',
        r'instagr\.am/p/',
    ]
    
    for pattern in spotify_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return 'spotify'
    
    for pattern in youtube_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return 'youtube'
    
    for pattern in instagram_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return 'instagram'
    
    return 'unknown'

def create_quality_keyboard(platform, content_type='video'):
    """Create inline keyboard for quality selection."""
    keyboard = []
    
    if platform == 'youtube':
        if content_type == 'video':
            keyboard.append([
                InlineKeyboardButton("📹 MP4", callback_data="format_mp4"),
                InlineKeyboardButton("🎵 MP3", callback_data="format_mp3")
            ])
            keyboard.append([
                InlineKeyboardButton("144p", callback_data="quality_144p"),
                InlineKeyboardButton("240p", callback_data="quality_240p"),
                InlineKeyboardButton("360p", callback_data="quality_360p")
            ])
            keyboard.append([
                InlineKeyboardButton("480p", callback_data="quality_480p"),
                InlineKeyboardButton("720p", callback_data="quality_720p"),
                InlineKeyboardButton("1080p", callback_data="quality_1080p")
            ])
            keyboard.append([
                InlineKeyboardButton("🌟 Best Quality", callback_data="quality_best")
            ])
        else:  # audio
            keyboard.append([
                InlineKeyboardButton("64kbps", callback_data="audio_64kbps"),
                InlineKeyboardButton("128kbps", callback_data="audio_128kbps")
            ])
            keyboard.append([
                InlineKeyboardButton("192kbps", callback_data="audio_192kbps"),
                InlineKeyboardButton("320kbps", callback_data="audio_320kbps")
            ])
            keyboard.append([
                InlineKeyboardButton("🌟 Best Quality", callback_data="audio_best")
            ])
    
    keyboard.append([
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    ])
    
    return InlineKeyboardMarkup(keyboard)

def create_main_menu_keyboard():
    """Create main menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("📖 Help", callback_data="help"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ],
        [
            InlineKeyboardButton("🔗 Supported Links", callback_data="supported_links")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_download_progress_keyboard():
    """Create keyboard shown during download."""
    keyboard = [
        [InlineKeyboardButton("❌ Cancel Download", callback_data="cancel_download")]
    ]
    return InlineKeyboardMarkup(keyboard)

def sanitize_filename(filename):
    """Sanitize filename for safe file operations."""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    return filename

def format_file_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"

def ensure_download_folder():
    """Ensure download folder exists."""
    from config import DOWNLOAD_FOLDER
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

def cleanup_file(filepath):
    """Clean up downloaded file."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception:
        pass

def extract_spotify_id(url):
    """Extract Spotify track/album/playlist ID from URL."""
    patterns = [
        r'open\.spotify\.com/(track|album|playlist)/([a-zA-Z0-9]+)',
        r'spotify:(track|album|playlist):([a-zA-Z0-9]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1), match.group(2)
    
    return None, None

def create_spotify_keyboard():
    """Create keyboard for Spotify downloads."""
    keyboard = [
        [
            InlineKeyboardButton("🎵 Download Audio", callback_data="spotify_download"),
            InlineKeyboardButton("ℹ️ Show Info", callback_data="spotify_info")
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_instagram_keyboard():
    """Create keyboard for Instagram downloads."""
    keyboard = [
        [
            InlineKeyboardButton("📥 Download", callback_data="instagram_download"),
            InlineKeyboardButton("ℹ️ Show Info", callback_data="instagram_info")
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
