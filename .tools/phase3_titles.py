#!/usr/bin/env python3
"""phase3_titles.py - bring titles to 50-60 chars and descriptions to
140-158 chars. Replaces the old string wherever it appears in the file
(title, DC.title, og:title, twitter:title, description, og:description,
twitter:description). Validates lengths at the end."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FIX = {
    "404.html": (
        "404 Page Not Found | Taki Sadik Portfolio, tyfsadik.org",
        "The page you requested was not found on tyfsadik.org. Return to the portfolio home page, or browse the projects, 116 hands-on labs, resume, and contact pages.",
    ),
    "about.html": (
        None,
        "About Taki Sadik, cybersecurity and IT professional in Toronto: Microsoft data center engineering, SOC incident analysis, SIEM, cloud, and networking.",
    ),
    "blog/assignments/milestone-1-vnet-vm.html": (
        None,
        "Azure milestone 1: create a virtual network, deploy a hardened virtual machine, and lock down access with network security groups in this guided assignment.",
    ),
    "blog/assignments/network-services-automation.html": (
        None,
        "Network services automation with Ansible: provision DNS, DHCP, and monitoring configurations consistently across servers with idempotent playbooks.",
    ),
    "blog/labs/containers-kubernetes/container-networking.html": (
        None,
        "Master Docker networking: user-defined bridges, embedded DNS, container-to-container connectivity, isolation tests, and publishing only what is needed.",
    ),
    "blog/labs/containers-kubernetes/kubernetes-networking.html": (
        None,
        "Learn Kubernetes networking by doing: ClusterIP, NodePort, and Ingress compared side by side, CoreDNS service discovery, and default-deny NetworkPolicies.",
    ),
    "blog/labs/containers-kubernetes/kubernetes-basics.html": (
        "Kubernetes Basics: kubectl, Cluster & First Pod | Taki Sadik",
        None,
    ),
    "blog/labs/containers-kubernetes/multi-container-apps.html": (
        None,
        "Run production-shaped multi-container stacks: reverse proxy routing, environment-driven config, runtime secrets, scaling stateless services, and teardown.",
    ),
    "blog/labs/databases/sql-fundamentals.html": (
        None,
        "Learn core SQL retrieval with SELECT, WHERE, GROUP BY, and indexes, then use EXPLAIN to turn full-table scans into fast index range scans, step by step.",
    ),
    "blog/labs/devops/branching-strategies.html": (
        None,
        "Compare GitHub Flow, trunk-based development, and GitFlow. Practice merge vs rebase and keep main releasable with short-lived branches in this lab.",
    ),
    "blog/labs/devops/cicd-pipeline.html": (
        None,
        "Build an end-to-end CI/CD pipeline with GitHub Actions: test, build, Trivy-scan, and deploy containers through gated, automated releases, commit to deploy.",
    ),
    "blog/labs/linux-fundamentals/index.html": (
        None,
        "24 hands-on Linux labs covering file management, shell scripting, text processing, permissions, virtualization, storage, and system administration basics.",
    ),
    "blog/labs/linux-fundamentals/redirection-pipelines.html": (
        "Linux Redirection & Pipelines: stdin, stdout | TYFSADIK",
        "Master Linux streams: stdin, stdout, stderr, file descriptors, pipes, and tee. Learn the redirection glue behind every filter and scripting lab you will run.",
    ),
    "blog/labs/linux-fundamentals/sed-awk.html": (
        "sed & awk: Stream Editing and Field Processing | TYFSADIK",
        None,
    ),
    "blog/labs/python/index.html": (
        None,
        "14 hands-on Python labs covering venvs, data types, control flow, OOP, file I/O, error handling, sysadmin scripting, CLI tools, and Git workflows.",
    ),
    "blog/labs/python/lists-dictionaries.html": (
        "Python Lists & Dictionaries: collections | TYFSADIK",
        None,
    ),
    "blog/labs/python/python-fundamentals.html": (
        "Python Fundamentals: venv, pip, Project Setup | TYFSADIK",
        None,
    ),
    "blog/labs/python/oop.html": (
        None,
        "Model a domain with Python classes, abstract base classes, and dataclasses, then use polymorphic dispatch for clean, extensible automation code you can test.",
    ),
    "blog/labs/security/threat-intelligence-frameworks.html": (
        None,
        "Work with threat intelligence frameworks: TAXII collection of STIX bundles, MISP import and correlation, and mapping indicators to ATT&CK techniques.",
    ),
    "blog.html": (
        None,
        "The TYFSADIK blog: 116 hands-on labs in Linux, networking, security, Python automation, databases, Azure, Docker, and Kubernetes by Taki Sadik.",
    ),
    "docs/asset-register.html": (
        "Infrastructure Asset Register | Taki Sadik Homelab Docs",
        "Physical and logical asset register for the TYFSADIK homelab: confirmed hardware, owner-stated expansion, GPU-stack feasibility, and storage capacity model.",
    ),
    "docs/decisions.html": (
        "Engineering Decision Records | Taki Sadik Portfolio",
        None,
    ),
    "docs/glossary.html": (
        "Engineering Glossary | Taki Sadik Portfolio, TYFSADIK",
        "Plain-language definitions of the networking, virtualization, storage, security, AI, and defence technology terms used across the TYFSADIK portfolio site.",
    ),
    "docs/index.html": (
        "Engineering Documentation Hub | Taki Sadik Portfolio",
        None,
    ),
    "work/defence/arctic-domain-awareness.html": (
        None,
        "Streaming pipeline fusing ADS-B aircraft data, AIS ship tracking, and Sentinel-1 radar imagery over Canada's North, with anomaly detection for dark vessels.",
    ),
    "work/defence/lentus-drone-mapping.html": (
        None,
        "Simulated drone flights with ArduPilot SITL and Gazebo map floods or wildfires; edge computer vision detects affected areas and feeds a live awareness map.",
    ),
    "work/defence/sky-passive-radar-node.html": (
        None,
        "Receive-only passive radar on a KrakenSDR 5-channel coherent SDR: broadcast reflections off aircraft, range-Doppler processing, scored against ADS-B truth.",
    ),
    "work/games/depot-gato.html": (
        None,
        "Depot Gato: a 2D tower defense game with wave spawning, tower placement, and pixel art, designed and built by MD. Taki Yasir Faraji Sadik, source included.",
    ),
    "work/infrastructure/arch-linux-remote-desktop.html": (
        None,
        "Arch Linux remote desktop via WSL2: a full XFCE desktop without router changes, documented step by step by MD. Taki Yasir Faraji Sadik, with tuning notes.",
    ),
    "work/infrastructure/email-server.html": (
        None,
        "Private email server: self-hosted SMTP and IMAP on the tyfsadik.org domain with spam filtering, TLS encryption, and backups, by Taki Sadik, with monitoring.",
    ),
    "work/infrastructure/homelab-server-room.html": (
        "Homelab Server Room: The Physical Build | Taki Sadik",
        "The physical build behind the TYFSADIK homelab: racked desktop and laptop Proxmox hosts, managed switching with VLAN trunking, wireless backhaul, and cooling.",
    ),
    "work/infrastructure/photo-server.html": (
        None,
        "Self-hosted photo server with ML face recognition at photo.tyfsadik.org: Immich deployment, hardware acceleration, and backup strategy, by Taki Sadik.",
    ),
    "work/web-development/faiaz-shisha.html": (
        None,
        "Faiaz Shisha: website for a shisha lounge with a flavour menu and booking, designed and developed by MD. Taki Yasir Faraji Sadik, source included.",
    ),
}


def esc(s: str) -> str:
    return s.replace("&", "&amp;")


def main():
    problems = []
    for page, (new_title, new_desc) in FIX.items():
        p = ROOT / page
        s = p.read_text(encoding="utf-8")
        if new_title:
            m = re.search(r"<title>(.*?)</title>", s, re.S)
            old = m.group(1).strip()
            s = s.replace(old, esc(new_title))
        if new_desc:
            m = re.search(r'<meta name="description" content="([^"]*)"', s)
            old = m.group(1)
            s = s.replace(old, esc(new_desc))
        p.write_text(s, encoding="utf-8")

    # validate every page
    for f in sorted(ROOT.rglob("*.html")):
        if "node_modules" in f.parts or ".tools" in f.parts:
            continue
        s = f.read_text(encoding="utf-8")
        t = re.search(r"<title>(.*?)</title>", s, re.S).group(1).strip()
        d = re.search(r'<meta name="description" content="([^"]*)"', s).group(1)
        t_plain = t.replace("&amp;", "&")
        d_plain = d.replace("&amp;", "&").replace("&#x27;", "'")
        if not (50 <= len(t_plain) <= 60):
            problems.append(f"title {len(t_plain):3d} {f}: {t_plain}")
        if not (140 <= len(d_plain) <= 158):
            problems.append(f"desc  {len(d_plain):3d} {f}")
    print("\n".join(problems) if problems else "all titles 50-60, all descriptions 140-158")
    return 1 if problems else 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
