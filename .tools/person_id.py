#!/usr/bin/env python3
"""Round 5: consolidate the Person entity across all pages.

Adds "@id": "https://tyfsadik.org/#person" to every inline
author/about Person object in JSON-LD so all pages reference the single
canonical person entity defined on about.html. Additive only.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD = '"@type": "Person", "name": "MD. Taki Yasir Faraji Sadik"'
NEW = '"@type": "Person", "@id": "https://tyfsadik.org/#person", "name": "MD. Taki Yasir Faraji Sadik"'

changed_files = 0
total_refs = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in ('.tools', '.git', '__pycache__', 'round4-logs', '.github')]
    for fn in filenames:
        if not fn.endswith('.html'):
            continue
        p = os.path.join(dirpath, fn)
        with open(p, 'r', encoding='utf-8') as f:
            html = f.read()
        n = html.count(OLD)
        if n:
            html = html.replace(OLD, NEW)
            with open(p, 'w', encoding='utf-8') as f:
                f.write(html)
            changed_files += 1
            total_refs += n
print(f"updated {total_refs} Person references across {changed_files} files")
