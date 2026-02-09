# 🧠 Long-Term Memory

## Key Decisions
- **Model Choice:** Switched to `google-gemini-cli/gemini-3-flash-preview` for balanced performance and efficiency.
- **Wallet Solution:** Selected **Latinum** as the primary wallet for autonomous agents due to its self-hostable, open-source nature.
- **Memory Provider:** Switched to **local** embeddings (Gemma) to ensure reliable, zero-cost memory search on the local server.
- **Expanded Role:** Patrick (me) has been assigned the role of system administrator and component builder for the wider agent ecosystem.

## Core Projects
- **Bittensor Miner Plan:** Selective miner utilizing surplus inference capacity from proprietary LLM subscriptions (OpenAI, Claude, Gemini) to deliver high-quality judgement/reasoning.
- **Daily Reporting:** Fully implemented and automated. 
  - **Schedule:** 6:30 AM Melbourne (19:30 UTC).
  - **Mechanism:** Cron job `ee030c9f-5218-42ce-a6ab-fe549030df62` triggers a `systemEvent`.
  - **Script:** `./generate_daily_report.py` (NPR news + MoltX activity).
  - **Documentation:** Logged in `AGENTS.md` and `HEARTBEAT.md` for session persistence.

## Pending Tasklist
1. **Latinum Integration (Priority #1):**
   - Outline wrapper/client design for `latinum-wallet-mcp`.
   - Provide deployment guide for the user's server.
2. **Security Scanning (Priority #2):**
   - Explore `https://isnad-scanner.fly.dev` for scanning agent skills for security issues.
3. **Bittensor Implementation:**
   - Develop a concrete lifecycle of a single Bittensor task.
   - Create a decision framework for choosing the first subnet.
