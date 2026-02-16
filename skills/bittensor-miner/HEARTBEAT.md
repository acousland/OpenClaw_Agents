# Bittensor Miner Heartbeat Checks

Periodic monitoring tasks to keep the miner healthy and optimized.

## Frequency: Every 2-4 Hours

When heartbeat triggers, if 2+ hours since last Bittensor check:

### 1. Daemon Health Check

```bash
bash skills/bittensor-miner/scripts/check-status.sh
```

**What to look for:**
- ✅ Daemon running and connected to subnet
- ✅ IPC socket responding
- ⚠️ Daemon crashed or not connected → restart: `bash scripts/start-miner.sh`

### 2. Recent Validator Scores (Last 10 Tasks)

```bash
# Check task history
tail -10 state/task-history.jsonl | jq '.validator_score'
```

**What to track:**
- Average score (target: >0.7)
- Score trend (increasing/decreasing/stable)
- ⚠️ Score drops >20% in last 10 tasks → review prompt strategy in subnet-profiles.json

### 3. Token Budget Status

```bash
# Check remaining budget
jq '.budgets | to_entries[] | {api: .key, used_pct: (.value.used_this_month / .value.monthly_allowance * 100)}' config/token-budgets.json
```

**What to check:**
- OpenAI: remaining budget
- Claude: remaining budget
- Gemini: remaining budget
- ⚠️ Any API >80% used → Review last week's token spend, may need to adjust budgets
- 🚨 Any API >95% used → Immediately reduce participation or stop mining

### 4. Performance Trends

```bash
# View aggregated metrics from last 7 days
jq '.performance_7day' state/performance-metrics.json
```

**What to analyze:**
- Average validator score (trend up/down?)
- Task success rate (% of tasks scoring >0.6)
- Token ROI (TAO earned per 1K tokens spent)
- Best performing LLM
- Best performing prompt strategy

**Actions:**
- ✅ Scores improving → continue current strategy
- ⚠️ Scores flat → A/B test new prompt strategy
- 🚨 Scores declining >20% → review and revert recent changes

### 5. Update Heartbeat State

```bash
# Record last check time
jq '.lastBittensorCheck = now' memory/heartbeat-state.json > /tmp/hb.json && mv /tmp/hb.json memory/heartbeat-state.json
```

## Extended Checks: Every Day at 9 AM

### Daily Performance Report

```bash
# Run performance analysis
python3 src/performance_tracker.py --analyze --days 1
```

**Generate report:**
- Task count: X tasks processed
- Average score: X.XX
- Token spend: X tokens
- ROI: X TAO per 1K tokens
- Best strategy: [strategy_name]
- Recommendation: [action]

### Token Budget Reset (Monthly)

On first day of month:

```bash
# Reset monthly counters
jq '.budgets |= map_values(.used_this_month = 0 | .last_reset = now)' config/token-budgets.json
```

## Weekly Review: Sundays at 10 AM

### Full Performance Analysis

```bash
python3 src/performance_tracker.py --analyze --days 7 --detailed
```

**Review:**
1. Week-over-week score trend
2. Subnet profitability (ROI per subnet)
3. LLM performance comparison
4. Prompt strategy effectiveness

### Strategy Optimization

Check if any changes needed:

1. **Update prompt strategies** if clear winner found
2. **Adjust LLM preferences** based on subnet performance
3. **Rebalance token budgets** if one LLM consistently better
4. **Consider new subnets** if current ROI low

### Clean Up Logs

```bash
# Archive week-old logs
find logs -name "*.log.*" -mtime +7 -delete
```

## Alert Conditions

Notify via Telegram immediately if:

```
🚨 CRITICAL (Immediate action needed):
  - Daemon crashed or not responding
  - Wallet connection error
  - Score drop >50% in last 10 tasks
  - Token budget >95% used

⚠️ WARNING (Review within 24h):
  - Score trend declining >20% over 7 days
  - Token budget >80% used
  - Task success rate <50%
  - IPC communication errors
```

## Dashboard Metrics to Monitor

Keep these KPIs in view:

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Validator Score Avg | >0.7 | <0.5 |
| Task Success Rate | >70% | <50% |
| Token ROI | >0.001 TAO/1K tokens | <0.0005 |
| Daemon Uptime | >99% | <95% |
| Budget Usage | 60-80% monthly | >90% |

## Automation Notes

The heartbeat system will:
- ✅ Run these checks automatically every 2-4 hours
- ✅ Generate daily summary at 9 AM
- ✅ Generate weekly report on Sundays at 10 AM
- ✅ Send Telegram alerts for critical issues
- ✅ Update memory/heartbeat-state.json with timestamps

You should manually review:
- Daily performance report (skim key metrics)
- Weekly deep analysis (identify trends, make adjustments)
- Monthly profitability (decide whether to continue/expand)

## Example Heartbeat Response

```
🤖 Bittensor Miner Status (2024-01-15 14:30 UTC)

✅ DAEMON: Running, 847 tasks processed today
📊 SCORES: Average 0.73 (↑ +2.1% from yesterday)
💰 BUDGET: OpenAI 45% | Claude 32% | Gemini 18% (all healthy)
🎯 ROI: 0.0012 TAO per 1K tokens (↑ profitable)
🏆 Best Strategy: structured_reasoning on subnet 1

No action needed. Mining operating normally.
```

---

For detailed performance analysis, see state/performance-metrics.json.
For troubleshooting, check logs/miner.log.
