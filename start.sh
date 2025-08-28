#!/bin/bash

# Check if required environment variables are set
if [ -z "$BOT_TOKEN" ]; then
    echo "ERROR: BOT_TOKEN environment variable is required"
    exit 1
fi

# Generate a secret token if not provided
if [ -z "$SECRET_TOKEN" ]; then
    echo "WARNING: SECRET_TOKEN not set, generating one..."
    export SECRET_TOKEN=$(python -c "import secrets; import string; alphabet = string.ascii_letters + string.digits + '_-'; print(''.join(secrets.choice(alphabet) for _ in range(32)))")
fi

# Create temporary directory for files
mkdir -p /tmp 2>/dev/null || true

# Start the bot
echo "Starting GROUP MEG 🇵🇸 Bot..."
echo "Webhook URL: $WEBHOOK_URL"
echo "Using secret token: $SECRET_TOKEN"
exec python main.py
