#!/usr/bin/env python3
"""Rewrite internal page URLs to their extensionless ("pretty") form.

GitHub Pages serves foo.html at /foo, so the site links to /foo and declares
/foo as the canonical URL. Files keep their .html names on disk.

    about.html                     -> about
    blog/labs/index.html           -> blog/labs/
    https://tyfsadik.org/work.html -> https://tyfsadik.org/work
    https://tyfsadik.org/index.html -> https://tyfsadik.org/

Covered: href/src/action attributes in HTML, absolute https://tyfsadik.org
URLs anywhere (canonical, og:url, JSON-LD, sitemap, feeds, llms.txt, API),
"url"/"href" values in JSON, and Markdown links. 404.html and offline.html
keep their names (the server and the service worker use them as files).

site-data.json is the build tools' source (build_feeds.py reads its url
values as file paths), so it is only rewritten with --all, which the deploy
workflow passes after the builders have run.

Idempotent: running it twice changes nothing the second time.

Usage:
  python3 .tools/pretty_urls.py          rewrite the site (not site-data.json)
  python3 .tools/pretty_urls.py --all    also site-data.json (deploy only)
  python3 .tools/pretty_urls.py --check  exit 1 if anything would change
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".tools", "node_modules", "__pycache__", "round4-logs", "Prove", "tools", "images", "fonts"}
EXTS = {".html", ".xml", ".json", ".txt", ".md", ".webmanifest"}
KEEP = {"404.html", "offline.html"}
END = r"""(?=[#?"'<>\s)\]}&,;|`]|$)"""


def pretty(path):
    """foo/bar.html -> foo/bar ; foo/index.html -> foo/ ; index.html -> ./"""
    name = path.rsplit("/", 1)[-1]
    if name in KEEP:
        return path
    if name == "index.html":
        head = path[: -len("index.html")]
        return head if head else "./"
    return path[: -len(".html")]


ABS = re.compile(r"(https://tyfsadik\.org)(/[A-Za-z0-9_./%~-]*\.html)" + END)
ATTR = re.compile(r"""((?:href|src|action)=["'])(?![a-zA-Z][a-zA-Z0-9+.-]*:|//|#)([^"'#?\s]*\.html)""" + END)
JSON_URL = re.compile(r"""("(?:url|href)"\s*:\s*")(?![a-zA-Z][a-zA-Z0-9+.-]*:|//|#)([^"#?]+\.html)""" + END)
MD_LINK = re.compile(r"""(\]\()(?![a-zA-Z][a-zA-Z0-9+.-]*:|//|#)([^)#?\s]+\.html)""" + END)


def abs_sub(m):
    p = pretty(m.group(2))
    return m.group(1) + ("/" if p in ("/", "./") else p)


def rel_sub(m):
    return m.group(1) + pretty(m.group(2))


def rewrite(text, suffix):
    text = ABS.sub(abs_sub, text)
    if suffix == ".html":
        text = ATTR.sub(rel_sub, text)
    elif suffix in (".json", ".webmanifest"):
        text = JSON_URL.sub(rel_sub, text)
    elif suffix in (".md", ".txt"):
        text = MD_LINK.sub(rel_sub, text)
    return text


def files(include_site_data):
    for f in sorted(ROOT.rglob("*")):
        rel = f.relative_to(ROOT)
        if not f.is_file() or f.suffix not in EXTS or SKIP_DIRS & set(rel.parts[:-1]):
            continue
        if rel.as_posix() == "site-data.json" and not include_site_data:
            continue
        yield f


def main(argv):
    check, include = "--check" in argv, "--all" in argv
    changed = []
    for f in files(include):
        old = f.read_text(encoding="utf-8")
        new = rewrite(old, f.suffix)
        if new != old:
            changed.append(f.relative_to(ROOT).as_posix())
            if not check:
                f.write_text(new, encoding="utf-8")
    verb = "would change" if check else "rewrote"
    print(f"pretty_urls: {verb} {len(changed)} files")
    return 1 if (check and changed) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
