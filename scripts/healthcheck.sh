#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

warn() {
  echo "WARN: $*" >&2
}

need_file() {
  [[ -f "$1" ]] || fail "missing file: $1"
}

need_dir() {
  [[ -d "$1" ]] || fail "missing dir: $1"
}

echo "== Life vault healthcheck =="

need_file "README.md"
need_file "AGENTS.md"
need_file "INDEX.md"

need_dir "00_System"
need_dir "00_System/Templates"
need_dir "00_System/Prompts"

need_file "00_System/Onboarding.md"
need_file "00_System/Agent-Runbook.md"
need_file "00_System/Routines.md"
need_file "00_System/Bootstrap.md"
need_file "00_System/Support.md"
need_file "00_System/Vault-Config.env"

need_dir "Personal"
need_dir "Work"

for domain in Personal Work; do
  need_dir "$domain/00_Inbox"
  need_dir "$domain/10_Daily"
  need_dir "$domain/20_Tasks"
  need_dir "$domain/30_Projects"
  need_dir "$domain/40_Areas"
  need_dir "$domain/50_Notes"
  need_dir "$domain/60_Goals"
  need_dir "$domain/70_Reviews"
  need_dir "$domain/90_Assets"
  need_dir "$domain/99_Archive"
  need_file "$domain/00_Home.md"
  need_file "$domain/20_Tasks/00_Taskboard.md"
done

need_dir ".obsidian"
need_file ".obsidian/templates.json"
need_file ".obsidian/community-plugins.json"

if ! grep -q '"dataview"' ".obsidian/community-plugins.json"; then
  warn "Dataview not listed in .obsidian/community-plugins.json"
fi
if ! grep -q '"obsidian-tasks-plugin"' ".obsidian/community-plugins.json"; then
  warn "Tasks not listed in .obsidian/community-plugins.json"
fi
if ! grep -q '"obsidian-kanban"' ".obsidian/community-plugins.json"; then
  warn "Kanban not listed in .obsidian/community-plugins.json"
fi

source "scripts/lib_vault_naming.sh"
vault_load_naming_config "$(pwd)"

if [[ "${VAULT_TECH_ID_LANGUAGE:-en}" == "ru" ]] && command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  declare -A recent_entity_candidates=()
  declare -A git_added_entity_candidates=()
  russian_title_with_latin_id=()
  today_iso="$(date +%F)"
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    path=""
    case "${line:0:2}" in
      "??")
        path="${line:3}"
        ;;
      "A " | "A?")
        path="${line:3}"
        ;;
      *)
        continue
        ;;
    esac

    recent_entity_candidates["$path"]=1
    git_added_entity_candidates["$path"]=1
  done < <(git status --porcelain 2>/dev/null || true)

  while IFS= read -r path; do
    [[ -n "$path" ]] || continue
    recent_entity_candidates["$path"]=1
  done < <(find Work Personal \
    \( -path '*/20_Tasks/*' -o -path '*/30_Projects/*' -o -path '*/40_Areas/*' -o -path '*/50_Notes/*' -o -path '*/60_Goals/*' \) \
    -type f -name '*.md' -mmin -180 2>/dev/null || true)

  for path in "${!recent_entity_candidates[@]}"; do
    [[ -f "$path" ]] || continue
    [[ "$path" =~ ^(Work|Personal)/(20_Tasks|30_Projects|40_Areas|50_Notes|60_Goals)/[WP][TPANG]-.+\.md$ ]] || continue

    if [[ -z "${git_added_entity_candidates[$path]:-}" ]]; then
      created_value="$(sed -n 's/^created:[[:space:]]*//p' "$path" | head -n 1 || true)"
      [[ "$created_value" == "$today_iso" ]] || continue
    fi

    base_no_ext="$(basename "$path" .md)"
    slug_tail="${base_no_ext#??-}"

    if ! [[ "$slug_tail" =~ ^[a-z0-9-]+$ ]]; then
      continue
    fi

    heading="$(sed -n 's/^# //p' "$path" | head -n 1 || true)"
    if printf "%s" "$heading" | LC_ALL=C grep -q $'[\320\321]'; then
      russian_title_with_latin_id+=("$path")
    fi
  done

  if [[ "${#russian_title_with_latin_id[@]}" -gt 0 ]]; then
    {
      echo "Detected new entity files with Latin-only tech-ID slug while VAULT_TECH_ID_LANGUAGE=русский:"
      printf '  - %s\n' "${russian_title_with_latin_id[@]}"
      echo "Use: scripts/new-entity.sh --domain ... --type ... --title \"...\""
      echo "(warning only; false positives are possible for intentionally English-only titles)"
    } >&2
    warn "new entity filenames may ignore VAULT_TECH_ID_LANGUAGE=русский"
  fi
fi

task_files_count="$(find Personal/20_Tasks Work/20_Tasks -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')"
if [[ "$task_files_count" -gt 0 ]]; then
  missing_checkbox="$(rg -L --glob='PT-*.md' --glob='WT-*.md' '^- \\[[ xX]\\] ' Personal/20_Tasks Work/20_Tasks 2>/dev/null || true)"
  if [[ -n "${missing_checkbox}" ]]; then
    echo "$missing_checkbox" | sed 's/^/  - /' >&2
    fail "some task files have no Tasks checkbox lines (need at least one '- [ ]')"
  fi
fi

if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  name="$(git config user.name || true)"
  email="$(git config user.email || true)"
  if [[ -z "${name}" || -z "${email}" ]]; then
    warn "git user.name/user.email not set (commits may fail)"
  fi
else
  warn "not a git repo (git init missing?)"
fi

echo "OK: basic structure looks good."
