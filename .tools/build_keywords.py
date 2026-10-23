#!/usr/bin/env python3
"""
build_keywords.py - generate docs/seo/keywords-master.txt,
keyword-map.md, keyword-map.json, and entity-list.md from the actual site
content plus the seed bank. Primary keywords are derived from each page's
unique title, so no two pages share one (no cannibalization by construction).
"""

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEO = ROOT / "docs" / "seo"
SEO.mkdir(exist_ok=True)

SEED = """
Taki Sadik; MD Taki Yasir Faraji Sadik; TYFSADIK; Taki Sadik cybersecurity; Taki Sadik Toronto; Taki Sadik portfolio; Taki Sadik GitHub; Taki Sadik Chakor; Taki Sadik labs
cybersecurity professional Toronto; SOC analyst Toronto; incident analyst; incident response analyst; IT infrastructure engineer Toronto; network analyst; DevOps engineer Canada; defence tech builder; defence technology engineer Canada; AI developer Toronto; AI-enabled defender; self-hosted AI developer; cybersecurity portfolio; SOC analyst portfolio; DevOps portfolio; network security portfolio; homelab portfolio; IT portfolio website
Canadian Defence Hardware Program; Defence Drone Initiative Canada; MINERVA challenge Canadian Army; DND digital transformation; pan-domain operations; DDIL networks; denied degraded intermittent limited bandwidth; GPS-denied navigation; GPS-denied rover ROS 2; EKF drift measurement; passive radar KrakenSDR; pyAPRiL passive radar; passive aerial early warning; ADS-B ground truth; AIS vessel tracking; hydrophone vessel monitor; passive acoustic vessel classification; seismic perimeter mesh; LoRa ESP32 sensor mesh; acoustic drone detector; counter-drone detection; passive counter-drone; counter-drone sensor fusion simulator; Kalman filter sensor fusion; thermal search and rescue drone; Arctic ISR; Arctic domain awareness digital twin; Sentinel-1 dark vessel detection; cold-soak battery testing; cold weather drone battery dataset; secure OTA robot fleet updates; convoy robots degraded mesh; multi-domain common operating picture; zero-trust air-gapped supply chain; SBOM sigstore reproducible builds; tamper-evident hash-chained audit log; OPA policy checks; k3s edge nodes; store-and-forward DevOps; drone disaster mapping; LENTUS-style drone mapping
7-node Kubernetes cluster; Kubernetes homelab; Kubernetes on Proxmox; Ubuntu VMs Proxmox Kubernetes; Calico CNI; MetalLB; Longhorn storage; Prometheus Grafana homelab; Proxmox HA cluster; Proxmox zero trust; ZFS snapshot retention; Cloudflare Tunnel homelab; Tailscale fallback; no public IP homelab; VLAN segmentation homelab; self-hosted email server; self-hosted AI workspace; Chakor open-source AI chat; Next.js self-hosted AI
reduce SOC alert MTTR; Splunk SPL correlation; AlienVault OSSIM; automate security alert triage Python; SOC automation; false positive reduction; incident response lab; digital forensics lab; Linux hardening lab; security hardening checklist
Linux fundamentals labs; Linux server administration labs; systemd service lab; LVM lab; Linux users and permissions lab; shell scripting lab; cron scheduling lab; backup and restore lab; subnetting practice lab; VLAN lab; inter-VLAN routing lab; DHCP lab; DNS lab; Wireshark packet analysis lab; software-defined networking lab; Python automation sysadmin scripts; SQL normalization lab; database backup lab; Azure virtual network lab; ARM template lab; Azure Monitor lab; cloud security posture management lab; Docker Compose lab; Kubernetes pods and services lab; AKS autoscaling lab; Git branching workflow lab; GitHub Actions CI/CD pipeline lab; container scan and deploy pipeline
how to configure inter-VLAN routing; how to build a Kubernetes cluster on Proxmox; how to expose a homelab without a public IP; how to automate SOC alert triage with Python and Splunk; how to reduce SOC mean time to respond; what is passive radar; how does GPS-denied navigation work; how to detect drones by sound; what is DDIL; what is an SBOM; how to sign containers with sigstore; how to build a tamper-evident audit log; how to test drone batteries in the cold; how to self-host email; how to harden a Linux server
cybersecurity portfolio examples; IT portfolio website examples; developer portfolio dark terminal theme; Tokyo Night portfolio; homelab documentation examples; defence tech portfolio; best cybersecurity portfolio website
"""

QUESTION_TEMPLATES = [
    "how to {t}", "what is {t}", "how does {t} work", "{t} tutorial",
    "{t} step by step", "{t} example", "{t} explained", "{t} lab guide",
]


def clean(s: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", s)).strip()


def page_meta(f: Path):
    s = f.read_text(encoding="utf-8")
    t = re.search(r"<title>(.*?)</title>", s, re.S)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
    kw = re.search(r'<meta name="keywords" content="([^"]*)"', s)
    return {
        "title": clean(t.group(1)) if t else "",
        "h1": clean(h1.group(1)) if h1 else "",
        "keywords": [k.strip() for k in unescape(kw.group(1)).split(",")] if kw else [],
    }


def slug_topic(title: str) -> str:
    """Derive a topic phrase from a title like 'VLAN Configuration: X | Y'."""
    main = re.split(r"[|:-]", title)[0].strip().lower()
    return re.sub(r"\s+", " ", main)


def main():
    pages = {}
    all_kw = set()
    for f in sorted(ROOT.rglob("*.html")):
        if "node_modules" in f.parts or ".tools" in f.parts:
            continue
        rel = str(f.relative_to(ROOT))
        m = page_meta(f)
        topic = slug_topic(m["title"] or m["h1"])
        primary = topic if topic else m["h1"].lower()
        secondary = list(dict.fromkeys(m["keywords"]))[:6]
        long_tail = []
        for sec in secondary[:5]:
            for tmpl in ("{t} lab", "{t} guide", "{t} tutorial", "{t} explained", "{t} homelab"):
                long_tail.append(tmpl.format(t=sec))
        questions = [tmpl.format(t=topic) for tmpl in QUESTION_TEMPLATES[:6]] if topic else []
        pages[rel] = {
            "primary": primary,
            "secondary": secondary,
            "longTail": long_tail[:10],
            "questions": questions,
        }
        all_kw.add(primary)
        all_kw.update(secondary)
        all_kw.update(long_tail)
        all_kw.update(questions)

    for line in SEED.strip().splitlines():
        for phrase in line.split(";"):
            phrase = phrase.strip().lower()
            if phrase:
                all_kw.add(phrase)

    # master list
    master = sorted(all_kw)
    (SEO / "keywords-master.txt").write_text("\n".join(master) + "\n", encoding="utf-8")

    # keyword map
    (SEO / "keyword-map.json").write_text(json.dumps(pages, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Keyword map", "",
             "One primary keyword per page (derived from its unique title, so no two pages",
             "share one). Secondaries come from the page's existing keywords meta;", "",
             "| Page | Primary | Secondary | Long-tail | Questions |",
             "|---|---|---|---|---|"]
    for rel, kw in pages.items():
        lines.append(
            f"| {rel} | {kw['primary']} | {', '.join(kw['secondary'][:6])} | "
            f"{', '.join(kw['longTail'][:5])} | {', '.join(kw['questions'][:5])} |"
        )
    (SEO / "keyword-map.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # entity list from site-data tech stacks + tags
    data = json.loads((ROOT / "site-data.json").read_text(encoding="utf-8"))
    entities = sorted({t for p in data["projects"] for t in p.get("techStack", [])}
                      | {t for p in data["projects"] for t in p.get("tags", [])})
    el = ["# Entity list", "",
          "Every tool, standard, protocol, and product named in the site's project",
          "metadata. Used for about/mentions schema decisions and internal linking.", ""]
    for e in entities:
        el.append(f"- {e}")
    (SEO / "entity-list.md").write_text("\n".join(el) + "\n", encoding="utf-8")

    print(f"{len(master)} unique phrases | {len(pages)} pages mapped | {len(entities)} entities")


if __name__ == "__main__":
    main()
