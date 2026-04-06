#!/usr/bin/env python3
"""
lint.py — Structural health check for wiki/.

Checks:
  1. Broken [[links]] — referenced pages that don't exist
  2. Orphan pages — not linked from anywhere
  3. Missing frontmatter fields (title, type, status, sources)
  4. [UNVERIFIED] claims in stable pages
  5. Broken provenance references (missing raw/ files, summary links drift)
  6. Template placeholders left in wiki pages
  7. Similar-name duplicates in raw/ (exact duplicates flagged separately)

Usage:
    python .opencode/skills/wiki-tools/scripts/lint.py
    python .opencode/skills/wiki-tools/scripts/lint.py --strict    # exit 1 if issues found
"""

import argparse
import hashlib
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent.parent
WIKI_DIR = ROOT / "wiki"
RAW_DIR = ROOT / "raw"
REQUIRED = ["title", "type", "status", "sources"]
EXEMPT = {"index", "AGENTS"}
RAW_SKIP = {"AGENTS.md"}


def wiki_pages() -> list[Path]:
    return [p for p in sorted(WIKI_DIR.rglob("*.md")) if p.name != "AGENTS.md"]


def page_map(pages: list[Path]) -> dict[str, Path]:
    return {p.stem: p for p in pages}


def links_in(text: str) -> list[str]:
    links = re.findall(r"\[\[([^\]]+)\]\]", text)
    return [lnk.rstrip(".md") for lnk in links]


def frontmatter(text: str) -> dict[str, str]:
    fields = {}
    in_fm = False
    for line in text.splitlines():
        if line.strip() == "---":
            if not in_fm:
                in_fm = True
                continue
            break
        if in_fm and ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            fields[k.strip()] = v.strip()
    return fields


def fm_list(text: str, field: str) -> list[str]:
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
                result.append(clean(re.sub(r"^\s*-\s*", "", line).strip()))
            else:
                break
    return [item for item in result if item]


def raw_source_url(raw_ref: str) -> str:
    if not raw_ref.startswith("raw/"):
        return ""
    raw_path = ROOT / raw_ref
    if not raw_path.exists():
        return ""
    return frontmatter(raw_path.read_text()).get("source", "").strip('"').strip("'")


def raw_files() -> list[Path]:
    return [p for p in sorted(RAW_DIR.glob("*.md")) if p.name not in RAW_SKIP]


def normalized_raw_name(path: Path) -> str:
    stem = path.stem.lower()
    stem = re.sub(r"\s+\d+$", "", stem)
    return stem


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def raw_duplicate_candidates(files: list[Path]) -> list[tuple[Path, Path, float]]:
    pairs = []
    items = [(p, normalized_raw_name(p)) for p in files]
    for i, (pa, sa) in enumerate(items):
        for pb, sb in items[i + 1 :]:
            score = similarity(sa, sb)
            if score >= 0.88:
                pairs.append((pa, pb, score))
    return pairs


def exact_raw_duplicates(files: list[Path]) -> list[list[Path]]:
    groups: dict[str, list[Path]] = {}
    for path in files:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        groups.setdefault(digest, []).append(path)
    return [sorted(group) for group in groups.values() if len(group) > 1]


def main():
    parser = argparse.ArgumentParser(description="Wiki structural linter")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    pages = wiki_pages()
    pmap = page_map(pages)
    raw = raw_files()
    issues = 0

    # Build link graph
    outgoing: dict[str, list[str]] = {}
    incoming: dict[str, set[str]] = {p.stem: set() for p in pages}
    for page in pages:
        links = links_in(page.read_text())
        outgoing[page.stem] = links
        for lnk in links:
            incoming.setdefault(lnk, set()).add(page.stem)

    print("# Wiki Lint\n")

    # 1. Broken links
    broken = [
        (src, lnk)
        for src, links in outgoing.items()
        for lnk in links
        if lnk not in pmap
    ]
    if broken:
        print(f"## Broken links ({len(broken)})")
        for src, lnk in broken:
            print(f"  {src} → [[{lnk}]]")
        print()
        issues += len(broken)
    else:
        print("## Broken links: none\n")

    # 2. Orphans
    orphans = [p for p in pages if p.stem not in EXEMPT and not incoming.get(p.stem)]
    if orphans:
        print(f"## Orphan pages ({len(orphans)})")
        for p in orphans:
            print(f"  {p.relative_to(ROOT)}")
        print()
        issues += len(orphans)
    else:
        print("## Orphan pages: none\n")

    # 3. Missing frontmatter
    fm_issues = []
    for page in pages:
        if page.stem in ("index",):
            continue
        fm = frontmatter(page.read_text())
        missing = [f for f in REQUIRED if f not in fm]
        if missing:
            fm_issues.append((page, missing))
    if fm_issues:
        print(f"## Missing frontmatter ({len(fm_issues)} pages)")
        for page, missing in fm_issues:
            print(f"  {page.relative_to(ROOT)} — missing: {', '.join(missing)}")
        print()
        issues += len(fm_issues)
    else:
        print("## Missing frontmatter: none\n")

    # 4. [UNVERIFIED] in stable pages
    unverified = []
    for page in pages:
        text = page.read_text()
        if frontmatter(text).get("status") == "stable" and "[UNVERIFIED]" in text:
            unverified.append((page, text.count("[UNVERIFIED]")))
    if unverified:
        print(f"## [UNVERIFIED] in stable pages ({len(unverified)} pages)")
        for page, n in unverified:
            print(f"  {page.relative_to(ROOT)} — {n} claim(s)")
        print()
        issues += len(unverified)
    else:
        print("## [UNVERIFIED] in stable pages: none\n")

    # 5. Provenance drift
    provenance_issues = []
    for page in pages:
        if page.stem in ("index",):
            continue
        text = page.read_text()
        sources = fm_list(text, "sources")
        links = set(fm_list(text, "links"))

        for source in sources:
            if source.startswith("raw/") and not (ROOT / source).exists():
                provenance_issues.append(
                    f"{page.relative_to(ROOT)} — missing raw source: {source}"
                )

        if frontmatter(text).get("type") == "summary":
            raw_sources = [source for source in sources if source.startswith("raw/")]
            expected_urls = {
                url for url in (raw_source_url(source) for source in raw_sources) if url
            }
            missing_urls = sorted(expected_urls - links)
            if missing_urls:
                provenance_issues.append(
                    f"{page.relative_to(ROOT)} — missing links for raw source URLs: {', '.join(missing_urls)}"
                )

    if provenance_issues:
        print(f"## Provenance drift ({len(provenance_issues)})")
        for issue in provenance_issues:
            print(f"  {issue}")
        print()
        issues += len(provenance_issues)
    else:
        print("## Provenance drift: none\n")

    # 6. Template placeholders
    placeholders = []
    for page in pages:
        if page.stem in ("index",):
            continue
        text = page.read_text()
        if "<!--" in text:
            placeholders.append(page)

    if placeholders:
        print(f"## Template placeholders ({len(placeholders)} pages)")
        for page in placeholders:
            print(f"  {page.relative_to(ROOT)}")
        print()
        issues += len(placeholders)
    else:
        print("## Template placeholders: none\n")

    # 7. raw/ duplicate candidates
    dup_candidates = raw_duplicate_candidates(raw)
    exact_dupes = exact_raw_duplicates(raw)
    if dup_candidates:
        print(f"## raw/ duplicate candidates ({len(dup_candidates)} pairs)")
        exact_pairs = {
            tuple(sorted((group[i].name, group[j].name)))
            for group in exact_dupes
            for i in range(len(group))
            for j in range(i + 1, len(group))
        }
        for pa, pb, score in dup_candidates:
            marker = (
                "exact duplicate"
                if tuple(sorted((pa.name, pb.name))) in exact_pairs
                else "similar name"
            )
            print(f"  {pa.name}  ≈  {pb.name}  ({score:.0%}, {marker})")
        print()
        issues += len(dup_candidates)
    else:
        print("## raw/ duplicate candidates: none\n")

    print(f"---\nTotal issues: {issues}")
    if args.strict and issues > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
