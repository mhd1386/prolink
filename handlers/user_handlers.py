"""
User command handlers with i18n support
"""

import re
import logging
import aiofiles
from typing import Optional
from pathlib import Path

from aiogram.types import Message
from aiogram.enums import ParseMode

from config import get_config, env_config
from config.i18n import translator, Language
from utils.shortlink import ShortLinkService

logger = logging.getLogger(__name__)

class UserHandlers:
    """User command handlers with i18n support"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def handle_start(self, message: Message):
        """Handler for /start command"""
        config = await get_config()
        display = config.display_settings
        user_lang = config.get_user_language(message.from_user.id)
        
        short_link_status = "✅ active" if display.enable_short_link else "❌ inactive"
        if user_lang == Language.PERSIAN:
            short_link_status = "✅ فعال" if display.enable_short_link else "❌ غیرفعال"
        
        welcome = translator.get("start", user_lang,
            support_username=env_config.support_username,
            short_link_status=short_link_status,
            short_link_service=display.short_link_service
        )
        
        await message.answer(welcome, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_help(self, message: Message):
        """Handler for /help command"""
        config = await get_config()
        display = config.display_settings
        user_lang = config.get_user_language(message.from_user.id)
        
        # Prepare status indicators
        filename_status = "✅" if display.show_filename else "❌"
        filesize_status = "✅" if display.show_filesize else "❌"
        sourceurl_status = "✅" if display.show_source_url else "❌"
        userid_status = "✅" if display.show_user_id else "❌"
        copyright_status = "✅" if display.show_copyright else "❌"
        short_link_note = "(shortened)" if display.enable_short_link else ""
        
        if user_lang == Language.PERSIAN:
            short_link_note = "(کوتاه شده)" if display.enable_short_link else ""
        
        help_text = translator.get("help", user_lang,
            filename_status=filename_status,
            filesize_status=filesize_status,
            sourceurl_status=sourceurl_status,
            userid_status=userid_status,
            copyright_status=copyright_status,
            short_link_note=short_link_note,
            max_size=env_config.max_file_size / 1024 / 1024,
            max_per_minute=config.security.max_requests_per_minute,
            max_per_day=config.security.max_requests_per_day,
            support_username=env_config.support_username
        )
        
        await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_upload(self, message: Message):
        """Handler for /upload command"""
        config = await get_config()
        user_lang = config.get_user_language(message.from_user.id)
        
        # Extract URL from command
        command_parts = message.text.split()
        if len(command_parts) < 2:
            error_msg = translator.get("invalid_url", user_lang)
            await message.answer(
                f"⚠️ {error_msg}\n"
                f"Example: `/upload https://example.com/file.zip`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        url = command_parts[1]
        await self._process_upload(message, url)
    
    async def handle_direct_link(self, message: Message):
        """Handler for direct links"""
        url = message.text.strip()
        
        # Check if text is a valid URL
        url_pattern = re.compile(r'^https?://[^\s/$.?#].[^\s]*$', re.IGNORECASE)
        if url_pattern.match(url):
            await self._process_upload(message, url)
    
    async def _process_upload(self, message: Message, url: str):
        """Process file upload"""
        user_id = message.from_user.id
        chat_id = message.chat.id
        config = await get_config()
        user_lang = config.get_user_language(user_id)
        
        # Send status message
        status_text = translator.get("upload_started", user_lang)
        status_msg = await message.answer(status_text)
        
        try:
            # Check URL
            if not url.startswith(('http://', 'https://')):
                error_msg = translator.get("invalid_url", user_lang)
                raise Exception(error_msg)
            
            # Check rate limit
            allowed, error_message = config.check_rate_limit(user_id)
            if not allowed:
                raise Exception(error_message)
            
            # Download file
            filepath = await self.bot.download_manager.download_file(url, user_id)
            
            if not filepath:
                error_msg = translator.get("network_error", user_lang)
                raise Exception(error_msg)
            
            # Generate caption
            caption = await self._generate_caption(filepath.name, url, user_id)
            
            # Determine file type
            file_type = self._get_file_type(filepath.name)
            
            # Send file based on type
            async with aiofiles.open(filepath, 'rb') as file:
                file_data = await file.read()
                
                if file_type == 'image':
                    await self.bot.send_photo(
                        chat_id=chat_id,
                        photo=file_data,
                        caption=caption,
                        parse_mode=ParseMode.MARKDOWN,
                        has_spoiler=True
                    )
                elif file_type == 'video':
                    await self.bot.send_video(
                        chat_id=chat_id,
                        video=file_data,
                        caption=caption,
                        parse_mode=ParseMode.MARKDOWN,
                        has_spoiler=True
                    )
                else:
                    await self.bot.send_document(
                        chat_id=chat_id,
                        document=file_data,
                        caption=caption,
                        parse_mode=ParseMode.MARKDOWN
                    )
            
            # Update statistics
            file_size = filepath.stat().st_size
            config.increment_request_count(user_id)
            config.increment_statistics(user_id, file_size)
            await config.save()
            
            # Delete status message
            await self.bot.delete_message(chat_id, status_msg.message_id)
            
            # Delete temporary file
            filepath.unlink()
            
            logger.info(f"Successful upload: file {filepath.name} by user {user_id}")
            
        except Exception as e:
            # Edit status message to error
            await self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg.message_id,
                text=f"❌ {str(e)}"
            )
            logger.error(f"Upload error: {e}")
    
    async def _generate_caption(self, filename: str, url: str, user_id: int) -> str:
        """Generate caption for file"""
        config = await get_config()
        display = config.display_settings
        user_lang = config.get_user_language(user_id)
        
        # Extract original filename
        original_filename = '_'.join(filename.split('_')[2:]) if '_' in filename else filename
        
        # Shorten link if needed
        source_url = url
        if display.enable_short_link and display.show_source_url:
            source_url = await self.bot.shortlink_service.shorten_url(url)
        
        caption_parts = []
        
        if display.show_filename:
            caption_parts.append(f"📝 **File:** {self._escape_markdown(original_filename)}")
            if user_lang == Language.PERSIAN:
                caption_parts[-1] = f"📝 **نام فایل:** {self._escape_markdown(original_filename)}"
        
        if display.show_filesize:
            # Calculate file size
            try:
                filepath = Path("temp") / filename
                if filepath.exists():
                    size_mb = filepath.stat().st_size / (1024 * 1024)
                    caption_parts.append(f"💾 **Size:** {size_mb:.2f} MB")
                    if user_lang == Language.PERSIAN:
                        caption_parts[-1] = f"💾 **حجم فایل:** {size_mb:.2f} مگابایت"
            except:
                pass
        
        if display.show_source_url:
            url_display = source_url
            if len(url_display) > 40:
                url_display = f"{url_display[:40]}..."
            caption_parts.append(f"🔗 **Source:** {self._escape_markdown(url_display)}")
            if user_lang == Language.PERSIAN:
                caption_parts[-1] = f"🔗 **لینک منبع:** {self._escape_markdown(url_display)}"
        
        if display.show_user_id:
            caption_parts.append(f"👤 **User ID:** `{user_id}`")
            if user_lang == Language.PERSIAN:
                caption_parts[-1] = f"👤 **آیدی کاربر:** `{user_id}`"
        
        if display.show_copyright and display.copyright_text:
            caption_parts.append(f"©️ **{display.copyright_text}**")
        
        return "\n".join(caption_parts)
    
    async def handle_support(self, message: Message):
        """Handler for /support command"""
        config = await get_config()
        user_lang = config.get_user_language(message.from_user.id)
        
        support_text = (
            f"📞 **Support**\n\n"
            f"👤 **Support:** {env_config.support_username}\n\n"
            f"⏰ **Response time:** 24/7\n"
            f"🚀 **Topics:**\n"
            f"• Technical issues\n"
            f"• Suggestions & feedback\n"
            f"• Bug reports\n"
            f"• Usage guide\n\n"
            f"📧 **Contact:**\n"
            f"Message the ID above directly\n\n"
            f"❤️ **Thank you for choosing us**"
        )
        
        if user_lang == Language.PERSIAN:
            support_text = (
                f"📞 **پشتیبانی ربات**\n\n"
                f"👤 **پشتیبان:** {env_config.support_username}\n\n"
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
        """Handler for /status command"""
        config = await get_config()
        display = config.display_settings
        stats = config.statistics
        user_lang = config.get_user_language(message.from_user.id)
        
        channels_status = "❌ inactive"
        if config.required_channels:
            channels_status = f"✅ {len(config.required_channels)} channels"
        
        if user_lang == Language.PERSIAN:
            channels_status = "❌ غیرفعال"
            if config.required_channels:
                channels_status = f"✅ {len(config.required_channels)} کانال"
        
        status_text = (
            f"📊 **Bot Status**\n\n"
            f"✅ **Status:** Online\n"
            f"🤖 **Bot:** @irprolinkbot\n"
            f"🚀 **Version:** 6.0.0\n"
            f"📅 **Release Year:** 2026\n"
            f"💾 **Max size:** {env_config.max_file_size / 1024 / 1024} MB\n"
            f"👥 **Users:** {stats.total_users}\n"
            f"📥 **Downloads:** {stats.total_downloads}\n"
            f"💽 **Total size:** {stats.total_size_gb:.2f} GB\n"
            f"📢 **Required channels:** {channels_status}\n"
            f"👤 **Support:** {env_config.support_username}\n\n"
            f"⚙️ **Display settings:**\n"
            f"• Filename: {'✅' if display.show_filename else '❌'}\n"
            f"• Filesize: {'✅' if display.show_filesize else '❌'}\n"
            f"• Source URL: {'✅' if display.show_source_url else '❌'}\n"
            f"• Short link: {'✅' if display.enable_short_link else '❌'}\n"
            f"• Service: {display.short_link_service}\n"
            f"• User ID: {'✅' if display.show_user_id else '❌'}\n"
            f"• Copyright: {'✅' if display.show_copyright else '❌'}\n"
        )
        
        if user_lang == Language.PERSIAN:
            status_text = (
                f"📊 **وضعیت ربات**\n\n"
                f"✅ **وضعیت:** آنلاین\n"
                f"🤖 **ربات:** @irprolinkbot\n"
                f"🚀 **نسخه:** ۶.۰.۰\n"
                f"📅 **سال انتشار:** ۲۰۲۶\n"
                f"💾 **حداکثر حجم:** {env_config.max_file_size / 1024 / 1024} مگابایت\n"
                f"👥 **کاربران:** {stats.total_users}\n"
                f"📥 **دانلودها:** {stats.total_downloads}\n"
                f"💽 **حجم کل:** {stats.total_size_gb:.2f} گیگابایت\n"
                f"📢 **کانال‌های اجباری:** {channels_status}\n"
                f"👤 **پشتیبانی:** {env_config.support_username}\n\n"
                f"⚙️ **تنظیمات نمایش:**\n"
                f"• نام فایل: {'✅' if display.show_filename else '❌'}\n"
                f"• حجم فایل: {'✅' if display.show_filesize else '❌'}\n"
                f"• لینک منبع: {'✅' if display.show_source_url else '❌'}\n"
                f"• لینک کوتاه: {'✅' if display.enable_short_link else '❌'}\n"
                f"• سرویس: {display.short_link_service}\n"
                f"• آیدی کاربر: {'✅' if display.show_user_id else '❌'}\n"
                f"• کپی رایت: {'✅' if display.show_copyright else '❌'}\n"
            )
        
        if display.show_copyright:
            status_text += f"• Copyright text: {display.copyright_text}\n"
            if user_lang == Language.PERSIAN:
                status_text += f"• متن کپی رایت: {display.copyright_text}\n"
        
        # If user is admin
        if config.is_admin(message.from_user.id):
            status_text += "\n👑 **You are admin**\nUse admin commands"
            if user_lang == Language.PERSIAN:
                status_text += "\n👑 **شما ادمین هستید**\nاز دستورات مدیریتی استفاده کنید"
        
        await message.answer(status_text, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_user_stats(self, message: Message):
        """Handler for /mystats command"""
        user_id = message.from_user.id
        config = await get_config()
        stats = config.statistics
        user_lang = config.get_user_language(user_id)
        
        user_downloads = stats.user_activity.get(str(user_id), 0)
        
        # Determine rank
        if user_downloads > 10:
            rank = "🏅 Gold"
        elif user_downloads > 5:
            rank = "🥈 Silver"
        elif user_downloads > 0:
            rank = "🥉 Bronze"
        else:
            rank = "👶 Newcomer"
        
        if user_lang == Language.PERSIAN:
            if user_downloads > 10:
                rank = "🏅 طلایی"
            elif user_downloads > 5:
                rank = "🥈 نقره‌ای"
            elif user_downloads > 0:
                rank = "🥉 برنزی"
            else:
                rank = "👶 تازه‌وارد"
        
        user_stats = (
            f"📈 **Your Statistics**\n\n"
            f"👤 **Your ID:** `{user_id}`\n"
            f"📥 **Downloads:** {user_downloads}\n"
            f"🏆 **Your rank:** {rank}\n"
            f"📅 **Last activity:** {stats.last_active}\n"
            f"🤖 **Bot:** @irprolinkbot\n\n"
            f"💡 **Tip:**\n"
            f"Use /status for full bot statistics"
        )
        
        if user_lang == Language.PERSIAN:
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
    
    def _get
