# Engineering Decision Records

Why the major platform choices behind the homelab were made, what else was considered, and what it would take to reverse each one.

## About These Records

An Architecture Decision Record (ADR) is a short document that captures one significant technical choice: the context
      that forced it, the decision itself, the alternatives that were rejected, and the consequences. The value is in the
      reasoning, not the outcome, because future changes are judged against why the current state exists.

These records are reconstructed. They were written on 2026-10-21, after the systems they describe were
      already built and running. The reasoning is faithful to how the decisions were actually made at the time, but it was not
      written down contemporaneously, and memory is less reliable than a dated commit. Where a record states a fact about the
      lab, that fact matches what is shown on the corresponding project page. Where it states intent or future work, it is
      labeled as such.

## ADR-001: Proxmox VE as the Homelab Hypervisor

Date: Recorded 2026-10-21 (decision made earlier, during initial lab build).

Status: Accepted (reconstructed).

### Context

The lab runs on consumer hardware: three desktop PCs and four laptops in a basement server room. A hypervisor layer
      was needed to carve that hardware into virtual machines for the Kubernetes cluster and supporting services, with a
      management interface usable without dedicated out-of-band tooling, and with no per-socket licensing cost.

### Decision

Run Proxmox VE 8.x on all physical hosts, with Ubuntu 24.04 as the standard guest OS for cluster nodes.

### Alternatives Considered

- VMware ESXi: the most common enterprise hypervisor, but licensing after the Broadcom acquisition became uncertain and costly for a homelab, and the free tier was discontinued. Rejected on cost and continuity risk.

- Microsoft Hyper-V: capable and effectively free with Windows, but it pulls the lab toward a Windows-centric management stack and complicates running Linux guests at scale. Rejected on ecosystem fit.

- Bare-metal Linux with KVM and libvirt: maximum control and zero abstraction, but every host must be managed by hand or with additional tooling (Cockpit, virt-manager, or custom scripts). Rejected on operational overhead for a multi-host lab.

### Consequences

- Positive: one web UI manages all hosts, VMs, and LXC containers; live migration, snapshots, and backup jobs are built in; the Debian base means standard Linux tooling works on the hosts; no licensing cost.

- Negative: Proxmox-specific concepts (its storage model, its cluster quorum) are a skill set of their own that does not transfer one-to-one to ESXi shops; the no-subscription repository requires care during upgrades.

### Reversal Strategy

Guests are standard KVM virtual machines with virtio disks, so migration off Proxmox (to plain KVM/libvirt or another
      KVM-based platform) is a matter of exporting disk images and recreating VM definitions. No proprietary disk format or
      guest agent locks the workloads in. Estimated effort: a weekend per host, planned, not tested.

## ADR-002: kubeadm and Vanilla Kubernetes for the Learning Cluster

Date: Recorded 2026-10-21 (decision made at cluster inception).

Status: Accepted (reconstructed).

### Context

The lab's primary purpose is learning Kubernetes the way it is actually operated in production environments. The
      cluster has seven nodes spread across heterogeneous hardware, so the distribution choice determines how much of the
      real machinery (certificates, etcd, the API server, static pods) the operator has to understand and touch.

### Decision

Bootstrap the cluster with kubeadm on vanilla upstream Kubernetes, rather than a packaged distribution.

### Alternatives Considered

- k3s: a single-binary, lightweight distribution that removes much of the setup friction. Excellent for edge deployments, but it hides exactly the control-plane mechanics this lab exists to teach. Rejected on learning value, not on quality.

- MicroK8s: Canonical's snap-packaged Kubernetes, similarly convenient and similarly abstracted. Same rejection reason as k3s.

- OpenShift (OKD): a full enterprise platform with its own console, opinionated security defaults, and additional operators. Rejected as too heavyweight for the available RAM and too far from the upstream baseline for a first cluster.

### Consequences

- Positive: every component of the control plane is visible and configurable; troubleshooting skills transfer directly to managed services (EKS, GKE, AKS) and to kubeadm-based production clusters; upgrades follow the upstream release cadence.

- Negative: cluster setup and upgrades are manual multi-step procedures; certificate renewal and etcd health are the operator's problem; there is no vendor safety net.

### Reversal Strategy

The workloads are plain Kubernetes manifests and Helm releases, portable to any conformant cluster. Rebuilding on k3s
      or a managed service would mean redeploying workloads and migrating Longhorn volumes via backups, not re-architecting
      anything. The learning investment is not recoverable, but it was the point.

## ADR-003: Longhorn for Persistent Storage on Heterogeneous Hosts

Date: Recorded 2026-10-21.

Status: Accepted (reconstructed).

### Context

Cluster nodes are a mix of desktop PCs and laptops with different disk layouts and capacities, joined partly over a
      5 GHz wireless bridge. Stateful workloads (Grafana dashboards, Prometheus data, service databases) need persistent
      volumes that survive pod rescheduling, provisioned automatically through persistent volume claims.

### Decision

Deploy Longhorn v1.6.2 as the cluster's storage provisioner, replicating volumes across node-local disks.

### Alternatives Considered

- Ceph / Rook-Ceph: the standard for serious distributed storage, but its memory footprint and operational complexity (MONs, OSDs, placement groups) are a poor fit for nodes with laptop-grade RAM. Rejected on resource cost and operational burden.

- local-path-provisioner: trivially simple, but volumes are pinned to the node where they were created, so a pod rescheduled to another node loses its data. Rejected because it defeats rescheduling, which is half the point of Kubernetes.

- NFS-backed provisioner: simple and centralized, but it makes one machine a single point of failure and a bandwidth bottleneck for every volume. Rejected on availability, though NFS remains reasonable for bulk, non-critical file storage.

### Consequences

- Positive: PVCs are provisioned automatically and follow workloads across nodes; the Longhorn UI makes replica placement and volume health visible; snapshots and backups to external targets are built in; resource requirements fit the hardware.

- Negative: replication consumes disk (usable capacity is well under raw capacity) and network bandwidth, which matters on the wireless-linked nodes; write latency is higher than local disk; Longhorn adds its own operational surface that must be monitored and upgraded.

### Reversal Strategy

Volumes are standard block devices from Kubernetes' point of view. Reversal means configuring Longhorn backups to an
      external target, deploying the replacement provisioner, restoring data into new PVCs, and repointing workloads. Done
      workload-by-workload, it requires no cluster outage; it is tedious, not dangerous.

## ADR-004: MetalLB and ingress-nginx for LoadBalancer Services Without a Cloud

Date: Recorded 2026-10-21.

Status: Accepted (reconstructed).

### Context

On a cloud provider, a Service of type LoadBalancer gets an external IP automatically. On bare metal, nothing fills
      that role, and without it every service must be reached through per-node ports. The lab also needs hostname-based HTTPS
      routing with automated certificates, terminating at the cluster edge on VLAN 30 (services).

### Decision

Deploy MetalLB v0.14.5 in layer-2 mode to assign LoadBalancer IPs from a reserved pool on the services VLAN, and
      ingress-nginx v1.10.1 as the ingress controller, with cert-manager v1.15.0 issuing TLS certificates.

### Alternatives Considered

- NodePort everywhere: no extra components, but clients must know node IPs and high port numbers, node failure moves the port, and it does not compose cleanly with hostname routing or certificate automation. Rejected on operability.

- Traefik as the ingress controller: a strong controller with simpler defaults and built-in Let's Encrypt support. Rejected in favour of ingress-nginx because it is the reference implementation most documentation, troubleshooting guides, and employer environments assume; Traefik remains a reasonable swap.

### Consequences

- Positive: services get stable, routable IPs that behave like cloud load balancers; all HTTP(S) entry converges on one controller where TLS, rate limits, and routing rules live; certificates renew without manual work.

- Negative: MetalLB in layer-2 mode depends on ARP, so failover moves an IP by gratuitous ARP rather than true redundancy, and it is sensitive to network quirks on the wireless-linked nodes (observed in practice during node flapping); the ingress controller is a single logical chokepoint that must be watched.

### Reversal Strategy

Ingress resources are portable YAML. Swapping ingress-nginx for Traefik (or a Gateway API implementation) means
      installing the new controller and adjusting annotations. Removing MetalLB reverts services to NodePort with an external
      load balancer in front. Neither change touches application code.

## ADR-005: Zero-Trust Remote Access Instead of Port Forwarding

Date: Recorded 2026-10-21.

Status: Accepted (reconstructed).

### Context

The lab's management interfaces (Proxmox web UI, Grafana, internal services) need to be reachable from outside the
      house. The conventional homelab answer is port forwarding on the router plus dynamic DNS, which puts login pages
      directly on the public internet. The [zero-trust access page](../work/infrastructure/proxmox-zero-trust.html)
      documents the implemented alternative.

### Decision

Expose management and selected services through an outbound-only tunnel (Cloudflare Tunnel) with an identity-aware,
      zero-trust access layer in front. No inbound ports are opened on the router; every request is authenticated before it
      reaches the lab.

HTTPS, authenticated

allowed requests only

outbound only

Remote user

Zero-trust access layer

Outbound tunnel

Management interfacesProxmox, Grafana, services

Home routerno inbound ports open

### Alternatives Considered

- Port forwarding plus dynamic DNS: simple and fully self-controlled, but every exposed service must be hardened individually, scanning and credential-stuffing begin within minutes of opening a port, and residential IP changes add fragility. Rejected on attack surface.

- WireGuard-only: a strong answer for administrator access, and it remains appropriate as a fallback path. Rejected as the sole mechanism because it is a network-level VPN (once connected, the client is on the network) rather than per-service, identity-checked access, and it is awkward for sharing a single service with someone without giving them network access.

### Consequences

- Positive: no public IP or open inbound port is required; authentication and authorization happen at the edge, before traffic reaches the lab; per-service policies implement least privilege; access logs are centralized.

- Negative: remote access now depends on an external provider's availability and continued free tier; misconfigured access policies can lock the operator out (mitigated by physical access and the WireGuard fallback); traffic transits a third party, which is accepted for management UIs but noted as a privacy trade-off.

### Reversal Strategy

The tunnel is an overlay, not a re-architecture: the services it fronts still listen on their normal internal
      addresses. Reversal is deleting tunnel and access-policy configuration and re-enabling direct access (VPN or, worst
      case, port forwards). No data migrates and nothing inside the lab changes.

## ADR-006: Local-First AI Inference for Chakor and TYF-AI

Date: Recorded 2026-10-21.

Status: Accepted (reconstructed).

### Context

The self-hosted AI workspace ([Chakor](../work/infrastructure/chakor.html)) and the
      [TYF-AI platform](../work/infrastructure/tyf-ai-platform.html) pages describe local LLM inference on lab hardware.
      The motivating requirement is privacy: prompts and documents processed for personal and professional use should not
      leave the building by default. The constraint is hardware: local GPU VRAM limits which models and quantization levels
      produce usable tokens-per-second rates.

### Decision

Run inference locally first, using quantized GGUF models sized to fit available VRAM, with cloud providers
      configurable as an optional fallback for workloads that exceed local capability.

### Alternatives Considered

- Cloud-only: access to frontier models with zero local hardware burden. Rejected as the default because it makes every prompt a data-sharing decision with a third party and adds per-token cost; retained as an optional, explicitly configured fallback.

- Local-only, no fallback: maximal privacy, but hard-caps capability at what the hardware can run and turns every oversized request into a failure instead of a choice. Rejected in favour of making the fallback explicit and opt-in.

### Consequences

- Positive: by default, prompts and context stay on local hardware; there are no per-token costs for routine use; inference works during internet outages; quantization trade-offs (model quality versus VRAM) are a documented, tunable parameter rather than a black box.

- Negative: local models are smaller and weaker than frontier cloud models; generation speed is bounded by local VRAM bandwidth; local-first does not mean all traffic stays local: when a cloud provider is configured as a fallback, the requests routed to it leave the building under that provider's terms, and anyone auditing privacy must check the active configuration rather than assume it.

### Reversal Strategy

Both directions are cheap. Going cloud-only means removing local runners and pointing clients at provider APIs. Going
      local-only means removing the provider configuration. Neither requires data migration, since conversation storage and
      retrieval indexes live on lab storage in both arrangements.

## See Also

- Engineering Glossary, definitions for the terms used in these records.

- Documentation hub, the status labels referenced throughout this site.

- Kubernetes Infrastructure, the cluster these decisions produced, including failures and fixes.
