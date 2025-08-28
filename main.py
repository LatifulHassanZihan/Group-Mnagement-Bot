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
        logging.FileHandler('/tmp/bot.log')  # Use /tmp for logging
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
    
    # ... rest of the class remains the same

if __name__ == '__main__':
    try:
        bot = GroupMegBot()
        bot.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
