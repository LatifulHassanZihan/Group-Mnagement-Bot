
import os
import json
import secrets
from typing import Dict, Any

class Config:
    def __init__(self):
        # Get bot token from environment variable
        self.token = os.environ.get('BOT_TOKEN')
        if not self.token:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        # Get webhook URL for production
        self.webhook_url = os.environ.get('WEBHOOK_URL', '')
        self.port = int(os.environ.get('PORT', 10000))
        self.admin_id = int(os.environ.get('ADMIN_ID', 0))
        
        # Generate a proper secret token (alphanumeric + hyphen/underscore only)
        self.secret_token = os.environ.get('SECRET_TOKEN', self.generate_secret_token())
        
        # Use Render's persistent disk for database
        self.database_url = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
        
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
    
    def generate_secret_token(self):
        """Generate a proper secret token that meets Telegram requirements"""
        # Telegram requires: 1-256 characters, containing A-Z, a-z, 0-9, _ and -
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def load_settings(self):
        try:
            # Use /tmp directory for Render compatibility
            settings_path = '/tmp/group_settings.json'
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    self.group_settings = json.load(f)
            else:
                self.group_settings = {}
        except (FileNotFoundError, json.JSONDecodeError):
            self.group_settings = {}
    
    def save_settings(self):
        try:
            # Use /tmp directory for Render compatibility
            settings_path = '/tmp/group_settings.json'
            with open(settings_path, 'w') as f:
                json.dump(self.group_settings, f, indent=4)
        except Exception as e:
            print(f"Warning: Could not save settings: {e}")
    
    def get_chat_settings(self, chat_id: int) -> Dict[str, Any]:
        if str(chat_id) not in self.group_settings:
            self.group_settings[str(chat_id)] = self.default_settings.copy()
            self.save_settings()
        return self.group_settings[str(chat_id)]
    
    def update_chat_settings(self, chat_id: int, settings: Dict[str, Any]):
        self.group_settings[str(chat_id)] = settings
        self.save_settings()

# Global config instance
config = Config()
