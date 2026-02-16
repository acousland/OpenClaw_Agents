#!/bin/bash
# Setup script for Bittensor Miner Skill
# This script initializes the environment and installs dependencies

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SKILL_DIR/venv"

echo "🚀 Bittensor Miner Skill Setup"
echo "=============================="
echo ""

# Check Python version
echo "1. Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment if not exists
echo ""
echo "2. Setting up virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# Install/upgrade pip
echo ""
echo "3. Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo "✅ pip upgraded"

# Install Python dependencies
echo ""
echo "4. Installing Python dependencies..."
pip install bittensor latinum-wallet-mcp aiohttp cryptography requests > /dev/null 2>&1
echo "✅ Dependencies installed"

# Create required directories
echo ""
echo "5. Creating directories..."
mkdir -p "$SKILL_DIR/state"
mkdir -p "$SKILL_DIR/logs"
mkdir -p "$SKILL_DIR/src/utils"
echo "✅ Directories created"

# Initialize state files if they don't exist
echo ""
echo "6. Initializing state files..."

if [ ! -f "$SKILL_DIR/state/miner-state.json" ]; then
    cat > "$SKILL_DIR/state/miner-state.json" << 'EOF'
{
  "status": "initialized",
  "daemon_pid": null,
  "socket_path": "/tmp/openclawd-bittensor.sock",
  "last_task_received": null,
  "tasks_processed": 0,
  "uptime_seconds": 0
}
EOF
    echo "✅ Created miner-state.json"
fi

if [ ! -f "$SKILL_DIR/state/task-history.jsonl" ]; then
    touch "$SKILL_DIR/state/task-history.jsonl"
    echo "✅ Created task-history.jsonl"
fi

if [ ! -f "$SKILL_DIR/state/performance-metrics.json" ]; then
    cat > "$SKILL_DIR/state/performance-metrics.json" << 'EOF'
{
  "performance_24h": {
    "tasks_completed": 0,
    "average_score": 0.0,
    "success_rate": 0.0,
    "token_spend": 0,
    "tao_earned": 0.0
  },
  "performance_7day": {
    "tasks_completed": 0,
    "average_score": 0.0,
    "success_rate": 0.0,
    "token_spend": 0,
    "tao_earned": 0.0,
    "best_strategy": null
  },
  "by_llm": {},
  "by_subnet": {},
  "last_updated": null
}
EOF
    echo "✅ Created performance-metrics.json"
fi

# Create __init__.py for src
echo ""
echo "7. Creating Python package files..."
touch "$SKILL_DIR/src/__init__.py"
touch "$SKILL_DIR/src/utils/__init__.py"
echo "✅ Package files created"

# Check for Bittensor wallet
echo ""
echo "8. Checking Bittensor wallet..."
if command -v btcli &> /dev/null; then
    if btcli wallet list | grep -q "openclawd-miner"; then
        echo "✅ Bittensor wallet 'openclawd-miner' found"
    else
        echo "⚠️  Bittensor wallet 'openclawd-miner' not found"
        echo "   To create: btcli wallet new_coldkey --wallet.name openclawd-miner"
        echo "   Then: btcli wallet new_hotkey --wallet.name openclawd-miner --wallet.hotkey default"
    fi
else
    echo "⚠️  btcli command not found. Bittensor may not be properly installed."
fi

# Summary
echo ""
echo "=============================="
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Create Bittensor wallet if not done:"
echo "   btcli wallet new_coldkey --wallet.name openclawd-miner"
echo "   btcli wallet new_hotkey --wallet.name openclawd-miner --wallet.hotkey default"
echo ""
echo "2. Acquire TAO and stake to hotkey"
echo "   See CONFIG.md for detailed instructions"
echo ""
echo "3. Start the miner:"
echo "   bash scripts/start-miner.sh"
echo ""
echo "4. Check status:"
echo "   bash scripts/check-status.sh"
echo ""
