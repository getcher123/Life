# Incoming materials (Personal)

Сюда складываются входящие **не‑md** файлы (DOCX/PPTX/PDF/аудио/XLSX/CSV/изображения) для разбора агентом.
Канонический формат в vault — `.md`; не‑md файлы считаются источниками/артефактами.

Протокол:
1) ты кладёшь файлы в `Personal/00_Inbox/Incoming/` (они не коммитятся в Git);
2) агент конвертирует файлы в заметки `Personal/50_Notes/` (с `## Summary`);
3) агент задаёт уточняющие вопросы и **только после подтверждения** создаёт задачи/проекты;
4) исходники перемещаются в `Personal/99_Archive/Incoming/` (вместо удаления).

Экспорт наружу (DOCX/PDF) делается из `.md` и хранится в `Personal/50_Notes/Exports/` или в `Personal/90_Assets/` для проектных артефактов.

Команда агента:
- `scripts/process-incoming.sh --domain personal`

#no-graph
