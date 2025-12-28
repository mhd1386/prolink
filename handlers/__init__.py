"""
ماژول ثبت هندلرها
"""

from aiogram import Dispatcher
from .user_handlers import UserHandlers
from .admin_handlers import AdminHandlers

async def register_handlers(dp: Dispatcher, bot):
    """ثبت تمام هندلرها"""
    user_handlers = UserHandlers(bot)
    admin_handlers = AdminHandlers(bot)
    
    # ثبت هندلرهای کاربر
    dp.message.register(user_handlers.handle_start, commands=["start"])
    dp.message.register(user_handlers.handle_help, commands=["help"])
    dp.message.register(user_handlers.handle_upload, commands=["upload"])
    dp.message.register(user_handlers.handle_support, commands=["support"])
    dp.message.register(user_handlers.handle_status, commands=["status"])
    dp.message.register(user_handlers.handle_user_stats, commands=["mystats"])
    
    # هندلر برای لینک‌های مستقیم
    dp.message.register(user_handlers.handle_direct_link)
    
    # ثبت هندلرهای ادمین
    dp.message.register(admin_handlers.handle_add_channel, commands=["addchannel"])
    dp.message.register(admin_handlers.handle_remove_channel, commands=["removechannel"])
    dp.message.register(admin_handlers.handle_list_channels, commands=["listchannels"])
    dp.message.register(admin_handlers.handle_add_admin, commands=["addadmin"])
    dp.message.register(admin_handlers.handle_remove_admin, commands=["removeadmin"])
    dp.message.register(admin_handlers.handle_list_admins, commands=["listadmins"])
    dp.message.register(admin_handlers.handle_display_config, commands=["displayconfig"])
    dp.message.register(admin_handlers.handle_toggle_filename, commands=["togglefilename"])
    dp.message.register(admin_handlers.handle_toggle_filesize, commands=["togglefilesize"])
    dp.message.register(admin_handlers.handle_toggle_sourceurl, commands=["togglesourceurl"])
    dp.message.register(admin_handlers.handle_toggle_userid, commands=["toggleuserid"])
    dp.message.register(admin_handlers.handle_toggle_copyright, commands=["togglecopyright"])
    dp.message.register(admin_handlers.handle_toggle_shortlink, commands=["toggleshortlink"])
    dp.message.register(admin_handlers.handle_set_copyright, commands=["setcopyright"])
    dp.message.register(admin_handlers.handle_set_shortlink_service, commands=["setshortlinkservice"])
    dp.message.register(admin_handlers.handle_save_config, commands=["saveconfig"])
    dp.message.register(admin_handlers.handle_broadcast, commands=["broadcast"])
    dp.message.register(admin_handlers.handle_full_stats, commands=["fullstats"])
    dp.message.register(admin_handlers.handle_reset_stats, commands=["resetstats"])
    dp.message.register(admin_handlers.handle_security_settings, commands=["security"])
