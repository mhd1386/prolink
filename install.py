#!/usr/bin/env python3
"""
Bot installation script - Improved version
Works on any directory with proper permission handling
"""

import os
import sys
import subprocess
import shutil
import platform
import stat
from pathlib import Path
import getpass

def print_colored(text, color):
    """Print colored text"""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'reset': '\033[0m'
    }
    if sys.platform == 'win32' and not os.environ.get('TERM'):
        # Windows without ANSI support
        print(text)
    else:
        print(f"{colors.get(color, '')}{text}{colors['reset']}")

def get_installation_directory():
    """Get installation directory from user with validation"""
    print_colored("\n📁 Installation Directory Setup", 'blue')
    print_colored("=" * 50, 'blue')
    
    # Get current user and suggest appropriate directory
    current_user = getpass.getuser()
    system = platform.system()
    
    if system == 'Linux':
        # Linux suggestions - always end with /prolink
        suggestions = [
            f"/home/{current_user}/prolink",
            f"/opt/prolink",
            f"/var/www/prolink",
            f"/root/prolink"
        ]
    elif system == 'Windows':
        # Windows suggestions
        suggestions = [
            f"C:\\Users\\{current_user}\\prolink",
            f"C:\\prolink",
            f"D:\\prolink"
        ]
    else:
        # Other OS
        suggestions = [
            f"./prolink",
            f"/opt/prolink"
        ]
    
    print_colored("\n💡 Suggested installation directories (always in 'prolink' folder):", 'cyan')
    for i, suggestion in enumerate(suggestions, 1):
        print_colored(f"  {i}. {suggestion}", 'yellow')
    
    print_colored("\n📝 You can also enter any custom directory path.", 'cyan')
    print_colored("⚠️ Note: The bot will be installed in a 'prolink' subdirectory.", 'yellow')
    
    while True:
        print_colored("\nEnter parent directory path (bot will be installed in 'prolink' subdirectory): ", 'yellow')
        user_input = input().strip()
        
        if not user_input:
            print_colored("❌ Please enter a directory path", 'red')
            continue
        
        # Clean up directory path
        parent_dir = os.path.abspath(os.path.expanduser(user_input))
        install_dir = os.path.join(parent_dir, "prolink")
        
        # Check if parent directory exists
        if not os.path.exists(parent_dir):
            print_colored(f"📁 Parent directory '{parent_dir}' doesn't exist.", 'yellow')
            create = input("Create it? (yes/NO): ").strip().lower()
            
            if create in ['yes', 'y', 'بله']:
                try:
                    os.makedirs(parent_dir, exist_ok=True)
                    print_colored(f"✅ Parent directory '{parent_dir}' created", 'green')
                except Exception as e:
                    print_colored(f"❌ Error creating parent directory: {e}", 'red')
                    print_colored("Please check permissions or choose another directory.", 'yellow')
                    continue
            else:
                print_colored("❌ Directory creation cancelled", 'red')
                continue
        
        # Check if installation directory exists
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
                                        shutil.rmtree(item_path)
                                print_colored(f"✅ Directory cleaned successfully", 'green')
                                return install_dir
                            except Exception as e:
                                print_colored(f"❌ Error cleaning directory: {e}", 'red')
                                print_colored("Please check permissions or choose another directory.", 'yellow')
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
                print_colored("Please check permissions or choose another directory.", 'yellow')
                continue
        else:
            # Installation directory doesn't exist, create it
            try:
                os.makedirs(install_dir, exist_ok=True)
                print_colored(f"✅ Directory '{install_dir}' created", 'green')
                
                # Check write permissions
                test_file = os.path.join(install_dir, '.permission_test')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.unlink(test_file)
                    print_colored(f"✅ Write permissions verified", 'green')
                except Exception as e:
                    print_colored(f"❌ Cannot write to directory: {e}", 'red')
                    print_colored("Please choose a directory with write permissions.", 'yellow')
                    continue
                
                return install_dir
            except Exception as e:
                print_colored(f"❌ Error creating directory: {e}", 'red')
                print_colored("Please check permissions or choose another directory.", 'yellow')
                continue
    
    return install_dir

def copy_project_files(install_dir):
    """Copy all project files to installation directory"""
    print_colored("\n📁 Copying project files...", 'blue')
    
    # Get current script directory
    current_dir = Path(__file__).parent
    
    try:
        # List of files and directories to copy
        items_to_copy = []
        for item in current_dir.iterdir():
            if item.name not in ['.git', '__pycache__', 'venv', '.env']:
                items_to_copy.append(item)
        
        # Copy each item
        for item in items_to_copy:
            dest = Path(install_dir) / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
            print_colored(f"  ✅ {item.name}", 'green')
        
        print_colored(f"✅ All files copied to {install_dir}", 'green')
        return True
    except Exception as e:
        print_colored(f"❌ Error copying files: {e}", 'red')
        return False

def check_python_version():
    """Check Python version"""
    print_colored("\n🐍 Checking Python version...", 'blue')
    
    if sys.version_info < (3, 6):
        print_colored("❌ Python 3.6 or higher required", 'red')
        print_colored(f"Current version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", 'yellow')
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

def install_dependencies(install_dir):
    """Install dependencies with proper permission handling"""
    print_colored("\n📦 Installing dependencies...", 'blue')
    
    # Change to installation directory
    original_dir = os.getcwd()
    os.chdir(install_dir)
    
    try:
        # Check if pip exists
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', '--version'])
        except:
            print_colored("❌ pip not found", 'red')
            print_colored("Installing pip...", 'blue')
            try:
                subprocess.check_call([sys.executable, '-m', 'ensurepip', '--upgrade'])
            except:
                print_colored("❌ Failed to install pip", 'red')
                return False
        
        # Install requirements with appropriate flags
        requirements_file = 'requirements.txt'
        if os.path.exists(requirements_file):
            print_colored("Installing from requirements.txt...", 'blue')
            
            # Try different installation methods
            methods = [
                [sys.executable, '-m', 'pip', 'install', '--user', '-r', requirements_file],
                [sys.executable, '-m', 'pip', 'install', '-r', requirements_file]
            ]
            
            success = False
            for method in methods:
                try:
                    print_colored(f"Trying: {' '.join(method)}", 'cyan')
                    subprocess.check_call(method)
                    print_colored("✅ Dependencies installed", 'green')
                    success = True
                    break
                except subprocess.CalledProcessError as e:
                    print_colored(f"Method failed: {e}", 'yellow')
                    continue
            
            if not success:
                print_colored("❌ All installation methods failed", 'red')
                print_colored("Please install dependencies manually:", 'yellow')
                print_colored(f"  cd {install_dir}", 'green')
                print_colored(f"  {sys.executable} -m pip install -r requirements.txt", 'green')
                return False
        else:
            print_colored("⚠️ requirements.txt file not found", 'yellow')
            return False
        
        return True
    except Exception as e:
        print_colored(f"❌ Error installing dependencies: {e}", 'red')
        return False
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def create_env_file(install_dir):
    """Create .env file"""
    print_colored("\n⚙️ Setting up configuration...", 'blue')
    
    env_example = Path(install_dir) / '.env.example'
    env_file = Path(install_dir) / '.env'
    
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

def create_directories(install_dir):
    """Create necessary directories"""
    print_colored("\n📁 Creating necessary directories...", 'blue')
    
    directories = ['data', 'logs', 'temp']
    base_dir = Path(install_dir)
    
    for dir_name in directories:
        dir_path = base_dir / dir_name
        try:
            dir_path.mkdir(exist_ok=True)
            print_colored(f"✅ Directory {dir_name} created", 'green')
        except Exception as e:
            print_colored(f"❌ Error creating directory {dir_name}: {e}", 'red')
    
    return True

def setup_start_scripts(install_dir):
    """Setup start and stop scripts for the platform"""
    print_colored("\n🚀 Setting up startup scripts...", 'blue')
    
    system = platform.system()
    
    if system == 'Linux':
        # Create start.sh
        start_script = Path(install_dir) / 'start.sh'
        start_content = """#!/bin/bash
# irProLink bot start script

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

# Check Python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
    if ! command -v python &> /dev/null; then
        log_message "❌ ERROR: Python not found"
        exit 1
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
        log_message "❌ ERROR: .env file not found"
        exit 1
    fi
fi

# Check BOT_TOKEN
if grep -q "BOT_TOKEN=YOUR_BOT_TOKEN_HERE" .env || ! grep -q "BOT_TOKEN=" .env; then
    log_message "❌ ERROR: BOT_TOKEN not set in .env file"
    log_message "Please edit .env file and set your bot token"
    exit 1
fi

# Create directories
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
        
        with open(start_script, 'w', encoding='utf-8') as f:
            f.write(start_content)
        
        # Make executable
        start_script.chmod(0o755)
        print_colored("✅ start.sh script created", 'green')
        
        # Create stop.sh
        stop_script = Path(install_dir) / 'stop.sh'
        stop_content = """#!/bin/bash
# irProLink bot stop script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_FILE="logs/bot.log"
mkdir -p logs

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "=== Stopping irProLink Bot ==="

# Find bot processes
PIDS=$(ps aux | grep -E "[p]ython3.*main\.py|[p]ython.*main\.py" | awk '{print $2}')

if [ -z "$PIDS" ]; then
    log_message "✅ Bot is not running"
    exit 0
fi

log_message "Found bot PIDs: $PIDS"

# Stop each process
for PID in $PIDS; do
    if [ -n "$PID" ]; then
        log_message "Stopping process $PID..."
        kill -TERM "$PID" 2>/dev/null
        sleep 2
        if ps -p "$PID" > /dev/null 2>&1; then
            log_message "Force stopping process $PID..."
            kill -KILL "$PID" 2>/dev/null
        fi
        log_message "✅ Process $PID stopped"
    fi
done

log_message "✅ Bot stopped successfully"
"""
        
        with open(stop_script, 'w', encoding='utf-8') as f:
            f.write(stop_content)
        
        stop_script.chmod(0o755)
        print_colored("✅ stop.sh script created", 'green')
        
    elif system == 'Windows':
        # Create start.bat
        start_script = Path(install_dir) / 'start.bat'
        start_content = """@echo off
chcp 65001 >nul
echo ========================================
echo 🤖 irProLink Bot - Starting
echo ========================================

REM Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found
    echo Please install Python 3.6 or higher
    pause
    exit /b 1
)

REM Check .env file
if not exist ".env" (
    if exist ".env.example" (
        echo ⚠️ .env file not found. Creating from .env.example...
        copy ".env.example" ".env"
        echo ✅ .env file created. Please edit it and set your BOT_TOKEN
        pause
        exit /b 1
    ) else (
        echo ❌ ERROR: .env file not found
        pause
        exit /b 1
    )
)

REM Check BOT_TOKEN
findstr /C:"BOT_TOKEN=YOUR_BOT_TOKEN_HERE" ".env" >nul
if %errorlevel% equ 0 (
    echo ❌ ERROR: BOT_TOKEN not set in .env file
    echo Please edit .env file and set your bot token
    pause
    exit /b 1
)

REM Create directories
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "temp" mkdir temp

echo ✅ All checks passed
echo 🚀 Starting bot...

REM Run the bot
python main.py

if %errorlevel% equ 0 (
    echo ✅ Bot stopped normally
) else (
    echo ❌ Bot stopped with error
)

echo === irProLink Bot Stopped ===
pause
"""
        
        with open(start_script, 'w', encoding='utf-8') as f:
            f.write(start_content)
        
        print_colored("✅ start.bat script created", 'green')
        
        # Create stop.bat
        stop_script = Path(install_dir) / 'stop.bat'
        stop_content = """@echo off
chcp 65001 >nul
echo ========================================
echo 🤖 irProLink Bot - Stopping
echo ========================================

REM Find and kill Python processes running main.py
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq main.py" 2>nul | findstr /I "python" >nul
if %errorlevel% equ 0 (
    echo Stopping bot processes...
    taskkill /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq main.py" /F >nul 2>nul
    echo ✅ Bot stopped
) else (
    echo ✅ Bot is not running
)

echo === Stop Script Finished ===
pause
"""
        
        with open(stop_script, 'w', encoding='utf-8') as f:
            f.write(stop_content)
        
        print_colored("✅ stop.bat script created", 'green')
        
    else:
        print_colored(f"⚠️ Unsupported operating system: {system}", 'yellow')
        print_colored("Please create startup scripts manually.", 'blue')
    
    return True

def setup_cron_job(install_dir):
    """Setup cron job for auto-start (Linux only)"""
    print_colored("\n🕐 Setting up auto-start...", 'blue')
    
    system = platform.system()
    
    if system == 'Linux':
        print_colored("📝 Cron job setup for Linux:", 'yellow')
        print_colored("To run bot on system startup:", 'blue')
        print_colored(f"1. Edit crontab: crontab -e", 'green')
        print_colored(f"2. Add this line:", 'blue')
        print_colored(f"   @reboot cd {install_dir} && ./start.sh", 'green')
        print_colored(f"3. Save and exit", 'blue')
    elif system == 'Windows':
        print_colored("📝 Task scheduler setup for Windows:", 'yellow')
        print_colored("To run bot on system startup:", 'blue')
        print_colored(f"1. Open Task Scheduler", 'green')
        print_colored(f"2. Create a new task that runs:", 'blue')
        print_colored(f"   {install_dir}\\start.bat", 'green')
        print_colored(f"3. Set trigger to 'At startup'", 'blue')
    else:
        print_colored("⚠️ Auto-start setup not available for this OS", 'yellow')
    
    return True

def main():
    """Main installation function"""
    # Import version module
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from version import get_version, get_release_year
        version = get_version()
        release_year = get_release_year()
    except ImportError:
        version = "6.1.0"
        release_year = "2026"
    
    print_colored("=" * 50, 'blue')
    print_colored("🤖 irProLink Bot Installation", 'blue')
    print_colored(f"🚀 Version: {version} (Improved)", 'blue')
    print_colored(f"📅 Release Year: {release_year}", 'blue')
    print_colored("=" * 50, 'blue')
    
    # Step 1: Get installation directory
    install_dir = get_installation_directory()
    
    # Step 2: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 3: Copy project files
    if not copy_project_files(install_dir):
        print_colored("❌ Failed to copy project files", 'red')
        sys.exit(1)
    
    # Step 4: Create necessary directories
    if not create_directories(install_dir):
        print_colored("⚠️ Some directories could not be created", 'yellow')
    
    # Step 5: Install dependencies
    if not install_dependencies(install_dir):
        print_colored("⚠️ Dependency installation had issues", 'yellow')
        print_colored("You may need to install dependencies manually", 'blue')
    
    # Step 6: Create .env file
    if not create_env_file(install_dir):
        print_colored("⚠️ .env file setup had issues", 'yellow')
    
    # Step 7: Setup startup scripts
    if not setup_start_scripts(install_dir):
        print_colored("⚠️ Startup script setup had issues", 'yellow')
    
    # Step 8: Setup auto-start
    setup_cron_job(install_dir)
    
    # Final summary
    print_colored("\n" + "=" * 50, 'green')
    print_colored("✅ Installation completed successfully!", 'green')
    print_colored("=" * 50, 'green')
    
    print_colored(f"\n📁 Installation directory: {install_dir}", 'yellow')
    print_colored("\n📋 Next steps:", 'yellow')
    print_colored("1. Edit .env file and set your BOT_TOKEN:", 'blue')
    print_colored(f"   cd {install_dir}", 'green')
    print_colored(f"   nano .env  (or edit with any text editor)", 'green')
    print_colored("2. Start the bot:", 'blue')
    
    system = platform.system()
    if system == 'Linux':
        print_colored(f"   cd {install_dir} && ./start.sh", 'green')
    elif system == 'Windows':
        print_colored(f"   cd {install_dir} && start.bat", 'green')
    else:
        print_colored(f"   cd {install_dir} && python main.py", 'green')
    
    print_colored("3. Check logs:", 'blue')
    print_colored(f"   tail -f {install_dir}/logs/bot.log", 'green')
    
    print_colored("\n💡 Tips:", 'yellow')
    print_colored("• Make sure you have write permissions in the installation directory", 'blue')
    print_colored("• For shared hosting, use '--user' flag for pip install", 'blue')
    print_colored("• Check firewall settings if bot cannot connect", 'blue')
    
    print_colored("\n📞 Support: @linkprosup", 'yellow')
    print_colored("🤖 Bot: @irprolinkbot", 'yellow')

if __name__ == "__main__":
    main()
