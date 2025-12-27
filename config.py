import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import aiofiles
from pathlib import Path
from dotenv import load_dotenv

@dataclass
class DisplaySettings:
    show_filename: bool = True
    show_filesize: bool = True
    show_source_url: bool = True
    show_user_id: bool = True
    show_copyright: bool = True
    enable_short_link: bool = True
    short_link_service: str = "is.gd"
    copyright_text: str = "دانلود شده توسط ربات : @prolinkbot"

@dataclass
class SecuritySettings:
    enable_rate_limit: bool = True
    max_requests_per_minute: int = 10
    max_requests_per_day: int = 100  # جدید: محدودیت روزانه
    enable_anti_spam: bool = True
    blocked_extensions: List[str] = field(default_factory=lambda: ["exe", "scr", "bat", "cmd", "msi", "vbs"])

@dataclass
class Statistics:
    total_downloads: int = 0
    total_users: int = 0
    total_size_gb: float = 0.0
    last_active: str = ""
    user_activity: Dict[str, int] = field(default_factory=dict)  # user_id -> download_count
    user_daily_requests: Dict[str, Dict[str, int]] = field(default_factory=dict)  # user_id -> {date: count}

@dataclass
class BroadcastSettings:
    enabled: bool = True
    last_sent: str = ""
    cooldown: int = 3600

@dataclass
class AppConfig:
    display_settings: DisplaySettings = field(default_factory=DisplaySettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)
    statistics: Statistics = field(default_factory=Statistics)
    broadcast: BroadcastSettings = field(default_factory=BroadcastSettings)
    admin_ids: List[int] = field(default_factory=lambda: [7660976743])
    required_channels: List[str] = field(default_factory=list)
    user_sessions: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # user_id -> session_data
    
    @classmethod
    async def load(cls, config_path: str = "data/config.json") -> 'AppConfig':
        """بارگذاری تنظیمات از فایل JSON"""
        try:
            if os.path.exists(config_path):
                async with aiofiles.open(config_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
                    
                    # تبدیل دیکشنری به آبجکت
                    display = DisplaySettings(**data.get('display_settings', {}))
                    security = SecuritySettings(**data.get('security', {}))
                    stats = Statistics(**data.get('statistics', {}))
                    broadcast = BroadcastSettings(**data.get('broadcast', {}))
                    
                    return cls(
                        display_settings=display,
                        security=security,
                        statistics=stats,
                        broadcast=broadcast,
                        admin_ids=data.get('admin_ids', [7660976743]),
                        required_channels=data.get('required_channels', []),
                        user_sessions=data.get('user_sessions', {})
                    )
        except Exception as e:
            print(f"خطا در بارگذاری تنظیمات: {e}")
        
        # اگر فایل وجود نداشت یا خطا داشت، تنظیمات پیش‌فرض
        return cls()
    
    async def save(self, config_path: str = "data/config.json") -> bool:
        """ذخیره تنظیمات در فایل JSON"""
        try:
            # ایجاد دایرکتوری اگر وجود ندارد
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # تبدیل به دیکشنری
            data = {
                'display_settings': asdict(self.display_settings),
                'security': asdict(self.security),
                'statistics': asdict(self.statistics),
                'broadcast': asdict(self.broadcast),
                'admin_ids': self.admin_ids,
                'required_channels': self.required_channels,
                'user_sessions': self.user_sessions
            }
            
            async with aiofiles.open(config_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            
            return True
        except Exception as e:
            print(f"خطا در ذخیره تنظیمات: {e}")
            return False
    
    def is_admin(self, user_id: int) -> bool:
        """بررسی اینکه کاربر ادمین است یا نه"""
        return user_id in self.admin_ids
    
    def check_rate_limit(self, user_id: int) -> tuple[bool, str]:
        """
        بررسی محدودیت نرخ درخواست
        بازگشت: (مجاز است, پیام خطا)
        """
        if not self.security.enable_rate_limit:
            return True, ""
        
        user_id_str = str(user_id)
        now = datetime.now()
        current_minute = now.strftime("%Y-%m-%d %H:%M")
        current_date = now.strftime("%Y-%m-%d")
        
        # مقداردهی اولیه session کاربر
        if user_id_str not in self.user_sessions:
            self.user_sessions[user_id_str] = {
                'minute_requests': {},
                'daily_requests': {}
            }
        
        user_session = self.user_sessions[user_id_str]
        
        # بررسی محدودیت دقیقه‌ای
        minute_requests = user_session.get('minute_requests', {})
        current_count = minute_requests.get(current_minute, 0)
        
        if current_count >= self.security.max_requests_per_minute:
            return False, f"⏰ محدودیت درخواست در دقیقه! حداکثر {self.security.max_requests_per_minute} درخواست در دقیقه مجاز است."
        
        # بررسی محدودیت روزانه
        daily_requests = user_session.get('daily_requests', {})
        daily_count = daily_requests.get(current_date, 0)
        
        if daily_count >= self.security.max_requests_per_day:
            return False, f"📅 محدودیت درخواست روزانه! حداکثر {self.security.max_requests_per_day} درخواست در روز مجاز است."
        
        return True, ""
    
    def increment_request_count(self, user_id: int):
        """افزایش شمارنده درخواست کاربر"""
        user_id_str = str(user_id)
        now = datetime.now()
        current_minute = now.strftime("%Y-%m-%d %H:%M")
        current_date = now.strftime("%Y-%m-%d")
        
        if user_id_str not in self.user_sessions:
            self.user_sessions[user_id_str] = {
                'minute_requests': {},
                'daily_requests': {}
            }
        
        user_session = self.user_sessions[user_id_str]
        
        # افزایش شمارنده دقیقه‌ای
        minute_requests = user_session.get('minute_requests', {})
        minute_requests[current_minute] = minute_requests.get(current_minute, 0) + 1
        user_session['minute_requests'] = minute_requests
        
        # افزایش شمارنده روزانه
        daily_requests = user_session.get('daily_requests', {})
        daily_requests[current_date] = daily_requests.get(current_date, 0) + 1
        user_session['daily_requests'] = daily_requests
        
        # پاکسازی داده‌های قدیمی (دقیقه‌ای)
        for minute in list(minute_requests.keys()):
            if minute != current_minute:
                del minute_requests[minute]
        
        # پاکسازی داده‌های قدیمی (روزانه - بیش از 30 روز)
        for date in list(daily_requests.keys()):
            if date != current_date:
                try:
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    if (now - date_obj).days > 30:
                        del daily_requests[date]
                except:
                    pass
    
    def increment_statistics(self, user_id: int, file_size: int):
        """افزایش آمار کلی"""
        self.statistics.total_downloads += 1
        self.statistics.total_size_gb += file_size / (1024 ** 3)  # تبدیل به گیگابایت
        self.statistics.last_active = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        user_id_str = str(user_id)
        self.statistics.user_activity[user_id_str] = self.statistics.user_activity.get(user_id_str, 0) + 1
        self.statistics.total_users = len(self.statistics.user_activity)
    
    def can_send_broadcast(self) -> bool:
        """بررسی امکان ارسال پیام همگانی"""
        if not self.broadcast.enabled:
            return False
        
        if not self.broadcast.last_sent:
            return True
        
        try:
            last_sent = datetime.strptime(self.broadcast.last_sent, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            elapsed = (now - last_sent).total_seconds()
            return elapsed >= self.broadcast.cooldown
        except:
            return True
    
    def update_broadcast_time(self):
        """به‌روزرسانی زمان آخرین پیام همگانی"""
        self.broadcast.last_sent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# تنظیمات محیطی
class EnvironmentConfig:
    def __init__(self):
        self.bot_token = os.getenv("BOT_TOKEN", "")
        self.support_username = os.getenv("SUPPORT_USERNAME", "@linkprosup")
        self.main_admin_id = int(os.getenv("MAIN_ADMIN_ID", "7660976743"))
        
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "2147483648"))
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.retry_attempts = int(os.getenv("RETRY_ATTEMPTS", "3"))
        self.parallel_downloads = int(os.getenv("PARALLEL_DOWNLOADS", "3"))
        
        # بارگذاری از فایل .env
        load_dotenv()
    
    def validate(self) -> bool:
        """اعتبارسنجی تنظیمات محیطی"""
        if not self.bot_token or self.bot_token == "YOUR_BOT_TOKEN_HERE":
            print("❌ خطا: BOT_TOKEN تنظیم نشده است!")
            print("لطفاً فایل .env را ویرایش کنید و توکن ربات خود را وارد کنید.")
            return False
        return True


# نمونه‌های سراسری
env_config = EnvironmentConfig()
app_config: Optional[AppConfig] = None

async def get_config() -> AppConfig:
    """دریافت نمونه پیکربندی (با لود کردن اگر لازم باشد)"""
    global app_config
    if app_config is None:
        app_config = await AppConfig.load()
    return app_config
