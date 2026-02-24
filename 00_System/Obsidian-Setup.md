# Obsidian: минимальная настройка (кратко)

Подробная актуальная инструкция: `00_System/Onboarding.md` (этот файл — короткая памятка).

## Плагины (минимум)
- Community: **Dataview**, **Tasks**, **Kanban**.
- Core: **Templates** (и при желании Daily notes).

## Templates
- Templates folder: `00_System/Templates`
  - В репозитории уже есть настройка: `.obsidian/templates.json`.

## UI (анти‑шум, рекомендуемо)
- `Show inline title = Off`
- `Properties in document = Collapsed` или `Hidden`
- Свернуть/выключить inline `Backlinks` / `Outgoing links`
- Отключить breadcrumbs (если включены)
- Проверить, что `*/20_Tasks/00_Kanban.md` открывается как Kanban‑доска

## Именование новых сущностей
- Язык tech-ID/slug задаётся в `00_System/Vault-Config.env` (`VAULT_TECH_ID_LANGUAGE`).
- Для ручного создания сущностей используй `scripts/new-entity.sh` (task/project/area/goal/note).

## Daily notes (опционально)
В этом репозитории личные и рабочие дневники разнесены по папкам:
- `Personal/10_Daily/`
- `Work/10_Daily/`

Core‑плагин Daily notes поддерживает только одну папку. Если нужен автокреатор дневников:
- выбери одну папку для автосоздания, вторую веди вручную/через агента; или
- используй два отдельных vault, если хочешь полностью независимые настройки.

#no-graph
