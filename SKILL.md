---
name: news-intelligence
description: "智能資訊收集、分析、去重、總結系統。整合 RSS + Tavily + X Accounts 三個來源，自動每日生成 AI 新聞摘要。觸發詞：'AI 新聞'、'今日資訊'、'News Intelligence'、'新聞摘要'、'每日資訊'、'最新 AI 動態'。"
version: "2.0.0"
metadata:
  author: "阿星"
  created: "2026-04-29"
  updated: "2026-05-01"
  trigger_priority: high
  output_type: markdown + telegram
---

# News Intelligence System

OCM Sup 之外第2個 Project — 智能資訊收集、分析、去重、總結

## 🎯 目標

大量收集各方資訊 → 阿星分析去重總結 → 重要資訊比期哥

## ⚡ 觸發條件

| 觸發詞 | 說明 |
|--------|------|
| "AI 新聞" | 即時生成 AI/科技新聞摘要 |
| "今日資訊" | 獲取今日最新資訊 |
| "News Intelligence" | 啟動完整收集流程 |
| "新聞摘要" | 生成每日摘要 |
| "每日資訊" | 檢查並生成當日摘要 |
| "最新 AI 動態" | 獲取最近 AI 動態 |

## 📁 專案結構

```
news-intelligence/
├── sources/              # 來源配置
│   ├── rss_feeds.yaml    # RSS feeds 配置
│   ├── x_accounts/       # X accounts 清單
│   └── tavily_config.json # API 配置（不在 Git）
├── scripts/              # 核心腳本
│   ├── rss_fetcher.py       # Phase 1: RSS 收集
│   ├── deduplicator.py      # Phase 2: Rolling 7-day 去重
│   ├── scorer.py            # Phase 3: 興趣評分
│   ├── daily_digest.py      # Phase 4: 每日總結生成
│   ├── unified_collector.py  # 統一收集器
│   └── x_account_fetcher.py # X Account 掃描
├── cache/                # 緩存（不去 Git）
├── output/               # 輸出
├── tests/               # 測試
└── README.md
```

## 🔄 執行流程

### Phase 0: 初始化
1. 確認執行環境（Python 3, httpx, feedparser）
2. 讀取 sources/ 配置
3. 檢查 cache/ 狀態

### Phase 1: 收集（Collection）
```
[1/6] 🧹 Cleanup old events...
[2/6] 📡 Fetch RSS feeds...
[3/6] 🔍 Search Tavily (optional)...
[4/6] 📱 Scan X Accounts...
[5/6] 🔄 Deduplicating...
[6/6] 🎯 Scoring and filtering...
```

### Phase 2: 去重（Deduplication）
- Rolling 7-day Events DB
- 新聞進入時 check 數據庫
- 有就標記為"舊聞"降權
- 冇就加入數據庫
- 自動清理第8日

### Phase 3: 評分（Scoring）
評分標準：
- AI/模型重大發布：+3分
- AI Agent/框架：+2分
- 實用工具/產品：+2分
- 行業趨勢：+1分
- 其他：+0分

輸出分級：
- 🔥 8-10分：頭條
- ⭐ 5-7分：重要
- 📌 3-4分：值得關注
- 📝 0-2分：一般

### Phase 4: 輸出（Output）
1. **詳細 MD** → `wiki/AI-News/daily/YYYY-MM-DD.md`
2. **簡報** → 直接 message 期哥

---

## ⚠️ 邊界條件（Boundary Conditions）

| 情況 | 處理方式 |
|------|----------|
| Tavily API key 缺失 | 跳過 Tavily，繼續 RSS + X |
| X Accounts 無法訪問 | 降級到 RSS only，標記 warning |
| 所有 source 失敗 | 輸出「今日無新資訊」並說明原因 |
| 去重後數量為 0 | 輸出「過去7日無新增資訊」 |
| 快取過期 | 自動重建 cache |

---

## 🛑 檢查點（Checkpoints）

| 檢查點 | 觸發條件 | 暫停等待確認 |
|--------|----------|-------------|
| **預覽確認** | 收集完成後，評分前 | ✅ 用戶確認繼續 |
| **输出格式確認** | 生成摘要前 | ✅ 用戶確認格式 |
| **緊急新聞** | 評分 ≥8 的頭條 | ✅ 立即展示 |

### 預覽確認 Prompt
```
📊 收集完成！
- RSS: {n} items
- X Accounts: {n} items
- 估計頭條: {n}

✅ 按 /confirm 繼續生成摘要
❌ 按 /cancel 取消
```

---

## 📊 數據來源

| 來源 | 類型 | 数量 | 狀態 |
|------|------|------|------|
| HackerNews AI | RSS | 20 | ✅ |
| MIT Tech Review | RSS | 10 | ✅ |
| TechCrunch AI | RSS | 19 | ✅ |
| The Verge AI | RSS | 10 | ✅ |
| Ars Technica | RSS | 20 | ✅ |
| Tavily Search | API | ~24 | ⏸️ 可選 |
| X Accounts | Google | 65 | ✅ |

---

## 🧪 測試

```bash
# 測試所有 Phase
python3 scripts/unified_collector.py --dry-run

# 測試 RSS
python3 scripts/rss_fetcher.py --test

# 測試 X Accounts
python3 scripts/x_account_fetcher.py --test

# 運行單元測試
python3 -m pytest tests/ -v
```

---

## 📝 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| 1.0 | 2026-04-29 | 初始版本 |
| 2.0 | 2026-05-01 | 整合 X Accounts，統一 Pipeline |

---

_Last updated: 2026-05-01_