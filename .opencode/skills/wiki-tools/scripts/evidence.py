#!/usr/bin/env python3
"""
evidence.py — Build a grounded evidence bundle from wiki/ and raw/ sources.

Inputs:
  - Natural-language query
  - Optional page type filter

Outputs:
  - Human-readable evidence brief to stdout
  - Or JSON with --json for downstream command consumption

Deps:
  - Standard library only
"""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent.parent
RAW_DIR = ROOT / "raw"
WIKI_DIR = ROOT / "wiki"
SKIP = {"AGENTS.md"}
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "what",
    "why",
    "with",
}
RAW_INDEX: dict[str, Path] | None = None


def wiki_pages(page_type: str | None = None) -> list[Path]:
    pages = []
    for path in sorted(WIKI_DIR.rglob("*.md")):
        if path.name in SKIP or path.stem == "index":
            continue
        if page_type:
            text = path.read_text(encoding="utf-8")
            if f"type: {page_type}" not in text:
                continue
        pages.append(path)
    return pages


def tokenize(query: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", query.lower())
    filtered = []
    for token in tokens:
        if len(token) <= 1 or token in STOPWORDS:
            continue
        if token not in filtered:
            filtered.append(token)
    return filtered


def frontmatter_block(text: str) -> list[str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []

    block = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        block.append(line)
    return block


def fm_field(text: str, field: str) -> str:
    for line in frontmatter_block(text):
        if line.startswith(field + ":"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return ""


def fm_list(text: str, field: str) -> list[str]:
    def clean(value: str) -> str:
        return value.strip().strip('"').strip("'")

    result = []
    lines = frontmatter_block(text)
    in_field = False
    for line in lines:
        if line.startswith(field + ":"):
            in_field = True
            inline = line.split(":", 1)[1].strip()
            if inline and inline != "[]":
                cleaned = clean(inline.strip("[]").strip())
                if cleaned:
                    result.append(cleaned)
            continue
        if in_field:
            if re.match(r"^\s+-", line):
                result.append(clean(re.sub(r"^\s*-\s*", "", line).strip()))
            else:
                break
    return [item for item in result if item and item != "[]"]


def body_lines(text: str) -> list[tuple[int, str]]:
    lines = text.splitlines()
    body_start = 0
    if lines and lines[0].strip() == "---":
        for idx, line in enumerate(lines[1:], start=2):
            if line.strip() == "---":
                body_start = idx
                break
    result = []
    for lineno, line in enumerate(lines[body_start:], start=body_start + 1):
        stripped = line.strip()
        if stripped:
            result.append((lineno, stripped))
    return result


def links_in(text: str) -> list[str]:
    return re.findall(r"\[\[([^\]]+)\]\]", text)


def normalize_ref(text: str) -> str:
    base = text.lower()
    base = re.sub(r"\.md$", "", base)
    base = re.sub(r"-20\d{2}-\d{2}-\d{2}$", "", base)
    return re.sub(r"[^a-z0-9]+", "", base)


def raw_index() -> dict[str, Path]:
    global RAW_INDEX
    if RAW_INDEX is not None:
        return RAW_INDEX

    index = {}
    for path in sorted(RAW_DIR.glob("*.md")):
        if path.name in SKIP:
            continue
        index[normalize_ref(path.name)] = path
    RAW_INDEX = index
    return index


def resolve_raw_path(raw_ref: str) -> Path | None:
    if not raw_ref.startswith("raw/"):
        return None

    raw_path = ROOT / raw_ref
    if raw_path.exists():
        return raw_path

    return raw_index().get(normalize_ref(Path(raw_ref).name))


def resolve_raw_url(raw_ref: str) -> str | None:
    raw_path = resolve_raw_path(raw_ref)
    if not raw_path:
        return None

    raw_text = raw_path.read_text(encoding="utf-8")
    url = fm_field(raw_text, "source")
    return url or None


def resolve_page_urls(page_name: str) -> list[str]:
    candidates = list(WIKI_DIR.rglob(f"{page_name}.md"))
    if not candidates:
        return []

    text = candidates[0].read_text(encoding="utf-8")
    sources = fm_list(text, "sources")
    links = fm_list(text, "links")
    raw_sources = [item for item in sources if item.startswith("raw/")]
    source_urls = [
        item
        for item in sources
        if item.startswith("http://") or item.startswith("https://")
    ]
    raw_urls = [url for url in (resolve_raw_url(item) for item in raw_sources) if url]
    return unique_preserve_order(links + source_urls + raw_urls)


def collect_snippets(text: str, terms: list[str], limit: int) -> list[dict]:
    snippets = []
    for lineno, line in body_lines(text):
        matched = [term for term in terms if term in line.lower()]
        if not matched:
            continue
        snippets.append(
            {
                "line": lineno,
                "text": line,
                "matched_terms": matched,
                "score": len(set(matched)),
            }
        )
    snippets.sort(key=lambda item: (-item["score"], item["line"]))
    return snippets[:limit]


def page_score(
    path: Path, text: str, terms: list[str], snippets: list[dict], query: str
) -> int:
    title = fm_field(text, "title").lower()
    stem = path.stem.lower()
    rel = str(path.relative_to(ROOT)).lower()
    query_lc = query.lower()

    score = 0
    for term in terms:
        if term in title:
            score += 6
        if term in stem:
            score += 5
        if term in rel:
            score += 2

    if query_lc and query_lc in text.lower():
        score += 8

    score += sum(snippet["score"] for snippet in snippets)
    return score


def unique_preserve_order(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def build_evidence(
    query: str, page_type: str | None, max_pages: int, max_snippets: int
) -> dict:
    terms = tokenize(query)
    results = []

    for path in wiki_pages(page_type=page_type):
        text = path.read_text(encoding="utf-8")
        snippets = collect_snippets(text, terms, max_snippets)
        if not snippets and query.lower() not in text.lower():
            continue

        sources = fm_list(text, "sources")
        links = fm_list(text, "links")
        raw_sources = [item for item in sources if item.startswith("raw/")]
        source_urls = [
            item
            for item in sources
            if item.startswith("http://") or item.startswith("https://")
        ]
        raw_urls = [
            url for url in (resolve_raw_url(item) for item in raw_sources) if url
        ]
        supporting_summaries = unique_preserve_order(
            [link for link in links_in(text) if link.startswith("summary-")]
        )
        supporting_urls = []
        for summary in supporting_summaries:
            supporting_urls.extend(resolve_page_urls(summary))

        score = page_score(path, text, terms, snippets, query)
        if score <= 0:
            continue

        results.append(
            {
                "page": path.stem,
                "path": str(path.relative_to(ROOT)),
                "type": fm_field(text, "type"),
                "status": fm_field(text, "status"),
                "title": fm_field(text, "title") or path.stem,
                "score": score,
                "snippets": snippets,
                "sources": sources,
                "raw_sources": raw_sources,
                "supporting_summaries": supporting_summaries,
                "urls": unique_preserve_order(
                    links + source_urls + raw_urls + supporting_urls
                ),
            }
        )

    results.sort(key=lambda item: (-item["score"], item["path"]))
    trimmed = results[:max_pages]

    for idx, item in enumerate(trimmed, start=1):
        item["citation_id"] = f"S{idx}"
        for snippet in item["snippets"]:
            snippet.pop("score", None)

    return {
        "query": query,
        "terms": terms,
        "page_type": page_type,
        "results": trimmed,
        "coverage": "covered" if trimmed else "not-covered",
    }


def print_report(bundle: dict):
    query = bundle["query"]
    results = bundle["results"]
    print(f'Evidence for "{query}"')
    print(f"Coverage: {bundle['coverage']}")
    print()

    if not results:
        print("No wiki-backed evidence found.")
        print("Use this as a hard stop for grounded generation.")
        return

    for item in results:
        print(
            f"[{item['citation_id']}] [[{item['page']}]]  "
            f"{item['path']}  [{item['type']}, {item['status']}]  score={item['score']}"
        )
        for snippet in item["snippets"]:
            terms = ", ".join(snippet["matched_terms"])
            print(f"  line {snippet['line']}: {snippet['text']}")
            print(f"    matched: {terms}")

        if item["supporting_summaries"]:
            print(f"  supporting summaries: {', '.join(item['supporting_summaries'])}")

        if item["raw_sources"]:
            print(f"  raw sources: {', '.join(item['raw_sources'])}")

        if item["urls"]:
            for url in item["urls"]:
                print(f"  url: {url}")
        else:
            print("  url: none")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Build a grounded evidence bundle from wiki/ and raw/"
    )
    parser.add_argument("query", help="Natural-language question or topic")
    parser.add_argument("--type", choices=["concept", "topic", "summary"])
    parser.add_argument("--max-pages", type=int, default=8)
    parser.add_argument("--max-snippets", type=int, default=3)
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON"
    )
    args = parser.parse_args()

    bundle = build_evidence(
        query=args.query,
        page_type=args.type,
        max_pages=max(1, args.max_pages),
        max_snippets=max(1, args.max_snippets),
    )

    if args.json:
        print(json.dumps(bundle, indent=2, ensure_ascii=False))
        return

    print_report(bundle)


if __name__ == "__main__":
    main()
