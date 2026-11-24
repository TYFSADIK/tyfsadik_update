from svgdiagram import Bars, Flow, Sequence, Stack, Timeline

PAGE = "work/defence/canadian-advanced-synthetic-environment.html"

platform = (
    Flow("case-platform", "Two training sites and one twin",
         "Site A simulates a real town from OpenStreetMap: traffic, sensors, weather, floods, plumes and power "
         "cuts. Site B joins over a WAN with a UAV, a convoy and a ROS 2 robot. Everything meets in the twin, "
         "which records, classifies and shows it in 3D.", cols=4)
    .node("sim", "Site A simulation", "an OpenStreetMap town: 100 vehicles, 95 sensors, events and faults", at=(0, 0), color="blue")
    .node("mq", "MQTT broker", "sensor telemetry", at=(0, 1), color="blue")
    .node("tw", "Twin backend", "record, detect, serve", at=(0, 2), color="purple")
    .node("pg", "PostGIS", "world, telemetry, alerts, impacts", at=(0, 3), color="purple")
    .node("sb", "Site B federates", "survey UAV, 3-vehicle convoy, ROS 2 patrol robot with a DIS bridge", at=(1, 0), span=2, color="green")
    .node("gw", "DIS gateway", "across the WAN (tc netem)", at=(1, 2), color="orange")
    .node("hw", "ESP32 field node", "BME280, PMS5003, ultrasonic water gauge, over MQTT", at=(2, 0), span=2, color="red")
    .node("view", "CesiumJS 3D viewer", "live map, alerts, instructor injects, ground truth", at=(2, 2), span=2, color="yellow")
    .edge("sim", "mq", "sensors").edge("mq", "tw").edge("tw", "pg")
    .edge("sb", "gw", "DIS").edge("gw", "tw", "WAN", exit="t", enter="b")
    .edge("pg", "view", exit="b", enter="t")
)

detector = (
    Flow("case-detector", "Sensor fault or real event?",
         "Every simulated minute each sensor is compared with its neighbours, its type and its own last hour. "
         "An IsolationForest flags unusual patterns; then the twin explains them in space.", cols=4)
    .node("f", "Features", "neighbours, type reference, own trend, flat, spike, noise", at=(0, 0), color="grey")
    .node("if", "IsolationForest + thresholds", "trained on the first 30 minutes", at=(0, 1), color="blue")
    .node("o", "Outage?", "substation load collapses or its sensors fall silent together", at=(0, 2), color="yellow")
    .node("e", "Event", "nearby sensors deviating together and agreeing: flood, plume, storm", at=(0, 3), color="purple")
    .node("w", "Unexplained, watching", "alone, no fault signature yet", at=(1, 1), color="orange")
    .node("s", "Sensor fault", "flat, spike, noise, silent, or alone for 8 of 15 minutes", at=(1, 2), color="red")
    .node("p", "PostGIS impacts", "shoreline band or substation service area", at=(1, 3), color="green")
    .edge("f", "if").edge("if", "o").edge("o", "e")
    .edge("if", "w", exit="b", enter="t").edge("w", "s")
    .edge("e", "p", exit="b", enter="t")
)

inject = (
    Sequence("case-inject", "An instructor inject, end to end",
             "Measured in the final run, in real time: a plume released at the police station became a plume alert "
             "on the twin 177 seconds later, with no ground truth reaching the detector.",
             [("ins", "Instructor (viewer)", "yellow"), ("tw", "Twin backend", "purple"), ("sim", "Site A sim", "blue"),
              ("sen", "Air sensors", "green"), ("det", "Detector", "red"), ("pg", "PostGIS", "purple")])
    .msg("ins", "tw", "POST /api/inject: plume here")
    .msg("tw", "sim", "case/control (and recorded)")
    .msg("sim", "sen", "Gaussian plume spreads downwind")
    .msg("sen", "det", "readings rise near the source")
    .msg("det", "ins", "first sensor: unexplained, watching", dashed=True)
    .msg("det", "ins", "neighbours agree: PLUME event")
    .msg("det", "pg", "footprint: buildings, roads, assets", dashed=True)
)

stack = (
    Stack("case-stack", "Software stack",
          "All open source. The world builder, simulation, detector, twin backend and viewer are my own.")
    .layer("World", ["OpenStreetMap\nBarrie extract", "Shapely +\nNetworkX", "PostGIS 16\nspatial store"], "grey")
    .layer("Simulation", ["Site A\ntraffic, sensors, events", "Site B\nUAV, convoy", "ROS 2 Jazzy\npatrol robot"], "blue")
    .layer("Interoperability", ["MQTT\nMosquitto", "DIS v7 ESPDUs\nOpen DIS", "Gateway\ntc netem WAN"], "orange")
    .layer("Twin", ["FastAPI\nbackend", "IsolationForest\n+ spatial reasoning", "Hash-chained\nrecording + replay"], "purple")
    .layer("View", ["CesiumJS\n3D viewer", "Instructor\ninjects + truth", "ESP32\nfield node"], "green")
)

dr = (
    Bars("case-dr", "UAV position error on the twin at 18 m/s (metres, mean)",
         "Measured in the final run across the site B gateway. Holding the last report is useless; dead reckoning "
         "from the receive time loses speed x latency; using the PDU's own timestamp (synchronised clocks) "
         "cancels the WAN.", unit="m")
    .bar("LAN, from arrival", 0.15, "", "green")
    .bar("50 ms, from arrival", 1.01, "", "yellow")
    .bar("150 ms, from arrival", 2.79, "", "orange")
    .bar("150 ms, from timestamp", 0.24, "", "green")
    .bar("300 ms, from arrival", 5.52, "", "red")
    .bar("300 ms, from timestamp", 0.35, "", "green")
)

timeline = (
    Timeline("case-timeline", "Build status",
             "The synthetic environment runs end to end in Docker and is measured; the field node and the second "
             "physical site come next.")
    .phase("World + simulation", "OSM, 95 sensors, 4 events", "done")
    .phase("Twin + detector", "2 exercises, 2 Docker runs", "done")
    .phase("Field sensor node", "ESP32 on the waterfront", "doing")
    .phase("Second physical site", "real WAN", "next")
    .phase("Real ROS 2 robot", "rover joins via DIS", "next")
)

DIAGRAMS = [platform, detector, inject, dr, stack, timeline]
