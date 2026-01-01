"""
تنظیمات پایه ربات irProLink
"""

import os
from pathlib import Path

# مسیرهای پروژه
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"

# تنظیمات فایل
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2 گیگابایت
ALLOWED_EXTENSIONS = {
    "jpg", "jpeg", "png", "gif", "bmp", "webp",  # تصاویر
    "mp4", "avi", "mkv", "mov", "wmv", "flv",  # ویدیوها
    "mp3", "wav", "ogg", "flac", "m4a",  # صوت
    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",  # اسناد
    "zip", "rar", "7z", "tar", "gz",  # آرشیو
    "txt", "csv", "json", "xml", "yaml", "yml",  # متن
}

# تنظیمات دانلود
REQUEST_TIMEOUT = 30
RETRY_ATTEMPTS = 3
PARALLEL_DOWNLOADS = 3

# تنظیمات تلگرام
TELEGRAM_API_URL = "https://api.telegram.org/bot"
TELEGRAM_FILE_URL = "https://api.telegram.org/file/bot"

# تنظیمات نمایش
DEFAULT_COPYRIGHT_TEXT = "دانلود شده توسط ربات : @prolinkbot"
SHORT_LINK_SERVICES = ["is.gd", "tinyurl.com", "short.io"]

# تنظیمات امنیتی
BLOCKED_EXTENSIONS = ["exe", "scr", "bat", "cmd", "msi", "vbs", "ps1", "sh"]
RATE_LIMIT_PER_MINUTE = 10
RATE_LIMIT_PER_DAY = 100

# تنظیمات ادمین
DEFAULT_ADMIN_IDS = [7660976743]
SUPPORT_USERNAME = "@linkprosup"

# تنظیمات دیتابیس (اگر استفاده شود)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/bot.db")

# ایجاد دایرکتوری‌های لازم
for directory in [DATA_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)
