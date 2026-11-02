"""
Live Trend & Breaking News Intelligence Engine
Scrapes real-time trending developments from Google News RSS feeds
to feed breaking investigative topics into Gemini 3.8 Flash.
"""

import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

TREND_QUERIES = [
    "AI agents autonomous when:2d",
    "humanoid robots labor when:2d",
    "quantum computing economy when:3d",
    "autonomous corporations AI when:3d"
]

def fetch_breaking_tech_trends(limit: int = 4) -> list:
    """
    Fetches the latest real-time headlines from Google News RSS feeds.
    Returns clean, deduplicated breaking stories for the script engine.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    discovered_trends = []
    seen_titles = set()

    for query in TREND_QUERIES:
        url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:2]:
                    raw_title = item.find("title").text if item.find("title") is not None else ""
                    # Google News titles usually end with " - Publisher Name"
                    clean_title = re.sub(r"\s+-\s+[^-]+$", "", raw_title).strip()
                    
                    if clean_title and clean_title not in seen_titles:
                        seen_titles.add(clean_title)
                        pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                        discovered_trends.append({
                            "title": clean_title,
                            "published": pub_date[:16] if pub_date else "Recent",
                            "category": query.split()[0]
                        })
                        if len(discovered_trends) >= limit:
                            break
        except Exception as e:
            print(f"[TrendEngine] Google News RSS query fallback: {e}")

        if len(discovered_trends) >= limit:
            break

    # If no trends fetched (e.g. network disconnect), return curated breaking evergreen topics
    if not discovered_trends:
        discovered_trends = [
            {
                "title": "Autonomous AI Agent Swarms Replace Traditional Corporate Operations",
                "published": "Recent",
                "category": "AI Agents"
            },
            {
                "title": "Humanoid Robotics Scale Collapses Marginal Cost of Physical Labor",
                "published": "Recent",
                "category": "Robotics"
            }
        ]

    return discovered_trends

def get_latest_investigative_topic() -> dict:
    """Selects the single most urgent, high-CPM breaking topic for the next production cycle."""
    trends = fetch_breaking_tech_trends(limit=3)
    return trends[0] if trends else {
        "title": "The $40 Trillion Machine Economy Has Begun",
        "published": "Recent",
        "category": "Machine Economy"
    }
