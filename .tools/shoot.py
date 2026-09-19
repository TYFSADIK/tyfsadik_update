#!/usr/bin/env python3
"""Screenshot one page per template at 1280 and 375 px."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8321'
OUT = Path('.tools/shots')
OUT.mkdir(parents=True, exist_ok=True)

PAGES = {
    'home':        '/index.html',
    'about':       '/about.html',
    'work':        '/work.html',
    'work-detail': '/work/infrastructure/kubernetes-infrastructure.html',
    'blog':        '/blog.html',
    'labs-index':  '/blog/labs/index.html',
    'lab':         '/blog/labs/linux-fundamentals/file-permissions.html',
    'assignment':  '/blog/assignments/capstone-cloud.html',
    'resume':      '/resume.html',
    'contact':     '/contact.html',
}

only = sys.argv[1:] or None
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    for name, path in PAGES.items():
        if only and name not in only:
            continue
        for w, h, tag in ((1280, 900, '1280'), (375, 800, '375')):
            page = browser.new_page(viewport={'width': w, 'height': h})
            page.goto(BASE + path, wait_until='networkidle')
            page.wait_for_timeout(700)
            page.screenshot(path=str(OUT / f'{name}-{tag}.png'), full_page=True)
            page.close()
        print('shot', name)
    browser.close()
