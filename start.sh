#!/bin/bash

echo "🚀 Starting GROUP MEG 🇵🇸 Bot Deployment..."
echo "==========================================="

# Check if required environment variables are set
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ ERROR: BOT_TOKEN environment variable is required"
    echo "   Get it from @BotFather on Telegram"
    exit 1
fi

if [ -z "$ADMIN_ID" ]; then
    echo "⚠️  WARNING: ADMIN_ID environment variable not set"
    echo "   Get your ID from @userinfobot on Telegram"
fi

# Generate secret token if not provided
if [ -z "$SECRET_TOKEN" ]; then
    echo "⚠️  WARNING: SECRET_TOKEN not set, generating one..."
    export SECRET_TOKEN=$(python -c "import secrets; import string; alphabet = string.ascii_letters + string.digits + '_-'; print(''.join(secrets.choice(alphabet) for _ in range(32)))")
    echo "🔐 Generated SECRET_TOKEN: $SECRET_TOKEN"
fi

# Set default values if not provided
export USE_WEBHOOK=${USE_WEBHOOK:-false}
export PORT=${PORT:-10000}
export DATABASE_URL=${DATABASE_URL:-sqlite:///:memory:}

# Display configuration
echo "📋 Configuration:"
echo "   🤖 BOT_TOKEN: ✅ Set"
echo "   👑 ADMIN_ID: ${ADMIN_ID:-❌ Not set}"
echo "   🔐 SECRET_TOKEN: $SECRET_TOKEN"
echo "   🌐 USE_WEBHOOK: $USE_WEBHOOK"
echo "   🚪 PORT: $PORT"
echo "   💾 DATABASE_URL: $DATABASE_URL"

# Create temporary directory for files
mkdir -p /tmp 2>/dev/null || true
echo "📁 Created temporary directory: /tmp"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Start the bot
echo "🎯 Starting GROUP MEG 🇵🇸 Bot..."
exec python main.py
