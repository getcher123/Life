---
type: area
domain: personal
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
FROM "Personal/30_Projects"
WHERE type = "project" AND area = this.file.link
SORT updated DESC
```

#no-graph
