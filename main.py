import logging
from telegram.ext import Application, ApplicationBuilder
from telegram import Update
from telegram.ext import ContextTypes

from config import config
from database import Database
from handlers import CommandHandlers
from keep_alive import keep_alive
keep_alive()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class GroupMegBot:
    def __init__(self):
        self.db = Database(config.database_url)
        self.handlers = CommandHandlers(self.db)
        self.application = None
    
    async def post_init(self, application: Application):
        """Perform post initialization tasks"""
        await application.bot.set_my_commands([
            ("start", "Start the bot"),
            ("help", "Show help"),
            ("about", "About the bot"),
            ("rules", "Show group rules"),
            ("settings", "Group settings (admins only)"),
        ])
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors in the telegram bot"""
        logger.error(msg="Exception while handling an update:", exc_info=context.error)
        
        try:
            # Notify the user that an error occurred
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ An error occurred while processing your request. "
                    "The developer has been notified."
                )
            
            # Notify the developer
            if config.admin_id:
                error_msg = f"Error in update {update.update_id if update else 'N/A'}:\n{context.error}"
                await context.bot.send_message(chat_id=config.admin_id, text=error_msg)
        
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
    
    def setup_handlers(self):
        """Set up all handlers"""
        # Add command handlers
        for handler in self.handlers.get_handlers():
            self.application.add_handler(handler)
        
        # Add error handler
        self.application.add_error_handler(self.error_handler)
    
    def run(self):
        """Run the bot"""
        # Create application
        self.application = ApplicationBuilder() \
            .token(config.token) \
            .post_init(self.post_init) \
            .build()
        
        # Set up handlers
        self.setup_handlers()
        
        # Start the bot
        if config.webhook_url:
            # Webhook mode for production
            self.application.run_webhook(
                listen="0.0.0.0",
                port=config.port,
                url_path=config.token,
                webhook_url=config.webhook_url
            )
        else:
            # Polling mode for development
            self.application.run_polling()

if __name__ == '__main__':
    bot = GroupMegBot()
    bot.run()
