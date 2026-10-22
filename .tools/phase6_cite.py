#!/usr/bin/env python3
"""
phase6_cite.py - add "Cite this page" blocks and author bylines to lab and
project pages (idempotent). Dates come from article:modified_time when
present, else git history.
"""

import html
import re
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUTHOR_PLAIN = "Taki Sadik"
AUTHOR_FULL = "MD. Taki Yasir Faraji Sadik"
TODAY = "2026-10-22"


def git_date(rel: str) -> str:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ad", "--date=short", "--", rel],
            capture_output=True, text=True, cwd=ROOT,
        ).stdout.strip()
        return out or TODAY
    except Exception:
        return TODAY


def main():
    targets = [f for f in ROOT.rglob("*.html")
               if (str(f.relative_to(ROOT)).startswith(("blog/labs/", "work/")))
               and "node_modules" not in f.parts]
    n_cite = n_byline = 0
    for f in sorted(targets):
        rel = str(f.relative_to(ROOT))
        s = f.read_text(encoding="utf-8")
        title_m = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
        if not title_m:
            continue
        title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip()
        mod_m = re.search(r'article:modified_time" content="([^"]+)"', s)
        mod = (mod_m.group(1)[:10] if mod_m else git_date(rel))
        year = mod[:4]
        url = "https://tyfsadik.org/" + ("" if rel == "index.html" else rel)
        slug = re.sub(r"[^a-z0-9]+", "-", Path(rel).stem.lower()).strip("-")
        depth = len(rel.split("/")) - 1
        about = "../" * depth + "about.html"

        if 'id="cite-this-page"' not in s:
            plain = f'{AUTHOR_PLAIN}, "{title}", TYFSADIK, {url} (accessed {TODAY}).'
            bib = (f"@misc{{sadik-{slug},\n"
                   f"  author  = {{Sadik, MD. Taki Yasir Faraji}},\n"
                   f"  title   = {{{title}}},\n"
                   f"  year    = {{{year}}},\n"
                   f"  url     = {{{url}}},\n"
                   f"  urldate = {{{TODAY}}}\n}}")
            apa = (f"Sadik, M. T. Y. F. ({year}). {title}. TYFSADIK. {url}")
            block = (
                '<section class="cite-this" id="cite-this-page">\n'
                '<h2>Cite This Page</h2>\n'
                f'<details><summary>Citation formats</summary>\n'
                f'<p><strong>Plain text</strong></p>\n<pre><code>{html.escape(plain)}</code></pre>\n'
                f'<p><strong>BibTeX</strong></p>\n<pre><code>{html.escape(bib)}</code></pre>\n'
                f'<p><strong>APA</strong></p>\n<pre><code>{html.escape(apa)}</code></pre>\n'
                '</details>\n</section>\n\n'
            )
            m = re.search(r"</div>\s*</div>\s*</main>", s)
            if m:
                s = s[: m.start()] + block + s[m.start():]
                n_cite += 1

        if 'class="byline"' not in s:
            byline = (f'<p class="byline">Written by <a href="{about}">{AUTHOR_PLAIN}</a>'
                      f' &middot; Last updated <time datetime="{mod}">{mod}</time></p>')
            s = s.replace(title_m.group(0), title_m.group(0) + "\n      " + byline, 1)
            n_byline += 1

        f.write_text(s, encoding="utf-8")
    print(f"cite blocks: {n_cite}, bylines: {n_byline}")


if __name__ == "__main__":
    main()
