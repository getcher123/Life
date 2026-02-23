---
type: project
domain: personal
status: active
created: {{date:YYYY-MM-DD}}
updated: {{date:YYYY-MM-DD}}
area:
goal:
tags:
  - project
---

# <Название проекта>

## Outcome
- <какой результат считаем “готово”>

## Notes
- <контекст/ссылки/риски>

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
