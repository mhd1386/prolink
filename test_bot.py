#!/usr/bin/env python3
"""
Test script to diagnose bot startup issues
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
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def test_setup():
    """Test bot setup"""
    print("=" * 50)
    print("🤖 Testing Bot Setup")
    print("=" * 50)
    
    # Validate environment configuration
    print("1. Validating environment configuration...")
    if not env_config.validate():
        print("❌ Environment validation failed")
        return False
    print("✅ Environment validation passed")
    
    try:
        # Create bot instance
        print("2. Creating bot instance...")
        bot = TelegramBot()
        
        # Setup bot
        print("3. Setting up bot...")
        await bot.setup()
        print("✅ Bot setup completed successfully")
        
        # Test bot commands
        print("4. Testing bot commands...")
        if bot.bot:
            me = await bot.bot.get_me()
            print(f"✅ Bot connected: @{me.username} (ID: {me.id})")
        else:
            print("❌ Bot instance not created")
            return False
            
        print("5. Testing config loading...")
        if bot.config:
            print(f"✅ Config loaded: {len(bot.config.admin_ids)} admin(s)")
        else:
            print("❌ Config not loaded")
            return False
            
        print("6. Testing services...")
        if bot.shortlink_service:
            print("✅ Shortlink service initialized")
        else:
            print("❌ Shortlink service not initialized")
            
        if bot.download_manager:
            print("✅ Download manager initialized")
        else:
            print("❌ Download manager not initialized")
        
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)
        
        # Clean shutdown
        print("\nShutting down...")
        await bot.shutdown()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
        # Check for common issues
        if "aiogram" in str(e):
            print("\n⚠️ Aiogram related issue detected.")
            print("Possible solutions:")
            print("1. Make sure aiogram 2.18 is installed for Python 3.6")
            print("2. Check your BOT_TOKEN in .env file")
            print("3. Check internet connection to Telegram API")
        
        return False

if __name__ == "__main__":
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    # Run test
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(test_setup())
    
    if success:
        print("\n🎉 Bot setup test PASSED!")
        print("The bot should work correctly.")
        print("\nTo start the bot, run:")
        print("  ./start.sh")
        sys.exit(0)
    else:
        print("\n💥 Bot setup test FAILED!")
        print("Please check the error messages above.")
        sys.exit(1)
