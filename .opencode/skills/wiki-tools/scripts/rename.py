#!/usr/bin/env python3
"""
rename.py — Slugify filenames in raw/ based on frontmatter title.

Extracts title from each markdown file's YAML frontmatter, converts to a
slug-based filename, and updates wiki/summaries/ pages that reference the
old filename.

Naming convention:
    <slugified-title>-<YYYY-MM-DD>.md

If no date in frontmatter, uses file's created date or skips date.

Usage:
    python .opencode/skills/wiki-tools/scripts/rename.py           # preview renames (dry run)
    python .opencode/skills/wiki-tools/scripts/rename.py --apply   # actually rename files
    python .opencode/skills/wiki-tools/scripts/rename.py --list    # list proposed new names only
"""

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent.parent
RAW_DIR = ROOT / "raw"
SUMMARIES_DIR = ROOT / "wiki" / "summaries"


def extract_frontmatter_title(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    in_fm = False
    for line in text.splitlines():
        if line.strip() == "---":
            in_fm = not in_fm
            continue
        if in_fm and line.startswith("title:"):
            # Extract quoted or unquoted title value
            val = line.split("title:", 1)[1].strip()
            val = re.sub(r'^["\']|["\']$', "", val).strip()
            return val
    return None


def extract_date(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    in_fm = False
    for line in text.splitlines():
        if line.strip() == "---":
            in_fm = not in_fm
            continue
        if in_fm:
            if line.startswith("created:"):
                val = line.split("created:", 1)[1].strip()
                # Extract YYYY-MM-DD
                m = re.search(r"(\d{4}-\d{2}-\d{2})", val)
                if m:
                    return m.group(1)
    return None


def slugify(title: str) -> str:
    """Convert title to URL-safe slug, preserving meaningful content."""
    prefix = ""

    # If title looks like "Author/Repo: Description", extract both
    prefix_match = re.match(r"^([\w-]+)/([\w-]+):\s*(.*)", title)
    if prefix_match:
        author = prefix_match.group(1).lower()
        repo = prefix_match.group(2).lower()
        desc = prefix_match.group(3) if prefix_match.group(3) else ""
        # Clean description
        desc = re.sub(r'["\'`\\\[\]]', "", desc)
        desc = re.sub(r"[;:,!?]", " ", desc)
        desc = re.sub(r"\s*[-–—]\s*", " ", desc)
        desc = re.sub(r"\s+", " ", desc).strip()
        words = desc.split()[:5]
        desc = "-".join(
            w.lower()[:12] for w in words if w and w.isascii() and w.isalpha()
        )
        prefix = f"{author}-{repo}"
        if desc:
            return f"{prefix}-{desc}"
        return prefix

    # Remove common prefixes
    title = re.sub(
        r"^(Summary|Notes?|Paper|Post|Article)\s*[:–—]\s*",
        "",
        title,
        flags=re.IGNORECASE,
    )

    # Remove author attribution (e.g., " - 阮一峰的网络日志")
    # Pattern: space + dash + space + non-space content at end
    # Only match when there's clear separation (space-dash-space)
    title = re.sub(r"\s+[-–—]\s+\S.*$", "", title)

    title = re.sub(r'["\'`\\\[\]]', "", title)
    title = re.sub(r"[;:,!?]", " ", title)
    title = re.sub(r"\([^)]*\)", "", title)

    # Preserve unicode characters (CJK) as they carry semantic meaning
    # Only strip control chars and unsafe URL chars
    title = title.lower()
    title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", title)
    title = re.sub(r"\s+", "-", title)
    title = title.strip("-")

    # For pure ASCII slugs, apply stricter cleaning
    if all(ord(c) < 128 for c in title):
        title = re.sub(r"[^a-z0-9\s\-]", " ", title)
        title = re.sub(r"[\s\-]+", "-", title)
        title = title.strip("-")

    # Truncate at word boundary
    if len(title) > 45:
        title = title[:45]
        last_dash = title.rfind("-")
        if last_dash > 20:
            title = title[:last_dash]
    return title


MAX_FILENAME_LEN = 200  # Leave room for path and .md extension


def generate_new_name(path: Path) -> str:
    title = extract_frontmatter_title(path)
    if title:
        slug = slugify(title)
    else:
        # Fallback: use original stem
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", path.stem).lower().strip("-")

    # Truncate slug if too long (leaving room for date and extension)
    date = extract_date(path)
    date_len = len(f"-{date}.md") if date else len(".md")
    max_slug_len = MAX_FILENAME_LEN - date_len
    if len(slug) > max_slug_len:
        slug = slug[:max_slug_len].rstrip("-")

    if date:
        return f"{slug}-{date}.md"
    else:
        return f"{slug}.md"


def find_references(old_name: str) -> list[Path]:
    """Find wiki/summaries/ pages that reference the old raw filename."""
    refs = []
    for page in SUMMARIES_DIR.glob("*.md"):
        text = page.read_text(encoding="utf-8")
        if f"raw/{old_name}" in text:
            refs.append(page)
    return refs


def update_references(page: Path, old_name: str, new_name: str):
    """Update all references in a page from old_name to new_name."""
    text = page.read_text(encoding="utf-8")
    new_text = text.replace(f"raw/{old_name}", f"raw/{new_name}")
    if text != new_text:
        page.write_text(new_text, encoding="utf-8")
        return True
    return False


def rename_file(old_path: Path, new_path: Path, dry_run: bool = True) -> bool:
    if dry_run:
        return True  # Pretend success for dry run
    shutil.move(str(old_path), str(new_path))
    return True


def get_conflicts(new_name: str, old_path: Path) -> list[str]:
    """Check for conflicts with existing files."""
    conflicts = []
    if new_name != old_path.name:
        new_path = RAW_DIR / new_name
        if new_path.exists():
            conflicts.append(f"File already exists: {new_name}")
        # Check git-tracked files too
        git_check = Path(f"raw/{new_name}")
    return conflicts


def main():
    parser = argparse.ArgumentParser(
        description="Slugify raw/ filenames based on frontmatter title"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually rename files (default is dry run)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Show proposed names only, don't preview changes",
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing files if conflict"
    )
    args = parser.parse_args()

    SKIP = {"AGENTS.md"}

    files = []
    for p in sorted(RAW_DIR.iterdir()):
        if p.is_file() and p.name not in SKIP:
            files.append(p)

    if not files:
        print("raw/ is empty.")
        return

    renames = []
    for f in files:
        new_name = generate_new_name(f)
        conflicts = get_conflicts(new_name, f)
        refs = find_references(f.name)
        renames.append(
            {
                "old": f.name,
                "new": new_name,
                "conflicts": conflicts,
                "refs": [r.name for r in refs],
                "path": f,
            }
        )

    if args.list:
        for r in renames:
            print(f"{r['new']}")
        return

    # Print preview
    for r in renames:
        status = "OK"
        if r["conflicts"]:
            status = f"CONFLICT: {', '.join(r['conflicts'])}"
        elif r["old"] != r["new"]:
            status = f"→ {r['new']}"
        if r["refs"]:
            status += f" (updates {len(r['refs'])} refs)"
        print(f"  {r['old']:<60}  {status}")

    if not any(r["old"] != r["new"] for r in renames):
        print("\nNo renames needed.")
        return

    if not args.apply:
        print("\nDry run complete. Use --apply to actually rename.")
        return

    # Apply renames
    for r in renames:
        if r["old"] == r["new"]:
            continue
        if r["conflicts"] and not args.force:
            print(f"\nSkipping {r['old']} due to conflict. Use --force to override.")
            continue

        new_path = RAW_DIR / r["new"]
        r["path"].rename(new_path)

        for ref_page in r["refs"]:
            ref_path = SUMMARIES_DIR / ref_page
            update_references(ref_path, r["old"], r["new"])
            print(f"  Updated references in {ref_page}")

        print(f"Renamed: {r['old']} → {r['new']}")

    print("\nDone.")


if __name__ == "__main__":
    main()
