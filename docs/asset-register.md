# Infrastructure Asset Register

The physical and logical inventory behind the TYFSADIK homelab: what is confirmed running, what is stated but not yet evidenced, and what is planned, with every claim labeled by verification status.

## How to Read This Register

In one sentence: this page is the single source of truth for what hardware
        and logical infrastructure exists behind this portfolio, what state each asset is in, and
        what evidence backs each claim.

Every asset carries one of four verification statuses. They mean specific things and are
        never blurred:

- CONFIRMED: direct evidence exists on this site or in the lab itself: a photograph, a configuration that is applied and running, or output captured from the live system. The server room page is the photographic record for the confirmed rows.

- PARTIALLY VERIFIED: the asset has been stated by the owner (the person who runs this site) but independent corroborating evidence has not yet been published: no photo, no captured inventory output, no serial-level record. Treat the quantity and model as accurate to the owner's account, pending the evidence items in the verification checklist below.

- PLANNED: an intended future capability. Designed and scoped, not purchased or deployed. Nothing in a PLANNED row should be read as operational.

- UNKNOWN: insufficient evidence to record a value at all. The field is left marked rather than filled with a guess.

Two rules follow from the site's documentation philosophy (evidence first, explanation
        second, presentation third). First, this register never converts an owner statement into a
        confirmed fact; status changes only when evidence lands. Second, physical assets, virtual
        machines, containers, and logical services are kept in separate inventories: a
        Kubernetes node is a VM on a Proxmox host, not a physical server, and counting it as one
        would double-count the fleet.

Register last reconciled: 2026-10-21. Evidence source for all
        non-CONFIRMED rows: owner statement, 2026-10-21 (updated the same day with
        configuration-level testimony for the GPU stack nodes and the estate's build sequence),
        unless a row says otherwise.

## Physical Asset Register

Confirmed rows describe the running lab documented on the
        [Homelab Server Room](../work/infrastructure/homelab-server-room.html) page.
        Expansion rows describe the stated next phase of the build. Specifications are recorded
        only where known; empty fields are marked UNKNOWN rather than estimated.

### Confirmed, in daily use

| Asset ID | Asset | Qty | Role (actual workload) | Software | Network | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PHY-HOST-D1..D3 | Desktop PCs, repurposed consumer towers | 3 | Proxmox VE hosts: control-plane VM, worker VMs, Longhorn storage nodes | Proxmox VE 8.x | Wired Cat6, VLAN 20 access ports | Photographed; documented across the server room and Kubernetes pages | CONFIRMED |
| PHY-HOST-L1..L4 | Laptops, repurposed | 4 | Proxmox VE hosts for lightweight worker VMs | Proxmox VE 8.x | 5 GHz wireless bridge into VLAN 20 | Photographed; flapping issue and fix documented | CONFIRMED |
| PHY-NET-SW1 | Managed switch | 1 | 802.1Q segmentation: VLAN 10 (management), 20 (cluster), 30 (services); trunk to router and radio | Vendor firmware | Core of the lab LAN | Configuration described on the Kubernetes page | CONFIRMED |
| PHY-NET-RTR | Router | 1 | NAT, DHCP reservations, inter-VLAN routing, firewall between segments | Vendor firmware | WAN to ISP, trunk to switch | Documented on the Kubernetes page | CONFIRMED |
| PHY-NET-RADIO | 5 GHz wireless radio | 1 | Bridge-mode backhaul carrying cluster traffic to the laptop hosts | Vendor firmware, fixed channel | Switch trunk port | Documented, including the fixed-channel tuning | CONFIRMED |
| PHY-OPS-1 | Ops desk monitoring station | 1 | Grafana dashboards, logs, hands-on maintenance | Browser to Grafana on VLAN 10 | VLAN 10 management | Photographed | CONFIRMED |
| PHY-PWR-1 | UPS units | UNKNOWN | Power protection not yet instrumented or documented | NUT planned | Household circuits, mapped by breaker | None yet | UNKNOWN |

Exact makes and models of the confirmed desktops and laptops, their CPU and RAM
        configurations, and per-node power draw have not been published yet; capturing
        lshw and dmidecode output per host is item 1 in the verification
        checklist below. No wattage figures are claimed anywhere on this site because none have
        been measured.

### Owner-stated expansion inventory (pending independent evidence)

The rows below were stated by the owner on 2026-10-21 as the next phase of the build.
        Until photographs, inventory captures, or configuration exports are published, they carry
        PARTIALLY VERIFIED or PLANNED status and must not be read as deployed infrastructure.

| Asset ID | Asset | Stated qty | Intended workload | Key specifications | Status |
| --- | --- | --- | --- | --- | --- |
| EXP-RACK-1..3 | Server racks / stacks for hosting infrastructure | 3 | House the 24-unit OptiPlex hosting fleet, the JBOD enclosures, and the network core. A fourth, separate large stack holds the GPU rental nodes, and a small standalone position holds the Raspberry Pi utility server | Rack units, rail kits, PDU models: UNKNOWN | PARTIALLY VERIFIED (owner-stated) |
| EXP-SFF-1..24 | Dell OptiPlex 5060 Small Form Factor desktops, hosting fleet | 24 | Owner-stated workloads: the self-hosted media library (movies, series, anime), Chakor AI serving ai.tyfsadik.org, and the general self-hosted service estate, spread across the three hosting stacks | Per Dell's specification: 200 W PSU (EPA Bronze or Platinum), 1 half-height PCIe 3.0 x16 slot + 1 half-height x4 slot, 4 DDR4 UDIMM slots (64 GB max), 8th-gen Intel Core, chassis 292 x 290 x 92.6 mm. Per-unit CPU/RAM/disk split across this fleet: UNKNOWN | PARTIALLY VERIFIED (owner-stated) |
| EXP-JBOD-1..4 | JBOD storage enclosures | 4 | Bulk storage behind the media library, backups, and dataset retention | Enclosure model, bay count, drive population, interface (SAS/SATA): UNKNOWN | PARTIALLY VERIFIED (owner-stated) |
| EXP-STORE-AGG | Aggregate storage capacity across the JBODs | ~2 PB intended | Raw capacity target before redundancy; see the storage capacity model below before quoting this number | Raw vs usable split: not yet established (depends on unknown drive population) | PARTIALLY VERIFIED as an intended target; not a measured figure |
| EXP-NET-CISCO | Cisco switching infrastructure | UNKNOWN | Managed switching for the expanded rack infrastructure | Exact models, port counts, link speeds, VLAN plan: UNKNOWN | UNKNOWN |
| EXP-PI-NET | Raspberry Pi utility server | UNKNOWN (at least 1) | Owner-stated roles: Pi-hole DNS filtering, security monitoring, and the domain watchdog that detects domain or DNS failures and drives the recovery runbook | Board model and count: UNKNOWN | PARTIALLY VERIFIED (owner-stated role; hardware unidentified) |
| EXP-GPU-NODE-1..20 | Dell OptiPlex 5060 SFF, GPU compute stack (separate large stack) | 20 | Dedicated GPU rental stack, isolated from the hosting fleet per owner statement | Owner-stated per-unit configuration: 8th-gen Intel Core i7-8700 (6 cores / 12 threads, up to 4.60 GHz), 16 GB DDR4-2666 (2 x 8 GB), 2x DisplayPort, Gigabit Ethernet only (no Wi-Fi). Chassis spec per Dell: 200 W PSU, half-height PCIe slots | PARTIALLY VERIFIED (owner-stated as built; power and mechanical integration undocumented, see feasibility analysis) |
| EXP-GPU-1..20 | RTX 4090-class GPUs (owner specification says "4090 Ti") | 20 | GPU compute for rental workloads | Reference card: 450 W TGP, 304 mm full-height 3-slot, 12VHPWR, per NVIDIA. Note: NVIDIA has not released a "4090 Ti" SKU as of this writing; the exact model string is pending nvidia-smi evidence | PARTIALLY VERIFIED (owner-stated; model string and integration pending evidence) |

Power protection, cooling capacity, and backup hardware for the expansion phase are
        recorded as UNKNOWN until measured. The 9 kW electrical implication of the GPU cluster is
        worked through in the feasibility section rather than assumed away.

## Logical Infrastructure Inventory

Logical assets ride on the physical rows above. VM counts are documented on the
        [Kubernetes Infrastructure](../work/infrastructure/kubernetes-infrastructure.html)
        page; they are not physical machines and are not double-counted here.

| Logical asset | Runs on | Depends on | Documented at | Status |
| --- | --- | --- | --- | --- |
| Proxmox VE virtualization layer | PHY-HOST-D1..D3, PHY-HOST-L1..L4 | Physical hosts, wired/wireless network | Proxmox Homelab | CONFIRMED |
| 7-node Kubernetes cluster (kubeadm: control plane + workers, Calico, MetalLB, Longhorn, ingress-nginx, cert-manager) | VMs across the Proxmox hosts | Proxmox layer, VLAN 20, storage network | Kubernetes Infrastructure | CONFIRMED |
| Self-hosted services (nine applications including DNS and the AI workspace) | Kubernetes cluster and VMs | Cluster, reverse proxy, certificates | Data Sovereignty Stack | CONFIRMED |
| Self-hosted DNS (filtering/resolution) | Service hosts | Router DHCP configuration, upstream resolvers | Self-Hosted DNS | CONFIRMED |
| Chakor AI workspace / TYF-AI platform | Cluster and service hosts | Model providers (local and configured cloud), storage | Chakor, TYF-AI | CONFIRMED as deployed software; performance claims carry their own methodology notes on those pages |
| Monitoring: Prometheus + Grafana | Cluster, VLAN 10 access | Cluster, persistent storage | Kubernetes Infrastructure | CONFIRMED |
| Zero-trust remote access layer | Edge tunnels to the Proxmox and service plane | Cloudflare account, identity provider rules | Proxmox Zero-Trust Private Cloud | CONFIRMED |
| Backup and recovery jobs (snapshots + off-host copies) | Proxmox and storage layer | Storage capacity, scheduling | Data Sovereignty Stack | CONFIRMED for the current lab; expansion-phase backup design is PLANNED |
| Public domains (tyfsadik.org and project sites) | GitHub Pages (this site) + tunneled self-hosted services | Registrar, DNS provider, tunnel layer | Proxmox Zero-Trust | CONFIRMED |

## Master Architecture Diagram

One picture of the whole estate: confirmed layers are drawn with solid lines and filled
        nodes, and owner-stated assets (the three hosting stacks, the 24-unit OptiPlex fleet, the
        JBOD storage, the Cisco switching, the Raspberry Pi utility server, the media library, and
        the separate 20-node GPU rental stack) with dashed lines until independent evidence is
        published. The diagram distinguishes the physical layer (racks, hosts, network) from
        the virtualization layer (Proxmox), the orchestration layer (Kubernetes), and the service
        plane (DNS, AI, monitoring, backups, public domains).

OWNER-STATED: pending independent evidence

CONFIRMED: running lab (photographed, in daily use)

7-VM Kubernetes (kubeadm)

hosts

hosts Chakor AI (ai.tyfsadik.org)

bulk storage + backups

media storage

DNS filtering + telemetry + domain watchdog

power + mechanical integration undocumented

expansion Proxmox / service nodes

ISP Uplink

RouterNAT / DHCP / inter-VLAN

Managed SwitchVLANs 10 / 20 / 30

5 GHz Bridge

3 Desktop Proxmox Hosts

4 Laptop Proxmox Hosts

Control plane

Workers

Longhorn storage

Prometheus + Grafana

Self-hosted servicesDNS / AI workspace / apps

Zero-trust tunnel layer

tyfsadik.org + project domains

3 hosting stacks + separate GPU stack

24x OptiPlex 5060 SFF hosting fleet

4x JBOD enclosures~2 PB intended raw aggregate

Cisco switchingmodels UNKNOWN

Raspberry Pi utility serverPi-hole + security + domain watchdog

Media library hostingmovies / series / anime

GPU rental stack20x OptiPlex 5060 SFFi7-8700 / 16 GB + RTX 4090-class each

Reading guide: solid arrows are paths that carry traffic today. Dashed arrows are
        owner-stated relationships awaiting independent evidence. The GPU rental stack links into
        the estate through the switching layer, but its power and mechanical integration is exactly
        the open question the feasibility analysis below addresses.

## Storage Capacity Model: Raw, Usable, Planned

The stated figure for the expansion phase is approximately 2 PB of intended
        aggregate capacity across 4 JBOD enclosures. Until the enclosure models, bay
        counts, and drive populations are evidenced, that number is an intended raw
        target, nothing more. Three distinctions matter before the number is quoted
        anywhere:

- Raw capacity is the sum of the label capacities of every physical drive. It is the largest number and the least useful one for planning.

- Usable capacity is what remains after redundancy (parity or mirroring), filesystem and metadata overhead, and sensible free-space headroom. Parity schemes commonly cost one to four drives per vdev; filesystem overhead and reservation typically cost a further few percent.

- Backup copies consume capacity again. A 3-2-1 posture (three copies, two media, one off-site) means protected data needs roughly double the usable capacity of the primary copy somewhere in the estate.

Illustrative arithmetic only (not a measurement, and not this lab's configuration): 2.0 PB
        raw, minus 20 percent for dual-parity redundancy, minus roughly 3 percent filesystem
        overhead, yields on the order of 1.5 PB usable for the primary copy, before any backup
        copy is carved out. The real number will be computed from the actual drive population once
        the JBOD rows above move from PARTIALLY VERIFIED to CONFIRMED, and this section will be
        updated with the measured split.

One further rule this site applies everywhere: replication is not backup.
        A replicated or mirrored copy faithfully reproduces accidental deletion and corruption.
        Independent, point-in-time recovery points (snapshots plus off-host copies, as documented
        on the [Data Sovereignty
        Stack](../work/infrastructure/data-sovereignty-stack.html) page) are what make recovery possible.

## GPU Cluster Feasibility: OptiPlex 5060 SFF vs RTX 4090

The owner states the stack is twenty OptiPlex 5060 SFF units (8th-gen Core i7-8700, 16 GB
        DDR4-2666, 2x DisplayPort, Gigabit Ethernet) each paired with an RTX 4090-class GPU,
        racked separately and reserved for rental workloads. Before that statement can be taken
        at face value, the chassis and power numbers have to be confronted, because a 450 W
        RTX 4090 cannot simply be assumed to fit and operate safely inside an unmodified Small
        Form Factor office PC. The comparison below uses the manufacturers' own published
        specifications (sources linked in the references).

| Constraint | OptiPlex 5060 SFF (Dell spec) | GeForce RTX 4090 (NVIDIA spec) | Verdict |
| --- | --- | --- | --- |
| System power supply | 200 W (EPA Bronze or Platinum) | 450 W TGP for the card alone; NVIDIA recommends a minimum 850 W system PSU | Incompatible: the card alone draws more than double the entire PSU budget |
| Auxiliary GPU power | No 6/8-pin PCIe or 16-pin leads documented on the 200 W SFF supply | 16-pin 12VHPWR connector, up to 600 W delivery spec | Incompatible without a PSU and cabling redesign |
| Slot and bracket | 1x PCIe 3.0 x16, half-height (low profile) only | Full-height card, 3 slots thick | Incompatible: bracket and slot height |
| Physical length / clearance | Chassis 292 x 290 x 92.6 mm | 304 x 137 mm card (Founders Edition) | Incompatible: the card is longer than the chassis is deep |
| Slot power delivery | PCIe slot power capped at 75 W by spec, shared with a 65 W-class CPU on a 200 W budget | Draws up to 450 W through slot + connector | Incompatible |
| Cooling | Compact airflow designed around an office CPU and slot-powered GPU (factory options: GT 730 / RX 550 class) | 450 W continuous heat load | Incompatible: thermal envelope exceeded by an order of magnitude |

Conclusion: the OptiPlex 5060 SFF cannot host an RTX 4090 unmodified.
        The owner reports the GPU stack is already built, which means one of three things must be
        true for every node, and the register records it honestly as an open documentation gap:

- the stock 200 W PSU was replaced or supplemented (for example an external ATX or server PSU feeding the card's 16-pin connector), or

- the card sits outside the closed SFF chassis on a PCIe riser or open-frame mount, or

- the installed cards are not actually RTX 4090 reference-class parts.

Two evidence items resolve this completely: a photograph of one open node showing the card
        mounting and power cabling, and the nvidia-smi --query-gpu=name,power.limit --format=csv
        output from one node. A further naming note: the owner specification says "4090 Ti", but
        NVIDIA has not released an RTX 4090 Ti SKU as of this writing, so the cards are recorded
        as RTX 4090-class until the model string is captured. If the stack is ever rebuilt or
        expanded, the realistic platform options, in order of increasing effort:

- Tower workstations: full-size towers with 750 to 1000 W+ PSUs and full-length x16 slots (for example Dell Precision or Lenovo ThinkStation class towers) host one 4090-class card each with stock cooling. Highest per-node cost, lowest engineering risk.

- Open-frame GPU nodes: rack-mounted open frames with server-grade 1600 W+ PSUs and PCIe risers, the standard pattern for multi-GPU density. Cheap per slot, but demands deliberate cable, vibration, and dust management.

- SFF-respecting alternative: keep the OptiPlex 5060 SFF fleet for what it is genuinely good at (Proxmox nodes, network services, control-plane duties) and, if GPU-in-SFF is ever required, use low-profile 70 W cards in the RTX A2000 / RTX 4000 SFF Ada class that are engineered for exactly this chassis constraint, accepting their much smaller VRAM and throughput.

Electrical planning is part of the same question. Twenty 4090-class cards
        imply roughly 9 kW of GPU load alone, and 12 kW or more once CPUs, memory, storage, and
        cooling overhead are included. A single North American 15 A / 120 V household circuit
        supplies about 1.8 kW maximum, so a stack of this size needs multiple dedicated circuits,
        and realistically 240 V feeds, plus heat rejection for a continuous multi-kilowatt load in a
        residential basement. These are solvable problems, but they are electrical and HVAC
        projects in their own right, and they are recorded here as open engineering questions
        rather than glossed over.

Status of the GPU stack: PARTIALLY VERIFIED, owner-stated as built and
        reserved for rental workloads, with the power/mechanical integration and the exact GPU
        model string undocumented. No performance, uptime, or revenue claims are made anywhere on
        this site for it.

## Build Process: How the Estate Was Assembled

This narrative reconstructs the build from the owner's account (2026-10-21) combined with
        the photographed and documented evidence for the confirmed layers. Steps that rest on
        owner testimony alone say so; nothing here is presented as independently verified unless
        it is. The confirmed basement lab build is documented separately on the
        [Homelab Server Room](../work/infrastructure/homelab-server-room.html) page;
        this section covers the larger estate.

### Site selection and power mapping

Objective: pick the room and learn its electrical limits before racking anything. The basement provides year-round low ambient temperature and acoustic isolation, which is why both the confirmed lab and the stated estate live there. First action: map which outlets share which breakers, and budget the load per circuit. A Canadian household 15 A / 120 V circuit delivers about 1.8 kW maximum, so the estate's total draw determines how many circuits the racks must span. Verification: no warm plugs or cables under sustained load, checked by hand after the first full-power evening. Gap: per-circuit draw has not been instrumented; inline metering is in the verification checklist.

### Rack assembly and physical layout

Objective: one known place for every device. Per the owner: three large stacks carry the hosting estate (24 OptiPlex 5060 SFF units, the 4 JBOD enclosures, and the network core), a separate large stack carries the 20 GPU rental nodes, and a small standalone position holds the Raspberry Pi utility server. Layout rule carried over from the confirmed lab: network core sits between compute and storage so cable runs stay short, data and power are dressed separately, and nothing is stacked exhaust-to-intake. Verification: photographs of the confirmed room exist; the expansion stacks are PARTIALLY VERIFIED, pending the same photographic record.

### Network core

Objective: segment before you scale. The confirmed design uses 802.1Q VLANs (10 management, 20 cluster, 30 services) on a managed switch behind a router doing NAT, DHCP reservations, and inter-VLAN routing. The owner states Cisco switching serves the expanded racks; exact models, port counts, and link speeds are UNKNOWN until show version / show vlan brief output is captured. The discipline that matters at this scale: trunk ports between switches carry all VLANs, access ports pin each host to exactly one, and the GPU rental stack gets its own segment so tenant workloads never share a broadcast domain with the hosting estate or the household.

### Storage: cabling the JBOD fleet

Objective: roughly 2 PB of intended raw aggregate across 4 JBOD enclosures, presented to the hosting fleet for the media library, backups, and dataset retention. JBOD means the enclosure supplies power and connectivity only; redundancy, if any, is decided in software on the host (the capacity model above explains why the 2 PB figure is raw, not usable). Enclosure models, bay counts, drive populations, and the host interface are UNKNOWN. Verification when evidenced: lsblk against the expected drive count, SMART baselines per drive, and a measured raw-vs-usable split replacing the illustrative arithmetic in the storage model.

### Provisioning the 24-unit hosting fleet

Objective: turn 24 identical OptiPlex 5060 SFF boxes into a managed fleet instead of 24 snowflakes. The pattern that works at this count: image one unit, automate the rest. Each node gets a hypervisor or base OS install (Proxmox VE 8.x is the estate standard, per the confirmed lab), a fixed DHCP reservation, enrollment into monitoring, and a label matching its rack position. Per-unit CPU, RAM, and disk splits across this fleet are UNKNOWN; the capture commands are in the verification checklist. Common error at this step: letting units drift by hand-editing one box; recovery is to re-image from the fleet standard rather than patch the drift.

### Media library hosting

Objective: serve the movie, series, and anime library from the JBOD-backed storage to household devices. This is a self-hosted media stack on the hosting fleet: storage presented from the JBODs, a media server application organizing and streaming the library, and access limited to the owner's own network and accounts. The legal boundary is documented in the considerations section below: this site neither hosts nor redistributes media, and the library is a private system. Stack details (media server software, transcoding settings, library structure) are UNKNOWN pending configuration evidence.

### Chakor AI on ai.tyfsadik.org

Objective: serve the Chakor AI workspace at ai.tyfsadik.org from the estate. The owner states the hosting fleet runs it; the software itself is CONFIRMED and documented on the [Chakor](../work/infrastructure/chakor.html) and [TYF-AI](../work/infrastructure/tyf-ai-platform.html) pages, including the request lifecycle and the honest note that configured cloud providers mean not all inference traffic stays local. Public reachability follows the estate's standard pattern: the service stays private on its segment and is published through the zero-trust access layer documented on the [Proxmox Zero-Trust](../work/infrastructure/proxmox-zero-trust.html) page, so no inbound ports are opened on the router.

### GPU rental stack assembly

Objective: 20 GPU nodes, each an OptiPlex 5060 SFF (i7-8700, 16 GB DDR4-2666, Gigabit Ethernet) paired with an RTX 4090-class card, on their own stack and their own network segment, reserved for rental workloads. The feasibility section above is required reading for this step: the stock 200 W PSU and half-height chassis cannot power or house a 450 W card, so the power and mechanical integration method (external PSU, riser, open frame, or a different card) is the single most important documentation gap in this register. Tenant isolation, acceptable-use enforcement, and per-tenant resource limits are also undocumented and are listed in the considerations section.

### Raspberry Pi utility server: Pi-hole, security, domain watchdog

Objective: keep the estate's hygiene services on hardware independent of the big stacks, so DNS filtering and monitoring survive a rack outage. Owner-stated roles: Pi-hole DNS filtering for the household and lab, security monitoring, and a domain watchdog. The watchdog's job, as documented for this site, is failure detection and recovery: detect when a domain stops resolving or stops serving (distinguishing DNS problems, origin failures, registrar issues, certificate errors, and provider outages), alert the owner, and drive a documented recovery runbook. It does not, and cannot, reverse a registrar or registry action on its own; what it provides is fast detection and a rehearsed path to restore service. Board model and count: UNKNOWN.

### Operations: monitoring, backup, and the evidence loop

Objective: keep the estate observable and recoverable as it grows. The confirmed lab's pattern (Prometheus metrics, Grafana dashboards, snapshot plus off-host backup copies, and the replication-is-not-backup rule from the [Data Sovereignty Stack](../work/infrastructure/data-sovereignty-stack.html)) extends to the new hardware as it is evidenced. The closing loop is this register itself: every PARTIALLY VERIFIED row above names the exact evidence that will confirm it, and the checklist below is the runbook for collecting it.

## Legal, Licensing, and Operational Considerations

- Media library: self-hosting media is lawful for content the owner holds rights to; this website does not host, index, link to, or redistribute any media, and the library is a private system on the owner's own network. Nothing on this page should be read as offering media access to anyone else.

- GPU rental workloads: renting compute to third parties creates obligations the estate must meet before any tenant runs anything: an acceptable-use policy, tenant isolation at the network and hypervisor layers, abuse handling, and logging sufficient to attribute tenant actions. None of these are documented yet; they are prerequisites, not afterthoughts, and no rental service is claimed to operate.

- Pi-hole and monitoring privacy: DNS query logs and network telemetry about household devices are personal data in practice. They stay on the utility server, are not published, and retention is kept minimal.

- Domain watchdog scope: the automation detects failures and drives a recovery runbook. It is resilience against DNS, certificate, and hosting failures, not a mechanism to circumvent registrar, registry, or legal actions.

- Electrical and fire safety: a multi-kilowatt continuous load in a residence needs circuits, PDUs, and heat rejection designed for it. This is an electrician-and-insurance conversation before it is a server conversation.

## Verification Checklist: Evidence to Collect

These are the concrete evidence items that will move rows from PARTIALLY VERIFIED or
        UNKNOWN to CONFIRMED. Commands are labeled by the environment they run in. Placeholders
        in angle brackets are environment-specific values the operator supplies; nothing here
        publishes serial numbers, MAC addresses, or private IPs, which are recorded privately and
        summarized publicly.

### Per-host hardware capture (each Linux/Proxmox host)

Objective: publish make, model, CPU, RAM, and disk population per host. Verify success by matching the captured model string against the physical label on the chassis.

sudo dmidecode -t system | grep -E "Manufacturer|Product Name"
sudo lshw -short -C cpu -C memory -C disk
lsblk -d -o NAME,MODEL,SIZE,ROTA

### Drive health baseline (each storage host)

Objective: establish SMART baselines before trusting any capacity claim. Common error: running against a USB-attached enclosure that hides SMART; recover by attaching through the HBA or using the enclosure's documented passthrough.

sudo smartctl -a /dev/<disk> | grep -E "Model|Capacity|Power_On_Hours|Reallocated"

### Network inventory (managed switches)

Objective: record exact switch models, port maps, and VLAN configuration. On Cisco IOS-class gear: show version, show vlan brief, show interfaces status. Export the running configuration to offline storage before any change.

### Virtualization and cluster inventory (Proxmox shell and control plane)

Objective: reconcile the VM inventory against the physical hosts so nothing is double-counted.

pvesh get /nodes --output-format json
qm list
kubectl get nodes -o wide

### Photographic record

Objective: photograph each rack, enclosure front and rear (model labels visible), and the patched switch panels, then publish selected frames the way the server room page already does. Recovery rule: if a photo exposes a serial or address, retake or crop rather than publish.

### Power measurement

Objective: replace every unmeasured wattage on this site with a number from an inline meter, per circuit and per rack, before the GPU cluster's electrical design is finalized.

## References

Sources for the specifications quoted above. A vendor specification sheet establishes what a product is; it does not establish that this lab owns one, which is why these citations support the feasibility analysis and not the asset statuses.

- Dell, OptiPlex 5060 Small Form Factor Setup and Specifications: Power supply, 200 W EPA Bronze/Platinum PSU. Supports the PSU row of the feasibility table.

- Dell, OptiPlex 5060 SFF Setup and Specifications, chassis dimensions 292 x 290 x 92.6 mm, half-height PCIe 3.0 x16 + x4 slots, 4 DDR4 UDIMM slots (64 GB max). Supports the slot, clearance, and memory rows.

- NVIDIA, GeForce RTX 40 Series Power Specifications, RTX 4090 TGP 450 W, minimum recommended PSU 850 W, 16-pin connector guidance. Supports the power rows of the feasibility table.

- CNET, Nvidia GeForce RTX 4090 review, specification table, Founders Edition dimensions 304 x 137 mm, 3-slot, 24 GB GDDR6X. Supports the physical size row.

- IT Pro, Dell OptiPlex 5060 review, independent confirmation of the SFF chassis dimensions (93 mm wide). Corroborates the Dell dimensional specification.

## Related Documentation

- Homelab Server Room, the photographic record of the CONFIRMED physical layer.

- Kubernetes Infrastructure, the 7-node cluster running on the confirmed hosts.

- Data Sovereignty Stack, the replication-versus-backup discipline referenced in the storage model.

- Engineering Documentation hub, status conventions and the documentation philosophy this register applies.
