#!/usr/bin/env python3
import argparse
import datetime as dt
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Rename:
    src: Path
    dst: Path
    old_base: str
    new_base: str


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(ROOT), check=False, text=True, capture_output=True)


def _is_tracked(path: Path) -> bool:
    rel = str(path.relative_to(ROOT))
    p = _run(["git", "ls-files", "--error-unmatch", rel])
    return p.returncode == 0


def _safe_slug(value: str) -> str:
    v = value.strip()
    v = re.sub(r"\s+", "-", v)
    v = re.sub(r"[^a-zA-Z0-9._-]+", "-", v)
    v = re.sub(r"-{2,}", "-", v).strip("-")
    return v or "item"


def _parse_frontmatter_created(md_path: Path) -> str | None:
    # Looks for:
    # ---
    # created: YYYY-MM-DD
    # ---
    try:
        text = md_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = md_path.read_text(encoding="utf-8", errors="ignore")

    if not text.startswith("---"):
        return None

    lines = text.splitlines()
    # Find closing ---
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return None

    for line in lines[1:end]:
        m = re.match(r"^\s*created:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*$", line)
        if m:
            return m.group(1)
    return None


def _date_from_yyyymmdd(yyyymmdd: str) -> str:
    return f"{yyyymmdd[0:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"


def _infer_date_for_note(md_path: Path) -> str:
    created = _parse_frontmatter_created(md_path)
    if created:
        return created
    # fallback: file mtime
    ts = md_path.stat().st_mtime
    return dt.date.fromtimestamp(ts).isoformat()


def _unique_dst(dst: Path) -> Path:
    if not dst.exists():
        return dst
    stem = dst.stem
    suffix = dst.suffix
    parent = dst.parent
    for i in range(2, 1000):
        candidate = parent / f"{stem}-{i}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find unique filename for: {dst}")


def _convert_basename(old_base: str, path: Path) -> str | None:
    # Tasks: W-T-YYYYMMDD-slug -> WT-slug-YYYY-MM-DD
    m = re.match(r"^([WP])-T-([0-9]{8})-(.+)$", old_base)
    if m:
        dom, yyyymmdd, slug = m.groups()
        date = _date_from_yyyymmdd(yyyymmdd)
        return f"{dom}T-{_safe_slug(slug)}-{date}"

    # Projects: W-PROJ-slug -> WP-slug
    m = re.match(r"^([WP])-PROJ-(.+)$", old_base)
    if m:
        dom, slug = m.groups()
        return f"{dom}P-{_safe_slug(slug)}"

    # Areas: W-AREA-slug -> WA-slug
    m = re.match(r"^([WP])-AREA-(.+)$", old_base)
    if m:
        dom, slug = m.groups()
        return f"{dom}A-{_safe_slug(slug)}"

    # Goals: W-GOAL-slug -> WG-slug
    m = re.match(r"^([WP])-GOAL-(.+)$", old_base)
    if m:
        dom, slug = m.groups()
        return f"{dom}G-{_safe_slug(slug)}"

    # Notes:
    # W-NOTE-docx-YYYYMMDD-slug -> WN-docx-slug-YYYY-MM-DD
    # W-NOTE-YYYYMMDD-slug -> WN-slug-YYYY-MM-DD
    # Otherwise: WN-<rest>-<created>
    m = re.match(r"^([WP])-NOTE-(.+)$", old_base)
    if m:
        dom, rest = m.groups()
        rest = rest.strip("-")

        m2 = re.match(r"^([a-z]+)-([0-9]{8})-(.+)$", rest)
        if m2:
            kind, yyyymmdd, slug = m2.groups()
            date = _date_from_yyyymmdd(yyyymmdd)
            return f"{dom}N-{_safe_slug(kind + '-' + slug)}-{date}"

        m3 = re.match(r"^([0-9]{8})-(.+)$", rest)
        if m3:
            yyyymmdd, slug = m3.groups()
            date = _date_from_yyyymmdd(yyyymmdd)
            return f"{dom}N-{_safe_slug(slug)}-{date}"

        date = _infer_date_for_note(path)
        return f"{dom}N-{_safe_slug(rest)}-{date}"

    return None


def _yyyymmdd_from_iso(date_iso: str) -> str:
    return date_iso.replace("-", "")


def _legacy_basenames_for_new_base(new_base: str) -> list[str]:
    """
    Given a new-style base (WT/WP/WA/WG/WN, PT/PP/PA/PG/PN), return plausible
    legacy basenames that may still be referenced in markdown (W-T-..., W-PROJ-..., etc.).
    """
    # Tasks: WT-slug-YYYY-MM-DD -> W-T-YYYYMMDD-slug
    m = re.match(r"^([WP]T)-(.+)-([0-9]{4}-[0-9]{2}-[0-9]{2})$", new_base)
    if m:
        domt, slug, date = m.groups()
        dom = domt[0]
        yyyymmdd = _yyyymmdd_from_iso(date)
        return [f"{dom}-T-{yyyymmdd}-{slug}"]

    # Projects: WP-slug -> W-PROJ-slug
    m = re.match(r"^([WP]P)-(.+)$", new_base)
    if m:
        domp, slug = m.groups()
        dom = domp[0]
        return [f"{dom}-PROJ-{slug}"]

    # Areas: WA-slug -> W-AREA-slug
    m = re.match(r"^([WP]A)-(.+)$", new_base)
    if m:
        doma, slug = m.groups()
        dom = doma[0]
        return [f"{dom}-AREA-{slug}"]

    # Goals: WG-slug -> W-GOAL-slug
    m = re.match(r"^([WP]G)-(.+)$", new_base)
    if m:
        domg, slug = m.groups()
        dom = domg[0]
        return [f"{dom}-GOAL-{slug}"]

    # Notes: WN-rest-YYYY-MM-DD
    m = re.match(r"^([WP]N)-(.+)-([0-9]{4}-[0-9]{2}-[0-9]{2})$", new_base)
    if m:
        domn, rest, date = m.groups()
        dom = domn[0]
        yyyymmdd = _yyyymmdd_from_iso(date)
        legacy: list[str] = []

        # 1) Legacy without date: W-NOTE-rest
        legacy.append(f"{dom}-NOTE-{rest}")

        # 2) Legacy date-first: W-NOTE-YYYYMMDD-rest
        legacy.append(f"{dom}-NOTE-{yyyymmdd}-{rest}")

        # 3) Legacy kind-first (common for audio/docx/pptx tools):
        for kind in ("audio", "docx", "pptx"):
            prefix = kind + "-"
            if rest.startswith(prefix) and len(rest) > len(prefix):
                slug = rest[len(prefix) :]
                legacy.append(f"{dom}-NOTE-{kind}-{yyyymmdd}-{slug}")

        return legacy

    return []


def build_reference_mapping_from_current_files(files: list[Path]) -> dict[str, str]:
    """
    Build old->new mapping for reference replacement even if renames already happened
    in a previous run (so this run has 0 planned renames).
    """
    mapping: dict[str, str] = {}
    collisions: set[str] = set()

    for md in files:
        new_base = md.stem
        for old_base in _legacy_basenames_for_new_base(new_base):
            if old_base == new_base:
                continue
            existing = mapping.get(old_base)
            if existing is None:
                mapping[old_base] = new_base
            elif existing != new_base:
                collisions.add(old_base)

    # Drop ambiguous keys (safer than guessing).
    for k in collisions:
        mapping.pop(k, None)

    return mapping


def _collect_candidates(root_dirs: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in root_dirs:
        if not root.exists():
            continue
        for md in root.rglob("*.md"):
            if md.name.startswith("."):
                continue
            rel = md.relative_to(ROOT)
            # Never touch private/incoming drop folders
            if rel.parts[:3] == ("Work", "00_Inbox", "Private"):
                continue
            if rel.parts[:3] == ("Work", "00_Inbox", "Incoming"):
                continue
            if rel.parts[:3] == ("Personal", "00_Inbox", "Private"):
                continue
            if rel.parts[:3] == ("Personal", "00_Inbox", "Incoming"):
                continue
            files.append(md)
    return files


def build_renames(files: list[Path]) -> list[Rename]:
    renames: list[Rename] = []
    for src in files:
        old_base = src.stem
        new_base = _convert_basename(old_base, src)
        if not new_base or new_base == old_base:
            continue
        dst = src.with_name(new_base + src.suffix)
        dst = _unique_dst(dst)
        renames.append(Rename(src=src, dst=dst, old_base=old_base, new_base=dst.stem))
    return renames


def apply_renames(renames: list[Rename], dry_run: bool) -> None:
    for r in renames:
        if dry_run:
            print(f"RENAME {r.src.relative_to(ROOT)} -> {r.dst.relative_to(ROOT)}")
            continue
        r.dst.parent.mkdir(parents=True, exist_ok=True)
        if _is_tracked(r.src):
            rel_src = str(r.src.relative_to(ROOT))
            rel_dst = str(r.dst.relative_to(ROOT))
            p = _run(["git", "mv", rel_src, rel_dst])
            if p.returncode != 0:
                raise RuntimeError(f"git mv failed: {rel_src} -> {rel_dst}\n{p.stderr}")
        else:
            r.src.rename(r.dst)


def replace_references(all_md_files: list[Path], mapping: dict[str, str], dry_run: bool) -> int:
    changed = 0
    # Replace longer keys first to avoid partial overlaps
    keys = sorted(mapping.keys(), key=len, reverse=True)
    for md in all_md_files:
        try:
            text = md.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = md.read_text(encoding="utf-8", errors="ignore")

        new_text = text
        for k in keys:
            new_text = new_text.replace(k, mapping[k])

        if new_text != text:
            changed += 1
            if not dry_run:
                md.write_text(new_text, encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate vault entity IDs to short prefixes (WT/WP/WA/WG/WN, PT/PP/PA/PG/PN) and update references.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned operations without changing files.")
    parser.add_argument("--include-personal", action="store_true", help="Also migrate Personal domain (default: only Work).")
    args = parser.parse_args()

    targets = [ROOT / "Work"]
    if args.include_personal:
        targets.append(ROOT / "Personal")

    md_files = _collect_candidates(targets + [ROOT / "00_System"])
    # Build rename list only for Work/Personal, not 00_System
    rename_sources = _collect_candidates(targets)

    renames = build_renames(rename_sources)
    mapping: dict[str, str] = {r.old_base: r.new_base for r in renames}

    print(f"Planned renames: {len(renames)}")
    apply_renames(renames, dry_run=args.dry_run)

    # Always build a mapping from current files as well, so we can fix references even
    # when renames were already applied in a previous run.
    current_entity_files = _collect_candidates(targets)
    mapping_current = build_reference_mapping_from_current_files(current_entity_files)
    mapping_all = {**mapping_current, **mapping}

    if not mapping_all:
        print("No mapping generated; no reference updates applied.")
        return 0

    # Re-scan after renames (paths may have changed).
    md_files = _collect_candidates(targets + [ROOT / "00_System"])
    changed = replace_references(md_files, mapping_all, dry_run=args.dry_run)
    print(f"Mapping entries: {len(mapping_all)}")
    print(f"Updated references in files: {changed}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
