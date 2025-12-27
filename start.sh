#!/bin/bash
# irProLink bot start script

cd "$(dirname "$0")"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the bot
python3 main.py
