from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

from config import config
from database import Database
from utilities import get_bengali_text

class WelcomeHandler:
    def __init__(self, db: Database):
        self.db = db
    
    async def send_welcome(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message to new members"""
        chat_id = update.effective_chat.id
        
        # Get group settings
        settings = config.get_chat_settings(chat_id)
        
        # Update statistics
        self.db.update_statistics(chat_id, datetime.now().strftime('%Y-%m-%d'), joins=1)
        
        for new_member in update.message.new_chat_members:
            # Skip if the new member is the bot itself
            if new_member.id == context.bot.id:
                await update.message.reply_text(
                    "🙏 Thanks for adding me to this group! "
                    "Use /help to see what I can do. 🇵🇸"
                )
                continue
            
            # Add user to database
            self.db.add_user(
                new_member.id,
                new_member.username,
                new_member.first_name,
                new_member.last_name
            )
            
            # Get welcome message
            welcome_message = settings.get('welcome_message', 
                "👋 Welcome {user_name} to {chat_title}! 🇵🇸\n\nPlease read the rules with /rules")
            
            # Format welcome message
            formatted_message = welcome_message.format(
                user_name=new_member.mention_html(),
                chat_title=update.effective_chat.title,
                user_id=new_member.id
            )
            
            # Send welcome message
            await update.message.reply_text(
                formatted_message,
                parse_mode='HTML'
            )
            
            # Send captcha if enabled
            if settings.get('captcha', False):
                await self.send_captcha(update, context, new_member)
    
    async def send_goodbye(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send goodbye message to leaving members"""
        chat_id = update.effective_chat.id
        
        # Get group settings
        settings = config.get_chat_settings(chat_id)
        
        # Update statistics
        self.db.update_statistics(chat_id, datetime.now().strftime('%Y-%m-%d'), leaves=1)
        
        left_member = update.message.left_chat_member
        
        # Get goodbye message
        goodbye_message = settings.get('goodbye_message', 
            "👋 Goodbye {user_name}! We'll miss you! ❤️")
        
        # Format goodbye message
        formatted_message = goodbye_message.format(
            user_name=left_member.mention_html(),
            chat_title=update.effective_chat.title
        )
        
        # Send goodbye message
        await update.message.reply_text(
            formatted_message,
            parse_mode='HTML'
        )
    
    async def send_captcha(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user):
        """Send captcha to new user"""
        # Simple math captcha for demonstration
        import random
        
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        answer = num1 + num2
        
        # Store captcha answer in context
        if 'captcha' not in context.chat_data:
            context.chat_data['captcha'] = {}
        
        context.chat_data['captcha'][user.id] = answer
        
        # Send captcha message
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🔒 {user.mention_html()}, please solve this captcha to verify you're human:\n"
                 f"{num1} + {num2} = ?",
            parse_mode='HTML'
        )
