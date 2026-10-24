# Taki Sadik: IT Infrastructure, Cybersecurity and Defence Technology Portfolio

## Latest Labs

116 hands-on labs across nine tracks: Linux Fundamentals (24), Linux Server Administration (12), Networking (16), Security (18), Python Automation (14), Databases (8), Cloud & Azure (9), Containers & Kubernetes (9), and Version Control & DevOps (6).

Wazuh + TheHive + MISP SOAR pipeline with MITRE ATT&CK mapping and automated enrichment. [Read the Automated SOC Pipeline lab](blog/labs/security/automated-soc-pipeline.html)

Hunt Kerberoasting, Pass-the-Hash, and Golden Tickets with BloodHound, Sysmon, and Splunk. [Read the Active Directory Threat Hunting lab](blog/labs/security/ad-threat-hunting.html)

Automate endpoint isolation with Python, yara-python, nftables, and the Proxmox API. [Read the Python IR Automation lab](blog/labs/security/python-ir-automation.html)

## At a Glance

## Currently Pursuing

## Who is Taki Sadik?

Cybersecurity and infrastructure professional in Toronto. I cut SOC alert MTTR by 25%,
              run a [7-node Kubernetes homelab](work/infrastructure/kubernetes-infrastructure.html),
              and published [116 hands-on IT labs](blog/labs/index.html).

I build and defend infrastructure, and, increasingly, the sensors and robots that run on top
              of it. From triaging security events at a SOC to running self-hosted servers, passive radar
              nodes, and GPS-denied rovers, I care deeply about owning my stack.

Right now I work as a Data Center Engineer at
              Microsoft, applying cyber threat intelligence to physical infrastructure. I also serve as an
              Incident Manager at Felixous Technology Inc.. Alongside all of that I am building
              [Chakor](work/infrastructure/chakor.html), an open-source self-hosted AI workspace, and the
              [Canadian Defence Hardware Program](work/defence/defence-hardware-program.html) -
              eleven sensor and robotics builds across sky, water, and ground, each mapped to a real requirement
              from Canada's Defence Drone Initiative and the Army's MINERVA challenges.

I got into IT through surveillance operations and discovered I cared more about the network
              underneath the cameras than the footage they captured. That curiosity led me to networking, then
              Linux administration, then cloud, then security, and now to the hardware itself: SDR receivers,
              microphone arrays, hydrophones, and the rovers and drones that carry them. Today my home runs a
              [7-node Kubernetes cluster (Ubuntu VMs on Proxmox hosts)](work/infrastructure/kubernetes-infrastructure.html),
              a [zero-trust Proxmox cloud](work/infrastructure/proxmox-zero-trust.html), nine
              self-hosted services, and a workbench of field sensors feeding a
              [multi-domain common operating picture](work/defence/multi-domain-common-operating-picture.html).

I study at the University of Toronto (B.Eng, Information Technology) and
              Seneca College of Applied Arts and Technology (postgraduate, Cyber/Electronic Operations), and I document
              everything I learn as [hands-on labs: 116 of them so far](blog/labs/index.html),
              across nine categories: Linux Fundamentals, Linux Server Administration, Networking,
              Security, Python Automation, Databases, Cloud & Azure, Containers & Kubernetes,
              and Version Control & DevOps. Each lab has real commands, diagrams, expected outputs,
              and validation checks. I believe in learning by doing.

MD. Taki Yasir Faraji Sadik  ·  North York, ON, Canada  · 
              [taki@tyfsadik.org](mailto:taki@tyfsadik.org)

## Career Highlights

- Cut SOC alert MTTR by 25%, mapped the end-to-end triage workflow across Splunk and AlienVault, found 3 bottlenecks, and shipped automated enrichment pipelines.

- Automated 30+ daily security alerts, Python scripts and Splunk SPL correlation that eliminate false positives with minimal human intervention.

- Building an 11-project defence hardware program, a receive-only passive radar early-warning node (KrakenSDR + pyAPRiL, scored against ADS-B truth), a ROS 2 GPS-denied rover with EKF drift measurements, a thermal SAR drone, and a cold-soak battery rig producing a public dataset, each mapped to a stated Defence Drone Initiative or MINERVA requirement.

- Built a 7-node Kubernetes cluster on Proxmox hosts, VLAN segmentation, Calico CNI, MetalLB, Longhorn storage, and Prometheus + Grafana observability, all on consumer hardware.

- Kept healthcare systems at 99%+ uptime, architected a VLAN-segmented network and documented data flows for compliance at CardiOCare.

- Eliminated public IP exposure, 3-node Proxmox HA cluster behind Cloudflare Tunnel with Tailscale fallback and automated 30-day ZFS snapshot retention.

- 25+ certifications and counting, Cisco, Microsoft, AWS, Google, IBM, and OPSWAT, while working and studying full-time.

## Current Focus: Defence Technology, Hands-On

My next step is infrastructure and DevOps engineering for Canada's defence sector, and my bench already looks the part.

DND and the Canadian Armed Forces are in the middle of a multi-year
              [digital transformation](https://www.cgai.ca/digital_transformation_and_pan_domain_the_cafs_quiet_revolution_in_military_affairs),
              and that is exactly where I want my career to go: building the secure pipelines, clusters, and
              networks that modern defence systems run on. Reliability, repeatability, and security are the
              whole job, and those are the muscles I train every day.

I also build the hardware side myself. My
              [Canadian Defence Hardware Program](work/defence/defence-hardware-program.html)
              is eleven active builds, passive radar, a hydrophone vessel monitor, a seismic LoRa mesh,
              GPS-denied rovers, a thermal SAR drone, and secure fleet updates, each one mapped to a real
              requirement from the Defence Drone Initiative or the Army's MINERVA challenges, each with full
              parts lists, prices, and step-by-step guides.

## DevOps in Practice

DevOps is not theory for me. These are hands-on labs I built and documented, each with real commands, configs, expected outputs, and validation checks, organized into nine categories:

- Linux Fundamentals (24 labs): command line, files and permissions, text processing, shell scripting, virtualization, scheduling.

- Linux Server Administration (12 labs): installs, systemd services, disks and LVM, users, backups, logging.

- Version Control & DevOps (6 labs): Git workflows, branching, pull requests, GitHub Actions, and a full CI/CD pipeline that tests, scans, and deploys a container on every push.

- Networking (16 labs): subnetting, VLANs, DHCP, DNS, packet analysis, and software-defined networking.

- Security (18 labs): hardening, forensics, incident response, and SOC automation.

- Python Automation (14 labs): system admin scripts and CLI tools that solve real operational problems.

- Databases (8 labs): SQL, design and normalization, admin, backups, and cloud deployments.

- Cloud & Azure (9 labs): virtual networks, ARM templates, monitoring, and cloud security posture management.

- Containers & Kubernetes (9 labs): Docker, Compose, Kubernetes pods and services, and AKS deployment with autoscaling.

[All 116 labs →](blog/labs/index.html)

## What I'm Doing, What I Did, What's Next

### Doing right now: the Canadian Defence Hardware Program

My bench is full. I read Canada's public defence calls, the Defence Drone Initiative
              (launched July 2026) and the Army's MINERVA challenges, as free requirements documents,
              and I'm building against them at hobby scale, every step documented:

- Sky: Passive Aerial Early-Warning Node, receive-only passive radar on a KrakenSDR, scored against an ADS-B ground-truth receiver.

- Water: Passive Acoustic Vessel Monitor, solar hydrophone node classifying vessels, with AIS ground truth.

- Ground: Seismic & Acoustic Perimeter Mesh, solar ESP32 LoRa nodes telling vehicles from footsteps at the edge.

- GPS-Denied Navigation Rover + Convoy Robots on a Degraded Mesh, ROS 2 EKF navigation with the GNSS cut, and convoys that survive bad links.

- Thermal Search-and-Rescue Drone + Passive Acoustic Drone Detector, the MINERVA Arctic ISR gap and the NRC/DRDC passive counter-drone idea, at hobby scale.

- Cold-Soak Battery Rig + Secure Robot-Fleet Updates, cold-weather battery data and supply-chain integrity, the two pain points the Army names outright.

Full parts lists, prices, and build guides: [Canadian Defence Hardware Program hub](work/defence/defence-hardware-program.html).

### Doing: six software defence builds, written up as they progress

- Arctic Domain Awareness Digital Twin, fusing ADS-B, AIS, and Sentinel-1 radar over the North; dark-vessel and route-deviation alerts.

- DDIL-Proof DevOps, CI/CD and telemetry that survive denied, degraded, intermittent links; store-and-forward to k3s edge nodes.

- Counter-Drone Sensor Fusion Simulator, synthetic radar/RF/acoustic/camera tracks, Kalman fusion, human-in-the-loop triage. Defensive simulation only.

- Decision Black Box, tamper-evident, hash-chained audit log with replay and OPA policy checks.

- Zero-Trust Air-Gapped Supply Chain, SBOM, sigstore signing, and reproducible builds across a simulated one-way transfer.

- Operation LENTUS-Style Drone Mapping, simulated disaster-response flights with edge computer vision and a live situational-awareness map.

### What I did

- Cut SOC alert MTTR by 25% and automated 30+ daily security alerts with Python and Splunk SPL correlation, mapped the triage workflow, found the bottlenecks, shipped the enrichment pipelines.

- Built a 7-node Kubernetes cluster on Proxmox hosts with VLAN segmentation, Calico, MetalLB, Longhorn, and Prometheus + Grafana, all on consumer hardware.

- Built a zero-trust Proxmox cloud behind Cloudflare Tunnel with Tailscale fallback and automated 30-day ZFS snapshot retention, no public IP exposure.

- Wrote and published 116 hands-on labs across nine tracks, each with real commands, diagrams, expected outputs, and validation checks.

- Kept healthcare systems at 99%+ uptime at CardiOCare with a VLAN-segmented network and documented data flows for compliance.

- Earned 25+ certifications across Cisco, Microsoft, AWS, Google, IBM, and OPSWAT while working and studying full-time.

### Next

- Publish the cold-soak dataset, runtime, voltage sag, and failure mode vs temperature.

- Stand up 2-3 passive radar nodes and fuse their outputs.

- Roll signed OTA updates across the rover fleet, validated in the cold chamber.

- Tie every node into the Multi-Domain Common Operating Picture and chaos-test it by cutting links and killing nodes.

## Featured Projects

[View all projects →](work.html)

## Contact

Open to new opportunities in cybersecurity, SOC operations, networking, and IT infrastructure.
