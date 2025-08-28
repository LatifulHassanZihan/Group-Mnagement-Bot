
import os
import json
from typing import Dict, Any

class Config:
    def __init__(self):
        self.token = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
        self.webhook_url = os.environ.get('WEBHOOK_URL', '')
        self.port = int(os.environ.get('PORT', 8443))
        self.admin_id = int(os.environ.get('ADMIN_ID', 123456789))  # Your Telegram ID
        self.database_url = os.environ.get('DATABASE_URL', 'sqlite:///bot.db')
        
        # Default settings for groups
        self.default_settings = {
            "welcome_message": "👋 Welcome {user_name} to {chat_title}! 🇵🇸\n\nPlease read the rules with /rules",
            "goodbye_message": "👋 Goodbye {user_name}! We'll miss you! ❤️",
            "rules": "📝 Please be respectful to all members. No spam, no NSFW content.",
            "warn_limit": 3,
            "mute_duration": 300,
            "language": "en",
            "antispam": True,
            "antiflood": True,
            "antilink": False,
            "captcha": False,
            "nightmode": False,
            "timezone": "UTC"
        }
        
        # Load custom settings if available
        self.load_settings()
    
    def load_settings(self):
        try:
            with open('group_settings.json', 'r') as f:
                self.group_settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.group_settings = {}
    
    def save_settings(self):
        with open('group_settings.json', 'w') as f:
            json.dump(self.group_settings, f, indent=4)
    
    def get_chat_settings(self, chat_id: int) -> Dict[str, Any]:
        if chat_id not in self.group_settings:
            self.group_settings[chat_id] = self.default_settings.copy()
            self.save_settings()
        return self.group_settings[chat_id]
    
    def update_chat_settings(self, chat_id: int, settings: Dict[str, Any]):
        self.group_settings[chat_id] = settings
        self.save_settings()

# Global config instance
config = Config()
