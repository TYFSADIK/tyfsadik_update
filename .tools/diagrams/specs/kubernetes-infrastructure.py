from svgdiagram import Flow, Stack

PAGE = "work/infrastructure/kubernetes-infrastructure.html"

physical = (
    Flow("k8s-physical", "Physical network topology",
         "ISP uplink into a router doing NAT, firewall, DHCP and inter-VLAN routing; a managed switch trunks VLANs 10, 20 "
         "and 30 to three wired desktop nodes and a 5 GHz wireless radio that bridges four laptop worker nodes.", cols=4)
    .node("isp", "ISP uplink", "public internet", at=(0, 0), color="red")
    .node("rtr", "Router", "NAT, firewall, DHCP, inter-VLAN routing, port forwarding", at=(0, 1), span=2, color="orange")
    .node("sw", "Managed switch", "802.1Q trunk: VLAN 10 management, VLAN 20 cluster, VLAN 30 storage", at=(1, 1), span=2, color="green")
    .group("Desktop nodes, wired", rows=(2, 2), cols=(0, 2), color="cyan")
    .node("pc1", "PC-01", "control plane, 8C / 32 GB / 512 GB NVMe, etcd + API server", at=(2, 0), color="cyan")
    .node("pc2", "PC-02", "worker, 6C / 16 GB / 1 TB SSD, Longhorn storage", at=(2, 1), color="cyan")
    .node("pc3", "PC-03", "worker, 6C / 16 GB / 1 TB SSD, Longhorn storage", at=(2, 2), color="cyan")
    .node("radio", "Wireless radio", "5 GHz backhaul, bridge mode", at=(2, 3), color="green")
    .group("Laptop nodes, wireless", rows=(3, 3), cols=(0, 3), color="purple")
    .node("lp1", "Laptop-01", "worker, 4C / 8 GB / 256 GB", at=(3, 0), color="purple")
    .node("lp2", "Laptop-02", "worker, 4C / 8 GB / 256 GB", at=(3, 1), color="purple")
    .node("lp3", "Laptop-03", "worker, 4C / 8 GB / 512 GB", at=(3, 2), color="purple")
    .node("lp4", "Laptop-04", "worker, 4C / 16 GB / 512 GB", at=(3, 3), color="purple")
    .edge("isp", "rtr", "WAN")
    .edge("rtr", "sw", "VLAN trunk")
    .edge("sw", "pc1").edge("sw", "pc2", "Ethernet, VLAN 20").edge("sw", "pc3").edge("sw", "radio")
    .edge("radio", "lp1").edge("radio", "lp2").edge("radio", "lp3").edge("radio", "lp4", "5 GHz bridge")
)

stack = (
    Stack("k8s-stack", "Virtualization and cluster stack",
          "Five layers from bare metal to services: Proxmox hosts, Ubuntu Server VMs acting as Kubernetes nodes, three "
          "VLAN network planes, cluster services (Calico, MetalLB, Nginx Ingress, Longhorn, observability), and nine "
          "hosted services.")
    .layer("Physical hosts\nProxmox VE 8.x", ["PC-01\n8C / 32 GB / 512 GB NVMe", "PC-02\n6C / 16 GB / 1 TB SSD",
                                              "PC-03\n6C / 16 GB / 1 TB SSD", "Laptops 01 to 04\n5 GHz backhaul"], "orange")
    .layer("Kubernetes nodes\nUbuntu Server 24.04 VMs", ["Control plane VM\nkube-apiserver, etcd",
                                                         "Worker VMs 1 and 2\non desktop hosts",
                                                         "Worker VMs 3 to 6\non laptop hosts"], "cyan")
    .layer("Network planes", ["VLAN 10 management\n10.10.10.0/24", "VLAN 20 cluster\n10.20.20.0/24",
                              "VLAN 30 storage\n10.30.30.0/24"], "blue")
    .layer("Cluster services", ["Calico CNI\npod network + policy", "MetalLB L2\nservice IPs", "Nginx Ingress\nTLS via cert-manager",
                                "Longhorn\n3x replicas", "Prometheus\nGrafana, Loki"], "green")
    .layer("Hosted services\nnine in total", ["Files and photos\nNextcloud, Immich", "Knowledge\nKiwix, SearXNG",
                                              "AI\nTYF-AI", "Network\nPi-hole DNS, Email",
                                              "Monitoring\nGrafana, Prometheus + Loki"], "purple")
)

architecture = (
    Flow("k8s-architecture", "Kubernetes component architecture",
         "Control plane components on PC-01, worker components on every node, the Calico, MetalLB and Nginx Ingress "
         "network path, Longhorn storage from volume to claim, and the Prometheus, Loki and Grafana observability stack.",
         cols=4)
    .group("Control plane, PC-01", rows=(0, 0), cols=(0, 3), color="red")
    .node("etcd", "etcd", "cluster state store", at=(0, 0), color="red")
    .node("api", "kube-apiserver", ":6443", at=(0, 1), color="red")
    .node("sched", "kube-scheduler", "places pods", at=(0, 2), color="red")
    .node("cm", "kube-controller-manager", "reconciles state", at=(0, 3), color="red")
    .group("Every worker node", rows=(1, 1), cols=(0, 2), color="cyan")
    .node("cr", "containerd", "container runtime", at=(1, 0), color="cyan")
    .node("kubelet", "kubelet", "runs and reports pods", at=(1, 1), color="cyan")
    .node("kproxy", "kube-proxy", "iptables / IPVS rules", at=(1, 2), color="cyan")
    .group("Network path", rows=(2, 2), cols=(1, 3), color="green")
    .node("calico", "Calico CNI", "pod network, NetworkPolicy", at=(2, 1), color="green")
    .node("mlb", "MetalLB", "L2 / ARP external IP pool", at=(2, 2), color="green")
    .node("ing", "Nginx Ingress", "TLS termination", at=(2, 3), color="green")
    .group("Storage", rows=(3, 3), cols=(1, 3), color="purple")
    .node("lh", "Longhorn", "block storage, 3x replication", at=(3, 1), color="purple")
    .node("pv", "PersistentVolume", at=(3, 2), color="purple")
    .node("pvc", "PersistentVolumeClaim", at=(3, 3), color="purple")
    .group("Observability", rows=(4, 5), cols=(0, 3), color="yellow")
    .node("nx", "Node Exporter", "hardware metrics", at=(4, 0), color="yellow")
    .node("prom", "Prometheus", "metrics store", at=(4, 1), color="yellow")
    .node("graf", "Grafana", "dashboards + alerts", at=(4, 2), color="yellow")
    .node("loki", "Loki", "log store", at=(4, 3), color="yellow")
    .node("ptail", "Promtail", "ships node and pod logs", at=(5, 3), color="yellow")
    .edge("api", "etcd").edge("sched", "api").edge("cm", "api", exit="t", enter="t", bend=-14)
    .edge("kubelet", "api", "watch / report").edge("kubelet", "cr")
    .edge("kproxy", "calico").edge("calico", "mlb").edge("mlb", "ing")
    .edge("lh", "pv").edge("pv", "pvc")
    .edge("nx", "prom", "node + kubelet metrics").edge("prom", "graf").edge("loki", "graf").edge("ptail", "loki", "logs")
)

pipeline = (
    Flow("k8s-cicd", "CI/CD pipeline",
         "A git push triggers GitHub Actions, which builds and pushes an image to Docker Hub; Kubernetes pulls it and "
         "rolls it out, health checks gate the rollout, and Prometheus and Grafana watch the result.", cols=4)
    .node("dev", "Developer", "git push", at=(0, 0), color="cyan")
    .node("ci", "GitHub Actions", "CI pipeline", at=(0, 1), color="yellow")
    .node("reg", "Container registry", "Docker Hub", at=(0, 2), color="green")
    .node("apply", "Kubernetes", "kubectl apply", at=(0, 3), color="cyan")
    .node("roll", "Rolling update", "one pod at a time", at=(1, 3), color="cyan")
    .node("health", "Health checks", "liveness + readiness", at=(1, 2), color="green")
    .node("prom", "Prometheus", "monitoring", at=(1, 1), color="yellow")
    .node("graf", "Grafana", "alerts + dashboards", at=(1, 0), color="yellow")
    .edge("dev", "ci", "webhook").edge("ci", "reg", "build + push").edge("reg", "apply", "image pull")
    .edge("apply", "roll").edge("roll", "health").edge("health", "prom", "metrics").edge("prom", "graf")
)

DIAGRAMS = [physical, stack, architecture, pipeline]
