#!/usr/bin/env python3
"""
stub.py — Create a blank wiki page from a schema template.

Usage:
    python .opencode/skills/wiki-tools/scripts/stub.py summary "paper_flashattention2-2023.md"
    python .opencode/skills/wiki-tools/scripts/stub.py concept "flash-attention"
    python .opencode/skills/wiki-tools/scripts/stub.py topic "gpu-memory-optimization"
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent.parent.parent.parent.parent
WIKI_DIR = ROOT / "wiki"
SCHEMAS_DIR = ROOT / "schemas"

DESTINATIONS = {
    "concept": WIKI_DIR / "concepts",
    "topic": WIKI_DIR / "topics",
    "summary": WIKI_DIR / "summaries",
}


def slugify(name: str) -> str:
    name = re.sub(r"\.md$", "", name)
    name = name.lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s_]+", "-", name)
    return name.strip("-")


def main():
    parser = argparse.ArgumentParser(description="Create a stub wiki page")
    parser.add_argument("type", choices=["concept", "topic", "summary"])
    parser.add_argument(
        "name", help="Source filename (for summary) or concept/topic name"
    )
    args = parser.parse_args()

    dest_dir = DESTINATIONS[args.type]
    schema = (SCHEMAS_DIR / f"{args.type}.md").read_text()

    slug = slugify(args.name)
    if args.type == "summary":
        filename = f"summary-{slug}.md"
        source_ref = (
            f"raw/{args.name}" if not args.name.startswith("raw/") else args.name
        )
    else:
        filename = f"{slug}.md"
        source_ref = ""

    out = dest_dir / filename
    if out.exists():
        print(f"Already exists: {out.relative_to(ROOT)}")
        sys.exit(0)

    today = date.today().isoformat()
    content = schema.replace("YYYY-MM-DD", today)
    if source_ref:
        content = content.replace("raw/<source-file> or https://...", source_ref)

    dest_dir.mkdir(parents=True, exist_ok=True)
    out.write_text(content)
    print(f"Created: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
