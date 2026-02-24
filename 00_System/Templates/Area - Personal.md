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
- <что входит / что не входит (коротко)>

## How to use this area (short)
- <когда привязывать сюда задачи/проекты/заметки>

## Reference notes (index)
- [[PN-...|<краткое название заметки>]] — <1 строка: что это / зачем>
- [[PN-...|<краткое название заметки>]] — <1 строка: что внутри>

## Projects
```dataview
TABLE status, updated, goal
FROM "Personal/30_Projects"
WHERE type = "project" AND area = this.file.link
SORT updated DESC
```

#no-graph
