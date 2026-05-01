#!/usr/bin/env python3
"""Tests for News Intelligence System"""

import sys
import os

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

def test_rss_fetcher_import():
    """Test RSS fetcher can be imported"""
    try:
        from rss_fetcher import fetch_all_feeds, save_rss_cache
        print("✅ rss_fetcher: Import successful")
        return True
    except ImportError as e:
        print(f"❌ rss_fetcher: Import failed - {e}")
        return False

def test_deduplicator_import():
    """Test deduplicator can be imported"""
    try:
        from deduplicator import deduplicate_items, cleanup_old_events
        print("✅ deduplicator: Import successful")
        return True
    except ImportError as e:
        print(f"❌ deduplicator: Import failed - {e}")
        return False

def test_scorer_import():
    """Test scorer can be imported"""
    try:
        from scorer import score_item, filter_by_freshness
        print("✅ scorer: Import successful")
        return True
    except ImportError as e:
        print(f"❌ scorer: Import failed - {e}")
        return False

def test_daily_digest_import():
    """Test daily digest can be imported"""
    try:
        from daily_digest import save_digest
        print("✅ daily_digest: Import successful")
        return True
    except ImportError as e:
        print(f"❌ daily_digest: Import failed - {e}")
        return False

def test_sources_config():
    """Test sources configuration exists"""
    sources_dir = os.path.join(os.path.dirname(__file__), '..', 'sources')
    rss_config = os.path.join(sources_dir, 'rss_feeds.yaml')
    accounts_file = os.path.join(sources_dir, 'x_accounts', 'accounts.txt')
    
    if os.path.exists(rss_config):
        print(f"✅ sources: rss_feeds.yaml exists")
    else:
        print(f"❌ sources: rss_feeds.yaml missing")
        return False
    
    if os.path.exists(accounts_file):
        print(f"✅ sources: x_accounts/accounts.txt exists")
    else:
        print(f"❌ sources: x_accounts/accounts.txt missing")
        return False
    
    return True

def test_manifest():
    """Test manifest.json exists and is valid"""
    manifest_path = os.path.join(os.path.dirname(__file__), '..', 'manifest.json')
    
    if not os.path.exists(manifest_path):
        print(f"❌ manifest.json: missing")
        return False
    
    try:
        import json
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        required_fields = ['name', 'version', 'owner', 'status']
        for field in required_fields:
            if field not in manifest:
                print(f"❌ manifest.json: missing '{field}'")
                return False
        
        print(f"✅ manifest.json: valid (v{manifest.get('version', '?')})")
        return True
    except Exception as e:
        print(f"❌ manifest.json: invalid - {e}")
        return False

def test_skill_md():
    """Test SKILL.md exists and has required sections"""
    skill_path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
    
    if not os.path.exists(skill_path):
        print(f"❌ SKILL.md: missing")
        return False
    
    with open(skill_path) as f:
        content = f.read()
    
    required_sections = ['## 🎯 目標', '## 🔄 執行流程', '## ⚠️ 邊界條件', '## 🛑 檢查點']
    missing = []
    for section in required_sections:
        if section not in content:
            missing.append(section)
    
    if missing:
        print(f"❌ SKILL.md: missing sections: {missing}")
        return False
    
    print(f"✅ SKILL.md: all required sections present")
    return True

def test_evals():
    """Test evals directory has required files"""
    evals_dir = os.path.join(os.path.dirname(__file__), '..', 'evals')
    
    trigger_cases = os.path.join(evals_dir, 'trigger_cases.json')
    semantic_config = os.path.join(evals_dir, 'semantic_config.json')
    
    if os.path.exists(trigger_cases):
        print(f"✅ evals: trigger_cases.json exists")
    else:
        print(f"❌ evals: trigger_cases.json missing")
        return False
    
    if os.path.exists(semantic_config):
        print(f"✅ evals: semantic_config.json exists")
    else:
        print(f"❌ evals: semantic_config.json missing")
        return False
    
    return True

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("🧪 News Intelligence System - Tests")
    print("=" * 50)
    print()
    
    tests = [
        test_manifest,
        test_skill_md,
        test_evals,
        test_sources_config,
        test_rss_fetcher_import,
        test_deduplicator_import,
        test_scorer_import,
        test_daily_digest_import,
    ]
    
    results = []
    for test in tests:
        print(f"\n{test.__name__}:")
        results.append(test())
    
    print()
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"📊 Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All tests passed!")
        return True
    else:
        print(f"❌ {total - passed} test(s) failed")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)