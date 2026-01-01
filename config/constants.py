"""
ثابت‌های ربات irProLink
"""

# وضعیت‌های کاربر
USER_STATE_IDLE = "idle"
USER_STATE_WAITING_FOR_URL = "waiting_for_url"
USER_STATE_WAITING_FOR_FILE = "waiting_for_file"
USER_STATE_WAITING_FOR_CHANNEL = "waiting_for_channel"

# دستورات ربات
COMMAND_START = "/start"
COMMAND_HELP = "/help"
COMMAND_STATS = "/stats"
COMMAND_BROADCAST = "/broadcast"
COMMAND_SETTINGS = "/settings"
COMMAND_ADMIN = "/admin"

# پیام‌های سیستم
MESSAGES = {
    "welcome": "👋 سلام! به ربات irProLink خوش آمدید.\n\n"
               "من می‌توانم فایل‌های شما را از لینک مستقیم دانلود و در تلگرام آپلود کنم.\n\n"
               "📁 حداکثر حجم فایل: ۲ گیگابایت\n"
               "⚡ پشتیبانی از اکثر فرمت‌ها\n"
               "🔗 کوتاه‌کننده لینک خودکار\n\n"
               "لطفاً لینک مستقیم فایل را ارسال کنید:",

    "help": "📖 راهنمای استفاده:\n\n"
            "۱. لینک مستقیم فایل را ارسال کنید\n"
            "۲. ربات فایل را دانلود می‌کند\n"
            "۳. فایل در تلگرام آپلود می‌شود\n\n"
            "📌 نکات مهم:\n"
            "• لینک باید مستقیم باشد (مثل: https://example.com/file.zip)\n"
            "• حداکثر حجم: ۲ گیگابایت\n"
            "• فرمت‌های مجاز: تصاویر، ویدیو، صوت، اسناد، آرشیو\n"
            "• برای پشتیبانی: @linkprosup",

    "invalid_url": "❌ لینک وارد شده معتبر نیست!\n"
                   "لطفاً یک لینک مستقیم (مستقیم به فایل) ارسال کنید.",

    "download_started": "⏳ در حال دانلود فایل...\n"
                        "لطفاً کمی صبر کنید.",

    "upload_started": "📤 در حال آپلود فایل به تلگرام...\n"
                      "این فرآیند ممکن است چند لحظه طول بکشد.",

    "success": "✅ فایل با موفقیت آپلود شد!",

    "error": "❌ خطایی رخ داد!\n"
             "لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.",

    "rate_limit": "⏰ شما درخواست‌های زیادی ارسال کرده‌اید!\n"
                  "لطفاً کمی صبر کنید و سپس دوباره تلاش کنید.",

    "file_too_large": "📁 حجم فایل بیش از حد مجاز است!\n"
                      "حداکثر حجم: ۲ گیگابایت",

    "extension_blocked": "🚫 این نوع فایل مجاز نیست!\n"
                         "لیست فرمت‌های مجاز در /help",

    "admin_only": "🔒 این دستور فقط برای ادمین‌ها قابل استفاده است!",
}

# کدهای خطا
ERROR_CODES = {
    "NETWORK_ERROR": 1001,
    "TIMEOUT_ERROR": 1002,
    "INVALID_URL": 1003,
    "FILE_TOO_LARGE": 1004,
    "EXTENSION_BLOCKED": 1005,
    "TELEGRAM_ERROR": 1006,
    "CONFIG_ERROR": 1007,
}

# تنظیمات پیش‌فرض
DEFAULT_CONFIG = {
    "display_settings": {
        "show_filename": True,
        "show_filesize": True,
        "show_source_url": True,
        "show_user_id": True,
        "show_copyright": True,
        "enable_short_link": True,
        "short_link_service": "is.gd",
        "copyright_text": "دانلود شده توسط ربات : @prolinkbot",
    },
    "security": {
        "enable_rate_limit": True,
        "max_requests_per_minute": 10,
        "max_requests_per_day": 100,
        "enable_anti_spam": True,
        "blocked_extensions": ["exe", "scr", "bat", "cmd", "msi", "vbs"],
    },
    "statistics": {
        "total_downloads": 0,
        "total_users": 0,
        "total_size_gb": 0.0,
        "last_active": "",
        "user_activity": {},
        "user_daily_requests": {},
    },
    "broadcast": {
        "enabled": True,
        "last_sent": "",
        "cooldown": 3600,
    },
    "admin_ids": [7660976743],
    "required_channels": [],
    "user_sessions": {},
}
