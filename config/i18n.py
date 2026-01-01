"""
Internationalization (i18n) system for the bot
"""

from typing import Dict, Any, Optional
from enum import Enum
import json
from pathlib import Path

class Language(str, Enum):
    """Supported languages"""
    ENGLISH = "en"
    PERSIAN = "fa"
    
    @classmethod
    def from_code(cls, code: str) -> 'Language':
        """Get language from code"""
        code = code.lower()
        if code in ['fa', 'persian', 'farsi']:
            return cls.PERSIAN
        return cls.ENGLISH

class Translator:
    """Translation system with fallback support"""
    
    def __init__(self, default_lang: Language = Language.ENGLISH):
        self.default_lang = default_lang
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load translation files"""
        translations_dir = Path(__file__).parent.parent / "translations"
        translations_dir.mkdir(exist_ok=True)
        
        # Load English translations
        en_file = translations_dir / "en.json"
        if en_file.exists():
            with open(en_file, 'r', encoding='utf-8') as f:
                self.translations['en'] = json.load(f)
        else:
            self.translations['en'] = self._get_default_english()
            with open(en_file, 'w', encoding='utf-8') as f:
                json.dump(self.translations['en'], f, ensure_ascii=False, indent=2)
        
        # Load Persian translations
        fa_file = translations_dir / "fa.json"
        if fa_file.exists():
            with open(fa_file, 'r', encoding='utf-8') as f:
                self.translations['fa'] = json.load(f)
        else:
            self.translations['fa'] = self._get_default_persian()
            with open(fa_file, 'w', encoding='utf-8') as f:
                json.dump(self.translations['fa'], f, ensure_ascii=False, indent=2)
    
    def _get_default_english(self) -> Dict[str, str]:
        """Default English translations"""
        return {
            # Common
            "error": "❌ Error",
            "success": "✅ Success",
            "warning": "⚠️ Warning",
            "info": "ℹ️ Info",
            
            # Bot commands
            "start": "🤖 Welcome to irProLink Bot!\n\n📋 **Main Commands:**\n• /start - Show help\n• /upload [link] - Upload file\n• /help - Complete guide\n• /support - Contact support\n• /status - Bot status\n• /mystats - User statistics\n\n📞 **Support:** {support_username}\n\n🚀 **Features:**\n• Upload up to 2GB\n• Complete file details\n• Short link: {short_link_status}\n• Service: {short_link_service}\n• All formats supported\n• Advanced security\n\n🔗 **Example:** `/upload https://example.com/file.zip`",
            
            "help": "📖 **Complete Bot Guide**\n\n🔗 **How to use:**\n1. Send direct file link\n2. Or use /upload command\n\n📝 **Example:**\n`/upload https://example.com/file.zip`\n\n📊 **Displayed details:**\n• Full filename {filename_status}\n• Size in MB {filesize_status}\n• Source link {sourceurl_status} {short_link_note}\n• User ID {userid_status}\n• Bot copyright {copyright_status}\n\n⚠️ **Limitations:**\n• Max size: {max_size} MB\n• Direct links only\n• Upload time: 5 minutes\n• Max requests: {max_per_minute}/minute\n• Daily requests: {max_per_day}\n\n❓ **Support:** {support_username}\n\n⚙️ **Admin commands:**\n(Only accessible to admins)",
            
            # Upload process
            "upload_started": "🔍 Checking link...",
            "download_started": "⏳ Downloading file...",
            "upload_in_progress": "📤 Uploading to Telegram...",
            "upload_success": "✅ File uploaded successfully!",
            "invalid_url": "❌ Invalid URL! Please send a direct link.",
            "file_too_large": "📁 File size exceeds limit! Max: {max_size}",
            "rate_limit_exceeded": "⏰ Too many requests! Please wait.",
            
            # Admin messages
            "admin_only": "⛔ Admin only!",
            "channel_added": "✅ Channel {channel} added to required channels",
            "channel_removed": "✅ Channel {channel} removed",
            "admin_added": "✅ ID {admin_id} added to admin list",
            "admin_removed": "✅ ID {admin_id} removed from admin list",
            
            # Settings
            "settings_saved": "✅ Settings saved successfully",
            "broadcast_sent": "✅ Broadcast message sent to {user_count} users",
            
            # Errors
            "network_error": "❌ Network error",
            "timeout_error": "❌ Timeout error",
            "server_error": "❌ Server error",
            "unknown_error": "❌ Unknown error",
        }
    
    def _get_default_persian(self) -> Dict[str, str]:
        """Default Persian translations"""
        return {
            # Common
            "error": "❌ خطا",
            "success": "✅ موفق",
            "warning": "⚠️ اخطار",
            "info": "ℹ️ اطلاعات",
            
            # Bot commands
            "start": "🤖 به ربات irProLink خوش آمدید!\n\n📋 **دستورات اصلی:**\n• /start - نمایش راهنما\n• /upload [لینک] - آپلود فایل\n• /help - راهنمای کامل\n• /support - تماس با پشتیبانی\n• /status - وضعیت ربات\n• /mystats - آمار کاربری\n\n📞 **پشتیبانی:** {support_username}\n\n🚀 **ویژگی‌ها:**\n• آپلود تا ۲ گیگابایت\n• نمایش جزئیات کامل فایل\n• لینک کوتاه: {short_link_status}\n• سرویس: {short_link_service}\n• پشتیبانی از همه فرمت‌ها\n• امنیت پیشرفته\n\n🔗 **مثال:** `/upload https://example.com/file.zip`",
            
            "help": "📖 **راهنمای کامل ربات**\n\n🔗 **نحوه استفاده:**\n۱. لینک مستقیم فایل را ارسال کنید\n۲. یا از دستور /upload استفاده کنید\n\n📝 **مثال:**\n`/upload https://example.com/file.zip`\n\n📊 **جزئیات نمایش داده شده:**\n• نام کامل فایل {filename_status}\n• حجم به مگابایت {filesize_status}\n• لینک منبع {sourceurl_status} {short_link_note}\n• آیدی کاربر {userid_status}\n• کپی رایت ربات {copyright_status}\n\n⚠️ **محدودیت‌ها:**\n• حداکثر حجم: {max_size} مگابایت\n• فقط لینک‌های مستقیم\n• زمان آپلود: ۵ دقیقه\n• حداکثر درخواست: {max_per_minute} در دقیقه\n• حداکثر درخواست روزانه: {max_per_day}\n\n❓ **پشتیبانی:** {support_username}\n\n⚙️ **دستورات ادمین:**\n(فقط برای مدیران قابل دسترسی است)",
            
            # Upload process
            "upload_started": "🔍 در حال بررسی لینک...",
            "download_started": "⏳ در حال دانلود فایل...",
            "upload_in_progress": "📤 در حال آپلود به تلگرام...",
            "upload_success": "✅ فایل با موفقیت آپلود شد!",
            "invalid_url": "❌ لینک نامعتبر! لطفاً لینک مستقیم ارسال کنید.",
            "file_too_large": "📁 حجم فایل بیش از حد مجاز! حداکثر: {max_size}",
            "rate_limit_exceeded": "⏰ درخواست‌های زیادی ارسال کرده‌اید! لطفاً صبر کنید.",
            
            # Admin messages
            "admin_only": "⛔ فقط ادمین!",
            "channel_added": "✅ کانال {channel} به لیست کانال‌های اجباری اضافه شد",
            "channel_removed": "✅ کانال {channel} حذف شد",
            "admin_added": "✅ آیدی {admin_id} به لیست ادمین‌ها اضافه شد",
            "admin_removed": "✅ آیدی {admin_id} از لیست ادمین‌ها حذف شد",
            
            # Settings
            "settings_saved": "✅ تنظیمات با موفقیت ذخیره شد",
            "broadcast_sent": "✅ پیام همگانی به {user_count} کاربر ارسال شد",
            
            # Errors
            "network_error": "❌ خطای شبکه",
            "timeout_error": "❌ خطای زمان‌بندی",
            "server_error": "❌ خطای سرور",
            "unknown_error": "❌ خطای ناشناخته",
        }
    
    def get(self, key: str, lang: Optional[Language] = None, **kwargs) -> str:
        """Get translation for key with formatting"""
        lang_obj = lang or self.default_lang
        lang_code = lang_obj.value
        
        # Get translation with fallback
        translation = self.translations.get(lang_code, {}).get(key)
        if not translation:
            # Fallback to English
            translation = self.translations.get('en', {}).get(key, key)
        
        # Format with kwargs
        try:
            return translation.format(**kwargs)
        except (KeyError, ValueError):
            return translation
    
    def set_user_language(self, user_id: int, language: Language):
        """Set user language preference"""
        # This would typically save to database
        # For now, we'll implement a simple in-memory store
        pass
    
    def get_user_language(self, user_id: int) -> Language:
        """Get user language preference"""
        # This would typically load from database
        # For now, default to English
        return self.default_lang

# Global translator instance
translator = Translator()
