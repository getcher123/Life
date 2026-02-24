# Onboarding (первая настройка)

Если вы подключаете AI‑агента: начните с `00_System/Bootstrap.md` и промпта `00_System/Prompts/Bootstrapper.md`.

## 1) Подготовка репозитория (Git)
1. Убедись, что это Git‑репозиторий: `git status`.
2. Задай имя и email (один раз на машине):
   - `git config --global user.name "Your Name"`
   - `git config --global user.email "you@example.com"`
3. Сделай первый коммит каркаса (если ещё не сделано):
   - `git add -A`
   - `git commit -m "Init vault scaffold"`
4. (Опционально) Подключи удалённый репозиторий:
   - `git remote add origin <url>`
   - `git push -u origin main`

## 2) Подключение Obsidian
1. Открой папку репозитория как vault: `Open folder as vault`.
2. Включи core‑плагин Templates и укажи папку: `00_System/Templates` (см. `.obsidian/templates.json`).
3. Установи community‑плагины (минимум):
   - Dataview
   - Tasks
4. (Рекомендуется для удобства) настрой UI:
   - `Show inline title = Off` (меньше техназваний вверху заметок)
   - `Properties in document = Collapsed` или `Hidden`
   - inline‑панели `Backlinks` / `Outgoing links` в документе — сверни или выключи (меньше визуального шума)
   - если включён breadcrumbs/путь вверху заметки — отключи, чтобы не видеть техназвания файлов
   - проверь, что общий граф использует фильтр из `.obsidian/graph.json` (скрывает архив/тех‑узлы)
   - при необходимости в Graph view дополнительно скрой `tags`/`attachments`
5. Открой стартовые страницы:
   - `INDEX.md`
   - `Personal/00_Home.md`
   - `Work/00_Home.md`
6. Быстрая проверка работоспособности:
   - `Work/20_Tasks/00_Taskboard.md` должен показывать секции задач (после появления задач с датами).
   - `Work/30_Projects/00_Projects.md` должен показывать таблицу проектов (после появления проектов).

## 2.1) Локальная среда для скриптов (опционально, но полезно)
1. Базовая проверка структуры:
   - `bash scripts/healthcheck.sh`
2. Для работы с DOCX/PPTX (через `pandoc`):
   - если `pandoc` не установлен, поставить локально: `scripts/setup-pandoc.sh`
3. Для распознавания аудио:
   - создай локальный `.env` (не коммитить);
   - добавь `OPENAI_API_KEY=...`
4. Для авторазбора входящих:
   - используй `scripts/process-incoming.sh --domain work` (или `personal`)
5. Для именования новых сущностей:
   - язык tech-ID/slug задаётся в `00_System/Vault-Config.env` (`VAULT_TECH_ID_LANGUAGE`); в этом vault — `русский`
   - для ручного создания файлов (task/project/area/goal/note) используй `scripts/new-entity.sh`, чтобы slug соответствовал настройке
6. Если работаешь из WSL:
   - путь вида `C:\\...` в WSL доступен как `/mnt/c/...`
   - сам vault обычно открыт как `/mnt/c/Life` (или ваш путь)

## 3) Первая “живая” запись (рекомендуемый минимум)
1. Создай 1 область (area):
   - файл в `Work/40_Areas/` по шаблону `Area - Work` (или personal‑аналог); предпочтительно через `scripts/new-entity.sh`.
2. Создай 1 цель (goal):
   - файл в `Work/60_Goals/` по шаблону `Goal - Work` (лучше через `scripts/new-entity.sh`).
3. Создай 1 проект (project) под эту цель:
   - файл в `Work/30_Projects/` по шаблону `Project - Work` (лучше через `scripts/new-entity.sh`);
   - в frontmatter проекта укажи `goal: [[WG-...]]` и (если нужно) `area: [[WA-...]]`.
4. Создай 3–5 задач под проект:
   - файлы в `Work/20_Tasks/` по шаблону `Task - Work` (лучше через `scripts/new-entity.sh`);
   - в строке задачи добавь ссылку на проект/цель: `[[WP-...]] [[WG-...]]`;
   - (по необходимости) добавь `📅 YYYY-MM-DD` и/или `⏳ YYYY-MM-DD`.
5. Проверь страницу проекта: блок `Tasks (open)` должен подтянуть задачи автоматически.

## 4) Правила безопасности и приватности
- Не храни в репозитории пароли/токены/ключи/персональные данные клиентов.
- Если нужно хранить чувствительное — вынеси в отдельное хранилище или шифруй вне репо.

## 5) Как запустить AI‑агента после настройки
1. Для первого запуска:
   - `@Bootstrapper Подключаюсь впервые, проверь настройку и проведи bootstrap`
2. Для обычной работы:
   - `@Assistant Выдай сводку по задачам и предложи фокус на сегодня`
3. Если запрос смешанный/непонятный:
   - `@Router Помоги выбрать роль и разложить запрос`
4. Для обслуживания репозитория:
   - `@Repo-Maintainer Проверь структуру, дашборды и healthcheck`

Список ролей и команд: `00_System/Agent-Commands.md`.

#no-graph
