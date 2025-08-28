import logging
import os
import sys
from telegram.ext import Application, ApplicationBuilder
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
    logger.error(f"❌ Import error: {e}")
    sys.exit(1)

class GroupMegBot:
    def __init__(self):
        try:
            logger.info("🔧 Initializing bot components...")
            self.db = Database(config.database_url)
            self.handlers = CommandHandlers(self.db)
            self.application = None
            logger.info("✅ Bot components initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {e}")
            raise
    
    async def post_init(self, application):
        """Perform post initialization tasks"""
        try:
            await application.bot.set_my_commands([
                ("start", "Start the bot"),
                ("help", "Show help"),
                ("about", "About the bot"),
                ("rules", "Show group rules"),
                ("settings", "Group settings (admins only)"),
            ])
            logger.info("✅ Bot commands set successfully")
            
            # Set webhook if enabled
            if config.use_webhook and config.webhook_url:
                webhook_url = f"{config.webhook_url}/{config.token}"
                logger.info(f"🌐 Setting webhook to: {webhook_url}")
                
                await application.bot.set_webhook(
                    url=webhook_url,
                    secret_token=config.secret_token,
                    drop_pending_updates=True,
                    allowed_updates=["message", "callback_query"]
                )
                logger.info("✅ Webhook set successfully")
                
        except Exception as e:
            logger.error(f"❌ Error in post_init: {e}")
    
    def setup_handlers(self):
        """Set up all handlers"""
        try:
            for handler in self.handlers.get_handlers():
                self.application.add_handler(handler)
            self.application.add_error_handler(self.error_handler)
            logger.info("✅ Handlers set up successfully")
        except Exception as e:
            logger.error(f"❌ Error setting up handlers: {e}")
            raise
    
    async def error_handler(self, update, context):
        """Handle errors in the telegram bot"""
        logger.error(f"❌ Exception: {context.error}")
        
        try:
            if update and hasattr(update, 'effective_message'):
                await update.effective_message.reply_text(
                    "❌ An error occurred. The developer has been notified."
                )
            
            if config.admin_id:
                error_msg = f"⚠️ Error: {context.error}"
                await context.bot.send_message(chat_id=config.admin_id, text=error_msg)
                
        except Exception as e:
            logger.error(f"❌ Error in error handler: {e}")
    
    def run(self):
        """Run the bot"""
        try:
            logger.info("🚀 Starting GROUP MEG 🇵🇸 Bot...")
            
            # Create application
            self.application = ApplicationBuilder() \
                .token(config.token) \
                .post_init(self.post_init) \
                .build()
            
            # Set up handlers
            self.setup_handlers()
            
            # Start the bot
            if config.use_webhook and config.webhook_url:
                logger.info("🌐 Starting in webhook mode...")
                self.application.run_webhook(
                    listen="0.0.0.0",
                    port=config.port,
                    secret_token=config.secret_token,
                    webhook_url=f"{config.webhook_url}/{config.token}",
                    drop_pending_updates=True
                )
            else:
                logger.info("📡 Starting in polling mode...")
                self.application.run_polling(
                    drop_pending_updates=True,
                    allowed_updates=["message", "callback_query"]
                )
                
        except Exception as e:
            logger.error(f"❌ Fatal error in run(): {e}")
            raise

if __name__ == '__main__':
    try:
        bot = GroupMegBot()
        bot.run()
    except Exception as e:
        logger.error(f"💥 Failed to start bot: {e}")
        sys.exit(1)
