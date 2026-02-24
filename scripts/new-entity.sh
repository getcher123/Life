#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/new-entity.sh --domain work|personal --type task|project|area|goal|note --title "Название"
                       [--date YYYY-MM-DD] [--slug CUSTOM-SLUG] [--path PATH] [--force]

Creates a new vault entity file from 00_System/Templates/* using the configured
tech-ID slug language from 00_System/Vault-Config.env (VAULT_TECH_ID_LANGUAGE).

Examples:
  scripts/new-entity.sh --domain work --type project --title "Поддержка рекламного контракта"
  scripts/new-entity.sh --domain personal --type task --title "Записаться к врачу" --date 2026-02-24
EOF
}

if [[ $# -eq 0 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

domain=""
entity_type=""
title=""
date_iso=""
custom_slug=""
custom_path=""
force="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain)
      domain="${2:-}"
      shift 2
      ;;
    --type)
      entity_type="${2:-}"
      shift 2
      ;;
    --title)
      title="${2:-}"
      shift 2
      ;;
    --date)
      date_iso="${2:-}"
      shift 2
      ;;
    --slug)
      custom_slug="${2:-}"
      shift 2
      ;;
    --path)
      custom_path="${2:-}"
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

[[ -n "$domain" ]] || { echo "--domain is required" >&2; exit 1; }
[[ -n "$entity_type" ]] || { echo "--type is required" >&2; exit 1; }
[[ -n "$title" ]] || { echo "--title is required" >&2; exit 1; }

if [[ -z "$date_iso" ]]; then
  date_iso="$(date +%F)"
elif ! [[ "$date_iso" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "Invalid --date format: $date_iso (expected YYYY-MM-DD)" >&2
  exit 1
fi

case "$domain" in
  work) domain_dir="Work"; domain_word="Work"; domain_prefix="W" ;;
  personal) domain_dir="Personal"; domain_word="Personal"; domain_prefix="P" ;;
  *)
    echo "Invalid --domain: $domain (use work|personal)" >&2
    exit 1
    ;;
esac

case "$entity_type" in
  task)
    type_letter="T"
    folder="20_Tasks"
    template_name="Task - ${domain_word}.md"
    include_date_suffix="1"
    ;;
  project)
    type_letter="P"
    folder="30_Projects"
    template_name="Project - ${domain_word}.md"
    include_date_suffix="0"
    ;;
  area)
    type_letter="A"
    folder="40_Areas"
    template_name="Area - ${domain_word}.md"
    include_date_suffix="0"
    ;;
  note)
    type_letter="N"
    folder="50_Notes"
    template_name="Note - ${domain_word}.md"
    include_date_suffix="1"
    ;;
  goal)
    type_letter="G"
    folder="60_Goals"
    template_name="Goal - ${domain_word}.md"
    include_date_suffix="0"
    ;;
  *)
    echo "Invalid --type: $entity_type (use task|project|area|goal|note)" >&2
    exit 1
    ;;
esac

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

template_path="00_System/Templates/${template_name}"
if [[ ! -f "$template_path" ]]; then
  echo "Template not found: $template_path" >&2
  exit 1
fi

source "$ROOT_DIR/scripts/lib_vault_naming.sh"
vault_load_naming_config "$ROOT_DIR"

if [[ -n "$custom_slug" ]]; then
  slug="$custom_slug"
else
  slug="$(vault_slugify_tech_id "$title" "$entity_type")"
fi

if [[ "$include_date_suffix" == "1" ]]; then
  file_stem="${domain_prefix}${type_letter}-${slug}-${date_iso}"
else
  file_stem="${domain_prefix}${type_letter}-${slug}"
fi

if [[ -n "$custom_path" ]]; then
  out_path="$custom_path"
else
  out_path="${domain_dir}/${folder}/${file_stem}.md"
fi

mkdir -p "$(dirname "$out_path")"

if [[ -f "$out_path" && "$force" != "1" ]]; then
  echo "File already exists: $out_path" >&2
  echo "Use --force to overwrite or --path to choose another file." >&2
  exit 1
fi

tmp_out="$(mktemp)"
cleanup() { rm -f "$tmp_out"; }
trap cleanup EXIT

escape_sed_repl() {
  printf "%s" "$1" | sed -e 's/[&|\\]/\\&/g'
}

title_esc="$(escape_sed_repl "$title")"
date_esc="$(escape_sed_repl "$date_iso")"

sed -E \
  -e "s|\\{\\{date:YYYY-MM-DD\\}\\}|${date_esc}|g" \
  -e "0,/^# <[^>]+>$/s|^# <[^>]+>$|# ${title_esc}|" \
  "$template_path" >"$tmp_out"

cp "$tmp_out" "$out_path"

entity_link="[[${file_stem}|${title}]]"

echo "Created: ${out_path}"
echo "Link: ${entity_link}"
echo "Template: ${template_name}"
echo "tech-id-language: ${VAULT_TECH_ID_LANGUAGE}"

