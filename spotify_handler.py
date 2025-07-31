"""
Spotify API handler for extracting song metadata.
"""

import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from config import Config
import logging

logger = logging.getLogger(__name__)

class SpotifyHandler:
    """Handles Spotify API operations."""
    
    def __init__(self):
        """Initialize Spotify client."""
        try:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=Config.SPOTIFY_CLIENT_ID,
                client_secret=Config.SPOTIFY_CLIENT_SECRET
            )
            self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        except Exception as e:
            logger.error(f"Failed to initialize Spotify client: {e}")
            self.sp = None
    
    def is_spotify_url(self, url):
        """Check if the URL is a valid Spotify track URL."""
        spotify_patterns = [
            r'https://open\.spotify\.com/track/([a-zA-Z0-9]+)',
            r'https://spotify\.com/track/([a-zA-Z0-9]+)',
            r'spotify:track:([a-zA-Z0-9]+)'
        ]
        
        for pattern in spotify_patterns:
            if re.match(pattern, url):
                return True
        return False
    
    def extract_track_id(self, url):
        """Extract Spotify track ID from URL."""
        patterns = [
            r'https://open\.spotify\.com/track/([a-zA-Z0-9]+)',
            r'https://spotify\.com/track/([a-zA-Z0-9]+)',
            r'spotify:track:([a-zA-Z0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_track_info(self, track_id):
        """Get track information from Spotify."""
        if not self.sp:
            return None
        
        try:
            track = self.sp.track(track_id)
            
            if not track:
                return None
            
            # Extract relevant information
            track_info = {
                'name': track.get('name', ''),
                'artists': [artist.get('name', '') for artist in track.get('artists', [])],
                'album': track.get('album', {}).get('name', ''),
                'duration_ms': track.get('duration_ms', 0),
                'popularity': track.get('popularity', 0),
                'preview_url': track.get('preview_url'),
                'external_urls': track.get('external_urls', {})
            }
            
            return track_info
            
        except Exception as e:
            logger.error(f"Error fetching track info: {e}")
            return None
    
    def get_search_query(self, track_info):
        """Generate search query from track info."""
        if not track_info:
            return None
        
        artists = ' '.join(track_info['artists'])
        query = f"{artists} - {track_info['name']}"
        
        return query
    
    def process_spotify_url(self, url):
        """Process Spotify URL and return track information."""
        if not self.is_spotify_url(url):
            return None
        
        track_id = self.extract_track_id(url)
        if not track_id:
            return None
        
        track_info = self.get_track_info(track_id)
        if not track_info:
            return None
        
        search_query = self.get_search_query(track_info)
        
        return {
            'track_info': track_info,
            'search_query': search_query
        }
