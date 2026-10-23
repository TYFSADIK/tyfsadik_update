#!/usr/bin/env python3
"""Collect unique external links from all HTML pages and check their status.

Writes .tools/external-links.json mapping url -> {status, pages}.
Report-only: does not modify any page.
"""

import json
import re
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HREF = re.compile(r'href="(https?://[^"]+)"')

def collect():
    found = {}
    for f in sorted(ROOT.rglob("*.html")):
        if "node_modules" in f.parts:
            continue
        text = f.read_text(encoding="utf-8")
        for url in HREF.findall(text):
            url = url.split("#")[0]
            if "tyfsadik.org" in url:
                continue
            found.setdefault(url, []).append(str(f.relative_to(ROOT)))
    return found

def check(url):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0 (link checker)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.error.HTTPError as e:
        if e.code == 405:  # HEAD not allowed, try GET
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (link checker)"})
                with urllib.request.urlopen(req, timeout=15) as r:
                    return r.status
            except Exception as e2:
                return f"ERR {type(e2).__name__}"
        return e.code
    except Exception as e:
        return f"ERR {type(e).__name__}"

def main():
    found = collect()
    print(f"{len(found)} unique external URLs")
    results = {}
    with ThreadPoolExecutor(max_workers=12) as ex:
        for url, status in zip(found, ex.map(check, found)):
            results[url] = {"status": status, "pages": found[url][:5]}
            if status != 200:
                print(f"  {status}  {url}")
    out = ROOT / ".tools" / "external-links.json"
    out.write_text(json.dumps(results, indent=1))
    bad = {u: r for u, r in results.items() if r["status"] != 200}
    print(f"wrote {out}; {len(bad)} non-200")

if __name__ == "__main__":
    main()
