#!/usr/bin/env python3
"""Cache-bust css/style.css and js/main.js. Run ONLY in the CI build
workspace, after minify_deploy.py and before `jekyll build` (see
.github/workflows/jekyll-gh-pages.yml). Source files are never stamped.

- Appends ?v=<hash> to every style.css / main.js reference in the HTML, so
  browsers fetch the new file as soon as it changes.
- Replaces the service worker cache name with tyfsadik-<hash>, so every deploy
  that changes an asset clears the previous caches on activation.

The hash covers the deployed CSS, JS and sw.js, so it only changes when one
of them does.
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {".tools", ".git", "_site", "node_modules"}

ASSET_REF = re.compile(r'((?:href|src)="[^"]*?(?:css/style\.css|js/main\.js))(?:\?v=[0-9a-f]+)?"')


def main() -> None:
    h = hashlib.sha256()
    for rel in ("css/style.css", "js/main.js", "sw.js"):
        h.update((ROOT / rel).read_bytes())
    version = h.hexdigest()[:10]

    pages = 0
    for f in ROOT.rglob("*.html"):
        if SKIP & set(f.relative_to(ROOT).parts):
            continue
        s = f.read_text(encoding="utf-8")
        out = ASSET_REF.sub(lambda m: f'{m.group(1)}?v={version}"', s)
        if out != s:
            f.write_text(out, encoding="utf-8")
            pages += 1

    sw = ROOT / "sw.js"
    s = sw.read_text(encoding="utf-8")
    out, n = re.subn(r"const CACHE = 'tyfsadik-[0-9a-z]+';", f"const CACHE = 'tyfsadik-{version}';", s)
    if not n:
        sys.exit("sw.js cache name placeholder not found, aborting")
    sw.write_text(out, encoding="utf-8")
    print(f"assets stamped v={version} on {pages} pages, sw cache tyfsadik-{version}")


if __name__ == "__main__":
    main()
