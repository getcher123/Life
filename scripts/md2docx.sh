#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: md2docx.sh INPUT.md [OUTPUT.docx]

Converts a Markdown file to DOCX via pandoc. If OUTPUT.docx is omitted,
the DOCX file is written next to the input using the same basename.
EOF
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_PANDOC="$ROOT_DIR/.pandoc_local/bin/pandoc"

if command -v pandoc >/dev/null 2>&1; then
  PANDOC_BIN="pandoc"
elif [[ -x "$LOCAL_PANDOC" ]]; then
  PANDOC_BIN="$LOCAL_PANDOC"
else
  echo "pandoc is required but not found in PATH or .pandoc_local/bin." >&2
  exit 1
fi

input=$1
if [[ ! -f "$input" ]]; then
  echo "Input file '$input' not found." >&2
  exit 1
fi

if [[ $# -eq 2 ]]; then
  output=$2
else
  base=${input%.*}
  output="${base}.docx"
fi

mkdir -p "$(dirname "$output")"

"$PANDOC_BIN" "$input" \
  --from=gfm \
  --to=docx \
  --resource-path="$(dirname "$input"):$ROOT_DIR" \
  --output="$output"

echo "Converted '$input' -> '$output'"

