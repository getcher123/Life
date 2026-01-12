#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: process-incoming.sh [--domain work|personal] [--project [[W-PROJ-...]]]

Scans */00_Inbox/Incoming for binary files and converts:
  - .docx -> note via scripts/docx2note.sh (note only)
  - .pptx -> note via scripts/pptx2note.sh (note only)
  - .ogg/.mp3/.m4a/.wav/.flac/.opus -> note via scripts/audio2note.sh (note only)

Then moves processed source files into */99_Archive/Incoming/ with a timestamp prefix.
No tasks/projects are created by this script (confirmation step happens later).

Examples:
  scripts/process-incoming.sh --domain work
  scripts/process-incoming.sh --domain work --project [[W-PROJ-amway-malaysia-brochure]]
EOF
}

domain="work"
project_link=""

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
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 1
      ;;
  esac
done

case "$domain" in
  work) domain_dir="Work" ;;
  personal) domain_dir="Personal" ;;
  *)
    echo "Invalid --domain: $domain (use work|personal)" >&2
    exit 1
    ;;
esac

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INCOMING_DIR="$ROOT_DIR/${domain_dir}/00_Inbox/Incoming"
ARCHIVE_DIR="$ROOT_DIR/${domain_dir}/99_Archive/Incoming"

mkdir -p "$INCOMING_DIR" "$ARCHIVE_DIR"

shopt -s nullglob

processed=0
skipped=0
failed=0

while IFS= read -r -d '' file; do
  base="$(basename "$file")"
  ext="${base##*.}"
  ext="$(printf "%s" "$ext" | tr '[:upper:]' '[:lower:]')"

  cmd=()
  case "$ext" in
    docx)
      cmd=("$ROOT_DIR/scripts/docx2note.sh" "$file" "--domain" "$domain")
      ;;
    pptx)
      cmd=("$ROOT_DIR/scripts/pptx2note.sh" "$file" "--domain" "$domain")
      ;;
    ogg|mp3|m4a|wav|flac|opus)
      cmd=("$ROOT_DIR/scripts/audio2note.sh" "$file" "--domain" "$domain")
      ;;
    md)
      skipped=$((skipped + 1))
      continue
      ;;
    *)
      echo "SKIP (unsupported): $file" >&2
      skipped=$((skipped + 1))
      continue
      ;;
  esac

  if [[ -n "$project_link" ]]; then
    cmd+=("--project" "$project_link")
  fi

  if ! output="$("${cmd[@]}" 2>&1)"; then
    echo "FAIL: $file" >&2
    echo "$output" >&2
    failed=$((failed + 1))
    continue
  fi

  note_path="$(printf "%s\n" "$output" | rg '^  note: ' | sed 's/^  note: //')"
  ts="$(date +%Y%m%d-%H%M%S)"
  target="$ARCHIVE_DIR/${ts}__${base}"

  mv "$file" "$target"

  echo "OK: ${base}"
  echo "  note: ${note_path}"
  echo "  archived: ${target}"
  processed=$((processed + 1))
done < <(find "$INCOMING_DIR" -maxdepth 1 -type f -print0)

echo
echo "Done."
echo "  processed: ${processed}"
echo "  skipped:   ${skipped}"
echo "  failed:    ${failed}"
