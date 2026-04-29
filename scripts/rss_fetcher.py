#!/usr/bin/env python3
"""
Phase 1: RSS Fetcher
收集 RSS feeds 並保存到 cache
"""

import json
import os
import time
from datetime import datetime, timedelta
import requests
import feedparser

# Config
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')
RSS_CACHE_FILE = os.path.join(CACHE_DIR, 'rss_cache.json')

RSS_FEEDS = [
    {"name": "HackerNews AI", "url": "https://hnrss.org/newest?q=AI%20OR%20machine%20learning%20OR%20GPT%20OR%20LLM&count=20"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/tag/artificial-intelligence/feed/"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/technology-lab"},
]

# AI keyword filter for additional scoring
AI_KEYWORDS = ["AI", "artificial intelligence", "machine learning", "deep learning", 
               "neural network", "GPT", "LLM", "Claude", "OpenAI", "Anthropic",
               "language model", "generative", "automation", "agent", "robotics"]


def fetch_rss_feed(feed_info: dict) -> list:
    """Fetch single RSS feed"""
    items = []
    try:
        response = requests.get(feed_info['url'], timeout=15, headers={
            'User-Agent': 'News-Intelligence/1.0'
        })
        response.raise_for_status()
        
        feed = feedparser.parse(response.text)
        
        for entry in feed.entries[:20]:
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6]).isoformat()
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6]).isoformat()
            
            # Extract summary/description
            summary = ""
            if hasattr(entry, 'summary'):
                summary = entry.summary[:500]
            elif hasattr(entry, 'description'):
                summary = entry.description[:500]
            
            item = {
                'id': entry.get('id', entry.get('link', '')),
                'title': entry.get('title', 'No Title'),
                'url': entry.get('link', ''),
                'source': feed_info['name'],
                'published': published or datetime.now().isoformat(),
                'summary': summary,
                'entities': entry.get('tags', [])
            }
            items.append(item)
            
    except Exception as e:
        print(f"  ❌ {feed_info['name']}: {e}")
        return []
    
    print(f"  ✅ {feed_info['name']}: {len(items)} items")
    return items


def fetch_all_feeds() -> list:
    """Fetch all RSS feeds"""
    print("📡 Fetching RSS feeds...")
    all_items = []
    
    for feed in RSS_FEEDS:
        items = fetch_rss_feed(feed)
        all_items.extend(items)
        time.sleep(0.5)  # Be polite
    
    return all_items


def save_rss_cache(items: list):
    """Save RSS items to cache"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # Load existing cache
    existing = []
    if os.path.exists(RSS_CACHE_FILE):
        with open(RSS_CACHE_FILE) as f:
            existing = json.load(f)
    
    # Merge new items (avoid duplicates by id)
    existing_ids = {item['id'] for item in existing}
    new_items = [item for item in items if item['id'] not in existing_ids]
    
    combined = existing + new_items
    
    with open(RSS_CACHE_FILE, 'w') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    
    print(f"💾 RSS cache saved: {len(existing)} existing + {len(new_items)} new = {len(combined)} total")


def main():
    print("=" * 50)
    print("Phase 1: RSS Fetcher")
    print("=" * 50)
    
    items = fetch_all_feeds()
    save_rss_cache(items)
    
    print(f"\n✅ RSS Fetch Complete: {len(items)} items collected")
    
    return items


if __name__ == '__main__':
    main()