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

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 6):
        print_colored("❌ Python 3.6 or higher required", 'red')
        return False
    print_colored(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", 'green')
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
# irProLink bot start script

cd "$(dirname "$0")"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the bot
python3 main.py
"""
    
    start_script = Path(__file__).parent / 'start.sh'
    with open(start_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    start_script.chmod(0o755)
    print_colored("✅ start.sh script created", 'green')
    
    return True

def create_stop_script():
    """Create stop.sh script"""
    script_content = """#!/bin/bash
# irProLink bot stop script

# Find bot PID
PID=$(ps aux | grep "python3.*main.py" | grep -v grep | awk '{print $2}')

if [ -z "$PID" ]; then
    echo "Bot is not running"
else
    kill $PID
    echo "Bot stopped (PID: $PID)"
fi
"""
    
    stop_script = Path(__file__).parent / 'stop.sh'
    with open(stop_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    stop_script.chmod(0o755)
    print_colored("✅ stop.sh script created", 'green')
    
    return True

def main():
    """Main function"""
    print_colored("=" * 50, 'blue')
    print_colored("🤖 irProLink Bot Installation for Shared Hosting", 'blue')
    print_colored("🚀 Version: 6.0.0 (2026)", 'blue')
    print_colored("=" * 50, 'blue')
    
    # Check Python version
    if not check_python_version():
        return
    
    # Create directories
    if not create_directories():
        return
    
    # Install dependencies
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
    
    print_colored("\n📋 Next steps:", 'yellow')
    print_colored("1. Edit .env file:", 'blue')
    print_colored("   nano .env", 'green')
    print_colored("2. Change BOT_TOKEN to your bot token", 'blue')
    print_colored("3. Start the bot:", 'blue')
    print_colored("   ./start.sh", 'green')
    print_colored("4. To stop:", 'blue')
    print_colored("   ./stop.sh", 'green')
    
    print_colored("\n📞 Support: @linkprosup", 'yellow')
    print_colored("🤖 Bot: @irprolinkbot", 'yellow')

if __name__ == "__main__":
    main()
