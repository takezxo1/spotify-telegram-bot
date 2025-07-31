import instaloader
import os
import re
from urllib.parse import urlparse
from config import DOWNLOAD_FOLDER, MAX_FILE_SIZE
from utils import sanitize_filename, cleanup_file, format_file_size

class InstagramHandler:
    def __init__(self):
        self.loader = instaloader.Instaloader(
            download_videos=True,
            download_pictures=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            dirname_pattern=DOWNLOAD_FOLDER,
            filename_pattern='{target}_{date_utc:%Y%m%d_%H%M%S}'
        )
    
    def extract_shortcode(self, url):
        """Extract Instagram shortcode from URL."""
        patterns = [
            r'instagram\.com/p/([A-Za-z0-9_-]+)',
            r'instagram\.com/reel/([A-Za-z0-9_-]+)',
            r'instagr\.am/p/([A-Za-z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def extract_story_info(self, url):
        """Extract Instagram story information from URL."""
        # Pattern for story URLs: instagram.com/stories/username/story_id
        pattern = r'instagram\.com/stories/([^/]+)/(\d+)'
        match = re.search(pattern, url)
        
        if match:
            return match.group(1), match.group(2)  # username, story_id
        
        return None, None
    
    async def get_post_info(self, url):
        """Get Instagram post information."""
        try:
            shortcode = self.extract_shortcode(url)
            if not shortcode:
                return None, "Invalid Instagram URL"
            
            # Get post information
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
            
            post_info = {
                'shortcode': shortcode,
                'owner_username': post.owner_username,
                'caption': post.caption[:200] + '...' if post.caption and len(post.caption) > 200 else post.caption or '',
                'likes': post.likes,
                'comments': post.comments,
                'date': post.date_utc.strftime('%Y-%m-%d %H:%M:%S'),
                'is_video': post.is_video,
                'video_duration': post.video_duration if post.is_video else None,
                'media_count': post.mediacount,
                'url': url,
                'typename': post.typename
            }
            
            return post_info, None
        
        except Exception as e:
            return None, f"Error getting post info: {str(e)}"
    
    async def download_post(self, url):
        """Download Instagram post (photo/video/carousel)."""
        try:
            shortcode = self.extract_shortcode(url)
            if not shortcode:
                return None, "Invalid Instagram URL"
            
            # Get post
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
            
            # Create a temporary directory for this download
            temp_dir = os.path.join(DOWNLOAD_FOLDER, f"temp_{shortcode}")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Set download directory
            original_dirname = self.loader.dirname_pattern
            self.loader.dirname_pattern = temp_dir
            
            try:
                # Download the post
                self.loader.download_post(post, target=post.owner_username)
                
                # Find downloaded files
                downloaded_files = []
                for file in os.listdir(temp_dir):
                    if file.startswith(post.owner_username):
                        file_path = os.path.join(temp_dir, file)
                        
                        # Check file size
                        if os.path.getsize(file_path) > MAX_FILE_SIZE:
                            cleanup_file(file_path)
                            continue
                        
                        # Move to main download folder with clean name
                        clean_name = sanitize_filename(f"{post.owner_username}_{shortcode}_{file}")
                        final_path = os.path.join(DOWNLOAD_FOLDER, clean_name)
                        
                        os.rename(file_path, final_path)
                        downloaded_files.append(final_path)
                
                # Clean up temp directory
                try:
                    os.rmdir(temp_dir)
                except:
                    pass
                
                return downloaded_files, None
            
            finally:
                # Restore original dirname pattern
                self.loader.dirname_pattern = original_dirname
        
        except Exception as e:
            return None, f"Download error: {str(e)}"
    
    async def download_story(self, url):
        """Download Instagram story."""
        try:
            username, story_id = self.extract_story_info(url)
            if not username or not story_id:
                return None, "Invalid Instagram story URL"
            
            # Get profile
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            # Get stories
            stories = self.loader.get_stories([profile.userid])
            
            downloaded_files = []
            
            for story in stories:
                for item in story.get_items():
                    if str(item.mediaid) == story_id:
                        # Create temp directory
                        temp_dir = os.path.join(DOWNLOAD_FOLDER, f"temp_story_{story_id}")
                        os.makedirs(temp_dir, exist_ok=True)
                        
                        # Set download directory
                        original_dirname = self.loader.dirname_pattern
                        self.loader.dirname_pattern = temp_dir
                        
                        try:
                            # Download story item
                            self.loader.download_storyitem(item, target=username)
                            
                            # Find downloaded files
                            for file in os.listdir(temp_dir):
                                if file.startswith(username):
                                    file_path = os.path.join(temp_dir, file)
                                    
                                    # Check file size
                                    if os.path.getsize(file_path) > MAX_FILE_SIZE:
                                        cleanup_file(file_path)
                                        continue
                                    
                                    # Move to main download folder
                                    clean_name = sanitize_filename(f"story_{username}_{story_id}_{file}")
                                    final_path = os.path.join(DOWNLOAD_FOLDER, clean_name)
                                    
                                    os.rename(file_path, final_path)
                                    downloaded_files.append(final_path)
                            
                            # Clean up temp directory
                            try:
                                os.rmdir(temp_dir)
                            except:
                                pass
                            
                            return downloaded_files, None
                        
                        finally:
                            self.loader.dirname_pattern = original_dirname
            
            return None, "Story not found or expired"
        
        except Exception as e:
            return None, f"Story download error: {str(e)}"
    
    async def get_reel_info(self, url):
        """Get Instagram reel information (reels are posts with video)."""
        return await self.get_post_info(url)
    
    async def download_reel(self, url):
        """Download Instagram reel (same as post download)."""
        return await self.download_post(url)
    
    def format_post_info(self, post_info):
        """Format post information for display."""
        if not post_info:
            return "No post information available"
        
        media_type = "🎥 Video" if post_info['is_video'] else "📷 Photo"
        if post_info['media_count'] > 1:
            media_type = f"📸 Carousel ({post_info['media_count']} items)"
        
        likes = self.format_number(post_info['likes'])
        comments = self.format_number(post_info['comments'])
        
        info_text = f"""
{media_type}
👤 **@{post_info['owner_username']}**
❤️ **Likes:** {likes}
💬 **Comments:** {comments}
📅 **Posted:** {post_info['date']}
📝 **Caption:** {post_info['caption']}
        """
        
        if post_info['is_video'] and post_info['video_duration']:
            duration = self.format_duration(post_info['video_duration'])
            info_text = info_text.replace(media_type, f"{media_type} ({duration})")
        
        return info_text.strip()
    
    def format_story_info(self, username, story_id):
        """Format story information for display."""
        info_text = f"""
📱 **Instagram Story**
👤 **@{username}**
🆔 **Story ID:** {story_id}
⚠️ **Note:** Stories expire after 24 hours
        """
        
        return info_text.strip()
    
    def format_duration(self, seconds):
        """Format duration from seconds to readable format."""
        if not seconds:
            return "Unknown"
        
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        
        if minutes > 0:
            return f"{minutes}:{seconds:02d}"
        else:
            return f"0:{seconds:02d}"
    
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
    
    def detect_instagram_content_type(self, url):
        """Detect the type of Instagram content from URL."""
        if '/stories/' in url:
            return 'story'
        elif '/reel/' in url:
            return 'reel'
        elif '/p/' in url:
            return 'post'
        else:
            return 'unknown'