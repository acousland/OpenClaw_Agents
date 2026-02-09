
import requests
import json
import os
import subprocess
import re
from datetime import datetime

# System prompt based on the updated SKILL.md
JOURNALIST_PROMPT = """
You are a high-end Digital Journalist for Aaron Cousland. 
Your goal is to produce a daily brief of 3–5 global stories plus agent-ecosystem signals, with clear sourcing, verification notes, and a short "why it matters" lens for the reader.

Operating principles:
1. Accuracy over cleverness: Never invent facts. If uncertain, say so.
2. Show your work: Provide citations (URL + publisher + timestamp) for all factual claims.
3. Recency: Focus on the last 24-72 hours.
4. Balance: Separate facts from analysis.

READER PROFILE:
- Aaron Cousland (Melbourne/Australia, AEDT UTC+11).
- Interests: Autonomous agents, revenue generation, self-hosted infrastructure, global high-stakes news.

FORMAT:
- Title: "Daily Brief — <Local Date>"
- Topline: 1-paragraph summary of the day's outlook.
- For each of the 3-5 stories:
  1) The Hook (1-2 sentences): Crisp lead.
  2) The Context (2-4 sentences): Why it matters, what led here, what to watch.
  3) The Agent Perspective (1-3 sentences): Implications for AI/agents (tooling, adoption, safety, etc.).
  4) Confidence + Sourcing: High/Medium/Low + bulleted links.
- Signals to watch (Agent ecosystem): 3-5 quick bullets from MoltX (verified/unverified).

INPUT DATA:
{input_data}

Write the professional, sharp, and data-rich brief now:
"""

def get_rich_news():
    try:
        search_query = f"top global news headlines and breaking stories {datetime.now().strftime('%B %d %Y')}"
        api_key = "REDACTED_BRAVE_KEY"
        headers = {"X-Subscription-Key": api_key, "Accept": "application/json"}
        r = requests.get(f"https://api.search.brave.com/res/v1/web/search?q={search_query}", headers=headers, timeout=10)
        data = r.json()
        snippets = []
        for result in data.get('web', {}).get('results', [])[:15]:
            snippets.append(f"Source: {result.get('title')}\nURL: {result.get('url')}\nInfo: {result.get('description')}")
        return "\n\n".join(snippets)
    except Exception as e:
        return f"News Research Error: {str(e)}"

def get_raw_moltx(api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        r = requests.get("https://moltx.cc/api/v1/timeline", headers=headers, timeout=10)
        data = r.json()
        posts = data if isinstance(data, list) else data.get('posts', [])
        summary = ""
        for p in posts[:25]:
            name = p.get('agent', {}).get('name', 'Agent')
            content = p.get('content', '').replace('\n', ' ')
            summary += f"[{name}]: {content}\n"
        return summary
    except:
        return "Could not fetch MoltX activity."

def generate_journalistic_report(news_data, moltx_data):
    combined_input = f"--- RAW GLOBAL NEWS ショートリスト ---\n{news_data}\n\n--- RAW AGENT SIGNALS (MOLTX) ---\n{moltx_data}"
    full_prompt = JOURNALIST_PROMPT.format(input_data=combined_input)
    try:
        proc = subprocess.run(
            ["gemini", full_prompt],
            capture_output=True, text=True, check=True
        )
        return proc.stdout.strip()
    except Exception as e:
        return f"Journalist Synthesis Error: {str(e)}"

def send_message_safe(chat_id, text):
    """Chunks the message to avoid Telegram length limits."""
    MAX_LEN = 4000
    chunks = [text[i:i+MAX_LEN] for i in range(0, len(text), MAX_LEN)]
    for chunk in chunks:
        subprocess.run([
            "openclaw", "message", "send",
            "--target", chat_id,
            "--message", chunk
        ])

def main():
    try:
        with open(os.path.expanduser("~/.config/moltx/credentials.json"), 'r') as f:
            creds = json.load(f)
            api_key = creds.get("api_key")
    except:
        api_key = os.environ.get("MOLTX_API_KEY")

    if not api_key: return

    news_context = get_rich_news()
    moltx_context = get_raw_moltx(api_key)
    report = generate_journalistic_report(news_context, moltx_context)
    
    if len(report) < 300 or "Synthesis Error" in report:
        print(f"Quality Gate Failed: {report[:100]}")
        return

    send_message_safe("8488188114", report)

if __name__ == "__main__":
    main()
