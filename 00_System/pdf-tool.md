# PDF → JSON + Markdown (OCR)

Скрипт `scripts/pdf_to_json_pipeline.py` извлекает содержимое PDF через vision‑модель и сохраняет:
- `pdf_pages_combined.json` (объединённый результат по всем страницам),
- опционально — `pdf_page_0001.json`, `pdf_page_0002.json` и т.д. (`--save-pages`),
- опционально — `pdf_pages_combined.md` (OCR‑Markdown, `--emit-md`).

Результаты создаются **в подпапке рядом с PDF**:
`<pdf>_results/pdf_pages_combined.json` (и `pdf_pages_combined.md`, если включён `--emit-md`).

## Правило для входного PDF
При создании заметки из PDF **все артефакты** храним в `*/90_Assets/<note-slug>/`:
1) Исходный PDF копируем в `Work/90_Assets/<note-slug>/` или `Personal/90_Assets/<note-slug>/`.
2) JSON и картинки страниц остаются в подпапке рядом с PDF: `<pdf>_results/.../pdf_pages_combined.json`.
3) Markdown превращаем в заметку `.md` в нужном домене (`Work/50_Notes/` или `Personal/50_Notes/`).
4) В заметке обязательно добавляем ссылку на JSON‑файл.
5) Текстовый OCR (`--emit-text`) **не используем**.

## Использование

Перед запуском скопируй PDF в `Work/90_Assets/<note-slug>/` или `Personal/90_Assets/<note-slug>/`.

```bash
python scripts/pdf_to_json_pipeline.py -i Work/90_Assets/<note-slug>/file.pdf --emit-md
```

Опционально сохранить JSON по каждой странице:

```bash
python scripts/pdf_to_json_pipeline.py -i Work/90_Assets/<note-slug>/file.pdf --save-pages
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
- Для заметки используй ссылку на JSON, например: `[[Work/90_Assets/<note-slug>/<pdf>_results/.../pdf_pages_combined.json|pdf_pages_combined.json]]`.

#no-graph
