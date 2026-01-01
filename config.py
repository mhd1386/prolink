"""
Configuration management for the bot
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import aiofiles
from pathlib import Path
from dotenv import load_dotenv
import asyncio

from config.i18n import translator, Language

logger = logging.getLogger(__name__)

@dataclass
class DisplaySettings:
    show_filename: bool = True
    show_filesize: bool = True
    show_source_url: bool = True
    show_user_id: bool = True
    show_copyright: bool = True
    enable_short_link: bool = True
    short_link_service: str = "is.gd"
    copyright_text: str = "Downloaded by bot: @prolinkbot"

@dataclass
class SecuritySettings:
    enable_rate_limit: bool = True
    max_requests_per_minute: int = 10
    max_requests_per_day: int = 100  # Daily limit
    enable_anti_spam: bool = True
    blocked_extensions: List[str] = field(default_factory=lambda: ["exe", "scr", "bat", "cmd", "msi", "vbs", "ps1", "sh"])

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
    user_languages: Dict[str, str] = field(default_factory=dict)  # user_id -> language_code
    
    @classmethod
    async def load(cls, config_path: str = "data/config.json") -> 'AppConfig':
        """Load settings from JSON file"""
        try:
            if os.path.exists(config_path):
                async with aiofiles.open(config_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
                    
                    # Convert dictionary to object
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
                        user_sessions=data.get('user_sessions', {}),
                        user_languages=data.get('user_languages', {})
                    )
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
        
        # If file doesn't exist or error, return default settings
        return cls()
    
    async def save(self, config_path: str = "data/config.json") -> bool:
        """Save settings to JSON file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Convert to dictionary
            data = {
                'display_settings': asdict(self.display_settings),
                'security': asdict(self.security),
                'statistics': asdict(self.statistics),
                'broadcast': asdict(self.broadcast),
                'admin_ids': self.admin_ids,
                'required_channels': self.required_channels,
                'user_sessions': self.user_sessions,
                'user_languages': self.user_languages
            }
            
            async with aiofiles.open(config_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.admin_ids
    
    def get_user_language(self, user_id: int) -> Language:
        """Get user language preference"""
        user_id_str = str(user_id)
        lang_code = self.user_languages.get(user_id_str, "en")
        return Language.from_code(lang_code)
    
    def set_user_language(self, user_id: int, language: Language):
        """Set user language preference"""
        user_id_str = str(user_id)
        self.user_languages[user_id_str] = language.value
    
    def check_rate_limit(self, user_id: int) -> Tuple[bool, str]:
        """
        Check rate limit for user
        Returns: (is_allowed, error_message)
        """
        if not self.security.enable_rate_limit:
            return True, ""
        
        user_id_str = str(user_id)
        now = datetime.now(timezone.utc)
        current_minute = now.strftime("%Y-%m-%d %H:%M")
        current_date = now.strftime("%Y-%m-%d")
        
        # Initialize user session
        if user_id_str not in self.user_sessions:
            self.user_sessions[user_id_str] = {
                'minute_requests': {},
                'daily_requests': {}
            }
        
        user_session = self.user_sessions[user_id_str]
        
        # Check minute limit
        minute_requests = user_session.get('minute_requests', {})
        current_count = minute_requests.get(current_minute, 0)
        
        if current_count >= self.security.max_requests_per_minute:
            user_lang = self.get_user_language(user_id)
            error_msg = translator.get("rate_limit_exceeded", user_lang)
            return False, error_msg
        
        # Check daily limit
        daily_requests = user_session.get('daily_requests', {})
        daily_count = daily_requests.get(current_date, 0)
        
        if daily_count >= self.security.max_requests_per_day:
            user_lang = self.get_user_language(user_id)
            error_msg = translator.get("rate_limit_exceeded", user_lang)
            return False, error_msg
        
        return True, ""
    
    def increment_request_count(self, user_id: int):
        """Increment request counter for user"""
        user_id_str = str(user_id)
        now = datetime.now(timezone.utc)
        current_minute = now.strftime("%Y-%m-%d %H:%M")
        current_date = now.strftime("%Y-%m-%d")
        
        if user_id_str not in self.user_sessions:
            self.user_sessions[user_id_str] = {
                'minute_requests': {},
                'daily_requests': {}
            }
        
        user_session = self.user_sessions[user_id_str]
        
        # Increment minute counter
        minute_requests = user_session.get('minute_requests', {})
        minute_requests[current_minute] = minute_requests.get(current_minute, 0) + 1
        user_session['minute_requests'] = minute_requests
        
        # Increment daily counter
        daily_requests = user_session.get('daily_requests', {})
        daily_requests[current_date] = daily_requests.get(current_date, 0) + 1
        user_session['daily_requests'] = daily_requests
        
        # Cleanup old data (minute)
        for minute in list(minute_requests.keys()):
            if minute != current_minute:
                del minute_requests[minute]
        
        # Cleanup old data (daily - older than 30 days)
        for date in list(daily_requests.keys()):
            if date != current_date:
                try:
                    date_obj = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    if (now - date_obj).days > 30:
                        del daily_requests[date]
                except:
                    pass
    
    def increment_statistics(self, user_id: int, file_size: int):
        """Increment global statistics"""
        self.statistics.total_downloads += 1
        self.statistics.total_size_gb += file_size / (1024 ** 3)  # Convert to GB
        self.statistics.last_active = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        user_id_str = str(user_id)
        self.statistics.user_activity[user_id_str] = self.statistics.user_activity.get(user_id_str, 0) + 1
        self.statistics.total_users = len(self.statistics.user_activity)
    
    def can_send_broadcast(self) -> bool:
        """Check if broadcast can be sent"""
        if not self.broadcast.enabled:
            return False
        
        if not self.broadcast.last_sent:
            return True
        
        try:
            last_sent = datetime.strptime(self.broadcast.last_sent, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            elapsed = (now - last_sent).total_seconds()
            return elapsed >= self.broadcast.cooldown
        except:
            return True
    
    def update_broadcast_time(self):
        """Update last broadcast time"""
        self.broadcast.last_sent = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# Environment configuration
class EnvironmentConfig:
    def __init__(self):
        # Load from .env file
        load_dotenv()
        
        # Core settings
        self.bot_token = os.getenv("BOT_TOKEN", "")
        self.support_username = os.getenv("SUPPORT_USERNAME", "@linkprosup")
        self.main_admin_id = int(os.getenv("MAIN_ADMIN_ID", "7660976743"))
        
        # Download settings
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "2147483648"))  # 2GB
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.retry_attempts = int(os.getenv("RETRY_ATTEMPTS", "3"))
        self.parallel_downloads = int(os.getenv("PARALLEL_DOWNLOADS", "3"))
        
        # CDN settings
        self.enable_cdn = os.getenv("ENABLE_CDN", "false").lower() == "true"
        self.cdn_provider = os.getenv("CDN_PROVIDER", "cloudflare")
        self.cdn_url = os.getenv("CDN_URL", "")
        
        # Update settings
        self.enable_auto_update = os.getenv("ENABLE_AUTO_UPDATE", "false").lower() == "true"
        self.update_repository = os.getenv("UPDATE_REPOSITORY", "https://github.com/mhd1386/prolink.git")
        self.update_branch = os.getenv("UPDATE_BRANCH", "main")
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.enable_file_logging = os.getenv("ENABLE_FILE_LOGGING", "true").lower() == "true"
    
    def validate(self) -> bool:
        """Validate environment configuration"""
        if not self.bot_token or self.bot_token == "YOUR_BOT_TOKEN_HERE":
            logger.error("BOT_TOKEN is not set!")
            logger.error("Please edit .env file and set your bot token.")
            return False
        return True


# Global instances
env_config = EnvironmentConfig()
app_config: Optional[AppConfig] = None

async def get_config() -> AppConfig:
    """Get configuration instance (load if necessary)"""
    global app_config
    if app_config is None:
        app_config = await AppConfig.load()
    return app_config
