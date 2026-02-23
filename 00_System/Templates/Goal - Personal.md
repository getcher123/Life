---
type: goal
domain: personal
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
FROM "Personal/30_Projects"
WHERE type = "project" AND goal = this.file.link
SORT updated DESC
```

## Tasks (open)
%% Для автоподборки задач добавляй ссылку на цель в строку задачи (используй короткий алиас). %%

```tasks
not done
path includes Personal/20_Tasks
description regex matches /\[\[{{query.file.filenameWithoutExtension}}(\|[^\]]+)?\]\]/
sort by due
sort by priority
hide backlinks
hide tags
hide edit button
hide postpone button
hide task count
```

#no-graph
