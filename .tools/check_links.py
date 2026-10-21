#!/usr/bin/env python3
"""Check every HTML page: internal links, images, css/js refs, nav consistency."""
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path('/Users/captain/Downloads/tyfsadik_update-main')

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.nav_links = []
        self.in_nav = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'ul' and 'nav-links' in a.get('class', ''):
            self.in_nav = True
        if self.in_nav and tag == 'a':
            self.nav_links.append(a.get('href', ''))
        for attr in ('href', 'src'):
            if attr in a:
                self.refs.append((tag, attr, a[attr]))
        if 'style' in a:
            for m in re.finditer(r"url\(['\"]?([^'\")]+)", a['style']):
                self.refs.append((tag, 'style', m.group(1)))
    def handle_endtag(self, tag):
        if tag == 'ul':
            self.in_nav = False

errors = []
nav_problems = []
EXPECT_NAV = {'about.html', 'work.html', 'blog.html', 'resume.html', 'contact.html'}
count = 0
for f in sorted(ROOT.rglob('*.html')):
    if '.tools' in f.parts:
        continue
    count += 1
    p = LinkParser()
    text = f.read_text(encoding='utf-8')
    p.feed(text)
    # nav check
    tails = {h.split('/')[-1] for h in p.nav_links}
    if tails != EXPECT_NAV:
        nav_problems.append((f.relative_to(ROOT), sorted(tails)))
    for tag, attr, ref in p.refs:
        if not ref or ref.startswith(('#', 'mailto:', 'tel:', 'data:', 'javascript:')):
            continue
        u = urlparse(ref)
        if u.scheme or u.netloc:
            continue
        target = (f.parent / u.path).resolve()
        if not target.exists():
            errors.append(f'{f.relative_to(ROOT)}: {tag}[{attr}] -> {ref} MISSING')

print(f'pages checked: {count}')
print(f'broken refs: {len(errors)}')
for e in errors:
    print(' ', e)
print(f'nav problems: {len(nav_problems)}')
for f, t in nav_problems[:10]:
    print(' ', f, t)
