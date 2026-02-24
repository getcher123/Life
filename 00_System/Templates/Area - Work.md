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
- <что входит / что не входит (коротко)>

## How to use this area (short)
- <когда привязывать сюда задачи/проекты/заметки>
- <какой основной процесс/стандарт применяется>

## Reusable Checklist (optional)
- <чеклист/гайдлайн для повторяемых задач в этой area>

## Red Flags / Risks (optional)
- <типовые риски/ошибки, на которые смотреть в задачах этой area>

## Reference notes (index)
- [[WN-...|<краткое название заметки>]] — <1 строка: что это и когда использовать>
- [[WN-...|<краткое название заметки>]] — <1 строка: что внутри>

## Related areas (optional)
- [[WA-...|<смежная область>]] — <когда пересекаются>

## Projects
```dataview
TABLE status, updated, goal
FROM "Work/30_Projects"
WHERE type = "project" AND area = this.file.link
SORT updated DESC
```

#no-graph
