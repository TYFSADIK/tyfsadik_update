#!/usr/bin/env python3
"""
build_feeds.py - generate RSS 2.0 (feed.xml), Atom (atom.xml), and JSON Feed
(feed.json) from site-data.json. Covers projects and labs; items are dated
with the file's last git commit, falling back to site-data lastUpdated.
"""

import json
import subprocess
from email.utils import format_datetime
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://tyfsadik.org"
AUTHOR = "MD. Taki Yasir Faraji Sadik"


def git_date(rel: str) -> datetime:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", rel],
            capture_output=True, text=True, cwd=ROOT,
        ).stdout.strip()
        if out:
            return datetime.fromisoformat(out)
    except Exception:
        pass
    return datetime.now(timezone.utc)


def collect():
    data = json.loads((ROOT / "site-data.json").read_text(encoding="utf-8"))
    items = []
    for p in data["projects"]:
        rel = p["url"]
        dt = git_date(rel)
        items.append({
            "title": p["title"],
            "url": f"{BASE}/{rel}",
            "description": p["description"],
            "date": dt,
            "section": p["category"],
        })
    for lab in data["labs"]:
        rel = lab["url"]
        dt = git_date(rel)
        items.append({
            "title": f"{lab['title']} ({lab['category']} lab)",
            "url": f"{BASE}/{rel}",
            "description": lab["description"],
            "date": dt,
            "section": lab["category"],
        })
    items.sort(key=lambda x: x["date"], reverse=True)
    return items


def rss(items):
    now = format_datetime(datetime.now(timezone.utc))
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">', "<channel>",
           f"<title>TYFSADIK: Projects and Labs</title>",
           f"<link>{BASE}/</link>",
           "<description>Defence technology, infrastructure builds, and hands-on IT labs by MD. Taki Yasir Faraji Sadik.</description>",
           "<language>en-ca</language>",
           f"<lastBuildDate>{now}</lastBuildDate>",
           f'<atom:link href="{BASE}/feed.xml" rel="self" type="application/rss+xml"/>']
    for it in items:
        out.append("<item>")
        out.append(f"<title>{escape(it['title'])}</title>")
        out.append(f"<link>{escape(it['url'])}</link>")
        out.append(f'<guid isPermaLink="true">{escape(it["url"])}</guid>')
        out.append(f"<description>{escape(it['description'])}</description>")
        out.append(f"<category>{escape(it['section'])}</category>")
        out.append(f"<pubDate>{format_datetime(it['date'])}</pubDate>")
        out.append("</item>")
    out.append("</channel></rss>")
    return "\n".join(out) + "\n"


def atom(items):
    updated = max(i["date"] for i in items).isoformat()
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<feed xmlns="http://www.w3.org/2005/Atom">',
           "<title>TYFSADIK: Projects and Labs</title>",
           f'<link href="{BASE}/"/>',
           f'<link href="{BASE}/atom.xml" rel="self"/>',
           f"<id>{BASE}/</id>",
           f"<updated>{updated}</updated>",
           f"<author><name>{AUTHOR}</name></author>"]
    for it in items:
        out.append("<entry>")
        out.append(f"<title>{escape(it['title'])}</title>")
        out.append(f'<link href="{escape(it["url"])}"/>')
        out.append(f"<id>{escape(it['url'])}</id>")
        out.append(f"<updated>{it['date'].isoformat()}</updated>")
        out.append(f"<summary>{escape(it['description'])}</summary>")
        out.append(f'<category term="{escape(it["section"])}"/>')
        out.append("</entry>")
    out.append("</feed>")
    return "\n".join(out) + "\n"


def json_feed(items):
    return json.dumps({
        "version": "https://jsonfeed.org/version/1.1",
        "title": "TYFSADIK: Projects and Labs",
        "home_page_url": f"{BASE}/",
        "feed_url": f"{BASE}/feed.json",
        "description": "Defence technology, infrastructure builds, and hands-on IT labs by MD. Taki Yasir Faraji Sadik.",
        "authors": [{"name": AUTHOR, "url": f"{BASE}/about.html"}],
        "items": [{
            "id": it["url"],
            "url": it["url"],
            "title": it["title"],
            "summary": it["description"],
            "date_published": it["date"].isoformat(),
            "tags": [it["section"]],
        } for it in items],
    }, indent=1) + "\n"


def main():
    items = collect()
    (ROOT / "feed.xml").write_text(rss(items), encoding="utf-8")
    (ROOT / "atom.xml").write_text(atom(items), encoding="utf-8")
    (ROOT / "feed.json").write_text(json_feed(items), encoding="utf-8")
    print(f"feeds: {len(items)} items -> feed.xml, atom.xml, feed.json")


if __name__ == "__main__":
    main()
