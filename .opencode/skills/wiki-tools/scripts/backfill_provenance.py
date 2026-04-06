#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
backfill_provenance.py — Repair wiki provenance drift against current raw/ files.

Fixes:
  - stale raw/<filename> references in wiki frontmatter `sources:`
  - missing summary `links:` entries derived from raw frontmatter `source:`
  - bumps `updated:` when a page changes

Usage:
  python .opencode/skills/wiki-tools/scripts/backfill_provenance.py          # dry run
  python .opencode/skills/wiki-tools/scripts/backfill_provenance.py --apply  # write changes
"""

import argparse
import re
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent.parent
RAW_DIR = ROOT / "raw"
WIKI_DIR = ROOT / "wiki"
SKIP = {"AGENTS.md"}


def normalize_ref(text: str) -> str:
    base = text.lower()
    base = re.sub(r"\.md$", "", base)
    base = re.sub(r"-20\d{2}-\d{2}-\d{2}$", "", base)
    return re.sub(r"[^a-z0-9]+", "", base)


def raw_index() -> dict[str, Path]:
    index = {}
    for path in sorted(RAW_DIR.glob("*.md")):
        if path.name in SKIP:
            continue
        index[normalize_ref(path.name)] = path
        fm_lines, _ = split_frontmatter(path.read_text(encoding="utf-8"))
        if fm_lines is None:
            continue
        fields = parse_frontmatter(fm_lines)
        title = str(fields.get("title", "")).strip('"').strip("'")
        if title:
            index[normalize_ref(title)] = path
    return index


def fuzzy_raw_match(raw_ref: str, index: dict[str, Path]) -> Path | None:
    target = normalize_ref(Path(raw_ref).name)
    if not target:
        return None

    prefix_matches = {
        path
        for alias, path in index.items()
        if alias.startswith(target) or target.startswith(alias)
    }
    if len(prefix_matches) == 1:
        return next(iter(prefix_matches))

    scored = []
    for alias, path in index.items():
        score = SequenceMatcher(None, target, alias).ratio()
        if score >= 0.82:
            scored.append((score, path))
    scored.sort(key=lambda item: item[0], reverse=True)

    if not scored:
        return None

    best_score, best_path = scored[0]
    competing_paths = {path for score, path in scored if score == best_score}
    if len(competing_paths) == 1 and best_score >= 0.9:
        return best_path

    return None


def split_frontmatter(text: str) -> tuple[list[str] | None, list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, lines

    fm = []
    end_idx = None
    for idx, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = idx
            break
        fm.append(line)

    if end_idx is None:
        return None, lines

    return fm, lines[end_idx + 1 :]


def parse_frontmatter(lines: list[str]) -> dict[str, object]:
    fields: dict[str, object] = {}
    current_list: str | None = None
    current_scalar: str | None = None

    for line in lines:
        if re.match(r"^\w[^:]*:\s*$", line):
            key = line.split(":", 1)[0].strip()
            fields[key] = []
            current_list = key
            current_scalar = None
            continue

        if re.match(r"^\w[^:]*:\s+\[\]\s*$", line):
            key = line.split(":", 1)[0].strip()
            fields[key] = []
            current_list = None
            current_scalar = None
            continue

        if re.match(r"^\w[^:]*:\s+", line):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
            current_scalar = key.strip()
            current_list = None
            continue

        if current_list and re.match(r"^\s*-\s+", line):
            values = fields.setdefault(current_list, [])
            assert isinstance(values, list)
            values.append(re.sub(r"^\s*-\s*", "", line).strip())
            continue

        current_list = None
        current_scalar = None

    return fields


def yaml_quote(value: str) -> str:
    if value == "":
        return '""'
    if re.search(r'[:\[\]{}#,&*!?|<>=@`"\']', value) or value != value.strip():
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def render_frontmatter(fields: dict[str, object]) -> list[str]:
    ordered_keys = [
        "title",
        "type",
        "status",
        "created",
        "updated",
        "sources",
        "links",
        "tags",
    ]
    rendered = []
    remaining = set(fields.keys())

    def render_key(key: str):
        value = fields[key]
        if isinstance(value, list):
            if value:
                rendered.append(f"{key}:")
                for item in value:
                    rendered.append(f"  - {yaml_quote(str(item))}")
            else:
                rendered.append(f"{key}: []")
        else:
            rendered.append(f"{key}: {value}")

    for key in ordered_keys:
        if key in fields:
            render_key(key)
            remaining.discard(key)

    for key in fields:
        if key in remaining:
            render_key(key)

    return rendered


def resolve_raw_ref(raw_ref: str, index: dict[str, Path]) -> str:
    if not raw_ref.startswith("raw/"):
        return raw_ref

    raw_path = ROOT / raw_ref
    if raw_path.exists():
        return raw_ref

    match = index.get(normalize_ref(Path(raw_ref).name))
    if not match:
        match = fuzzy_raw_match(raw_ref, index)
    if not match:
        return raw_ref
    return f"raw/{match.name}"


def raw_source_url(raw_ref: str) -> str:
    if not raw_ref.startswith("raw/"):
        return ""
    raw_path = ROOT / raw_ref
    if not raw_path.exists():
        return ""
    fm_lines, _ = split_frontmatter(raw_path.read_text(encoding="utf-8"))
    if fm_lines is None:
        return ""
    fields = parse_frontmatter(fm_lines)
    source = fields.get("source", "")
    return str(source).strip('"').strip("'")


def process_page(
    path: Path, index: dict[str, Path], today: str
) -> tuple[bool, list[str]]:
    text = path.read_text(encoding="utf-8")
    fm_lines, body_lines = split_frontmatter(text)
    if fm_lines is None:
        return False, []

    fields = parse_frontmatter(fm_lines)
    changes = []

    sources = fields.get("sources", [])
    if not isinstance(sources, list):
        sources = []
    updated_sources = []
    for source in sources:
        source_str = str(source)
        resolved = resolve_raw_ref(source_str, index)
        updated_sources.append(resolved)
        if resolved != source_str:
            changes.append(f"source: {source_str} -> {resolved}")
    fields["sources"] = updated_sources

    page_type = str(fields.get("type", ""))
    links = fields.get("links", [])
    if isinstance(links, list):
        updated_links = list(links)
    elif str(links).strip() in {"", "[]"}:
        updated_links = []
    else:
        updated_links = [str(links)]

    if page_type == "summary":
        for source in updated_sources:
            url = raw_source_url(source)
            if url and url not in updated_links:
                updated_links.append(url)
                changes.append(f"link+: {url}")
    fields["links"] = updated_links

    if changes:
        fields["updated"] = today
        rendered = ["---", *render_frontmatter(fields), "---", *body_lines]
        new_text = "\n".join(rendered).rstrip() + "\n"
        return True, changes + [new_text]

    return False, []


def main():
    parser = argparse.ArgumentParser(description="Repair wiki provenance drift")
    parser.add_argument("--apply", action="store_true", help="Write changes to disk")
    args = parser.parse_args()

    index = raw_index()
    today = datetime.now().strftime("%Y-%m-%d")
    changed_pages = []

    for path in sorted(WIKI_DIR.rglob("*.md")):
        if path.name in SKIP or path.stem == "index":
            continue
        changed, payload = process_page(path, index, today)
        if not changed:
            continue
        new_text = payload[-1]
        changes = payload[:-1]
        changed_pages.append((path, changes, new_text))

    if not changed_pages:
        print("No provenance changes needed.")
        return

    for path, changes, _ in changed_pages:
        print(path.relative_to(ROOT))
        for change in changes:
            print(f"  - {change}")

    print(f"\n{len(changed_pages)} page(s) would change.")

    if not args.apply:
        print("Dry run. Use --apply to write changes.")
        return

    for path, _, new_text in changed_pages:
        path.write_text(new_text, encoding="utf-8")

    print("Applied provenance backfill.")


if __name__ == "__main__":
    main()
