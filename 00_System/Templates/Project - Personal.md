---
type: project
domain: personal
status: active
created: {{date:YYYY-MM-DD}}
updated: {{date:YYYY-MM-DD}}
# Optional links (add only if relevant; don't keep empty fields):
# area: "[[PA-...|Название area]]"
# goal: "[[PG-...|Название цели]]"
tags:
  - project
---

# <Название проекта>

## Outcome
- <какой результат считаем “готово”>

## Scope / Constraints (short)
- <что входит>
- <ограничения / сроки / рамки>

## Reference notes (index)
- [[PN-...|<brief / заметка>]] — <что внутри>
- [[PN-...|<оценка / план>]] — <что внутри>

## Risks / Open questions
- <ключевой риск или вопрос>

## Related areas (optional)
- [[PA-...|<смежная area>]] — <если есть пересечение>

## Tasks (open)
%% Для автоподборки задач добавляй ссылку на проект в строку задачи (используй короткий алиас). %%

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

## Tasks (done, last week)
```tasks
done last week
path includes Personal/20_Tasks
description regex matches /\[\[{{query.file.filenameWithoutExtension}}(\|[^\]]+)?\]\]/
sort by done reverse
hide backlinks
hide tags
hide edit button
hide postpone button
hide task count
```

#no-graph
