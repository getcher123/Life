---
type: area
domain: work
status: active
created: 2026-01-27
updated: 2026-01-27
tags:
  - area
---

# Telegram Ads

## Definition
- Рекламные размещения в Telegram: договорённости, счёта‑оферты, маркировка (ERID/ОРД/ЕРИР), закрывающие документы.

## Templates
- Договор по умолчанию: [[W-NOTE-contract-template-telegram-ads-offer]]

## Private
- Реквизиты Исполнителя (локально, не в Git): [[W-NOTE-requisites-krupiy]]

## Projects
```dataview
TABLE status, updated, goal
FROM "Work/30_Projects"
WHERE type = "project" AND area = this.file.link
SORT updated DESC
```
