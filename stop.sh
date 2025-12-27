#!/bin/bash
# irProLink bot stop script

# Find bot PID
PID=$(ps aux | grep "python3.*main.py" | grep -v grep | awk '{print $2}')

if [ -z "$PID" ]; then
    echo "Bot is not running"
else
    kill $PID
    echo "Bot stopped (PID: $PID)"
fi
