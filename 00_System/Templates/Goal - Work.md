---
type: goal
domain: work
status: active
created: {{date:YYYY-MM-DD}}
updated: {{date:YYYY-MM-DD}}
horizon:
metric:
tags:
  - goal
---

# <Цель>

## Почему это важно
- <зачем / ценность>

## Метрика / критерий успеха
- <как измеряем>

## План
- <проекты / привычки / ставки>

## Projects
```dataview
TABLE status, updated
FROM "Work/30_Projects"
WHERE type = "project" AND goal = this.file.link
SORT updated DESC
```

## Tasks (open)
> Привязывай задачи к этой цели, добавляя ссылку `[[{{query.file.filenameWithoutExtension}}|человеческое название]]` в строку задачи.

```tasks
not done
path includes Work/20_Tasks
description regex matches /\[\[{{query.file.filenameWithoutExtension}}(\|[^\]]+)?\]\]/
```
