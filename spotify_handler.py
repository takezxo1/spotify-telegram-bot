"""
Spotify API handler for extracting song metadata.
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import os
import re
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, DOWNLOAD_FOLDER
from utils import sanitize_filename, cleanup_file

class SpotifyHandler:
    def __init__(self):
        self.spotify = None
        self.setup_spotify_client()
    
    def setup_spotify_client(self):
        """Initialize Spotify client with credentials."""
        try:
            if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=SPOTIFY_CLIENT_ID,
                    client_secret=SPOTIFY_CLIENT_SECRET
                )
                self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            else:
                print("Warning: Spotify credentials not found")
        except Exception as e:
            print(f"Error setting up Spotify client: {e}")
    
    def get_track_info(self, track_id):
        """Get track information from Spotify."""
        try:
            if not self.spotify:
                return None
            
            track = self.spotify.track(track_id)
            
            # Extract relevant information
            track_info = {
                'name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'album': track['album']['name'],
                'duration_ms': track['duration_ms'],
                'preview_url': track.get('preview_url'),
                'external_urls': track['external_urls'],
                'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'release_date': track['album']['release_date'],
                'popularity': track['popularity']
            }
            
            return track_info
        except Exception as e:
            print(f"Error getting track info: {e}")
            return None
    
    def get_album_info(self, album_id):
        """Get album information from Spotify."""
        try:
            if not self.spotify:
                return None
            
            album = self.spotify.album(album_id)
            tracks = self.spotify.album_tracks(album_id)
            
            album_info = {
                'name': album['name'],
                'artists': [artist['name'] for artist in album['artists']],
                'total_tracks': album['total_tracks'],
                'release_date': album['release_date'],
                'image_url': album['images'][0]['url'] if album['images'] else None,
                'tracks': []
            }
            
            for track in tracks['items']:
                track_info = {
                    'name': track['name'],
                    'artists': [artist['name'] for artist in track['artists']],
                    'duration_ms': track['duration_ms'],
                    'track_number': track['track_number']
                }
                album_info['tracks'].append(track_info)
            
            return album_info
        except Exception as e:
            print(f"Error getting album info: {e}")
            return None
    
    def get_playlist_info(self, playlist_id):
        """Get playlist information from Spotify."""
        try:
            if not self.spotify:
                return None
            
            playlist = self.spotify.playlist(playlist_id)
            
            playlist_info = {
                'name': playlist['name'],
                'description': playlist.get('description', ''),
                'owner': playlist['owner']['display_name'],
                'total_tracks': playlist['tracks']['total'],
                'image_url': playlist['images'][0]['url'] if playlist['images'] else None,
                'tracks': []
            }
            
            # Get all tracks (handle pagination)
            tracks = playlist['tracks']
            while tracks:
                for item in tracks['items']:
                    if item['track']:
                        track = item['track']
                        track_info = {
                            'name': track['name'],
                            'artists': [artist['name'] for artist in track['artists']],
                            'album': track['album']['name'],
                            'duration_ms': track['duration_ms']
                        }
                        playlist_info['tracks'].append(track_info)
                
                if tracks['next']:
                    tracks = self.spotify.next(tracks)
                else:
                    break
            
            return playlist_info
        except Exception as e:
            print(f"Error getting playlist info: {e}")
            return None
    
    def create_search_query(self, track_info):
        """Create a search query for YouTube based on Spotify track info."""
        if not track_info:
            return None
        
        # Create search query with artist and track name
        artists = ' '.join(track_info['artists'])
        query = f"{artists} {track_info['name']}"
        
        # Clean up the query
        query = re.sub(r'[^\w\s\-&]', '', query)
        query = re.sub(r'\s+', ' ', query).strip()
        
        return query
    
    async def download_track_from_youtube(self, track_info, quality='best'):
        """Download track from YouTube based on Spotify metadata."""
        try:
            search_query = self.create_search_query(track_info)
            if not search_query:
                return None, "Could not create search query"
            
            # Prepare filename
            artists = '_'.join(track_info['artists'])
            filename = sanitize_filename(f"{artists}_{track_info['name']}")
            output_path = os.path.join(DOWNLOAD_FOLDER, f"{filename}.%(ext)s")
            
            # YouTube-DL options for audio download
            ydl_opts = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': 'mp3',
                'audioquality': quality,
                'outtmpl': output_path,
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'default_search': 'ytsearch1:',  # Search YouTube and take first result
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search and download
                info = ydl.extract_info(search_query, download=True)
                
                if info and 'entries' in info and info['entries']:
                    entry = info['entries'][0]
                    # Find the actual downloaded file
                    downloaded_file = ydl.prepare_filename(entry).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                    
                    if os.path.exists(downloaded_file):
                        return downloaded_file, None
                    else:
                        # Try to find the file with different extension
                        base_name = os.path.splitext(downloaded_file)[0]
                        for ext in ['.mp3', '.m4a', '.webm', '.ogg']:
                            test_file = base_name + ext
                            if os.path.exists(test_file):
                                return test_file, None
                
                return None, "Download failed - file not found"
        
        except Exception as e:
            return None, f"Download error: {str(e)}"
    
    def format_track_info(self, track_info):
        """Format track information for display."""
        if not track_info:
            return "No track information available"
        
        artists = ', '.join(track_info['artists'])
        duration = self.format_duration(track_info['duration_ms'])
        
        info_text = f"""
🎵 **{track_info['name']}**
👨‍🎤 **Artist(s):** {artists}
💿 **Album:** {track_info['album']}
⏱️ **Duration:** {duration}
📅 **Release Date:** {track_info['release_date']}
⭐ **Popularity:** {track_info['popularity']}/100
        """
        
        return info_text.strip()
    
    def format_album_info(self, album_info):
        """Format album information for display."""
        if not album_info:
            return "No album information available"
        
        artists = ', '.join(album_info['artists'])
        
        info_text = f"""
💿 **{album_info['name']}**
👨‍🎤 **Artist(s):** {artists}
🎵 **Total Tracks:** {album_info['total_tracks']}
📅 **Release Date:** {album_info['release_date']}
        """
        
        return info_text.strip()
    
    def format_playlist_info(self, playlist_info):
        """Format playlist information for display."""
        if not playlist_info:
            return "No playlist information available"
        
        info_text = f"""
📋 **{playlist_info['name']}**
👤 **Owner:** {playlist_info['owner']}
🎵 **Total Tracks:** {playlist_info['total_tracks']}
📝 **Description:** {playlist_info['description'][:100]}...
        """
        
        return info_text.strip()
    
    def format_duration(self, duration_ms):
        """Format duration from milliseconds to mm:ss format."""
        seconds = duration_ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
