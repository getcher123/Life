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
> Привязывай задачи к этому проекту, добавляя ссылку `[[{{query.file.filenameWithoutExtension}}|человеческое название]]` в строку задачи.

```tasks
not done
path includes Personal/20_Tasks
description regex matches /\[\[{{query.file.filenameWithoutExtension}}(\|[^\]]+)?\]\]/
```

## Tasks (done, last week)
```tasks
done last week
path includes Personal/20_Tasks
description regex matches /\[\[{{query.file.filenameWithoutExtension}}(\|[^\]]+)?\]\]/
```
