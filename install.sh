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

# Version-specific information
if [ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -eq 6 ]; then
    print_colored "⚠️ Python 3.6 detected: Using aiogram 2.18 (compatible version)" "$YELLOW"
    print_colored "   Note: aiogram 2.19+ requires Python 3.7+" "$BLUE"
elif [ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -ge 7 ]; then
    print_colored "✅ Python 3.7+ detected: Can use aiogram 2.19+" "$GREEN"
fi

# Check if we're in the right directory
if [ -f "install.py" ]; then
    print_colored "📁 Found install.py in current directory" "$GREEN"
    
    # Ask user if they want to install here or choose another directory
    print_colored "\nInstallation directory options:" "$BLUE"
    print_colored "1. Install in current directory: $(pwd)" "$YELLOW"
    print_colored "2. Install in /public_html (recommended for shared hosting)" "$YELLOW"
    print_colored "3. Choose custom directory" "$YELLOW"
    
    read -p "Enter choice (1/2/3): " dir_choice
    
    case $dir_choice in
        1)
            # Install in current directory
            print_colored "📁 Installing in current directory..." "$BLUE"
            ;;
        2)
            # Install in /public_html
            if [ ! -d "/public_html" ]; then
                print_colored "⚠️ /public_html directory doesn't exist" "$YELLOW"
                read -p "Create it? (yes/NO): " create_public
                if [[ "$create_public" =~ ^[Yy] ]]; then
                    mkdir -p /public_html
                    print_colored "✅ Created /public_html directory" "$GREEN"
                else
                    print_colored "❌ Installation cancelled" "$RED"
                    exit 1
                fi
            fi
            
            # Check if /public_html is empty
            if [ "$(ls -A /public_html 2>/dev/null)" ]; then
                print_colored "⚠️ /public_html directory is not empty" "$YELLOW"
                print_colored "Contents:" "$BLUE"
                ls -la /public_html | head -10
                
                read -p "Continue anyway? (yes/NO): " continue_anyway
                if [[ ! "$continue_anyway" =~ ^[Yy] ]]; then
                    print_colored "❌ Installation cancelled" "$RED"
                    exit 1
                fi
            fi
            
            # Copy files to /public_html
            print_colored "📁 Copying files to /public_html..." "$BLUE"
            cp -r . /public_html/
            cd /public_html
            print_colored "✅ Files copied to /public_html" "$GREEN"
            ;;
        3)
            # Choose custom directory
            read -p "Enter custom directory path: " custom_dir
            if [ ! -d "$custom_dir" ]; then
                print_colored "⚠️ Directory doesn't exist" "$YELLOW"
                read -p "Create it? (yes/NO): " create_custom
                if [[ "$create_custom" =~ ^[Yy] ]]; then
                    mkdir -p "$custom_dir"
                    print_colored "✅ Created directory: $custom_dir" "$GREEN"
                else
                    print_colored "❌ Installation cancelled" "$RED"
                    exit 1
                fi
            fi
            
            # Check if directory is empty
            if [ "$(ls -A "$custom_dir" 2>/dev/null)" ]; then
                print_colored "⚠️ Directory is not empty" "$YELLOW"
                print_colored "Contents:" "$BLUE"
                ls -la "$custom_dir" | head -10
                
                read -p "Continue anyway? (yes/NO): " continue_custom
                if [[ ! "$continue_custom" =~ ^[Yy] ]]; then
                    print_colored "❌ Installation cancelled" "$RED"
                    exit 1
                fi
            fi
            
            # Copy files to custom directory
            print_colored "📁 Copying files to $custom_dir..." "$BLUE"
            cp -r . "$custom_dir"/
            cd "$custom_dir"
            print_colored "✅ Files copied to $custom_dir" "$GREEN"
            ;;
        *)
            print_colored "❌ Invalid choice, using current directory" "$RED"
            ;;
    esac
    
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
