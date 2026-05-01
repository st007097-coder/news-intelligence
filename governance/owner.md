# News Intelligence Governance

## Owner

- **Primary Owner**: 阿星 (main agent)
- **Responsible for**: System maintenance, source updates, quality assurance

## Review Cadence

- **Monthly review** (every 30 days)
- **Next review**: 2026-06-01

## Maturity

- **Tier**: Production
- **Stage**: Production
- **Status**: Active

## Lifecycle Rules

1. **Version bumps** require: new sources, scoring changes, or format updates
2. **Breaking changes** require: user confirmation (期哥)
3. **Source updates** should be done when feeds become unavailable

## Evolution Triggers

- Add new RSS feeds when relevant AI news sources appear
- Update X account list quarterly (AI influencers change frequently)
- Improve scoring algorithm based on user feedback
- Add new content categories as AI field evolves

## Regression History

| Date | Version | Changes |
|------|---------|---------|
| 2026-05-01 | 2.0.0 | Added X Account integration, unified pipeline |
| 2026-04-29 | 1.0.0 | Initial version with RSS + Tavily |

## Quality Metrics

- **Freshness**: 7-day rolling window
- **Deduplication**: True duplicate removal
- **Scoring**: 4-tier system (🔥⭐📌📝)
- **Output**: MD + Telegram brief

## Contact & Feedback

- For source additions: 通知阿星
- For scoring issues: 通知阿星
- For system errors: 通知阿星