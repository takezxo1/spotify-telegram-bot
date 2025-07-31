"""
YouTube handler for searching and downloading audio.
"""

import yt_dlp
import os
import asyncio
from config import DOWNLOAD_FOLDER, YOUTUBE_QUALITIES, AUDIO_QUALITIES, MAX_FILE_SIZE
from utils import sanitize_filename, cleanup_file, format_file_size

class YouTubeHandler:
    def __init__(self):
        self.current_downloads = {}
    
    async def get_video_info(self, url):
        """Get video information from YouTube URL."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return None, "Could not extract video information"
                
                # Extract relevant information
                video_info = {
                    'title': info.get('title', 'Unknown Title'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'description': info.get('description', '')[:200] + '...' if info.get('description') else '',
                    'thumbnail': info.get('thumbnail'),
                    'upload_date': info.get('upload_date'),
                    'formats': info.get('formats', []),
                    'url': url
                }
                
                # Get available qualities
                video_qualities = self.get_available_qualities(info.get('formats', []))
                video_info['available_qualities'] = video_qualities
                
                return video_info, None
        
        except Exception as e:
            return None, f"Error getting video info: {str(e)}"
    
    def get_available_qualities(self, formats):
        """Extract available video qualities from formats."""
        qualities = set()
        
        for fmt in formats:
            height = fmt.get('height')
            if height:
                if height <= 144:
                    qualities.add('144p')
                elif height <= 240:
                    qualities.add('240p')
                elif height <= 360:
                    qualities.add('360p')
                elif height <= 480:
                    qualities.add('480p')
                elif height <= 720:
                    qualities.add('720p')
                elif height <= 1080:
                    qualities.add('1080p')
        
        # Sort qualities
        quality_order = ['144p', '240p', '360p', '480p', '720p', '1080p']
        available = [q for q in quality_order if q in qualities]
        
        if available:
            available.append('best')
        
        return available
    
    async def download_video(self, url, quality='best', format_type='mp4', progress_callback=None):
        """Download video from YouTube."""
        try:
            # Get video info first
            video_info, error = await self.get_video_info(url)
            if error:
                return None, error
            
            # Prepare filename
            title = sanitize_filename(video_info['title'])
            
            if format_type == 'mp3':
                output_path = os.path.join(DOWNLOAD_FOLDER, f"{title}.%(ext)s")
                # Audio download options
                ydl_opts = {
                    'format': AUDIO_QUALITIES.get(quality, 'bestaudio'),
                    'extractaudio': True,
                    'audioformat': 'mp3',
                    'outtmpl': output_path,
                    'noplaylist': True,
                    'quiet': True,
                    'no_warnings': True,
                }
            else:
                output_path = os.path.join(DOWNLOAD_FOLDER, f"{title}.%(ext)s")
                # Video download options
                if quality == 'best':
                    format_selector = 'best[ext=mp4]/best'
                else:
                    format_selector = YOUTUBE_QUALITIES.get(quality, 'best') + '[ext=mp4]/best[ext=mp4]/best'
                
                ydl_opts = {
                    'format': format_selector,
                    'outtmpl': output_path,
                    'noplaylist': True,
                    'quiet': True,
                    'no_warnings': True,
                }
            
            # Add progress hook if callback provided
            if progress_callback:
                ydl_opts['progress_hooks'] = [progress_callback]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Download the video
                info = ydl.extract_info(url, download=True)
                
                if info:
                    # Find the downloaded file
                    downloaded_file = ydl.prepare_filename(info)
                    
                    # Handle different extensions
                    if format_type == 'mp3':
                        downloaded_file = downloaded_file.replace('.webm', '.mp3').replace('.m4a', '.mp3')
                    
                    # Check if file exists and find actual file
                    if os.path.exists(downloaded_file):
                        file_size = os.path.getsize(downloaded_file)
                        if file_size > MAX_FILE_SIZE:
                            cleanup_file(downloaded_file)
                            return None, f"File too large ({format_file_size(file_size)}). Max size: {format_file_size(MAX_FILE_SIZE)}"
                        return downloaded_file, None
                    else:
                        # Try to find the file with different extensions
                        base_name = os.path.splitext(downloaded_file)[0]
                        extensions = ['.mp4', '.webm', '.mkv'] if format_type == 'mp4' else ['.mp3', '.m4a', '.webm', '.ogg']
                        
                        for ext in extensions:
                            test_file = base_name + ext
                            if os.path.exists(test_file):
                                file_size = os.path.getsize(test_file)
                                if file_size > MAX_FILE_SIZE:
                                    cleanup_file(test_file)
                                    return None, f"File too large ({format_file_size(file_size)}). Max size: {format_file_size(MAX_FILE_SIZE)}"
                                return test_file, None
                
                return None, "Download completed but file not found"
        
        except Exception as e:
            return None, f"Download error: {str(e)}"
    
    async def download_playlist(self, url, quality='best', format_type='mp4', max_videos=10):
        """Download playlist from YouTube (limited to max_videos)."""
        try:
            # Get playlist info
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info or 'entries' not in info:
                    return None, "Could not extract playlist information"
                
                playlist_info = {
                    'title': info.get('title', 'Unknown Playlist'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'total_videos': len(info['entries']),
                    'videos': []
                }
                
                # Limit number of videos
                entries = info['entries'][:max_videos]
                
                for entry in entries:
                    if entry:
                        video_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                        video_info = {
                            'title': entry.get('title', 'Unknown'),
                            'url': video_url,
                            'duration': entry.get('duration', 0)
                        }
                        playlist_info['videos'].append(video_info)
                
                return playlist_info, None
        
        except Exception as e:
            return None, f"Error processing playlist: {str(e)}"
    
    def format_video_info(self, video_info):
        """Format video information for display."""
        if not video_info:
            return "No video information available"
        
        duration = self.format_duration(video_info['duration'])
        view_count = self.format_number(video_info['view_count'])
        like_count = self.format_number(video_info['like_count'])
        
        info_text = f"""
📹 **{video_info['title']}**
👤 **Channel:** {video_info['uploader']}
⏱️ **Duration:** {duration}
👀 **Views:** {view_count}
👍 **Likes:** {like_count}
📝 **Description:** {video_info['description']}
        """
        
        return info_text.strip()
    
    def format_playlist_info(self, playlist_info):
        """Format playlist information for display."""
        if not playlist_info:
            return "No playlist information available"
        
        info_text = f"""
📋 **{playlist_info['title']}**
👤 **Channel:** {playlist_info['uploader']}
🎥 **Total Videos:** {playlist_info['total_videos']}

**Videos Preview:**
        """
        
        for i, video in enumerate(playlist_info['videos'][:5], 1):
            duration = self.format_duration(video['duration'])
            info_text += f"\n{i}. {video['title']} ({duration})"
        
        if len(playlist_info['videos']) > 5:
            info_text += f"\n... and {len(playlist_info['videos']) - 5} more videos"
        
        return info_text.strip()
    
    def format_duration(self, seconds):
        """Format duration from seconds to readable format."""
        if not seconds:
            return "Unknown"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def format_number(self, number):
        """Format large numbers in readable format."""
        if not number:
            return "0"
        
        if number >= 1000000:
            return f"{number / 1000000:.1f}M"
        elif number >= 1000:
            return f"{number / 1000:.1f}K"
        else:
            return str(number)
    
    def create_progress_callback(self, chat_id, message_id, bot):
        """Create progress callback for download updates."""
        async def progress_hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', 'N/A')
                speed = d.get('_speed_str', 'N/A')
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=f"⬇️ Downloading... {percent}\n🚀 Speed: {speed}"
                    )
                except:
                    pass  # Ignore edit errors
            elif d['status'] == 'finished':
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text="✅ Download completed! Processing..."
                    )
                except:
                    pass
        
        return progress_hook
