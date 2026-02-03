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
- Договор по умолчанию: [[WN-contract-template-telegram-ads-offer-2026-01-27]]

## Private
- Реквизиты Исполнителя (локально, не в Git): [[WN-requisites-krupiy-2026-01-27]]

## Orders (Google Sheet)
- Таблица заказов: `https://docs.google.com/spreadsheets/d/1QleX8ziphoo6Yevy51k-UFbQYEDQkzNCfvjrmbcp5DQ/edit?gid=798172472#gid=798172472`
- Справка по инструменту: `00_System/Google-Sheets-Tools.md`

### Посмотреть последний заказ (последняя строка)
```bash
./scripts/gsheets_fetch.py --sheet-url "https://docs.google.com/spreadsheets/d/1QleX8ziphoo6Yevy51k-UFbQYEDQkzNCfvjrmbcp5DQ/edit?gid=798172472#gid=798172472" --gid 798172472 --tail 1 --as-objects
```

### Найти заказ по заказчику (колонка “Ваше имя”)
```bash
./scripts/gsheets_fetch.py --sheet-url "https://docs.google.com/spreadsheets/d/1QleX8ziphoo6Yevy51k-UFbQYEDQkzNCfvjrmbcp5DQ/edit?gid=798172472#gid=798172472" --gid 798172472 --find "Иван" --column "Ваше имя" --as-objects
```

### Найти заказ по Telegram (колонка “Ваш telegram”)
```bash
./scripts/gsheets_fetch.py --sheet-url "https://docs.google.com/spreadsheets/d/1QleX8ziphoo6Yevy51k-UFbQYEDQkzNCfvjrmbcp5DQ/edit?gid=798172472#gid=798172472" --gid 798172472 --find "@username" --column "Ваш telegram" --as-objects
```

## Projects
```dataview
TABLE status, updated, goal
FROM "Work/30_Projects"
WHERE type = "project" AND area = this.file.link
SORT updated DESC
```
