# Notification Patterns - Bittensor Miner

How and when the miner sends notifications to the user.

## Telegram Channel Binding

Uses Patrick's main Telegram channel for all notifications. Messages are sent with emoji context and brief summaries.

## Notification Types

### 🟢 Operational (Status Updates)

**Daily Summary** (9 AM UTC)
```
🤖 Bittensor Miner Daily Report (2024-01-15)

📊 Tasks: 847 completed, avg score 0.73
💰 Token spend: 45K (8% of daily limit)
🎯 ROI: 0.0012 TAO per 1K tokens (profitable)
🏆 Best strategy: structured_reasoning (78% success rate)

✅ All systems normal. Continue current strategy.
```

**Weekly Summary** (Sunday 10 AM UTC)
```
📈 Bittensor Miner Weekly Report (Jan 8-14)

📊 Tasks: 5,847 completed
💰 Tokens spent: 285K (42% of weekly allowance)
💵 TAO earned: 7.04 TAO (↑ +12% vs last week)
🎯 ROI: 0.00124 TAO per 1K tokens

Top strategy: structured_reasoning (subnet 1)
Recommendation: Increase participation rate from 0.8 → 0.9

Next week focus: Test new prompt variant on subnet 19.
```

### 🟡 Warnings (Action Recommended)

**Token Budget Warning**
```
⚠️ Token Budget Alert

OpenAI: 82% of monthly allowance used
Daily burn rate: 15K tokens/day at current rate

Action: Either reduce max_tokens_per_task from 1000 → 800,
or lower participation_rate from 1.0 → 0.8

Current trajectory: Budget exhausted in 5 days
```

**Score Trend Warning**
```
⚠️ Validator Score Declining

Last 7 days: avg score 0.73 → 0.58 (↓ 20%)
Last 24h: 10/20 tasks scoring <0.5

Likely causes: Prompt strategy mismatch or validator preference shift

Recommend: A/B test new prompt strategy in subnet-profiles.json
```

**Performance Degradation**
```
⚠️ ROI Declining

Last week: 0.00124 TAO per 1K tokens
This week: 0.00087 TAO per 1K tokens (↓ 30%)

Analysis: Increasing token spend without proportional score improvement

Action: Review task selection logic - may be accepting low-confidence tasks
```

### 🔴 Critical (Immediate Action Required)

**Daemon Crashed**
```
🚨 CRITICAL: Miner Daemon Crashed

Last activity: 23 minutes ago
Socket unresponsive at /tmp/openclawd-bittensor.sock

Recovering... attempting auto-restart
```

**Wallet Error**
```
🚨 CRITICAL: Wallet Connection Lost

Cannot reach Solana wallet via latinum-wallet-mcp
Last successful balance check: 2 hours ago

Cannot submit responses without wallet access.
Mining paused until wallet restored.

Check: wallet_manager.py logs for detailed error
```

**Budget Exhausted**
```
🚨 CRITICAL: Token Budget Exhausted

OpenAI monthly allowance completely used
Participating in remaining tasks without budget tracking

URGENT: Increase monthly allowance or cease mining
to prevent overspend
```

**Score Collapse**
```
🚨 CRITICAL: Validator Scores Collapsed

Last 20 tasks: avg score 0.14 (normally >0.7)
Likely systemic issue: wrong subnet selected? validator preference changed?

Mining paused for investigation.
Check: logs/miner.log for response rejection details
```

## Alert Thresholds

| Condition | Threshold | Level | Action |
|-----------|-----------|-------|--------|
| Daemon unavailable | >10 min | 🔴 Critical | Auto-restart, notify |
| Token budget | >80% | 🟡 Warning | Daily notification |
| Token budget | >95% | 🔴 Critical | Immediate, pause mining |
| Score trend | ↓ >20% / 7d | 🟡 Warning | Review, A/B test |
| Score trend | ↓ >50% / 7d | 🔴 Critical | Pause, investigate |
| Task success rate | <50% | 🟡 Warning | Analyze tasks |
| Task success rate | <30% | 🔴 Critical | Pause mining |
| IPC errors | >5 per hour | 🟡 Warning | Check daemon logs |

## Notification Routing

All notifications → **@patrick** (main agent channel on Telegram)

**Message Priority:**
- 🔴 Critical: Immediate, may be repeated
- 🟡 Warning: Batched once per day if threshold maintained
- 🟢 Operational: Scheduled summaries only

## Response to Notifications

### User Responses

**If you reply to a notification:**
- Acknowledge: "✅ acknowledge" or thumbs-up reaction
- Investigate: Ask specific questions about metrics
- Update: "Update participation_rate to 0.8" → applied immediately
- Pause: "Stop mining" → graceful shutdown
- Resume: "Resume subnet 1" → restart with same config

### Agent Auto-Responses

The agent can autonomously:
- ✅ Restart daemon on crash
- ✅ Adjust participation_rate based on ROI
- ✅ Swap LLM preferences based on performance
- ✅ Apply small strategy tweaks (prompt wording)
- ✅ Generate daily/weekly reports

But requires user approval for:
- 🔑 Unstaking TAO or changing stake levels
- 🔄 Switching to new subnets
- 🛑 Stopping mining entirely
- 💰 Changing token budgets (if means reduced mining)

## Quiet Hours

No non-critical notifications between 22:00 - 08:00 UTC, unless:
- 🔴 Critical alert (daemon crash, wallet error)
- 💰 Budget exhausted

Low-priority summaries (daily/weekly) still queued but delivered in morning.

## Message Format

**Keep it consistent:**

```
🔴/🟡/🟢 [TYPE]: [Headline]

[Detailed explanation, 1-2 sentences]

📊 Key metrics:
- Metric 1: value
- Metric 2: value

Action: What needs to happen, or "No action needed"
```

**Examples:**

✅ GOOD:
```
⚠️ Token Budget Alert

OpenAI at 82% of allowance.
Recommend reducing max_tokens_per_task to slow burn rate.

Current rate: 15K/day, budget exhausts in 5 days
Reduced rate (1000→800 tokens): extends 7+ days

Action: Update config/token-budgets.json max_tokens_per_task
```

❌ NOT GOOD:
```
Token budget thing

OpenAI is using a lot of money. Maybe reduce something?
```

## Implementation

Notifications are sent via:
1. **Telegram API** (using Patrick's credentials)
2. **Heartbeat system** (scheduled checks)
3. **performance_tracker.py** (anomaly detection)
4. **miner_daemon.py** (critical errors)

All notification code should:
- Use consistent emoji prefixes
- Include relevant metrics
- Suggest specific actions
- Avoid jargon (explain technical concepts)
- Keep to <500 characters when possible

---

For heartbeat monitoring logic, see HEARTBEAT.md.
For actual notification code, see src/performance_tracker.py and src/miner_daemon.py.
