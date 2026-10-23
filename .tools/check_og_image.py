#!/usr/bin/env python3
"""Verify hard rule 3: images/banner-mine.jpg is the FIRST og:image and the
twitter:image on every HTML page (404.html and offline.html included, minus
headless utility files)."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANNER = "https://tyfsadik.org/images/banner-mine.jpg"

problems = []
checked = 0
for page in sorted(ROOT.rglob("*.html")):
    if any(part in {".tools", "node_modules"} for part in page.parts):
        continue
    html = page.read_text(encoding="utf-8")
    rel = page.relative_to(ROOT)
    checked += 1
    ogs = re.findall(r'<meta property="og:image" content="([^"]+)"', html)
    tw = re.search(r'<meta name="twitter:image" content="([^"]+)"', html)
    if not ogs or ogs[0] != BANNER:
        problems.append(f"{rel}: first og:image is {ogs[0] if ogs else 'MISSING'}")
    if not tw or tw.group(1) != BANNER:
        problems.append(f"{rel}: twitter:image is {tw.group(1) if tw else 'MISSING'}")

print(f"og:image rule checked on {checked} pages")
if problems:
    print("\n".join(problems))
    sys.exit(1)
print("all pages: banner-mine.jpg first og:image and twitter:image")
