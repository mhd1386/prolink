"""
ماژول اصلی ربات تلگرام
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import env_config, get_config
from handlers import register_handlers
from middleware import RateLimitMiddleware, AdminMiddleware
from utils.shortlink import ShortLinkService
from utils.downloader import DownloadManager

logger = logging.getLogger(__name__)

class TelegramBot:
    """کلاس اصلی ربات تلگرام"""
    
    def __init__(self):
        self.bot: Optional[Bot] = None
        self.dp: Optional[Dispatcher] = None
        self.config = None
        self.shortlink_service: Optional[ShortLinkService] = None
        self.download_manager: Optional[DownloadManager] = None
        
    async def setup(self):
        """راه‌اندازی اولیه ربات"""
        # بارگذاری تنظیمات
        self.config = await get_config()
        
        # ایجاد نمونه ربات
        self.bot = Bot(
            token=env_config.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # ایجاد dispatcher
        self.dp = Dispatcher()
        
        # ایجاد سرویس‌ها
        self.shortlink_service = ShortLinkService()
        self.download_manager = DownloadManager(
            max_file_size=env_config.max_file_size,
            parallel_downloads=env_config.parallel_downloads
        )
        
        # ثبت middleware
        self.dp.message.middleware(RateLimitMiddleware())
        self.dp.message.middleware(AdminMiddleware())
        
        # ثبت هندلرها
        await register_handlers(self.dp, self)
        
        # تنظیم command list
        await self.set_bot_commands()
        
    async def set_bot_commands(self):
        """تنظیم لیست دستورات ربات"""
        commands = [
            types.BotCommand(command="start", description="📋 راهنمای ربات"),
            types.BotCommand(command="help", description="🆘 راهنمای کامل"),
            types.BotCommand(command="upload", description="📤 آپلود فایل از URL"),
            types.BotCommand(command="support", description="📞 تماس با پشتیبانی"),
            types.BotCommand(command="status", description="📊 وضعیت ربات"),
            types.BotCommand(command="mystats", description="📈 آمار کاربر"),
        ]
        
        # اضافه کردن دستورات ادمین
        admin_commands = [
            types.BotCommand(command="addchannel", description="➕ اضافه کردن کانال اجباری"),
            types.BotCommand(command="removechannel", description="➖ حذف کانال اجباری"),
            types.BotCommand(command="listchannels", description="📋 لیست کانال‌ها"),
            types.BotCommand(command="addadmin", description="👑 اضافه کردن ادمین"),
            types.BotCommand(command="removeadmin", description="❌ حذف ادمین"),
            types.BotCommand(command="listadmins", description="👥 لیست ادمین‌ها"),
            types.BotCommand(command="displayconfig", description="⚙️ تنظیمات نمایش"),
            types.BotCommand(command="broadcast", description="📢 ارسال پیام همگانی"),
            types.BotCommand(command="fullstats", description="📊 آمار کامل ربات"),
            types.BotCommand(command="resetstats", description="🔄 ریست آمار"),
            types.BotCommand(command="security", description="🔧 تنظیمات امنیتی"),
        ]
        
        commands.extend(admin_commands)
        
        await self.bot.set_my_commands(commands)
    
    async def run(self):
        """اجرای ربات"""
        if not self.bot or not self.dp:
            raise RuntimeError("ربات راه‌اندازی نشده است. ابتدا setup() را فراخوانی کنید.")
        
        # حذف webhook (اگر وجود دارد)
        await self.bot.delete_webhook(drop_pending_updates=True)
        
        # شروع polling
        await self.dp.start_polling(self.bot)
    
    async def shutdown(self):
        """خاموش کردن ربات"""
        if self.download_manager:
            await self.download_manager.shutdown()
        
        if self.bot:
            await self.bot.session.close()
        
        # ذخیره تنظیمات
        if self.config:
            await self.config.save()
    
    async def process_upload(self, message: Message, url: str):
        """پردازش آپلود فایل"""
        from handlers.user_handlers import UserHandlers
        handler = UserHandlers(self)
        await handler._process_upload(message, url)
    
    async def send_message(self, chat_id: int, text: str, **kwargs) -> Message:
        """ارسال پیام با هندل کردن خطاها"""
        try:
            return await self.bot.send_message(chat_id, text, **kwargs)
        except Exception as e:
            logger.error(f"خطا در ارسال پیام به {chat_id}: {e}")
            raise
    
    async def edit_message(self, chat_id: int, message_id: int, text: str, **kwargs) -> Message:
        """ویرایش پیام با هندل کردن خطاها"""
        try:
            return await self.bot.edit_message_text(text, chat_id, message_id, **kwargs)
        except Exception as e:
            logger.error(f"خطا در ویرایش پیام {message_id} در {chat_id}: {e}")
            raise
    
    async def delete_message(self, chat_id: int, message_id: int):
        """حذف پیام با هندل کردن خطاها"""
        try:
            await self.bot.delete_message(chat_id, message_id)
        except Exception as e:
            logger.error(f"خطا در حذف پیام {message_id} از {chat_id}: {e}")
    
    async def send_document(self, chat_id: int, document, **kwargs) -> Message:
        """ارسال فایل با هندل کردن خطاها"""
        try:
            return await self.bot.send_document(chat_id, document, **kwargs)
        except Exception as e:
            logger.error(f"خطا در ارسال فایل به {chat_id}: {e}")
            raise
    
    async def send_photo(self, chat_id: int, photo, **kwargs) -> Message:
        """ارسال عکس با هندل کردن خطاها"""
        try:
            return await self.bot.send_photo(chat_id, photo, **kwargs)
        except Exception as e:
            logger.error(f"خطا در ارسال عکس به {chat_id}: {e}")
            raise
    
    async def send_video(self, chat_id: int, video, **kwargs) -> Message:
        """ارسال ویدیو با هندل کردن خطاها"""
        try:
            return await self.bot.send_video(chat_id, video, **kwargs)
        except Exception as e:
            logger.error(f"خطا در ارسال ویدیو به {chat_id}: {e}")
            raise
