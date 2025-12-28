#!/bin/bash
# irProLink Bot Installation Script
# Auto-detects Python version and runs the installer

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_colored() {
    echo -e "${2}${1}${NC}"
}

print_colored "🤖 irProLink Bot Installation" "$BLUE"
print_colored "==============================" "$BLUE"

# Check for Python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_colored "✅ Found python3: $PYTHON_VERSION" "$GREEN"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    print_colored "✅ Found python: $PYTHON_VERSION" "$GREEN"
else
    print_colored "❌ Python not found!" "$RED"
    print_colored "Please install Python 3.6 or higher:" "$YELLOW"
    echo ""
    print_colored "For Ubuntu/Debian:" "$BLUE"
    print_colored "  sudo apt update && sudo apt install python3 python3-pip" "$GREEN"
    echo ""
    print_colored "For CentOS/RHEL:" "$BLUE"
    print_colored "  sudo yum install python3 python3-pip" "$GREEN"
    echo ""
    print_colored "For shared hosting:" "$BLUE"
    print_colored "  Contact your hosting provider to enable Python" "$YELLOW"
    exit 1
fi

# Check Python version
PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")

if [ $PYTHON_MAJOR -lt 3 ] || ([ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -lt 6 ]); then
    print_colored "❌ Python 3.6 or higher required (found $PYTHON_MAJOR.$PYTHON_MINOR)" "$RED"
    exit 1
fi

print_colored "✅ Python version OK: $PYTHON_MAJOR.$PYTHON_MINOR" "$GREEN"

# Check if we're in the right directory
if [ -f "install.py" ]; then
    print_colored "📁 Running installer from current directory..." "$BLUE"
else
    print_colored "⚠️ install.py not found in current directory" "$YELLOW"
    print_colored "Make sure you're in the prolink directory:" "$BLUE"
    print_colored "  cd /path/to/prolink" "$GREEN"
    exit 1
fi

# Run the Python installer
print_colored "🚀 Starting installation..." "$BLUE"
$PYTHON_CMD install.py

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo ""
    print_colored "==========================================" "$GREEN"
    print_colored "✅ Installation completed successfully!" "$GREEN"
    print_colored "==========================================" "$GREEN"
    echo ""
    print_colored "📋 Next steps:" "$YELLOW"
    print_colored "1. Edit .env file and set your BOT_TOKEN" "$BLUE"
    print_colored "   nano .env" "$GREEN"
    print_colored "2. Start the bot:" "$BLUE"
    print_colored "   ./start.sh" "$GREEN"
    print_colored "3. Check logs:" "$BLUE"
    print_colored "   tail -f logs/bot.log" "$GREEN"
else
    print_colored "❌ Installation failed!" "$RED"
    print_colored "Check the error messages above." "$YELLOW"
    exit 1
fi
