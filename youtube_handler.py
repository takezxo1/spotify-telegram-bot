"""
YouTube handler for searching and downloading audio.
"""

import os
import yt_dlp
import tempfile
from config import Config
import logging

logger = logging.getLogger(__name__)

class YouTubeHandler:
    """Handles YouTube operations."""
    
    def __init__(self):
        """Initialize YouTube handler."""
        # Ensure temp directory exists
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
    
    def search_youtube(self, query, max_results=5):
        """Search for videos on YouTube."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'default_search': 'ytsearch5:',  # Search for top 5 results
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(query, download=False)
                
                if not search_results or 'entries' not in search_results:
                    return []
                
                results = []
                entries = search_results.get('entries', [])
                for entry in entries[:max_results]:
                    if entry:
                        results.append({
                            'id': entry.get('id'),
                            'title': entry.get('title'),
                            'duration': entry.get('duration'),
                            'url': entry.get('webpage_url'),
                            'uploader': entry.get('uploader')
                        })
                
                return results
                
        except Exception as e:
            logger.error(f"Error searching for track: {e}")
            return []
    
    def download_audio(self, video_url, filename=None):
        """Download audio from YouTube video."""
        try:
            # Create a unique temporary filename
            if not filename:
                temp_file = tempfile.NamedTemporaryFile(
                    suffix=f'.{Config.AUDIO_FORMAT}',
                    dir=Config.TEMP_DIR,
                    delete=False
                )
                filename = temp_file.name
                temp_file.close()
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': filename.replace(f'.{Config.AUDIO_FORMAT}', '.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': Config.AUDIO_FORMAT,
                    'preferredquality': Config.AUDIO_QUALITY,
                }],
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            # Find the actual downloaded file
            expected_filename = filename
            if os.path.exists(expected_filename):
                return expected_filename
            
            # Sometimes the extension might be different
            base_name = filename.replace(f'.{Config.AUDIO_FORMAT}', '')
            for ext in ['mp3', 'm4a', 'webm', 'ogg']:
                test_file = f"{base_name}.{ext}"
                if os.path.exists(test_file):
                    return test_file
            
            return None
            
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            return None
    
    def get_best_match(self, search_results, track_info):
        """Find the best matching video from search results."""
        if not search_results or not track_info:
            return None
        
        # Simple scoring system based on title similarity and duration
        best_match = None
        best_score = 0
        
        expected_duration = track_info.get('duration_ms', 0) / 1000  # Convert to seconds
        track_name = track_info.get('name', '').lower()
        artists = [artist.lower() for artist in track_info.get('artists', [])]
        
        for result in search_results:
            score = 0
            title = result.get('title', '').lower()
            duration = result.get('duration', 0)
            
            # Score based on title containing track name
            if track_name in title:
                score += 50
            
            # Score based on title containing artist names
            for artist in artists:
                if artist in title:
                    score += 30
            
            # Score based on duration similarity (if available)
            if duration and expected_duration:
                duration_diff = abs(duration - expected_duration)
                if duration_diff < 10:  # Within 10 seconds
                    score += 20
                elif duration_diff < 30:  # Within 30 seconds
                    score += 10
            
            # Prefer official/music videos
            if any(keyword in title for keyword in ['official', 'music video', 'audio']):
                score += 15
            
            # Penalize live versions, covers, etc.
            if any(keyword in title for keyword in ['live', 'cover', 'remix', 'karaoke']):
                score -= 20
            
            if score > best_score:
                best_score = score
                best_match = result
        
        return best_match
    
    def process_download_request(self, search_query, track_info):
        """Process a complete download request."""
        # Search for videos
        search_results = self.search_youtube(search_query)
        if not search_results:
            return None, "This track is not available for download at the moment"
        
        # Find best match
        best_match = self.get_best_match(search_results, track_info)
        if not best_match:
            return None, "No suitable match found"
        
        # Download audio
        downloaded_file = self.download_audio(best_match['url'])
        if not downloaded_file:
            return None, "Failed to download audio"
        
        return downloaded_file, None
