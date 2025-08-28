#!/bin/bash

# Check if required environment variables are set
if [ -z "$BOT_TOKEN" ]; then
    echo "ERROR: BOT_TOKEN environment variable is required"
    exit 1
fi

# Create necessary directories (if using persistent storage)
mkdir -p /tmp/data 2>/dev/null || true

# Start the bot
exec python main.py
