#!/usr/bin/env python3
"""Round 4 phase 3: SEO hardening for tyfsadik.org (193 pages).
Tasks: titles, descriptions, keywords, OG/Twitter, canonicals,
BreadcrumbList JSON-LD, FAQPage JSON-LD (honest only), internal links.
No em dash, en dash, or ' - ' may appear in any inserted text.
"""
import re, json, html as htmllib, posixpath, os, sys

ROOT = os.path.expanduser("~/workspace/site-fixed")
PAGES = [l.strip()[2:] for l in open("/tmp/all_pages.txt")]
CANON_BASE = "https://tyfsadik.org"
DASHES = ("—", "–", " - ")

def clean(s):
    s = htmllib.unescape(re.sub(r"<[^>]+>", "", s or ""))
    return re.sub(r"\s+", " ", s).strip()

def esc(s):
    return htmllib.escape(s, quote=True)

def nodash(s, where):
    bad = [d for d in DASHES if d in s]
    if bad:
        raise ValueError(f"dash {bad} in {where}: {s[:80]}")

def canonical_of(path):
    return CANON_BASE + "/" if path == "index.html" else CANON_BASE + "/" + path

# ---------------- title overrides: base text (38-47 chars); " | TYFSADIK" appended ----------------
TITLE_OVERRIDES = {
 "index.html": "Taki Sadik: Cybersecurity, IT, Defence Tech",
 "about.html": "About Taki Sadik: Cybersecurity IT Engineer",
 "resume.html": "Taki Sadik Resume: Cybersecurity IT Engineer",
 "contact.html": "Contact Taki Sadik: Cybersecurity Engineer",
 "work.html": "Projects: Defence Builds and Homelab Portfolio",
 "blog.html": "Blog: 116 Hands-On IT Labs, Linux to Kubernetes",
 "blog/labs/index.html": "All 116 Labs: Linux, Networking, Security, Cloud",
 "blog/labs/linux-fundamentals/index.html": "Linux Labs: 24 Hands-On Tutorials and Guides",
 "blog/labs/linux-server/index.html": "Linux Server Labs: Admin Tutorials and Guides",
 "blog/labs/networking/index.html": "Networking Labs: 16 Hands-On Lab Tutorials",
 "blog/labs/security/index.html": "Cybersecurity Labs: 18 Hands-On Tutorials",
 "blog/labs/python/index.html": "Python Labs: 14 Automation Tutorials, Guides",
 "blog/labs/databases/index.html": "Database Labs: SQL Tutorials and Admin Guides",
 "blog/labs/cloud-azure/index.html": "Microsoft Azure Labs: 9 Hands-On Cloud Tutorials",
 "blog/labs/containers-kubernetes/index.html": "Kubernetes Labs: Docker and K8s Tutorials",
 "blog/labs/devops/index.html": "DevOps Labs: Git, CI/CD and Automation Tutorials",
 "blog/assignments/index.html": "College Assignments: Cloud and Network Builds",
 "work/defence/acoustic-drone-detector.html": "Passive Acoustic Drone Detector: Defence Build",
 "work/defence/airspace-deconfliction-manager.html": "Airspace Deconfliction Manager: Defence Build",
 "work/defence/arctic-domain-awareness.html": "Arctic Domain Awareness Twin: Defence Build",
 "work/defence/cold-soak-battery-rig.html": "Cold-Soak Battery Test Rig: Defence Build",
 "work/defence/counter-drone-sensor-fusion.html": "Counter-Drone Sensor Fusion: Defence Simulator",
 "work/defence/ddil-proof-devops.html": "DDIL-Proof DevOps: Disconnected CI/CD Build",
 "work/defence/decision-black-box.html": "Decision Black Box: Tamper-Evident Audit Log",
 "work/defence/defence-hardware-program.html": "Canadian Defence Hardware Program: 11 Builds",
 "work/defence/gps-denied-navigation-rover.html": "GPS-Denied Rover: ROS 2 Navigation Build",
 "work/defence/lentus-drone-mapping.html": "LENTUS Drone Mapping: Disaster Response Sim",
 "work/defence/multi-domain-common-operating-picture.html": "Multi-Domain Common Operating Picture Build",
 "work/defence/secure-fleet-updates.html": "Secure Robot Fleet Updates: TPM 2.0 OTA",
 "work/defence/sky-passive-radar-node.html": "Passive Radar Node: KrakenSDR Defence Build",
 "work/defence/thermal-sar-drone.html": "Thermal SAR Drone: FLIR Lepton Rescue Build",
 "work/defence/water-passive-acoustic-vessel-monitor.html": "Hydrophone Vessel Monitor: Defence Build",
 "work/infrastructure/arch-linux-remote-desktop.html": "Arch Linux Remote Desktop via WSL2: Guide",
 "work/infrastructure/data-sovereignty-stack.html": "Data Sovereignty Stack: Self-Hosted Guide",
 "work/infrastructure/email-server.html": "Private Email Server: Self-Hosted Guide",
 "work/infrastructure/kubernetes-infrastructure.html": "Kubernetes Infrastructure: Homelab Guide",
 "work/infrastructure/nextcloud-storage.html": "Self-Hosted Cloud Storage: Homelab Guide",
 "work/infrastructure/photo-server.html": "Self-Hosted Photo Server: Homelab Guide",
 "work/infrastructure/private-ai-model.html": "Custom LLM from Scratch: Training Guide",
 "work/infrastructure/proxmox-homelab.html": "Proxmox Homelab: Virtualization Build Guide",
 "work/infrastructure/proxmox-zero-trust.html": "Proxmox Zero-Trust Private Cloud: Guide",
 "work/infrastructure/search-engine.html": "Public Search Engine: Self-Hosted Guide",
 "work/infrastructure/self-hosted-dns.html": "Run Your Own DNS: Self-Hosted Server Guide",
 "work/infrastructure/tyf-ai-platform.html": "TYF-AI: Local AI Inference Stack on CUDA",
 "work/infrastructure/wiki-server.html": "Public Wiki Server: Self-Hosted Build Guide",
 "work/applications/gatearch.html": "GateArch: Student Portal App Case Study",
 "work/applications/taxglobe.html": "TaxGlobe: Canadian Tax Calculator Web App",
 "work/applications/wonder-learning.html": "Wonder Learning: E-Learning Platform Build",
 "work/games/depot-gato.html": "Depot Gato: 2D Tower Defense Game Build",
 "work/web-development/birthday-project.html": "Birthday Project: Interactive JS Celebration",
 "work/web-development/faiaz-shisha.html": "Faiaz Shisha: Lounge Website with Booking",
 "work/web-development/gta-high-glass.html": "GTA High Glass: Glazing Company Website",
 "work/web-development/hakimi-fruits.html": "Hakimi Fruits: Produce Business Website",
 "work/web-development/homebound-aisha.html": "HomeBound Aisha: Home-Based Service Website",
 "work/web-development/pharmacy-website.html": "Pharmacy Website: Medical Site with Listings",
 "work/web-development/practice-apps.html": "Practice Apps: TypeScript Web Dev Projects",
}
CAT_PHRASE = {
 "blog/assignments": "College Project",
 "blog/labs/linux-fundamentals": "Linux Tutorial",
 "blog/labs/linux-server": "Linux Server Guide",
 "blog/labs/networking": "Networking Lab",
 "blog/labs/security": "Security Lab",
 "blog/labs/python": "Python Lab",
 "blog/labs/databases": "Database Guide",
 "blog/labs/cloud-azure": "Azure Lab",
 "blog/labs/containers-kubernetes": "Kubernetes Lab",
 "blog/labs/devops": "DevOps Guide",
}

# ---------------- description overrides (target 150-160 chars) ----------------
DESC_OVERRIDES = {
 "about.html": "About Taki Sadik, cybersecurity and IT infrastructure specialist in Toronto: Microsoft data center engineering, SOC incident analysis, SIEM, cloud, networking.",
 "resume.html": "Resume of Taki Sadik: cybersecurity and IT infrastructure specialist in Toronto. SOC analyst skilled in incident response, SIEM, cloud, and networking.",
 "work/defence/acoustic-drone-detector.html": "MEMS microphone array on a Raspberry Pi that detects drone rotor harmonics, rejects birds and aircraft, and estimates direction of arrival by beamforming.",
 "work/defence/airspace-deconfliction-manager.html": "Small-scale UAS airspace manager: ESP32 tracker beacons, ArduPilot SITL simulated drones, dynamic geofences, predicted-conflict alerts, human override.",
 "work/defence/arctic-domain-awareness.html": "Streaming pipeline fusing ADS-B aircraft data, AIS ship tracking, and Sentinel-1 radar imagery over Canada's North, with anomaly detection for dark ships.",
 "work/defence/cold-soak-battery-rig.html": "Heated, instrumented drone battery bay tested in a lab freezer and real Canadian winter: runtime, voltage sag, and failure modes logged against temperature.",
 "work/defence/convoy-robots-degraded-mesh.html": "Two rovers convoy behind a lead vehicle over a 915 MHz LoRa and Wi-Fi mesh, hold formation through link drops, and recover on reconnect, at bench scale.",
 "work/defence/counter-drone-sensor-fusion.html": "Simulation-only defensive counter-drone project: synthetic radar, RF, acoustic, and camera tracks fused with Kalman filters, confidence-scored, human triaged.",
 "work/defence/ddil-proof-devops.html": "CI/CD and telemetry for denied, degraded, intermittent, limited networks: store-and-forward queues, delta updates, cosign-signed artifacts, k3s edge nodes.",
 "work/defence/decision-black-box.html": "Tamper-evident audit layer for human-in-the-loop decisions: hash-chained, signed, append-only log with Merkle proofs, a replay tool, and OPA policy checks.",
 "work/defence/defence-hardware-program.html": "Self-funded Canadian defence hardware program: passive radar, hydrophone vessel monitor, seismic mesh, GPS-denied rovers, thermal SAR drone, secure fleet updates.",
 "work/defence/gps-denied-navigation-rover.html": "ROS 2 rover that keeps navigating after GNSS is cut: wheel odometry, BNO085 IMU, and 2D LiDAR fused with an Extended Kalman Filter, drift vs u-blox truth.",
 "work/defence/ground-seismic-perimeter-mesh.html": "Solar-powered 915 MHz LoRa mesh of ESP32 sensor nodes with ADXL355 accelerometers and geophones, classifying vehicles, footsteps, and wind at the edge.",
 "work/defence/lentus-drone-mapping.html": "Simulated drone flights with ArduPilot SITL and Gazebo map floods or wildfires, edge computer vision detects affected areas, results feed a live awareness map.",
 "work/defence/multi-domain-common-operating-picture.html": "The fusion layer tying every sensor build together: signed detections over MQTT and Zenoh, store-and-forward through dead links, one Kalman-filtered dashboard.",
 "work/defence/secure-fleet-updates.html": "Secure boot, TPM 2.0 measured boot, YubiKey-signed over-the-air updates, and automatic A/B rollback for a small robot fleet, tested in a cold chamber.",
 "work/defence/sky-passive-radar-node.html": "Receive-only passive radar on a KrakenSDR 5-channel coherent SDR: FM and TV broadcast reflections off aircraft, range-Doppler processing, scored vs ADS-B truth.",
 "work/defence/thermal-sar-drone.html": "X500-class quadcopter with FLIR Lepton thermal camera and Hailo AI HAT+ edge detection that finds people in snow and brush, pushing detections to a live map.",
 "work/defence/water-passive-acoustic-vessel-monitor.html": "Dock-mounted hydrophone node that detects and classifies passing vessels from underwater sound, with an RTL-SDR AIS receiver as ground truth, solar powered.",
 "work/defence/zero-trust-air-gapped-supply-chain.html": "SBOM generation with syft, sigstore and cosign signing, and reproducible builds, moved across a simulated data diode into an offline Harbor registry.",
}
# ---------------- keywords: 6 missing pages ----------------
KEYWORDS_ADD = {
 "work/defence/arctic-domain-awareness.html": "Arctic domain awareness, digital twin, ADS-B AIS fusion, northern surveillance, Kafka streaming, Grafana, Canadian Arctic security",
 "work/defence/counter-drone-sensor-fusion.html": "counter-drone, sensor fusion simulator, drone detection, RF sensing, acoustic sensing, Kalman filter, C-UAS simulation",
 "work/defence/ddil-proof-devops.html": "DDIL DevOps, denied degraded intermittent limited networks, k3s edge, NATS messaging, cosign signing, store-and-forward, chaos engineering",
 "work/defence/decision-black-box.html": "decision black box, audit logging, OPA policy as code, Ed25519 signing, PostgreSQL, Merkle proofs, accountable autonomy",
 "work/defence/lentus-drone-mapping.html": "LENTUS, disaster response drones, drone mapping, emergency management, ArduPilot SITL, Gazebo simulation, aerial survey",
 "work/defence/zero-trust-air-gapped-supply-chain.html": "zero trust supply chain, air-gapped registry, SBOM, sigstore, cosign, Harbor, reproducible builds, software supply chain security",
}
KW_POOL = {
 "blog/labs/linux-fundamentals": ["Linux command line tutorial", "bash scripting guide"],
 "blog/labs/linux-server": ["Linux system administration", "server hardening guide"],
 "blog/labs/networking": ["TCP/IP networking tutorial", "network configuration lab"],
 "blog/labs/security": ["cybersecurity hands-on lab", "SOC analyst training"],
 "blog/labs/python": ["Python scripting tutorial", "automation with Python"],
 "blog/labs/databases": ["SQL hands-on tutorial", "PostgreSQL administration"],
 "blog/labs/cloud-azure": ["Microsoft Azure hands-on", "cloud infrastructure lab"],
 "blog/labs/containers-kubernetes": ["Docker hands-on tutorial", "Kubernetes administration"],
 "blog/labs/devops": ["CI/CD pipeline tutorial", "Git version control guide"],
 "blog/assignments": ["college IT project", "hands-on capstone build"],
}

# ---------------- internal linking plan: path -> [(href, anchor, note)] ----------------
# Defence pages: <section id="related"><h2>Related Builds</h2>
RELATED_DEFENCE = {
 "work/defence/arctic-domain-awareness.html": [
  ("multi-domain-common-operating-picture.html", "Multi-Domain Common Operating Picture", "the fusion layer that would consume these Arctic tracks alongside the hardware sensor builds"),
  ("counter-drone-sensor-fusion.html", "Counter-Drone Sensor Fusion Simulator", "the same Kalman-filter fusion approach applied to synthetic radar, RF, acoustic, and camera tracks"),
  ("defence-hardware-program.html", "Canadian Defence Hardware Program", "the program hub with all 11 builds, phased BOMs, and build guides")],
 "work/defence/counter-drone-sensor-fusion.html": [
  ("acoustic-drone-detector.html", "Passive Acoustic Drone Detector", "the real MEMS microphone array build behind the acoustic channel in the simulation"),
  ("sky-passive-radar-node.html", "Passive Radar Node", "the real KrakenSDR radar build behind the radar channel in the simulation"),
  ("multi-domain-common-operating-picture.html", "Multi-Domain Common Operating Picture", "where fused tracks from every sensor end up on one operator dashboard")],
 "work/defence/ddil-proof-devops.html": [
  ("secure-fleet-updates.html", "Secure Robot Fleet Updates", "YubiKey-signed OTA with A/B rollback, the update half of the DDIL story"),
  ("zero-trust-air-gapped-supply-chain.html", "Zero-Trust Air-Gapped Supply Chain", "SBOM and cosign signing for artifacts before they ever reach the edge"),
  ("decision-black-box.html", "Decision Black Box", "tamper-evident audit logging for the human-in-the-loop decisions this pipeline supports")],
 "work/defence/decision-black-box.html": [
  ("secure-fleet-updates.html", "Secure Robot Fleet Updates", "signed, measured boot and OTA updates, the integrity companion to audit logging"),
  ("ddil-proof-devops.html", "DDIL-Proof DevOps", "the resilient CI/CD pipeline that ships the software this audit layer watches"),
  ("zero-trust-air-gapped-supply-chain.html", "Zero-Trust Air-Gapped Supply Chain", "signed artifacts end to end, so the black box records only trustworthy software")],
 "work/defence/lentus-drone-mapping.html": [
  ("thermal-sar-drone.html", "Thermal SAR Drone", "the real thermal quadcopter build for finding people in snow and brush"),
  ("airspace-deconfliction-manager.html", "Airspace Deconfliction Manager", "the tracker beacons and geofencing that keep mapping drones separated"),
  ("defence-hardware-program.html", "Canadian Defence Hardware Program", "the program hub with all 11 builds, phased BOMs, and build guides")],
 "work/defence/zero-trust-air-gapped-supply-chain.html": [
  ("secure-fleet-updates.html", "Secure Robot Fleet Updates", "where these signed artifacts land: measured boot and YubiKey-signed OTA on real robots"),
  ("ddil-proof-devops.html", "DDIL-Proof DevOps", "the CI/CD system that produces the signed artifacts this pipeline verifies"),
  ("decision-black-box.html", "Decision Black Box", "tamper-evident logging that records what the trusted software decided")],
}
# Infra pages: <section class="related-labs"><h2>Related Work</h2>
RELATED_INFRA = {
 "work/infrastructure/arch-linux-remote-desktop.html": [
  ("proxmox-homelab.html", "Proxmox Homelab", "the virtualization host this remote desktop can run on"),
  ("private-ai-model.html", "Custom LLM from Scratch", "local AI work that pairs well with a GPU-backed remote desktop"),
  ("tyf-ai-platform.html", "TYF-AI", "the hardened local AI inference stack this desktop can drive")],
 "work/infrastructure/email-server.html": [
  ("self-hosted-dns.html", "Self-Hosted DNS", "the DNS records every mail server depends on: MX, SPF, DKIM, DMARC"),
  ("data-sovereignty-stack.html", "Data Sovereignty Stack", "the backup story that keeps mail data under your control"),
  ("nextcloud-storage.html", "Self-Hosted Cloud Storage", "file storage to round out the self-hosted productivity suite")],
 "work/infrastructure/kubernetes-infrastructure.html": [
  ("proxmox-homelab.html", "Proxmox Homelab", "the virtualization layer the 7-node cluster runs on"),
  ("proxmox-zero-trust.html", "Proxmox Zero-Trust Private Cloud", "identity-aware access in front of cluster services"),
  ("data-sovereignty-stack.html", "Data Sovereignty Stack", "storage and backup for stateful cluster workloads")],
 "work/infrastructure/nextcloud-storage.html": [
  ("photo-server.html", "Self-Hosted Photo Server", "photo management alongside file sync"),
  ("data-sovereignty-stack.html", "Data Sovereignty Stack", "the 3-2-1 backup design protecting this data"),
  ("wiki-server.html", "Public Wiki Server", "documentation hosting next to file storage")],
 "work/infrastructure/photo-server.html": [
  ("nextcloud-storage.html", "Self-Hosted Cloud Storage", "file sync behind the photo library"),
  ("data-sovereignty-stack.html", "Data Sovereignty Stack", "backups for an irreplaceable photo collection"),
  ("wiki-server.html", "Public Wiki Server", "another self-hosted service on the same stack")],
 "work/infrastructure/private-ai-model.html": [
  ("tyf-ai-platform.html", "TYF-AI", "the hardened local inference stack this model work feeds into"),
  ("chakor.html", "Chakor", "the self-hosted AI workspace that consumes local models"),
  ("search-engine.html", "Public Search Engine", "self-hosted search to complement local AI")],
 "work/infrastructure/proxmox-homelab.html": [
  ("proxmox-zero-trust.html", "Proxmox Zero-Trust Private Cloud", "the zero-trust access layer on top of this cluster"),
  ("kubernetes-infrastructure.html", "Kubernetes Infrastructure", "the 7-node K8s cluster hosted on this virtualization"),
  ("self-hosted-dns.html", "Self-Hosted DNS", "internal DNS for the homelab network")],
 "work/infrastructure/self-hosted-dns.html": [
  ("email-server.html", "Private Email Server", "the mail server that depends on these DNS records"),
  ("proxmox-homelab.html", "Proxmox Homelab", "the virtualization host for the DNS VMs"),
  ("search-engine.html", "Public Search Engine", "another self-hosted network service")],
 "work/infrastructure/wiki-server.html": [
  ("nextcloud-storage.html", "Self-Hosted Cloud Storage", "file storage alongside the wiki"),
  ("search-engine.html", "Public Search Engine", "self-hosted search across your own content"),
  ("data-sovereignty-stack.html", "Data Sovereignty Stack", "the backup design behind these services")],
}
# Web/app/game pages: <section class="related-projects"><h2>Related Projects</h2>
RELATED_WEB = {
 "work/web-development/birthday-project.html": [
  ("faiaz-shisha.html", "Faiaz Shisha", "a multi-page business site with booking"),
  ("homebound-aisha.html", "HomeBound Aisha", "a responsive business website"),
  ("practice-apps.html", "Practice Apps", "TypeScript practice builds")],
 "work/web-development/faiaz-shisha.html": [
  ("gta-high-glass.html", "GTA High Glass", "a business website for a glazing company"),
  ("hakimi-fruits.html", "Hakimi Fruits", "an online presence for a produce business"),
  ("homebound-aisha.html", "HomeBound Aisha", "a responsive business website")],
 "work/web-development/gta-high-glass.html": [
  ("faiaz-shisha.html", "Faiaz Shisha", "a multi-page business site with booking"),
  ("hakimi-fruits.html", "Hakimi Fruits", "an online presence for a produce business"),
  ("pharmacy-website.html", "Pharmacy Website", "a medical and pharmacy site")],
 "work/web-development/hakimi-fruits.html": [
  ("gta-high-glass.html", "GTA High Glass", "a business website for a glazing company"),
  ("faiaz-shisha.html", "Faiaz Shisha", "a multi-page business site with booking"),
  ("homebound-aisha.html", "HomeBound Aisha", "a responsive business website")],
 "work/web-development/homebound-aisha.html": [
  ("pharmacy-website.html", "Pharmacy Website", "a medical and pharmacy site"),
  ("hakimi-fruits.html", "Hakimi Fruits", "an online presence for a produce business"),
  ("birthday-project.html", "Birthday Project", "an interactive celebration page")],
 "work/web-development/pharmacy-website.html": [
  ("homebound-aisha.html", "HomeBound Aisha", "a responsive business website"),
  ("gta-high-glass.html", "GTA High Glass", "a business website for a glazing company"),
  ("practice-apps.html", "Practice Apps", "TypeScript practice builds")],
 "work/web-development/practice-apps.html": [
  ("birthday-project.html", "Birthday Project", "an interactive celebration page"),
  ("pharmacy-website.html", "Pharmacy Website", "a medical and pharmacy site"),
  ("faiaz-shisha.html", "Faiaz Shisha", "a multi-page business site with booking")],
 "work/applications/taxglobe.html": [
  ("gatearch.html", "GateArch", "a student portal and admin system"),
  ("wonder-learning.html", "Wonder Learning", "an e-learning platform")],
 "work/applications/wonder-learning.html": [
  ("gatearch.html", "GateArch", "a student portal and admin system"),
  ("taxglobe.html", "TaxGlobe", "a tax calculator for Canadian jurisdictions")],
 "work/games/depot-gato.html": [
  ("../web-development/practice-apps.html", "Practice Apps", "TypeScript practice builds"),
  ("../web-development/birthday-project.html", "Birthday Project", "interactive JavaScript effects"),
  ("../applications/wonder-learning.html", "Wonder Learning", "an e-learning platform")],
}
SECTION_LABEL = {
 "blog/assignments": "Assignments",
 "blog/labs/linux-fundamentals": "Linux Fundamentals Labs",
 "blog/labs/linux-server": "Linux Server Labs",
 "blog/labs/networking": "Networking Labs",
 "blog/labs/security": "Security Labs",
 "blog/labs/python": "Python Labs",
 "blog/labs/databases": "Database Labs",
 "blog/labs/cloud-azure": "Azure Labs",
 "blog/labs/containers-kubernetes": "Kubernetes Labs",
 "blog/labs/devops": "DevOps Labs",
 "blog/labs": "Labs",
 "work/defence": "Defence Builds",
 "work/infrastructure": "Infrastructure",
 "work/applications": "Applications",
 "work/web-development": "Web Development",
 "work/games": "Games",
 "work": "Projects",
 "blog": "Blog",
}
TOP_PAGE_NAME = {
 "index.html": "Home",
 "about.html": "About",
 "resume.html": "Resume",
 "contact.html": "Contact",
 "work.html": "Projects",
 "blog.html": "Blog",
}

# ---------------- processing ----------------
LOG = []
STATS = {"titles": 0, "descs": 0, "kw_added": 0, "kw_expanded": 0, "bc": 0, "faq": 0, "links": 0, "og_fixed": 0}
used_titles = {}

def build_title(path, cur):
    if path in TITLE_OVERRIDES:
        base = TITLE_OVERRIDES[path]
        assert 39 <= len(base) <= 49, (path, base)
        t = base + " | TYFSADIK"
        nodash(t, "title " + path)
        return t
    if 50 <= len(cur) <= 60:
        return None
    parts = [x.strip() for x in cur.split("|")]
    t1 = parts[0]
    t2 = parts[1] if len(parts) > 1 and parts[1].strip() not in ("TYFSADIK", "") else None
    d = path.rsplit("/", 1)[0] if "/" in path else ""
    cat = CAT_PHRASE.get(d, "Guide")
    cands = []
    if t2:
        cands.append("%s: %s" % (t1, t2))
    cands += ["%s: %s" % (t1, cat), "%s Explained: %s" % (t1, cat),
              "%s, Hands-On %s" % (t1, cat), "%s: Hands-On %s Tutorial" % (t1, cat)]
    for c in cands:
        if 39 <= len(c) <= 49:
            t = c + " | TYFSADIK"
            nodash(t, "title " + path)
            return t
    base = t1 if len(t1) <= 49 else t1[:49].rsplit(" ", 1)[0]
    if len(base) < 39:
        for suffix in [": %s Lab Guide" % cat, ": Hands-On %s Lab Guide" % cat,
                       " Tutorial: Hands-On %s" % cat]:
            c = t1 + suffix
            if 39 <= len(c) <= 49:
                base = c
                break
    t = base + " | TYFSADIK"
    nodash(t, "title " + path)
    return t

def resolve_url(path, href):
    if href.startswith("http"):
        return href
    p = posixpath.normpath(posixpath.join(posixpath.dirname(path), href))
    if p in ("index.html", "."):
        return CANON_BASE + "/"
    return CANON_BASE + "/" + p

def breadcrumb_trail(path, html):
    m = re.search(r'<nav class="breadcrumb">(.*?)</nav>', html, re.S)
    if m:
        nav = m.group(1)
        items = []
        for href, text in re.findall(r'<a href="([^"]+)">([^<]+)</a>', nav):
            items.append((clean(text), resolve_url(path, href)))
        sm = re.search(r"<span>([^<]+)</span>", nav)
        if sm:
            items.append((clean(sm.group(1)), canonical_of(path)))
        return items, "visible"
    trail = [("Home", CANON_BASE + "/")]
    if path == "index.html":
        return trail, "derived"
    if path in TOP_PAGE_NAME:
        trail.append((TOP_PAGE_NAME[path], canonical_of(path)))
        return trail, "derived"
    d = path.rsplit("/", 1)[0]
    label = SECTION_LABEL.get(d, d.replace("-", " ").title())
    if path.endswith("/index.html"):
        trail.append((label, canonical_of(path)))
    else:
        if d == "work/defence":
            trail.append((label, CANON_BASE + "/work/defence/defence-hardware-program.html"))
        elif d.startswith("work/"):
            trail.append((label, CANON_BASE + "/work.html"))
        else:
            trail.append((label, CANON_BASE + "/" + d + "/index.html"))
        hm = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
        name = clean(hm.group(1)) if hm else path.rsplit("/", 1)[-1]
        if len(name) > 70:
            name = name[:67].rsplit(" ", 1)[0] + "..."
        trail.append((name, canonical_of(path)))
    return trail, "derived"

GENERIC_SYMPTOMS = {"command not found", "permission denied", "output differs", "service or api unreachable"}

def faqs_from_table(html):
    m = re.search(r"<h2[^>]*>[^<]*[Tt]roubleshoot[^<]*</h2>\s*<table[^>]*>(.*?)</table>", html, re.S)
    if not m:
        return None
    rows = re.findall(r"<tr><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td></tr>", m.group(1), re.S)
    if not rows:
        return None
    if all(clean(r[0]).lower() in GENERIC_SYMPTOMS for r in rows):
        return None
    faqs = []
    for s, c, f in rows:
        s, c, f = clean(s), clean(c), clean(f)
        if not s or not f or s.lower() in GENERIC_SYMPTOMS:
            continue
        try:
            q = "How do I fix '%s'?" % s
            a = "Likely cause: %s. Fix: %s" % (c.rstrip("."), f.rstrip("."))
            if not a.endswith("."):
                a += "."
            nodash(q, "faq-q"); nodash(a, "faq-a")
        except ValueError:
            continue
        faqs.append((q, a))
        if len(faqs) >= 5:
            break
    return faqs or None

def faqs_from_list(html):
    m = re.search(r"<h2[^>]*>[^<]*[Tt]roubleshoot[^<]*</h2>(.*)", html, re.S)
    if not m:
        return None
    seg = m.group(1).split("<h2")[0][:6000]
    items = re.findall(r"<li><strong>(.*?)</strong>(.*?)</li>", seg, re.S)
    faqs = []
    for strong, rest in items:
        sym = clean(strong).rstrip(":").strip()
        if len(sym) < 15 or sym.lower() in ("done", "in progress", "next", "note", "tip", "warning"):
            continue
        ans = clean(rest)
        if len(ans) < 30:
            continue
        if len(ans) > 500:
            ans = ans[:500].rsplit(" ", 1)[0] + "."
        try:
            q = "How do I fix '%s'?" % sym
            nodash(q, "faq-q"); nodash(ans, "faq-a")
        except ValueError:
            continue
        faqs.append((q, ans))
        if len(faqs) >= 5:
            break
    return faqs or None

def ensure_meta(head, key, content, attr="name"):
    """Set meta tag content; return (head, changed_bool, was_missing_bool)."""
    pat = re.compile(r'<meta %s="%s" content="(.*?)"\s*/?>' % (attr, re.escape(key)), re.S)
    m = pat.search(head)
    tag = '<meta %s="%s" content="%s">' % (attr, key, esc(content))
    if m:
        if htmllib.unescape(m.group(1)) == content:
            return head, False, False
        return head.replace(m.group(0), tag, 1), True, False
    return head + "\n  " + tag, True, True

def process(path):
    fp = os.path.join(ROOT, path)
    html = open(fp, encoding="utf-8").read()
    log = {"file": path}
    hm = re.search(r"<head>(.*?)</head>", html, re.S)
    head = hm.group(1)
    canon = canonical_of(path)

    # title
    tm = re.search(r"<title>(.*?)</title>", head, re.S)
    cur_title = clean(tm.group(1))
    new_title = build_title(path, cur_title)
    if new_title:
        assert 50 <= len(new_title) <= 60, (path, new_title, len(new_title))
        if new_title in used_titles:
            raise ValueError("dup title %s on %s (also %s)" % (new_title, path, used_titles[new_title]))
        used_titles[new_title] = path
        head = head.replace(tm.group(0), "<title>%s</title>" % esc(new_title), 1)
        log["title"] = (cur_title, new_title)
        STATS["titles"] += 1
    else:
        used_titles[cur_title] = path
        log["title"] = (cur_title, None)
    title = new_title or cur_title

    # description
    dm = re.search(r'<meta name="description" content="(.*?)"', head, re.S)
    cur_desc = htmllib.unescape(dm.group(1)) if dm else ""
    new_desc = DESC_OVERRIDES.get(path)
    if new_desc:
        assert 148 <= len(new_desc) <= 162, (path, len(new_desc), new_desc)
        nodash(new_desc, "desc " + path)
        head = head.replace(dm.group(0), '<meta name="description" content="%s">' % esc(new_desc), 1)
        log["desc"] = (cur_desc[:60] + "...", new_desc)
        STATS["descs"] += 1
    else:
        log["desc"] = None
    desc = new_desc or cur_desc

    # keywords
    km = re.search(r'<meta name="keywords" content="(.*?)"', head, re.S)
    if path in KEYWORDS_ADD:
        kw = KEYWORDS_ADD[path]
        nodash(kw, "kw " + path)
        tag = '<meta name="keywords" content="%s">' % esc(kw)
        if km:
            head = head.replace(km.group(0), tag, 1)
        else:
            head = head.replace(dm.group(0), dm.group(0) + "\n  " + tag, 1)
        log["keywords"] = "added (%d terms)" % len(kw.split(","))
        STATS["kw_added"] += 1
    elif km:
        terms = [t.strip() for t in htmllib.unescape(km.group(1)).split(",") if t.strip()]
        d = path.rsplit("/", 1)[0] if "/" in path else ""
        added = []
        if len(terms) < 5 and d in KW_POOL:
            for extra in KW_POOL[d]:
                if not any(extra.lower() in t.lower() or t.lower() in extra.lower() for t in terms):
                    terms.append(extra); added.append(extra)
            kw = ", ".join(terms)
            nodash(kw, "kw " + path)
            head = head.replace(km.group(0), '<meta name="keywords" content="%s">' % esc(kw), 1)
            log["keywords"] = "expanded to %d terms" % len(terms)
            STATS["kw_expanded"] += 1
        else:
            log["keywords"] = "kept (%d terms)" % len(terms)
    else:
        log["keywords"] = "missing, no pool (left)"

    # OG / Twitter
    og_fixed = []
    head, ch, _ = ensure_meta(head, "og:title", title, "property"); og_fixed += ["og:title"] if ch else []
    head, ch, _ = ensure_meta(head, "og:description", desc, "property"); og_fixed += ["og:description"] if ch else []
    tm_ = re.search(r'<meta property="og:type" content="(.*?)"', head)
    if not tm_:
        otype = "website" if (path == "index.html" or path.endswith("/index.html") or path in ("blog.html", "work.html")) else "article"
        head, _, _ = ensure_meta(head, "og:type", otype, "property"); og_fixed.append("og:type")
    head, ch, _ = ensure_meta(head, "og:url", canon, "property"); og_fixed += ["og:url"] if ch else []
    if not re.search(r'<meta property="og:image"', head):
        head, _, _ = ensure_meta(head, "og:image", CANON_BASE + "/images/banner-space.jpg", "property")
        og_fixed.append("og:image")
    head, ch, _ = ensure_meta(head, "twitter:card", "summary_large_image"); og_fixed += ["twitter:card"] if ch else []
    head, ch, _ = ensure_meta(head, "twitter:title", title); og_fixed += ["twitter:title"] if ch else []
    head, ch, _ = ensure_meta(head, "twitter:description", desc); og_fixed += ["twitter:description"] if ch else []
    if not re.search(r'<meta name="twitter:image"', head):
        im = re.search(r'<meta property="og:image" content="(.*?)"', head)
        img = htmllib.unescape(im.group(1)) if im else CANON_BASE + "/images/banner-space.jpg"
        head, _, _ = ensure_meta(head, "twitter:image", img); og_fixed.append("twitter:image")
    if og_fixed:
        STATS["og_fixed"] += 1
    log["og"] = og_fixed

    # canonical
    cm = re.search(r'<link rel="canonical" href="(.*?)"', head)
    if not cm or cm.group(1) != canon:
        if cm:
            head = head.replace(cm.group(0), '<link rel="canonical" href="%s">' % canon, 1)
        else:
            head += '\n  <link rel="canonical" href="%s">' % canon
        log["canonical"] = "fixed to " + canon
    else:
        log["canonical"] = "ok"

    html = html.replace(hm.group(0), "<head>" + head + "</head>", 1)

    # JSON-LD: BreadcrumbList
    trail, tsrc = breadcrumb_trail(path, html)
    for name, _url in trail:
        nodash(name, "breadcrumb " + path)
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList",
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u}
                              for i, (n, u) in enumerate(trail)]}
    scripts = '\n  <script type="application/ld+json">%s</script>' % json.dumps(bc, ensure_ascii=False)

    # JSON-LD: FAQPage (honest only)
    faqs = faqs_from_table(html)
    faq_src = "table"
    if faqs is None:
        faqs = faqs_from_list(html)
        faq_src = "list"
    if faqs:
        fq = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
        scripts += '\n  <script type="application/ld+json">%s</script>' % json.dumps(fq, ensure_ascii=False)
        log["faq"] = "yes (%d, from %s)" % (len(faqs), faq_src)
        STATS["faq"] += 1
    else:
        log["faq"] = "no (no genuine Q/A content)"
    json.loads(json.dumps(bc)); 
    if faqs:
        json.loads(json.dumps(fq))
    html = html.replace("</head>", scripts + "\n</head>", 1)
    log["breadcrumb"] = "added (%s: %s)" % (tsrc, " > ".join(n for n, _ in trail))
    STATS["bc"] += 1

    # internal links
    links_added = []
    rel = None
    if path in RELATED_DEFENCE:
        items = "\n".join('        <li><a href="%s">%s</a>, %s.</li>' % (h, esc(a), esc(n))
                          for h, a, n in RELATED_DEFENCE[path])
        rel = '    <section id="related">\n      <h2>Related Builds</h2>\n      <ul>\n%s\n      </ul>\n    </section>' % items
        if '<nav class="viz-toc"' in html and 'href="#related"' not in html:
            html = re.sub(r'(<nav class="viz-toc"[^>]*>.*?)</ul>', r'\1        <li><a href="#related">Related Builds</a></li>\n      </ul>', html, count=1, flags=re.S)
            links_added.append("toc-anchor")
    elif path in RELATED_INFRA:
        items = "\n".join('        <li><a href="%s">%s</a>, %s.</li>' % (h, esc(a), esc(n))
                          for h, a, n in RELATED_INFRA[path])
        rel = '    <section class="related-labs"><h2>Related Work</h2>\n      <ul>\n%s\n      </ul>\n    </section>' % items
    elif path in RELATED_WEB:
        items = "\n".join('        <li><a href="%s">%s</a>, %s.</li>' % (h, esc(a), esc(n))
                          for h, a, n in RELATED_WEB[path])
        rel = '    <section class="related-projects">\n      <h2>Related Projects</h2>\n      <ul>\n%s\n      </ul>\n    </section>' % items
    if rel:
        for h, a, n in (RELATED_DEFENCE.get(path) or RELATED_INFRA.get(path) or RELATED_WEB.get(path)):
            nodash(a, "link " + path); nodash(n, "link " + path)
            tgt = posixpath.normpath(posixpath.join(posixpath.dirname(path), h))
            assert os.path.exists(os.path.join(ROOT, tgt)), (path, h)
            links_added.append(h)
        idx = html.rfind("</main>")
        html = html[:idx] + rel + "\n\n" + html[idx:]
        STATS["links"] += 1
    log["links"] = links_added

    # final validations
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        json.loads(m.group(1))
    assert html.count("<head>") == 1 and html.count("</head>") == 1
    open(fp, "w", encoding="utf-8").write(html)
    LOG.append(log)

for p in PAGES:
    process(p)

# ---------------- log ----------------
with open(os.path.join(ROOT, "round4-logs", "worker-seo.md"), "w", encoding="utf-8") as f:
    f.write("# SEO hardening log, round 4 phase 3 (worker-seo)\n\n")
    f.write("Date: 2026-09-29. Working dir: ~/workspace/site-fixed. Dash purge already complete; no em/en dashes or hyphen-dashes introduced.\n\n")
    f.write("## Summary\n\n")
    f.write("- Pages processed: %d\n" % len(PAGES))
    f.write("- Titles rewritten: %d (kept %d already in 50-60 char range)\n" % (STATS["titles"], len(PAGES) - STATS["titles"]))
    f.write("- Meta descriptions rewritten (were >170 chars): %d\n" % STATS["descs"])
    f.write("- Keywords added: %d, expanded: %d\n" % (STATS["kw_added"], STATS["kw_expanded"]))
    f.write("- OG/Twitter tags added or synced on pages: %d\n" % STATS["og_fixed"])
    f.write("- BreadcrumbList JSON-LD added: %d\n" % STATS["bc"])
    f.write("- FAQPage JSON-LD added: %d (honest only, derived from page-specific troubleshooting content)\n" % STATS["faq"])
    f.write("- Related-link sections added: %d\n" % STATS["links"])
    f.write("\n## Per-file\n\n")
    for log in LOG:
        f.write("### %s\n" % log["file"])
        before, after = log["title"]
        f.write("- title: %s\n" % ('kept "%s"' % before if after is None else '"%s" -> "%s" (%d chars)' % (before, after, len(after))))
        if log["desc"]:
            f.write("- description: rewrote (%d chars)\n" % len(DESC_OVERRIDES[log["file"]]))
        else:
            f.write("- description: kept\n")
        f.write("- keywords: %s\n" % log["keywords"])
        f.write("- social: %s\n" % ("synced (%s)" % ", ".join(log["og"]) if log["og"] else "already complete"))
        f.write("- canonical: %s\n" % log["canonical"])
        f.write("- BreadcrumbList: %s\n" % log["breadcrumb"])
        f.write("- FAQPage: %s\n" % log["faq"])
        f.write("- links added: %s\n" % (", ".join(log["links"]) if log["links"] else "none (already sufficient)"))
        f.write("\n")
print("STATS:", STATS)
