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
             "Detections are scored and correlated into an incident, a local model explains the incident with "
             "evidence, code checks the explanation, and only the analyst can run a response. Every step is "
             "written to the hash-chained approval log.",
             [("sensor", "Sensors + rules", "cyan"), ("score", "Scorer", "yellow"), ("corr", "Correlator", "blue"),
              ("ai", "Local LLM", "purple"), ("hive", "TheHive", "orange"), ("analyst", "Analyst", "green"),
              ("act", "Playbooks", "red")])
    .msg("sensor", "score", "finding with ATT&CK technique")
    .msg("score", "corr", "score, priority, reasons")
    .msg("corr", "hive", "one alert per incident, with timeline")
    .msg("corr", "ai", "incident evidence E1..En")
    .msg("ai", "hive", "summary, checked in code, suggestions only")
    .note("nothing acts on its own up to here", over=("sensor", "hive"))
    .msg("hive", "analyst", "ranked incident queue")
    .msg("analyst", "act", "approve: triage, contain or block")
    .msg("act", "analyst", "result, every step logged", dashed=True)
)

aisoc = (
    Flow("cddar-aisoc", "AI-assisted SOC pipeline",
         "Logs from Linux, Windows and the network are collected, normalised and stored; a Python detection "
         "engine and the sensors' rules produce findings; the scorer ranks them; the correlator groups them into "
         "incidents; a local model explains each incident; the analyst approves any response; everything is "
         "audited and reported.", cols=4)
    .node("src", "Linux, Windows, network", "14 test machines, Zeek, Suricata, field kit", at=(0, 0), color="grey")
    .node("col", "Log collection", "Wazuh, Sysmon, auditd, Vector, Kafka, Splunk HEC input", at=(0, 1), color="blue")
    .node("cdr", "Data repository", "OpenSearch (OCSF) and a copy in the Daru SIEM", at=(0, 2), color="blue")
    .node("det", "Detection engine", "Python rules: match, threshold, sequence, plus sensor rules", at=(0, 3), color="cyan")
    .node("score", "Scoring", "criticality x stage x confidence x severity", at=(1, 3), color="yellow")
    .node("corr", "Incident correlation", "shared IP or user within 30 min, merged stories", at=(1, 2), color="yellow")
    .node("ai", "AI investigation", "local LLM on vLLM, evidence-cited, checked in code", at=(1, 1), color="purple")
    .node("dash", "Analyst dashboard", "Grafana COP, incidents, TheHive cases", at=(1, 0), color="orange")
    .node("appr", "Human approval", "analyst starts a responder", at=(2, 0), color="green")
    .node("resp", "Response playbooks", "triage, contain, release, block", at=(2, 1), color="red")
    .node("audit", "Audit and reporting", "hash-chained log, incident reports", at=(2, 2), span=2, color="grey")
    .edge("src", "col").edge("col", "cdr").edge("cdr", "det")
    .edge("det", "score").edge("score", "corr").edge("corr", "ai").edge("ai", "dash")
    .edge("dash", "appr").edge("appr", "resp").edge("resp", "audit")
)

guardrails = (
    Flow("cddar-guardrails", "How the model's answer is checked",
         "The incident's evidence is numbered and cleaned, the model answers in JSON, and code removes any "
         "statement without valid evidence, any action outside the allow-list and any target not in the evidence. "
         "If nothing grounded is left, the model gets one retry. Only the checked answer reaches the analyst.", cols=4)
    .node("ev", "Number and clean the evidence", "E1..En findings, C1..Cn context; attacker text stripped and cut", at=(0, 0), color="cyan")
    .node("llm", "Local model (vLLM)", "evidence fenced as data; JSON answer only", at=(0, 1), color="purple")
    .node("chk", "Checks in code", "cited ids exist, action on the allow-list, target in the evidence", at=(0, 2), color="yellow")
    .node("out", "Checked summary", "into TheHive, suggestions only; hashes to the approval log", at=(0, 3), color="green")
    .node("drop", "Removed and listed", "uncited claims, unknown targets, disallowed actions", at=(1, 2), color="red")
    .edge("ev", "llm").edge("llm", "chk").edge("chk", "out", "kept")
    .edge("chk", "drop", "fails")
    .edge("drop", "llm", "nothing grounded: one retry", dashed=True, exit="l", enter="b")
)

stack = (
    Stack("cddar-stack", "Software stack",
          "Six layers from capture to decision, all open source: sensors, transport, the Cyber Data Repository and "
          "SIEM, detection and decision services, the AI layer, and the analyst consoles.")
    .layer("Sensors", ["Zeek 7\nnetwork logs", "Suricata 7\nET Open + lab rules", "Wazuh 4.9\nhost alerts",
                       "Sysmon / auditd\nprocess events", "Nmap + NetBox\ndiscovery"], "cyan")
    .layer("Transport", ["Vector 0.62\nedge + core", "Kafka 3.9\n8 topics", "Splunk HEC\ninput", "WireGuard\nkit and laptop"], "blue")
    .layer("Repository and SIEM", ["OpenSearch 2.18\nOCSF 1.3 indices", "Daru SIEM\nClickHouse", "Retention\n30 / 180 days"], "green")
    .layer("Detection and decision", ["Detection engine\nYAML rules", "Scorer\nranked, with reasons",
                                      "Correlator\nincidents", "Approval log\nSHA-256 chain"], "yellow")
    .layer("AI layer", ["vLLM\nlocal model on my GPU", "Investigator\nevidence-cited summary", "Checks in code\nallow-list, citations"], "purple")
    .layer("Analyst consoles", ["Grafana\nCOP + incidents", "TheHive 5\ncases", "Cortex 3\nplaybooks",
                                "Velociraptor\nforensics + quarantine"], "orange")
)

ram = (
    Bars("cddar-ram", "Planned memory per machine (GB)",
         "Memory allocated to each lab VM in the full build, 71 GB in total; the lite profile cuts core and SOC "
         "and uses four extra test machines instead of eight. The language model runs on a separate GPU machine.",
         unit="GB", max_value=20)
    .bar("cddar-core", 20, "OpenSearch, Kafka, NetBox, AI services", "blue")
    .bar("cddar-soc", 20, "Wazuh, Daru, TheHive, Cortex", "blue")
    .bar("cddar-sensor", 6, "Zeek, Suricata", "cyan")
    .bar("srv03-srv10", 8, "1 GB each, 8 machines", "purple")
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
             "Where the build stands: the lab code and the AI SOC layer are written and tested offline, the "
             "physical build is next, then the lab deployment, the model on vLLM, and the test runs.")
    .phase("Lab code", "pipeline, COP, forensics, kit", "done")
    .phase("AI SOC layer", "rules, incidents, LLM, playbooks; 62 tests", "done")
    .phase("Physical build", "kit, switch, Windows, GPU", "doing")
    .phase("Lab deploy", "deploy.sh all + llm", "next")
    .phase("Test runs", "scripted, Caldera, Atomic", "next")
)

DIAGRAMS = [topology, kit, decision, aisoc, guardrails, stack, ram, scores, timeline]
