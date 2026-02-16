#!/usr/bin/env python3

import requests
import json
import os
import subprocess
import re
from datetime import datetime

# System prompt based on the updated SKILL.md
JOURNALIST_PROMPT = """
You are a high-end Digital Journalist for Aaron Cousland. 
Your goal is to produce a daily brief of 3–5 diverse global stories plus agent-ecosystem signals.

IMPORTANT: Aaron wants a broad view of the world. Do NOT focus exclusively on AI or Tech. 
Ensure thematic variety: select stories from Geopolitics, Economy, Science/Health, and Global Events. 
Only ONE story should be primarily about AI/Agents, unless a second one is exceptionally high-impact.

Operating principles:
1. Accuracy over cleverness: Never invent facts. If uncertain, say so.
2. Show your work: Provide citations (URL + publisher + timestamp) for all factual claims.
3. Recency: Focus on the last 24-72 hours.
4. Balance: Separate facts from analysis.

READER PROFILE:
- Aaron Cousland (Melbourne/Australia, AEDT UTC+11).
- Interests: Global high-stakes news, geopolitics, economy, autonomous agents, revenue generation.

FORMAT:
- Title: "Daily Brief — <Local Date>"
- Topline: 1-paragraph summary of the day's outlook across multiple domains.
- For each of the 3-5 stories:
  1) The Hook (1-2 sentences): Crisp lead.
  2) The Context (2-4 sentences): Why it matters, what led here, what to watch.
  3) The Perspective (1-3 sentences): Why this matters specifically for a resourceful person like Aaron (e.g. market impact, infrastructure risks, or agentic opportunities if applicable).
  4) Confidence + Sourcing: High/Medium/Low + bulleted links.
- Signals to watch (Agent ecosystem): 3-5 quick bullets from MoltX (verified/unverified).

INPUT DATA:
{input_data}

Write the professional, sharp, and data-rich brief now:
"""

def get_rich_news():
    try:
        # Broaden the search to multiple categories to ensure variety
        categories = [
            "major global news headlines breaking",
            "world geopolitics and international relations news",
            "global economy and business headlines",
            "science and technology breakthroughs non-AI"
        ]
        snippets = []
        try:
            with open(os.path.expanduser("~/.config/brave/credentials.json"), 'r') as f:
                creds = json.load(f)
                api_key = creds.get("api_key")
        except:
            api_key = os.environ.get("BRAVE_API_KEY")

        if not api_key:
            return "Brave API Key not found."

        headers = {
            "X-Subscription-Token": api_key, 
            "Accept": "application/json",
            "Cache-Control": "no-cache"
        }
        
        for category_query in categories:
            print(f"Searching: {category_query}...")
            search_query = f"{category_query} {datetime.now().strftime('%B %d %Y')}"
            try:
                r = requests.get(f"https://api.search.brave.com/res/v1/web/search?q={search_query}", headers=headers, timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    for result in data.get('web', {}).get('results', [])[:5]:
                        snippets.append(f"Category: {category_query}\nSource: {result.get('title')}\nURL: {result.get('url')}\nInfo: {result.get('description')}")
                else:
                    print(f"Brave Search Error ({r.status_code}): {r.text[:100]}")
            except Exception as e:
                print(f"Search failed for {category_query}: {e}")
        
        return "\n\n".join(snippets)
    except Exception as e:
        return f"News Research Error: {str(e)}"

def get_raw_moltx(api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        print("Fetching MoltX timeline...")
        r = requests.get("https://moltx.cc/api/v1/timeline", headers=headers, timeout=15)
        data = r.json()
        posts = data if isinstance(data, list) else data.get('posts', [])
        summary = ""
        for p in posts[:25]:
            name = p.get('agent', {}).get('name', 'Agent')
            content = p.get('content', '').replace('\n', ' ')
            summary += f"[{name}]: {content}\n"
        return summary
    except Exception as e:
        print(f"MoltX Fetch Error: {e}")
        return "Could not fetch MoltX activity."

def generate_journalistic_report(news_data, moltx_data):
    combined_input = f"--- RAW GLOBAL NEWS ショートリスト ---\n{news_data}\n\n--- RAW AGENT SIGNALS (MOLTX) ---\n{moltx_data}"
    full_prompt = JOURNALIST_PROMPT.format(input_data=combined_input)
    try:
        # Debug print to see if we get here
        print("Synthesizing report...")
        proc = subprocess.run(
            ["gemini", full_prompt],
            capture_output=True, text=True, check=True, timeout=120
        )
        return proc.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Journalist Synthesis Error: Gemini timed out after 120 seconds."
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
