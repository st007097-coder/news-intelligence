#!/usr/bin/env python3
"""
Unified Collector: RSS + Tavily + X Accounts
Combines all sources into single pipeline
"""

import json
import os
import sys
from datetime import datetime, timedelta

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from rss_fetcher import fetch_all_feeds, save_rss_cache
from deduplicator import deduplicate_items, cleanup_old_events
from scorer import score_item, filter_by_freshness
from daily_digest import save_digest

# Config
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')
SOURCES_DIR = os.path.join(os.path.dirname(__file__), '..', 'sources')

# Tavily search queries (for AI news)
TAVILY_QUERIES = [
    "OpenAI GPT AI news 2024",
    "Anthropic Claude AI news 2024",
    "AI Agent autonomous news 2024"
]

# X Account keywords (from ai-influence-digest)
X_ACCOUNT_KEYWORDS = ["tool", "workflow", "method", "tutorial", "prompt", "tip", "guide", "framework"]
X_ACCOUNT_EXCLUDE = ["gpu", "tpu", "benchmark", "funding", "raised", "valuation", "revenue", "pricing", "acquisition"]


def search_tavily(query: str, api_key: str = None) -> list:
    """Search using Tavily API"""
    if not api_key:
        config_file = os.path.join(SOURCES_DIR, 'tavily_config.json')
        if os.path.exists(config_file):
            with open(config_file) as f:
                config = json.load(f)
                api_key = config.get('api_key')
        
        if not api_key:
            print("  ⚠️ Tavily API key not configured")
            return []
    
    try:
        import httpx
        
        response = httpx.post(
            "https://api.tavily.com/search",
            json={
                "query": query,
                "search_depth": "basic",
                "max_results": 8
            },
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            items = []
            for r in results:
                items.append({
                    'id': r.get('url', ''),
                    'title': r.get('title', ''),
                    'url': r.get('url', ''),
                    'source': 'Tavily',
                    'published': datetime.now().isoformat(),
                    'summary': r.get('content', '')[:300],
                    'score': 2
                })
            
            print(f"  ✅ Tavily '{query}': {len(items)} results")
            return items
        else:
            print(f"  ❌ Tavily error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"  ❌ Tavily exception: {e}")
        return []


def fetch_x_accounts() -> list:
    """Fetch X account content via Google search (without X API)
    
    Uses opencli google search to scan AI influencer accounts.
    Falls back to accounts.txt list if available.
    """
    accounts_file = os.path.join(SOURCES_DIR, 'x_accounts', 'accounts.txt')
    
    if not os.path.exists(accounts_file):
        print("  ⚠️ X accounts file not found, skipping")
        return []
    
    # Read account list
    with open(accounts_file, 'r') as f:
        accounts = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"  📱 X Accounts: {len(accounts)} accounts configured")
    
    # Check if opencli is available
    try:
        import subprocess
        subprocess.run(['opencli', '--version'], capture_output=True, check=True)
        opencli_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  ⚠️ opencli not available, skipping X accounts")
        return []
    
    items = []
    
    try:
        # Use Google search to find recent posts
        for account in accounts[:10]:  # Limit to 10 accounts for performance
            try:
                cmd = [
                    'opencli', 'google', 'search',
                    '-f', 'json',
                    '--limit', '5',
                    '--lang', 'en',
                    f"site:x.com OR site:twitter.com {account} AI tool tutorial"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and result.stdout:
                    try:
                        results = json.loads(result.stdout)
                        for r in results:
                            # Filter by keywords
                            title = r.get('title', '').lower()
                            if any(kw in title for kw in X_ACCOUNT_KEYWORDS):
                                if not any(ex in title for ex in X_ACCOUNT_EXCLUDE):
                                    items.append({
                                        'id': r.get('url', ''),
                                        'title': r.get('title', ''),
                                        'url': r.get('url', ''),
                                        'source': f'X:{account}',
                                        'published': datetime.now().isoformat(),
                                        'summary': r.get('snippet', '')[:300],
                                        'score': 2
                                    })
                    except json.JSONDecodeError:
                        pass
            except Exception as e:
                continue  # Skip failed accounts
    
    except Exception as e:
        print(f"  ❌ X account fetch error: {e}")
    
    print(f"  ✅ X Accounts: {len(items)} items from search")
    return items


def unified_pipeline():
    """Run complete unified pipeline with all sources"""
    print("=" * 60)
    print("🚀 News Intelligence — Unified Pipeline v2.0")
    print("   RSS + Tavily + X Accounts")
    print("=" * 60)
    
    all_items = []
    
    # Step 1: Cleanup old events
    print("\n[1/6] 🧹 Cleanup old events...")
    removed = cleanup_old_events()
    if removed > 0:
        print(f"  Cleaned {removed} events older than 7 days")
    
    # Step 2: Fetch RSS feeds
    print("\n[2/6] 📡 Fetch RSS feeds...")
    rss_items = fetch_all_feeds()
    all_items.extend(rss_items)
    print(f"  RSS: {len(rss_items)} items")
    
    # Step 3: Search Tavily
    print("\n[3/6] 🔍 Search Tavily...")
    tavily_items = []
    # Uncomment to enable Tavily:
    # for query in TAVILY_QUERIES:
    #     results = search_tavily(query)
    #     tavily_items.extend(results)
    all_items.extend(tavily_items)
    if tavily_items:
        print(f"  Tavily: {len(tavily_items)} items")
    else:
        print("  Tavily: skipped (no API key)")
    
    # Step 4: Fetch X Accounts (via Google search, not X API)
    print("\n[4/6] 📱 Scan X Accounts...")
    x_items = fetch_x_accounts()
    all_items.extend(x_items)
    print(f"  X Accounts: {len(x_items)} items")
    
    print(f"\n  Combined total: {len(all_items)} items")
    
    # Step 5: Deduplicate
    print("\n[5/6] 🔄 Deduplicating...")
    unique_items, dup_count = deduplicate_items(all_items)
    print(f"  Duplicates found: {dup_count}")
    print(f"  Unique items: {len(unique_items)}")
    
    # Step 6: Score and filter
    print("\n[6/6] 🎯 Scoring and filtering...")
    scored_items = [score_item(item) for item in unique_items]
    fresh_items = filter_by_freshness(scored_items, days=7)
    fresh_items.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"  Fresh items (7-day): {len(fresh_items)}")
    
    # Count tiers
    tier_counts = {"🔥 Headline": 0, "⭐ Important": 0, "📌 Notable": 0, "📝 General": 0}
    for item in fresh_items:
        tier = item.get('tier', '📝 General')
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    print("\n📊 Final Results:")
    for tier, count in sorted(tier_counts.items(), key=lambda x: -x[1]):
        print(f"  {tier}: {count}")
    
    # Save unified combined
    output_file = os.path.join(CACHE_DIR, 'unified_combined.json')
    with open(output_file, 'w') as f:
        json.dump(fresh_items, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Saved: {output_file}")
    
    # Generate digest
    print("\n📄 Generating digest...")
    save_digest(fresh_items)
    
    print("\n" + "=" * 60)
    print("✅ Unified Pipeline Complete!")
    print("=" * 60)
    
    return fresh_items


if __name__ == '__main__':
    items = unified_pipeline()
    print(f"\nTotal fresh items: {len(items)}")