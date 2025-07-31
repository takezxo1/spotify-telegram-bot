# Spotify to MP3 Telegram Bot

A Telegram bot that downloads audio from YouTube when users share Spotify song links. The bot extracts metadata from Spotify tracks, searches for corresponding videos on YouTube, and downloads them as MP3 files.

## Features

- 🎵 Download any Spotify track as high-quality MP3
- 📱 Professional "SpotifyDL Pro" interface
- ⚡ Lightning-fast processing
- 🎯 Accurate track matching
- 📦 Up to 50MB file support
- 🔄 Rotating demo system with popular hits

## Environment Variables

You need to set these environment variables:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

## Deployment Options

### 1. Railway (Recommended for bots)
- Create account at railway.app
- Connect your GitHub repo
- Add environment variables
- Deploy automatically

### 2. Heroku
- Create a Heroku app
- Add Python buildpack
- Set environment variables
- Deploy from GitHub

### 3. VPS/Server
- Clone the repository
- Install Python 3.11+
- Install ffmpeg: `sudo apt install ffmpeg`
- Install dependencies: `pip install -r requirements_github.txt`
- Set environment variables
- Run: `python main.py`

## Getting API Keys

### Telegram Bot Token
1. Message @BotFather on Telegram
2. Create a new bot with `/newbot`
3. Copy the token

### Spotify API Keys
1. Go to https://developer.spotify.com/dashboard
2. Create a new app
3. Copy Client ID and Client Secret

## Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements_github.txt`
3. Install ffmpeg on your system
4. Set environment variables
5. Run: `python main.py`

## Project Structure

- `main.py` - Entry point and bot initialization
- `bot_handlers.py` - Telegram bot message and callback handlers
- `spotify_handler.py` - Spotify API integration
- `youtube_handler.py` - YouTube search and download
- `config.py` - Configuration settings
- `utils.py` - Utility functions

## Notes

- This bot requires ffmpeg for audio conversion
- Designed to run as a long-running process
- Uses polling method (no webhooks needed)
- Professional "SpotifyDL Pro" branding (no YouTube mentions)