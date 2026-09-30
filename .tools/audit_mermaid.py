#!/usr/bin/env python3
"""Find pages whose mermaid diagrams fail to render, and capture the error."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path('/Users/captain/Downloads/tyfsadik_update-main')
pages = [f for f in ROOT.rglob('*.html') if '.tools' not in f.parts
         and 'class="mermaid"' in f.read_text(encoding='utf-8', errors='ignore')]
print(f'{len(pages)} pages contain mermaid')

failures = {}
with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page()
    for f in pages:
        url = 'http://127.0.0.1:8325/' + f.relative_to(ROOT).as_posix()
        try:
            pg.goto(url, wait_until='networkidle', timeout=20000)
        except Exception:
            pass
        pg.wait_for_timeout(500)
        fails = pg.evaluate('''() => {
          const out = [];
          document.querySelectorAll('.mermaid').forEach((m, i) => {
            const t = m.innerText || '';
            if (t.includes('Syntax error in text')) out.push(i);
          });
          return { total: document.querySelectorAll('.mermaid').length, bad: out };
        }''')
        if fails['bad']:
            # capture the raw source of each failing diagram
            srcs = pg.evaluate('''(idxs) => idxs.map(i =>
              document.querySelectorAll('.mermaid')[i].textContent.trim().slice(0, 400))''', fails['bad'])
            failures[f.relative_to(ROOT).as_posix()] = srcs
            print('FAIL', f.relative_to(ROOT), fails)
    b.close()

Path('.tools/mermaid_failures.json').write_text(json.dumps(failures, indent=2))
print(f'{len(failures)} pages with broken diagrams -> .tools/mermaid_failures.json')
