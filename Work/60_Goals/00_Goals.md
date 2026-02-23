# Goals (Work)

```dataview
TABLE WITHOUT ID key AS "Status", length(rows) AS "Count"
FROM "Work/60_Goals"
WHERE type = "goal"
GROUP BY status
SORT key ASC
```

## Active goals
```dataview
TABLE WITHOUT ID goal_name AS "Goal", status AS "Status", horizon AS "Horizon", dateformat(updated, "yyyy-MM-dd") AS "Updated"
FROM "Work/60_Goals"
WHERE type = "goal" AND status = "active"
FLATTEN link(file.path, replace(regexreplace(file.name, "^WG-", ""), "-", " ")) AS goal_name
SORT updated DESC
```

## Goal metrics / success criteria
```dataview
TABLE WITHOUT ID goal_name AS "Goal", metric AS "Metric", dateformat(updated, "yyyy-MM-dd") AS "Updated"
FROM "Work/60_Goals"
WHERE type = "goal" AND status = "active"
FLATTEN link(file.path, replace(regexreplace(file.name, "^WG-", ""), "-", " ")) AS goal_name
SORT updated DESC
```

## Needs review (oldest updates first)
```dataview
TABLE WITHOUT ID goal_name AS "Goal", status AS "Status", horizon AS "Horizon", dateformat(updated, "yyyy-MM-dd") AS "Updated"
FROM "Work/60_Goals"
WHERE type = "goal" AND status = "active"
FLATTEN link(file.path, replace(regexreplace(file.name, "^WG-", ""), "-", " ")) AS goal_name
SORT updated ASC
```

#no-graph
