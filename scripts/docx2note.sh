#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: docx2note.sh INPUT.docx [--domain work|personal] [--project [[W-PROJ-...]]] [--note-file PATH] [--create-task] [--task-file PATH] [--force]

Converts a DOCX file to a Markdown note in the vault and creates (or links) a task
that references the note (optional).

Defaults:
  --domain work

Example:
  scripts/docx2note.sh "/mnt/c/Users/Ivan/Downloads/Contract.docx" --project [[W-PROJ-contract-...]]
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
LOCAL_PANDOC="$ROOT_DIR/.pandoc_local/bin/pandoc"

if command -v pandoc >/dev/null 2>&1; then
  PANDOC_BIN="pandoc"
elif [[ -x "$LOCAL_PANDOC" ]]; then
  PANDOC_BIN="$LOCAL_PANDOC"
else
  echo "pandoc is required but not found in PATH or .pandoc_local/bin." >&2
  echo "Install locally: scripts/setup-pandoc.sh 3.1.11" >&2
  exit 1
fi

today_iso="$(date +%F)"
today_compact="$(date +%Y%m%d)"

base="$(basename "$input")"
base_no_ext="${base%.*}"

slug_raw="$base_no_ext"
if command -v iconv >/dev/null 2>&1; then
  slug_raw="$(printf "%s" "$slug_raw" | iconv -c -f UTF-8 -t ASCII//TRANSLIT || printf "%s" "$slug_raw")"
fi
slug="$(printf "%s" "$slug_raw" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')"
if [[ -z "$slug" ]]; then
  slug="docx"
fi

note_name="${domain_prefix}-NOTE-docx-${today_compact}-${slug}"
note_path_default="${domain_dir}/50_Notes/${note_name}.md"

task_name_default="${domain_prefix}-T-${today_compact}-review-docx-${slug}"
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

tmp_md="$(mktemp)"
cleanup() { rm -f "$tmp_md"; }
trap cleanup EXIT

"$PANDOC_BIN" "$input" \
  --from=docx \
  --to=gfm \
  --wrap=preserve \
  --markdown-headings=setext \
  --output="$tmp_md"

mkdir -p "$(dirname "$note_path")" "$(dirname "$task_path")"

if [[ -f "$note_path" && "$force" != "1" ]]; then
  echo "Note already exists: $note_path" >&2
  echo "Use --note-file to choose a different filename or --force to overwrite." >&2
  exit 1
fi

{
  echo "---"
  echo "type: note"
  echo "domain: ${domain}"
  echo "created: ${today_iso}"
  echo "updated: ${today_iso}"
  echo "source_docx: \"${input}\""
  if [[ "${create_task}" == "1" ]]; then
    echo "task: \"${task_link}\""
  fi
  if [[ -n "${project_link}" ]]; then
    echo "project: \"${project_link}\""
  fi
  echo "tags:"
  echo "  - note"
  echo "  - docx"
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
  echo "- <1–5 буллетов: суть/сроки/обязательства/следующий шаг>"
  echo
  echo "---"
  echo
  cat "$tmp_md"
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
    echo "- [ ] Изучить DOCX: ${note_link} #task"
  } >"$task_path"
fi

echo "OK:"
echo "  note: $note_path"
if [[ "${create_task}" == "1" ]]; then
  echo "  task: $task_path"
fi
