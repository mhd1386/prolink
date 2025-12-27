"""
Middleware برای بررسی دسترسی ادمین
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

from config import get_config

class AdminMiddleware(BaseMiddleware):
    """Middleware برای بررسی دسترسی ادمین"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # بررسی اینکه آیا پیام از کاربر است
        if not event.from_user:
            return await handler(event, data)
        
        user_id = event.from_user.id
        
        # دریافت تنظیمات
        config = await get_config()
        
        # بررسی دستورات ادمین
        command = event.text
        if command and command.startswith('/'):
            # استخراج نام دستور
            cmd_name = command.split()[0].lower()
            
            # لیست دستورات ادمین
            admin_commands = [
                '/addchannel', '/removechannel', '/listchannels',
                '/addadmin', '/removeadmin', '/listadmins',
                '/displayconfig', '/togglefilename', '/togglefilesize',
                '/togglesourceurl', '/toggleuserid', '/togglecopyright',
                '/toggleshortlink', '/setcopyright', '/setshortlinkservice',
                '/saveconfig', '/broadcast', '/fullstats', '/resetstats',
                '/security'
            ]
            
            # اگر دستور ادمین است، بررسی دسترسی
            if any(cmd_name.startswith(cmd) for cmd in admin_commands):
                if not config.is_admin(user_id):
                    await event.answer("⛔ دسترسی ممنوع! این دستور فقط برای ادمین‌ها قابل استفاده است.")
                    return
        
        # ادامه پردازش
        return await handler(event, data)
