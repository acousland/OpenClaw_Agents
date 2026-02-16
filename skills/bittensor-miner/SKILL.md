# Bittensor Miner Skill

OpenClawd's Bittensor miner participation system. Acts as a judgment/inference-specialized miner in text-based Bittensor subnets, using existing proprietary LLM subscriptions (OpenAI, Anthropic Claude, Google Gemini) to compete on quality rather than throughput.

## Quick Start

```bash
# Phase 0: Setup (first time only)
bash skills/bittensor-miner/scripts/setup.sh

# Phase 1: Start mining
bash skills/bittensor-miner/scripts/start-miner.sh

# Check status
bash skills/bittensor-miner/scripts/check-status.sh

# Stop mining
bash skills/bittensor-miner/scripts/stop-miner.sh
```

## Architecture

The miner consists of five core components:

### 1. **miner_daemon.py** - Bittensor Client
Persistent background process that:
- Registers hotkey to target subnet
- Listens for `forward_pass` tasks from validators
- Routes tasks to task_handler via Unix socket IPC
- Submits responses back to validators
- Handles reconnection and error recovery

### 2. **llm_router.py** - Intelligence Layer
Decision engine that implements:
- **Selective participation:** Should we respond to this task?
- **LLM selection:** Which model (OpenAI/Claude/Gemini)?
- **Token budget allocation:** How many tokens can we spend?
- **Prompt strategy:** Which formatting wins validator approval?

### 3. **task_handler.py** - Execution Bridge
Connects Bittensor tasks to OpenClawd's LLM APIs:
- Receives tasks from miner_daemon
- Invokes llm_router for decision-making
- Executes LLM inference calls
- Formats responses per subnet requirements
- Returns responses to daemon

### 4. **performance_tracker.py** - Learning System
Implements feedback loop:
- Records validator scores for each response
- Analyzes task_type × LLM × prompt_strategy correlations
- Identifies high-performing configurations
- Automatically adapts strategy based on empirical results

### 5. **wallet_manager.py** - TAO Management
Manages wallet operations via latinum-wallet-mcp:
- Checks balance and earnings
- Signs transactions for staking
- Monitors TAO emissions

## Configuration

See `CONFIG.md` for setup instructions. Key config files:

- **miner-config.json** - Bittensor connection details and daemon settings
- **subnet-profiles.json** - Per-subnet strategies (preferred LLM, prompts, budgets)
- **token-budgets.json** - LLM API allowances and usage tracking
- **llm-credentials.json** - Encrypted API keys (encrypted locally)

## Monitoring

Integrated with OpenClawd's heartbeat system. See `HEARTBEAT.md` for periodic checks.

Key alerts:
- **Daemon status** - Is the miner running?
- **Validator scores** - Are we getting rewarded?
- **Token budget** - Are we overspending?
- **Performance trends** - Is ROI improving?

## Notifications

See `MESSAGING.md` for alert patterns. Critical issues trigger immediate Telegram notifications.

## Data Flow

```
Validator Task
    ↓
miner_daemon (listens on subnet)
    ↓ IPC (Unix socket)
task_handler
    ├─ llm_router.should_respond()?
    └─ YES: select_llm() → allocate_tokens() → apply_prompt()
    ↓
LLM API calls (OpenAI/Claude/Gemini)
    ↓
Format response per subnet format
    ↓ IPC (return to daemon)
miner_daemon (submit to validators)
    ↓
Validator scores response
    ↓
performance_tracker (record result & adapt)
```

## Performance Targets

- **Validator Score Average:** >0.7 (scale 0-1)
- **Task Success Rate:** >70% of accepted tasks score >0.6
- **Token ROI:** >0.001 TAO per 1K tokens
- **Uptime:** >99% daemon availability

## Development Notes

- Keep it simple initially: start with one subnet, one LLM
- All intelligence in llm_router.py and performance_tracker.py
- Prompt quality matters more than model choice
- Token budget is hard constraint (better to miss tasks than burn allowances)
- Update strategy gradually based on empirical data

## Troubleshooting

**Daemon won't start:**
- Check Bittensor wallet exists: `btcli wallet list --wallet.name openclawd-miner`
- Check hotkey registered to subnet: `btcli subnet validate --wallet.name openclawd-miner`
- Check logs/miner.log for errors

**No tasks received:**
- Verify subnet selection in miner-config.json
- Confirm hotkey has positive stake in target subnet
- Check validator count (need active validators to receive tasks)

**Low validator scores:**
- Analyze performance-metrics.json to identify weak LLM/prompt combinations
- A/B test prompt strategies in subnet-profiles.json
- Check if task_type classification is accurate

**Token budget warnings:**
- Review recent LLM API calls in token-budgets.json
- Lower max_tokens_per_task in subnet-profiles.json
- Consider reducing task participation rate if ROI is negative

## Future Enhancements

- Multi-subnet portfolio management
- ML-based task classification
- Advanced prompt A/B testing
- Automated staking/unstaking
- Validator behavior modeling

---

For detailed configuration and setup, see CONFIG.md.
For performance tracking and optimization, see performance-metrics.json and performance_tracker.py.
