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

task_files_count="$(find Personal/20_Tasks Work/20_Tasks -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')"
if [[ "$task_files_count" -gt 0 ]]; then
  missing_checkbox="$(rg -L --glob='P-T-*.md' --glob='W-T-*.md' '^- \\[[ xX]\\] ' Personal/20_Tasks Work/20_Tasks 2>/dev/null || true)"
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
