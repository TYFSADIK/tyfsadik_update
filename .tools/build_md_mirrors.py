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
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Written by hand and kept here so a rebuild of llms-full.txt never drops it.
# Edit this text when roles, certifications or headline numbers change.
PROFILE = """## Profile summary

MD. Taki Yasir Faraji Sadik (Taki Sadik) is a defence researcher and a cybersecurity and
infrastructure engineer in Ontario, Canada, based in North York, Toronto.

- Roles: Defence Researcher; Cybersecurity and Infrastructure Engineer; Data Center Engineer at
  Microsoft; Senior IT Infrastructure Specialist at Amico Group of Companies (Richmond Hill, ON).
- Defence contract work: from time to time, private contract work with Lockheed Martin Canada
  Mission Systems in Ottawa (research support, systems work and security work), alongside his own
  personal defence research.
- Defence research: the Canadian Defence Hardware Program (eleven sensor and robotics builds
  across sky, water and ground) and six build guides written against Canada's 2027 MINERVA and
  IDEaS defence calls.
- Infrastructure: a 7-node Kubernetes cluster on Proxmox hosts, a zero-trust Proxmox private
  cloud, and nine self-hosted services.
- Open source: Daru (self-hosted SIEM) and Chakor (self-hosted AI workspace).
- Writing: 116 hands-on IT labs across nine tracks, from Linux to Kubernetes.
- Certifications: CompTIA Security+, Cisco CCNA, CompTIA A+, Microsoft AZ-900, AWS Cloud
  Practitioner and 25+ more; currently pursuing the CISSP.
- Education: University of Toronto (B.Eng, Information Technology); Seneca Polytechnic
  (postgraduate, Cyber/Electronic Operations).
- Languages: English, Bengali, Urdu, French.
- Contact: taki@tyfsadik.org, https://www.linkedin.com/in/md-taki-yasir-faraji-sadik-63a026278/,
  https://github.com/TYFSADIK
- Full project list: see "All projects" in the Projects section below ({count} projects).
"""

# Sections of the "All projects" list, in the order work.html shows them.
PROJECT_SECTIONS = [("Defence", "Defence & Sovereignty Tech"),
                    ("Infrastructure", "Homelab & Infrastructure"),
                    ("Web Dev", "Web Development"),
                    ("Games", "Games"),
                    ("Apps", "Applications")]


def load_projects() -> list:
    return json.loads((ROOT / "site-data.json").read_text(encoding="utf-8"))["projects"]


def project_catalogue(projects: list) -> str:
    """Every project from site-data.json, grouped by section, as markdown.

    work.html builds its cards in JavaScript, so convert() alone sees only the
    section headings; this list is what gives llms-full.txt the projects."""
    out = ["## All projects", "",
           f"Every project on https://tyfsadik.org/work, {len(projects)} in total, grouped by section.", ""]
    for cat, label in PROJECT_SECTIONS:
        group = [p for p in projects if p["category"] == cat]
        if not group:
            continue
        out += [f"### {label} ({len(group)})", ""]
        for p in group:
            url = "https://tyfsadik.org/" + p["url"].removesuffix(".html")
            meta = " · ".join(v for v in (p.get("year", ""), p.get("badge", "")) if v)
            out.append(f"- **{html.unescape(p['title'])}** ({meta}), {url}")
            out.append(f"  {html.unescape(p['description'])}")
            tech = p.get("techStack") or p.get("tags") or []
            if tech:
                out.append(f"  Tech: {', '.join(tech)}")
        out.append("")
    return "\n".join(out) + "\n"

# index, about, resume, contact and docs/ are deliberately not mirrored:
# their .md files were removed from the repo and must not be regenerated.
PAGES = [
    "work.html",
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
    "work/infrastructure/kubernetes-infrastructure.html",
    "work/infrastructure/proxmox-zero-trust.html",
    "work/infrastructure/chakor.html",
    "work/infrastructure/daru.html",
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
# Every project page gets a mirror too (AI assistants and agents read these).
PAGES += sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "work").glob("*/*.html")
                if p.relative_to(ROOT).as_posix() not in PAGES)


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
           "work/infrastructure/daru.html",
           "work/infrastructure/homelab-server-room.html",
           "docs/asset-register.html"]
    projects = load_projects()
    parts = ["# TYFSADIK full-text mirror",
             "",
             "Complete markdown text of the key pages on tyfsadik.org.",
             "Author: MD. Taki Yasir Faraji Sadik (Taki Sadik), https://tyfsadik.org/",
             "",
             PROFILE.format(count=len(projects))]
    for rel in key:
        f = ROOT / rel
        if f.exists():
            # Clean URLs, as the site serves them: about.html -> about, blog/labs/index.html -> blog/labs/
            url = re.sub(r"(^|/)index\.html$", r"\1", rel).removesuffix(".html")
            parts.append(f"\n\n---\n\n<!-- Source: https://tyfsadik.org/{url} -->\n")
            title = text(re.search(r"<h1[^>]*>(.*?)</h1>", f.read_text(encoding='utf-8'), re.S).group(1)) if re.search(r"<h1", f.read_text(encoding='utf-8')) else rel
            parts.append("# " + title + "\n\n" + convert(f.read_text(encoding="utf-8"), rel))
            if rel == "work.html":
                parts.append(project_catalogue(projects))
    (ROOT / "llms-full.txt").write_text("\n".join(parts), encoding="utf-8")
    print(f"{len(mirrored)} .md mirrors + llms-full.txt written")


if __name__ == "__main__":
    main()
