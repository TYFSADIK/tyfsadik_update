#!/usr/bin/env python3
"""
build_search_index.py - generate search-index.json for the static client-side
search on the labs index page. Covers labs, assignments, and projects.
No third-party calls; the browser fetches one small JSON file.
"""

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def clean(s: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", s)).strip()


def main():
    items = []
    for folder, kind in [("blog/labs", "lab"), ("blog/assignments", "assignment"), ("work", "project")]:
        for f in sorted((ROOT / folder).rglob("*.html")):
            if f.name == "index.html":
                continue
            s = f.read_text(encoding="utf-8")
            t = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
            d = re.search(r'<meta name="description" content="([^"]*)"', s)
            diff = re.search(r'class="difficulty difficulty-([a-z]+)"', s)
            cat = f.parent.name if f.parent.name not in ("labs", "assignments", "work") else f.parts[-2]
            items.append({
                "title": clean(t.group(1)) if t else f.stem,
                "url": str(f.relative_to(ROOT)),
                "kind": kind,
                "track": cat,
                "description": unescape(d.group(1)) if d else "",
                "difficulty": diff.group(1) if diff else "",
            })
    out = ROOT / "search-index.json"
    out.write_text(json.dumps(items, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"search-index.json: {len(items)} items, {out.stat().st_size} bytes")


if __name__ == "__main__":
    main()
