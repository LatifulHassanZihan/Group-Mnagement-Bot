import os
import json
import secrets
import string
from typing import Dict, Any

class Config:
    def __init__(self):
        # Get bot token from environment variable (REQUIRED)
        self.token = os.environ.get('BOT_TOKEN')
        if not self.token:
            raise ValueError("❌ BOT_TOKEN environment variable is required. Get it from @BotFather")
        
        # Get admin ID from environment variable (REQUIRED)
        self.admin_id = int(os.environ.get('ADMIN_ID', 0))
        if not self.admin_id:
            print("⚠️  WARNING: ADMIN_ID not set. Some features may not work properly.")
        
        # Get secret token from environment or generate one
        self.secret_token = os.environ.get('SECRET_TOKEN', self.generate_secret_token())
        
        # Webhook configuration
        self.webhook_url = os.environ.get('WEBHOOK_URL', '')
        self.use_webhook = os.environ.get('USE_WEBHOOK', 'false').lower() == 'true'
        self.port = int(os.environ.get('PORT', 10000))
        
        # Database configuration
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
        
        # Print configuration for debugging
        self.print_config()
    
    def generate_secret_token(self):
        """Generate a proper secret token that meets Telegram requirements"""
        alphabet = string.ascii_letters + string.digits + "_-"
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def print_config(self):
        """Print configuration for debugging purposes"""
        print("🔧 Configuration Loaded:")
        print(f"   🤖 BOT_TOKEN: {'✅ Set' if self.token else '❌ Missing'}")
        print(f"   👑 ADMIN_ID: {self.admin_id if self.admin_id else '❌ Not set'}")
        print(f"   🔐 SECRET_TOKEN: {self.secret_token}")
        print(f"   🌐 WEBHOOK_URL: {self.webhook_url if self.webhook_url else '❌ Not set'}")
        print(f"   📡 USE_WEBHOOK: {self.use_webhook}")
        print(f"   🚪 PORT: {self.port}")
        print(f"   💾 DATABASE_URL: {self.database_url}")
    
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
            print(f"⚠️  Warning: Could not save settings: {e}")
    
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
