"""
Utility functions for the Telegram bot.
"""

import re
import os

def clean_filename(filename):
    """Clean filename to be safe for file systems."""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'[\r\n\t]', ' ', filename)
    filename = re.sub(r'\s+', ' ', filename).strip()
    
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

def is_valid_audio_file(filepath):
    """Check if file is a valid audio file."""
    if not os.path.exists(filepath):
        return False
    
    # Check file size
    if os.path.getsize(filepath) == 0:
        return False
    
    # Check extension
    valid_extensions = ['.mp3', '.m4a', '.ogg', '.webm']
    file_ext = os.path.splitext(filepath)[1].lower()
    
    return file_ext in valid_extensions

def sanitize_search_query(query):
    """Sanitize search query for processing."""
    # Remove special characters that might interfere with search
    query = re.sub(r'[^\w\s\-&]', '', query)
    query = re.sub(r'\s+', ' ', query).strip()
    
    return query
