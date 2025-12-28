#!/usr/bin/env python3
"""
Bot installation script for shared hosting
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_colored(text, color):
    """Print colored text"""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

def get_installation_directory():
    """Get installation directory from user with validation"""
    print_colored("\n📁 Installation Directory Setup", 'blue')
    print_colored("=" * 40, 'blue')
    
    default_dir = "prolink"
    
    while True:
        print_colored(f"\nEnter installation directory (default: {default_dir}): ", 'yellow')
        user_input = input().strip()
        
        if not user_input:
            install_dir = default_dir
        else:
            install_dir = user_input
        
        # Clean up directory path
        install_dir = install_dir.rstrip('/').rstrip('\\')
        
        # Check if directory exists
        if os.path.exists(install_dir):
            try:
                # Check if directory is empty
                contents = os.listdir(install_dir)
                if contents:
                    print_colored(f"⚠️ Directory '{install_dir}' is not empty.", 'yellow')
                    print_colored(f"Contents: {', '.join(contents[:5])}{'...' if len(contents) > 5 else ''}", 'yellow')
                    
                    print_colored("\nOptions:", 'blue')
                    print_colored("1. Clean directory (delete all contents)", 'yellow')
                    print_colored("2. Choose different directory", 'yellow')
                    print_colored("3. Cancel installation", 'yellow')
                    
                    choice = input("\nEnter choice (1/2/3): ").strip()
                    
                    if choice == '1':
                        # Confirm cleanup
                        confirm = input(f"⚠️ Are you sure you want to DELETE ALL CONTENTS of '{install_dir}'? (yes/NO): ").strip().lower()
                        if confirm in ['yes', 'y', 'بله']:
                            print_colored(f"🗑️ Cleaning directory '{install_dir}'...", 'blue')
                            try:
                                # Remove all contents
                                for item in os.listdir(install_dir):
                                    item_path = os.path.join(install_dir, item)
                                    if os.path.isfile(item_path) or os.path.islink(item_path):
                                        os.unlink(item_path)
                                    elif os.path.isdir(item_path):
                                        import shutil
                                        shutil.rmtree(item_path)
                                print_colored(f"✅ Directory cleaned successfully", 'green')
                                return install_dir
                            except Exception as e:
                                print_colored(f"❌ Error cleaning directory: {e}", 'red')
                                continue
                        else:
                            print_colored("❌ Cleanup cancelled", 'red')
                            continue
                    elif choice == '2':
                        continue
                    elif choice == '3':
                        print_colored("❌ Installation cancelled", 'red')
                        sys.exit(0)
                    else:
                        print_colored("❌ Invalid choice", 'red')
                        continue
                else:
                    # Directory exists but is empty
                    print_colored(f"✅ Directory '{install_dir}' exists and is empty", 'green')
                    return install_dir
            except Exception as e:
                print_colored(f"❌ Error checking directory: {e}", 'red')
                continue
        else:
            # Directory doesn't exist, ask to create it
            print_colored(f"📁 Directory '{install_dir}' doesn't exist.", 'yellow')
            create = input("Create it? (yes/NO): ").strip().lower()
            
            if create in ['yes', 'y', 'بله']:
                try:
                    os.makedirs(install_dir, exist_ok=True)
                    print_colored(f"✅ Directory '{install_dir}' created", 'green')
                    return install_dir
                except Exception as e:
                    print_colored(f"❌ Error creating directory: {e}", 'red')
                    continue
            else:
                print_colored("❌ Directory creation cancelled", 'red')
                continue
    
    return install_dir

def change_to_installation_directory(install_dir):
    """Change to installation directory and return original directory"""
    original_dir = os.getcwd()
    
    try:
        os.chdir(install_dir)
        print_colored(f"📂 Changed to installation directory: {install_dir}", 'green')
        return original_dir
    except Exception as e:
        print_colored(f"❌ Error changing directory: {e}", 'red')
        sys.exit(1)

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 6):
        print_colored("❌ Python 3.6 or higher required", 'red')
        print_colored("\n💡 Try using 'python3' instead of 'python':", 'yellow')
        print_colored("   python3 install.py", 'green')
        return False
    
    python_cmd = sys.executable.split('/')[-1] if '/' in sys.executable else sys.executable
    print_colored(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ({python_cmd})", 'green')
    
    # Check if python3 is available (for user guidance)
    try:
        subprocess.check_call(['python3', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print_colored("✅ python3 command is also available", 'green')
    except:
        pass
    
    return True

def install_dependencies():
    """Install dependencies"""
    print_colored("📦 Installing dependencies...", 'blue')
    
    try:
        # Check if pip exists
        subprocess.check_call([sys.executable, '-m', 'pip', '--version'])
    except:
        print_colored("❌ pip not found", 'red')
        return False
    
    # Install requirements with --user flag for shared hosting
    requirements_file = Path(__file__).parent / 'requirements.txt'
    if requirements_file.exists():
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', '-r', str(requirements_file)])
            print_colored("✅ Dependencies installed", 'green')
            return True
        except subprocess.CalledProcessError:
            print_colored("❌ Error installing dependencies", 'red')
            return False
    else:
        print_colored("⚠️ requirements.txt file not found", 'yellow')
        return True

def create_env_file():
    """Create .env file"""
    env_example = Path(__file__).parent / '.env.example'
    env_file = Path(__file__).parent / '.env'
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print_colored("✅ .env file created", 'green')
            print_colored("⚠️ Please edit .env file and set your bot token", 'yellow')
        else:
            print_colored("⚠️ .env.example file not found", 'yellow')
    else:
        print_colored("✅ .env file already exists", 'green')
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['data', 'logs', 'temp']
    base_dir = Path(__file__).parent
    
    for dir_name in directories:
        dir_path = base_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        print_colored(f"✅ Directory {dir_name} created", 'green')
    
    return True

def setup_cron_job():
    """Setup cron job for auto-start"""
    print_colored("🕐 Setting up cron job for auto-start", 'blue')
    
    # Python file path
    python_path = sys.executable
    main_script = Path(__file__).parent / 'main.py'
    script_dir = Path(__file__).parent
    
    cron_command = f"cd {script_dir} && {python_path} {main_script}"
    
    print_colored("📝 Cron command:", 'yellow')
    print_colored(f"@reboot {cron_command}", 'blue')
    print_colored("📋 To add to cron:", 'yellow')
    print_colored("1. Run the following command:", 'blue')
    print_colored(f"   crontab -e", 'green')
    print_colored("2. Add this line:", 'blue')
    print_colored(f"   @reboot {cron_command} > {script_dir}/logs/cron.log 2>&1", 'green')
    
    return True

def create_start_script():
    """Create start.sh script"""
    script_content = """#!/bin/bash
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
"""
    
    start_script = Path(__file__).parent / 'start.sh'
    with open(start_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    start_script.chmod(0o755)
    print_colored("✅ start.sh script created (Version 6.1.0)", 'green')
    
    return True

def create_stop_script():
    """Create stop.sh script"""
    script_content = """#!/bin/bash
# irProLink bot stop script - Version 6.1.0

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

log_message "=== Stopping irProLink Bot ==="

# Find bot PID using multiple methods
PID=""

# Method 1: Look for python3 main.py
PID1=$(ps aux | grep -E "[p]ython3.*main\.py|[p]ython.*main\.py" | awk '{print $2}')

# Method 2: Look for process in current directory
PID2=$(lsof -t -c python -a -d cwd -F p | grep '^p' | cut -c 2-)

# Method 3: Look for bot process by name
PID3=$(pgrep -f "main.py")

# Combine and get unique PIDs
ALL_PIDS=$(echo "$PID1 $PID2 $PID3" | tr ' ' '\n' | sort -u | tr '\n' ' ')

if [ -z "$ALL_PIDS" ]; then
    log_message "✅ Bot is not running"
    exit 0
fi

log_message "Found bot PIDs: $ALL_PIDS"

# Stop each process
for PID in $ALL_PIDS; do
    if [ -n "$PID" ] && ps -p "$PID" > /dev/null 2>&1; then
        log_message "Stopping process $PID..."
        
        # Send SIGTERM first (graceful shutdown)
        kill -TERM "$PID" 2>/dev/null
        
        # Wait for process to terminate
        for i in {1..10}; do
            if ! ps -p "$PID" > /dev/null 2>&1; then
                log_message "✅ Process $PID stopped gracefully"
                break
            fi
            sleep 1
        done
        
        # If still running, send SIGKILL
        if ps -p "$PID" > /dev/null 2>&1; then
            log_message "Process $PID not responding, forcing termination..."
            kill -KILL "$PID" 2>/dev/null
            sleep 1
            
            if ! ps -p "$PID" > /dev/null 2>&1; then
                log_message "✅ Process $PID forced to stop"
            else
                log_message "❌ Failed to stop process $PID"
            fi
        fi
    fi
done

# Clean up any remaining .pyc files
find . -name "*.pyc" -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

log_message "✅ Bot stopped successfully"
log_message "=== Stop Script Finished ==="
"""
    
    stop_script = Path(__file__).parent / 'stop.sh'
    with open(stop_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    stop_script.chmod(0o755)
    print_colored("✅ stop.sh script created (Version 6.1.0)", 'green')
    
    return True

def create_virtual_env():
    """Create virtual environment in project directory"""
    print_colored("🐍 Creating virtual environment...", 'blue')
    
    venv_dir = Path(__file__).parent / 'venv'
    
    if venv_dir.exists():
        print_colored("✅ Virtual environment already exists", 'green')
        return True
    
    try:
        subprocess.check_call([sys.executable, '-m', 'venv', str(venv_dir)])
        print_colored("✅ Virtual environment created", 'green')
        
        # Install pip in virtual environment
        if sys.platform == 'win32':
            pip_path = venv_dir / 'Scripts' / 'pip.exe'
        else:
            pip_path = venv_dir / 'bin' / 'pip'
        
        # Upgrade pip in virtual environment
        subprocess.check_call([str(pip_path), 'install', '--upgrade', 'pip'])
        print_colored("✅ pip upgraded in virtual environment", 'green')
        
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Error creating virtual environment: {e}", 'red')
        print_colored("⚠️ Continuing without virtual environment", 'yellow')
        return False

def install_dependencies_virtualenv():
    """Install dependencies in virtual environment"""
    print_colored("📦 Installing dependencies in virtual environment...", 'blue')
    
    venv_dir = Path(__file__).parent / 'venv'
    requirements_file = Path(__file__).parent / 'requirements.txt'
    
    if not venv_dir.exists():
        print_colored("❌ Virtual environment not found", 'red')
        return False
    
    try:
        if sys.platform == 'win32':
            pip_path = venv_dir / 'Scripts' / 'pip.exe'
        else:
            pip_path = venv_dir / 'bin' / 'pip'
        
        subprocess.check_call([str(pip_path), 'install', '-r', str(requirements_file)])
        print_colored("✅ Dependencies installed in virtual environment", 'green')
        return True
    except subprocess.CalledProcessError:
        print_colored("❌ Error installing dependencies in virtual environment", 'red')
        return False

def main():
    """Main function"""
    print_colored("=" * 50, 'blue')
    print_colored("🤖 irProLink Bot Installation for Shared Hosting", 'blue')
    print_colored("🚀 Version: 6.1.0 (2026)", 'blue')
    print_colored("=" * 50, 'blue')
    
    # Get installation directory from user
    install_dir = get_installation_directory()
    
    # Change to installation directory
    original_dir = change_to_installation_directory(install_dir)
    
    try:
        # Check Python version
        if not check_python_version():
            return
        
        # Create directories
        if not create_directories():
            return
        
        # Try to create virtual environment (preferred method)
        venv_created = create_virtual_env()
        
        if venv_created:
            # Install dependencies in virtual environment
            if not install_dependencies_virtualenv():
                print_colored("⚠️ Falling back to user installation", 'yellow')
                if not install_dependencies():
                    return
        else:
            # Fallback to user installation
            if not install_dependencies():
                return
        
        # Create .env file
        if not create_env_file():
            return
        
        # Create scripts
        create_start_script()
        create_stop_script()
        
        # Setup cron job
        setup_cron_job()
        
        print_colored("\n" + "=" * 50, 'green')
        print_colored("✅ Installation completed!", 'green')
        print_colored("=" * 50, 'green')
        
        print_colored(f"\n📁 Installation directory: {os.path.abspath('.')}", 'yellow')
        print_colored("\n📋 Next steps:", 'yellow')
        print_colored("1. Edit .env file:", 'blue')
        print_colored("   nano .env", 'green')
        print_colored("2. Change BOT_TOKEN to your bot token", 'blue')
        print_colored("3. Start the bot:", 'blue')
        print_colored("   ./start.sh", 'green')
        print_colored("4. To stop:", 'blue')
        print_colored("   ./stop.sh", 'green')
        
        print_colored("\n💡 Tips for shared hosting:", 'yellow')
        print_colored("• Use 'python3' instead of 'python' if needed", 'blue')
        print_colored("• Check file permissions: chmod +x *.sh", 'blue')
        print_colored("• Monitor logs: tail -f logs/bot.log", 'blue')
        
        print_colored("\n📞 Support: @linkprosup", 'yellow')
        print_colored("🤖 Bot: @irprolinkbot", 'yellow')
        
    finally:
        # Change back to original directory
        os.chdir(original_dir)
        print_colored(f"\n📂 Returned to original directory: {original_dir}", 'green')

if __name__ == "__main__":
    main()
