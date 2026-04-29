#!/usr/bin/env python3
"""
Phase 3: Interest Scorer
Score news items based on interest keywords
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Config
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')

# Interest scoring keywords
SCORING_KEYWORDS = {
    # High priority (AI/模型重大發布)
    "high": [
        "GPT-5", "GPT-4o", "GPT-4", "Claude 4", "Claude 3.5", "Gemini 2.0",
        "OpenAI", "Anthropic", "Google DeepMind", "Meta AI",
        "language model", "foundation model", "multimodal",
        "breakthrough", "revolutionary", "state-of-the-art", "SOTA"
    ],
    # Medium priority (AI Agent/框架)
    "medium": [
        "AI agent", "agentic", "autonomous", "reasoning", "chain-of-thought",
        "framework", "tool use", "RAG", "fine-tuning",
        "LangChain", "AutoGPT", "BabyAGI", "crewAI"
    ],
    # Lower priority (實用工具/產品)
    "lower": [
        "API", "SDK", "open source", "github", "release",
        "product", "launch", "announcement", "integration"
    ],
    # Low priority (行業趨勢)
    "low": [
        "trend", "market", "investment", "funding", "startup",
        "regulation", "policy", "ethics", "privacy"
    ]
}

# Score mapping
SCORE_MAP = {
    "high": 3,
    "medium": 2,
    "lower": 1,
    "low": 1
}

# Score thresholds
THRESHOLDS = {
    "headline": 8,    # 🔥 8-10
    "important": 5,    # ⭐ 5-7
    "notable": 3,     # 📌 3-4
    # 0-2 = 📝 General
}


def score_item(item: dict) -> dict:
    """Score a single item"""
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    
    score = 0
    matched_keywords = []
    
    for level, keywords in SCORING_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                score += SCORE_MAP[level]
                matched_keywords.append(kw)
    
    # Cap at 10
    score = min(score, 10)
    
    # Determine tier
    if score >= THRESHOLDS["headline"]:
        tier = "🔥 Headline"
    elif score >= THRESHOLDS["important"]:
        tier = "⭐ Important"
    elif score >= THRESHOLDS["notable"]:
        tier = "📌 Notable"
    else:
        tier = "📝 General"
    
    item['score'] = score
    item['tier'] = tier
    item['matched_keywords'] = matched_keywords[:5]  # Keep top 5
    
    return item


def filter_by_freshness(items: list, days: int = 7) -> list:
    """Filter items to only show fresh ones (within N days)"""
    cutoff = datetime.now() - timedelta(days=days)
    fresh_items = []
    
    for item in items:
        try:
            pub = item.get('published', '')
            if pub:
                pub_date = datetime.fromisoformat(pub.replace('Z', '+00:00'))
                if pub_date > cutoff:
                    fresh_items.append(item)
            else:
                fresh_items.append(item)  # Keep if no date
        except:
            fresh_items.append(item)
    
    return fresh_items


def main():
    print("=" * 50)
    print("Phase 3: Interest Scorer")
    print("=" * 50)
    
    # Load deduplicated items
    dedup_file = os.path.join(CACHE_DIR, 'deduplicated.json')
    if not os.path.exists(dedup_file):
        print("❌ No deduplicated items found. Run deduplicator.py first.")
        return
    
    with open(dedup_file) as f:
        items = json.load(f)
    
    print(f"📥 Loaded {len(items)} items for scoring")
    
    # Score all items
    scored_items = [score_item(item) for item in items]
    
    # Filter to fresh items only (7 days)
    fresh_items = filter_by_freshness(scored_items, days=7)
    
    print(f"📅 Fresh items (7-day): {len(fresh_items)} of {len(items)}")
    
    # Sort by score descending
    fresh_items.sort(key=lambda x: x['score'], reverse=True)
    
    # Count by tier
    tier_counts = {
        "🔥 Headline": 0,
        "⭐ Important": 0,
        "📌 Notable": 0,
        "📝 General": 0
    }
    
    for item in fresh_items:
        tier_counts[item['tier']] = tier_counts.get(item['tier'], 0) + 1
    
    print("\n📊 Scoring Results:")
    for tier, count in tier_counts.items():
        print(f"  {tier}: {count}")
    
    # Save scored items
    output_file = os.path.join(CACHE_DIR, 'scored_items.json')
    with open(output_file, 'w') as f:
        json.dump(fresh_items, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Scored and saved {len(fresh_items)} items to {output_file}")
    
    return fresh_items


if __name__ == '__main__':
    main()