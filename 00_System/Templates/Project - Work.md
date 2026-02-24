---
type: project
domain: work
status: active
created: {{date:YYYY-MM-DD}}
updated: {{date:YYYY-MM-DD}}
# Optional links (add only if relevant; don't keep empty fields):
# area: "[[WA-...|Название area]]"
# goal: "[[WG-...|Название цели]]"
tags:
  - project
---

# <Название проекта>

## Outcome
- <какой результат считаем “готово”>

## Scope / Constraints (short)
- <что входит в проект>
- <ключевые ограничения / дедлайн / формат>

## Reference notes (index)
- [[WN-...|<brief / входящие>]] — <что внутри>
- [[WN-...|<оценка / смета>]] — <что внутри>
- [[WN-...|<ТЗ / handoff>]] — <что внутри>

## Risks / Open questions
- <критичный риск или вопрос>

## Related areas (optional)
- [[WA-...|<смежная area>]] — <если проект пересекается с несколькими контурами>

## Tasks (open)
%% Для автоподборки задач добавляй ссылку на проект в строку задачи (используй короткий алиас). %%

```tasks
not done
path includes Work/20_Tasks
description regex matches /\[\[{{query.file.filenameWithoutExtension}}(\|[^\]]+)?\]\]/
sort by due
sort by priority
hide backlinks
hide tags
hide edit button
hide postpone button
hide task count
```

## Tasks (done, last week)
```tasks
done last week
path includes Work/20_Tasks
description regex matches /\[\[{{query.file.filenameWithoutExtension}}(\|[^\]]+)?\]\]/
sort by done reverse
hide backlinks
hide tags
hide edit button
hide postpone button
hide task count
```

#no-graph
