#!/usr/bin/env python3
"""
ربات تلگرام irProLink - نسخه پایتون
ربات حرفه‌ای آپلود فایل با مدیریت پیشرفته
"""

import asyncio
import logging
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه به sys.path
sys.path.insert(0, str(Path(__file__).parent))

from bot.bot import TelegramBot
from config import env_config

# تنظیمات لاگ‌گیری
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """تابع اصلی اجرای ربات"""
    print("=" * 50)
    print("🤖 ربات irProLink - نسخه پایتون")
    print("🚀 نسخه: ۲۰۲۵.۱.۰")
    print("📅 تاریخ: ۱۴۰۴/۱۰/۰۴")
    print("👑 مدیر اصلی: 7660976743")
    print("=" * 50)
    
    # اعتبارسنجی تنظیمات محیطی
    if not env_config.validate():
        sys.exit(1)
    
    try:
        # ایجاد نمونه ربات
        bot = TelegramBot()
        
        # راه‌اندازی ربات
        await bot.setup()
        
        # اجرای ربات
        logger.info("ربات در حال راه‌اندازی...")
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("ربات توسط کاربر متوقف شد.")
    except Exception as e:
        logger.error(f"خطای غیرمنتظره: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    # ایجاد دایرکتوری‌های لازم
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    # اجرای ربات (سازگار با پایتون 3.6)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
