#!/usr/bin/env python3
"""Minify css/style.css and js/main.js in place. Run ONLY in the CI build
workspace before `jekyll build` (see .github/workflows/jekyll-gh-pages.yml).
Source files in the repo are never minified; deploy output is.

Dependency-free on purpose: the deploy pipeline must not depend on npm.

Checks after minifying: CSS brace balance, JS paren/brace/bracket balance,
and a non-trivial size reduction. Aborts (exit 1) rather than ship a broken
file if any check fails.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def minify_css(src: str) -> str:
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    src = re.sub(r"\s+", " ", src)
    src = re.sub(r"\s*([{}:;,>~+])\s*", r"\1", src)
    src = src.replace(";}", "}")
    return src.strip()


def minify_js(src: str) -> str:
    # Conservative: strip full-line // comments and leading/trailing
    # whitespace only. Never touch inline comments or collapse newlines,
    # so string literals, regexes, and ASI behaviour stay intact.
    out_lines = []
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        out_lines.append(line.rstrip())
    out = "\n".join(out_lines)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip() + "\n"


def check_balanced(text: str, pairs: str) -> bool:
    counts = {c: 0 for c in pairs}
    for ch in text:
        if ch in counts:
            counts[ch] += 1
    return (
        counts["{"] == counts["}"]
        and counts["("] == counts[")"]
        and counts["["] == counts["]"]
    )


def process(rel: str, kind: str) -> None:
    path = ROOT / rel
    original = path.read_text(encoding="utf-8")
    minified = minify_css(original) if kind == "css" else minify_js(original)
    if kind == "css" and not check_balanced(minified, "{}()[]"):
        sys.exit(f"unbalanced braces in minified {rel}, aborting")
    if kind == "js" and not check_balanced(minified, "{}()[]"):
        sys.exit(f"unbalanced delimiters in minified {rel}, aborting")
    if len(minified) > len(original) * 0.98:
        sys.exit(f"minified {rel} is not smaller, aborting")
    path.write_text(minified, encoding="utf-8")
    print(f"{rel}: {len(original)} -> {len(minified)} bytes "
          f"({100 - len(minified) * 100 // len(original)}% smaller)")


if __name__ == "__main__":
    process("css/style.css", "css")
    process("js/main.js", "js")
