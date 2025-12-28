#!/bin/bash
# irProLink bot start script - Version 6.1.0
# Compatible with shared hosting (no root access required)

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Log file
LOG_FILE="logs/bot.log"
mkdir -p logs

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "=== Starting irProLink Bot ==="

# Check Python version
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
    if ! command -v python &> /dev/null; then
        log_message "❌ ERROR: Python not found. Please install Python 3.6+"
        exit 1
    fi
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
log_message "Python version: $PYTHON_VERSION"

# Check for virtual environment
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    log_message "Activating virtual environment..."
    source venv/bin/activate
    
    # Check if dependencies are installed in venv
    if ! $PYTHON_CMD -c "import aiogram" &> /dev/null; then
        log_message "⚠️ Dependencies not found in virtual environment"
        log_message "Installing dependencies in virtual environment..."
        
        # Determine pip command
        if [ -f "venv/bin/pip" ]; then
            PIP_CMD="venv/bin/pip"
        elif [ -f "venv/bin/pip3" ]; then
            PIP_CMD="venv/bin/pip3"
        else
            PIP_CMD="pip"
        fi
        
        if [ -f "requirements.txt" ]; then
            $PIP_CMD install -r requirements.txt
            if [ $? -eq 0 ]; then
                log_message "✅ Dependencies installed successfully"
            else
                log_message "❌ Failed to install dependencies"
            fi
        fi
    fi
else
    log_message "ℹ️ No virtual environment found, using system Python"
    
    # Check if dependencies are installed
    if ! $PYTHON_CMD -c "import aiogram" &> /dev/null; then
        log_message "⚠️ Dependencies not found. Attempting to install with --user flag..."
        
        # Try to install with --user flag (no root required)
        if [ -f "requirements.txt" ]; then
            $PYTHON_CMD -m pip install --user -r requirements.txt
            if [ $? -eq 0 ]; then
                log_message "✅ Dependencies installed with --user flag"
            else
                log_message "❌ Failed to install dependencies. Please run: python -m pip install --user -r requirements.txt"
                exit 1
            fi
        fi
    fi
fi

# Check .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        log_message "⚠️ .env file not found. Creating from .env.example..."
        cp .env.example .env
        log_message "✅ .env file created. Please edit it and set your BOT_TOKEN"
        exit 1
    else
        log_message "❌ ERROR: .env file not found and .env.example missing"
        exit 1
    fi
fi

# Check BOT_TOKEN in .env
if grep -q "BOT_TOKEN=YOUR_BOT_TOKEN_HERE" .env || ! grep -q "BOT_TOKEN=" .env; then
    log_message "❌ ERROR: BOT_TOKEN not set in .env file"
    log_message "Please edit .env file and set your bot token from @BotFather"
    exit 1
fi

# Create necessary directories
mkdir -p data logs temp

log_message "✅ All checks passed"
log_message "🚀 Starting bot..."

# Run the bot
$PYTHON_CMD main.py 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}
log_message "Bot stopped with exit code: $EXIT_CODE"

if [ $EXIT_CODE -eq 0 ]; then
    log_message "✅ Bot stopped normally"
else
    log_message "❌ Bot stopped with error"
fi

log_message "=== irProLink Bot Stopped ==="
