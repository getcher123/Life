---
type: area
domain: work
status: active
created: {{date:YYYY-MM-DD}}
updated: {{date:YYYY-MM-DD}}
tags:
  - area
---

# <Область>

## Definition
- <за что отвечаю / что поддерживаю>

## Projects
```dataview
TABLE status, updated, goal
FROM "Work/30_Projects"
WHERE type = "project" AND area = this.file.link
SORT updated DESC
```

#no-graph
