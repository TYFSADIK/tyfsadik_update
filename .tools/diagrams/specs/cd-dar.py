from svgdiagram import Bars, Flow, Sequence, Stack, Timeline

PAGE = "work/defence/cyber-defence-decision-analysis-response.html"

topology = (
    Flow("cddar-topology", "Lab network topology",
         "One Proxmox node with an isolated VLAN-aware bridge. The lab router separates the management VLAN "
         "(core, SOC and sensor VMs), the notional command network (dc01, ws01, srv01, srv02) and the attacker "
         "network, and connects the physical field kit and the analyst laptop over WireGuard.", cols=4)
    .node("home", "Home network", "internet, WireGuard endpoint", at=(0, 0), color="grey")
    .node("rtr", "lab-router 10.10.10.1", "nftables default-deny, WireGuard, DNS, lab-internet on/off", at=(0, 1), span=2, color="orange")
    .node("laptop", "Analyst laptop", "WireGuard 10.10.40.3, web consoles", at=(0, 3), color="grey")
    .group("VLAN 10 management", rows=(1, 1), cols=(0, 3), color="blue")
    .node("core", "cddar-core .10", "OpenSearch, Kafka, Grafana, NetBox, scorer", at=(1, 0), color="blue")
    .node("soc", "cddar-soc .11", "Wazuh, TheHive, Cortex, Velociraptor", at=(1, 1), color="blue")
    .node("sensor", "cddar-sensor .12", "Zeek, Suricata on a hub-mode copy of VLAN 20 and 66", at=(1, 2), color="cyan")
    .node("kit", "Field kit 10.10.40.2", "mini PC on k3s, own sensor, 10.10.30.0/24 behind it", at=(1, 3), color="green")
    .group("VLAN 20 notional command network", rows=(2, 2), cols=(0, 3), color="purple")
    .node("dc", "dc01 .10", "AD domain controller, criticality 5", at=(2, 0), color="purple")
    .node("ws", "ws01 .21", "Windows 11 workstation, criticality 2", at=(2, 1), color="purple")
    .node("s1", "srv01 .30", "mission web service, criticality 4", at=(2, 2), color="purple")
    .node("s2", "srv02 .31", "file share, criticality 3", at=(2, 3), color="purple")
    .group("VLAN 66 adversary", rows=(3, 3), cols=(1, 2), color="red")
    .node("atk", "atk01 10.10.66.10", "Caldera, nmap, DNS sink. Reaches VLAN 20 only", at=(3, 1), span=2, color="red")
    .edge("home", "rtr", "WAN")
    .edge("laptop", "rtr", dashed=True)
    .edge("rtr", "core").edge("rtr", "soc")
    .edge("rtr", "kit", dashed=True, exit="r", enter="t")
    .edge("sensor", "s1", "SPAN copy", dashed=True)
    .edge("atk", "ws", "attack path", exit="t", enter="b")
)

kit = (
    Flow("cddar-kit", "Field kit wiring",
         "The mini PC has three network ports: an uplink to the home network or any long-haul link, a downlink "
         "that is the gateway and DHCP server for the field switch, and a USB network card on the switch's mirror "
         "port so Zeek and Suricata see every field device's traffic.", cols=3)
    .node("wan", "Home network or long-haul link", "WireGuard tunnel back to the lab router", at=(0, 0), span=3, color="grey")
    .node("pc", "Mini PC kit01", "Ubuntu 24.04, k3s pod: Zeek + Suricata + Vector with a 4 GB disk buffer", at=(1, 0), span=3, color="green")
    .node("p1", "Switch port 1", "kit DOWNLINK, gateway 10.10.30.1, DHCP", at=(2, 0), color="blue")
    .node("p2", "Switch port 2", "mirror DESTINATION, kit USB capture NIC, no IP", at=(2, 1), color="orange")
    .node("p3", "Switch ports 3-5", "field devices, mirror SOURCES, 10.10.30.100-200", at=(2, 2), color="purple")
    .edge("wan", "pc", "UPLINK")
    .edge("pc", "p1", "DOWNLINK")
    .edge("p2", "pc", "CAPTURE")
    .edge("p3", "p2", "mirrored copy", dashed=True)
)

decision = (
    Sequence("cddar-decision", "From detection to an approved response",
             "A sensor detection travels through the pipeline to the scorer, which ranks it and opens a TheHive "
             "alert with reasons. Only the analyst can run a response. Every step is written to the hash-chained "
             "approval log.",
             [("sensor", "Sensors", "cyan"), ("pipe", "Vector + Kafka", "blue"), ("score", "Scorer", "yellow"),
              ("hive", "TheHive", "orange"), ("analyst", "Analyst", "green"), ("act", "Router / Velociraptor", "red"),
              ("log", "Approval log", "purple")])
    .msg("sensor", "pipe", "Suricata, Zeek or Wazuh alert")
    .msg("pipe", "pipe", "normalise to OCSF, store in OpenSearch")
    .msg("pipe", "score", "Detection Finding")
    .msg("score", "score", "criticality x stage x confidence x severity")
    .msg("score", "hive", "alert: score, priority, reasons")
    .msg("hive", "analyst", "ranked queue")
    .note("nothing acts on its own up to here", over=("sensor", "hive"))
    .msg("analyst", "act", "approve: block IP or collect evidence")
    .msg("act", "analyst", "result", dashed=True)
    .msg("hive", "log", "every event, hash-chained")
)

stack = (
    Stack("cddar-stack", "Software stack",
          "Five layers from capture to decision, all open source: sensors, transport, the Cyber Data Repository, "
          "decision services, and the analyst consoles.")
    .layer("Sensors", ["Zeek 7\nnetwork logs", "Suricata 7\nET Open + lab rules", "Wazuh 4.9\nhost alerts",
                       "Sysmon / auditd\nprocess events", "Nmap + NetBox\ndiscovery"], "cyan")
    .layer("Transport", ["Vector 0.62\nedge + core", "Kafka 3.9\n5 topics", "WireGuard\nkit and laptop"], "blue")
    .layer("Cyber Data Repository", ["OpenSearch 2.18\nOCSF 1.3 indices", "Index template\ntyped fields",
                                     "Retention\n30 / 180 days"], "green")
    .layer("Decision services", ["Scorer\nranked, with reasons", "Discovery\nactive + passive",
                                 "Approval log\nSHA-256 hash chain"], "yellow")
    .layer("Analyst consoles", ["Grafana\nCyber COP", "TheHive 5\ncases", "Cortex 3\nresponders",
                                "Velociraptor\nremote forensics"], "orange")
)

ram = (
    Bars("cddar-ram", "Planned memory per machine (GB)",
         "Memory allocated to each lab VM in the full build, 59 GB in total; the lite profile cuts core and SOC "
         "to 12 GB each.", unit="GB", max_value=20)
    .bar("cddar-core", 20, "OpenSearch, Kafka, NetBox", "blue")
    .bar("cddar-soc", 16, "Wazuh, TheHive, Cortex", "blue")
    .bar("cddar-sensor", 6, "Zeek, Suricata", "cyan")
    .bar("dc01 / ws01", 4, "each", "purple")
    .bar("atk01", 4, "Caldera", "red")
    .bar("srv01 / srv02", 2, "each", "purple")
    .bar("lab-router", 1, "", "orange")
)

scores = (
    Bars("cddar-scores", "Same detection, different asset: scorer output",
         "Scores produced by the testbed's scoring code for one LSASS credential-dumping detection "
         "(ATT&CK T1003.001, confidence 90%, severity critical) on assets of different criticality.",
         unit="", max_value=100)
    .bar("dc01, criticality 5", 92, "P1", "red")
    .bar("srv01, criticality 4", 87, "P1", "red")
    .bar("unknown asset (treated as 3)", 81, "P1", "orange")
    .bar("ws01, criticality 2", 73, "P2", "orange")
    .bar("atk01, criticality 1", 62, "P2", "yellow")
)

timeline = (
    Timeline("cddar-timeline", "Build status",
             "Where the build stands: the code and offline tests are done, the physical build is next, then the "
             "lab deployment, emulation runs and the deployable-kit outage test.")
    .phase("Code and offline tests", "86 files, 29 tests passing", "done")
    .phase("Physical build", "kit, switch, Windows VMs", "doing")
    .phase("Lab deploy", "deploy.sh all", "next")
    .phase("Emulation runs", "coverage, MTTD, MTTR", "next")
    .phase("Kit outage test", "zero lost events", "next")
)

DIAGRAMS = [topology, kit, decision, stack, ram, scores, timeline]
