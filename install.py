#!/usr/bin/env python3
"""
اسکریپت نصب ربات برای هاست اشتراکی
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_colored(text, color):
    """چاپ متن رنگی"""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

def check_python_version():
    """بررسی نسخه پایتون"""
    if sys.version_info < (3, 6):
        print_colored("❌ نیاز به پایتون 3.6 یا بالاتر", 'red')
        return False
    print_colored(f"✅ پایتون {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", 'green')
    return True

def install_dependencies():
    """نصب وابستگی‌ها"""
    print_colored("📦 در حال نصب وابستگی‌ها...", 'blue')
    
    try:
        # نصب pip اگر وجود ندارد
        subprocess.check_call([sys.executable, '-m', 'pip', '--version'])
    except:
        print_colored("❌ pip یافت نشد", 'red')
        return False
    
    # نصب requirements با flag --user برای هاست اشتراکی
    requirements_file = Path(__file__).parent / 'requirements.txt'
    if requirements_file.exists():
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', '-r', str(requirements_file)])
            print_colored("✅ وابستگی‌ها نصب شدند", 'green')
            return True
        except subprocess.CalledProcessError:
            print_colored("❌ خطا در نصب وابستگی‌ها", 'red')
            return False
    else:
        print_colored("⚠️ فایل requirements.txt یافت نشد", 'yellow')
        return True

def create_env_file():
    """ایجاد فایل .env"""
    env_example = Path(__file__).parent / '.env.example'
    env_file = Path(__file__).parent / '.env'
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print_colored("✅ فایل .env ایجاد شد", 'green')
            print_colored("⚠️ لطفاً فایل .env را ویرایش و توکن ربات را تنظیم کنید", 'yellow')
        else:
            print_colored("⚠️ فایل .env.example یافت نشد", 'yellow')
    else:
        print_colored("✅ فایل .env از قبل وجود دارد", 'green')
    
    return True

def create_directories():
    """ایجاد دایرکتوری‌های لازم"""
    directories = ['data', 'logs', 'temp']
    base_dir = Path(__file__).parent
    
    for dir_name in directories:
        dir_path = base_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        print_colored(f"✅ دایرکتوری {dir_name} ایجاد شد", 'green')
    
    return True

def setup_cron_job():
    """تنظیم cron job برای اجرای خودکار"""
    print_colored("🕐 تنظیم cron job برای اجرای خودکار", 'blue')
    
    # مسیر فایل پایتون
    python_path = sys.executable
    main_script = Path(__file__).parent / 'main.py'
    script_dir = Path(__file__).parent
    
    cron_command = f"cd {script_dir} && {python_path} {main_script}"
    
    print_colored("📝 دستور cron:", 'yellow')
    print_colored(f"@reboot {cron_command}", 'blue')
    print_colored("📋 برای اضافه کردن به cron:", 'yellow')
    print_colored("1. دستور زیر را اجرا کنید:", 'blue')
    print_colored(f"   crontab -e", 'green')
    print_colored("2. خط زیر را اضافه کنید:", 'blue')
    print_colored(f"   @reboot {cron_command} > {script_dir}/logs/cron.log 2>&1", 'green')
    
    return True

def create_start_script():
    """ایجاد اسکریپت start.sh"""
    script_content = """#!/bin/bash
# اسکریپت شروع ربات irProLink

cd "$(dirname "$0")"

# فعال کردن محیط مجازی اگر وجود دارد
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# اجرای ربات
python3 main.py
"""
    
    start_script = Path(__file__).parent / 'start.sh'
    with open(start_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    start_script.chmod(0o755)
    print_colored("✅ اسکریپت start.sh ایجاد شد", 'green')
    
    return True

def create_stop_script():
    """ایجاد اسکریپت stop.sh"""
    script_content = """#!/bin/bash
# اسکریپت توقف ربات irProLink

# پیدا کردن PID ربات
PID=$(ps aux | grep "python3.*main.py" | grep -v grep | awk '{print $2}')

if [ -z "$PID" ]; then
    echo "ربات در حال اجرا نیست"
else
    kill $PID
    echo "ربات متوقف شد (PID: $PID)"
fi
"""
    
    stop_script = Path(__file__).parent / 'stop.sh'
    with open(stop_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    stop_script.chmod(0o755)
    print_colored("✅ اسکریپت stop.sh ایجاد شد", 'green')
    
    return True

def main():
    """تابع اصلی"""
    print_colored("=" * 50, 'blue')
    print_colored("🤖 نصب ربات irProLink برای هاست اشتراکی", 'blue')
    print_colored("🚀 نسخه: ۲۰۲۵.۱.۰", 'blue')
    print_colored("=" * 50, 'blue')
    
    # بررسی نسخه پایتون
    if not check_python_version():
        return
    
    # ایجاد دایرکتوری‌ها
    if not create_directories():
        return
    
    # نصب وابستگی‌ها
    if not install_dependencies():
        return
    
    # ایجاد فایل .env
    if not create_env_file():
        return
    
    # ایجاد اسکریپت‌ها
    create_start_script()
    create_stop_script()
    
    # تنظیم cron job
    setup_cron_job()
    
    print_colored("\n" + "=" * 50, 'green')
    print_colored("✅ نصب کامل شد!", 'green')
    print_colored("=" * 50, 'green')
    
    print_colored("\n📋 مراحل بعدی:", 'yellow')
    print_colored("1. فایل .env را ویرایش کنید:", 'blue')
    print_colored("   nano .env", 'green')
    print_colored("2. BOT_TOKEN را به توکن ربات خود تغییر دهید", 'blue')
    print_colored("3. ربات را اجرا کنید:", 'blue')
    print_colored("   ./start.sh", 'green')
    print_colored("4. برای توقف:", 'blue')
    print_colored("   ./stop.sh", 'green')
    
    print_colored("\n📞 پشتیبانی: @linkprosup", 'yellow')
    print_colored("🤖 ربات: @irprolinkbot", 'yellow')

if __name__ == "__main__":
    main()
