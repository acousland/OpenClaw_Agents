#!/bin/bash
# Start the Bittensor miner daemon

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SKILL_DIR/venv"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

echo "🚀 Starting Bittensor Miner..."
echo ""

# Check if already running
if [ -f "$SKILL_DIR/state/miner.pid" ]; then
    PID=$(cat "$SKILL_DIR/state/miner.pid")
    if kill -0 "$PID" 2>/dev/null; then
        echo "⚠️  Miner already running (PID: $PID)"
        exit 1
    else
        echo "🧹 Cleaning up stale PID file..."
        rm -f "$SKILL_DIR/state/miner.pid"
    fi
fi

# Check Bittensor wallet
if ! btcli wallet list | grep -q "openclawd-miner"; then
    echo "❌ Bittensor wallet 'openclawd-miner' not found"
    echo "   Create with: btcli wallet new_coldkey --wallet.name openclawd-miner"
    exit 1
fi

echo "✅ Wallet found: openclawd-miner"
echo ""

# Start daemon in background
echo "Starting daemon process..."
cd "$SKILL_DIR"
python3 -u src/miner_daemon.py > logs/miner.log 2>&1 &
DAEMON_PID=$!

# Save PID
echo $DAEMON_PID > state/miner.pid

# Wait a moment for daemon to start
sleep 2

# Check if daemon is running
if kill -0 $DAEMON_PID 2>/dev/null; then
    echo "✅ Daemon started (PID: $DAEMON_PID)"
    echo ""
    echo "Check status with: bash scripts/check-status.sh"
    echo "View logs with:    tail -f logs/miner.log"
else
    echo "❌ Failed to start daemon"
    echo "Check logs: tail logs/miner.log"
    exit 1
fi
