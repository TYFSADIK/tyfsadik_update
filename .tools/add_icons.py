#!/usr/bin/env python3
"""Round 5: add Google-eligible favicon variants and web manifest links.

The existing favicon.png (orange brand mark, 36x64) is kept untouched on
every page. This script APPENDS additional icon links derived from the real
headshot (Portrait.png) so the site has square icons at sizes Google Search
requires (multiple of 48x48) plus an apple-touch-icon and web manifest.

Insertion point: immediately after the existing `<link rel="icon" ...>`
line in each HTML page. Relative prefix matches the page depth, matching
the convention already used by the stylesheet and favicon links.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def rel_prefix(path):
    depth = path.count(os.sep)
    return "../" * depth

def main():
    changed, skipped = [], []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in ('.tools', '.git', '__pycache__', 'round4-logs', '.github')]
        for fn in filenames:
            if not fn.endswith('.html'):
                continue
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, ROOT)
            with open(p, 'r', encoding='utf-8') as f:
                html = f.read()
            if 'favicon-48.png' in html:
                skipped.append(rel)
                continue
            m = re.search(r'^([ \t]*)<link rel="icon" href="([^"]*favicon\.png)"[^\n]*$', html, re.M)
            if not m:
                skipped.append(rel + '  (no favicon link found)')
                continue
            indent, existing = m.group(1), m.group(2)
            prefix = existing[:-len('favicon.png')]  # e.g. "../../"
            block = (
                f'{indent}<link rel="icon" type="image/png" sizes="48x48" href="{prefix}favicon-48.png">\n'
                f'{indent}<link rel="icon" type="image/png" sizes="32x32" href="{prefix}favicon-32.png">\n'
                f'{indent}<link rel="icon" type="image/png" sizes="16x16" href="{prefix}favicon-16.png">\n'
                f'{indent}<link rel="apple-touch-icon" sizes="180x180" href="{prefix}apple-touch-icon.png">\n'
                f'{indent}<link rel="manifest" href="{prefix}site.webmanifest">'
            )
            html = html[:m.end()] + '\n' + block + html[m.end():]
            with open(p, 'w', encoding='utf-8') as f:
                f.write(html)
            changed.append(rel)
    print(f"updated: {len(changed)} pages")
    if skipped:
        print("skipped:")
        for s in skipped:
            print("  " + s)

if __name__ == '__main__':
    main()
