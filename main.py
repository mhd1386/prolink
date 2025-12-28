#!/usr/bin/env python3
"""
Telegram Bot irProLink - Python Version
Professional file upload bot with advanced management
"""

import asyncio
import logging
import sys
import site
from pathlib import Path

# Add user site-packages to sys.path for --user installed packages
try:
    user_site = site.getusersitepackages()
    if user_site and user_site not in sys.path:
        sys.path.insert(0, user_site)
except Exception:
    pass

# Add project path to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from bot.bot import TelegramBot
from config import env_config

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main bot execution function"""
    print("=" * 50)
    print("🤖 irProLink Bot - Python Version")
    print("🚀 Version: 6.1.0")
    print("📅 Release Year: 2026")
    print("👑 Main Admin: 7660976743")
    print("=" * 50)
    
    # Validate environment configuration
    if not env_config.validate():
        sys.exit(1)
    
    bot = None
    try:
        # Create bot instance
        logger.info("Creating bot instance...")
        bot = TelegramBot()
        
        # Setup bot
        logger.info("Setting up bot...")
        await bot.setup()
        logger.info("Bot setup completed successfully")
        
        # Run bot
        logger.info("Bot starting polling...")
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except asyncio.CancelledError:
        logger.info("Bot task cancelled.")
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        # Try to get more details about the error
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error details:\n{error_details}")
        
        # Check if it's an aiogram specific error
        if "aiogram" in str(e).lower():
            logger.error("Aiogram related error detected.")
            logger.error("This might be due to Python 3.6 compatibility issues.")
            logger.error("Make sure aiogram 2.18 is installed for Python 3.6")
        
        sys.exit(1)
    finally:
        if bot:
            try:
                logger.info("Shutting down bot...")
                await bot.shutdown()
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    # Run bot (compatible with Python 3.6)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
