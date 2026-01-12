#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: setup-pandoc.sh [VERSION]

Downloads a pandoc release and installs it locally into .pandoc_local/bin/pandoc
so conversion scripts can run without a system-wide pandoc install.

Examples:
  scripts/setup-pandoc.sh 3.1.11
  PANDOC_VERSION=3.1.11 scripts/setup-pandoc.sh
EOF
}

version="${1:-${PANDOC_VERSION:-}}"
if [[ -z "${version}" ]]; then
  usage
  exit 1
fi

uname_s="$(uname -s)"
if [[ "${uname_s}" != "Linux" ]]; then
  echo "This installer currently supports Linux/WSL only. Install pandoc via your OS package manager." >&2
  exit 1
fi

arch="$(uname -m)"
case "${arch}" in
  x86_64) platform="linux-amd64" ;;
  aarch64|arm64) platform="linux-arm64" ;;
  *)
    echo "Unsupported architecture: ${arch}" >&2
    exit 1
    ;;
esac

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="$ROOT_DIR/.pandoc_local/bin"
mkdir -p "$TARGET_DIR"

tmp_dir="$(mktemp -d)"
cleanup() { rm -rf "$tmp_dir"; }
trap cleanup EXIT

archive="pandoc-${version}-${platform}.tar.gz"
url="https://github.com/jgm/pandoc/releases/download/${version}/${archive}"

if command -v curl >/dev/null 2>&1; then
  curl -fsSL -o "$tmp_dir/$archive" "$url"
elif command -v wget >/dev/null 2>&1; then
  wget -O "$tmp_dir/$archive" "$url"
else
  echo "Need curl or wget to download pandoc." >&2
  exit 1
fi

tar -xzf "$tmp_dir/$archive" -C "$tmp_dir"

src_bin="$tmp_dir/pandoc-${version}/bin/pandoc"
if [[ ! -x "$src_bin" ]]; then
  src_bin="$tmp_dir/pandoc-${version}/pandoc"
fi
if [[ ! -x "$src_bin" ]]; then
  echo "Could not find pandoc in extracted archive." >&2
  exit 1
fi

install -m 0755 "$src_bin" "$TARGET_DIR/pandoc"

echo "OK: installed $TARGET_DIR/pandoc"
echo "Try: $TARGET_DIR/pandoc --version"

