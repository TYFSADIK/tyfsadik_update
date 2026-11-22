from svgdiagram import Bars, Flow, Sequence, Stack, Timeline

PAGE = "work/defence/it-infrastructure-command-control.html"

sites = (
    Flow("itic2-sites", "Three sites",
         "Site A is the primary, site B a warm standby, site C holds the witness, global DNS, backups and "
         "monitoring. Each site has its own router; the routers form a WireGuard mesh over an emulated WAN, and "
         "site C is the only way out to the internet.", cols=3)
    .node("wan", "Emulated WAN (VLAN 100) + WireGuard mesh", "delay, loss and cuts injected per site", at=(0, 0), span=3, color="grey")
    .group("Site A, primary (VLAN 110)", rows=(1, 2), cols=(0, 0), color="green")
    .node("ra", "rtr-a 10.110.0.1", "nftables, WireGuard, wan-impair", at=(1, 0), color="orange")
    .node("ka", "K3s x3 (embedded etcd)", "C2 Board, database primary x3, Longhorn, MetalLB", at=(2, 0), color="green")
    .group("Site B, standby (VLAN 120)", rows=(1, 2), cols=(1, 1), color="blue")
    .node("rb", "rtr-b 10.120.0.1", "nftables, WireGuard, wan-impair", at=(1, 1), color="orange")
    .node("kb", "K3s x3 (embedded etcd)", "C2 Board standby, replica database x2, Longhorn", at=(2, 1), color="blue")
    .group("Site C, management (VLAN 130)", rows=(1, 2), cols=(2, 2), color="purple")
    .node("rc", "rtr-c 10.130.0.1", "WireGuard, NAT to the internet", at=(1, 2), color="orange")
    .node("mc", "mgmt-c1", "witness + failover controller, DNS, S3, Prometheus, Loki, Grafana", at=(2, 2), color="purple")
    .edge("ra", "wan").edge("rb", "wan").edge("rc", "wan")
    .edge("ra", "ka").edge("rb", "kb").edge("rc", "mc")
)

failover = (
    Sequence("itic2-failover", "Site failover, step by step",
             "Site A stops answering. Its own application stops writing once its lease runs out, then the witness "
             "moves the lease, points c2.lab at site B and promotes site B's database. Clients follow the DNS change.",
             [("cl", "C2 clients", "grey"), ("dns", "DNS c2.lab", "cyan"), ("wit", "Witness (site C)", "purple"),
              ("a", "Site A", "green"), ("b", "Site B", "blue")])
    .msg("a", "wit", "renew write lease every 2 s")
    .msg("wit", "a", "health check fails (site A lost)", dashed=True)
    .note("A cannot renew: it stops writing after 10 s", over=("wit", "a"))
    .msg("wit", "wit", "still failing after FAIL_AFTER")
    .msg("wit", "b", "lease to B, promote B's database")
    .msg("wit", "dns", "c2.lab -> site B")
    .msg("cl", "dns", "resolve (TTL 2 s)")
    .msg("cl", "b", "writes resume at site B")
)

layers = (
    Stack("itic2-layers", "Layers of redundancy",
          "Each failure is caught by the smallest layer that can handle it. Only a whole-site failure moves the "
          "service to another site.")
    .layer("Application", ["C2 Board x2\nper site", "Kubernetes\nrestarts", "Write lease\nfencing"], "green")
    .layer("Database", ["CloudNativePG\nin-site failover", "Replica cluster\nat site B", "WAL + base backups\nto S3"], "blue")
    .layer("Platform", ["K3s 3 servers\nembedded etcd", "Longhorn\n3 replicas", "MetalLB\nservice addresses"], "cyan")
    .layer("Network", ["Site routers\nnftables", "WireGuard\nfull mesh", "Global DNS\nTTL 2 s"], "orange")
    .layer("Operations", ["Prometheus\n+ Alloy", "Loki\nlogs", "Grafana\navailability", "Velero + Longhorn\nbackups"], "purple")
)

physical = (
    Flow("itic2-physical", "Option B: one physical host per site",
         "Three mini PCs on a managed switch. Port 1 of each goes to the home network for the Proxmox console; "
         "port 2 is a trunk carrying the four lab VLANs. Pulling a power cord or a trunk cable is a real site "
         "failure.", cols=3)
    .node("home", "Home router", "internet, Proxmox web consoles", at=(0, 1), color="grey")
    .node("sw", "Managed switch", "port 1 home LAN; ports 2-4 trunk, VLANs 100/110/120/130", at=(1, 1), color="orange")
    .node("p1", "pve1 = site A", "mini PC, 16 GB, smart plug", at=(2, 0), color="green")
    .node("p2", "pve2 = site B", "mini PC, 16 GB, smart plug", at=(2, 1), color="blue")
    .node("p3", "pve3 = site C", "mini PC, 16 GB, smart plug", at=(2, 2), color="purple")
    .edge("home", "sw").edge("sw", "p1", "trunk").edge("sw", "p2", "trunk").edge("sw", "p3", "trunk")
)

ram = (
    Bars("itic2-ram", "Memory per VM (GB), full build",
         "29.5 GB across ten VMs on one Proxmox host; lite mode uses 3 GB for the K3s and management VMs, "
         "about 20 GB in total.", unit="GB", max_value=12)
    .bar("Site A K3s (3 VMs)", 12, "4 GB each", "green")
    .bar("Site B K3s (3 VMs)", 12, "4 GB each", "blue")
    .bar("mgmt-c1", 4, "witness, DNS, S3, monitoring", "purple")
    .bar("Routers (3 VMs)", 1.5, "0.5 GB each", "orange")
)

timeline = (
    Timeline("itic2-timeline", "Build status",
             "The code and the local rehearsal are done; the Proxmox build and its measured runs come next.")
    .phase("Code", "Terraform, Ansible, services; 21 tests", "done")
    .phase("Local rehearsal", "4 runs, 0 lost writes", "done")
    .phase("Proxmox build", "10 VMs, 3 sites", "doing")
    .phase("Measured runs", "8 scenarios on VMs", "next")
    .phase("Physical sites", "3 hosts, pulled cords", "next")
)

rto = (
    Bars("itic2-rto", "Longest client outage per failure (s)",
         "Longest run of failed writes seen by the prober in each scenario of rehearsal run 4. Zero means no write failed.", unit="s")
    .bar("app pod killed", 0, "0 lost writes", "green")
    .bar("DB primary pod killed", 0, "0 lost writes", "green")
    .bar("node powered off", 29, "0 lost writes", "yellow")
    .bar("degraded WAN", 0, "0 lost writes", "green")
    .bar("witness (site C) lost for 60 s", 54.5, "0 lost writes", "orange")
    .bar("site A lost", 95.9, "0 lost writes", "red")
)

DIAGRAMS = [sites, failover, layers, rto, physical, ram, timeline]
