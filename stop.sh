#!/bin/bash
# irProLink bot stop script - Version 6.1.0

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Log file
LOG_FILE="logs/bot.log"
mkdir -p logs

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "=== Stopping irProLink Bot ==="

# Find bot PID using multiple methods
PID=""

# Method 1: Look for python3 main.py
PID1=$(ps aux | grep -E "[p]ython3.*main\.py|[p]ython.*main\.py" | awk '{print $2}')

# Method 2: Look for process in current directory
PID2=$(lsof -t -c python -a -d cwd -F p | grep '^p' | cut -c 2-)

# Method 3: Look for bot process by name
PID3=$(pgrep -f "main.py")

# Combine and get unique PIDs
ALL_PIDS=$(echo "$PID1 $PID2 $PID3" | tr ' ' '\n' | sort -u | tr '\n' ' ')

if [ -z "$ALL_PIDS" ]; then
    log_message "✅ Bot is not running"
    exit 0
fi

log_message "Found bot PIDs: $ALL_PIDS"

# Stop each process
for PID in $ALL_PIDS; do
    if [ -n "$PID" ] && ps -p "$PID" > /dev/null 2>&1; then
        log_message "Stopping process $PID..."
        
        # Send SIGTERM first (graceful shutdown)
        kill -TERM "$PID" 2>/dev/null
        
        # Wait for process to terminate
        for i in {1..10}; do
            if ! ps -p "$PID" > /dev/null 2>&1; then
                log_message "✅ Process $PID stopped gracefully"
                break
            fi
            sleep 1
        done
        
        # If still running, send SIGKILL
        if ps -p "$PID" > /dev/null 2>&1; then
            log_message "Process $PID not responding, forcing termination..."
            kill -KILL "$PID" 2>/dev/null
            sleep 1
            
            if ! ps -p "$PID" > /dev/null 2>&1; then
                log_message "✅ Process $PID forced to stop"
            else
                log_message "❌ Failed to stop process $PID"
            fi
        fi
    fi
done

# Clean up any remaining .pyc files
find . -name "*.pyc" -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

log_message "✅ Bot stopped successfully"
log_message "=== Stop Script Finished ==="
