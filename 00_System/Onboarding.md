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
4. Открой стартовые страницы:
   - `INDEX.md`
   - `Personal/00_Home.md`
   - `Work/00_Home.md`
5. Быстрая проверка работоспособности:
   - `Work/20_Tasks/00_Taskboard.md` должен показывать секции задач (после появления задач с датами).
   - `Work/30_Projects/00_Projects.md` должен показывать таблицу проектов (после появления проектов).

## 3) Первая “живая” запись (рекомендуемый минимум)
1. Создай 1 область (area):
   - файл в `Work/40_Areas/` по шаблону `Area - Work` (или personal‑аналог).
2. Создай 1 цель (goal):
   - файл в `Work/60_Goals/` по шаблону `Goal - Work`.
3. Создай 1 проект (project) под эту цель:
   - файл в `Work/30_Projects/` по шаблону `Project - Work`;
   - в frontmatter проекта укажи `goal: [[WG-...]]` и (если нужно) `area: [[WA-...]]`.
4. Создай 3–5 задач под проект:
   - файлы в `Work/20_Tasks/` по шаблону `Task - Work`;
   - в строке задачи добавь ссылку на проект/цель: `[[WP-...]] [[WG-...]]`;
   - (по необходимости) добавь `📅 YYYY-MM-DD` и/или `⏳ YYYY-MM-DD`.
5. Проверь страницу проекта: блок `Tasks (open)` должен подтянуть задачи автоматически.

## 4) Правила безопасности и приватности
- Не храни в репозитории пароли/токены/ключи/персональные данные клиентов.
- Если нужно хранить чувствительное — вынеси в отдельное хранилище или шифруй вне репо.

#no-graph
