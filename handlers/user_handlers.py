"""
هندلرهای دستورات کاربران
"""

import re
import logging
from typing import Optional
from pathlib import Path

from aiogram.types import Message
from aiogram.enums import ParseMode

from config import get_config
from utils.shortlink import ShortLinkService

logger = logging.getLogger(__name__)

class UserHandlers:
    """هندلرهای دستورات کاربران"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def handle_start(self, message: Message):
        """هندلر دستور /start"""
        config = await get_config()
        display = config.display_settings
        
        welcome = (
            f"🤖 **به ربات irProLink خوش آمدید!**\n\n"
            f"📋 **دستورات اصلی:**\n"
            f"• /start - نمایش راهنما\n"
            f"• /upload [لینک] - آپلود فایل\n"
            f"• /help - راهنمای کامل\n"
            f"• /support - تماس با پشتیبانی\n"
            f"• /status - وضعیت ربات\n"
            f"• /mystats - آمار کاربری\n\n"
            f"📞 **پشتیبانی:** {self.bot.config.support_username}\n\n"
            f"🚀 **ویژگی‌ها:**\n"
            f"• آپلود تا ۲ گیگابایت\n"
            f"• نمایش جزئیات کامل فایل\n"
            f"• لینک کوتاه: {'✅ فعال' if display.enable_short_link else '❌ غیرفعال'}\n"
            f"• سرویس لینک کوتاه: {display.short_link_service}\n"
            f"• پشتیبانی از همه فرمت‌ها\n"
            f"• امنیت پیشرفته\n\n"
            f"🔗 **مثال:** `/upload https://example.com/file.zip`"
        )
        
        await message.answer(welcome, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_help(self, message: Message):
        """هندلر دستور /help"""
        config = await get_config()
        display = config.display_settings
        
        help_text = (
            f"📖 **راهنمای کامل ربات**\n\n"
            f"🔗 **نحوه استفاده:**\n"
            f"۱. لینک مستقیم فایل را ارسال کنید\n"
            f"۲. یا از دستور /upload استفاده کنید\n\n"
            f"📝 **مثال:**\n"
            f"`/upload https://example.com/file.zip`\n\n"
            f"📊 **جزئیات نمایش داده شده:**\n"
            f"• نام کامل فایل {'✅' if display.show_filename else '❌'}\n"
            f"• حجم به مگابایت {'✅' if display.show_filesize else '❌'}\n"
            f"• لینک منبع {'✅' if display.show_source_url else '❌'} "
            f"{'(کوتاه شده)' if display.enable_short_link else ''}\n"
            f"• آیدی کاربر {'✅' if display.show_user_id else '❌'}\n"
            f"• کپی رایت ربات {'✅' if display.show_copyright else '❌'}\n\n"
            f"⚠️ **محدودیت‌ها:**\n"
            f"• حداکثر حجم: {self.bot.config.max_file_size / 1024 / 1024} مگابایت\n"
            f"• فقط لینک‌های مستقیم\n"
            f"• زمان آپلود: ۵ دقیقه\n"
            f"• حداکثر درخواست: {config.security.max_requests_per_minute} در دقیقه\n"
            f"• حداکثر درخواست روزانه: {config.security.max_requests_per_day}\n\n"
            f"❓ **پشتیبانی:** {self.bot.config.support_username}\n\n"
            f"⚙️ **دستورات ادمین:**\n"
            f"(فقط برای مدیران قابل دسترسی است)"
        )
        
        await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_upload(self, message: Message):
        """هندلر دستور /upload"""
        # استخراج URL از دستور
        command_parts = message.text.split()
        if len(command_parts) < 2:
            await message.answer(
                "⚠️ لطفاً لینک فایل را وارد کنید\n"
                "مثال: `/upload https://example.com/file.zip`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        url = command_parts[1]
        await self._process_upload(message, url)
    
    async def handle_direct_link(self, message: Message):
        """هندلر لینک‌های مستقیم"""
        url = message.text.strip()
        
        # بررسی اینکه آیا متن یک URL معتبر است
        url_pattern = re.compile(r'^https?://[^\s/$.?#].[^\s]*$', re.IGNORECASE)
        if url_pattern.match(url):
            await self._process_upload(message, url)
    
    async def _process_upload(self, message: Message, url: str):
        """پردازش آپلود فایل"""
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # ارسال پیام وضعیت
        status_msg = await message.answer("🔍 در حال بررسی لینک...")
        
        try:
            # بررسی URL
            if not url.startswith(('http://', 'https://')):
                raise Exception("❌ لینک نامعتبر است. لینک باید با http:// یا https:// شروع شود.")
            
            # دانلود فایل
            filepath = await self.bot.download_manager.download_file(url, user_id)
            
            if not filepath:
                raise Exception("❌ خطا در دانلود فایل")
            
            # ساخت کپشن
            caption = await self._generate_caption(filepath.name, url, user_id)
            
            # ارسال فایل
            with open(filepath, 'rb') as file:
                await self.bot.send_document(
                    chat_id=chat_id,
                    document=file,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN
                )
            
            # به‌روزرسانی آمار
            file_size = filepath.stat().st_size
            config = await get_config()
            config.increment_statistics(user_id, file_size)
            await config.save()
            
            # حذف پیام وضعیت
            await self.bot.delete_message(chat_id, status_msg.message_id)
            
            # حذف فایل موقت
            filepath.unlink()
            
            logger.info(f"آپلود موفق: فایل {filepath.name} توسط کاربر {user_id}")
            
        except Exception as e:
            # ویرایش پیام وضعیت به خطا
            await self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg.message_id,
                text=f"❌ خطا: {str(e)}"
            )
            logger.error(f"خطا در آپلود: {e}")
    
    async def _generate_caption(self, filename: str, url: str, user_id: int) -> str:
        """ساخت کپشن برای فایل"""
        config = await get_config()
        display = config.display_settings
        
        # استخراج نام اصلی فایل
        original_filename = '_'.join(filename.split('_')[2:]) if '_' in filename else filename
        
        # کوتاه کردن لینک اگر لازم باشد
        source_url = url
        if display.enable_short_link and display.show_source_url:
            source_url = await self.bot.shortlink_service.shorten_url(url)
        
        caption_parts = []
        
        if display.show_filename:
            caption_parts.append(f"📝 **نام فایل:** {self._escape_markdown(original_filename)}")
        
        if display.show_filesize:
            # محاسبه حجم فایل
            try:
                filepath = Path("temp") / filename
                if filepath.exists():
                    size_mb = filepath.stat().st_size / (1024 * 1024)
                    caption_parts.append(f"💾 **حجم فایل:** {size_mb:.2f} مگابایت")
            except:
                pass
        
        if display.show_source_url:
            url_display = source_url
            if len(url_display) > 40:
                url_display = f"{url_display[:40]}..."
            caption_parts.append(f"🔗 **لینک منبع:** {self._escape_markdown(url_display)}")
        
        if display.show_user_id:
            caption_parts.append(f"👤 **آیدی کاربر:** `{user_id}`")
        
        if display.show_copyright and display.copyright_text:
            caption_parts.append(f"©️ **{display.copyright_text}**")
        
        return "\n".join(caption_parts)
    
    async def handle_support(self, message: Message):
        """هندلر دستور /support"""
        support_text = (
            f"📞 **پشتیبانی ربات**\n\n"
            f"👤 **پشتیبان:** {self.bot.config.support_username}\n\n"
            f"⏰ **ساعت پاسخگویی:** ۲۴ ساعته\n"
            f"🚀 **موضوعات قابل پیگیری:**\n"
            f"• مشکلات فنی ربات\n"
            f"• پیشنهادات و انتقادات\n"
            f"• گزارش باگ و خطاها\n"
            f"• راهنمای استفاده\n\n"
            f"📧 **ارتباط:**\n"
            f"مستقیم به آیدی بالا پیام دهید\n\n"
            f"❤️ **تشکر از انتخاب ما**"
        )
        
        await message.answer(support_text, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_status(self, message: Message):
        """هندلر دستور /status"""
        config = await get_config()
        display = config.display_settings
        stats = config.statistics
        
        status_text = (
            f"📊 **وضعیت ربات**\n\n"
            f"✅ **وضعیت:** آنلاین\n"
            f"🤖 **نام ربات:** @irprolinkbot\n"
            f"🚀 **نسخه:** ۲۰۲۵.۱.۰\n"
            f"📅 **آخرین بروزرسانی:** ۱۴۰۴/۱۰/۰۴\n"
            f"💾 **حداکثر حجم:** {self.bot.config.max_file_size / 1024 / 1024} مگابایت\n"
            f"👥 **تعداد کاربران:** {stats.total_users}\n"
            f"📥 **تعداد دانلودها:** {stats.total_downloads}\n"
            f"💽 **حجم کل:** {stats.total_size_gb:.2f} گیگابایت\n"
            f"📢 **کانال‌های اجباری:** {'❌ غیرفعال' if not config.required_channels else f'✅ {len(config.required_channels)} کانال'}\n"
            f"👤 **پشتیبانی:** {self.bot.config.support_username}\n\n"
            f"⚙️ **تنظیمات نمایش:**\n"
            f"• نام فایل: {'✅' if display.show_filename else '❌'}\n"
            f"• حجم فایل: {'✅' if display.show_filesize else '❌'}\n"
            f"• لینک منبع: {'✅' if display.show_source_url else '❌'}\n"
            f"• لینک کوتاه: {'✅' if display.enable_short_link else '❌'}\n"
            f"• سرویس لینک کوتاه: {display.short_link_service}\n"
            f"• آیدی کاربر: {'✅' if display.show_user_id else '❌'}\n"
            f"• کپی رایت: {'✅' if display.show_copyright else '❌'}\n"
        )
        
        if display.show_copyright:
            status_text += f"• متن کپی رایت: {display.copyright_text}\n"
        
        # اگر کاربر ادمین است
        if config.is_admin(message.from_user.id):
            status_text += "\n👑 **شما ادمین هستید**\nاز دستورات مدیریتی استفاده کنید"
        
        await message.answer(status_text, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_user_stats(self, message: Message):
        """هندلر دستور /mystats"""
        user_id = message.from_user.id
        config = await get_config()
        stats = config.statistics
        
        user_downloads = stats.user_activity.get(str(user_id), 0)
        
        # تعیین رتبه
        if user_downloads > 10:
            rank = "🏅 طلایی"
        elif user_downloads > 5:
            rank = "🥈 نقره‌ای"
        elif user_downloads > 0:
            rank = "🥉 برنزی"
        else:
            rank = "👶 تازه‌وارد"
        
        user_stats = (
            f"📈 **آمار کاربری شما**\n\n"
            f"👤 **آیدی شما:** `{user_id}`\n"
            f"📥 **تعداد دانلودها:** {user_downloads}\n"
            f"🏆 **رتبه شما:** {rank}\n"
            f"📅 **آخرین فعالیت:** {stats.last_active}\n"
            f"🤖 **ربات:** @irprolinkbot\n\n"
            f"💡 **نکته:**\n"
            f"برای مشاهده آمار کامل ربات از /status استفاده کنید"
        )
        
        await message.answer(user_stats, parse_mode=ParseMode.MARKDOWN)
    
    def _escape_markdown(self, text: str) -> str:
        """فرار کردن کاراکترهای مخصوص مارک‌داون"""
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        return text
