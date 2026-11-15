#!/usr/bin/env python3
"""Add the defence-technology-researcher identity and per-project schema.

Additive and idempotent: nothing is removed or reworded, and a second run
changes nothing.

1. Person entity (#person): jobTitle gains "Defence Technology Researcher"
   (the existing title is kept), plus hasOccupation and defence topics in
   knowsAbout. Inline author/about references to #person on every page get
   the same jobTitle so each page states the role on its own.
2. Project pages (work/*/*.html) get one extra JSON-LD block, built only
   from facts already on the page (canonical URL, h1, meta description,
   meta keywords, repository links):
     defence/            -> ResearchProject
     games/              -> VideoGame
     others with a repo  -> SoftwareSourceCode (codeRepository)
   Pages that already declare SoftwareApplication are left alone.
3. Meta keywords gain role and category phrases (deduplicated).
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PERSON_ID = "https://tyfsadik.org/#person"
NEW_TITLE = "Defence Technology Researcher"
OLD_TITLE = "Cybersecurity & IT Professional"
TITLES = [NEW_TITLE, OLD_TITLE]
DEFENCE_TOPICS = [
    "Defence technology research", "Passive radar", "Software-defined radio", "GPS-denied navigation",
    "Counter-drone detection", "Sensor fusion", "Arctic domain awareness", "DDIL networks",
    "Edge computing for defence", "Supply chain security",
]
OCCUPATION = {
    "@type": "Occupation",
    "name": "Defence technology researcher",
    "occupationLocation": {"@type": "Country", "name": "Canada"},
    "skills": DEFENCE_TOPICS[1:],
}
MARK = "seo-researcher"  # id of the added project JSON-LD block
CATEGORY_KW = {
    "defence": ["defence technology research", "defence tech researcher Canada", "Canadian defence research project",
                "Taki Sadik defence research"],
    "applications": ["software application project", "Taki Sadik project"],
    "infrastructure": ["infrastructure engineering project", "Taki Sadik project"],
    "web-development": ["web development project", "Taki Sadik project"],
    "games": ["game development project", "Taki Sadik project"],
}
LD = re.compile(r'(<script type="application/ld\+json"[^>]*>)(.*?)(</script>)', re.S)


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def enrich_person(node):
    """Full canonical Person definition (has jobTitle as data, not a reference)."""
    changed = False
    jt = node.get("jobTitle")
    titles = jt if isinstance(jt, list) else ([jt] if jt else [])
    if NEW_TITLE not in titles:
        node["jobTitle"] = [NEW_TITLE] + titles
        changed = True
    if "hasOccupation" not in node:
        node["hasOccupation"] = OCCUPATION
        changed = True
    ka = node.get("knowsAbout")
    if isinstance(ka, list):
        names = {k if isinstance(k, str) else k.get("name") for k in ka}
        add = [t for t in DEFENCE_TOPICS if t not in names]
        if add:
            node["knowsAbout"] = ka + add
            changed = True
    return changed


def walk(obj, fn):
    changed = False
    if isinstance(obj, dict):
        changed |= fn(obj)
        for v in obj.values():
            changed |= walk(v, fn)
    elif isinstance(obj, list):
        for v in obj:
            changed |= walk(v, fn)
    return changed


def person_fix(obj):
    if not (isinstance(obj, dict) and obj.get("@id") == PERSON_ID and obj.get("@type") == "Person"):
        return False
    if "jobTitle" in obj and "description" in obj:  # the full canonical definition
        return enrich_person(obj)
    jt = obj.get("jobTitle")
    if jt is None:
        obj["jobTitle"] = TITLES
        return True
    return False


def fix_jsonld(page):
    def rep(m):
        raw = m.group(2)
        try:
            data = json.loads(raw)
        except ValueError:
            return m.group(0)
        if not walk(data, person_fix):
            return m.group(0)
        compact = "\n" not in raw.strip()
        out = json.dumps(data, ensure_ascii=False, separators=(", ", ": ")) if compact else json.dumps(data, ensure_ascii=False, indent=2)
        return m.group(1) + ("" if compact else "\n") + out + ("" if compact else "\n") + m.group(3)
    return LD.sub(rep, page)


def meta(page, name):
    m = re.search(r'<meta name="%s" content="([^"]*)"' % re.escape(name), page)
    return html.unescape(m.group(1)) if m else ""


def project_block(page, rel):
    if f'id="{MARK}"' in page:
        return None
    cat = rel.split("/")[1]
    canon = re.search(r'<link rel="canonical" href="([^"]+)"', page).group(1)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
    name = text(h1.group(1)) if h1 else text(re.search(r"<title>(.*?)</title>", page, re.S).group(1)).split(" | ")[0]
    desc = meta(page, "description")
    kws = [k.strip() for k in meta(page, "keywords").split(",") if k.strip()]
    links = re.findall(r'href="https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/?"', page)
    upstream = {r.lower() for o, r in links if o.lower() != "tyfsadik"}
    repos = []
    for o, r in links:  # only the user's own repositories, in page order; skip forks of an upstream repo
        if o.lower() == "tyfsadik" and r.lower() not in upstream and f"https://github.com/{o}/{r}" not in repos:
            repos.append(f"https://github.com/{o}/{r}")
    author = {"@id": PERSON_ID}
    if cat == "defence":
        node = {"@type": "ResearchProject", "name": name, "url": canon, "description": desc,
                "founder": author, "member": author, "areaServed": {"@type": "Country", "name": "Canada"}}
    elif cat == "games":
        node = {"@type": "VideoGame", "name": name, "url": canon, "description": desc, "author": author}
    elif repos and not re.search(r'"@type":\s*"(SoftwareApplication|SoftwareSourceCode|VideoGame)"', page):
        node = {"@type": "SoftwareSourceCode", "name": name, "url": canon, "description": desc,
                "author": author, "codeRepository": repos[0]}
    else:
        return None
    if kws:
        node["keywords"] = kws
    node = {"@context": "https://schema.org", **node}
    return f'<script type="application/ld+json" id="{MARK}">' + json.dumps(node, ensure_ascii=False) + "</script>"


def add_keywords(page, rel):
    cat = rel.split("/")[1]
    m = re.search(r'(<meta name="keywords" content=")([^"]*)(")', page)
    if not m:
        return page
    have = [k.strip() for k in html.unescape(m.group(2)).split(",") if k.strip()]
    low = {k.lower() for k in have}
    add = [k for k in CATEGORY_KW.get(cat, []) if k.lower() not in low]
    if not add:
        return page
    new = ", ".join(have + add)
    return page[:m.start(2)] + html.escape(new, quote=False).replace('"', "&quot;") + page[m.end(2):]


def main(argv):
    check = "--check" in argv
    changed = []
    for f in sorted(ROOT.rglob("*.html")):
        rel = f.relative_to(ROOT).as_posix()
        if rel.startswith((".tools/", "node_modules/", "round4-logs/", "docs/baseline")):
            continue
        page = f.read_text(encoding="utf-8")
        new = fix_jsonld(page)
        if rel.startswith("work/") and rel.count("/") == 2:
            new = add_keywords(new, rel)
            block = project_block(new, rel)
            if block:
                new = new.replace("</head>", "  " + block + "\n</head>", 1)
        if new != page:
            changed.append(rel)
            if not check:
                f.write_text(new, encoding="utf-8")
    print(f"seo_researcher: {'would change' if check else 'updated'} {len(changed)} pages")
    return 1 if (check and changed) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
