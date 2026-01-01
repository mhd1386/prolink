"""
مدیریت دانلود فایل‌ها
"""

import aiohttp
import aiofiles
import asyncio
import os
import re
from typing import Optional, Dict, Set
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DownloadManager:
    """مدیریت دانلود فایل‌ها با قابلیت محدودیت همزمان"""
    
    def __init__(self, max_file_size: int = 2 * 1024 * 1024 * 1024,  # 2GB
                 parallel_downloads: int = 3):
        self.max_file_size = max_file_size
        self.parallel_downloads = parallel_downloads
        self.semaphore = asyncio.Semaphore(parallel_downloads)
        self.active_downloads: Set[int] = set()  # user_id های در حال دانلود
        self.session: Optional[aiohttp.ClientSession] = None
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """دریافت یا ایجاد session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=300)  # 5 دقیقه
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def download_file(self, url: str, user_id: int) -> Optional[Path]:
        """
        دانلود فایل از URL
        بازگشت: مسیر فایل دانلود شده یا None در صورت خطا
        """
        # بررسی اینکه کاربر در حال دانلود فایل دیگری نباشد
        if user_id in self.active_downloads:
            raise Exception("⏳ شما در حال دانلود فایل دیگری هستید")
        
        self.active_downloads.add(user_id)
        
        try:
            async with self.semaphore:
                return await self._download_file_internal(url, user_id)
        finally:
            self.active_downloads.discard(user_id)
    
    async def _download_file_internal(self, url: str, user_id: int) -> Optional[Path]:
        """دانلود داخلی فایل"""
        session = await self._get_session()
        
        try:
            # بررسی HEAD برای دریافت اطلاعات فایل
            async with session.head(url, allow_redirects=True) as response:
                if not response.status == 200:
                    raise Exception(f"❌ سرور خطا داد: {response.status}")
                
                content_length = response.headers.get('Content-Length')
                if content_length:
                    file_size = int(content_length)
                    if file_size > self.max_file_size:
                        raise Exception(f"❌ حجم فایل ({self._format_size(file_size)}) بیش از حد مجاز ({self._format_size(self.max_file_size)}) است")
                    if file_size == 0:
                        raise Exception("❌ فایل خالی است یا حجم نامشخص")
                
                # بررسی نوع محتوا
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' in content_type:
                    raise Exception("❌ لینک معتبر فایل نیست (صفحه HTML)")
            
            # استخراج نام فایل
            filename = self._extract_filename(url, response.headers)
            
            # بررسی پسوند فایل
            if not self._check_file_extension(filename):
                raise Exception("❌ این نوع فایل به دلایل امنیتی مجاز نیست")
            
            # ایجاد نام فایل منحصر به فرد
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{user_id}_{timestamp}_{filename}"
            filepath = self.temp_dir / unique_filename
            
            # دانلود فایل
            logger.info(f"شروع دانلود فایل: {filename} از {url}")
            
            async with session.get(url) as response:
                response.raise_for_status()
                
                total_size = 0
                async with aiofiles.open(filepath, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):  # 8KB chunks
                        await f.write(chunk)
                        total_size += len(chunk)
                        
                        if total_size > self.max_file_size:
                            await f.close()
                            if filepath.exists():
                                filepath.unlink()
                            raise Exception("❌ حجم فایل بیش از حد مجاز است")
            
            logger.info(f"دانلود کامل شد: {filename} - حجم: {self._format_size(total_size)}")
            return filepath
            
        except aiohttp.ClientError as e:
            raise Exception(f"❌ خطا در ارتباط با سرور: {str(e)}")
        except asyncio.TimeoutError:
            raise Exception("❌ زمان دانلود به پایان رسید")
        except Exception as e:
            raise e
    
    def _extract_filename(self, url: str, headers: Dict) -> str:
        """استخراج نام فایل از URL یا headers"""
        # بررسی header Content-Disposition
        content_disposition = headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            match = re.search(r'filename=["\']?([^"\']+)["\']?', content_disposition)
            if match:
                return match.group(1).strip()
        
        # استخراج از URL
        url_path = url.split('?')[0]
        filename = url_path.split('/')[-1]
        
        if not filename or filename == '':
            filename = "file"
        
        # حذف کاراکترهای نامعتبر
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # اگر پسوند ندارد، اضافه کردن پسوند
        if '.' not in filename:
            content_type = headers.get('Content-Type', '')
            if 'image/jpeg' in content_type or 'image/jpg' in content_type:
                filename += '.jpg'
            elif 'image/png' in content_type:
                filename += '.png'
            elif 'video/mp4' in content_type:
                filename += '.mp4'
            elif 'application/pdf' in content_type:
                filename += '.pdf'
            elif 'application/zip' in content_type:
                filename += '.zip'
            else:
                filename += '.bin'
        
        return filename
    
    def _check_file_extension(self, filename: str) -> bool:
        """بررسی پسوند فایل برای امنیت"""
        from config import get_config
        import asyncio
        
        try:
            # بارگذاری تنظیمات (سازگار با پایتون 3.6)
            loop = asyncio.get_event_loop()
            config = loop.run_until_complete(get_config())
            blocked_extensions = config.security.blocked_extensions
            
            extension = filename.split('.')[-1].lower() if '.' in filename else ''
            return extension not in blocked_extensions
        except:
            # در صورت خطا، لیست پیش‌فرض
            blocked_extensions = ["exe", "scr", "bat", "cmd", "msi", "vbs"]
            extension = filename.split('.')[-1].lower() if '.' in filename else ''
            return extension not in blocked_extensions
    
    def _format_size(self, size_bytes: int) -> str:
        """فرمت‌بندی حجم فایل"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    async def cleanup_temp_files(self, older_than_hours: int = 24):
        """پاکسازی فایل‌های موقت قدیمی"""
        try:
            now = datetime.now().timestamp()
            for filepath in self.temp_dir.iterdir():
                if filepath.is_file():
                    file_age = now - filepath.stat().st_mtime
                    if file_age > older_than_hours * 3600:
                        filepath.unlink()
                        logger.info(f"فایل موقت حذف شد: {filepath.name}")
        except Exception as e:
            logger.error(f"خطا در پاکسازی فایل‌های موقت: {e}")
    
    async def shutdown(self):
        """خاموش کردن manager"""
        # پاکسازی فایل‌های موقت
        await self.cleanup_temp_files(older_than_hours=0)
        
        # بستن session
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """دستورات تخریب"""
        if self.session and not self.session.closed:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.session.close())
            except:
                pass
