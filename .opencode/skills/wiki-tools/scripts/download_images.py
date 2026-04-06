#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "httpx>=0.27.0",
# ]
# ///
"""
download_images.py — Download images from raw/*.md files and update links.

Scans all Markdown files in raw/ directory, finds image links in Markdown format,
downloads them to raw/assets/, and updates the links to point to local files.

Usage:
    python .opencode/skills/wiki-tools/scripts/download_images.py           # preview only (dry run)
    python .opencode/skills/wiki-tools/scripts/download_images.py --apply   # actually download and update
    python .opencode/skills/wiki-tools/scripts/download_images.py --help    # show help

Features:
    - Parses Markdown image links: ![alt](url) format
    - Downloads images to raw/assets/{md_filename}-{index}.{ext}
    - Updates md files to use local links: assets/{filename}-{index}.{ext}
    - Skips already downloaded images (checks local existence)
    - Supports common image formats: jpg, jpeg, png, gif, webp, svg
    - Handles URL query parameters (strips ?xxx part)
    - Clear progress output: found count, success/fail, updated links
"""

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import httpx

ROOT = Path(__file__).parent.parent.parent.parent.parent
RAW_DIR = ROOT / "raw"
ASSETS_DIR = ROOT / "raw" / "assets"
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "svg"}
SKIP_FILES = {"AGENTS.md"}
TIMEOUT = 30.0


def find_image_links(text: str) -> list[tuple[str, str, int, int]]:
    """
    Find all Markdown image links in text.

    Returns list of (alt_text, url, start_pos, end_pos) tuples.
    """
    pattern = r"!\[([^\]]*)\]\(([^)]+)\)"
    matches = []
    for m in re.finditer(pattern, text):
        url = m.group(2)
        # Check if URL looks like an image
        ext = get_extension_from_url(url)
        if ext in IMAGE_EXTENSIONS:
            matches.append((m.group(1), url, m.start(), m.end()))
    return matches


def get_extension_from_url(url: str) -> str:
    """
    Extract image extension from URL, stripping query parameters.

    Returns lowercase extension or empty string if not recognized.
    """
    # Strip query parameters
    clean_url = url.split("?")[0].split("#")[0]
    # Get path and extract extension
    path = urlparse(clean_url).path
    ext = Path(path).suffix.lower().lstrip(".")
    return ext if ext in IMAGE_EXTENSIONS else ""


def generate_local_filename(md_stem: str, index: int, ext: str) -> str:
    """
    Generate local filename for downloaded image.

    Format: {md_filename}-{index}.{ext}
    Example: github-oauth-第三方登录示例教程-1.jpg
    """
    return f"{md_stem}-{index}.{ext}"


def download_image(client: httpx.Client, url: str, dest_path: Path) -> bool:
    """
    Download image from URL to destination path.

    Returns True if successful, False otherwise.
    """
    try:
        response = client.get(url, timeout=TIMEOUT, follow_redirects=True)
        if response.status_code == 200:
            dest_path.write_bytes(response.content)
            return True
        print(f"    FAIL: HTTP {response.status_code}")
        return False
    except Exception as e:
        print(f"    FAIL: {e}")
        return False


def process_file(md_path: Path, apply: bool, client: httpx.Client) -> dict:
    """
    Process a single Markdown file.

    Returns dict with stats: found, downloaded, skipped, failed, updated.
    """
    text = md_path.read_text(encoding="utf-8")
    links = find_image_links(text)

    stats = {
        "found": len(links),
        "downloaded": 0,
        "skipped": 0,
        "failed": 0,
        "updated": 0,
    }

    if not links:
        return stats

    print(f"\n{md_path.name}:")
    print(f"  Found {len(links)} image(s)")

    replacements = []
    for i, (alt, url, start, end) in enumerate(links, 1):
        ext = get_extension_from_url(url)
        local_name = generate_local_filename(md_path.stem, i, ext)
        local_path = ASSETS_DIR / local_name
        local_link = f"assets/{local_name}"

        print(f"  [{i}] {url}")

        # Check if already exists
        if local_path.exists():
            print(f"    SKIP: already exists as {local_name}")
            stats["skipped"] += 1
            replacements.append((start, end, f"![{alt}]({local_link})"))
            continue

        if apply:
            # Download the image
            if download_image(client, url, local_path):
                print(f"    OK: saved as {local_name}")
                stats["downloaded"] += 1
                replacements.append((start, end, f"![{alt}]({local_link})"))
            else:
                stats["failed"] += 1
        else:
            # Dry run: just show what would happen
            print(f"    WOULD DOWNLOAD: → {local_name}")
            replacements.append((start, end, f"![{alt}]({local_link})"))

    # Update the file if we have replacements and apply mode
    if apply and replacements:
        # Sort by position (reverse) to avoid offset issues when replacing
        replacements.sort(key=lambda x: x[0], reverse=True)
        new_text = text
        for start, end, new_link in replacements:
            new_text = new_text[:start] + new_link + new_text[end:]
        if new_text != text:
            md_path.write_text(new_text, encoding="utf-8")
            stats["updated"] = len(replacements)
            print(f"  Updated {len(replacements)} link(s) in file")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Download images from raw/*.md files and update links",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s              Preview changes (dry run)
  %(prog)s --apply      Download images and update files
  %(prog)s --file foo.md  Process specific file only
        """,
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually download images and update Markdown files",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Process specific file only (default: all *.md in raw/)",
    )
    args = parser.parse_args()

    # Ensure assets directory exists
    if args.apply:
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # Get files to process
    if args.file:
        md_files = [RAW_DIR / args.file]
        if not md_files[0].exists():
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
    else:
        md_files = [p for p in sorted(RAW_DIR.glob("*.md")) if p.name not in SKIP_FILES]

    if not md_files:
        print("No Markdown files found in raw/")
        return

    # Create HTTP client
    client = httpx.Client(follow_redirects=True)

    # Process files
    total_stats = {"found": 0, "downloaded": 0, "skipped": 0, "failed": 0, "updated": 0}

    print(f"{'=' * 60}")
    print(f"Processing {len(md_files)} file(s) in raw/")
    print(
        f"Mode: {'APPLY (download and update)' if args.apply else 'DRY RUN (preview only)'}"
    )
    print(f"{'=' * 60}")

    for md_path in md_files:
        stats = process_file(md_path, args.apply, client)
        for key in total_stats:
            total_stats[key] += stats[key]

    # Summary
    print(f"\n{'=' * 60}")
    print("Summary:")
    print(f"  Images found:    {total_stats['found']}")
    print(f"  Downloaded:      {total_stats['downloaded']}")
    print(f"  Skipped (exist): {total_stats['skipped']}")
    print(f"  Failed:          {total_stats['failed']}")
    if args.apply:
        print(f"  Links updated:   {total_stats['updated']}")
    else:
        print(f"  Links to update: {total_stats['found'] - total_stats['failed']}")
        print("\nDry run. Use --apply to download and update files.")
    print(f"{'=' * 60}")

    client.close()


if __name__ == "__main__":
    main()
