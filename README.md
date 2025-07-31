# 🎵 Premium Media Downloader Bot

A powerful Telegram bot that can download content from **Spotify**, **YouTube**, and **Instagram** with a beautiful, premium interface using inline keyboards.

## ✨ Features

### 🎶 Spotify Support
- **Track Downloads**: Fetches metadata from Spotify and searches YouTube for the exact song
- **Album/Playlist Info**: Shows detailed information (downloads coming soon)
- **High-Quality Audio**: Downloads in MP3 format with metadata

### 📹 YouTube Support
- **Video Downloads**: Multiple quality options (144p to 1080p)
- **Audio Downloads**: Extract audio in various bitrates (64kbps to 320kbps)
- **Format Selection**: Choose between MP4 (video) or MP3 (audio)
- **Progress Tracking**: Real-time download progress updates

### 📱 Instagram Support
- **Posts**: Download photos and videos from regular posts
- **Reels**: Download Instagram Reels
- **Stories**: Download stories (expires after 24 hours)
- **Carousel Posts**: Download all media from multi-image/video posts

### 🎨 Premium UI Features
- **Inline Keyboards**: Beautiful button-based interface
- **Real-time Updates**: Progress indicators and status messages
- **Quality Selection**: Interactive quality and format selection
- **Error Handling**: Detailed error messages with helpful suggestions
- **File Size Limits**: Automatic handling of Telegram's 50MB limit

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Spotify API credentials (from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd telegram-media-downloader-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   SPOTIFY_CLIENT_ID=your_spotify_client_id_here
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

## 🔧 Configuration

### Getting API Keys

#### Telegram Bot Token
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token provided

#### Spotify API Credentials
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in the app details
5. Copy the Client ID and Client Secret

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | ✅ Yes |
| `SPOTIFY_CLIENT_ID` | Spotify application client ID | ✅ Yes |
| `SPOTIFY_CLIENT_SECRET` | Spotify application client secret | ✅ Yes |

## 📖 Usage

### Basic Commands
- `/start` - Start the bot and see welcome message
- `/help` - Show help information and supported links

### Supported Link Formats

#### Spotify
- `https://open.spotify.com/track/...`
- `https://open.spotify.com/album/...`
- `https://open.spotify.com/playlist/...`
- `spotify:track:...`

#### YouTube
- `https://youtube.com/watch?v=...`
- `https://youtu.be/...`
- `https://youtube.com/playlist?list=...`
- `https://youtube.com/shorts/...`

#### Instagram
- `https://instagram.com/p/...` (Posts)
- `https://instagram.com/reel/...` (Reels)
- `https://instagram.com/stories/...` (Stories)

### How It Works

1. **Send a Link**: Simply paste any supported link to the bot
2. **Choose Options**: Use the interactive buttons to select format and quality
3. **Download**: The bot processes and sends your file
4. **Enjoy**: Receive your media with proper metadata and captions

## 🏗️ Project Structure

```
telegram-media-downloader-bot/
├── bot.py                 # Main bot application
├── config.py             # Configuration and settings
├── utils.py              # Utility functions and UI components
├── spotify_handler.py    # Spotify API and YouTube search logic
├── youtube_handler.py    # YouTube download functionality
├── instagram_handler.py  # Instagram download functionality
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── README.md            # This file
└── downloads/           # Downloaded files (created automatically)
```

## 🛠️ Technical Details

### Dependencies
- **python-telegram-bot**: Telegram Bot API wrapper
- **spotipy**: Spotify Web API wrapper
- **yt-dlp**: YouTube and video platform downloader
- **instaloader**: Instagram content downloader
- **python-dotenv**: Environment variable management

### How Spotify Downloads Work
Since direct Spotify downloads would violate copyright, the bot:
1. Fetches track metadata using Spotify's API
2. Creates a search query with artist and track name
3. Searches YouTube for the best matching video
4. Downloads the audio from YouTube
5. Provides it to the user as if it came from Spotify

This approach is **legal** and **ethical** as it:
- Uses official Spotify API for metadata only
- Downloads from YouTube (which allows downloads via their API)
- Doesn't circumvent any DRM or protection systems
- Provides the same music the user could find manually

### File Size Handling
- Maximum file size: 50MB (Telegram limit)
- Automatic quality adjustment for large files
- Progress tracking for long downloads
- Automatic cleanup of temporary files

## 🔒 Privacy & Security

- **No Data Storage**: The bot doesn't store user data or downloaded files
- **Temporary Files**: All downloads are cleaned up after sending
- **Session Management**: User sessions are memory-only and temporary
- **API Compliance**: All integrations follow platform terms of service

## 🚨 Limitations

- **File Size**: Limited to 50MB per file (Telegram restriction)
- **Region Restrictions**: Some content may not be available in all regions
- **Rate Limits**: Subject to API rate limits from various platforms
- **Story Expiration**: Instagram stories expire after 24 hours

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is for educational purposes. Please respect copyright laws and platform terms of service.

## ⚠️ Disclaimer

This bot is for personal use only. Users are responsible for complying with:
- YouTube's Terms of Service
- Instagram's Terms of Service
- Spotify's Terms of Service
- Local copyright laws

The bot creator is not responsible for any misuse of this software.

## 🆘 Support

If you encounter any issues:
1. Check the logs for error messages
2. Verify your API credentials are correct
3. Ensure all dependencies are installed
4. Check that the download folder has write permissions

For additional help, please open an issue on GitHub.

---

**Made with ❤️ for the community**