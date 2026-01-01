#!/bin/bash
# irProLink bot stop script - Version 6.2.0
# Compatible with Docker, cPanel, shared hosting, and systemd

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

# Check if Docker is available and containers are running
DOCKER_COMPOSE_FILE="docker-compose.yml"
DOCKER_AVAILABLE=false
DOCKER_RUNNING=false
DOCKER_COMPOSE_CMD=""

# Check for docker compose command (newer versions use 'docker compose')
if command -v docker &> /dev/null; then
    DOCKER_AVAILABLE=true
    # Try docker compose (new format)
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
    # Try docker-compose (old format)
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    fi
    
    # Check if containers are running
    if [ -n "$DOCKER_COMPOSE_CMD" ] && [ -f "$DOCKER_COMPOSE_FILE" ]; then
        if $DOCKER_COMPOSE_CMD ps 2>/dev/null | grep -q "irprolink-bot"; then
            DOCKER_RUNNING=true
        fi
    fi
fi

# Stop Docker containers if running
if [ "$DOCKER_RUNNING" = true ] && [ -n "$DOCKER_COMPOSE_CMD" ]; then
    log_message "🛑 Stopping Docker containers..."
    
    # Stop containers gracefully
    $DOCKER_COMPOSE_CMD down --timeout 30
    
    if [ $? -eq 0 ]; then
        log_message "✅ Docker containers stopped successfully"
    else
        log_message "⚠️ Docker containers may not have stopped cleanly"
        log_message "Trying force stop..."
        $DOCKER_COMPOSE_CMD down --timeout 10 --remove-orphans
    fi
    
    # Check if containers are still running
    if $DOCKER_COMPOSE_CMD ps 2>/dev/null | grep -q "Up"; then
        log_message "❌ Some containers are still running"
        log_message "Forcing removal..."
        $DOCKER_COMPOSE_CMD down --remove-orphans --volumes --timeout 5
    fi
    
    # Clean up Docker resources
    log_message "🧹 Cleaning up Docker resources..."
    docker system prune -f --filter "until=24h" 2>/dev/null || true
    
    log_message "✅ Docker cleanup completed"
    exit 0
fi

# If Docker is available but not running, check if we should stop regular processes
if [ "$DOCKER_AVAILABLE" = true ] && [ "$DOCKER_RUNNING" = false ]; then
    log_message "ℹ️ Docker is available but no containers are running"
    log_message "Checking for regular bot processes..."
fi

# Check for systemd service
SYSTEMD_SERVICE="irprolink-bot.service"
if systemctl is-active --quiet "$SYSTEMD_SERVICE" 2>/dev/null; then
    log_message "🛑 Stopping systemd service: $SYSTEMD_SERVICE"
    sudo systemctl stop "$SYSTEMD_SERVICE"
    if [ $? -eq 0 ]; then
        log_message "✅ Systemd service stopped"
        log_message "Disabling auto-start..."
        sudo systemctl disable "$SYSTEMD_SERVICE" 2>/dev/null || true
    else
        log_message "⚠️ Failed to stop systemd service"
    fi
fi

# Find bot PID using multiple methods (for non-Docker deployments)
PID=""

# Method 1: Look for python3 main.py (including cPanel virtual environment)
PID1=$(ps aux 2>/dev/null | grep -E "[p]ython3.*main\.py|[p]ython.*main\.py" | awk '{print $2}')

# Method 2: Look for process in current directory (including cPanel path)
if command -v lsof &> /dev/null; then
    PID2=$(timeout 2 lsof -t -c python -a -d cwd -F p 2>/dev/null | grep '^p' | cut -c 2- || echo "")
else
    PID2=""
fi

# Method 3: Look for bot process by name (including cPanel specific)
if command -v pgrep &> /dev/null; then
    PID3=$(pgrep -f "main.py" 2>/dev/null || echo "")
else
    PID3=""
fi

# Method 4: Check for cPanel Python app processes (auto-detect)
CPANEL_VENV_PATH=""
# Try to detect cPanel virtualenv path
if [ -d "/home" ]; then
    # Look for virtualenv directories in /home/*/virtualenv/
    for user_dir in /home/*/; do
        if [ -d "${user_dir}virtualenv/prolink" ]; then
            CPANEL_VENV_PATH="${user_dir}virtualenv/prolink"
            break
        fi
    done
fi

if [ -n "$CPANEL_VENV_PATH" ]; then
    PID4=$(ps aux 2>/dev/null | grep -E "$CPANEL_VENV_PATH.*python.*main\.py" | grep -v grep | awk '{print $2}')
    if [ -n "$PID4" ]; then
        log_message "⚠️ Found cPanel Python app processes in $CPANEL_VENV_PATH"
    fi
else
    PID4=""
fi

# Combine and get unique PIDs
ALL_PIDS=$(echo "$PID1 $PID2 $PID3 $PID4" | tr ' ' '\n' | sort -u | grep -v '^$' | tr '\n' ' ')

if [ -z "$ALL_PIDS" ]; then
    log_message "✅ Bot is not running"
    
    # Clean up any remaining .pyc files and cache
    find . -name "*.pyc" -delete 2>/dev/null
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    find . -name ".coverage" -delete 2>/dev/null
    find . -name "*.log" -type f -mtime +7 -delete 2>/dev/null
    
    # Clean temp directory
    if [ -d "temp" ]; then
        find temp -type f -mtime +1 -delete 2>/dev/null
    fi
    
    log_message "🧹 Cleaned up Python cache and temporary files"
    exit 0
fi

log_message "Found bot PIDs: $ALL_PIDS"

# Stop each process
STOPPED_COUNT=0
FAILED_COUNT=0

for PID in $ALL_PIDS; do
    if [ -n "$PID" ] && ps -p "$PID" > /dev/null 2>&1; then
        log_message "Stopping process $PID..."
        
        # Get process details for logging
        PROCESS_INFO=$(ps -p "$PID" -o pid,user,cmd --no-headers 2>/dev/null || echo "Unknown process")
        log_message "Process details: $PROCESS_INFO"
        
        # Send SIGTERM first (graceful shutdown)
        kill -TERM "$PID" 2>/dev/null
        
        # Wait for process to terminate
        TERMINATED=false
        for i in {1..15}; do
            if ! ps -p "$PID" > /dev/null 2>&1; then
                log_message "✅ Process $PID stopped gracefully"
                STOPPED_COUNT=$((STOPPED_COUNT + 1))
                TERMINATED=true
                break
            fi
            sleep 1
        done
        
        # If still running, send SIGKILL
        if [ "$TERMINATED" = false ] && ps -p "$PID" > /dev/null 2>&1; then
            log_message "Process $PID not responding, forcing termination..."
            kill -KILL "$PID" 2>/dev/null
            sleep 2
            
            if ! ps -p "$PID" > /dev/null 2>&1; then
                log_message "✅ Process $PID forced to stop"
                STOPPED_COUNT=$((STOPPED_COUNT + 1))
            else
                log_message "❌ Failed to stop process $PID"
                FAILED_COUNT=$((FAILED_COUNT + 1))
            fi
        fi
    fi
done

# Clean up any remaining .pyc files and cache
find . -name "*.pyc" -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name ".coverage" -delete 2>/dev/null
find . -name "*.log" -type f -mtime +7 -delete 2>/dev/null

# Clean temp directory
if [ -d "temp" ]; then
    find temp -type f -mtime +1 -delete 2>/dev/null
fi

# Summary
log_message "=== Stop Summary ==="
log_message "Stopped processes: $STOPPED_COUNT"
log_message "Failed to stop: $FAILED_COUNT"

if [ $FAILED_COUNT -eq 0 ]; then
    log_message "✅ Bot stopped successfully"
else
    log_message "⚠️ Some processes may still be running"
    log_message "You may need to manually check and kill remaining processes"
fi

log_message "🧹 Cleaned up Python cache and temporary files"
log_message "=== Stop Script Finished ==="
