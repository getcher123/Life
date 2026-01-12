#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: pptx2note.sh INPUT.pptx [--domain work|personal] [--project [[W-PROJ-...]]] [--note-file PATH] [--force]

Extracts text from a PPTX and creates a Markdown note in */50_Notes/ with:
  - Summary placeholder
  - Slide-by-slide outline
  - Extracted text
  - Simple keyword list

This script creates a note first (no tasks/projects are created here).

Example:
  scripts/pptx2note.sh "/mnt/c/Users/Ivan/Downloads/deck.pptx" --domain work
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
note_file=""
force="0"

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
    --note-file)
      note_file="${2:-}"
      shift 2
      ;;
    --force)
      force="1"
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

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but not found." >&2
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
  slug="pptx"
fi

note_name="${domain_prefix}-NOTE-pptx-${today_compact}-${slug}"
note_path_default="${domain_dir}/50_Notes/${note_name}.md"

if [[ -n "$note_file" ]]; then
  note_path="$note_file"
  note_name="$(basename "$note_path" .md)"
else
  note_path="$note_path_default"
fi

mkdir -p "$(dirname "$note_path")"

if [[ -f "$note_path" && "$force" != "1" ]]; then
  echo "Note already exists: $note_path" >&2
  echo "Use --note-file to choose a different filename or --force to overwrite." >&2
  exit 1
fi

tmp_json="$(mktemp)"
cleanup() { rm -f "$tmp_json"; }
trap cleanup EXIT

python3 - "$input" >"$tmp_json" <<'PY'
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

pptx_path = sys.argv[1]

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}

def extract_slide_text(xml_bytes: bytes) -> str:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return ""
    texts = []
    for t in root.findall(".//a:t", NS):
        if t.text:
            texts.append(t.text)
    text = "\n".join(texts)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text

with zipfile.ZipFile(pptx_path) as z:
    slide_names = [n for n in z.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
    def slide_key(name: str):
        m = re.search(r"slide(\d+)\.xml$", name)
        return int(m.group(1)) if m else 0
    slide_names.sort(key=slide_key)

    slides = []
    all_text_parts = []
    for name in slide_names:
        num = slide_key(name)
        text = extract_slide_text(z.read(name))
        slides.append({"n": num, "text": text})
        if text:
            all_text_parts.append(text)

all_text = "\n\n".join(all_text_parts).strip()

stop = {
    "и","в","во","на","но","а","что","это","как","к","ко","по","из","за","для","у","о","об","от","до","при","же","ли",
    "мы","вы","он","она","они","я","ты","там","тут","то","так","же","не","да","нет","или","либо","уже","еще","ещё",
    "с","со","без","над","под","про","при","если","чтобы","где","когда","почему","какой","какая","какие","какого",
}

words = re.findall(r"[A-Za-zА-Яа-яЁё0-9]{3,}", all_text.lower())
freq = {}
for w in words:
    if w in stop:
        continue
    if w.isdigit():
        continue
    freq[w] = freq.get(w, 0) + 1

keywords = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:20]

out = {
    "slides_count": len(slides),
    "slides": slides,
    "keywords": keywords,
}
print(json.dumps(out, ensure_ascii=False))
PY

slides_count="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["slides_count"])' <"$tmp_json")"

{
  echo "---"
  echo "type: note"
  echo "domain: ${domain}"
  echo "created: ${today_iso}"
  echo "updated: ${today_iso}"
  echo "source_pptx: \"${input}\""
  if [[ -n "${project_link}" ]]; then
    echo "project: \"${project_link}\""
  fi
  echo "tags:"
  echo "  - note"
  echo "  - pptx"
  echo "---"
  echo
  echo "# ${base_no_ext}"
  echo
  echo "- Источник: \`${input}\`"
  if [[ -n "${project_link}" ]]; then
    echo "- Проект: ${project_link}"
  fi
  echo "- Слайдов: ${slides_count}"
  echo
  echo "## Summary"
  echo
  echo "- <1–5 буллетов: суть/цель/сроки/следующий шаг>"
  echo
  echo "## Outline"
  echo
  python3 - "$tmp_json" <<'PY'
import json,sys
data=json.load(open(sys.argv[1], "r", encoding="utf-8"))
for s in data["slides"]:
    text=(s.get("text") or "").strip()
    if not text:
        print(f"- Slide {s['n']}: (no text)")
        continue
    first = text.splitlines()[0].strip()
    if len(first) > 120:
        first = first[:117] + "..."
    print(f"- Slide {s['n']}: {first}")
PY
  echo
  echo "## Keywords"
  echo
  python3 - "$tmp_json" <<'PY'
import json,sys
data=json.load(open(sys.argv[1], "r", encoding="utf-8"))
kw=data["keywords"]
if not kw:
    print("- (no keywords)")
else:
    print("- " + ", ".join([f"{w}({c})" for w,c in kw]))
PY
  echo
  echo "## Extracted Text"
  echo
  python3 - "$tmp_json" <<'PY'
import json,sys
data=json.load(open(sys.argv[1], "r", encoding="utf-8"))
for s in data["slides"]:
    print(f"### Slide {s['n']}")
    text=(s.get("text") or "").strip()
    print(text if text else "(no text)")
    print()
PY
} >"$note_path"

echo "OK:"
echo "  note: $note_path"
