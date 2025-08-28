from datetime import datetime, timedelta
from typing import List, Dict, Any
from telegram import Update, InputMediaPhoto, InputMediaVideo, InputMediaDocument
from telegram.ext import ContextTypes

from database import Database
from utilities import is_admin

class ChannelManager:
    def __init__(self, db: Database):
        self.db = db
        self.scheduled_posts = {}
    
    async def schedule_post(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Schedule a post for a channel"""
        if not is_admin(update, context):
            await update.message.reply_text("❌ This command is only available for admins.")
            return
        
        if not context.args or len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /schedule <channel_id> <time> <message>\nTime format: 1h, 30m, 2d")
            return
        
        try:
            channel_id = context.args[0]
            time_str = context.args[1]
            message = ' '.join(context.args[2:])
            
            # Parse time
            time_units = {
                's': 1,
                'm': 60,
                'h': 3600,
                'd': 86400,
            }
            
            match = re.match(r'^(\d+)([smhd])$', time_str.lower())
            if not match:
                await update.message.reply_text("❌ Invalid time format. Use: 1h, 30m, 2d")
                return
            
            amount, unit = match.groups()
            delay = int(amount) * time_units[unit]
            
            # Schedule the post
            post_time = datetime.now() + timedelta(seconds=delay)
            self.scheduled_posts[len(self.scheduled_posts)] = {
                'channel_id': channel_id,
                'message': message,
                'time': post_time
            }
            
            await update.message.reply_text(
                f"✅ Post scheduled for {post_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error scheduling post: {str(e)}")
    
    async def cross_post(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cross-post a message to multiple channels"""
        if not is_admin(update, context):
            await update.message.reply_text("❌ This command is only available for admins.")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Please reply to a message to cross-post it.")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please provide channel IDs.\nUsage: /crosspost <channel_id1> <channel_id2> ...")
            return
        
        try:
            message = update.message.reply_to_message
            channel_ids = context.args
            
            for channel_id in channel_ids:
                if message.text:
                    await context.bot.send_message(chat_id=channel_id, text=message.text)
                elif message.photo:
                    await context.bot.send_photo(
                        chat_id=channel_id,
                        photo=message.photo[-1].file_id,
                        caption=message.caption
                    )
                elif message.video:
                    await context.bot.send_video(
                        chat_id=channel_id,
                        video=message.video.file_id,
                        caption=message.caption
                    )
                elif message.document:
                    await context.bot.send_document(
                        chat_id=channel_id,
                        document=message.document.file_id,
                        caption=message.caption
                    )
            
            await update.message.reply_text(f"✅ Message cross-posted to {len(channel_ids)} channels.")
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error cross-posting: {str(e)}")
    
    async def export_subscribers(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Export channel subscribers list"""
        if not is_admin(update, context):
            await update.message.reply_text("❌ This command is only available for admins.")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please provide a channel ID.\nUsage: /exportsubs <channel_id>")
            return
        
        try:
            channel_id = context.args[0]
            
            # Get channel members count (approximate)
            chat = await context.bot.get_chat(channel_id)
            member_count = chat.get_members_count()
            
            # Create a simple CSV file
            csv_content = f"Channel: {chat.title}\nSubscribers: {member_count}\nExported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Send as document
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=csv_content.encode(),
                filename=f"subscribers_{channel_id}.txt"
            )
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error exporting subscribers: {str(e)}")
    
    async def check_scheduled_posts(self, context: ContextTypes.DEFAULT_TYPE):
        """Check and send scheduled posts"""
        current_time = datetime.now()
        posts_to_remove = []
        
        for post_id, post in self.scheduled_posts.items():
            if current_time >= post['time']:
                try:
                    await context.bot.send_message(
                        chat_id=post['channel_id'],
                        text=post['message']
                    )
                    posts_to_remove.append(post_id)
                except Exception as e:
                    print(f"Error sending scheduled post: {e}")
        
        # Remove sent posts
        for post_id in posts_to_remove:
            del self.scheduled_posts[post_id]
