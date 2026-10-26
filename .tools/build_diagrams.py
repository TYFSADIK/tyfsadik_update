#!/usr/bin/env python3
"""Render the inline SVG diagrams defined in .tools/diagrams/specs/*.py into
their pages.

Each spec module sets PAGE (repo-relative html path) and DIAGRAMS (a list of
svgdiagram objects). In the page, a diagram lives in

    <figure class="diagram-figure" data-diagram="<uid>">
      <svg class="dg" ...>...</svg>        <- replaced on every run
      <figcaption class="diagram-caption">...</figcaption>   <- hand-written, kept
    </figure>

Usage:
  python3 .tools/build_diagrams.py            write all pages
  python3 .tools/build_diagrams.py --check    exit 1 if any page is stale
  python3 .tools/build_diagrams.py specs/x.py only the given spec files
"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent / "diagrams"
sys.path.insert(0, str(HERE))


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv):
    check = "--check" in argv
    files = [HERE / a for a in argv if a.endswith(".py")] or sorted((HERE / "specs").glob("*.py"))
    stale, written, total = [], 0, 0
    for f in files:
        mod = load(f)
        page = ROOT / mod.PAGE
        html = page.read_text(encoding="utf-8")
        out = html
        for d in mod.DIAGRAMS:
            total += 1
            svg = d.render()
            pat = re.compile(r'(<figure class="diagram-figure" data-diagram="' + re.escape(d.uid) + r'">\s*)(<svg class="dg".*?</svg>)?', re.S)
            if not pat.search(out):
                sys.exit(f"{mod.PAGE}: no <figure data-diagram=\"{d.uid}\"> placeholder")
            out = pat.sub(lambda m: m.group(1) + svg, out, count=1)
        if out != html:
            stale.append(mod.PAGE)
            if not check:
                page.write_text(out, encoding="utf-8")
                written += 1
    if check:
        if stale:
            print("stale diagrams (run python3 .tools/build_diagrams.py):", *stale, sep="\n  ")
            return 1
        print(f"{total} diagrams up to date")
        return 0
    print(f"{total} diagrams rendered, {written} pages written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
