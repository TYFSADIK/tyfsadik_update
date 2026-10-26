#!/usr/bin/env python3
"""
build_prerender.py - pre-render site-data.json content into index.html.

The homepage fills #recent-labs, #featured-projects, and the At a Glance
counters with JavaScript. With JavaScript disabled those areas were empty.
This script injects static HTML between PRERENDER marker comments so the page
is complete without JS. The runtime script still replaces the content via
innerHTML, so nothing is duplicated when JS runs.

Idempotent: re-run after editing site-data.json.
"""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
DATA = ROOT / "site-data.json"


def render_recent_labs(labs: list) -> str:
    items = []
    for lab in labs[:3]:
        title = html.escape(lab["title"])
        category = html.escape(lab["category"])
        description = html.escape(lab["description"])
        url = html.escape(lab["url"], quote=True)
        items.append(
            f'        <div class="news-item">\n'
            f'          <div class="news-date">{category}</div>\n'
            f'          <a class="news-title" href="{url}">{title}</a>\n'
            f'          <p>{description} <a href="{url}">Read the {title} lab</a></p>\n'
            f'        </div>'
        )
    return "\n".join(items)


def render_featured_projects(projects: list) -> str:
    cards = []
    for p in [p for p in projects if p.get("featured")][:6]:
        title = html.escape(p["title"])
        category = html.escape(p["category"])
        description = html.escape(p["description"])
        url = html.escape(p["url"], quote=True)
        meta = category
        if p.get("year"):
            meta += " &middot; " + html.escape(str(p["year"]))
        if p.get("badge"):
            meta += " &middot; " + html.escape(p["badge"])
        tags = "".join(
            f'<span class="tag">{html.escape(t)}</span>' for t in p.get("tags", [])
        )
        cards.append(
            f'  <a href="{url}" class="card">\n'
            f'    <div class="card-category">{meta}</div>\n'
            f'    <div class="card-title">{title}</div>\n'
            f'    <div class="card-description">{description}</div>\n'
            f'    <div class="tags">{tags}</div>\n'
            f'    <span class="read-more">Read more</span>\n'
            f'  </a>'
        )
    return "\n".join(cards)


def replace_block(source: str, name: str, content: str) -> str:
    pattern = re.compile(
        r"(<!-- PRERENDER:" + re.escape(name) + r" START -->).*?"
        r"(<!-- PRERENDER:" + re.escape(name) + r" END -->)",
        re.DOTALL,
    )
    if not pattern.search(source):
        raise SystemExit(f"marker block PRERENDER:{name} not found in index.html")
    return pattern.sub(lambda m: m.group(1) + "\n" + content + "\n" + m.group(2), source)


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    source = INDEX.read_text(encoding="utf-8")
    source = replace_block(source, "recent-labs", render_recent_labs(data["labs"]))
    source = replace_block(
        source, "featured-projects", render_featured_projects(data["projects"])
    )
    INDEX.write_text(source, encoding="utf-8")
    print("index.html: prerendered recent-labs and featured-projects from site-data.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
