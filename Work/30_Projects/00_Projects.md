# Projects (Work)

```dataview
TABLE WITHOUT ID key AS "Status", length(rows) AS "Count"
FROM "Work/30_Projects"
WHERE type = "project"
GROUP BY status
SORT key ASC
```

## Active (portfolio)
```dataview
TABLE WITHOUT ID project_name AS "Project", status AS "Status", dateformat(updated, "yyyy-MM-dd") AS "Updated", area_name AS "Area", goal_name AS "Goal"
FROM "Work/30_Projects"
WHERE type = "project" AND status = "active"
FLATTEN link(file.path, replace(regexreplace(file.name, "^WP-", ""), "-", " ")) AS project_name
FLATTEN choice(area, link(area.path, replace(regexreplace(regexreplace(regexreplace(area.path, "^Work/40_Areas/", ""), "\\.md$", ""), "^WA-", ""), "-", " ")), "-") AS area_name
FLATTEN choice(goal, link(goal.path, replace(regexreplace(regexreplace(regexreplace(goal.path, "^Work/60_Goals/", ""), "\\.md$", ""), "^WG-", ""), "-", " ")), "-") AS goal_name
SORT updated DESC
```

## Needs attention (oldest updates first)
```dataview
TABLE WITHOUT ID project_name AS "Project", status AS "Status", dateformat(updated, "yyyy-MM-dd") AS "Updated"
FROM "Work/30_Projects"
WHERE type = "project" AND status = "active"
FLATTEN link(file.path, replace(regexreplace(file.name, "^WP-", ""), "-", " ")) AS project_name
SORT updated ASC
```

## Missing links (area/goal)
```dataview
TABLE WITHOUT ID project_name AS "Project", choice(!area AND !goal, "area + goal", choice(!area, "area", "goal")) AS "Missing", dateformat(updated, "yyyy-MM-dd") AS "Updated"
FROM "Work/30_Projects"
WHERE type = "project" AND status = "active" AND (!area OR !goal)
FLATTEN link(file.path, replace(regexreplace(file.name, "^WP-", ""), "-", " ")) AS project_name
SORT updated ASC
```

## Archive
- [[Work/99_Archive/30_Projects/|Work/99_Archive/30_Projects]]

#no-graph
