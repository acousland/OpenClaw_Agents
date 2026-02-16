# Configuration Guide - Bittensor Miner

## Phase 0: Foundation Setup

### 1. Install Bittensor SDK

```bash
# Create virtual environment (optional but recommended)
python3 -m venv /home/acousland/.openclaw/workspace-patrick/skills/bittensor-miner/venv
source /home/acousland/.openclaw/workspace-patrick/skills/bittensor-miner/venv/bin/activate

# Install Bittensor and dependencies
pip install bittensor latinum-wallet-mcp aiohttp cryptography
```

### 2. Create Bittensor Wallet

Generate a new wallet for mining:

```bash
# Create coldkey (stores your private key offline, use for staking)
btcli wallet new_coldkey --wallet.name openclawd-miner

# Generate hotkey (your identity on-chain, used for mining)
btcli wallet new_hotkey --wallet.name openclawd-miner --wallet.hotkey default

# View wallet addresses
btcli wallet overview --wallet.name openclawd-miner
```

**Save these addresses safely.** You'll fund the coldkey from an exchange.

### 3. Acquire TAO and Stake to Hotkey

**Manual action required:**

1. **Get TAO from exchange:**
   - Buy TAO on Binance, Kraken, or other exchange
   - Minimum recommended: 0.1 TAO (covers staking + buffer)
   - Withdrawal address: The coldkey address from `wallet overview`

2. **Transfer to coldkey wallet:**
   ```bash
   # Monitor wallet balance
   btcli wallet balance --wallet.name openclawd-miner
   ```

3. **Stake TAO to hotkey:**
   ```bash
   # Register to target subnet (subnet 1 for testing)
   btcli subnet register --wallet.name openclawd-miner --subnet.id 1 --amount 0.01

   # Verify registration
   btcli subnet validate --wallet.name openclawd-miner
   ```

### 4. Install and Configure Latinum Wallet MCP

The latinum-wallet-mcp handles Solana wallet operations (TAO runs on Solana):

```bash
# Already installed with pip above
pip install latinum-wallet-mcp

# Verify installation
latinum-wallet-mcp --help
```

The wallet manager will launch this automatically. No additional config needed unless you're on a non-standard Solana cluster.

### 5. Secure LLM API Keys

Create encrypted credential store:

```bash
# Copy template (OPTIONAL - can use environment variables)
cp config/llm-credentials.json.example config/llm-credentials.json

# Edit with your API keys (if using this method)
# Keys should be available via:
#   - OpenAI_API_KEY environment variable
#   - ANTHROPIC_API_KEY environment variable
#   - GOOGLE_API_KEY environment variable
# Or hardcoded in task_handler.py (less secure)
```

**Recommended:** Use environment variables or OpenClawd's existing auth profiles.

### 6. Configuration Files

#### miner-config.json

Core daemon configuration:

```json
{
  "bittensor": {
    "wallet_name": "openclawd-miner",
    "hotkey": "default",
    "subnet_id": 1,
    "network": "finney",
    "timeout": 30
  },
  "daemon": {
    "ipc_method": "unix_socket",
    "socket_path": "/tmp/openclawd-bittensor.sock",
    "max_concurrent_tasks": 3,
    "task_timeout_seconds": 60,
    "log_level": "INFO"
  },
  "wallet_mcp": {
    "enabled": true,
    "command": "latinum-wallet-mcp",
    "network": "mainnet"
  }
}
```

**Key settings:**
- `subnet_id`: Which Bittensor subnet to mine (1 = Text Prompting, 19 = Nineteen, etc.)
- `network`: "finney" (testnet) or "mainnet" (production)
- `socket_path`: Unix socket for IPC (must match what task_handler expects)
- `max_concurrent_tasks`: How many tasks to process simultaneously

#### subnet-profiles.json

Per-subnet mining strategies:

```json
{
  "subnets": {
    "1": {
      "name": "Text Prompting",
      "enabled": true,
      "preferred_llm": "openai-gpt4",
      "prompt_strategy": "structured_reasoning",
      "min_confidence_threshold": 0.7,
      "max_tokens_per_task": 1000,
      "participation_rate": 1.0,
      "task_types_to_handle": ["generation", "evaluation", "ranking"]
    },
    "19": {
      "name": "Nineteen Inference",
      "enabled": false,
      "preferred_llm": "claude-sonnet",
      "prompt_strategy": "concise_generation",
      "min_confidence_threshold": 0.6,
      "max_tokens_per_task": 500,
      "participation_rate": 0.8,
      "task_types_to_handle": ["generation", "evaluation"]
    }
  },
  "default_subnet": "1"
}
```

**How to add a new subnet:**
1. Find subnet ID on [Bittensor Explorer](https://explorer.bittensor.com/)
2. Register your hotkey to that subnet
3. Add entry to `subnets` object above
4. Set `enabled: true` when ready to mine
5. Configure `prompt_strategy` based on validator behavior

**Prompt strategies:**
- `structured_reasoning` - Use chain-of-thought (good for evaluation)
- `concise_generation` - Minimal verbosity (good for speed-focused subnets)
- `calibrated_uncertainty` - Express confidence levels (good for scoring)

#### token-budgets.json

LLM API allowance tracking:

```json
{
  "budgets": {
    "openai-gpt4": {
      "monthly_allowance": 1000000,
      "used_this_month": 0,
      "daily_limit": 50000,
      "hard_limit": true,
      "cost_per_1k_tokens": 0.03
    },
    "claude-sonnet": {
      "monthly_allowance": 800000,
      "used_this_month": 0,
      "daily_limit": 40000,
      "hard_limit": true,
      "cost_per_1k_tokens": 0.003
    },
    "gemini-pro": {
      "monthly_allowance": 2000000,
      "used_this_month": 0,
      "daily_limit": 80000,
      "hard_limit": true,
      "cost_per_1k_tokens": 0.0
    }
  },
  "allocation_strategy": "roi_weighted",
  "min_budget_threshold_for_task_percent": 0.1,
  "last_reset": "2024-01-01"
}
```

**Update monthly:**
- Reset `used_this_month` on first of month
- Verify actual allowances from billing dashboards
- Adjust `daily_limit` if needed based on actual usage

**How it works:**
- Task router checks remaining budget before each LLM call
- Refuses tasks if remaining budget < 10% of monthly allowance
- Tracks every API call and updates usage counters
- performance_tracker.py analyzes ROI per LLM/subnet

### 7. Run Setup Script

```bash
bash scripts/setup.sh
```

This will:
- Verify directory structure
- Create required directories if missing
- Generate default config files if not present
- Install Python dependencies
- Run basic connectivity tests

## Phase 1: Starting the Miner

### Verify Everything is Ready

```bash
# Check wallet balance
btcli wallet balance --wallet.name openclawd-miner

# Verify hotkey registration
btcli subnet validate --wallet.name openclawd-miner

# Check Bittensor network connectivity
btcli subnet list --wallet.name openclawd-miner
```

### Start the Miner

```bash
bash scripts/start-miner.sh
```

This will:
1. Activate Python virtual environment
2. Start miner_daemon.py in background
3. Initialize Unix socket at configured path
4. Begin listening for validator tasks
5. Log to logs/miner.log

### Monitor Initial Operation

```bash
# Check daemon status
bash scripts/check-status.sh

# Watch logs in real-time
tail -f logs/miner.log

# Check for received tasks
grep "task_received" logs/miner.log | tail -20
```

### Initial Testing (Testnet)

For first run, use Bittensor testnet (not mainnet):

1. **Switch to testnet in miner-config.json:**
   ```json
   "network": "finney"
   ```

2. **Register to testnet subnet 1:**
   ```bash
   btcli subnet register --wallet.name openclawd-miner --subnet.id 1 --network finney
   ```

3. **Start miner and monitor:**
   - Should see task reception within 5-10 minutes if validators active
   - Initial responses will be stubs (echo tasks)
   - Validator scores will be recorded

4. **Verify responses are being submitted:**
   ```bash
   grep "response_submitted" logs/miner.log
   ```

## Phase 2: Configuring LLM Integration

Once miner is receiving tasks, integrate LLM APIs:

### Update subnet-profiles.json

Change prompt strategy from "echo" to "structured_reasoning":

```json
"prompt_strategy": "structured_reasoning"
```

### Verify LLM API Keys

Ensure OpenAI, Anthropic, and Google APIs are accessible:

```bash
# Test OpenAI
python3 -c "import openai; print('OpenAI OK')"

# Test Anthropic
python3 -c "import anthropic; print('Anthropic OK')"

# Test Google
python3 -c "import google.generativeai; print('Google OK')"
```

### Set Token Budgets

Update token-budgets.json with your actual monthly allowances:

```bash
# OpenAI: Check billing at https://platform.openai.com/account/billing/overview
# Anthropic: Check at https://console.anthropic.com/
# Google: Check at https://ai.google.dev/
```

### Monitor First LLM Calls

Once configured, watch logs for API calls:

```bash
# Watch for successful LLM API calls
tail -f logs/miner.log | grep "llm_api_call\|tokens_used\|validator_score"
```

**Expected improvements:**
- Validator scores should increase from stub responses
- Task acceptance rate should stabilize around 70-80%
- Token spend should be tracked in token-budgets.json

## Troubleshooting

### Daemon Won't Start

```bash
# Check Bittensor installation
python3 -c "import bittensor; print(bittensor.__version__)"

# Check wallet exists
btcli wallet list

# Check for socket conflicts
lsof -i :8000  # Bittensor default port
```

**Solution:** Reinstall Bittensor or check firewall rules.

### No Tasks Received

```bash
# Verify hotkey has stake
btcli subnet metagraph --subnet.id 1 | grep your-hotkey

# Check validator count on subnet
btcli subnet list --subnet.id 1
```

**Solution:** May need more stake (minimum varies by subnet) or validators not online.

### Low Validator Scores

This is expected initially. Scores improve as you:
1. Implement proper LLM routing
2. A/B test prompt strategies
3. Adapt based on feedback (performance_tracker)

Monitor performance-metrics.json for trends.

### API Rate Limiting

If seeing rate limit errors:
- Lower `max_tokens_per_task` in subnet-profiles.json
- Reduce `max_concurrent_tasks` in miner-config.json
- Increase delays in task_handler.py

### Token Budget Exceeded

If using too many tokens:
- Lower token budgets in token-budgets.json
- Reduce `participation_rate` in subnet-profiles.json
- Switch to more efficient LLM (Gemini is free tier available)

## Moving to Mainnet

When ready for production:

1. **Switch network in miner-config.json:**
   ```json
   "network": "mainnet"
   ```

2. **Register to mainnet subnet:**
   ```bash
   btcli subnet register --wallet.name openclawd-miner --subnet.id 1 --network mainnet
   ```

3. **Verify configuration:**
   - Check token budgets are realistic
   - Verify prompt strategies are tested
   - Confirm logging and monitoring are working

4. **Start with reduced participation:**
   ```json
   "participation_rate": 0.5
   ```
   Increase gradually as confidence improves.

5. **Monitor closely:**
   - Daily performance reviews
   - Weekly ROI analysis
   - Adjust strategy based on empirical results

---

For troubleshooting and support, check logs/miner.log and state/performance-metrics.json.
