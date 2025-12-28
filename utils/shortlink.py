"""
سرویس لینک کوتاه
"""

import aiohttp
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ShortLinkService:
    """سرویس لینک کوتاه با پشتیبانی از چندین سرویس"""
    
    def __init__(self, service: str = "is.gd"):
        self.service = service
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """دریافت یا ایجاد session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def shorten_url(self, url: str) -> str:
        """
        کوتاه کردن لینک
        بازگشت: لینک کوتاه شده یا لینک اصلی در صورت خطا
        """
        if not url or not url.startswith(("http://", "https://")):
            return url
        
        try:
            session = await self._get_session()
            
            if self.service == "tinyurl":
                return await self._shorten_tinyurl(session, url)
            elif self.service == "is.gd":
                return await self._shorten_isgd(session, url)
            elif self.service == "cleanuri":
                return await self._shorten_cleanuri(session, url)
            else:
                logger.warning(f"سرویس لینک کوتاه نامعتبر: {self.service}")
                return url
                
        except Exception as e:
            logger.error(f"خطا در کوتاه کردن لینک {url}: {e}")
            return url
    
    async def _shorten_tinyurl(self, session: aiohttp.ClientSession, url: str) -> str:
        """کوتاه کردن با TinyURL"""
        api_url = f"https://tinyurl.com/api-create.php?url={url}"
        async with session.get(api_url) as response:
            if response.status == 200:
                short_url = await response.text()
                if short_url.startswith("http"):
                    logger.info(f"لینک کوتاه شده با TinyURL: {url} -> {short_url}")
                    return short_url
        return url
    
    async def _shorten_isgd(self, session: aiohttp.ClientSession, url: str) -> str:
        """کوتاه کردن با is.gd"""
        api_url = f"https://is.gd/create.php?format=simple&url={url}"
        async with session.get(api_url) as response:
            if response.status == 200:
                short_url = await response.text()
                if short_url.startswith("http"):
                    logger.info(f"لینک کوتاه شده با is.gd: {url} -> {short_url}")
                    return short_url
        return url
    
    async def _shorten_cleanuri(self, session: aiohttp.ClientSession, url: str) -> str:
        """کوتاه کردن با CleanURI"""
        api_url = "https://cleanuri.com/api/v1/shorten"
        data = {"url": url}
        
        async with session.post(api_url, data=data) as response:
            if response.status == 200:
                result = await response.json()
                if "result_url" in result:
                    short_url = result["result_url"]
                    logger.info(f"لینک کوتاه شده با CleanURI: {url} -> {short_url}")
                    return short_url
        return url
    
    async def close(self):
        """بستن session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """دستورات تخریب"""
        if self.session and not self.session.closed:
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.session.close())
            except:
                pass
