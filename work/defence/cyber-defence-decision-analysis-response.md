# Cyber Defence Decision Analysis and Response (CD-DAR) Testbed

Written by [Taki Sadik](../../about) · Last updated 2026-11-21 · Status: Planned, build guide published · 10 min read

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
        information, synthetic data and my own machines. Status everywhere on this page is
        Planned: the guide is published so the design can be checked before it is built.

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

Figure 1: sensors, host agents, discovery and the deployable kit all feed one pipeline into the Cyber Data Repository; the operating picture and decision scoring read from it; an analyst approves every response, and every approval and action is written to the tamper-evident log.

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

## How to Build It

Weeks are indicative; the order matters more than the calendar. The lab comes before the
        tools, and the attack plan comes before any claim of detection.

### Phase 1: Lab network and threat model (weeks 1-2)

- Build an isolated lab segment on Proxmox with VLANs standing in for a notional command network, a notional deployable network and an attacker network. All names and data are synthetic.

- Pick the ATT&CK techniques the testbed must detect (initial access, credential access, lateral movement, exfiltration) and write one test case per technique.

- Record the baseline: what is detected today with no new tooling.

### Phase 2: Discovery and asset truth (weeks 2-3)

- Load every lab device into NetBox with an owner, role and mission criticality.

- Schedule Nmap scans and enable Zeek's passive software and host logs; reconcile both against NetBox.

- Plant unknown devices and measure how long it takes for each to be flagged.

### Phase 3: Sensors and the data repository (weeks 3-5)

- Mirror lab traffic to a SPAN port and run Zeek and Suricata on it.

- Enrol every host in Wazuh and Daru.

- Ship all events with Vector through Kafka into OpenSearch, mapped to OCSF, with retention and index templates written as code.

### Phase 4: Operating picture and decision scoring (weeks 5-7)

- Build the Grafana and OpenSearch Dashboards views: asset map, live alerts, ATT&CK heat map and mission-service status.

- Write the scoring service: criticality from NetBox, confidence from the detection, stage from ATT&CK, and a short plain-language reason for every score.

### Phase 5: Response and remote forensics (weeks 7-9)

- Stand up TheHive and Cortex, with playbooks for isolate host, block indicator and collect evidence.

- Deploy Velociraptor to every host and build collection packs for memory, browser, persistence and log artefacts, hashing every artefact.

- Require human approval for every action, and log each approval to the decision black box.

### Phase 6: Adversary emulation and scoring (weeks 9-11)

- Run MITRE Caldera and Atomic Red Team against the lab only, technique by technique.

- Score coverage, time to detect, time to respond and false positives for both the ranked queue and a plain severity-sorted queue.

- Run the analyst workload study on the same scenarios.

### Phase 7: Deployable kit (weeks 11-12)

- Package a mini PC as a deployable sensor kit on k3s with local storage.

- Cut and degrade its link with tc netem and prove it keeps collecting and syncs without loss when the link returns, using the patterns from DDIL-Proof DevOps.

## Spec-Gap and Status Table

Everything is Planned until it is measured. This table is the honest scoreboard and will be
        updated in place as phases complete.

| Capability | Design intent | Status |
| --- | --- | --- |
| Network discovery | Active and passive discovery reconciled with NetBox; unknown devices flagged | Planned |
| Integrated sensors | Zeek, Suricata, Wazuh and Daru feeding one pipeline | Planned |
| Cyber Data Repository | OpenSearch with OCSF-normalised events and stated retention | Planned |
| Cyber COP | Single picture of assets, alerts, ATT&CK stage and mission impact | Planned |
| Decision scoring | Context-ranked alerts with a readable reason | Planned |
| Human-approved response | TheHive playbooks; no action without approval; every decision logged | Planned |
| Remote forensics | Velociraptor collection with hashed chain of custody | Planned |
| ATT&CK coverage | Caldera and Atomic Red Team scenarios scored per technique | Not tested |
| Human factors | Workload and triage time measured against a plain queue | Not tested |
| Deployable kit | k3s kit with store-and-forward through link loss | Planned |

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

Most of this build runs on the homelab I already have. The shopping list is short.

- Existing hosts: the Proxmox nodes and Kubernetes cluster carry the pipeline, repository, dashboards, TheHive and Velociraptor.

- A managed switch with port mirroring: gives Zeek and Suricata a SPAN copy of lab traffic.

- A small fanless mini PC: the deployable sensor kit, running k3s with local storage.

- Extra RAM or disk, if needed: OpenSearch is the heaviest component, so storage is sized after the first week of real event volume.

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

A: Not yet. This page is a published build guide. Every capability in the status table is marked Planned or Not tested, and results will be added in place as each phase is measured.

## Related Builds

- Daru SIEM, my self-hosted SIEM, which feeds host and network telemetry into this testbed.

- Decision Black Box, the tamper-evident log that records every analyst approval and response action.

- Multi-Domain Common Operating Picture, the physical-sensor fusion layer whose operating-picture design this cyber COP mirrors.

- DDIL-Proof DevOps, the store-and-forward patterns behind the deployable sensor kit.

- Zero-Trust Air-Gapped Supply Chain, signed and verified software for every tool installed in the testbed.

- Canadian Defence Hardware Program, the hub page for all of my defence builds.

## What Happens Next

- Phase 1 and 2 next: the isolated lab segments, the ATT&CK test cases and NetBox as the asset source of truth.

- Winter fit: like the other software builds, this one needs no field weather window, so it runs through the southern Ontario winter.

- Publish as it goes: one repo with the README, configuration as code, emulation results and the status table above updated in place as capabilities move from Planned to measured.

- Project timeline: CD-DAR implementation is listed to start in 2026/2027, so this testbed is pre-competitive skill building aligned with where Canada's defensive cyber work is heading.

## Cite This Page

**Q: Citation formats**

A: Plain text
