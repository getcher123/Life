# PDF → страницы → JSON

Скрипт `scripts/pdf_to_json_pipeline.py` извлекает содержимое PDF через vision‑модель и сохраняет:
- `pdf_pages_combined.json` (объединённый результат по всем страницам),
- опционально — `pdf_page_0001.json`, `pdf_page_0002.json` и т.д. (`--save-pages`).

Результаты создаются **в подпапке рядом с PDF**:
`<pdf>_results/pdf_pages_combined.json`.

## Использование

Перед запуском скопируй PDF внутрь проекта (например, в `tmp/`).

```bash
python scripts/pdf_to_json_pipeline.py -i tmp/file.pdf
```

Опционально сохранить JSON по каждой странице:

```bash
python scripts/pdf_to_json_pipeline.py -i tmp/file.pdf --save-pages
```

## Настройки

Используются переменные из `.env`:
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_VISION_MODEL`
- `POPPLER_PATH` (если нужен внешний Poppler)

## Примечания

- Для Windows‑Poppler в WSL путь к PDF конвертируется автоматически.
- `--results-dir` задаёт подпапку **внутри папки PDF**.
