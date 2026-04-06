#!/usr/bin/env python3
"""
search.py — Keyword search across wiki/ pages. Outputs to stdout only.

Usage:
    python .opencode/skills/wiki-tools/scripts/search.py "flash attention"
    python .opencode/skills/wiki-tools/scripts/search.py "memory bandwidth" --type concept
    python .opencode/skills/wiki-tools/scripts/search.py "HBM" --paths-only
"""

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent.parent
WIKI_DIR = ROOT / "wiki"
SKIP = {"AGENTS.md"}


def wiki_pages(page_type: str | None = None) -> list[Path]:
    pages = []
    for p in sorted(WIKI_DIR.rglob("*.md")):
        if p.name in SKIP or p.stem == "index":
            continue
        if page_type:
            text = p.read_text()
            if f"type: {page_type}" not in text:
                continue
        pages.append(p)
    return pages


def fm_field(text: str, field: str) -> str:
    for line in text.splitlines():
        if line.startswith(field + ":"):
            return line.split(":", 1)[1].strip()
    return ""


def fm_list(text: str, field: str) -> list[str]:
    """Extract a YAML list field from frontmatter."""

    def clean(value: str) -> str:
        return value.strip().strip('"').strip("'")

    lines = text.splitlines()
    result = []
    in_field = False
    in_fm = False
    for line in lines:
        if line.strip() == "---":
            in_fm = not in_fm
            continue
        if not in_fm:
            break
        if line.startswith(field + ":"):
            in_field = True
            inline = line.split(":", 1)[1].strip()
            if inline and inline != "[]":
                result.append(clean(inline.strip("[]").strip()))
            continue
        if in_field:
            if re.match(r"^\s+-", line):
                result.append(clean(re.sub(r"^\s+-\s*", "", line).strip()))
            else:
                break
    return [r for r in result if r]


def search(path: Path, terms: list[str]) -> list[tuple[int, str]]:
    matches = []
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if all(t in line.lower() for t in terms):
            matches.append((i, line.strip()))
    return matches


def main():
    parser = argparse.ArgumentParser(description="Search wiki pages (stdout only)")
    parser.add_argument("query", help="Search terms")
    parser.add_argument("--type", choices=["concept", "topic", "summary"])
    parser.add_argument(
        "--paths-only", action="store_true", help="Print only matching file paths"
    )
    args = parser.parse_args()

    terms = args.query.lower().split()
    pages = wiki_pages(page_type=args.type)
    results = []

    for page in pages:
        hits = search(page, terms)
        if hits:
            results.append((page, hits))

    results.sort(key=lambda x: len(x[1]), reverse=True)

    if not results:
        print(f'No matches for "{args.query}"')
        return

    print(f'Matches for "{args.query}": {len(results)} pages\n')

    for page, hits in results:
        text = page.read_text()
        rel = page.relative_to(ROOT)
        links = fm_list(text, "links")

        if args.paths_only:
            print(rel)
            continue

        page_type = fm_field(text, "type")
        status = fm_field(text, "status")
        print(f"[[{page.stem}]]  {rel}  [{page_type}, {status}]  ({len(hits)} hits)")
        if links:
            for url in links:
                print(f"  link: {url}")
        for lineno, line in hits[:5]:
            print(f"  {lineno}: {line[:100]}")
        if len(hits) > 5:
            print(f"  ... +{len(hits) - 5} more")
        print()


if __name__ == "__main__":
    main()
