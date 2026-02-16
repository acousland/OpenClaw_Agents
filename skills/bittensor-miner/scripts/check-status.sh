#!/bin/bash
# Check Bittensor miner status

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔍 Bittensor Miner Status"
echo "=========================="
echo ""

# Check if PID file exists and daemon is running
if [ -f "$SKILL_DIR/state/miner.pid" ]; then
    PID=$(cat "$SKILL_DIR/state/miner.pid")
    if kill -0 "$PID" 2>/dev/null; then
        echo "✅ Daemon Status: RUNNING (PID: $PID)"
    else
        echo "❌ Daemon Status: NOT RUNNING (PID file exists but process not found)"
    fi
else
    echo "❌ Daemon Status: NOT RUNNING (no PID file)"
fi

echo ""

# Check if socket is accessible
if [ -S "/tmp/openclawd-bittensor.sock" ]; then
    echo "✅ IPC Socket: ACCESSIBLE (/tmp/openclawd-bittensor.sock)"
else
    echo "⚠️  IPC Socket: NOT FOUND"
fi

echo ""

# Show recent logs
if [ -f "$SKILL_DIR/logs/miner.log" ]; then
    echo "📋 Recent Log Entries:"
    echo "---"
    tail -10 "$SKILL_DIR/logs/miner.log"
else
    echo "📋 No log file yet"
fi

echo ""

# Check recent performance metrics
if [ -f "$SKILL_DIR/state/performance-metrics.json" ]; then
    echo "📊 Performance Metrics:"
    echo "---"
    if command -v jq &> /dev/null; then
        jq '.performance_24h' "$SKILL_DIR/state/performance-metrics.json"
    else
        cat "$SKILL_DIR/state/performance-metrics.json" | head -20
    fi
else
    echo "📊 No metrics yet"
fi

echo ""
echo "=========================="
