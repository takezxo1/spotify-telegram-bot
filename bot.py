import asyncio
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode

# Import our handlers
from spotify_handler import SpotifyHandler
from youtube_handler import YouTubeHandler
from instagram_handler import InstagramHandler
from utils import (
    detect_link_type, create_quality_keyboard, create_main_menu_keyboard,
    create_spotify_keyboard, create_instagram_keyboard, extract_spotify_id,
    ensure_download_folder, cleanup_file
)
from config import (
    TELEGRAM_BOT_TOKEN, WELCOME_MESSAGE, HELP_MESSAGE, DOWNLOAD_FOLDER
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MediaDownloaderBot:
    def __init__(self):
        self.spotify_handler = SpotifyHandler()
        self.youtube_handler = YouTubeHandler()
        self.instagram_handler = InstagramHandler()
        
        # Store user sessions for download context
        self.user_sessions = {}
        
        # Ensure download folder exists
        ensure_download_folder()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        keyboard = create_main_menu_keyboard()
        
        await update.message.reply_text(
            WELCOME_MESSAGE,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        keyboard = create_main_menu_keyboard()
        
        await update.message.reply_text(
            HELP_MESSAGE,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages with links."""
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        # Detect link type
        link_type = detect_link_type(message_text)
        
        if link_type == 'unknown':
            keyboard = create_main_menu_keyboard()
            await update.message.reply_text(
                "❌ **Unsupported Link**\n\nPlease send a valid Spotify, YouTube, or Instagram link.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
            return
        
        # Store the URL in user session
        self.user_sessions[user_id] = {
            'url': message_text,
            'link_type': link_type
        }
        
        # Handle different link types
        if link_type == 'spotify':
            await self.handle_spotify_link(update, context, message_text)
        elif link_type == 'youtube':
            await self.handle_youtube_link(update, context, message_text)
        elif link_type == 'instagram':
            await self.handle_instagram_link(update, context, message_text)
    
    async def handle_spotify_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
        """Handle Spotify links."""
        # Show processing message
        processing_msg = await update.message.reply_text(
            "🎵 **Processing Spotify Link...**\n\n⏳ Fetching track information...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Extract Spotify ID and type
            content_type, spotify_id = extract_spotify_id(url)
            
            if not content_type or not spotify_id:
                await processing_msg.edit_text(
                    "❌ **Error**\n\nInvalid Spotify link format.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Get track/album/playlist info
            if content_type == 'track':
                info = self.spotify_handler.get_track_info(spotify_id)
                if info:
                    formatted_info = self.spotify_handler.format_track_info(info)
                    keyboard = create_spotify_keyboard()
                    
                    # Store track info in session
                    user_id = update.effective_user.id
                    self.user_sessions[user_id]['track_info'] = info
                    
                    await processing_msg.edit_text(
                        formatted_info,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=keyboard
                    )
                else:
                    await processing_msg.edit_text(
                        "❌ **Error**\n\nCould not fetch track information.",
                        parse_mode=ParseMode.MARKDOWN
                    )
            
            elif content_type == 'album':
                info = self.spotify_handler.get_album_info(spotify_id)
                if info:
                    formatted_info = self.spotify_handler.format_album_info(info)
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("ℹ️ Album not supported yet", callback_data="not_supported")],
                        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
                    ])
                    
                    await processing_msg.edit_text(
                        formatted_info + "\n\n⚠️ **Album downloads coming soon!**",
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=keyboard
                    )
                else:
                    await processing_msg.edit_text(
                        "❌ **Error**\n\nCould not fetch album information.",
                        parse_mode=ParseMode.MARKDOWN
                    )
            
            elif content_type == 'playlist':
                info = self.spotify_handler.get_playlist_info(spotify_id)
                if info:
                    formatted_info = self.spotify_handler.format_playlist_info(info)
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("ℹ️ Playlists not supported yet", callback_data="not_supported")],
                        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
                    ])
                    
                    await processing_msg.edit_text(
                        formatted_info + "\n\n⚠️ **Playlist downloads coming soon!**",
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=keyboard
                    )
                else:
                    await processing_msg.edit_text(
                        "❌ **Error**\n\nCould not fetch playlist information.",
                        parse_mode=ParseMode.MARKDOWN
                    )
        
        except Exception as e:
            logger.error(f"Error handling Spotify link: {e}")
            await processing_msg.edit_text(
                "❌ **Error**\n\nFailed to process Spotify link.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_youtube_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
        """Handle YouTube links."""
        # Show processing message
        processing_msg = await update.message.reply_text(
            "📹 **Processing YouTube Link...**\n\n⏳ Fetching video information...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Get video info
            video_info, error = await self.youtube_handler.get_video_info(url)
            
            if error:
                await processing_msg.edit_text(
                    f"❌ **Error**\n\n{error}",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Format and display video info
            formatted_info = self.youtube_handler.format_video_info(video_info)
            
            # Create quality selection keyboard
            keyboard = create_quality_keyboard('youtube', 'video')
            
            # Store video info in session
            user_id = update.effective_user.id
            self.user_sessions[user_id]['video_info'] = video_info
            
            await processing_msg.edit_text(
                formatted_info + "\n\n🎯 **Choose format and quality:**",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
        
        except Exception as e:
            logger.error(f"Error handling YouTube link: {e}")
            await processing_msg.edit_text(
                "❌ **Error**\n\nFailed to process YouTube link.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_instagram_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
        """Handle Instagram links."""
        # Show processing message
        processing_msg = await update.message.reply_text(
            "📱 **Processing Instagram Link...**\n\n⏳ Fetching post information...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Detect content type
            content_type = self.instagram_handler.detect_instagram_content_type(url)
            
            if content_type == 'story':
                username, story_id = self.instagram_handler.extract_story_info(url)
                if username and story_id:
                    formatted_info = self.instagram_handler.format_story_info(username, story_id)
                    keyboard = create_instagram_keyboard()
                    
                    await processing_msg.edit_text(
                        formatted_info,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=keyboard
                    )
                else:
                    await processing_msg.edit_text(
                        "❌ **Error**\n\nInvalid Instagram story link.",
                        parse_mode=ParseMode.MARKDOWN
                    )
            
            else:  # post or reel
                post_info, error = await self.instagram_handler.get_post_info(url)
                
                if error:
                    await processing_msg.edit_text(
                        f"❌ **Error**\n\n{error}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    return
                
                formatted_info = self.instagram_handler.format_post_info(post_info)
                keyboard = create_instagram_keyboard()
                
                # Store post info in session
                user_id = update.effective_user.id
                self.user_sessions[user_id]['post_info'] = post_info
                
                await processing_msg.edit_text(
                    formatted_info,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
        
        except Exception as e:
            logger.error(f"Error handling Instagram link: {e}")
            await processing_msg.edit_text(
                "❌ **Error**\n\nFailed to process Instagram link.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        data = query.data
        
        # Handle different callback types
        if data == "help":
            await query.edit_message_text(
                HELP_MESSAGE,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=create_main_menu_keyboard()
            )
        
        elif data == "about":
            about_text = """
🤖 **Premium Media Downloader Bot**

✨ **Features:**
• High-quality downloads
• Multiple format support
• Fast processing
• Beautiful interface

🔧 **Powered by:**
• yt-dlp for YouTube
• Spotify Web API
• Instaloader for Instagram

💡 **Tips:**
• Use best quality for optimal results
• Large files may take longer to process
• Some content may be region-restricted

🚀 **Version:** 1.0.0
            """
            await query.edit_message_text(
                about_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=create_main_menu_keyboard()
            )
        
        elif data == "supported_links":
            await query.edit_message_text(
                HELP_MESSAGE,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=create_main_menu_keyboard()
            )
        
        elif data == "cancel":
            # Clear user session
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]
            
            await query.edit_message_text(
                "❌ **Cancelled**\n\nOperation cancelled. Send me another link to get started!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=create_main_menu_keyboard()
            )
        
        elif data.startswith("format_"):
            await self.handle_format_selection(query, user_id, data)
        
        elif data.startswith("quality_") or data.startswith("audio_"):
            await self.handle_quality_selection(query, user_id, data)
        
        elif data == "spotify_download":
            await self.handle_spotify_download(query, user_id)
        
        elif data == "spotify_info":
            # Already showing info, just acknowledge
            await query.answer("ℹ️ Track information is already displayed above!")
        
        elif data == "instagram_download":
            await self.handle_instagram_download(query, user_id)
        
        elif data == "instagram_info":
            await query.answer("ℹ️ Post information is already displayed above!")
        
        elif data == "not_supported":
            await query.answer("⚠️ This feature is coming soon!", show_alert=True)
    
    async def handle_format_selection(self, query, user_id: int, data: str):
        """Handle format selection (MP4/MP3)."""
        if user_id not in self.user_sessions:
            await query.edit_message_text("❌ Session expired. Please send the link again.")
            return
        
        format_type = data.split("_")[1]  # mp4 or mp3
        self.user_sessions[user_id]['format'] = format_type
        
        # Show quality selection for the chosen format
        if format_type == 'mp3':
            keyboard = create_quality_keyboard('youtube', 'audio')
            text = "🎵 **MP3 Selected**\n\nChoose audio quality:"
        else:
            keyboard = create_quality_keyboard('youtube', 'video')
            text = "📹 **MP4 Selected**\n\nChoose video quality:"
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
    
    async def handle_quality_selection(self, query, user_id: int, data: str):
        """Handle quality selection and start download."""
        if user_id not in self.user_sessions:
            await query.edit_message_text("❌ Session expired. Please send the link again.")
            return
        
        session = self.user_sessions[user_id]
        quality = data.split("_", 1)[1]  # Remove prefix (quality_ or audio_)
        
        # Determine format
        if 'format' in session:
            format_type = session['format']
        else:
            format_type = 'mp3' if data.startswith('audio_') else 'mp4'
        
        # Start download
        await self.start_youtube_download(query, user_id, quality, format_type)
    
    async def start_youtube_download(self, query, user_id: int, quality: str, format_type: str):
        """Start YouTube download process."""
        session = self.user_sessions[user_id]
        url = session['url']
        
        # Show download progress
        await query.edit_message_text(
            f"⬇️ **Starting Download...**\n\n🎯 **Format:** {format_type.upper()}\n🌟 **Quality:** {quality}\n\n⏳ Please wait...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
                         # Create progress callback
             progress_callback = self.youtube_handler.create_progress_callback(
                 query.message.chat_id, query.message.message_id, query.bot
             )
            
            # Download the file
            downloaded_file, error = await self.youtube_handler.download_video(
                url, quality, format_type, progress_callback
            )
            
            if error:
                await query.edit_message_text(
                    f"❌ **Download Failed**\n\n{error}",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            if not downloaded_file or not os.path.exists(downloaded_file):
                await query.edit_message_text(
                    "❌ **Download Failed**\n\nFile not found after download.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Send the file
            await query.edit_message_text(
                "📤 **Uploading...**\n\nSending your file...",
                parse_mode=ParseMode.MARKDOWN
            )
            
                         # Send file based on type
             if format_type == 'mp3':
                 with open(downloaded_file, 'rb') as audio_file:
                     await query.bot.send_audio(
                         chat_id=query.message.chat_id,
                         audio=audio_file,
                         caption=f"🎵 **Downloaded from YouTube**\n\n🌟 Quality: {quality}",
                         parse_mode=ParseMode.MARKDOWN
                     )
             else:
                 with open(downloaded_file, 'rb') as video_file:
                     await query.bot.send_video(
                         chat_id=query.message.chat_id,
                         video=video_file,
                         caption=f"📹 **Downloaded from YouTube**\n\n🌟 Quality: {quality}",
                         parse_mode=ParseMode.MARKDOWN
                     )
            
            # Clean up
            cleanup_file(downloaded_file)
            
            # Success message
            await query.edit_message_text(
                "✅ **Download Complete!**\n\nYour file has been sent successfully!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=create_main_menu_keyboard()
            )
        
        except Exception as e:
            logger.error(f"Error downloading YouTube video: {e}")
            await query.edit_message_text(
                "❌ **Download Failed**\n\nAn unexpected error occurred.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_spotify_download(self, query, user_id: int):
        """Handle Spotify download (via YouTube search)."""
        if user_id not in self.user_sessions or 'track_info' not in self.user_sessions[user_id]:
            await query.edit_message_text("❌ Session expired. Please send the link again.")
            return
        
        track_info = self.user_sessions[user_id]['track_info']
        
        # Show download progress
        await query.edit_message_text(
            "🎵 **Downloading from Spotify...**\n\n🔍 Searching on YouTube...\n⏳ Please wait...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Download track via YouTube search
            downloaded_file, error = await self.spotify_handler.download_track_from_youtube(track_info)
            
            if error:
                await query.edit_message_text(
                    f"❌ **Download Failed**\n\n{error}",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            if not downloaded_file or not os.path.exists(downloaded_file):
                await query.edit_message_text(
                    "❌ **Download Failed**\n\nFile not found after download.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Send the audio file
            await query.edit_message_text(
                "📤 **Uploading...**\n\nSending your audio file...",
                parse_mode=ParseMode.MARKDOWN
            )
            
                         with open(downloaded_file, 'rb') as audio_file:
                 artists = ', '.join(track_info['artists'])
                 caption = f"🎵 **{track_info['name']}**\n👨‍🎤 **{artists}**\n\n💿 From Spotify (via YouTube)"
                 
                 await query.bot.send_audio(
                     chat_id=query.message.chat_id,
                     audio=audio_file,
                     caption=caption,
                     parse_mode=ParseMode.MARKDOWN,
                     title=track_info['name'],
                     performer=artists
                 )
            
            # Clean up
            cleanup_file(downloaded_file)
            
            # Success message
            await query.edit_message_text(
                "✅ **Download Complete!**\n\nYour Spotify track has been downloaded and sent!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=create_main_menu_keyboard()
            )
        
        except Exception as e:
            logger.error(f"Error downloading Spotify track: {e}")
            await query.edit_message_text(
                "❌ **Download Failed**\n\nAn unexpected error occurred.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_instagram_download(self, query, user_id: int):
        """Handle Instagram download."""
        if user_id not in self.user_sessions:
            await query.edit_message_text("❌ Session expired. Please send the link again.")
            return
        
        session = self.user_sessions[user_id]
        url = session['url']
        
        # Show download progress
        await query.edit_message_text(
            "📱 **Downloading from Instagram...**\n\n⏳ Please wait...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Detect content type and download
            content_type = self.instagram_handler.detect_instagram_content_type(url)
            
            if content_type == 'story':
                downloaded_files, error = await self.instagram_handler.download_story(url)
            else:
                downloaded_files, error = await self.instagram_handler.download_post(url)
            
            if error:
                await query.edit_message_text(
                    f"❌ **Download Failed**\n\n{error}",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            if not downloaded_files:
                await query.edit_message_text(
                    "❌ **Download Failed**\n\nNo files were downloaded.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Send files
            await query.edit_message_text(
                f"📤 **Uploading...**\n\nSending {len(downloaded_files)} file(s)...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            for file_path in downloaded_files:
                if os.path.exists(file_path):
                    file_ext = os.path.splitext(file_path)[1].lower()
                    
                                         with open(file_path, 'rb') as media_file:
                         if file_ext in ['.jpg', '.jpeg', '.png']:
                             await query.bot.send_photo(
                                 chat_id=query.message.chat_id,
                                 photo=media_file,
                                 caption="📱 **Downloaded from Instagram**",
                                 parse_mode=ParseMode.MARKDOWN
                             )
                         elif file_ext in ['.mp4', '.mov', '.avi']:
                             await query.bot.send_video(
                                 chat_id=query.message.chat_id,
                                 video=media_file,
                                 caption="📱 **Downloaded from Instagram**",
                                 parse_mode=ParseMode.MARKDOWN
                             )
                         else:
                             await query.bot.send_document(
                                 chat_id=query.message.chat_id,
                                 document=media_file,
                                 caption="📱 **Downloaded from Instagram**",
                                 parse_mode=ParseMode.MARKDOWN
                             )
                    
                    # Clean up
                    cleanup_file(file_path)
            
            # Success message
            await query.edit_message_text(
                "✅ **Download Complete!**\n\nYour Instagram content has been downloaded and sent!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=create_main_menu_keyboard()
            )
        
        except Exception as e:
            logger.error(f"Error downloading Instagram content: {e}")
            await query.edit_message_text(
                "❌ **Download Failed**\n\nAn unexpected error occurred.",
                parse_mode=ParseMode.MARKDOWN
            )

def main():
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    # Create bot instance
    bot = MediaDownloaderBot()
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    application.add_handler(CallbackQueryHandler(bot.handle_callback_query))
    
    # Start the bot
    print("🤖 Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()