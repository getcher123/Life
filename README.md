# Life (Obsidian + Git)

Этот репозиторий — Obsidian‑vault для личной и рабочей системы:
- заметки и знания (`[[wiki links]]`);
- задачи / проекты / цели;
- Git‑история и работа с AI‑агентом через файлы.

## Что это решает
- Единый процесс: входящее → заметка → уточнения → задачи/проекты.
- Связный контекст: `goal → project → task → note`.
- Дашборды (Tasks/Dataview) + Kanban для фокуса.
- Аккуратный Git‑след: минимальный дифф, архив вместо удаления.

## Быстрый старт (5 шагов)
1. Открой папку репозитория в Obsidian: `Open folder as vault`.
2. Включи core‑плагин `Templates` и укажи папку: [`00_System/Templates`](00_System/Templates/).
3. Установи community‑плагины: `Dataview`, `Tasks`, `Kanban`.
4. Запусти проверку структуры: `bash scripts/healthcheck.sh` (скрипт: [scripts/healthcheck.sh](scripts/healthcheck.sh)).
5. Запусти агентский bootstrap: `@Bootstrapper`.

Стартовые страницы:
- [`INDEX.md`](INDEX.md)
- [`Personal/00_Home.md`](Personal/00_Home.md)
- [`Work/00_Home.md`](Work/00_Home.md)

## Obsidian (анти‑шум, рекомендуемо)
- `Show inline title = Off`
- `Properties in document = Collapsed` (или `Hidden`)
- Сверни/выключи inline `Backlinks` и `Outgoing links`
- Отключи breadcrumbs (если включены)
- Проверь, что `*/20_Tasks/00_Kanban.md` открывается как kanban‑доска

Подробная настройка Obsidian и UI: [`00_System/Onboarding.md`](00_System/Onboarding.md).

## AI‑агент (быстрые команды)
- `@Bootstrapper Подключаюсь к vault впервые. Проведи bootstrap и проверь настройку.`
- `@Assistant Выдай сводку по задачам в человеческом формате и предложи фокус на сегодня.`
- `@Assistant Разбери входящие и оформи заметки, потом задай уточнения.`
- `@Router Помоги выбрать роль и разложить запрос на шаги: ...`
- `@Repo-Maintainer Проверь здоровье vault, синхронизируй дашборды и предложи точечные фиксы.`

Полный список ролей/команд: [`00_System/Agent-Commands.md`](00_System/Agent-Commands.md).

## Модель системы (коротко)
- **Notes**: `*/50_Notes/` — знания и разбор входящих.
- **Tasks**: `*/20_Tasks/` — 1 файл = 1 задача (минимум один чекбокс `- [ ]`).
- **Projects**: `*/30_Projects/` — outcome + автоподбор связанных задач.
- **Goals**: `*/60_Goals/` — горизонт/метрика + связанные проекты/задачи.
- Связи: в строках задач добавляй `[[WP-...]]` / `[[WG-...]]` (или personal‑аналог), чтобы страницы проектов/целей собирались автоматически.

Входящие материалы:
- складывай в `Work/00_Inbox/Incoming/` (или personal‑аналог);
- агент сначала делает заметку с `## Summary`, потом задаёт уточнения, и только затем создаёт задачи/проекты;
- исходники уходят в `*/99_Archive/Incoming/`.

## Tech‑ID / slug (важно)
- Язык tech-ID/slug задаётся в [`00_System/Vault-Config.env`](00_System/Vault-Config.env) (`VAULT_TECH_ID_LANGUAGE`).
- В этом vault установлен `русский`.
- Для ручного создания сущностей используй [`scripts/new-entity.sh`](scripts/new-entity.sh) (task/project/area/goal/note) — он применяет настройку автоматически.
- Если `healthcheck` предупреждает про англоязычный slug при режиме `русский`, создай файл через [`scripts/new-entity.sh`](scripts/new-entity.sh) (или переименуй по запросу).

## Куда смотреть дальше
- Первая настройка: [`00_System/Onboarding.md`](00_System/Onboarding.md)
- Bootstrap (первый запуск агента): [`00_System/Bootstrap.md`](00_System/Bootstrap.md)
- Runbook агента (протоколы/качество/архивирование): [`00_System/Agent-Runbook.md`](00_System/Agent-Runbook.md)
- Команды ролей: [`00_System/Agent-Commands.md`](00_System/Agent-Commands.md)
- Регламенты рутин: [`00_System/Routines.md`](00_System/Routines.md)

## Приватность
Не храните в репозитории пароли, токены, приватные ключи и клиентские секреты. Для чувствительных данных используйте менеджер секретов или шифрование вне этого репо.

#no-graph
