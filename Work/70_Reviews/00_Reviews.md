# Reviews (Work)

## Latest weekly review
```dataview
TABLE WITHOUT ID link(file.path, "Weekly review — " + file.name) AS "Review", dateformat(file.mtime, "yyyy-MM-dd") AS "Updated"
FROM "Work/70_Reviews/weekly"
WHERE file.name != "README"
SORT file.name DESC
LIMIT 1
```

## Weekly
```dataview
TABLE WITHOUT ID link(file.path, "Weekly review — " + file.name) AS "Review", dateformat(file.mtime, "yyyy-MM-dd") AS "Updated"
FROM "Work/70_Reviews/weekly"
WHERE file.name != "README"
SORT file.name DESC
```

## Регламент
- Onboarding: [[00_System/Onboarding|Onboarding (первая настройка)]]
- Рутины: [[00_System/Routines|Регламенты рутины (чтобы система работала)]]
- Runbook агента: [[00_System/Agent-Runbook|Runbook для AI‑агента]]

#no-graph
