# 🤖 irProLink Bot - Python Version 6.1.0 (2026)

**Enhanced for Shared Hosting - No Root Access Required**

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

### 🎯 **Automatic Installation (Recommended for Shared Hosting)**
```bash
# Step 1: Clone repository
git clone https://github.com/mhd1386/prolink.git

# Step 2: Enter the project directory
cd prolink

# Step 3: Make install.sh executable
chmod +x install.sh

# Step 4: Run the installation script (auto-detects Python)
./install.sh

# The script will:
# 1. Auto-detect Python (python3 or python)
# 2. Check Python version (3.6+ required)
# 3. Run the Python installer
# 4. Create virtual environment
# 5. Install dependencies with --user flag
# 6. Create .env file from template
# 7. Set up start/stop scripts
# 8. Configure cron job for auto-start

# Step 5: Edit .env file and set your bot token
nano .env

# Step 6: Start the bot
./start.sh
```

### 🚀 **One-Line Installation (For Experienced Users)**
```bash
git clone https://github.com/mhd1386/prolink.git && cd prolink && chmod +x install.sh && ./install.sh
```

### 🐍 **Direct Python Installation (If you know your Python command)**
```bash
# If you have python3:
git clone https://github.com/mhd1386/prolink.git
cd prolink
python3 install.py

# If you have python:
git clone https://github.com/mhd1386/prolink.git
cd prolink
python install.py
```

### 🔧 **Manual Installation**
```bash
# Clone repository
git clone https://github.com/mhd1386/prolink.git
cd prolink

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies (use --user flag if no root access)
pip install --user -r requirements.txt

# Or install in virtual environment
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env file
nano .env  # Set BOT_TOKEN=your_bot_token_here

# Create necessary directories
mkdir -p data logs temp

# Start the bot
python main.py
```

### 🚀 **One-Command Installation**
```bash
# Complete installation in one command
git clone https://github.com/mhd1386/prolink.git && cd prolink && python install.py && echo "Please edit .env file and set BOT_TOKEN" && nano .env
```

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
- **Version**: 6.1.0
- **Release Year**: 2026

## 📝 Changelog

### Version 6.1.0 (2026) - Shared Hosting Edition
- **Enhanced for shared hosting**: No root access required
- **Automatic dependency installation**: Uses `--user` flag for pip install
- **Improved start.sh script**: Auto-detects Python, checks dependencies, validates .env
- **Enhanced stop.sh script**: Graceful shutdown with multiple PID detection methods
- **Virtual environment support**: Automatic creation and activation
- **Better error handling**: Comprehensive logging and user-friendly messages
- **Updated installation script**: install.py now supports virtual environments
- **Fixed permission issues**: Better handling of file permissions
- **Compatibility improvements**: Works with Python 3.6+ on shared hosting

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

### Installation Errors
1. **"bash: cd: too many arguments"**:
   - **Cause**: Missing space between commands, e.g., `cd prolinkgit clone` instead of `cd prolink && git clone`
   - **Solution**: Run commands separately:
     ```bash
     git clone https://github.com/mhd1386/prolink.git
     cd prolink
     ```
   - **Alternative**: Use the one-line installation:
     ```bash
     git clone https://github.com/mhd1386/prolink.git && cd prolink && python install.py
     ```

2. **"command not found: python"**:
   - **Solution**: Use `python3` instead of `python`:
     ```bash
     python3 install.py
     ```

3. **"Permission denied" when running scripts**:
   - **Solution**: Make scripts executable:
     ```bash
     chmod +x start.sh stop.sh
     ```

### Logs
Check `logs/` directory for detailed logs.

## 💝 Support Development

Your support helps maintain and improve irProLink bot. Consider donating to support ongoing development:

### **USDT (BEP20) Donations**
- **Network**: Binance Smart Chain (BEP20)
- **Wallet Address**: `0x4e08a7c0a5ba928814965bb72f9ca399d99b85ae`
- **Token**: USDT (Tether)

For more donation options and information, see [DONATE.md](DONATE.md).

## 📄 License

This project is licensed under the MIT License.

## 🙏 Credits

Developed by **[MHD1386 (GEMBit)](https://github.com/mhd1386)**

---

**🚀 Happy uploading!**
