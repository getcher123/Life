# PPTX → текст → заметка

Скрипт `scripts/pptx2note.sh` извлекает текст со слайдов `.pptx` и создаёт заметку в `*/50_Notes/` с:
- `## Summary` (заполняется человеком/агентом),
- `## Outline` (по слайдам),
- `## Keywords` (простая частотная выборка),
- `## Extracted Text` (полный текст).

## Использование

```bash
scripts/pptx2note.sh "/path/to/deck.pptx" --domain work
```

Опционально привязать к проекту:

```bash
scripts/pptx2note.sh "/path/to/deck.pptx" --domain work --project [[W-PROJ-...]]
```

## Incoming (drop folder)

Если `.pptx` лежит в `Work/00_Inbox/Incoming/`, обработка идёт через:

```bash
scripts/process-incoming.sh --domain work
```

