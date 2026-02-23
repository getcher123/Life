# Notes (Work)

```dataview
TABLE WITHOUT ID note_name AS "Note", dateformat(updated, "yyyy-MM-dd") AS "Updated"
FROM "Work/50_Notes"
WHERE type = "note"
FLATTEN link(file.path, replace(regexreplace(regexreplace(file.name, "^WN-", ""), "-\\d{4}-\\d{2}-\\d{2}$", ""), "-", " ")) AS note_name
SORT updated DESC
LIMIT 15
```

## Needs triage (no project / no task)
```dataview
TABLE WITHOUT ID note_name AS "Note", dateformat(updated, "yyyy-MM-dd") AS "Updated", tags AS "Tags"
FROM "Work/50_Notes"
WHERE type = "note" AND !project AND !task
FLATTEN link(file.path, replace(regexreplace(regexreplace(file.name, "^WN-", ""), "-\\d{4}-\\d{2}-\\d{2}$", ""), "-", " ")) AS note_name
SORT updated DESC
```

## Imported / source notes (DOCX / audio / PPTX)
```dataview
TABLE WITHOUT ID note_name AS "Note", dateformat(updated, "yyyy-MM-dd") AS "Updated", project_name AS "Project", tags AS "Tags"
FROM "Work/50_Notes"
WHERE type = "note" AND (contains(tags, "docx") OR contains(tags, "audio") OR contains(tags, "pptx"))
FLATTEN link(file.path, replace(regexreplace(regexreplace(file.name, "^WN-", ""), "-\\d{4}-\\d{2}-\\d{2}$", ""), "-", " ")) AS note_name
FLATTEN choice(project, link(project.path, replace(regexreplace(regexreplace(regexreplace(project.path, "^Work/30_Projects/", ""), "\\.md$", ""), "^WP-", ""), "-", " ")), "-") AS project_name
SORT updated DESC
```

#no-graph
