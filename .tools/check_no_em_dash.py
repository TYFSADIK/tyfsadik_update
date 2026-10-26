#!/usr/bin/env python3
"""Fail if any published file contains an em dash (U+2014, &mdash;, &#8212;).

House style: no em dashes anywhere on the site. Use a comma, colon,
parentheses, or a new sentence instead.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTS = {".html", ".md", ".txt", ".xml", ".json", ".webmanifest", ".vcf", ".js", ".css"}
SKIP = {".git", ".tools", "node_modules", "_site", "round4-logs"}
EM = re.compile(r"—|&mdash;|&#8212;|&#x2014;", re.I)


def main() -> int:
    hits = []
    for f in ROOT.rglob("*"):
        rel = f.relative_to(ROOT)
        if f.is_dir() or f.suffix not in EXTS or SKIP & set(rel.parts) or rel.parts[:2] == ("docs", "baseline"):
            continue
        for n, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if EM.search(line):
                hits.append(f"{rel}:{n}: {line.strip()[:120]}")
    if hits:
        print(f"{len(hits)} em dash(es) found:", *hits, sep="\n  ")
        return 1
    print("no em dashes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
