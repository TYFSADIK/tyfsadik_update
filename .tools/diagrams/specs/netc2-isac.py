from svgdiagram import Bars, Flow, Sequence, Stack, Timeline

PAGE = "work/defence/network-c2-situational-awareness.html"

platform = (
    Flow("isac-platform", "From probes to mission impact",
         "Probes at each site run real transactions every 2 seconds. The engine judges each probe against its own "
         "learned normal, infers which component is really broken, and pushes the impact up a service model to the "
         "mission capabilities a commander cares about.", cols=4)
    .node("hq", "HQ services", "DNS, directory, database, broker, C2 app", at=(0, 0), color="grey")
    .node("dep", "Deployed site", "DNS, gateway; the WAN to HQ", at=(1, 0), color="grey")
    .node("ph", "Prober at HQ", "9 real transactions, every 2 s", at=(0, 1), color="blue")
    .node("pd", "Prober at the deployed site", "5 transactions, incl. WAN loss", at=(1, 1), color="blue")
    .node("judge", "Probe judgement", "down, or slower than its own normal", at=(0, 2), color="yellow")
    .node("root", "Root cause", "smallest set that explains it all, site-aware", at=(1, 2), color="red")
    .node("model", "Service model", "4 capabilities, 6 services, 8 components", at=(2, 2), color="purple")
    .node("cmd", "Commander's view", "capabilities, incident, evidence", at=(0, 3), color="green")
    .node("graf", "Grafana", "technicians: components, latency, loss", at=(1, 3), color="green")
    .edge("hq", "ph").edge("dep", "pd").edge("ph", "judge").edge("pd", "judge", exit="r", enter="b")
    .edge("judge", "root", exit="b", enter="t").edge("model", "root", exit="t", enter="b")
    .edge("root", "cmd").edge("root", "graf")
)

inference = (
    Sequence("isac-inference", "A lossy WAN, step by step",
             "The deployed site's orders time out while the same orders at HQ pass, so the failure is on the path. The "
             "WAN probe confirms it: the WAN is degraded, and the deployed site's command capability is down.",
             [("dep", "Deployed probes", "blue"), ("hq", "HQ probes", "blue"), ("eng", "Engine", "red"),
              ("cmd", "Commander", "green")])
    .msg("dep", "eng", "orders and picture time out from the deployed site")
    .msg("hq", "eng", "the same orders and picture pass at HQ")
    .msg("eng", "eng", "same check passes at HQ: the failure is on the path, not the C2 application")
    .msg("dep", "eng", "WAN probe: round trip far above its normal, 10% loss")
    .msg("eng", "cmd", "WAN degraded; command from the deployed site not available")
)

results = (
    Bars("isac-detection", "Time to detect each fault, median of 3 runs (s)",
         "From injecting the fault until an incident names the real cause. Every fault was detected, with the right "
         "cause first, in every run.", unit="s")
    .bar("Disk filling (a warning)", 5.4, "", "green")
    .bar("Certificate expired", 5.4, "", "green")
    .bar("Directory hangs", 7.1, "", "green")
    .bar("C2 application crashes", 7.5, "", "green")
    .bar("C2 application overloaded", 8.7, "", "green")
    .bar("Database hangs", 8.8, "", "green")
    .bar("WAN degraded", 9.2, "", "yellow")
    .bar("HQ DNS stops", 9.3, "", "yellow")
    .bar("Gateway stops", 9.3, "", "yellow")
    .bar("WAN cut", 9.5, "", "yellow")
    .bar("Broker stops", 11.4, "", "yellow")
    .bar("Deployed DNS stops", 15.0, "", "red")
)

stack = (
    Stack("isac-stack", "Software stack",
          "Open source throughout; the probes, the service model, the engine and the rehearsal are my own.")
    .layer("Estate", ["CoreDNS\nx2", "OpenLDAP", "Postgres\n+ disk agent", "Mosquitto", "C2 app\nFastAPI, TLS"], "grey")
    .layer("Network", ["Docker networks\nHQ, deployed, mgmt", "socat gateway", "tc netem\nWAN faults"], "blue")
    .layer("Probes", ["Python\nreal transactions", "Prometheus\nmetrics"], "yellow")
    .layer("Engine", ["Learned\nbaselines", "Root cause\nsite-aware", "Impact\nservice model", "Incidents"], "red")
    .layer("Views", ["Commander's\nview", "Grafana"], "green")
)

timeline = (
    Timeline("isac-timeline", "Build status",
             "The engine is validated by fault injection on a small estate; next is more telemetry and a larger, "
             "discovered service model.")
    .phase("Estate + probes", "2 sites, 14 checks", "done")
    .phase("Engine", "root cause, impact", "done")
    .phase("Rehearsal 2", "36 of 36", "done")
    .phase("Host metrics", "every server", "next")
    .phase("Discovered model", "traffic, CMDB", "next")
)

DIAGRAMS = [platform, inference, results, stack, timeline]
