#!/usr/bin/env python3
"""
build_sitemap.py - regenerate sitemap.xml from the repo.

- Every public HTML page except 404.html (noindex) gets an entry.
- lastmod comes from git history (falls back to today).
- First local content image on the page is emitted as an image sitemap entry.
- Priority and changefreq follow the existing scheme: home 1.0 daily,
  top-level pages 0.8 weekly, work/defence 0.9 monthly, labs 0.7 monthly,
  assignments 0.6 monthly, docs 0.5 monthly.
"""

import re
import subprocess
from datetime import date
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://tyfsadik.org"


def lastmod(rel: str) -> str:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ad", "--date=short", "--", rel],
            capture_output=True, text=True, cwd=ROOT,
        ).stdout.strip()
        return out or str(date.today())
    except Exception:
        return str(date.today())


def priority_changefreq(rel: str):
    if rel == "index.html":
        return "1.0", "daily"
    if rel.startswith("work/defence/"):
        return "0.9", "monthly"
    if rel.startswith("work/"):
        return "0.8", "monthly"
    if rel.startswith("blog/labs/"):
        return "0.7", "monthly"
    if rel.startswith("blog/assignments/"):
        return "0.6", "monthly"
    if rel.startswith("docs/"):
        return "0.5", "monthly"
    return "0.8", "weekly"


def page_url(rel: str) -> str:
    if rel == "index.html":
        return BASE + "/"
    return f"{BASE}/{rel}"


def first_image(f: Path, rel: str, s: str):
    """First local, non-gif content image inside <main>, as absolute URL."""
    m = re.search(r"<main\b.*</main>", s, re.S)
    body = m.group(0) if m else s
    im = re.search(r'<img\b[^>]*src="([^"]+)"', body)
    if not im:
        return None
    u = im.group(1)
    if u.startswith("http") or u.lower().endswith(".gif"):
        return None
    p = (f.parent / u).resolve()
    try:
        relimg = p.relative_to(ROOT)
    except ValueError:
        return None
    if not p.exists():
        return None
    return BASE + "/" + quote(str(relimg))


def main():
    entries = []
    for f in sorted(ROOT.rglob("*.html")):
        if "node_modules" in f.parts or ".tools" in f.parts:
            continue
        rel = str(f.relative_to(ROOT))
        if rel == "404.html":
            continue
        s = f.read_text(encoding="utf-8")
        prio, freq = priority_changefreq(rel)
        img = first_image(f, rel, s)
        entries.append((page_url(rel), lastmod(rel), freq, prio, img))

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ]
    for loc, mod, freq, prio, img in entries:
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(loc)}</loc>")
        lines.append(f"    <lastmod>{mod}</lastmod>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"    <priority>{prio}</priority>")
        if img:
            lines.append("    <image:image>")
            lines.append(f"      <image:loc>{escape(img)}</image:loc>")
            lines.append("    </image:image>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"sitemap.xml: {len(entries)} URLs, {sum(1 for e in entries if e[4])} with images")


if __name__ == "__main__":
    main()
