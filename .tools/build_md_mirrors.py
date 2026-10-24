#!/usr/bin/env python3
"""
build_md_mirrors.py - generate clean markdown mirrors of key pages.

For each page in PAGES, writes a sibling .md file containing the main content
converted to markdown (headings, paragraphs, lists, links, code blocks,
tables, details/summary FAQs). Also writes llms-full.txt at the repo root
concatenating the key pages, and reports which pages got mirrors so
rel=alternate links can be added.

Deterministic and rerunnable: mirrors are fully regenerated each run.
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGES = [
    "index.html", "about.html", "work.html", "resume.html", "contact.html",
    "blog.html", "blog/labs/index.html",
    "blog/labs/linux-fundamentals/index.html",
    "blog/labs/linux-server/index.html",
    "blog/labs/networking/index.html",
    "blog/labs/security/index.html",
    "blog/labs/python/index.html",
    "blog/labs/databases/index.html",
    "blog/labs/cloud-azure/index.html",
    "blog/labs/containers-kubernetes/index.html",
    "blog/labs/devops/index.html",
    "docs/index.html", "docs/asset-register.html", "docs/glossary.html",
    "docs/decisions.html",
    "work/infrastructure/kubernetes-infrastructure.html",
    "work/infrastructure/proxmox-zero-trust.html",
    "work/infrastructure/chakor.html",
    "work/infrastructure/homelab-server-room.html",
] + [
    f"work/defence/{p}" for p in [
        "defence-hardware-program.html", "sky-passive-radar-node.html",
        "water-passive-acoustic-vessel-monitor.html",
        "ground-seismic-perimeter-mesh.html", "gps-denied-navigation-rover.html",
        "convoy-robots-degraded-mesh.html", "thermal-sar-drone.html",
        "acoustic-drone-detector.html", "cold-soak-battery-rig.html",
        "secure-fleet-updates.html", "airspace-deconfliction-manager.html",
        "arctic-domain-awareness.html", "ddil-proof-devops.html",
        "counter-drone-sensor-fusion.html", "decision-black-box.html",
        "zero-trust-air-gapped-supply-chain.html", "lentus-drone-mapping.html",
        "multi-domain-common-operating-picture.html",
        "arctic-isr-drone.html", "gps-denied-cargo-ugv.html",
        "seabed-survey-boat.html", "counter-drone-scoring-harness.html",
        "secure-fleet-autonomy.html", "sovereign-ai-enclave.html",
    ]
]


def text(el: str) -> str:
    el = re.sub(r"<[^>]+>", "", el)
    return html.unescape(el).strip()


def convert(page_html: str, base: str) -> str:
    m = re.search(r"<main\b.*?</main>", page_html, re.S)
    body = m.group(0) if m else page_html
    # drop navigation, scripts, styles, TOC, breadcrumbs
    body = re.sub(r"<script\b.*?</script>", "", body, flags=re.S)
    body = re.sub(r"<nav\b.*?</nav>", "", body, flags=re.S)
    body = re.sub(r'<button\b.*?</button>', "", body, flags=re.S)
    out = []
    token = re.compile(
        r"(<h[1-4][^>]*>.*?</h[1-4]>|<p\b.*?</p>|<li\b.*?</li>|<pre\b.*?</pre>|"
        r"<table\b.*?</table>|<details\b.*?</details>|<div class=\"lab-challenge\".*?</div>)",
        re.S,
    )
    for m in token.finditer(body):
        chunk = m.group(0)
        hm = re.match(r"<h([1-4])", chunk)
        if hm:
            out.append("#" * int(hm.group(1)) + " " + text(chunk))
        elif chunk.startswith("<p"):
            # keep links as [text](href)
            def link(mm):
                return f"[{text(mm.group(2))}]({mm.group(1)})"
            c = re.sub(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', link, chunk, flags=re.S)
            out.append(text(c))
        elif chunk.startswith("<li"):
            out.append("- " + text(chunk))
        elif chunk.startswith("<pre"):
            code = text(chunk)
            out.append("```\n" + code + "\n```")
        elif chunk.startswith("<table"):
            rows = re.findall(r"<tr[^>]*>(.*?)</tr>", chunk, re.S)
            table = []
            for i, r in enumerate(rows):
                cells = [text(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)]
                if not cells:
                    continue
                table.append("| " + " | ".join(cells) + " |")
                if i == 0:
                    table.append("|" + "|".join([" --- "] * len(cells)) + "|")
            if table:
                out.append("\n".join(table))
        elif chunk.startswith("<details"):
            q = re.search(r"<summary[^>]*>(.*?)</summary>", chunk, re.S)
            a = re.search(r"<p[^>]*>(.*?)</p>", chunk, re.S)
            if q:
                out.append("**Q: " + text(q.group(1)) + "**")
            if a:
                out.append("A: " + text(a.group(1)))
        else:
            t = text(chunk)
            if t:
                out.append(t)
    md = "\n\n".join(x for x in out if x)
    return md + "\n"


def main():
    mirrored = []
    for rel in PAGES:
        f = ROOT / rel
        if not f.exists():
            print("missing:", rel)
            continue
        s = f.read_text(encoding="utf-8")
        title = text(re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S).group(1)) if re.search(r"<h1", s) else rel
        conv = convert(s, rel)
        conv = re.sub(r"^# " + re.escape(title) + r"\n\n", "", conv)
        md = "# " + title + "\n\n" + conv
        target = f.with_suffix(".md")
        target.write_text(md, encoding="utf-8")
        mirrored.append(rel)

    # llms-full.txt concatenates the top-level key pages
    key = ["index.html", "about.html", "work.html", "blog/labs/index.html",
           "work/defence/defence-hardware-program.html",
           "work/infrastructure/kubernetes-infrastructure.html",
           "work/infrastructure/proxmox-zero-trust.html",
           "work/infrastructure/chakor.html",
           "work/infrastructure/homelab-server-room.html",
           "docs/asset-register.html"]
    parts = ["# TYFSADIK full-text mirror",
             "",
             "Complete markdown text of the key pages on tyfsadik.org.",
             "Author: MD. Taki Yasir Faraji Sadik (Taki Sadik), https://tyfsadik.org/",
             ""]
    for rel in key:
        f = ROOT / rel
        if f.exists():
            parts.append(f"\n\n---\n\n<!-- Source: https://tyfsadik.org/{'' if rel=='index.html' else rel} -->\n")
            title = text(re.search(r"<h1[^>]*>(.*?)</h1>", f.read_text(encoding='utf-8'), re.S).group(1)) if re.search(r"<h1", f.read_text(encoding='utf-8')) else rel
            parts.append("# " + title + "\n\n" + convert(f.read_text(encoding="utf-8"), rel))
    (ROOT / "llms-full.txt").write_text("\n".join(parts), encoding="utf-8")
    print(f"{len(mirrored)} .md mirrors + llms-full.txt written")


if __name__ == "__main__":
    main()
