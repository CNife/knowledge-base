#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
digest.py — Full ingestion pipeline: rename new raw files + create summaries.

Combines rename.py logic + summary creation into one workflow.

Usage:
    python .opencode/skills/wiki-tools/scripts/digest.py           # preview only (dry run)
    python .opencode/skills/wiki-tools/scripts/digest.py --apply  # actually rename and create summaries
    python .opencode/skills/wiki-tools/scripts/digest.py --list   # show proposed summary filenames only
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
SCHEMAS_DIR = ROOT / "schemas"


def extract_frontmatter_title(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    in_fm = False
    for line in text.splitlines():
        if line.strip() == "---":
            in_fm = not in_fm
            continue
        if in_fm and line.startswith("title:"):
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
                m = re.search(r"(\d{4}-\d{2}-\d{2})", val)
                if m:
                    return m.group(1)
            if line.startswith("published:"):
                val = line.split("published:", 1)[1].strip()
                m = re.search(r"(\d{4}-\d{2}-\d{2})", val)
                if m:
                    return m.group(1)
    return None


def slugify(title: str) -> str:
    """Convert title to URL-safe slug, preserving meaningful content."""
    prefix = ""

    prefix_match = re.match(r"^([\w-]+)/([\w-]+):\s*(.*)", title)
    if prefix_match:
        author = prefix_match.group(1).lower()
        repo = prefix_match.group(2).lower()
        desc = prefix_match.group(3) if prefix_match.group(3) else ""
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

    title = re.sub(
        r"^(Summary|Notes?|Paper|Post|Article)\s*[:–—]\s*",
        "",
        title,
        flags=re.IGNORECASE,
    )
    title = re.sub(r"\s+[-–—]\s+\S.*$", "", title)
    title = re.sub(r'["\'`\\\[\]]', "", title)
    title = re.sub(r"[;:,!?]", " ", title)
    title = re.sub(r"\([^)]*\)", "", title)
    title = title.lower()
    title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", title)
    title = re.sub(r"\s+", "-", title)
    title = title.strip("-")
    if all(ord(c) < 128 for c in title):
        title = re.sub(r"[^a-z0-9\s\-]", " ", title)
        title = re.sub(r"[\s\-]+", "-", title)
        title = title.strip("-")
    if len(title) > 45:
        title = title[:45]
        last_dash = title.rfind("-")
        if last_dash > 20:
            title = title[:last_dash]
    return title


def generate_new_name(path: Path) -> str:
    title = extract_frontmatter_title(path)
    if title:
        slug = slugify(title)
    else:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", path.stem).lower().strip("-")

    date = extract_date(path)
    date_len = len(f"-{date}.md") if date else len(".md")
    max_slug_len = 200 - date_len
    if len(slug) > max_slug_len:
        slug = slug[:max_slug_len].rstrip("-")

    if date:
        return f"{slug}-{date}.md"
    else:
        return f"{slug}.md"


def find_summary_refs(old_name: str) -> list[Path]:
    refs = []
    for page in SUMMARIES_DIR.glob("*.md"):
        text = page.read_text(encoding="utf-8")
        if f"raw/{old_name}" in text:
            refs.append(page)
    return refs


def update_summary_refs(page: Path, old_name: str, new_name: str):
    text = page.read_text(encoding="utf-8")
    new_text = text.replace(f"raw/{old_name}", f"raw/{new_name}")
    if text != new_text:
        page.write_text(new_text, encoding="utf-8")


def get_source_info(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    info = {"type": "web", "author": "", "year": "", "venue": "", "url": ""}

    in_fm = False
    for line in text.splitlines():
        if line.strip() == "---":
            in_fm = not in_fm
            continue
        if not in_fm:
            break
        if line.startswith("source:"):
            info["url"] = line.split("source:", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("author:"):
            info["author"] = line.split("author:", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("published:"):
            val = line.split("published:", 1)[1].strip()
            m = re.search(r"(\d{4})", val)
            if m:
                info["year"] = m.group(1)
        elif line.startswith("title:"):
            title = line.split("title:", 1)[1].strip()
            title = re.sub(r'^["\']|["\']$', "", title).strip()
            info["title"] = title

    if "url" not in info and "source:" in text:
        pass

    return info


def generate_summary_filename(path: Path) -> str:
    title = extract_frontmatter_title(path)
    if title:
        slug = slugify(title)
    else:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", path.stem).lower().strip("-")
    return f"summary-{slug}.md"


def create_summary(raw_path: Path, new_raw_name: str) -> str:
    info = get_source_info(raw_path)
    today = datetime.now().strftime("%Y-%m-%d")

    filename = generate_summary_filename(raw_path)
    filepath = SUMMARIES_DIR / filename

    title = info.get("title", new_raw_name)
    author = info.get("author", "")
    year = info.get("year", "")
    url = info.get("url", "")
    links_block = f"links:\n  - {url}" if url else "links: []"

    content = f"""---
title: "Summary — {title}"
type: summary
status: draft
created: {today}
updated: {today}
sources:
  - raw/{new_raw_name}
{links_block}
tags: []
---

# Summary — {title}

## Source Metadata

| Field        | Value                          |
|--------------|--------------------------------|
| Source type  | {info.get("type", "web")}     |
| Author(s)    | {author or "Unknown"}         |
| Year         | {year or "n/a"}               |
| Venue        | {info.get("venue", "n/a")}    |
| Raw file     | `raw/{new_raw_name}`          |

## Main Idea

<!-- 1-3 sentences. What is the central claim or contribution? Be precise. -->

## Key Details

<!-- Most important technical details, results, or arguments. -->

## Method / Approach

<!-- For papers: technical approach. For blogs: main argument. -->

## Results / Evidence

<!-- Evidence supporting the main idea. -->

## Limitations

<!-- What the source acknowledges as limitations. -->

## Links to Concepts

<!-- Which wiki concept pages does this source support? -->

## Links to Topics

<!-- Which wiki topic pages does this source belong under? -->

## Quotes Worth Preserving

<!-- Optional verbatim quotes. -->
"""

    if filepath.exists():
        print(f"  SKIP: {filename} already exists")
        return ""

    return content


def main():
    parser = argparse.ArgumentParser(
        description="Full ingestion: rename raw files + create summaries"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually rename files and create summaries",
    )
    parser.add_argument(
        "--list", action="store_true", help="Show proposed summary filenames only"
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    SKIP = {"AGENTS.md"}

    files = []
    for p in sorted(RAW_DIR.iterdir()):
        if p.is_file() and p.name not in SKIP:
            files.append(p)

    if not files:
        print("raw/ is empty.")
        return

    operations = []
    for f in files:
        new_name = generate_new_name(f)
        summary_filename = generate_summary_filename(f)
        refs = find_summary_refs(f.name)
        operations.append(
            {
                "old": f.name,
                "new": new_name,
                "summary": summary_filename,
                "refs": [r.name for r in refs],
                "path": f,
            }
        )

    if args.list:
        for op in operations:
            if op["old"] != op["new"]:
                print(f"{op['old']}  →  {op['new']}")
            print(f"  summary: {op['summary']}")
        return

    # Preview
    for op in operations:
        rename_status = "keep" if op["old"] == op["new"] else f"→ {op['new']}"
        print(f"  {op['old']:<60}  {rename_status}")
        if op["refs"]:
            print(f"    (updates {len(op['refs'])} summary refs)")

    if not any(op["old"] != op["new"] for op in operations):
        print("\nNo new files to rename.")
        return

    if not args.apply:
        print("\nDry run. Use --apply to execute.")
        return

    # Execute
    for op in operations:
        if op["old"] == op["new"]:
            continue

        new_path = RAW_DIR / op["new"]
        op["path"].rename(new_path)
        op["new_path"] = new_path

        for ref_page in op["refs"]:
            ref_path = SUMMARIES_DIR / ref_page
            update_summary_refs(ref_path, op["old"], op["new"])

        print(f"Renamed: {op['old']} → {op['new']}")

    # Create summaries for truly new files (no existing summary refs them)
    new_raw_files = [op for op in operations if not op["refs"]]

    if new_raw_files:
        print(f"\n--- Creating {len(new_raw_files)} summaries ---")
        for op in new_raw_files:
            path_to_read = op.get("new_path", op["path"])
            content = create_summary(path_to_read, op["new"])
            if content and op["new"]:
                filepath = SUMMARIES_DIR / op["summary"]
                filepath.write_text(content, encoding="utf-8")
                print(f"Created: {op['summary']}")

    print("\nDone. Run `python .opencode/skills/wiki-tools/scripts/lint.py` to verify.")


if __name__ == "__main__":
    main()
