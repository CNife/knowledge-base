#!/usr/bin/env python3
"""
ingest.py — Find raw/ files not yet referenced by any wiki/summaries/ page.

"New" is defined structurally: a raw file is new if no page in wiki/summaries/
lists it in its `sources:` frontmatter field. No sidecar files needed.

Usage:
    python .opencode/skills/wiki-tools/scripts/ingest.py           # list all files with status
    python .opencode/skills/wiki-tools/scripts/ingest.py --new     # list only undigested files
"""

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent.parent
RAW_DIR = ROOT / "raw"
SUMMARIES_DIR = ROOT / "wiki" / "summaries"
SKIP = {"AGENTS.md"}


def compiled_sources() -> set[str]:
    """Return set of raw filenames referenced in any wiki/summaries/ page."""
    refs = set()
    for page in SUMMARIES_DIR.glob("*.md"):
        text = page.read_text()
        in_fm = False
        in_sources = False
        for line in text.splitlines():
            if line.strip() == "---":
                in_fm = not in_fm
                continue
            if not in_fm:
                break
            if line.startswith("sources:"):
                in_sources = True
                continue
            if in_sources:
                if line.startswith(" ") or line.startswith("\t"):
                    # extract filename from "  - raw/foo.md" or "  - https://..."
                    val = re.sub(r"^\s*-\s*", "", line).strip()
                    if val.startswith("raw/"):
                        refs.add(val[len("raw/") :])
                else:
                    in_sources = False
    return refs


def raw_files() -> list[Path]:
    files = []
    for p in sorted(RAW_DIR.iterdir()):
        if p.is_file() and p.name not in SKIP:
            files.append(p)
    return files


def main():
    parser = argparse.ArgumentParser(description="Find undigested raw/ files")
    parser.add_argument("--new", action="store_true", help="Show only undigested files")
    args = parser.parse_args()

    compiled = compiled_sources()
    files = raw_files()

    if not files:
        print("raw/ is empty.")
        return

    width = max(len(f.name) for f in files) + 2
    counts = {"new": 0, "compiled": 0}

    for f in files:
        status = "compiled" if f.name in compiled else "new"
        counts[status] += 1
        if args.new and status != "new":
            continue
        print(f"{f.name:<{width}}  {status}")

    print(f"\n{len(files)} files — {counts['new']} new, {counts['compiled']} compiled")


if __name__ == "__main__":
    main()
