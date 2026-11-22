# Cyber Defence Decision Analysis and Response (CD-DAR) Testbed

Written by [Taki Sadik](../../about) · Last updated 2026-11-21 · Status: code ready, physical build next · 18 min read

A bench-scale defensive cyber operations testbed shaped by National Defence's CD-DAR project: network discovery, integrated open-source defence tools, a cyber data repository, a cyber common operating picture, remote forensics, and response actions that a human approves.

## Overview

The CD-DAR Testbed is a planned, bench-scale version of the capability National Defence
        describes in its Cyber Defence - Decision Analysis and Response project: see every device on
        a network, collect what the defence tools report into one trusted store, show it as a single
        cyber picture, and help an analyst decide what to do, fast. This page is a build guide;
        nothing here is built or tested yet.

CD-DAR is one of the largest cyber projects in the Defence Capabilities Blueprint, with a
        listed funding range of $250 million to $499 million and Assistant Deputy Minister (Digital
        Services) as the sponsoring group. Its goal is to improve decision support and security
        across DND/CAF networks so Defensive Cyber Operations (DCO) can detect, analyze and respond
        to threats in time. That is the same problem every security operations centre faces, at a
        much larger scale and with much higher stakes.

This build takes the public requirement list and answers each line with open-source tools
        on my own homelab: Zeek and Suricata on the wire, Wazuh and my own
        [Daru SIEM](../../work/infrastructure/daru) on the hosts, OpenSearch as the data
        repository, Grafana as the operating picture, Velociraptor for remote forensics, and TheHive
        for cases and response. The design rule throughout: the tools rank and explain, a
        person decides. Every response action needs human approval and is written to a
        tamper-evident log.

This is independent research, not part of the CD-DAR project. It uses only public
        information, synthetic data and my own machines. Where it stands: the whole
        testbed is now written as code: 86 files of Proxmox scripts, cloud-init, Docker stacks, data
        pipelines, three Python services and 29 automated tests that pass. What is left is the physical
        build and the first full run; nothing on this page is measured yet.

## The DND Project

The facts below come from the public CD-DAR entry in the Defence Capabilities Blueprint,
        managed by the Directorate of Capability Integration at National Defence.

| Item | Public detail |
| --- | --- |
| Project | Cyber Defence - Decision Analysis and Response (CD-DAR), new project |
| Sponsor | Assistant Deputy Minister (Digital Services) |
| Funding range | $250 million to $499 million |
| Networks in scope | Designated Command Network (Comd-Net) extensions and interfaces, and deployable Defence Wide Area Network (DWAN) systems |
| Options Analysis | Completed |
| Definition | In progress |
| Start of implementation | 2026/2027 |
| Initial delivery | 2029/2030 |
| Final delivery | 2030/2031 |
| Capability areas | C4I; Cyber, Electronic and Irregular Warfare; Emerging Technology; Training and Simulation |
| Key industrial capabilities | Artificial Intelligence; Cyber Resilience |

The requirement in plain words: DND/CAF need network discovery, integrated software cyber
        defence tools, an authoritative Cyber Data Repository (CDR), a Cyber Common Operating
        Picture (CyCOP), attention to the human factors of the analysts using it, and the ability to
        do cyber forensics remotely, giving full situational awareness and a timely response across
        strategic and operational cyber domains.

## Target Design

Each row maps one stated CD-DAR need to the component that answers it in this testbed.
        The [status table](#spec-gap) below tracks each one honestly.

| CD-DAR need | Testbed component | Design requirement |
| --- | --- | --- |
| Network discovery | Nmap, Zeek, NetBox | Scheduled active scans plus passive discovery from Zeek, reconciled against NetBox as the asset source of truth. Unknown devices raise an alert within one scan cycle. |
| Integrated cyber defence tools | Zeek, Suricata, Wazuh, Daru | Network sensors on a SPAN port and agents on every host, all feeding one pipeline instead of separate consoles. |
| Cyber Data Repository | Vector, Kafka, OpenSearch | Every event normalised to one schema (OCSF), tagged with its source and asset, kept with a stated retention, and searchable from one place. |
| Cyber Common Operating Picture | Grafana, OpenSearch Dashboards | One screen showing assets, live alerts, ATT&CK stage, and which mission-critical services each alert touches, refreshed in under a minute. |
| Decision analysis | Scoring service, MITRE ATT&CK | Each alert ranked by asset criticality, detection confidence and ATT&CK stage, with a plain-language reason shown next to the score. |
| Response | TheHive, Cortex, playbooks | Playbooks suggest actions (isolate host, block indicator, collect evidence); a person approves each one before it runs. |
| Remote forensics | Velociraptor | Collect memory, disk artefacts and logs from any enrolled host without being there, with every artefact hashed for chain of custody. |
| Human factors | Workload study | Analyst workload measured (alerts per hour, time per triage, NASA-TLX survey) so the tooling is judged on whether it helps people, not only on what it detects. |
| Deployable networks | k3s kit, store-and-forward | A small deployable sensor kit that keeps collecting when its link drops and syncs to the central repository when it returns. |

## Lab Layout

The whole lab runs on one Proxmox node behind its own router VM. Four networks keep the
        roles apart: management for the security tools, a notional command network of victims,
        an attacker network that can only reach the victims, and a physical field network behind
        the deployable kit, which comes home over WireGuard.

How the sensor sees traffic without a physical tap: the lab bridge is set to
        forget MAC addresses instantly (bridge-ageing 0), so it floods every frame to
        every port like an old hub. The sensor VM's capture card is a member of the victim and attacker
        VLANs, so Zeek and Suricata see everything between them. That trick is fine for a lab and
        never for production; the field kit uses a real switch mirror port instead.

| Network | Subnet | Machines | Can reach |
| --- | --- | --- | --- |
| VLAN 10 management | 10.10.10.0/24 | router, cddar-core, cddar-soc, cddar-sensor | Everything |
| VLAN 20 command (notional) | 10.10.20.0/24 | dc01, ws01, srv01, srv02 | Only the security agent ports, and the attacker's C2 ports so emulation agents can call back |
| VLAN 66 adversary | 10.10.66.0/24 | atk01 | The command network only; never management, never the internet during tests |
| Field network (physical) | 10.10.30.0/24 | kit01 and field devices | The internet through its own uplink; the lab only through WireGuard to Kafka, Wazuh and Velociraptor |
| WireGuard | 10.10.40.0/24 | kit01, analyst laptop | Kit: three service ports. Laptop: the web consoles |

The router's firewall is default-deny with one switch, lab-internet on|off: on while
        packages install, off before any attack test runs. Every address and name in the lab is synthetic.

## What the Build Will Prove

A homelab cannot stand in for a national defence network, and this one will not claim to.
        What it can prove, with published methods and data, is narrower and useful:

- One picture from many tools works. Network, host and forensic data from different tools land in one normalised repository and one operating picture, without analysts switching between consoles.

- Context speeds up decisions. Ranking alerts by asset criticality and ATT&CK stage, with a stated reason, is measured against a plain severity-sorted queue for time to triage and missed attacks.

- Discovery finds what the inventory misses. Planted unknown devices are found and flagged, and discovery completeness is measured against the known asset list.

- Forensics can be done remotely. Evidence is collected from a distant host in a measured time, with hashes that prove it was not changed.

- A person stays in charge. No response action runs without approval, and every decision can be replayed from the tamper-evident log.

## Architecture

Network sensorsZeek + Suricata on SPAN

Host agentsWazuh + Daru

DiscoveryNmap + passive Zeek

NetBoxasset source of truth

Deployable kitk3s, store-and-forward

PipelineVector + Kafka, OCSF schema

Cyber Data RepositoryOpenSearch

Cyber COPGrafana + Dashboards

Decision scoringcriticality x confidence x ATT&CK stage

Analystapproves every action

TheHive + Cortexcases and playbooks

Velociraptorremote forensics

Tamper-evident logdecision black box

Figure 2: sensors, host agents, discovery and the deployable kit all feed one pipeline into the Cyber Data Repository; the operating picture and decision scoring read from it; an analyst approves every response, and every approval and action is written to the tamper-evident log.

The data path is built around one rule: every tool writes into the same repository in the
        same schema. Zeek and Suricata watch traffic from a switch SPAN port, Wazuh and Daru watch
        the hosts, and discovery keeps NetBox current. Vector ships everything through Kafka,
        normalising it to OCSF on the way, so a login event from a firewall and a login event from
        a server look the same to the analyst.

On the decision side, a small scoring service reads new alerts, joins them to the asset's
        criticality in NetBox and to the ATT&CK technique, and writes back a score with a reason
        the analyst can read. The operating picture shows that ranked list beside the asset map.
        When the analyst opens a case, TheHive suggests playbook steps, Velociraptor collects
        evidence remotely, and nothing that changes a system runs until a person approves it.

Every event is stored in one schema, the Open Cybersecurity Schema Framework (OCSF):
        Zeek and Suricata flows become Network, DNS or HTTP Activity, and every alert from Suricata,
        Zeek, Wazuh or the discovery service becomes a Detection Finding with its ATT&CK technique.
        The mapping is written in Vector's language and ships with its own tests, so a broken mapping
        fails before it reaches the lab.

## Decision Scoring

CD-DAR asks for "reliable contextual analysis to support decisions". In this build that is a
        small scoring service. For every finding it multiplies four factors, each between 0 and 1, and
        takes the fourth root so the result reads on a 0 to 100 scale:

| Factor | Where it comes from | Example |
| --- | --- | --- |
| Asset criticality | NetBox custom field, 1 to 5, set per asset in inventory.yaml | dc01 = 5 (every login depends on it) |
| Attack stage | The ATT&CK tactic, from Discovery 0.40 to Exfiltration 0.95 and Impact 1.00 | Credential Access = 0.80 |
| Confidence | The sensor's own confidence, 0 to 100% | Suricata rule metadata "confidence High" = 90% |
| Severity | The sensor's severity, OCSF 1 to 5 | Wazuh level 12 = critical |

Multiplying means one weak factor pulls the score down hard, which is what an analyst would do
        in their head. If several different techniques hit the same asset within 30 minutes, the score
        rises by up to 15 points and says so. Scores of 60 or more open a TheHive alert; 80 or more are P1.

Every score carries its reasons, in plain words, into the alert the analyst reads:

[P1 92] LSASS access on dc01
- Asset dc01 has criticality 5/5.
- ATT&CK T1003.001 (Credential Access) is at attack stage 0.80.
- Detection confidence is 90%.
- Sensor severity is critical.
No response action has been taken.

## The Operating Picture

The Grafana dashboard has twelve panels, each answering one question an analyst asks:

- P1 findings, all findings, unknown devices, decisions logged: is anything on fire right now?

- Decision queue: every finding ranked by score, with the asset, ATT&CK technique and the reasons. This replaces the plain severity-sorted list most consoles show.

- Findings by ATT&CK tactic and over time by priority: how far along is an intruder, and is it getting worse?

- Most-targeted assets and top talkers: where is the activity concentrated?

- Network activity per sensor: a flat line means a sensor or its link is down, which matters for the deployable kit.

- Discovered devices and the approval log: what is on the network, and who decided what.

## How to Build It

The build splits into a physical part, which I do by hand over about one weekend, and a scripted
        part, which the repository does. Full step-by-step instructions, with the exact menu path for every
        setting, are in the docs/ folder of the [public repository on GitHub](https://github.com/TYFSADIK/cd-dar-testbed).

### Step 1: The physical part

- Proxmox node: free about 64 GB of RAM (47 GB with the lite profile) and 900 GB of disk on one node, enable Snippets on the local storage, and install git, rsync and genisoimage.

- Windows ISOs: download the free Windows Server 2022 and Windows 11 Enterprise evaluation images and virtio-win.iso, and upload them to Proxmox.

- Home router: give the lab router VM a DHCP reservation. Forward UDP 51820 to it only if the kit will sit on a different network.

- Field kit: install Ubuntu Server 24.04 on the mini PC with user lab and the Proxmox node's SSH key, then wire it as in Figure 6.

- Switch mirror port: on a TP-Link Easy Smart switch, Monitoring > Port Mirror: enable, destination port 2, sources ports 1 and 3 to 5, ingress and egress. Netgear calls it System > Monitoring > Mirroring.

- Windows installs: install Windows Server in dc01 and Windows 11 in ws01 from the Proxmox console, loading the vioscsi driver so the disk appears.

### Step 2: Build the lab (scripted)

cp lab.env.example lab.env          # set node name, storage, SSH key
./proxmox/setup-lab-bridge.sh        # isolated VLAN-aware bridge in hub mode
./proxmox/create-lab.sh              # router, core, soc, sensor, srv01, srv02, atk01
./proxmox/create-windows-shells.sh   # dc01 and ws01, with a CD of lab scripts

### Step 3: Windows domain (three scripts from the CD)

E:\01-dc01-promote.ps1 -SafeModePassword "..."   # dc01: lab.cddar.test forest
E:\02-dc01-populate.ps1                          # dc01: synthetic users, audit policy
E:\01-ws01-join.ps1                              # ws01: join the domain

### Step 4: Deploy everything else

./deploy/deploy.sh all          # 30 to 60 minutes
./deploy/deploy.sh passwords    # every web console login
./deploy/deploy.sh status       # every service should say "up"

That one command generates every password and key, then sets up the router (responder key,
        WireGuard configs), the core (OpenSearch, Kafka, Vector, Grafana, NetBox with the asset list,
        scorer, discovery, approval log), the SOC (Wazuh, TheHive, Cortex with the block responder,
        Velociraptor, and links them all), the sensor (Zeek, Suricata with ET Open rules), the Linux
        agents and Caldera. Then E:\install-agents.ps1 on both Windows machines adds
        Sysmon, the Wazuh agent and the Velociraptor client.

### Step 5: The field kit

./deploy/deploy.sh kit 192.168.1.50   # the kit's home-network address
./deploy/deploy.sh internet off       # close the lab before any attack test

The kit becomes the gateway and DHCP server for its field network, opens WireGuard to the lab,
        installs k3s and runs Zeek, Suricata and Vector as one pod, using the same configuration files
        as the lab sensor.

### Step 6: Test it

./tests/emulation/run-all.sh   # 10 attack steps, then scores coverage, MTTD, MTTR
./deploy/deploy.sh ddil        # kit outage test: healthy, degraded, cut, restored

| ATT&CK | Step | From | Expected detector |
| --- | --- | --- | --- |
| T1046 | Service scan of the command network | atk01 | Suricata (ET Open + lab rule) |
| T1110.001 | SSH password guessing against srv01 | atk01 | Zeek SSH brute-force policy, Wazuh |
| T1021.002 | SMB admin share access on dc01 | atk01, ws01 | Suricata lab rules, Wazuh |
| T1059.001 | Encoded PowerShell | ws01 | Sysmon + Wazuh |
| T1087.002 | Domain account discovery | ws01 | Sysmon + Wazuh |
| T1053.005 | Scheduled task created and deleted | ws01 | Sysmon + Wazuh |
| T1547.001 | Run key added and removed | ws01 | Sysmon + Wazuh |
| T1003.001 | LSASS minidump, deleted at once | ws01 | Sysmon LSASS access + Wazuh |
| T1048.003 | Synthetic document out over DNS to a lab-only zone | ws01 | Zeek long-query notice, Suricata lab rule |
| T1200 | Unknown device plugged into the field switch | field network | Discovery vs NetBox |

Each step is logged to the approval log before it starts, so the scoring script can measure time
        to detect exactly, and each step cleans up after itself. A missed technique is a result, not a
        failure: tune the detection, re-run, and publish both runs.

## What Is in the Code

All of it is open source under the MIT licence:
        [github.com/TYFSADIK/cd-dar-testbed](https://github.com/TYFSADIK/cd-dar-testbed).

| Folder | What it holds |
| --- | --- |
| proxmox/ | Lab bridge, VM creation, cloud-init for every Linux VM, including the router's default-deny firewall, WireGuard and the restricted lab-block command |
| deploy/ | Secret generator and one deploy script with all, per-machine, kit, internet on|off, status, passwords and ddil targets |
| stacks/ | Docker Compose stacks for core, SOC and sensor; the Vector OCSF mapping with built-in tests; the OpenSearch index template and retention; the generated Grafana dashboard; Zeek policy and Suricata lab rules |
| services/ | Decision scorer, discovery (Nmap plus passive Zeek sightings against NetBox) and the hash-chained approval log, in Python |
| responders/ | Cortex responder that blocks a lab IP on the router, refusing anything outside the lab ranges |
| endpoints/ | Windows domain scripts and the Sysmon, Wazuh and Velociraptor installers for Windows and Linux |
| kit/ | Field kit setup, the k3s sensor pod, and the outage test |
| tests/, tools/ | Emulation runners, Caldera launcher, NASA-TLX workload scoring, run scoring, NetBox seeding, TheHive and Cortex setup, chain-of-custody hashing |

Checked before any hardware is touched:

- 29 automated tests pass: 23 Python tests (scoring, correlation, alert content, discovery reconciliation, hash-chain tamper and deletion detection, run scoring) and 6 Vector pipeline tests (Zeek, Suricata, Wazuh and discovery events mapped to OCSF).

- All three Docker Compose stacks validate, every shell script passes ShellCheck, every cloud-init template renders with no missing values.

- A security review of my own code caught one real problem before it shipped: the endpoint download server would have exposed Velociraptor's private server keys. It now serves a separate folder holding only client files.

What tests on a laptop cannot prove is how it behaves on real hardware. Expect first-run fixes;
        they will be recorded here.

## Spec-Gap and Status Table

"Code ready" means written and tested offline, not yet running in the lab. Nothing is
        "Measured" until a lab run produces the number. This table will be updated in place.

| Capability | Design intent | Status |
| --- | --- | --- |
| Network discovery | Active and passive discovery reconciled with NetBox; unknown devices flagged | Code ready |
| Integrated sensors | Zeek, Suricata, Wazuh and Daru feeding one pipeline | Code ready |
| Cyber Data Repository | OpenSearch with OCSF-normalised events and stated retention | Code ready |
| Cyber COP | Single picture of assets, alerts, ATT&CK stage and mission impact | Code ready |
| Decision scoring | Context-ranked alerts with a readable reason | Code ready |
| Human-approved response | TheHive playbooks; no action without approval; every decision logged | Code ready |
| Remote forensics | Velociraptor collection with hashed chain of custody | Code ready |
| ATT&CK coverage | Caldera and Atomic Red Team scenarios scored per technique | Not tested |
| Human factors | Workload and triage time measured against a plain queue | Not tested (form and script ready) |
| Deployable kit | k3s kit with store-and-forward through link loss | Code ready |

## Metrics to Publish

- ATT&CK technique coverage: share of emulated techniques detected.

- Mean time to detect and mean time to respond, for the ranked queue and the plain queue.

- False-positive rate per day of normal lab activity.

- Asset discovery completeness against NetBox, and time to flag a planted unknown device.

- Remote forensic collection time per host, and hash verification of every artefact.

- Operating picture freshness: time from event to screen.

- Analyst workload: alerts per hour, time per triage, and NASA-TLX score.

- Deployable kit: events lost during link outages, target zero.

## Hardware to Buy First

Most of the build runs on the homelab I already have. The shopping list is short:

| Item | Why | Notes |
| --- | --- | --- |
| Fanless mini PC, 16 GB RAM, 256 GB SSD, two Ethernet ports | The deployable kit | Any N100 or N305 class box with dual 2.5 GbE |
| USB 3 gigabit Ethernet adapter | Third port on the kit, for the mirror port | RTL8153 or AX88179 chipsets work well on Linux |
| 5 or 8 port managed switch with port mirroring | The field network | TP-Link TL-SG105E / TL-SG108E or Netgear GS305E / GS308E |
| One or two small devices | Something on the field network to watch | A Raspberry Pi or an old laptop |
| RAM for the Proxmox node, if short | The lab needs about 59 GB, 47 GB in lite mode | See Figure 7 |

## Safety and Legal Notes

## Frequently Asked Questions

**Q: What is CD-DAR?**

A: Cyber Defence - Decision Analysis and Response (CD-DAR) is a National Defence project listed in the Defence Capabilities Blueprint. It will acquire defensive cyber capabilities for DND/CAF networks: network discovery, integrated cyber defence tools, an authoritative Cyber Data Repository, a Cyber Common Operating Picture, attention to human factors, and remote cyber forensics. The listed funding range is $250 million to $499 million, with implementation starting in 2026/2027 and final delivery in 2030/2031.

**Q: Is this build part of the CD-DAR project?**

A: No. This is an independent, personal research build. It uses only the public project description to shape a bench-scale testbed on homelab hardware. It is not affiliated with, funded by, or submitted to DND, the CAF or ADM(DS), and it touches no government network or data.

**Q: Which open-source tools does the testbed use?**

A: Zeek and Suricata for network sensing, Nmap and NetBox for discovery and the asset source of truth, Wazuh and Daru for host telemetry and SIEM, OpenSearch with an OCSF-normalised schema as the Cyber Data Repository, Grafana and OpenSearch Dashboards for the cyber COP, Velociraptor for remote forensics, and TheHive with Cortex for cases and human-approved response.

**Q: How will detection and response be tested?**

A: With adversary emulation in an isolated lab segment: MITRE Caldera and Atomic Red Team run known ATT&CK techniques against my own machines. The testbed is scored on ATT&CK coverage, time to detect, time to respond, false-positive rate, asset discovery completeness and remote forensic collection time.

**Q: Is anything built or measured yet?**

A: The code is. The whole testbed is written as scripts, configuration and three Python services, with 29 automated tests that pass. The physical build and the first lab run come next, so no capability is measured yet; results will be added to the status table as each one is.

## Related Builds

- CD-DAR Testbed source code, every script, configuration, service and test behind this page.

- Daru SIEM, my self-hosted SIEM, which feeds host and network telemetry into this testbed.

- Decision Black Box, the tamper-evident log that records every analyst approval and response action.

- Multi-Domain Common Operating Picture, the physical-sensor fusion layer whose operating-picture design this cyber COP mirrors.

- DDIL-Proof DevOps, the store-and-forward patterns behind the deployable sensor kit.

- Zero-Trust Air-Gapped Supply Chain, signed and verified software for every tool installed in the testbed.

- Canadian Defence Hardware Program, the hub page for all of my defence builds.

## What Happens Next

- Next: buy the kit parts, wire the switch, install Windows, then deploy.sh all.

- First results: the first emulation run's coverage, time to detect and time to respond, published as a table here, missed techniques included.

- Winter fit: like the other software builds, this one needs no field weather window, so it runs through the southern Ontario winter.

- Project timeline: CD-DAR implementation is listed to start in 2026/2027, so this testbed is pre-competitive skill building aligned with where Canada's defensive cyber work is heading.

## Cite This Page

**Q: Citation formats**

A: Plain text
