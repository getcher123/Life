---
type: system
status: active
created: 2026-01-27
updated: 2026-01-27
tags:
  - system
  - tools
---

# Google Sheets tools (service account)

Инструмент для чтения Google Sheets через **service account** (без браузера), чтобы агент мог:
- забирать данные заказов/лидов из таблиц;
- делать сводки/проверки/валидацию;
- превращать строки в заметки/задачи (только после подтверждения пользователя).

Правило безопасности: **никогда не хранить** JSON сервисного аккаунта (private key) в Git/Markdown‑заметках. Держим локально в `Work/00_Inbox/Private/` (gitignored).

## Что делает
- Скрипт: `scripts/gsheets_fetch.py`
- Вход: ссылка на Google Sheet (или spreadsheet id) + `gid` листа
- Выход: данные таблицы (JSON или TSV) для дальнейшей обработки

По умолчанию используются read‑only права (`spreadsheets.readonly`).

## Подготовка (1 раз)
1) Создай файл `Work/00_Inbox/Private/google-service-account.json` и вставь туда JSON сервисного аккаунта.  
   - Этот файл gitignored.
2) Убедись, что Google‑таблица расшарена на `client_email` из JSON (Viewer/Editor — по задаче).
3) Установи зависимости:
```bash
./scripts/setup-gsheets.sh
```

## Быстрый тест доступа
```bash
./scripts/gsheets_fetch.py \
  --sheet-url "<google-sheet-url>" \
  --gid 798172472 \
  --limit 5
```

## Параметры
- `--sheet-url` — URL таблицы или `spreadsheet_id`
- `--gid` — id листа (можно не указывать, если он есть в URL)
- `--format json|tsv` — формат вывода (по умолчанию `json`)
- `--tail N` — последние N строк (без заголовка)
- `--find "<text>"` — найти строки по подстроке (можно несколько раз, логика OR)
- `--column "<header>"|<index>` — ограничить поиск одной колонкой (имя из шапки или 0‑индекс)
- `--as-objects` — вернуть строки как объекты `{header: value}` (только JSON)
- `--creds <path>` — путь к JSON (если не стандартный)
- `GSHEETS_SERVICE_ACCOUNT_JSON` — альтернатива `--creds`

## Примечания
- По умолчанию креды читаются из `Work/00_Inbox/Private/google-service-account.json` или из переменной `GSHEETS_SERVICE_ACCOUNT_JSON`.
- Если прав у сервисного аккаунта нет — будет `403` (нужно расшарить таблицу на `client_email`).
- Если `python3-venv` недоступен, `scripts/setup-gsheets.sh` ставит зависимости в user site‑packages.

#no-graph
