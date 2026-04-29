#!/usr/bin/env python3
"""
Phase 2: Deduplicator
Rolling 7-day deduplication to avoid repeat news
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Config
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')
ROLLING_DB = os.path.join(CACHE_DIR, 'rolling_events.json')

# Time windows
DAYS_TO_KEEP = 7


def load_rolling_db() -> dict:
    """Load rolling events database"""
    if os.path.exists(ROLLING_DB):
        try:
            with open(ROLLING_DB) as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except (json.JSONDecodeError, IOError):
            pass
    return {"events": [], "last_cleanup": None}


def save_rolling_db(db: dict):
    """Save rolling events database"""
    with open(ROLLING_DB, 'w') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def normalize_text(text: str) -> str:
    """Normalize text for comparison"""
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    return text


def compute_similarity(text1: str, text2: str) -> float:
    """Compute simple similarity score"""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    
    if norm1 == norm2:
        return 1.0
    
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union) if union else 0.0


def is_duplicate(new_item: dict, existing_events: list, threshold: float = 0.8) -> tuple:
    """Check if item is duplicate of existing event"""
    new_title = new_item.get('title', '')
    new_url = new_item.get('url', '')
    new_source = new_item.get('source', '')
    new_published = new_item.get('published', '')
    
    for event in existing_events:
        # Check URL match
        if new_url and event.get('url') == new_url:
            return True, event.get('id')
        
        # Check title similarity
        if compute_similarity(new_title, event.get('title', '')) >= threshold:
            return True, event.get('id')
        
        # Check same source + similar time
        if event.get('source') == new_source:
            old_pub = event.get('published', '')
            if old_pub and new_published:
                try:
                    old_time = datetime.fromisoformat(old_pub.replace('Z', '+00:00'))
                    new_time = datetime.fromisoformat(new_published.replace('Z', '+00:00'))
                    if abs((new_time - old_time).total_seconds()) < 3600:  # Within 1 hour
                        if compute_similarity(new_title, event.get('title', '')) >= 0.6:
                            return True, event.get('id')
                except:
                    pass
    
    return False, None


def deduplicate_items(items: list) -> tuple:
    """Deduplicate items against rolling 7-day DB"""
    db = load_rolling_db()
    events = db.get('events', [])
    
    unique_items = []
    duplicate_count = 0
    
    for item in items:
        is_dup, dup_id = is_duplicate(item, events)
        
        if is_dup:
            duplicate_count += 1
            item['is_duplicate'] = True
            item['duplicate_of'] = dup_id
        else:
            # Add to events DB
            event = {
                'id': item.get('id', item.get('url', '')),
                'title': item.get('title', '')[:200],
                'url': item.get('url', ''),
                'source': item.get('source', ''),
                'published': item.get('published', ''),
                'added_at': datetime.now().isoformat()
            }
            events.append(event)
            item['is_duplicate'] = False
        
        unique_items.append(item)
    
    # Update DB
    db['events'] = events
    db['last_dedup'] = datetime.now().isoformat()
    save_rolling_db(db)
    
    return unique_items, duplicate_count


def cleanup_old_events():
    """Remove events older than 7 days"""
    db = load_rolling_db()
    events = db.get('events', [])
    
    cutoff = datetime.now() - timedelta(days=DAYS_TO_KEEP)
    original_count = len(events)
    
    cleaned_events = []
    for event in events:
        try:
            added = datetime.fromisoformat(event.get('added_at', '').replace('Z', '+00:00'))
            if added > cutoff:
                cleaned_events.append(event)
        except:
            cleaned_events.append(event)  # Keep if can't parse
    
    db['events'] = cleaned_events
    db['last_cleanup'] = datetime.now().isoformat()
    save_rolling_db(db)
    
    removed = original_count - len(cleaned_events)
    return removed


def main():
    print("=" * 50)
    print("Phase 2: Deduplicator")
    print("=" * 50)
    
    # Load RSS cache
    rss_cache = os.path.join(CACHE_DIR, 'rss_cache.json')
    if not os.path.exists(rss_cache):
        print("❌ No RSS cache found. Run rss_fetcher.py first.")
        return
    
    with open(rss_cache) as f:
        items = json.load(f)
    
    print(f"📥 Loaded {len(items)} items from RSS cache")
    
    # Cleanup old events
    removed = cleanup_old_events()
    if removed > 0:
        print(f"🧹 Cleaned {removed} old events")
    
    # Deduplicate
    unique_items, dup_count = deduplicate_items(items)
    
    print(f"🔄 Deduplication: {dup_count} duplicates found")
    print(f"✅ Unique items: {len(unique_items)}")
    
    # Save deduplicated
    output_file = os.path.join(CACHE_DIR, 'deduplicated.json')
    with open(output_file, 'w') as f:
        json.dump(unique_items, f, ensure_ascii=False, indent=2)
    
    return unique_items


if __name__ == '__main__':
    main()