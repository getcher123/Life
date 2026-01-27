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

Правило: **никогда не хранить** JSON сервисного аккаунта (private key) в Git/Markdown‑заметках. Держим локально в `Work/00_Inbox/Private/`.

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

## Примечания
- По умолчанию креды читаются из `Work/00_Inbox/Private/google-service-account.json` или из переменной `GSHEETS_SERVICE_ACCOUNT_JSON`.
- Если прав у сервисного аккаунта нет — будет `403` (нужно расшарить таблицу на `client_email`).

#no-graph

