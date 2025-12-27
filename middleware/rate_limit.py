"""
Middleware برای محدودیت نرخ درخواست
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
import asyncio

from config import get_config

class RateLimitMiddleware(BaseMiddleware):
    """Middleware برای اعمال محدودیت نرخ درخواست"""
    
    def __init__(self):
        super().__init__()
        self.user_cooldowns: Dict[int, asyncio.Event] = {}
    
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
        
        # بررسی محدودیت نرخ
        allowed, error_message = config.check_rate_limit(user_id)
        
        if not allowed:
            await event.answer(error_message)
            return
        
        # افزایش شمارنده درخواست
        config.increment_request_count(user_id)
        
        # ادامه پردازش
        return await handler(event, data)
