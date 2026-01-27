#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

install_target="user site-packages"

if python3 -m venv .venv >/dev/null 2>&1; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
  install_target=".venv"
else
  echo "WARN: python3-venv is missing; installing deps into user site-packages instead." >&2
  echo "Tip (Ubuntu/WSL): sudo apt install python3-venv" >&2
fi

python3 -m pip install --upgrade pip
python3 -m pip install "gspread>=6" "google-auth>=2"

echo "OK: gsheets deps installed in ${install_target}"
