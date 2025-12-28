"""
هندلرهای دستورات ادمین
"""

import logging
from aiogram.types import Message
from aiogram.enums import ParseMode

from config import get_config

logger = logging.getLogger(__name__)

class AdminHandlers:
    """هندلرهای دستورات ادمین"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def handle_add_channel(self, message: Message):
        """اضافه کردن کانال اجباری"""
        config = await get_config()
        
        if not config.is_admin(message.from_user.id):
            await message.answer("⛔ دسترسی ممنوع!")
            return
        
        command_parts = message.text.split()
        if len(command_parts) < 2:
            await message.answer("⚠️ لطفاً آیدی کانال را وارد کنید\nمثال: /addchannel @channel")
            return
        
        channel = command_parts[1].strip()
        if not channel.startswith('@'):
            await message.answer("⚠️ آیدی کانال باید با @ شروع شود")
            return
        
        if channel not in config.required_channels:
            config.required_channels.append(channel)
            await config.save()
            await message.answer(f"✅ کانال {channel} به لیست کانال‌های اجباری اضافه شد")
        else:
            await message.answer("⚠️ این کانال قبلاً اضافه شده است")
    
    async def handle_remove_channel(self, message: Message):
        """حذف کانال اجباری"""
        config = await get_config()
        
        if not config.is_admin(message.from_user.id):
            await message.answer("⛔ دسترسی ممنوع!")
            return
        
        command_parts = message.text.split()
        if len(command_parts) < 2:
            await message.answer("⚠️ لطفاً آیدی کانال را وارد کنید\nمثال: /removechannel @channel")
            return
        
        channel = command_parts[1].strip()
        if channel in config.required_channels:
            config.required_channels.remove(channel)
            await config.save()
            await message.answer(f"✅ کانال {channel} از لیست حذف شد")
        else:
            await message.answer("⚠️ این کانال در لیست وجود ندارد")
    
    async def handle_list_channels(self, message: Message):
        """لیست کانال‌های اجباری"""
        config = await get_config()
        
        if not config.is_admin(message.from_user.id):
            await message.answer("⛔ دسترسی ممنوع!")
            return
        
        if not config.required_channels:
            await message.answer("📭 هیچ کانال اجباری تنظیم نشده است")
        else:
            channels_list = "\n".join([f"{i+1}. {channel}" for i, channel in enumerate(config.required_channels)])
            await message.answer(f"📋 لیست کانال‌های اجباری:\n\n{channels_list}")
    
    async def handle_add_admin(self, message: Message):
        """اضافه کردن ادمین"""
        config = await get_config()
        
        if not config.is_admin(message.from_user.id):
            await message.answer("⛔ دسترسی ممنوع!")
            return
        
        command_parts = message.text.split()
        if len(command_parts) < 2:
            await message.answer("⚠️ لطفاً آیدی ادمین را وارد کنید\nمثال: /addadmin 123456789")
            return
        
        try:
            admin_id = int(command_parts[1].strip())
            if admin_id not in config.admin_ids:
                config.admin_ids.append(admin_id)
                await config.save()
                await message.answer(f"✅ آیدی {admin_id} به لیست ادمین‌ها اضافه شد")
            else:
                await message.answer("⚠️ این آیدی قبلاً ادمین است")
        except ValueError:
            await message.answer("⚠️ آیدی نامعتبر است")
    
    async def handle_remove_admin(self, message: Message):
        """حذف ادمین"""
        config = await get_config()
        
        if not config.is_admin(message.from_user.id):
            await message.answer("⛔ دسترسی ممنوع!")
            return
        
        command_parts = message.text.split()
        if len(command_parts) < 2:
            await message.answer("⚠️ لطفاً آیدی ادمین را وارد کنید\nمثال: /removeadmin 123456789")
            return
        
        try:
            admin_id = int(command_parts[1].strip())
            if admin_id == message.from_user.id:
                await message.answer("⚠️ نمی‌توانید خودتان را حذف کنید")
                return
            
            if admin_id in config.admin_ids:
                config.admin_ids.remove(admin_id)
                await config.save()
                await message.answer(f"✅ آیدی {admin_id} از لیست ادمین‌ها حذف شد")
            else:
                await message.answer("⚠️ این آیدی در لیست ادمین‌ها نیست")
        except ValueError:
            await message.answer("⚠️ آیدی نامعتبر است")
    
    async def handle_list_admins(self, message: Message):
        """لیست ادمین‌ها"""
        config = await get_config()
        
        if not config.is_admin(message.from_user.id):
            await message.answer("⛔ دسترسی ممنوع!")
            return
        
        if not config.admin_ids:
            await message.answer("👥 هیچ ادمینی تنظیم نشده است")
        else:
            admins_list = []
            for i, admin_id in enumerate(config.admin_ids):
                if admin_id == message.from_user.id:
                    admins_list.append(f"{i+1}. {admin_id} 👑 (شما)")
                elif admin_id == 7660976743:
                    admins_list.append(f"{i+1}. {admin_id} 👑 (مدیر اصلی)")
                else:
                    admins_list.append(f"{i+1}. {admin_id}")
            
            await message.answer("👑 لیست ادمین‌ها:\n\n" + "\n".join(admins_list))
    
    async def handle_display_config(self, message: Message):
        """نمایش تنظیمات نمایش"""
        config = await get_config()
        
        if not config.is_admin(message.from_user.id):
            await message.answer("⛔ دسترسی ممنوع!")
            return
        
        display = config.display_settings
        
        config_text = (
            f"⚙️ **تنظیمات نمایش جزئیات**\n\n"
            f"📝 **نام فایل:** {'✅ فعال' if display.show_filename else '❌ غیرفعال'}\n"
            f"💾 **حجم فایل:** {'✅ فعال' if display.show_filesize else '❌ غیرفعال'}\n"
            f"🔗 **لینک منبع:** {'✅ فعال' if display.show_source_url else '❌ غیرفعال'}\n"
            f"🔗 **لینک کوتاه:** {'✅ فعال' if display.enable_short_link else '❌ غیرفعال'}\n"
            f"🔗 **سرویس لینک کوتاه:** {display.short_link_service}\n"
            f"👤 **آیدی کاربر:** {'✅ فعال' if display.show_user_id else '❌ غیرفعال'}\n"
            f"©️ **کپی رایت:** {'✅ فعال' if display.show_copyright else '❌ غیرفعال'}\n"
            f"✏️ **متن کپی رایت:** {display.copyright_text}\n\n"
            f"🔧 **دستورات تغییر:**\n"
            f"/togglefilename - تغییر نمایش نام\n"
            f"/togglefilesize - تغییر نمایش حجم\n"
            f"/togglesourceurl - تغییر نمایش لینک\n"
            f"/toggleshortlink - تغییر لینک کوتاه\n"
            f"/setshortlinkservice [سرویس] - تغییر سرویس\n"
            f"/toggleuserid - تغییر نمایش آیدی\n"
            f"/togglecopyright - تغییر نمایش کپی رایت\n"
            f"/setcopyright [متن] - تغییر متن کپی رایت\n"
            f"/saveconfig - ذخیره تنظیمات\n\n"
            f"💡 **نکته:**\n"
            f"تغییرات تا زمانی که ذخیره نشوند، موقت هستند\n\n"
            f"📌 **سرویس‌های پشتیبانی شده:**\n"
            f"• tinyurl - قدیمی و مطمئن\n"
            f"• is.gd - سریع و رایگان\n"
            f"• cleanuri - بدون نیاز به API"
        )
        
        await message.answer(config_text, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_toggle_filename(self, message: Message):
        """تغییر نمایش نام فایل"""
        await self._toggle_setting(message, 'filename')
    
    async def handle_toggle_filesize(self, message: Message):
        """تغییر نمایش حجم فایل"""
        await self._toggle_setting(message, 'filesize')
    
    async def handle_toggle_sourceurl(self, message: Message):
        """تغییر نمایش لینک منبع"""
        await self._toggle_setting(message, 'sourceurl')
    
    async def handle_toggle_userid(self, message: Message):
        """تغییر نمایش آیدی کاربر"""
        await self._toggle_setting(message, 'userid')
    
    async def handle_toggle_copyright(self, message: Message):
        """تغییر نمایش کپی رایت"""
        await self._toggle_setting(message, 'copyright')
    
    async def handle_toggle_shortlink(self, message: Message):
        """تغییر لینک کوتاه"""
        await self._toggle_setting(message, 'shortlink')
    
    async def _toggle_setting(self, message: Message, setting: str):
        """تغییر تنظیمات نمایش"""
        config = await get_config()
        
        if not config.is_admin(message.from_user.id):
            await message.answer("⛔ دسترسی ممنوع!")
            return
        
        display = config.display_settings
        setting_names = {
            'filename': ('نام فایل', 'show_filename'),
            'filesize': ('حجم فایل', 'show_filesize'),
            'sourceurl': ('لینک منبع', 'show_source_url'),
            'userid': ('آیدی کاربر', 'show_user_id'),
            'copyright': ('کپی رایت', 'show_copyright'),
            'shortlink': ('لینک کوتاه', 'enable_short_link'),
        }
        
        if setting not in setting_names:
            await message.answer("⚠️ تنظیمات نامعتبر")
            return
        
        name, attr = setting_names[setting]
        current_value = getattr(display, attr)
        setattr(display, attr, not current_value)
        
        status = 'فعال' if not current_value else 'غیرفعال'
        await message.answer(
            f"✅ تنظیم **{name}** به **{status}** تغییر کرد\n\n"
            f"⚠️ برای ذخیره دائمی از /saveconfig استفاده کنید",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_set_copyright(self, message: Message):
        """تغییر متن کپی رایت"""
        config = await get_config()
        
        if not config.is_admin(message.from_user.id):
            await message.answer("⛔ دسترسی ممنوع!")
            return
        
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.answer("⚠️ لطفاً متن کپی رایت را وارد کنید\nمثال: /setcopyright متن جدید")
            return
        
        text = command_parts[1].strip()
        config.display_settings.copyright_text = text
        
        await message.answer(
            f"✅ متن کپی رایت به '{text}' تغییر کرد\n\n"
            f"⚠️ برای ذخیره دائمی از /saveconfig استفاده کنید"
        )
    
    async def handle_set_shortlink_service(self, message: Message):
        """تغییر سرویس لینک کوتاه"""
        config = await get_config()
        
        if not config.is_admin(message.from_user.id):
            await message.answer("⛔ دسترسی ممنوع!")
            return
        
        command_parts = message.text.split()
        if len(command_parts) < 2:
            await message.answer("⚠️ لطفاً نام سرویس را وارد کنید\nمثال: /setshortlinkservice is.gd")
            return
        
        service = command_parts[1].strip().lower()
        valid_services = ['tinyurl', 'is.gd', 'cleanuri']
        
        if service not in valid_services:
            await message.answer(
                f"⚠️ سرویس نامعتبر!\n\nسرویس‌های معتبر: {', '.join(valid_services)}"
            )
            return
        
        config.display_settings.short_link_service = service
        self.bot.shortlink_service.service = service
        
        await message.answer(
            f"✅ سرویس لینک کوتاه به '{service}' تغییر کرد\n\n"
            f"⚠️ برای ذخیره دائمی از /saveconfig استفاده کنید"
        )
    
    async def handle_save_config(self, message: Message):
        """ذخیره تنظیمات"""
        config = await get_config()
        
        if not config.is_admin(message.from_user.id):
            await message.answer("⛔ دسترسی ممنوع!")
            return
        
        if await config.save():
            await message.answer("✅ تنظیمات با موفقیت ذخیره شد\nتغییرات از این پس دائمی هستند")
        else:
            await message.answer("❌ خطا در ذخیره تنظیمات")
    
    async def handle_broadcast(self, message: Message):
        """ارسال پیام همگانی"""
        config = await get_config()
        
        if not config.is_admin(message.from_user.id):
            await message.answer("⛔ دسترسی ممنوع!")
            return
        
        if not config.broadcast.enabled:
            await message.answer("⛔ ارسال پیام همگانی غیرفعال است")
            return
        
        if not config.can_send_broadcast():
            await message.answer("⏰ می‌توانید بعداً دوباره پیام همگانی ارسال کنید")
            return
        
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) < 2:
            await message.answer("⚠️ لطفاً متن پیام را وارد کنید\nمثال: /broadcast متن پیام")
            return
        
        broadcast_text = command_parts[1].strip()
        config.update_broadcast_time()
        await config.save()
        
        await message.answer(
            f"✅ پیام همگانی با موفقیت تنظیم شد\n\n"
            f"📝 متن:\n{broadcast_text}\n\n"
            f"👥 ارسال به: {config.statistics.total_users} کاربر\n"
            f"📅 زمان: {config.broadcast.last_sent}",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_full_stats(self, message: Message):
        """آمار کامل ربات"""
        config = await get_config()
        
        if not config.is_admin(message.from_user.id):
            await message.answer("⛔ دسترسی ممنوع!")
            return
        
        stats = config.statistics
        
        # کاربران برتر
        top_users = sorted(
            [(uid, count) for uid, count in stats.user_activity.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        top_users_text = "\n".join([
            f"{i+1}. {uid}: {count} دانلود"
            for i, (uid, count) in enumerate(top_users)
        ]) if top_users else "📭 هنوز کاربری فعالیت نکرده است"
        
        full_stats = (
            f"📈 **آمار کامل ربات**\n\n"
            f"🤖 **نام ربات:** @irprolinkbot\n"
            f"🚀 **نسخه:** ۲۰۲۵.۱.۰\n"
            f"📅 **تاریخ گزارش:** {stats.last_active}\n\n"
            f"📊 **آمار کلی:**\n"
            f"• 👥 تعداد کاربران: {stats.total_users}\n"
            f"• 📥 تعداد دانلودها: {stats.total_downloads}\n"
            f"• 💽 حجم کل: {stats.total_size_gb:.2f} گیگابایت\n"
            f"• 📅 آخرین فعالیت: {stats.last_active}\n\n"
            f"⚙️ **تنظیمات:**\n"
            f"• 🔗 لینک کوتاه: {'✅' if config.display_settings.enable_short_link else '❌'}\n"
            f"• ⏰ محدودیت درخواست: {config.security.max_requests_per_minute}/دقیقه\n"
            f"• 🛡️ امنیت فایل: {'✅' if config.security.enable_anti_spam else '❌'}\n"
            f"• 📢 برودکست: {'✅' if config.broadcast.enabled else '❌'}\n\n"
            f"🏆 **کاربران برتر:**\n"
            f"{top_users_text}\n\n"
            f"👑 **ادمین‌ها:** {len(config.admin_ids)} نفر\n"
            f"📢 **کانال‌های اجباری:** {len(config.required_channels)} کانال"
        )
        
        await message.answer(full_stats, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_reset_stats(self, message: Message):
        """ریست آمار"""
        config = await get_config()
        
        if not config.is_admin(message.from_user.id):
            await message.answer("⛔ دسترسی ممنوع!")
            return
        
        # نگه داشتن مدیر اصلی
        main_admin = 7660976743
        admin_ids = [main_admin] if main_admin in config.admin_ids else [main_admin]
        
        # ریست کردن آمار
        from dataclasses import replace
        config.statistics = type(config.statistics)()
        config.admin_ids = admin_ids
        config.user_sessions = {}
        
        if await config.save():
            await message.answer("✅ آمار با موفقیت ریست شد\nتمام آمار کاربران و دانلودها پاک شدند")
        else:
            await message.answer("❌ خطا در ذخیره تنظیمات")
    
    async def handle_security_settings(self, message: Message):
        """تنظیمات امنیتی"""
        config = await get_config()
        
        if not config.is_admin(message.from_user.id):
            await message.answer("⛔ دسترسی ممنوع!")
            return
        
        security = config.security
        
        security_text = (
            f"🛡️ **تنظیمات امنیتی**\n\n"
            f"⚙️ **محدودیت نرخ:** {'✅ فعال' if security.enable_rate_limit else '❌ غیرفعال'}\n"
            f"📊 **حداکثر درخواست:** {security.max_requests_per_minute} در دقیقه\n"
            f"📅 **حداکثر درخواست روزانه:** {security.max_requests_per_day}\n"
            f"🚫 **ضد اسپم:** {'✅ فعال' if security.enable_anti_spam else '❌ غیرفعال'}\n"
            f"⛔ **پسوندهای مسدود:** {', '.join(security.blocked_extensions)}\n\n"
            f"📈 **آمار فعلی:**\n"
            f"• 👥 کاربران فعال: {len(config.user_sessions)}\n"
            f"• ⏰ آخرین درخواست: {config.statistics.last_active}\n\n"
            f"💡 **نکته:**\n"
            f"برای تغییر این تنظیمات، فایل .env را ویرایش کنید"
        )
        
        await message.answer(security_text, parse_mode=ParseMode.MARKDOWN)
