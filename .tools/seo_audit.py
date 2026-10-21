#!/usr/bin/env python3
"""Audit per-page SEO metadata across all HTML files."""
import glob, re, json
from html.parser import HTMLParser

class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_head = False
        self.in_title = False
        self.title = ''
        self.meta = {}          # (name|property) -> content
        self.canonical = None
        self.jsonld_types = []
        self._in_jsonld = False
        self._jsonld_buf = ''
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'head': self.in_head = True
        if not self.in_head: return
        if tag == 'title': self.in_title = True
        if tag == 'meta':
            key = a.get('name') or a.get('property')
            if key: self.meta[key] = a.get('content', '')
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical = a.get('href')
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self._in_jsonld = True; self._jsonld_buf = ''
    def handle_endtag(self, tag):
        if tag == 'head': self.in_head = False
        if tag == 'title': self.in_title = False
        if tag == 'script' and self._in_jsonld:
            self._in_jsonld = False
            try:
                data = json.loads(self._jsonld_buf)
                items = data if isinstance(data, list) else [data]
                for it in items:
                    if isinstance(it, dict): self.jsonld_types.append(it.get('@type'))
            except Exception:
                self.jsonld_types.append('UNPARSEABLE')
    def handle_data(self, d):
        if self.in_title: self.title += d
        if self._in_jsonld: self._jsonld_buf += d

pages = sorted(glob.glob('**/*.html', recursive=True))
pages = [p for p in pages if not p.startswith('.tools/')]
report = []
for p in pages:
    hp = HeadParser()
    hp.feed(open(p, encoding='utf-8').read())
    missing = []
    if not hp.title.strip(): missing.append('title')
    if 'description' not in hp.meta: missing.append('description')
    if not hp.canonical: missing.append('canonical')
    for og in ('og:title','og:description','og:url','og:type'):
        if og not in hp.meta: missing.append(og)
    if 'twitter:card' not in hp.meta: missing.append('twitter')
    if not hp.jsonld_types: missing.append('jsonld')
    report.append({'page': p, 'missing': missing,
                   'title': hp.title.strip()[:80],
                   'desc': (hp.meta.get('description') or '')[:100]})

full = [r for r in report if not r['missing']]
partial = [r for r in report if r['missing']]
print(f'total pages: {len(report)}')
print(f'fully covered: {len(full)}')
print(f'missing something: {len(partial)}')
from collections import Counter
c = Counter()
for r in partial:
    for m in r['missing']: c[m] += 1
print('missing counts:', dict(c))
json.dump(report, open('.tools/seo_audit.json','w'), indent=1)
print('-> .tools/seo_audit.json')
