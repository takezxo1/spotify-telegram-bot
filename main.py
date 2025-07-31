#!/usr/bin/env python3
"""
Telegram bot that downloads YouTube audio from Spotify song links.
"""

import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import Config
from bot_handlers import BotHandlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Initialize bot handlers
    bot_handlers = BotHandlers()
    
    # Register handlers
    application.add_handler(CommandHandler("start", bot_handlers.start))
    application.add_handler(CommandHandler("help", bot_handlers.help_command))
    application.add_handler(CallbackQueryHandler(bot_handlers.button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handlers.handle_message))
    
    # Start the bot
    logger.info("Starting Telegram bot...")
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == '__main__':
    main()
