#!/usr/bin/env python3
"""Round 5b: link the square brand favicon variants and web manifest.

The original favicon.png link stays first on every page (unchanged). This
script APPENDS the Google-eligible square brand icons (favicon-48, icon-192,
icon-512, apple-touch-icon) plus the manifest, with the same relative-path
prefix the page already uses for favicon.png.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
            if rel == '404.html':
                m = re.search(r'^([ \t]*)<link rel="icon" href="/favicon\.png"[^\n]*$', html, re.M)
            else:
                m = re.search(r'^([ \t]*)<link rel="icon" href="([^"]*favicon\.png)"[^\n]*$', html, re.M)
            if not m:
                skipped.append(rel + '  (no favicon link found)')
                continue
            indent = m.group(1)
            prefix = '/' if rel == '404.html' else m.group(2)[:-len('favicon.png')]
            block = (
                f'{indent}<link rel="icon" type="image/png" sizes="48x48" href="{prefix}favicon-48.png">\n'
                f'{indent}<link rel="icon" type="image/png" sizes="192x192" href="{prefix}icon-192.png">\n'
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
