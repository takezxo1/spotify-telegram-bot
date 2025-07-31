"""
Telegram bot message handlers.
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from spotify_handler import SpotifyHandler
from youtube_handler import YouTubeHandler
from utils import clean_filename, format_file_size

logger = logging.getLogger(__name__)

class BotHandlers:
    """Handles Telegram bot interactions."""
    
    def __init__(self):
        """Initialize handlers."""
        self.spotify = SpotifyHandler()
        self.youtube = YouTubeHandler()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_message = """🎵 **Welcome to SpotifyDL Pro** 🎵

Transform your Spotify discoveries into high-quality MP3 files instantly!

✨ **What makes us special:**
• Lightning-fast downloads in seconds
• Crystal-clear 192kbps audio quality  
• Smart track recognition technology
• Automatic metadata tagging
• Zero registration required

🎯 **How it works:**
Just paste any Spotify track link and watch the magic happen!

🚀 **Ready to get started?**"""
        
        # Create attractive buttons
        keyboard = [
            [InlineKeyboardButton("📖 How to Use", callback_data='help'),
             InlineKeyboardButton("🎵 Try Demo", callback_data='demo')],
            [InlineKeyboardButton("⭐ Rate Us", callback_data='rate'),
             InlineKeyboardButton("📢 Share Bot", callback_data='share')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(
                welcome_message, 
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = """🎯 **SpotifyDL Pro - Quick Guide**

**Step 1: Find Your Song** 🔍
• Open Spotify (app or web)
• Navigate to any track you love
• Tap the share button (•••)
• Copy the link

**Step 2: Send to SpotifyDL** 📱
• Paste the Spotify link here
• Our AI instantly recognizes the track
• Sit back and relax!

**Step 3: Enjoy Your Music** 🎧
• Receive high-quality MP3 in seconds
• Complete with artist, title & album info
• Ready to play anywhere, anytime

**Supported Links:**
✅ `https://open.spotify.com/track/...`
✅ `https://spotify.com/track/...`  
✅ `spotify:track:...`

**Features:**
🎵 192kbps premium quality
📱 Works with any Spotify track
⚡ Lightning-fast processing
🎯 100% accurate track matching
📦 Up to 50MB file size

**Ready to download?** Just paste a Spotify link below! 👇"""
        
        keyboard = [
            [InlineKeyboardButton("🏠 Back to Home", callback_data='start'),
             InlineKeyboardButton("🎵 Try Now", callback_data='demo')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(
                help_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages."""
        if not update.message or not update.message.text:
            return
            
        message_text = update.message.text
        
        # Check if message contains Spotify URL
        if not self.spotify.is_spotify_url(message_text):
            error_keyboard = [
                [InlineKeyboardButton("📖 How to Get Spotify Links", callback_data='help')],
                [InlineKeyboardButton("🎵 Try Demo Link", callback_data='demo')]
            ]
            error_markup = InlineKeyboardMarkup(error_keyboard)
            
            await update.message.reply_text(
                "❌ **Invalid Link Detected**\n\n"
                "Please send a valid Spotify track link.\n"
                "Example: `https://open.spotify.com/track/...`",
                reply_markup=error_markup,
                parse_mode='Markdown'
            )
            return
        
        # Send processing message with progress
        processing_msg = await update.message.reply_text(
            "🔄 **Processing your request...**\n"
            "🎵 Analyzing Spotify track data...",
            parse_mode='Markdown'
        )
        downloaded_file = None
        
        try:
            # Process Spotify URL
            spotify_data = self.spotify.process_spotify_url(message_text)
            if not spotify_data:
                await processing_msg.edit_text(
                    "❌ **Unable to Process Link**\n\n"
                    "The Spotify link appears to be invalid or the track is not available.\n"
                    "Please try with a different Spotify track link.",
                    parse_mode='Markdown'
                )
                return
            
            track_info = spotify_data['track_info']
            search_query = spotify_data['search_query']
            
            # Update message with found track info
            await processing_msg.edit_text(
                f"✅ **Track Identified Successfully!**\n\n"
                f"🎵 **{track_info['name']}**\n"
                f"👤 **{', '.join(track_info['artists'])}**\n"
                f"💿 **{track_info['album']}**\n\n"
                f"🔄 Preparing high-quality download...",
                parse_mode='Markdown'
            )
            
            # Process and download track
            downloaded_file, error = self.youtube.process_download_request(search_query, track_info)
            
            if error or not downloaded_file:
                await processing_msg.edit_text(
                    f"❌ **Download Failed**\n\n"
                    f"{error or 'Unable to process this track at the moment.'}\n"
                    f"Please try again with a different Spotify link.",
                    parse_mode='Markdown'
                )
                return
            
            # Check file size
            file_size = os.path.getsize(downloaded_file)
            if file_size > 50 * 1024 * 1024:  # 50MB limit
                await processing_msg.edit_text(
                    f"❌ **File Too Large**\n\n"
                    f"This track ({format_file_size(file_size)}) exceeds Telegram's 50MB limit.\n"
                    f"Please try a shorter track or different version.",
                    parse_mode='Markdown'
                )
                # Clean up file
                os.remove(downloaded_file)
                return
            
            # Update message
            await processing_msg.edit_text(
                "📤 **Almost Ready!**\n"
                "Finalizing your premium MP3 file...",
                parse_mode='Markdown'
            )
            
            # Generate clean filename
            clean_name = clean_filename(f"{', '.join(track_info['artists'])} - {track_info['name']}")
            
            # Send audio file
            with open(downloaded_file, 'rb') as audio_file:
                if update.message:
                    await update.message.reply_audio(
                        audio=audio_file,
                        filename=f"{clean_name}.mp3",
                        title=track_info['name'],
                        performer=', '.join(track_info['artists']),
                        duration=track_info.get('duration_ms', 0) // 1000
                    )
            
            # Delete processing message
            await processing_msg.delete()
            
            # Send success message with action buttons
            success_keyboard = [
                [InlineKeyboardButton("🎵 Download Another", callback_data='start')],
                [InlineKeyboardButton("⭐ Rate SpotifyDL", callback_data='rate'),
                 InlineKeyboardButton("📢 Share Bot", callback_data='share')]
            ]
            success_markup = InlineKeyboardMarkup(success_keyboard)
            
            if update.message:
                await update.message.reply_text(
                    f"🎉 **Download Complete!**\n\n"
                    f"🎵 **{track_info['name']}**\n"
                    f"👤 **{', '.join(track_info['artists'])}**\n"
                    f"💿 **{track_info['album']}**\n\n"
                    f"✨ Enjoy your premium quality MP3!\n"
                    f"💝 Thank you for using SpotifyDL Pro",
                    reply_markup=success_markup,
                    parse_mode='Markdown'
                )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await processing_msg.edit_text(
                "❌ **Temporary Service Issue**\n\n"
                "We're experiencing high demand right now.\n"
                "Please try again in a few moments!",
                parse_mode='Markdown'
            )
        
        finally:
            # Clean up downloaded file
            try:
                if downloaded_file and os.path.exists(downloaded_file):
                    os.remove(downloaded_file)
            except Exception as e:
                logger.error(f"Error cleaning up file: {e}")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks."""
        query = update.callback_query
        if not query:
            logger.error("No callback query found in update")
            return
        
        logger.info(f"Button clicked: {query.data}")
        
        try:
            await query.answer()
        except Exception as e:
            logger.error(f"Error answering callback query: {e}")
            return
        
        if query.data == 'help':
            # Create a modified update object for help command
            help_message = """🎯 **SpotifyDL Pro - Quick Guide**

**Step 1: Find Your Song** 🔍
• Open Spotify (app or web)
• Navigate to any track you love
• Tap the share button (•••)
• Copy the link

**Step 2: Send to SpotifyDL** 📱
• Paste the Spotify link here
• Our AI instantly recognizes the track
• Sit back and relax!

**Step 3: Enjoy Your Music** 🎧
• Receive high-quality MP3 in seconds
• Complete with artist, title & album info
• Ready to play anywhere, anytime

**Supported Links:**
✅ `https://open.spotify.com/track/...`
✅ `https://spotify.com/track/...`  
✅ `spotify:track:...`

**Features:**
🎵 192kbps premium quality
📱 Works with any Spotify track
⚡ Lightning-fast processing
🎯 100% accurate track matching
📦 Up to 50MB file size

**Ready to download?** Just paste a Spotify link below! 👇"""
            
            keyboard = [
                [InlineKeyboardButton("🏠 Back to Home", callback_data='start'),
                 InlineKeyboardButton("🎵 Try Now", callback_data='demo')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await query.edit_message_text(
                    help_message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error editing message for help: {e}")
        elif query.data == 'demo':
            # Rotating demo songs - popular hits
            demo_songs = [
                ("Billie Eilish - BIRDS OF A FEATHER", "https://open.spotify.com/track/6dOtVTDdiauQNBQEDOtlAB"),
                ("Sabrina Carpenter - Espresso", "https://open.spotify.com/track/2qSkIjg1o9h3YT9RAgYN75"),
                ("Lady Gaga & Bruno Mars - Die With A Smile", "https://open.spotify.com/track/2plbrEY59IikOBgBGLjaoe"),
                ("The Weeknd - Blinding Lights", "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b"),
                ("Harry Styles - As It Was", "https://open.spotify.com/track/4LRPiXqCikLlN15c3yImP7"),
                ("Wiz Khalifa - See You Again (feat. Charlie Puth)", "https://open.spotify.com/track/6UVjo42dT0yQXX0ogxeR9s"),
            ]
            
            # Select random song
            import random
            selected_song, selected_url = random.choice(demo_songs)
            
            demo_text = f"""🎵 **Try with this demo Spotify link:**

*{selected_song}*
`{selected_url}`

Just copy and paste the link above to see SpotifyDL Pro in action! 🚀"""
            
            keyboard = [
                [InlineKeyboardButton("🏠 Back to Home", callback_data='start')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await query.edit_message_text(
                    demo_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error editing message for demo: {e}")
        elif query.data == 'rate':
            rate_text = """⭐ **Rate SpotifyDL Pro**

Thank you for using our service! Your feedback helps us improve.

Please rate us on:
• Speed of download
• Audio quality  
• User experience
• Overall satisfaction

Share your experience with friends and family! 💝"""
            
            keyboard = [
                [InlineKeyboardButton("📢 Share Bot", callback_data='share')],
                [InlineKeyboardButton("🏠 Back to Home", callback_data='start')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await query.edit_message_text(
                    rate_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error editing message for rate: {e}")
        elif query.data == 'share':
            share_text = """📢 **Share SpotifyDL Pro**

Love our service? Spread the word!

📱 **Share this bot with friends:**
`@SAN_Filebot (SpotifyDLProBot)`

💬 **Tell them about:**
• Lightning-fast downloads
• Premium audio quality
• Zero registration required
• 100% free to use

Thank you for helping us grow! 🚀"""
            
            keyboard = [
                [InlineKeyboardButton("⭐ Rate Us", callback_data='rate')],
                [InlineKeyboardButton("🏠 Back to Home", callback_data='start')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await query.edit_message_text(
                    share_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error editing message for share: {e}")
        elif query.data == 'start':
            # Recreate start message for callback
            welcome_message = """🎵 **Welcome to SpotifyDL Pro** 🎵

Transform your Spotify discoveries into high-quality MP3 files instantly!

✨ **What makes us special:**
• Lightning-fast downloads in seconds
• Crystal-clear 192kbps audio quality  
• Smart track recognition technology
• Automatic metadata tagging
• Zero registration required

🎯 **How it works:**
Just paste any Spotify track link and watch the magic happen!

🚀 **Ready to get started?**"""
            
            # Create attractive buttons
            keyboard = [
                [InlineKeyboardButton("📖 How to Use", callback_data='help'),
                 InlineKeyboardButton("🎵 Try Demo", callback_data='demo')],
                [InlineKeyboardButton("⭐ Rate Us", callback_data='rate'),
                 InlineKeyboardButton("📢 Share Bot", callback_data='share')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await query.edit_message_text(
                    welcome_message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error editing message for start: {e}")
