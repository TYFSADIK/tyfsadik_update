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
from datetime import date
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


ABOUT = ROOT / "about.html"
# Taki started working in IT in 2022 (programming since grade 8 is not counted).
IT_START_YEAR = 2022


def compute_stats(data: dict) -> dict:
    """At a Glance numbers that should never go stale.

    years:    whole years since IT_START_YEAR, e.g. "4+" in 2026, "5+" in 2027
    certs:    active certifications listed on the About page
    projects: projects in site-data.json (the same list as the Work page)
    services: kept from site-data.json, edited by hand"""
    certs = len(re.findall(r'class="cert-item cert-active"', ABOUT.read_text(encoding="utf-8")))
    return {
        "years": f"{date.today().year - IT_START_YEAR}+",
        "certs": str(certs),
        "projects": str(len(data["projects"])),
        "services": str(data["stats"]["self_hosted_services"]),
    }


def set_stat(source: str, stat_id: str, value: str) -> str:
    pattern = re.compile(r'(<div class="stat-value" id="stat-' + stat_id + r'">)[^<]*(</div>)')
    if not pattern.search(source):
        raise SystemExit(f"#stat-{stat_id} not found in index.html")
    return pattern.sub(lambda m: m.group(1) + html.escape(value) + m.group(2), source)


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    source = INDEX.read_text(encoding="utf-8")
    source = replace_block(source, "recent-labs", render_recent_labs(data["labs"]))
    source = replace_block(
        source, "featured-projects", render_featured_projects(data["projects"])
    )
    stats = compute_stats(data)
    for stat_id, value in stats.items():
        source = set_stat(source, stat_id, value)
    INDEX.write_text(source, encoding="utf-8")

    # Keep site-data.json (read by build_api.py and the JSON API) in step.
    data["stats"].update({"years_in_it": stats["years"],
                          "certifications": stats["certs"],
                          "projects_built": stats["projects"]})
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("index.html: prerendered recent-labs, featured-projects and stats "
          f"(years {stats['years']}, certs {stats['certs']}, projects {stats['projects']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
