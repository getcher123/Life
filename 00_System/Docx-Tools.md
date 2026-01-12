# DOCX ↔ Markdown tools (pandoc)

Этот vault содержит скрипты для конвертации DOCX ↔ Markdown через `pandoc`.

## 1) Инициализация (локальная установка pandoc в repo)

В WSL/Linux можно поставить `pandoc` локально (без установки в систему):

```bash
scripts/setup-pandoc.sh 3.1.11
```

`pandoc` будет установлен в `.pandoc_local/bin/pandoc` (папка игнорируется Git через `.gitignore`).

## 2) Конвертация

DOCX → Markdown:

```bash
scripts/docx2md.sh /path/to/input.docx [/path/to/output.md]
```

Markdown → DOCX:

```bash
scripts/md2docx.sh /path/to/input.md [/path/to/output.docx]
```

## 2.1) Intake в vault (DOCX → заметка + задача)

Если нужно, чтобы каждый DOCX попадал в vault как заметка и имел связанную задачу:

```bash
scripts/docx2note.sh "/path/to/input.docx"
```

Опционально можно привязать к проекту:

```bash
scripts/docx2note.sh "/path/to/input.docx" --project [[W-PROJ-...]]
```

Задачу создавать только после подтверждения (когда решено, что именно нужно сделать):

```bash
scripts/docx2note.sh "/path/to/input.docx" --create-task --project [[W-PROJ-...]]
```

## 3) PATH (опционально)

Если хочешь, чтобы `pandoc` (локальный) был доступен в текущей сессии:

```bash
source scripts/env-docx-tools.sh
pandoc --version
```
