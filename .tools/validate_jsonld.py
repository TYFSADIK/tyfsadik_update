#!/usr/bin/env python3
"""Parse every application/ld+json block in every HTML page.

Fails (exit 1) on invalid JSON, missing @context/@type, or a BreadcrumbList
whose items do not start at position 1. Prints a summary of schema types.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOCK = re.compile(
    r'<script type="application/ld\+json">(.*?)</script>', re.S)


def main() -> int:
    problems = []
    types = Counter()
    total = 0
    for page in sorted(ROOT.rglob("*.html")):
        if any(part in {".tools", "node_modules"} for part in page.parts):
            continue
        rel = page.relative_to(ROOT)
        for i, m in enumerate(BLOCK.finditer(page.read_text(encoding="utf-8"))):
            total += 1
            try:
                data = json.loads(m.group(1))
            except json.JSONDecodeError as e:
                problems.append(f"{rel} block {i}: invalid JSON: {e}")
                continue
            nodes = data.get("@graph", [data]) if isinstance(data, dict) else []
            for node in nodes:
                t = node.get("@type")
                if "@context" not in data:
                    problems.append(f"{rel} block {i}: missing @context")
                if not t:
                    problems.append(f"{rel} block {i}: node missing @type")
                    continue
                types[t if isinstance(t, str) else ",".join(t)] += 1
                if t == "BreadcrumbList":
                    pos = [it.get("position") for it in node.get("itemListElement", [])]
                    if pos and pos[0] != 1:
                        problems.append(f"{rel} block {i}: breadcrumb starts at {pos[0]}")
    print(f"{total} JSON-LD blocks checked")
    for t, n in types.most_common():
        print(f"  {t}: {n}")
    if problems:
        print("\n".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
