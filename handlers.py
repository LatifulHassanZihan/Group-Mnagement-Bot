from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from config import config
from database import Database
from utilities import is_admin, is_owner, get_main_keyboard, get_commands_keyboard, get_settings_keyboard
from moderation import Moderation
from welcome import WelcomeHandler
from analytics import Analytics
from channel import ChannelManager

class CommandHandlers:
    def __init__(self, db: Database):
        self.db = db
        self.moderation = Moderation(db)
        self.welcome = WelcomeHandler(db)
        self.analytics = Analytics(db)
        self.channel = ChannelManager(db)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message with main menu"""
        user = update.effective_user
        
        # Add user to database
        self.db.add_user(user.id, user.username, user.first_name, user.last_name)
        
        # Send welcome message with inline keyboard
        keyboard = get_main_keyboard()
        
        await update.message.reply_text(
            f"👋 Welcome to GROUP MEG 🇵🇸!\n\n"
            f"I'm a powerful group management bot with advanced moderation features.\n\n"
            f"🌟 Features:\n"
            f"• 🔒 Advanced moderation tools\n"
            f"• 📊 Detailed analytics and statistics\n"
            f"• 👋 Custom welcome/goodbye messages\n"
            f"• 🛡️ Anti-spam and flood protection\n"
            f"• 📢 Channel management tools\n"
            f"• 🇧🇩 Bengali language support\n\n"
            f"Use the buttons below to get started!",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message with commands"""
        keyboard = get_commands_keyboard()
        
        await update.message.reply_text(
            "📋 <b>GROUP MEG 🇵🇸 - Command List</b>\n\n"
            "Select a category to view commands:",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    async def about(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show information about the bot"""
        await update.message.reply_text(
            f"🤖 <b>GROUP MEG 🇵🇸</b>\n\n"
            f"<b>Developer:</b> Latiful Hassan Zihan 🇵🇸\n"
            f"<b>Username:</b> @alwayszihan\n"
            f"<b>Nationality:</b> Bangladeshi 🇧🇩\n\n"
            f"<b>Features:</b>\n"
            f"• Advanced group moderation\n"
            f"• Custom welcome/goodbye messages\n"
            f"• Anti-spam and flood protection\n"
            f"• User analytics and statistics\n"
            f"• Channel management tools\n"
            f"• Bengali language support\n\n"
            f"<b>Version:</b> 2.0.0\n"
            f"<b>Library:</b> python-telegram-bot\n\n"
            f"Use /help to see all available commands.",
            parse_mode='HTML'
        )
    
    async def settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show settings menu"""
        if not is_admin(update, context):
            await update.message.reply_text("❌ This command is only available for admins.")
            return
        
        chat_id = update.effective_chat.id
        keyboard = get_settings_keyboard(chat_id)
        
        await update.message.reply_text(
            "⚙️ <b>Group Settings</b>\n\n"
            "Configure your group settings:",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    async def rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show group rules"""
        chat_id = update.effective_chat.id
        settings = config.get_chat_settings(chat_id)
        
        await update.message.reply_text(
            f"📝 <b>Group Rules</b>\n\n{settings.get('rules', 'No rules set yet.')}",
            parse_mode='HTML'
        )
    
    async def set_welcome(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set custom welcome message"""
        if not is_admin(update, context):
            await update.message.reply_text("❌ This command is only available for admins.")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please provide a welcome message.\nUsage: /setwelcome Your welcome message")
            return
        
        chat_id = update.effective_chat.id
        welcome_message = ' '.join(context.args)
        settings = config.get_chat_settings(chat_id)
        settings['welcome_message'] = welcome_message
        config.update_chat_settings(chat_id, settings)
        
        await update.message.reply_text("✅ Welcome message updated successfully!")
    
    async def set_goodbye(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set custom goodbye message"""
        if not is_admin(update, context):
            await update.message.reply_text("❌ This command is only available for admins.")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please provide a goodbye message.\nUsage: /setgoodbye Your goodbye message")
            return
        
        chat_id = update.effective_chat.id
        goodbye_message = ' '.join(context.args)
        settings = config.get_chat_settings(chat_id)
        settings['goodbye_message'] = goodbye_message
        config.update_chat_settings(chat_id, settings)
        
        await update.message.reply_text("✅ Goodbye message updated successfully!")
    
    async def show_welcome(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current welcome message"""
        chat_id = update.effective_chat.id
        settings = config.get_chat_settings(chat_id)
        
        await update.message.reply_text(
            f"👋 <b>Current Welcome Message</b>\n\n{settings.get('welcome_message', 'No welcome message set yet.')}",
            parse_mode='HTML'
        )
    
    async def show_goodbye(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current goodbye message"""
        chat_id = update.effective_chat.id
        settings = config.get_chat_settings(chat_id)
        
        await update.message.reply_text(
            f"👋 <b>Current Goodbye Message</b>\n\n{settings.get('goodbye_message', 'No goodbye message set yet.')}",
            parse_mode='HTML'
        )
    
    async def set_rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set group rules"""
        if not is_admin(update, context):
            await update.message.reply_text("❌ This command is only available for admins.")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please provide rules.\nUsage: /setrules Your group rules")
            return
        
        chat_id = update.effective_chat.id
        rules = ' '.join(context.args)
        settings = config.get_chat_settings(chat_id)
        settings['rules'] = rules
        config.update_chat_settings(chat_id, settings)
        
        await update.message.reply_text("✅ Group rules updated successfully!")
    
    async def set_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set bot language"""
        if not is_admin(update, context):
            await update.message.reply_text("❌ This command is only available for admins.")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please provide a language code.\nUsage: /language en")
            return
        
        chat_id = update.effective_chat.id
        language = context.args[0].lower()
        settings = config.get_chat_settings(chat_id)
        settings['language'] = language
        config.update_chat_settings(chat_id, settings)
        
        await update.message.reply_text(f"✅ Language set to {language}!")
    
    async def reload_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reload configuration"""
        if not is_admin(update, context):
            await update.message.reply_text("❌ This command is only available for admins.")
            return
        
        config.load_settings()
        await update.message.reply_text("✅ Configuration reloaded successfully!")
    
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "main_menu":
            keyboard = get_main_keyboard()
            await query.edit_message_text(
                "👋 Welcome to GROUP MEG 🇵🇸!\n\n"
                "Use the buttons below to navigate:",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        
        elif data == "commands":
            keyboard = get_commands_keyboard()
            await query.edit_message_text(
                "📋 <b>Command Categories</b>\n\n"
                "Select a category to view commands:",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        
        elif data == "commands_basic":
            await query.edit_message_text(
                "🔧 <b>Basic Commands</b>\n\n"
                "/start - Start the bot and show welcome message\n"
                "/help - Show all available commands\n"
                "/about - Show bot information\n"
                "/rules - Show group rules\n"
                "/settings - Open settings panel (admins only)\n\n"
                "<i>Use /help to see other command categories</i>",
                parse_mode='HTML'
            )
        
        elif data == "commands_mod":
            await query.edit_message_text(
                "🛡️ <b>Moderation Commands</b>\n\n"
                "/kick [reply] - Kick a user from the group\n"
                "/ban [reply] - Ban a user from the group\n"
                "/unban <user_id> - Unban a user by ID\n"
                "/mute [reply] <duration> - Mute a user temporarily\n"
                "/unmute [reply] - Unmute a user\n"
                "/purge - Delete multiple messages at once\n"
                "/lock - Lock the group (only admins can send messages)\n"
                "/unlock - Unlock the group\n\n"
                "<i>Use /help to see other command categories</i>",
                parse_mode='HTML'
            )
        
        elif data == "commands_warn":
            await query.edit_message_text(
                "⚠️ <b>Warning Commands</b>\n\n"
                "/warn [reply] <reason> - Warn a user\n"
                "/warnings [reply] - Show warnings for a user\n"
                "/clearwarns [reply] - Clear all warnings for a user\n"
                "/topwarned - Show users with most warnings\n\n"
                "<i>Use /help to see other command categories</i>",
                parse_mode='HTML'
            )
        
        # Add more command categories here...
        
        elif data == "settings":
            chat_id = query.message.chat_id
            keyboard = get_settings_keyboard(chat_id)
            await query.edit_message_text(
                "⚙️ <b>Group Settings</b>\n\n"
                "Configure your group settings:",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        
        elif data.startswith("toggle_"):
            chat_id = query.message.chat_id
            setting = data.replace("toggle_", "")
            settings = config.get_chat_settings(chat_id)
            
            if setting in settings:
                settings[setting] = not settings[setting]
                config.update_chat_settings(chat_id, settings)
                
                keyboard = get_settings_keyboard(chat_id)
                await query.edit_message_reply_markup(reply_markup=keyboard)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all incoming messages"""
        # Skip if message is from a channel
        if update.effective_chat.type == 'channel':
            return
        
        # Check for flood
        if await self.moderation.check_flood(update, context):
            return
        
        # Check for spam
        if await self.moderation.check_spam(update, context):
            return
        
        # Check for links
        if await self.moderation.check_links(update, context):
            return
        
        # Update statistics
        chat_id = update.effective_chat.id
        self.db.update_statistics(chat_id, update.message.date.strftime('%Y-%m-%d'), messages=1)
    
    def get_handlers(self):
        """Return all command handlers"""
        return [
            CommandHandler('start', self.start),
            CommandHandler('help', self.help_command),
            CommandHandler('about', self.about),
            CommandHandler('settings', self.settings),
            CommandHandler('rules', self.rules),
            CommandHandler('setwelcome', self.set_welcome),
            CommandHandler('setgoodbye', self.set_goodbye),
            CommandHandler('welcome', self.show_welcome),
            CommandHandler('goodbye', self.show_goodbye),
            CommandHandler('setrules', self.set_rules),
            CommandHandler('language', self.set_language),
            CommandHandler('reloadconfig', self.reload_config),
            CallbackQueryHandler(self.callback_handler),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message),
        ]
