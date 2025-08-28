import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from telegram import Update
from telegram.ext import ContextTypes

from config import config
from database import Database
from utilities import is_admin, parse_time, format_time, get_bengali_text

# Bad words list (can be customized per group)
DEFAULT_BAD_WORDS = [
    "badword1", "badword2", "badword3", 
    "spam", "scam", "hate", "violence"
]

class Moderation:
    def __init__(self, db: Database):
        self.db = db
        self.flood_data = {}  # {chat_id: {user_id: [message_times]}}
    
    async def check_flood(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if user is flooding the chat"""
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        # Get group settings
        settings = config.get_chat_settings(chat_id)
        if not settings.get('antiflood', True):
            return False
        
        # Initialize flood data for chat
        if chat_id not in self.flood_data:
            self.flood_data[chat_id] = {}
        
        # Initialize flood data for user
        if user_id not in self.flood_data[chat_id]:
            self.flood_data[chat_id][user_id] = []
        
        # Add current message time
        current_time = datetime.now()
        self.flood_data[chat_id][user_id].append(current_time)
        
        # Keep only messages from last 10 seconds
        self.flood_data[chat_id][user_id] = [
            t for t in self.flood_data[chat_id][user_id] 
            if current_time - t < timedelta(seconds=10)
        ]
        
        # Check if user has sent more than 5 messages in 10 seconds
        if len(self.flood_data[chat_id][user_id]) > 5:
            # Mute user for 5 minutes
            await self.mute_user(update, context, "300", "Flooding chat")
            return True
        
        return False
    
    async def check_spam(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if message contains spam"""
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        message = update.effective_message
        
        # Get group settings
        settings = config.get_chat_settings(chat_id)
        if not settings.get('antispam', True):
            return False
        
        # Check for bad words
        if message.text:
            text = message.text.lower()
            bad_words = settings.get('bad_words', DEFAULT_BAD_WORDS)
            
            for word in bad_words:
                if word.lower() in text:
                    # Delete message and warn user
                    await message.delete()
                    await self.warn_user(update, context, f"Using inappropriate word: {word}")
                    return True
        
        # Check for excessive emojis
        if message.text and len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]', message.text)) > 10:
            await message.delete()
            await self.warn_user(update, context, "Excessive emoji usage")
            return True
        
        return False
    
    async def check_links(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if message contains unauthorized links"""
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        message = update.effective_message
        
        # Get group settings
        settings = config.get_chat_settings(chat_id)
        if not settings.get('antilink', False) or is_admin(update, context):
            return False
        
        # Check for URLs
        if message.text and re.search(r'https?://\S+', message.text):
            # Delete message and warn user
            await message.delete()
            await self.warn_user(update, context, "Posting external links")
            return True
        
        return False
    
    async def warn_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str = "No reason provided"):
        """Warn a user"""
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Please reply to a user's message to warn them.")
            return
        
        chat_id = update.effective_chat.id
        target_user = update.message.reply_to_message.from_user
        admin_user = update.effective_user
        
        # Add warning to database
        self.db.add_warning(target_user.id, chat_id, reason, admin_user.id)
        
        # Get user's warning count
        warnings = self.db.get_warnings(target_user.id, chat_id)
        warning_count = len(warnings)
        
        # Get group settings
        settings = config.get_chat_settings(chat_id)
        warn_limit = settings.get('warn_limit', 3)
        
        # Check if warning limit reached
        if warning_count >= warn_limit:
            # Take action based on group settings
            action = settings.get('warn_action', 'mute')
            duration = settings.get('mute_duration', 300)
            
            if action == 'mute':
                await self.mute_user(update, context, str(duration), f"Reached warning limit: {reason}")
            elif action == 'kick':
                await self.kick_user(update, context, f"Reached warning limit: {reason}")
            elif action == 'ban':
                await self.ban_user(update, context, f"Reached warning limit: {reason}")
            
            # Reset warnings
            self.db.clear_warnings(target_user.id, chat_id)
            
            await update.message.reply_text(
                f"⚠️ {target_user.mention_html()} has been {action}ed for reaching the warning limit!"
            )
        else:
            # Send warning message
            await update.message.reply_text(
                f"⚠️ {target_user.mention_html()} has been warned!\n"
                f"Reason: {reason}\n"
                f"Warnings: {warning_count}/{warn_limit}"
            )
    
    async def mute_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, duration_str: str = None, reason: str = "No reason provided"):
        """Mute a user"""
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Please reply to a user's message to mute them.")
            return
        
        chat_id = update.effective_chat.id
        target_user = update.message.reply_to_message.from_user
        admin_user = update.effective_user
        
        # Parse duration
        duration = parse_time(duration_str) if duration_str else 300  # Default 5 minutes
        
        # Add moderation action to database
        self.db.add_moderation_action(target_user.id, chat_id, "mute", duration, reason, admin_user.id)
        
        # Restrict user in chat
        until_date = datetime.now() + timedelta(seconds=duration)
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False
            ),
            until_date=until_date
        )
        
        await update.message.reply_text(
            f"🔇 {target_user.mention_html()} has been muted for {format_time(duration)}!\n"
            f"Reason: {reason}"
        )
    
    async def unmute_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unmute a user"""
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Please reply to a user's message to unmute them.")
            return
        
        chat_id = update.effective_chat.id
        target_user = update.message.reply_to_message.from_user
        
        # Restore user permissions
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        
        await update.message.reply_text(
            f"🔊 {target_user.mention_html()} has been unmuted!"
        )
    
    async def kick_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str = "No reason provided"):
        """Kick a user from the group"""
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Please reply to a user's message to kick them.")
            return
        
        chat_id = update.effective_chat.id
        target_user = update.message.reply_to_message.from_user
        admin_user = update.effective_user
        
        # Add moderation action to database
        self.db.add_moderation_action(target_user.id, chat_id, "kick", 0, reason, admin_user.id)
        
        # Kick user from chat
        await context.bot.ban_chat_member(chat_id, target_user.id)
        await context.bot.unban_chat_member(chat_id, target_user.id)
        
        await update.message.reply_text(
            f"🚫 {target_user.mention_html()} has been kicked!\n"
            f"Reason: {reason}"
        )
    
    async def ban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str = "No reason provided"):
        """Ban a user from the group"""
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Please reply to a user's message to ban them.")
            return
        
        chat_id = update.effective_chat.id
        target_user = update.message.reply_to_message.from_user
        admin_user = update.effective_user
        
        # Add moderation action to database
        self.db.add_moderation_action(target_user.id, chat_id, "ban", 0, reason, admin_user.id)
        
        # Ban user from chat
        await context.bot.ban_chat_member(chat_id, target_user.id)
        
        await update.message.reply_text(
            f"🔒 {target_user.mention_html()} has been banned!\n"
            f"Reason: {reason}"
        )
    
    async def unban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int = None):
        """Unban a user from the group"""
        if user_id is None:
            if not context.args:
                await update.message.reply_text("❌ Please provide a user ID to unban.")
                return
            user_id = int(context.args[0])
        
        chat_id = update.effective_chat.id
        
        # Unban user from chat
        await context.bot.unban_chat_member(chat_id, user_id)
        
        await update.message.reply_text(
            f"🔓 User {user_id} has been unbanned!"
        )
