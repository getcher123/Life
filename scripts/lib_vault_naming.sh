#!/usr/bin/env bash
set -euo pipefail

vault_load_naming_config() {
  local root_dir="${1:?root dir is required}"
  local config_file="$root_dir/00_System/Vault-Config.env"

  if [[ -f "$config_file" ]]; then
    # shellcheck disable=SC1090
    source "$config_file"
  fi

  case "${VAULT_TECH_ID_LANGUAGE:-english}" in
    ru|russian|русский|рус)
      VAULT_TECH_ID_LANGUAGE="ru"
      ;;
    en|english|английский|англ)
      VAULT_TECH_ID_LANGUAGE="en"
      ;;
    *)
      VAULT_TECH_ID_LANGUAGE="en"
      ;;
  esac

  export VAULT_TECH_ID_LANGUAGE
}

vault_slugify_tech_id() {
  local value="${1:-}"
  local fallback="${2:-item}"

  if [[ "${VAULT_TECH_ID_LANGUAGE:-en}" == "ru" ]]; then
    if ! command -v python3 >/dev/null 2>&1; then
      echo "python3 is required for VAULT_TECH_ID_LANGUAGE=русский" >&2
      return 1
    fi

    python3 - "$value" "$fallback" <<'PY'
import re
import sys

value = (sys.argv[1] or "").strip().lower()
fallback = sys.argv[2]

slug = re.sub(r"[^0-9a-zа-яё]+", "-", value, flags=re.IGNORECASE)
slug = re.sub(r"-{2,}", "-", slug).strip("-")

print(slug or fallback)
PY
    return 0
  fi

  local slug_raw="$value"
  if command -v iconv >/dev/null 2>&1; then
    slug_raw="$(printf "%s" "$slug_raw" | iconv -c -f UTF-8 -t ASCII//TRANSLIT || printf "%s" "$slug_raw")"
  fi
  local slug
  slug="$(printf "%s" "$slug_raw" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')"
  printf "%s\n" "${slug:-$fallback}"
}

