#!/usr/bin/env python3
"""Per-project metadata enrichment for work/ and blog/labs/ pages.

For each page in docs/seo/keyword-map.json:
1. Merges the page's existing meta keywords with the map's primary,
   secondary, and long-tail phrases (deduped, capped at 25, all drawn from
   content that actually exists on the page or in site-data.json).
2. Enriches TechArticle JSON-LD: keywords array updated to match, plus an
   "about" list of Thing entities from docs/seo/entity-list.md that appear
   in the page's visible text (word-boundary match, cap 15).
3. Adds article:tag meta tags (first 5 keywords) on og:type=article pages.

No keywords are invented; every phrase comes from the keyword map, the
page's existing keywords, or the entity list.
"""
import html as html_mod
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KW_MAP = json.loads((ROOT / "docs/seo/keyword-map.json").read_text())
ENTITIES = [
    line[2:].strip()
    for line in (ROOT / "docs/seo/entity-list.md").read_text().splitlines()
    if line.startswith("- ")
]

LD_BLOCK = re.compile(
    r'<script type="application/ld\+json">(.*?)</script>', re.S)
KW_META = re.compile(r'<meta name="keywords" content="[^"]*">')
TAG_STRIP = re.compile(r"<[^>]+>")


def dedupe(phrases):
    seen, out = set(), []
    for p in phrases:
        p = p.strip()
        key = p.lower()
        if p and key not in seen:
            seen.add(key)
            out.append(p)
    return out


def page_entities(visible_text):
    found = []
    for ent in ENTITIES:
        if len(ent) < 3:
            continue
        if re.search(r"(?<![\w-])" + re.escape(ent) + r"(?![\w-])",
                     visible_text, re.I):
            found.append(ent)
        if len(found) >= 15:
            break
    return found


def process(rel):
    path = ROOT / rel
    if not path.exists():
        return None
    s = path.read_text(encoding="utf-8")
    entry = KW_MAP[rel]
    changed = False

    existing = []
    m = KW_META.search(s)
    if m:
        existing = html_mod.unescape(
            re.search(r'content="([^"]*)"', m.group(0)).group(1)
        ).split(", ")
    merged = dedupe(existing + [entry["primary"]] + entry["secondary"]
                    + entry["longTail"][:6])[:25]
    kw_content = html_mod.escape(", ".join(merged), quote=True)
    new_meta = f'<meta name="keywords" content="{kw_content}">'
    if m and m.group(0) != new_meta:
        s = s[:m.start()] + new_meta + s[m.end():]
        changed = True

    visible = TAG_STRIP.sub(" ", s)
    ents = page_entities(visible)

    def fix_ld(match):
        nonlocal changed
        raw = match.group(1)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)
        if not (isinstance(data, dict)
                and "TechArticle" in str(data.get("@type", ""))):
            return match.group(0)
        data["keywords"] = merged
        if ents:
            data["about"] = [{"@type": "Thing", "name": e} for e in ents]
        changed = True
        return ('<script type="application/ld+json">'
                + json.dumps(data, ensure_ascii=False) + "</script>")

    s = LD_BLOCK.sub(fix_ld, s)

    if ('property="og:type" content="article"' in s
            and 'article:tag' not in s):
        canon = re.search(
            r'<meta property="og:site_name" content="TYFSADIK">', s)
        tags = "".join(
            f'\n  <meta property="article:tag" content="{html_mod.escape(k, quote=True)}">'
            for k in merged[:5])
        if canon:
            s = s.replace(canon.group(0), canon.group(0) + tags)
            changed = True

    if changed:
        path.write_text(s, encoding="utf-8")
    return rel if changed else None


def main():
    done = [r for rel in KW_MAP
            if rel.startswith(("work/", "blog/labs/"))
            for r in [process(rel)] if r]
    print(f"enriched {len(done)} project/lab pages")


if __name__ == "__main__":
    main()
