#!/usr/bin/env python3
"""Inject missing SEO tags (canonical, description, OG, Twitter, JSON-LD) into every page.

Only ADDS tags that are absent; never modifies existing ones.
"""
import glob, re, json, html as htmlmod

SITE = 'https://tyfsadik.org'
AUTHOR_JSON = '{"@type": "Person", "name": "MD. Taki Yasir Faraji Sadik", "url": "https://tyfsadik.org/about.html"}'

def canonical_for(path):
    if path == 'index.html':
        return SITE + '/'
    if path.endswith('/index.html'):
        return SITE + '/' + path[:-len('index.html')]
    return SITE + '/' + path

def text_of(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = htmlmod.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()

def esc(s):
    return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

pages = sorted(p for p in glob.glob('**/*.html', recursive=True) if not p.startswith('.tools/'))
stats = {'canonical': 0, 'description': 0, 'og': 0, 'twitter': 0, 'jsonld': 0}

for path in pages:
    src = open(path, encoding='utf-8').read()
    head_m = re.search(r'<head>(.*?)</head>', src, re.S)
    head = head_m.group(1)

    title_m = re.search(r'<title>(.*?)</title>', head, re.S)
    title_raw = title_m.group(1).strip() if title_m else ''
    title_txt = text_of(title_raw)

    desc_m = re.search(r'<meta name="description" content="([^"]*)"', head)
    canon_m = re.search(r'<link rel="canonical" href="([^"]*)"', head)

    inserts = []  # lines to inject

    # description
    desc_content = desc_m.group(1) if desc_m else None
    if desc_content is None:
        sub_m = re.search(r'<p class="subtitle">(.*?)</p>', src, re.S)
        if not sub_m:
            sub_m = re.search(r'<p>(.*?)</p>', src, re.S)
        derived = text_of(sub_m.group(1)) if sub_m else title_txt
        if len(derived) > 160:
            derived = derived[:157].rsplit(' ', 1)[0] + '...'
        desc_content = esc(derived)
        inserts.append(f'  <meta name="description" content="{desc_content}">')
        stats['description'] += 1

    # canonical
    canon_url = canon_m.group(1) if canon_m else None
    if canon_url is None:
        canon_url = canonical_for(path)
        inserts.append(f'  <link rel="canonical" href="{canon_url}">')
        stats['canonical'] += 1

    # og
    og_type = 'website' if path.endswith('index.html') or path in ('index.html',) else 'article'
    og_needed = []
    if 'property="og:title"' not in head:
        og_needed.append(f'  <meta property="og:title" content="{esc(title_txt)}">')
    if 'property="og:description"' not in head:
        og_needed.append(f'  <meta property="og:description" content="{desc_content}">')
    if 'property="og:url"' not in head:
        og_needed.append(f'  <meta property="og:url" content="{canon_url}">')
    if 'property="og:type"' not in head:
        og_needed.append(f'  <meta property="og:type" content="{og_type}">')
    if 'property="og:image"' not in head:
        og_needed.append(f'  <meta property="og:image" content="{SITE}/favicon.png">')
    if 'property="og:site_name"' not in head:
        og_needed.append('  <meta property="og:site_name" content="TYFSADIK">')
    if 'property="og:locale"' not in head:
        og_needed.append('  <meta property="og:locale" content="en_CA">')
    if og_needed:
        inserts.extend(og_needed)
        stats['og'] += 1

    # twitter
    tw_needed = []
    if 'name="twitter:card"' not in head:
        tw_needed.append('  <meta name="twitter:card" content="summary">')
    if 'name="twitter:title"' not in head:
        tw_needed.append(f'  <meta name="twitter:title" content="{esc(title_txt)}">')
    if 'name="twitter:description"' not in head:
        tw_needed.append(f'  <meta name="twitter:description" content="{desc_content}">')
    if 'name="twitter:image"' not in head:
        tw_needed.append(f'  <meta name="twitter:image" content="{SITE}/favicon.png">')
    if tw_needed:
        inserts.extend(tw_needed)
        stats['twitter'] += 1

    # JSON-LD (only for pages that have none)
    if 'application/ld+json' not in head:
        ld = ('{"@context": "https://schema.org", "@type": "CollectionPage", '
              f'"name": "{title_txt.replace(chr(34), chr(39))}", "url": "{canon_url}", '
              f'"description": "{text_of(desc_content).replace(chr(34), chr(39))}", '
              f'"author": {AUTHOR_JSON}}}')
        inserts.append(f'  <script type="application/ld+json">{ld}</script>')
        stats['jsonld'] += 1

    if not inserts:
        continue

    # anchor: after canonical link line, else after description line, else after title line
    lines = head.split('\n')
    anchor_idx = None
    for pat in (r'rel="canonical"', r'name="description"', r'<title>'):
        for i, ln in enumerate(lines):
            if re.search(pat, ln):
                anchor_idx = i
        if anchor_idx is not None:
            break
    assert anchor_idx is not None, path
    new_head_lines = lines[:anchor_idx + 1] + inserts + lines[anchor_idx + 1:]
    new_head = '\n'.join(new_head_lines)
    src = src.replace(head, new_head, 1)
    open(path, 'w', encoding='utf-8').write(src)

print(stats)
print('done')
