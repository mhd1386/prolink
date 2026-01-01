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

# Check Python version compatibility
PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")

if [ $PYTHON_MAJOR -lt 3 ] || ([ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -lt 6 ]); then
    log_message "❌ ERROR: Python 3.6 or higher required (found $PYTHON_MAJOR.$PYTHON_MINOR)"
    exit 1
fi

# Check if Python 3.6 (aiogram 2.18) or Python 3.7+ (aiogram 2.19)
if [ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -eq 6 ]; then
    log_message "⚠️ Python 3.6 detected: Using aiogram 2.18 (compatible version)"
    
    # Force install aiogram 2.18 for Python 3.6
    log_message "Installing aiogram 2.18 for Python 3.6 compatibility..."
    
    # First, uninstall any existing aiogram version
    $PYTHON_CMD -m pip uninstall -y aiogram 2>/dev/null || true
    
    # Install aiogram 2.18 specifically
    $PYTHON_CMD -m pip install --user "aiogram==2.18" --no-cache-dir
    
    # Verify installation
    if $PYTHON_CMD -c "import aiogram; import pkg_resources; v = pkg_resources.get_distribution('aiogram').version; print('Version:', v)" 2>/dev/null | grep -q "2.18"; then
        log_message "✅ aiogram 2.18 installed successfully (compatible with Python 3.6)"
    else
        log_message "❌ Failed to install aiogram 2.18"
        log_message "Trying alternative installation method..."
        $PYTHON_CMD -m pip install --user "aiogram==2.18.0" --no-cache-dir
    fi
    
elif [ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -ge 7 ]; then
    log_message "✅ Python 3.7+ detected: Can use aiogram 2.19+"
    
    # For cPanel Python 3.9, ensure aiogram 2.19+ is installed
    if [ $PYTHON_MINOR -ge 9 ]; then
        log_message "Python 3.9+ detected: Installing aiogram 2.19+"
        $PYTHON_CMD -m pip uninstall -y aiogram 2>/dev/null || true
        $PYTHON_CMD -m pip install --user "aiogram>=2.19" --no-cache-dir
    fi
else
    log_message "✅ Python version compatible"
fi

# Check for cPanel Python app virtual environment
CPANEL_VENV_PATH="/home/mihanexp/virtualenv/prolink/3.9/bin/activate"
if [ -f "$CPANEL_VENV_PATH" ]; then
    log_message "⚠️ cPanel Python app environment detected"
    log_message "Activating cPanel virtual environment: $CPANEL_VENV_PATH"
    source "$CPANEL_VENV_PATH"
    # Update PYTHON_CMD to use the virtual environment python
    PYTHON_CMD="python3"
    log_message "Using cPanel Python environment"
    
    # Check and install dependencies in cPanel environment
    if ! $PYTHON_CMD -c "import aiogram" &> /dev/null; then
        log_message "⚠️ Dependencies not found in cPanel environment"
        log_message "Installing dependencies in cPanel virtual environment..."
        
        # For Python 3.9+, install aiogram 2.19+ instead of 2.18
        if [ $PYTHON_MINOR -ge 9 ]; then
            log_message "Python 3.9+ in cPanel: Installing aiogram 2.19+ and dependencies..."
            
            # Install core dependencies for Python 3.9
            $PYTHON_CMD -m pip install "aiogram>=2.19" "aiohttp>=3.8.0" "aiofiles>=0.7.0" \
                "python-dotenv>=0.19.0" "pytz>=2021.1" "requests>=2.25.1" \
                "beautifulsoup4>=4.9.3" "urllib3>=1.26.5"
            
            if [ $? -eq 0 ]; then
                log_message "✅ Dependencies installed successfully for Python 3.9+"
            else
                log_message "❌ Failed to install dependencies for Python 3.9+"
                log_message "Trying with requirements.txt..."
                if [ -f "requirements.txt" ]; then
                    $PYTHON_CMD -m pip install -r requirements.txt
                fi
            fi
        else
            # For Python 3.6-3.8, use requirements.txt
            if [ -f "requirements.txt" ]; then
                $PYTHON_CMD -m pip install -r requirements.txt
                if [ $? -eq 0 ]; then
                    log_message "✅ Dependencies installed successfully in cPanel environment"
                else
                    log_message "❌ Failed to install dependencies in cPanel environment"
                    log_message "Trying with --user flag..."
                    $PYTHON_CMD -m pip install --user -r requirements.txt
                fi
            fi
        fi
    else
        log_message "✅ Dependencies found in cPanel environment"
        
        # Check aiogram version for Python 3.9+
        if [ $PYTHON_MINOR -ge 9 ]; then
            AIOGRAM_VERSION=$($PYTHON_CMD -c "import aiogram; import pkg_resources; print(pkg_resources.get_distribution('aiogram').version)" 2>/dev/null || echo "")
            if [[ "$AIOGRAM_VERSION" == "2.18"* ]]; then
                log_message "⚠️ Python 3.9+ detected with aiogram 2.18 - upgrading to 2.19+"
                $PYTHON_CMD -m pip install --upgrade "aiogram>=2.19"
            fi
        fi
    fi
    
# Check for local virtual environment
elif [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    log_message "Activating local virtual environment..."
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

# Run the bot with user site-packages path
# Add user site-packages to Python path for --user installed packages
USER_SITE=$($PYTHON_CMD -c "import site; print(site.getusersitepackages())" 2>/dev/null || echo "")
if [ -n "$USER_SITE" ] && [ -d "$USER_SITE" ]; then
    log_message "Using user site-packages: $USER_SITE"
    export PYTHONPATH="$USER_SITE:$PYTHONPATH"
fi

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
