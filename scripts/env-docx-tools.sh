#!/usr/bin/env bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_BIN="$ROOT_DIR/.pandoc_local/bin"

if [[ -d "$LOCAL_BIN" ]]; then
  export PATH="$LOCAL_BIN:$PATH"
fi

