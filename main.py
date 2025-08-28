import logging
import os
import sys
from telegram.ext import Application, ApplicationBuilder
from telegram import Update
from telegram.ext import ContextTypes
from keep_alive import keep_alive
keep_alive()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/bot.log')
    ]
)
logger = logging.getLogger(__name__)

try:
    from config import config
    from database import Database
    from handlers import CommandHandlers
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)

class GroupMegBot:
    def __init__(self):
        try:
            self.db = Database(config.database_url)
            self.handlers = CommandHandlers(self.db)
            self.application = None
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise
    
    async def post_init(self, application: Application):
        """Perform post initialization tasks"""
        await application.bot.set_my_commands([
            ("start", "Start the bot"),
            ("help", "Show help"),
            ("about", "About the bot"),
            ("rules", "Show group rules"),
            ("settings", "Group settings (admins only)"),
        ])
        
        # Set webhook if in production
        if config.webhook_url:
            webhook_url = f"{config.webhook_url}/{config.token}"
            logger.info(f"Setting webhook to: {webhook_url}")
            
            try:
                await application.bot.set_webhook(
                    url=webhook_url,
                    secret_token=config.secret_token,
                    drop_pending_updates=True,
                    allowed_updates=["message", "callback_query"]
                )
                logger.info("Webhook set successfully")
            except Exception as e:
                logger.error(f"Failed to set webhook: {e}")
                # Fall back to polling if webhook fails
                logger.info("Falling back to polling mode")
                config.webhook_url = ""
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors in the telegram bot"""
        logger.error(msg="Exception while handling an update:", exc_info=context.error)
        
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ An error occurred while processing your request. "
                    "The developer has been notified."
                )
            
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
            logger.info("Starting in webhook mode...")
            self.application.run_webhook(
                listen="0.0.0.0",
                port=config.port,
                secret_token=config.secret_token,
                webhook_url=f"{config.webhook_url}/{config.token}",
                drop_pending_updates=True
            )
        else:
            # Polling mode for development/fallback
            logger.info("Starting in polling mode...")
            self.application.run_polling(
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )

if __name__ == '__main__':
    try:
        logger.info("Starting GROUP MEG 🇵🇸 Bot...")
        logger.info(f"Webhook URL: {config.webhook_url}")
        logger.info(f"Using secret token: {config.secret_token}")
        
        bot = GroupMegBot()
        bot.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
