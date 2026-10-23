#!/usr/bin/env python3
"""
phase3_meta.py - enforce sitewide metadata rules (idempotent).

Per page:
1. images/banner-mine.jpg becomes the FIRST og:image (1300x560) with
   width/height/type/alt; any existing page-specific og:image stays as a
   secondary image. twitter:image is set to banner-mine with image:alt.
2. Adds the standard extra-meta block (format-detection, color-scheme,
   referrer, application-name, geo, Dublin Core, apple/ms tags) after
   theme-color when missing.
3. Adds link rel=author (about page) and rel=me (GitHub, LinkedIn).
4. Adds article:modified_time from git history on article pages.
"""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANNER = "https://tyfsadik.org/images/banner-mine.jpg"
BANNER_ALT = "Taki Sadik at the beach, portfolio banner"

EXTRA_BLOCK = """  <meta name="format-detection" content="telephone=no">
  <meta name="color-scheme" content="dark">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta name="application-name" content="TYFSADIK">
  <meta name="geo.region" content="CA-ON">
  <meta name="geo.placename" content="North York, Toronto">
  <meta name="msapplication-TileColor" content="#333333">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-title" content="TYFSADIK">
"""


def git_modified(rel: str) -> str:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", rel],
            capture_output=True, text=True, cwd=ROOT,
        ).stdout.strip()
        return out
    except Exception:
        return ""


def main():
    for f in sorted(ROOT.rglob("*.html")):
        if "node_modules" in f.parts or ".tools" in f.parts:
            continue
        s = f.read_text(encoding="utf-8")
        rel = str(f.relative_to(ROOT))
        depth = len(rel.split("/")) - 1
        root = "../" * depth

        # 1. banner-mine first og:image
        if f'og:image" content="{BANNER}"' not in s:
            block = (
                f'  <meta property="og:image" content="{BANNER}">\n'
                f'  <meta property="og:image:width" content="1300">\n'
                f'  <meta property="og:image:height" content="560">\n'
                f'  <meta property="og:image:type" content="image/jpeg">\n'
                f'  <meta property="og:image:alt" content="{BANNER_ALT}">\n'
            )
            m = re.search(r'[ \t]*<meta property="og:image"', s)
            if m:
                s = s[: m.start()] + block + s[m.start():]
            else:
                # no og:image at all (404): append after og:url or description
                anchor = re.search(r'[ \t]*<meta name="robots"[^>]*>\n', s)
                if anchor:
                    s = s[: anchor.end()] + block + s[anchor.end():]
        # twitter:image -> banner-mine + alt
        if f'twitter:image" content="{BANNER}"' not in s:
            s = re.sub(
                r'<meta name="twitter:image" content="[^"]*">',
                f'<meta name="twitter:image" content="{BANNER}">\n'
                f'  <meta name="twitter:image:alt" content="{BANNER_ALT}">',
                s,
            )

        # 2. extra meta block
        if 'name="format-detection"' not in s:
            s = s.replace(
                '<meta name="theme-color" content="#333333">',
                '<meta name="theme-color" content="#333333">\n' + EXTRA_BLOCK.rstrip("\n"),
                1,
            )
        # Dublin Core (title mirrors the page title)
        if 'name="DC.title"' not in s:
            t = re.search(r"<title>(.*?)</title>", s, re.S)
            title = (t.group(1).strip() if t else "").replace('"', "&quot;")
            dc = (
                f'  <meta name="DC.title" content="{title}">\n'
                f'  <meta name="DC.creator" content="MD. Taki Yasir Faraji Sadik">\n'
                f'  <meta name="DC.language" content="en-CA">\n'
            )
            s = s.replace("</title>", "</title>\n" + dc.rstrip("\n"), 1)

        # 3. rel=author and rel=me
        if 'rel="author"' not in s:
            s = s.replace(
                '<link rel="canonical"',
                f'<link rel="author" href="{root}about.html">\n  <link rel="canonical"',
                1,
            )
        if 'rel="me"' not in s:
            me = (
                '  <link rel="me" href="https://github.com/TYFSADIK">\n'
                '  <link rel="me" href="https://www.linkedin.com/in/md-taki-yasir-faraji-sadik-63a026278/">\n'
            )
            s = re.sub(r"([ \t]*<link rel=\"canonical\")", me + r"\1", s, count=1)

        # 4. article:modified_time from git
        if "article:published_time" in s and "article:modified_time" not in s:
            mod = git_modified(rel)
            if mod:
                s = re.sub(
                    r'([ \t]*<meta property="article:published_time"[^>]*>)',
                    r"\1\n" + f'  <meta property="article:modified_time" content="{mod}">',
                    s,
                    count=1,
                )

        f.write_text(s, encoding="utf-8")
    print("phase3 meta pass complete")


if __name__ == "__main__":
    main()
