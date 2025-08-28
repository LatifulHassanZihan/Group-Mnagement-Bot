import re
import random
from typing import List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Bengali language support
BENGALI_RESPONSES = {
    "welcome": "👋 স্বাগতম {user_name} {chat_title} এ! 🇵🇸\n\nদয়া করে /rules দিয়ে নিয়মগুলি পড়ুন",
    "goodbye": "👋 বিদায় {user_name}! আমরা আপনাকে মিস করব! ❤️",
    "rules": "📝 দয়া করে সকল সদস্যের প্রতি শ্রদ্ধাশীল হন। স্প্যাম না, NSFW কন্টেন্ট না।",
    "warned": "⚠️ সতর্কতা: {reason}\nসর্বমোট সতর্কতা: {count}/3",
    "kicked": "🚫 আপনি গ্রুপ থেকে বের করে দেওয়া হয়েছে। কারণ: {reason}",
    "banned": "🔒 আপনি গ্রুপ থেকে স্থায়ীভাবে নিষিদ্ধ করা হয়েছে। কারণ: {reason}",
    "muted": "🔇 আপনি {duration} সেকেন্ডের জন্য মিউট করা হয়েছে। কারণ: {reason}",
    "unmuted": "🔊 আপনার মিউট সরানো হয়েছে।",
    "admin_only": "❌ এই কমান্ডটি শুধুমাত্র অ্যাডমিনদের জন্য।",
    "reply_needed": "❌ দয়া করে এই কমান্ডটি ব্যবহার করার জন্য একটি ব্যবহারকারীর রিপ্লাই করুন।",
}

def get_bengali_text(key: str, **kwargs) -> str:
    """Get Bengali text for the given key with formatting"""
    if key in BENGALI_RESPONSES:
        return BENGALI_RESPONSES[key].format(**kwargs)
    return key

def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is admin in the group"""
    if update.effective_chat.type == 'private':
        return False
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Check if user is admin
    member = context.bot.get_chat_member(chat_id, user_id)
    return member.status in ['administrator', 'creator']

def is_owner(user_id: int) -> bool:
    """Check if user is the bot owner"""
    from config import config
    return user_id == config.admin_id

def parse_time(time_str: str) -> Optional[int]:
    """Parse time string like 1h, 30m, 2d into seconds"""
    if not time_str:
        return None
    
    time_units = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
    }
    
    match = re.match(r'^(\d+)([smhd])$', time_str.lower())
    if match:
        amount, unit = match.groups()
        return int(amount) * time_units[unit]
    
    return None

def format_time(seconds: int) -> str:
    """Format seconds into human readable time"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m"
    elif seconds < 86400:
        return f"{seconds // 3600}h"
    else:
        return f"{seconds // 86400}d"

def build_menu(buttons: List[InlineKeyboardButton], 
               n_cols: int = 2, 
               header_buttons: List[InlineKeyboardButton] = None,
               footer_buttons: List[InlineKeyboardButton] = None) -> InlineKeyboardMarkup:
    """Build inline keyboard menu with specified columns"""
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    
    return InlineKeyboardMarkup(menu)

def get_main_keyboard() -> InlineKeyboardMarkup:
    """Get main menu keyboard"""
    buttons = [
        InlineKeyboardButton("➕ Add to Group", url="https://t.me/group_meg_bot?startgroup=true"),
        InlineKeyboardButton("📋 Commands", callback_data="commands"),
        InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
        InlineKeyboardButton("📊 Stats", callback_data="stats"),
        InlineKeyboardButton("👤 Profile", callback_data="profile"),
        InlineKeyboardButton("ℹ️ About", callback_data="about"),
        InlineKeyboardButton("📞 Contact Developer", url="https://t.me/alwayszihan"),
    ]
    return build_menu(buttons, n_cols=2)

def get_commands_keyboard() -> InlineKeyboardMarkup:
    """Get commands menu keyboard"""
    buttons = [
        InlineKeyboardButton("🔧 Basic", callback_data="commands_basic"),
        InlineKeyboardButton("🛡️ Moderation", callback_data="commands_mod"),
        InlineKeyboardButton("⚠️ Warnings", callback_data="commands_warn"),
        InlineKeyboardButton("👑 Roles", callback_data="commands_roles"),
        InlineKeyboardButton("👋 Welcome", callback_data="commands_welcome"),
        InlineKeyboardButton("📊 Info", callback_data="commands_info"),
        InlineKeyboardButton("🔒 Security", callback_data="commands_security"),
        InlineKeyboardButton("📈 Analytics", callback_data="commands_analytics"),
        InlineKeyboardButton("🎉 Fun", callback_data="commands_fun"),
        InlineKeyboardButton("🔙 Back", callback_data="main_menu"),
    ]
    return build_menu(buttons, n_cols=2)

def get_settings_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    """Get settings menu keyboard"""
    from config import config
    settings = config.get_chat_settings(chat_id)
    
    buttons = [
        InlineKeyboardButton(f"🛡️ Anti-Spam: {'✅' if settings['antispam'] else '❌'}", callback_data="toggle_antispam"),
        InlineKeyboardButton(f"🌊 Anti-Flood: {'✅' if settings['antiflood'] else '❌'}", callback_data="toggle_antiflood"),
        InlineKeyboardButton(f"🔗 Anti-Link: {'✅' if settings['antilink'] else '❌'}", callback_data="toggle_antilink"),
        InlineKeyboardButton(f"🧩 Captcha: {'✅' if settings['captcha'] else '❌'}", callback_data="toggle_captcha"),
        InlineKeyboardButton(f"🌙 Night Mode: {'✅' if settings['nightmode'] else '❌'}", callback_data="toggle_nightmode"),
        InlineKeyboardButton("📝 Set Rules", callback_data="set_rules"),
        InlineKeyboardButton("👋 Set Welcome", callback_data="set_welcome"),
        InlineKeyboardButton("👋 Set Goodbye", callback_data="set_goodbye"),
        InlineKeyboardButton("🌐 Set Language", callback_data="set_language"),
        InlineKeyboardButton("🕐 Set Timezone", callback_data="set_timezone"),
        InlineKeyboardButton("🔙 Back", callback_data="main_menu"),
    ]
    return build_menu(buttons, n_cols=2)
