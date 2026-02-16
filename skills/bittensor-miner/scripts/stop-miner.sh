#!/bin/bash
# Stop the Bittensor miner daemon

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "🛑 Stopping Bittensor Miner..."
echo ""

if [ ! -f "$SKILL_DIR/state/miner.pid" ]; then
    echo "⚠️  No PID file found. Miner may not be running."
    exit 0
fi

PID=$(cat "$SKILL_DIR/state/miner.pid")

if kill -0 "$PID" 2>/dev/null; then
    echo "Terminating daemon (PID: $PID)..."
    kill -TERM "$PID"

    # Wait up to 10 seconds for graceful shutdown
    TIMEOUT=10
    while [ $TIMEOUT -gt 0 ] && kill -0 "$PID" 2>/dev/null; do
        sleep 1
        TIMEOUT=$((TIMEOUT - 1))
    done

    # Force kill if still running
    if kill -0 "$PID" 2>/dev/null; then
        echo "Force killing daemon..."
        kill -9 "$PID"
    fi

    rm -f "$SKILL_DIR/state/miner.pid"

    # Clean up socket
    if [ -f "/tmp/openclawd-bittensor.sock" ]; then
        rm -f "/tmp/openclawd-bittensor.sock"
    fi

    echo "✅ Daemon stopped"
else
    echo "⚠️  Daemon not running (PID: $PID not found)"
    rm -f "$SKILL_DIR/state/miner.pid"
fi

echo ""
