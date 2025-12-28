#!/usr/bin/env python3
"""
Telegram Bot irProLink - Python Version
Professional file upload bot with advanced management
"""

import asyncio
import logging
import sys
from pathlib import Path

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
    
    try:
        # Create bot instance
        bot = TelegramBot()
        
        # Setup bot
        await bot.setup()
        
        # Run bot
        logger.info("Bot starting...")
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

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
