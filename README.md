GROUP MEG 🇵🇸 - Advanced Telegram Group Management Bot

[https://img.shields.io/badge/python-3.8%252B-blue]
[https://img.shields.io/badge/Telegram-Bot-blue]
[https://img.shields.io/badge/license-MIT-green]
[https://img.shields.io/badge/deploy-Render-66C7FF]

A powerful, feature-rich Telegram group management bot built with Python and python-telegram-bot library. Designed for managing groups and channels with advanced administrative capabilities.
🌟 Features
🔧 Basic Commands

    /start - Start the bot and show welcome message

    /help - Show all available commands

    /about - Show bot information

    /rules - Display group rules

    /settings - Admin-only settings panel

🛡️ Moderation & Security

    User Management: Kick, ban, mute, unmute users

    Warning System: Automated actions after threshold limits

    Anti-Spam: Customizable bad word filtering

    Anti-Flood: Prevent message spamming

    Link Control: URL whitelist exceptions

    Media Restrictions: Control media types

📊 Analytics & Statistics

    /stats - Show group statistics

    /userstats - Detailed user statistics

    /topwarned - Users with most warnings

    /topactive - Most active members

    /activity - Message activity graph

    /metrics - Detailed message metrics

👋 Welcome & Goodbye

    Custom welcome messages with placeholders

    Custom goodbye messages

    Captcha verification for new users

    Rules presentation for new members

👑 Role Management

    Role-based access control

    Admin verification system

    Moderator permissions

    Whitelist functionality

📢 Channel Management

    Post scheduling

    Automated announcements

    Cross-posting between channels

    Subscriber tracking

🇧🇩 Bengali Language Support

    Bengali text support

    Localized responses

    Bengali command responses

🚀 Quick Start
Prerequisites

    Python 3.8+

    Telegram Bot Token from @BotFather

    Render account (for deployment)

Local Development

    Clone the repository
    bash

git clone https://github.com/your-username/group-meg-bot.git
cd group-meg-bot

Install dependencies
bash

pip install -r requirements.txt

Set up environment variables
bash

export BOT_TOKEN=your_bot_token_here
export ADMIN_ID=your_telegram_id

Run the bot
bash

    python main.py

🚀 Deployment on Render
Method 1: One-Click Deployment

https://render.com/images/deploy-to-render-button.svg
Method 2: Manual Deployment

    Fork this repository to your GitHub account

    Create a new Web Service on Render

        Connect your GitHub account

        Select your forked repository

        Configure build settings:

            Build Command: pip install -r requirements.txt

            Start Command: python main.py

    Set environment variables in Render dashboard:

        BOT_TOKEN: Your Telegram bot token

        ADMIN_ID: Your Telegram user ID

        DATABASE_URL: sqlite:///data/bot.db (for persistent storage)

    Deploy and your bot will be live!

⚙️ Configuration
Environment Variables
Variable	Description	Required
BOT_TOKEN	Telegram Bot Token from @BotFather	Yes
ADMIN_ID	Your Telegram User ID	Yes
WEBHOOK_URL	Webhook URL for production	No
DATABASE_URL	Database connection string	No
Customizing Settings

Group settings can be customized through:

    /settings command (admin only)

    Direct configuration in data/group_settings.json

    Environment variables

📋 Command Reference
Basic Commands
Command	Description	Access
/start	Start the bot	All
/help	Show help menu	All
/about	Bot information	All
/rules	Show group rules	All
/settings	Group settings panel	Admins
Moderation Commands
Command	Description	Access
/kick [reply]	Kick user	Admins
/ban [reply]	Ban user	Admins
/mute [reply] <time>	Mute user	Admins
/warn [reply] <reason>	Warn user	Admins
/purge	Delete multiple messages	Admins
Analytics Commands
Command	Description	Access
/stats	Group statistics	Admins
/userstats [reply]	User statistics	Admins
/topactive	Most active users	Admins
/activity <days>	Activity graph	Admins
/exportstats	Export statistics	Admins
Welcome Commands
Command	Description	Access
/setwelcome <text>	Set welcome message	Admins
/setgoodbye <text>	Set goodbye message	Admins
/welcome	Show welcome message	Admins
/goodbye	Show goodbye message	Admins
🏗️ Project Structure
text

group-meg-bot/
├── main.py              # Main application entry point
├── config.py            # Configuration settings
├── database.py          # Database operations
├── handlers.py          # Command handlers
├── moderation.py        # Moderation functions
├── utilities.py         # Utility functions
├── welcome.py           # Welcome/goodbye handlers
├── analytics.py         # Analytics and statistics
├── channel.py           # Channel management
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── render.yaml         # Render deployment config
└── README.md           # This file

🔧 Customization
Adding New Commands

    Create handler function in handlers.py

    Register command in CommandHandlers.get_handlers()

    Add to help menu in utilities.py

Adding New Language Support

    Add language responses in utilities.py

    Update language detection logic

    Add language option to settings

Modifying Moderation Rules

Edit the moderation settings in:

    moderation.py for core logic

    config.py for default settings

    Through /settings command

🐛 Troubleshooting
Common Issues

    Bot doesn't respond

        Check BOT_TOKEN environment variable

        Verify webhook configuration

    Database errors

        Check file permissions for data directory

        Verify database path

    Import errors

        Ensure all dependencies are installed

        Check Python version compatibility

Getting Help

    Check the Render logs for errors

    Verify environment variables are set correctly

    Ensure your bot has admin privileges in groups

📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
👥 Development Team

    Developer: Latiful Hassan Zihan 🇵🇸

    Username: @alwayszihan

    Nationality: Bangladeshi 🇧🇩

🤝 Contributing

We welcome contributions! Please feel free to submit pull requests, open issues, or suggest new features.

    Fork the project

    Create your feature branch (git checkout -b feature/AmazingFeature)

    Commit your changes (git commit -m 'Add some AmazingFeature')

    Push to the branch (git push origin feature/AmazingFeature)

    Open a Pull Request

📞 Support

For support and questions:

    Open an issue on GitHub

    Contact the developer: @alwayszihan

    Join our support group: [Coming Soon]

🙏 Acknowledgments

    python-telegram-bot library

    Render for hosting

    Telegram Bot API

Note: This bot is designed for group management and requires appropriate permissions to function correctly. Make sure to grant the bot admin privileges in your groups for full functionality.

Happy Managing! 🎉
