# Areas (Work)

```dataview
TABLE WITHOUT ID area_name AS "Area", status AS "Status", dateformat(updated, "yyyy-MM-dd") AS "Updated"
FROM "Work/40_Areas"
WHERE type = "area"
FLATTEN link(file.path, replace(regexreplace(file.name, "^WA-", ""), "-", " ")) AS area_name
SORT updated DESC
```

## Active projects by area
```dataview
TABLE WITHOUT ID area_name AS "Area", length(rows) AS "Active projects", dateformat(max(rows.updated), "yyyy-MM-dd") AS "Last project update"
FROM "Work/30_Projects"
WHERE type = "project" AND status = "active"
GROUP BY area
FLATTEN choice(key, link(key.path, replace(regexreplace(regexreplace(regexreplace(key.path, "^Work/40_Areas/", ""), "\\.md$", ""), "^WA-", ""), "-", " ")), "-") AS area_name
SORT length(rows) DESC, max(rows.updated) ASC
```

## Active projects (detailed)
```dataview
TABLE WITHOUT ID project_name AS "Project", area_name AS "Area", dateformat(updated, "yyyy-MM-dd") AS "Updated", goal_name AS "Goal"
FROM "Work/30_Projects"
WHERE type = "project" AND status = "active"
FLATTEN link(file.path, replace(regexreplace(file.name, "^WP-", ""), "-", " ")) AS project_name
FLATTEN choice(area, link(area.path, replace(regexreplace(regexreplace(regexreplace(area.path, "^Work/40_Areas/", ""), "\\.md$", ""), "^WA-", ""), "-", " ")), "-") AS area_name
FLATTEN choice(goal, link(goal.path, replace(regexreplace(regexreplace(regexreplace(goal.path, "^Work/60_Goals/", ""), "\\.md$", ""), "^WG-", ""), "-", " ")), "-") AS goal_name
SORT area ASC, updated DESC
```

#no-graph
