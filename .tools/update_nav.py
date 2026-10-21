#!/usr/bin/env python3
"""Restructure every HTML page's chrome for the littlesvr-style redesign.

Replaces <nav class="nav">...</nav> with the new header:
  top panel (site name + tagline + contact icon link)
  menu/banner panel (vertical nav box + per-section banner photo)
Also wraps main content in an inner .content-box div:
  <main class="page-content"><div class="container">[HERE]...</div></main>
Paths get the correct ../ prefix per folder depth. Idempotent.
"""
import re
import sys
from pathlib import Path

ROOT = Path('/Users/captain/Downloads/tyfsadik_update-main')

def prefix_for(path: Path) -> str:
    return '../' * (len(path.relative_to(ROOT).parts) - 1)

def section_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == 'about.html':   return 'about'
    if rel == 'work.html' or rel.startswith('work/'): return 'work'
    if rel == 'blog.html' or rel.startswith('blog/'): return 'blog'
    if rel == 'resume.html':  return 'resume'
    if rel == 'contact.html': return 'contact'
    return ''

NAV_ITEMS = [
    ('about',   'about.html',   'About Me'),
    ('work',    'work.html',    'Work'),
    ('blog',    'blog.html',    'Blog/Labs'),
    ('resume',  'resume.html',  'R&eacute;sum&eacute;'),
    ('contact', 'contact.html', 'Contact'),
]

def new_header(p: str, active: str, banner: str) -> str:
    items = '\n        '.join(
        f'<li><a href="{p}{href}" class="nav-link{" current" if key == active else ""}">{label}</a></li>'
        for key, href, label in NAV_ITEMS
    )
    return f'''<header class="site-header">
  <div class="top-panel">
    <div class="site-id">
      <a href="{p}index.html" class="site-name">Taki Sadik</a>
      <div class="site-tagline">Cybersecurity &amp; IT Professional &mdash; North York, ON, Canada</div>
    </div>
    <a href="{p}contact.html" class="contact-link" aria-label="Contact Taki Sadik"><span aria-hidden="true">&#9993;</span> <span class="contact-link-text">Contact</span></a>
  </div>
  <div class="menu-banner-panel">
    <nav class="nav" aria-label="Main navigation">
      <button class="nav-mobile-toggle" aria-expanded="false">MENU</button>
      <ul class="nav-links">
        {items}
      </ul>
    </nav>
    <div class="banner" style="background-image:url('{p}images/{banner}');" role="img" aria-label="Banner photo"></div>
  </div>
</header>'''

NAV_RE = re.compile(r'<nav class="nav">.*?</nav>', re.DOTALL)
MAIN_OPEN_RE = re.compile(r'(<main class="page-content">\s*<div class="container">)')

def process(path: Path, dry: bool) -> str:
    text = path.read_text(encoding='utf-8')
    if 'class="site-header"' in text:
        return 'skip(already)'
    if not NAV_RE.search(text):
        return 'NO-NAV'
    rel = path.relative_to(ROOT).as_posix()
    banner = 'banner-mine.jpg' if rel in ('index.html', 'about.html') else 'banner-space.jpg'
    text = NAV_RE.sub(lambda m: new_header(prefix_for(path), section_for(path), banner), text, count=1)
    # wrap content in .content-box
    text, n1 = MAIN_OPEN_RE.subn(r'\1\n    <div class="content-box">', text, count=1)
    if n1 == 0:
        return 'NO-MAIN'
    text, n2 = re.subn(r'</main>', '</div>\n</main>', text, count=1)
    if not dry:
        path.write_text(text, encoding='utf-8')
    return 'ok'

def main():
    dry = '--dry-run' in sys.argv
    files = [f for f in sorted(ROOT.rglob('*.html')) if '.tools' not in f.parts]
    counts = {}
    for f in files:
        r = process(f, dry)
        counts[r] = counts.get(r, 0) + 1
        if r != 'ok':
            print(f'{r}: {f.relative_to(ROOT)}')
    print(counts)

if __name__ == '__main__':
    main()
