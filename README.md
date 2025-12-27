# 🤖 irProLink Bot - Python Version 6.0.0 (2026)

A powerful Telegram bot for downloading and uploading files from URLs with advanced features.

## 🚀 Features

### Core Features
- **File Upload**: Upload files up to 2GB from direct URLs
- **Multi-language Support**: English and Persian interface
- **Spoiler Mode**: Images and videos are sent with spoiler effect
- **Smart Caption**: Customizable file details display
- **Rate Limiting**: Prevent abuse with configurable limits
- **Admin Panel**: Full control for administrators

### Advanced Features
- **CDN Support**: Optional CDN integration for better performance
- **Auto Update**: Update bot from repository with admin commands
- **Statistics**: Detailed usage statistics and user tracking
- **Broadcast System**: Send messages to all users
- **Security**: File extension filtering and anti-spam measures

## 📦 Installation

### Quick Install
```bash
# Clone repository
git clone https://github.com/mhd1386/prolink.git
cd prolink-python

# Run installation script
python install.py

# Edit .env file
nano .env

# Start the bot
./start.sh
```

### Manual Installation
1. Install Python 3.6+
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure
4. Run: `python main.py`

## ⚙️ Configuration

### Environment Variables (.env)
```env
# Required
BOT_TOKEN=your_bot_token_here

# Optional
SUPPORT_USERNAME=@linkprosup
MAX_FILE_SIZE=2147483648  # 2GB in bytes
PARALLEL_DOWNLOADS=3
ENABLE_CDN=false
CDN_PROVIDER=cloudflare
ENABLE_AUTO_UPDATE=false
UPDATE_REPOSITORY=https://github.com/mhd1386/prolink.git
LOG_LEVEL=INFO
```

### Bot Commands
```
/start - Show help
/upload [url] - Upload file from URL
/help - Complete guide
/support - Contact support
/status - Bot status
/mystats - User statistics

# Admin Commands
/addchannel @channel - Add required channel
/removechannel @channel - Remove channel
/listchannels - List required channels
/addadmin 123456789 - Add admin
/removeadmin 123456789 - Remove admin
/listadmins - List admins
/displayconfig - Show display settings
/broadcast [message] - Send broadcast
/fullstats - Full statistics
/resetstats - Reset statistics
/security - Security settings
/update - Update bot from repository
```

## 🔧 Advanced Features

### CDN Integration
Enable CDN in `.env`:
```env
ENABLE_CDN=true
CDN_PROVIDER=cloudflare  # or "custom"
CDN_URL=https://your-cdn.example.com/
```

### Auto Update
Enable auto-update and use `/update` command to update from repository.

### Multi-language
Users can switch between English and Persian. Admin can set default language.

## 🛡️ Security

- Rate limiting (10 requests/minute, 100/day)
- File extension filtering
- Admin-only commands protection
- Session management
- Secure file handling

## 📊 Statistics

The bot tracks:
- Total downloads
- Total users
- Total data transferred
- User activity
- Daily requests

## 🔄 Update System

### Manual Update
```bash
cd prolink-python
git pull origin main
pip install -r requirements.txt
./start.sh
```

### Auto Update (Admin Command)
Use `/update` command to update from configured repository.

## 🤝 Support

- **Support**: @linkprosup
- **Bot**: @irprolinkbot
- **Version**: 6.0.0
- **Release Year**: 2026

## 📝 Changelog

### Version 6.0.0 (2026)
- Added multi-language support (English/Persian)
- Added spoiler mode for images and videos
- Added CDN support for better performance
- Added auto-update system
- Improved error handling and logging
- Enhanced security features
- Updated dependencies
- Fixed various bugs

### Version 5.x
- Basic file upload functionality
- Admin panel
- Statistics tracking
- Rate limiting

## 🐛 Troubleshooting

### Common Issues
1. **Bot not starting**: Check BOT_TOKEN in .env
2. **File upload fails**: Check URL and file size
3. **Rate limit error**: Wait and try again
4. **Permission denied**: Check file permissions

### Logs
Check `logs/` directory for detailed logs.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Credits

Developed by [MHD](https://github.com/mhd1386)

Donate by USDT ( BEP20 ) : 0x4e08a7c0a5ba928814965bb72f9ca399d99b85ae
---

**🚀 Happy uploading!**
