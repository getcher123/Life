#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: audio2note.sh INPUT_AUDIO [--domain work|personal] [--project [[WP-...]]] [--note-file PATH] [--create-task] [--task-file PATH] [--force]

Transcribes an audio file (ogg/mp3/wav/m4a/...) via OpenAI Whisper API and writes:
  - a note in */50_Notes/ (always)
  - optionally a linked task in */20_Tasks/ (--create-task)

Requires OPENAI_API_KEY in environment or in repo .env (ignored by git).

Example:
  scripts/audio2note.sh "/mnt/c/Users/Ivan/Downloads/audio.ogg"
  scripts/audio2note.sh "/mnt/c/Users/Ivan/Downloads/audio.ogg" --create-task --project [[WP-...]]
EOF
}

if [[ $# -lt 1 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

input="$1"
shift

domain="work"
project_link=""
task_file=""
note_file=""
force="0"
create_task="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain)
      domain="${2:-}"
      shift 2
      ;;
    --project)
      project_link="${2:-}"
      shift 2
      ;;
    --task-file)
      task_file="${2:-}"
      shift 2
      ;;
    --note-file)
      note_file="${2:-}"
      shift 2
      ;;
    --force)
      force="1"
      shift 1
      ;;
    --create-task)
      create_task="1"
      shift 1
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ ! -f "$input" ]]; then
  echo "Input file not found: $input" >&2
  exit 1
fi

case "$domain" in
  work) domain_dir="Work"; domain_prefix="W" ;;
  personal) domain_dir="Personal"; domain_prefix="P" ;;
  *)
    echo "Invalid --domain: $domain (use work|personal)" >&2
    exit 1
    ;;
esac

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT_DIR/scripts/lib_vault_naming.sh"
vault_load_naming_config "$ROOT_DIR"

load_api_key_from_dotenv() {
  local env_file="$ROOT_DIR/.env"
  [[ -f "$env_file" ]] || return 1
  local line
  line="$(rg -n '^OPENAI_API_KEY=' "$env_file" 2>/dev/null | head -n 1 | cut -d: -f2- || true)"
  [[ -n "$line" ]] || return 1
  line="${line#OPENAI_API_KEY=}"
  line="${line%$'\r'}"
  line="${line%\"}"
  line="${line#\"}"
  export OPENAI_API_KEY="$line"
}

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  load_api_key_from_dotenv || true
fi
if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "OPENAI_API_KEY is missing. Put it in environment or in $ROOT_DIR/.env" >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required but not found." >&2
  exit 1
fi
if ! command -v rg >/dev/null 2>&1; then
  echo "ripgrep (rg) is required but not found." >&2
  exit 1
fi

today_iso="$(date +%F)"
today_filename="$today_iso"

base="$(basename "$input")"
base_no_ext="${base%.*}"

slug="$(vault_slugify_tech_id "$base_no_ext" "audio")"

note_name="${domain_prefix}N-audio-${slug}-${today_filename}"
note_path_default="${domain_dir}/50_Notes/${note_name}.md"

task_name_default="${domain_prefix}T-process-audio-${slug}-${today_filename}"
task_path_default="${domain_dir}/20_Tasks/${task_name_default}.md"

if [[ -n "$note_file" ]]; then
  note_path="$note_file"
  note_name="$(basename "$note_path" .md)"
else
  note_path="$note_path_default"
fi

if [[ -n "$task_file" ]]; then
  task_path="$task_file"
  task_name="$(basename "$task_path" .md)"
else
  task_path="$task_path_default"
  task_name="$task_name_default"
fi

note_link="[[${note_name}]]"
task_link="[[${task_name}]]"

mkdir -p "$(dirname "$note_path")" "$(dirname "$task_path")"

if [[ -f "$note_path" && "$force" != "1" ]]; then
  echo "Note already exists: $note_path" >&2
  echo "Use --note-file to choose a different filename or --force to overwrite." >&2
  exit 1
fi

transcript="$(curl -fsS \
  -H "Authorization: Bearer ${OPENAI_API_KEY}" \
  -H "Accept: text/plain" \
  -F "file=@${input}" \
  -F "model=whisper-1" \
  -F "language=ru" \
  -F "response_format=text" \
  "https://api.openai.com/v1/audio/transcriptions")"

{
  echo "---"
  echo "type: note"
  echo "domain: ${domain}"
  echo "created: ${today_iso}"
  echo "updated: ${today_iso}"
  echo "source_audio: \"${input}\""
  if [[ "${create_task}" == "1" ]]; then
    echo "task: \"${task_link}\""
  fi
  if [[ -n "${project_link}" ]]; then
    echo "project: \"${project_link}\""
  fi
  echo "tags:"
  echo "  - note"
  echo "  - audio"
  echo "---"
  echo
  echo "# ${base_no_ext}"
  echo
  echo "- Источник: \`${input}\`"
  if [[ "${create_task}" == "1" ]]; then
    echo "- Задача: ${task_link}"
  fi
  if [[ -n "${project_link}" ]]; then
    echo "- Проект: ${project_link}"
  fi
  echo
  echo "## Summary"
  echo
  echo "- <1–5 буллетов: суть/сроки/варианты/следующий шаг>"
  echo
  echo "## Transcript"
  echo
  printf "%s\n" "$transcript"
} >"$note_path"

if [[ "${create_task}" == "1" && ! -f "$task_path" ]]; then
  {
    echo "---"
    echo "type: task"
    echo "domain: ${domain}"
    echo "status: todo"
    echo "created: ${today_iso}"
    echo "updated: ${today_iso}"
    echo "note: \"${note_link}\""
    if [[ -n "${project_link}" ]]; then
      echo "project: \"${project_link}\""
    fi
    echo "tags:"
    echo "  - task"
    echo "---"
    echo
    echo "# Разобрать расшифровку аудио"
    echo
    echo "## Next step"
    echo "- [ ] Обработать расшифровку аудио: ${note_link} (выделить задачи/решения, разнести по проектам)"
    echo
    echo "- [ ] Подготовить разбор аудио и список задач/решений по ${note_link}"
    echo
    echo "## Checklist"
    echo "- [ ] Выделить задачи / решения / вопросы"
    echo "- [ ] Привязать к проектам/целям (при подтверждении пользователя)"
    echo
    echo "## Context / Links"
    echo "- Note: ${note_link}"
    if [[ -n "${project_link}" ]]; then
      echo "- Project: ${project_link}"
    fi
    echo
    echo "## Планирование (Tasks)"
    echo "Добавляй свойства в строку задачи по необходимости: ⏳ / 🛫 / 📅 / ✅."
  } >"$task_path"
fi

echo "OK:"
echo "  note: $note_path"
echo "  tech-id-language: ${VAULT_TECH_ID_LANGUAGE}"
if [[ "${create_task}" == "1" ]]; then
  echo "  task: $task_path"
fi
