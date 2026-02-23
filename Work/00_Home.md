# Work

## Today
```tasks
not done
path includes Work/20_Tasks
path does not include Work/20_Tasks/00_Kanban.md
due today
sort by priority
sort by due
hide backlinks
hide tags
hide edit button
hide postpone button
hide task count
```

## Scheduled today
```tasks
not done
path includes Work/20_Tasks
path does not include Work/20_Tasks/00_Kanban.md
scheduled today
sort by priority
sort by scheduled
hide backlinks
hide tags
hide edit button
hide postpone button
hide task count
```

## Overdue
```tasks
not done
path includes Work/20_Tasks
path does not include Work/20_Tasks/00_Kanban.md
due before today
sort by due
sort by priority
hide backlinks
hide tags
hide edit button
hide postpone button
hide task count
```

## This week (due)
```tasks
not done
path includes Work/20_Tasks
path does not include Work/20_Tasks/00_Kanban.md
due this week
sort by due
sort by priority
hide backlinks
hide tags
hide edit button
hide postpone button
hide task count
```

## Waiting / Blocked
```tasks
not done
path includes Work/20_Tasks
path does not include Work/20_Tasks/00_Kanban.md
description includes #waiting
sort by due
hide backlinks
hide tags
hide edit button
hide postpone button
hide task count
```

```tasks
not done
path includes Work/20_Tasks
path does not include Work/20_Tasks/00_Kanban.md
description includes #blocked
sort by due
hide backlinks
hide tags
hide edit button
hide postpone button
hide task count
```

## Focus (projects)
- [[WG-2026-w03-deliverables|Deliverables недели (Work) — 2026-W03]]
- [[WP-bi-core-xp-historic-inputs|BI core XP: проверить вводные по историке и запустить проект]]

## Projects needing attention
```dataview
TABLE WITHOUT ID project_name AS "Project", status AS "Status", dateformat(updated, "yyyy-MM-dd") AS "Updated", area_name AS "Area"
FROM "Work/30_Projects"
WHERE type = "project" AND status = "active"
FLATTEN link(file.path, replace(regexreplace(file.name, "^WP-", ""), "-", " ")) AS project_name
FLATTEN choice(area, link(area.path, replace(regexreplace(regexreplace(regexreplace(area.path, "^Work/40_Areas/", ""), "\\.md$", ""), "^WA-", ""), "-", " ")), "-") AS area_name
SORT updated ASC
LIMIT 7
```

## Quick capture
- Inbox: [[Work/00_Inbox/Incoming/README|Work/00_Inbox/Incoming]]
- [[Work/20_Tasks/00_Taskboard|Taskboard (Work)]]
- [[Work/20_Tasks/00_Kanban|Kanban (focus / WIP)]]

## Navigation
- [[Work/30_Projects/00_Projects|Projects (Work)]]
- [[Work/40_Areas/00_Areas|Areas (Work)]]
- [[Work/60_Goals/00_Goals|Goals (Work)]]
- [[Work/70_Reviews/00_Reviews|Reviews (Work)]]
- [[Work/70_Reviews/weekly/2026-W03|Weekly review (Work) — 2026-01-12]]

## Bootstrap
- [[WG-bootstrap-life-vault|Bootstrap: рабочая система заметок/задач]]

## Done today
```tasks
done today
path includes Work/20_Tasks
path does not include Work/20_Tasks/00_Kanban.md
sort by done
hide backlinks
hide tags
hide edit button
hide postpone button
hide task count
```

#no-graph
