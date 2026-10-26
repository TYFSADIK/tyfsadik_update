# Mini Airspace Deconfliction Manager

Written by [Taki Sadik](../../about.html) · Last updated 2026-10-22 · Status: Building · 26 min read

A small-scale UAS airspace manager on my bench: ESP32 tracker beacons plus ArduPilot SITL simulated drones, dynamic geofences, predicted-conflict alerts, and a human-in-the-loop override for every resolution.

## Overview

When a dozen uncrewed aircraft share the same block of sky, somebody, or something, has to
        keep them apart. The Canadian Army is studying exactly this problem: how to
        manage airspace shared by many uncrewed aircraft at once, a discipline known as airspace
        deconfliction. With the Defence Drone Initiative (launched July 23, 2026)
        promising fleets of cheap tactical drones, and DRDC trials like Operation NANOOK pushing more
        uncrewed systems into the same training areas, deconfliction stops being an airline problem
        and becomes a platoon-level one.

This build explores that problem safely and cheaply. It is mostly simulation:
        several ArduPilot SITL drone instances fly missions on my homelab and stream MAVLink telemetry
        into a manager I wrote. A handful of physical ESP32 tracker beacons stand in for live tracks,
        so there is real RF hardware in the loop. On top of that track picture sit the two things a
        deconfliction system actually does: predict conflicts before separation is lost,
        and enforce dynamic geofences the operator can draw, move, and resize live.

The design rule that shapes everything: the manager is advisory, never autonomous.
        It proposes resolutions, climb, hold, reroute, and a human approves every single one. That is
        deliberate: it mirrors how military airspace control actually works, and it makes the system
        safe to experiment with at any scale.

## Proof of Build

What each part of the photo does:

- Three ESP32 tracker beacons: stand in for drones in the air. Each one reports a position, like a real aircraft tracker would.

- Breadboarded controller with OLED: shows the manager's status at a glance: how many tracks it sees and whether any conflict is active.

- Signed test-case sheets: each scenario has an expected result written down first, then signed off when the run matches it.

- Laptop with ArduPilot SITL: simulates several drones and draws the 3D geofence volumes. The red alert is a live conflict between two tracks.

## Bill of Materials

| Item | What I used | Est. US$ |
| --- | --- | --- |
| Beacons | 3 cheap ESP32 boards (tracker beacons) | 6-12 each |
| Simulation | ArduPilot SITL (free), several drone instances | 0 |
| Compute | Existing laptop / homelab node | 0 |
| Display/UI | Web dashboard on the homelab | 0 |

This is deliberately the cheapest build in the program: the point is that deconfliction is a
        software and doctrine problem, not a hardware procurement. The ESP32s were already in the
        Phase 3 parts bin; everything else is free software and machines I already own.

## Wiring & Connections

There is very little copper in this build, most of the "wiring" is UDP sockets, but the
        few physical and logical links all have to be right or the track picture goes stale silently:

| From | To | Cable or interface | Notes |
| --- | --- | --- | --- |
| ESP32 beacons (x3) | Bench Wi-Fi access point | 2.4 GHz Wi-Fi (WPA2), UDP to manager :5005 | Position packets at 5 Hz; static DHCP lease per beacon MAC so IDs survive reboots |
| Beacon controller ESP32 | SSD1306 OLED display | 4-wire I2C: GPIO21 (SDA), GPIO22 (SCL), 3.3 V, GND | Display at address 0x3C; shows beacon health and active alert count |
| ESP32 boards | Laptop | USB-C cable | Flashing and serial monitor at 115200 baud; removed in normal operation |
| ArduPilot SITL instances | Manager ingest | Loopback UDP 14550-14552 | MAVLink telemetry; GLOBAL_POSITION_INT requested at 10 Hz per instance |
| Manager | SITL instances | Loopback UDP (same MAVLink sockets) | Approved resolution commands only, nothing flows without a human click |
| Manager | MQTT broker (homelab) | TCP 1883 | cop/air/* topics, QoS 1; integration feed for the common operating picture |
| Operator browser | Dashboard backend | HTTP :8080 + WebSocket on the LAN | Leaflet map UI; 2 Hz state push, no full-history resend |

## Architecture

Traffic Sources

ArduPilot SITLthree drone instances

ESP32 tracker beaconsstand-in live tracks

Track ingestMAVLink + UDPpymavlink

Track storeposition history

Conflict enginetrajectory predictiontime-to-closest-approach

Geofence service3D keep-in / keep-out

Alert queueadvisory only

Operator dashboardmap + volumes + queue

Human operatorapproves every resolution

Resolution commandsMAVLink to SITL

Common operatingpicture feed

Figure 1: simulated and physical tracks flow into one track store; the conflict engine and geofence service raise alerts; a human approves every resolution before any command goes back to an aircraft.

## How Conflict Prediction Works

The conflict engine answers one question for every pair of live tracks: when will
        these two aircraft be closest to each other, and how close will that be? The
        pipeline runs in four stages, all of them on the constant-velocity model from step 05:

yes

no

Track A(position + velocity)

Track B(position + velocity)

Relative positionand velocity vectors

Closest-point time(d of dist-squared = 0)

Miss distance(horizontal + vertical)

Inside lookaheadand separation bubble?

Hysteresis(3 consecutive violations)

Advisory alert queue

Stays quiet

Figure 2: the four-stage prediction pipeline: relative motion, time of closest approach, miss distance in horizontal and vertical components, then a stability gate before anything reaches the operator.

Two details make this work in practice rather than just in geometry. First, the vertical
        check is independent: two tracks can miss by metres horizontally and still be a non-event
        if they are 80 m apart vertically, so the separation bubble is a cylinder (horizontal
        radius plus vertical band), not a sphere. Second, the alert must fire with margin:
        the design target is an advisory in the queue at least 30 seconds before the predicted
        separation loss, giving the human time to read it, decide, and click.

Figure 3: the alert margin as a design target, not a measured result: the engine must raise the advisory at least 30 s before the predicted separation loss, so the human has time to act. Measured margins will be published after the Run 1-2 series.

## How I Built It

**Q: Build steps (10 steps with code; expand to read)**

A: The first requirement is a busy sky. I run three ArduPilot SITL instances on a homelab node, each with its own instance offset (-I, which shifts the base ports by 10 per instance) and its own MAVLink system ID (--sysid), and each streaming telemetry out to a dedicated UDP port where the manager listens. Every instance flies an autonomous waypoint mission loaded through MAVProxy, so the virtual field has real crossing traffic, not three drones hovering politely apart.

## Testing & Metrics

Testing is scenario-driven, built around the scripted harness from step 09. Every numbered
        run below follows the same discipline: identical initial conditions, a fresh SITL state, a
        signed result sheet per repetition, and a pass only when the alert precedes the separation
        loss with margin.

### Run 1, Crossing paths

Setup: two SITL drones on perpendicular waypoint courses at the same
        altitude, timed to reach the intersection within seconds of each other.
        Procedure: start both missions simultaneously, let the conflict engine run,
        then approve the proposed altitude resolution for one drone.
        Metric: time-to-alert (scenario start to alert in queue) and alert margin
        (alert time to predicted separation loss); post-resolution, the recomputed TCPA must sit
        outside the bubble.

### Run 2, Altitude convergence

Setup: two drones on parallel tracks, one climbing through the other's
        altitude at a fixed vertical rate.
        Procedure: no operator input until the alert fires; then approve a hold for
        the climbing drone.
        Metric: whether the vertical miss distance is computed correctly (this run
        exists because horizontal-only checks pass here while separation is actually being lost),
        and time-to-alert margin as in Run 1.

### Run 3, Geofence breach and live edit

Setup: one drone on a straight course through where a keep-out cylinder will
        appear.
        Procedure: create the volume live from the dashboard while the drone is
        inbound, then move and resize it mid-run.
        Metric: violation alert latency from the crossing telemetry packet, and
        enforcement latency from each live edit, target is the next track update.

### Run 4, Quiet-sky false-alarm soak

Setup: three SITL drones on well-separated missions plus all three beacons
        running their stand-in tracks, no designed conflict.
        Procedure: soak for two hours with normal waypoint traffic and beacon jitter.
        Metric: false-alarm count, target is zero; every spurious alert gets
        root-caused before the soak counts.

### Run 5, Degraded track (beacon drop-out mid-conflict)

Setup: a beacon on a converging course with a SITL drone.
        Procedure: kill the beacon's power after the conflict engine has begun
        tracking the pair, then restore it.
        Metric: the track must flag STALE inside the timeout, the conflict must
        downgrade gracefully rather than freeze on the last position, and the track must rejoin
        cleanly on beacon return.

### Targets and Current Status

| Metric | Target | Current status |
| --- | --- | --- |
| Time-to-alert margin (Runs 1-2) | Alert at least 30 s before predicted separation loss | In progress, harness runs, sheets being filled |
| False alerts (Run 4) | Zero over a 2-hour quiet soak | In progress |
| Resolution clearance | Predicted CPA outside the bubble after every approved manoeuvre | In progress |
| Geofence edit-to-enforcement (Run 3) | Next track update (1 s or less) | In progress |
| Stale-track detection (Run 5) | Flag within 2 s of the last beacon packet | In progress |

No results are published yet: the scenario harness runs and the result sheets are being
        filled in, but numbers go up only when every scripted case has been run repeatedly and the
        sheets are consistent.

## Troubleshooting & Lessons

- Second SITL instance never connected: I forgot the -I instance offset, so both instances fought over the same ports and the second one's telemetry silently went nowhere. Fix: unique -I and --sysid per instance, and a heartbeat check in the ingest path that screams instead of waiting forever.

- Beacons dropped packets in bursts: the ESP32's default modem sleep batches radio traffic, which made stand-in tracks jump and nearly triggered false conflicts. Fix: WiFi.setSleep(false) in the beacon firmware, confirmed with a packet-gap histogram.

- Alerts flapped at the bubble boundary: a single-sample threshold raised and cleared the same conflict several times a second as telemetry jittered. Fix: require three consecutive violating predictions to raise, and a clear margin to release, classic hysteresis.

- Predictions were useless at default telemetry rates: SITL streams position slowly unless asked, and 1 Hz updates made TCPA estimates jump around. Fix: request GLOBAL_POSITION_INT at 10 Hz with MAV_CMD_SET_MESSAGE_INTERVAL on connect.

- "Repeatable" scenarios were not repeatable: SITL kept leftover waypoints and parameters between runs, so run 2 never matched run 1. Fix: the harness restarts instances and wipes state (sim_vehicle.py -w) before every run.

## Legal & Safety Notes

## Status & Roadmap

- Done: multi-instance ArduPilot SITL environment with MAVLink ingest via pymavlink; common track model covering simulated and beacon tracks; ESP32 beacon firmware broadcasting stand-in positions; dynamic 3D geofence service with live edit and violation alerts; operator dashboard with alert queue and approve/reject flow.

- In progress: conflict-engine tuning (separation bubble, lookahead horizon, alert flapping); scripted test-case harness with signed result sheets; resolution manoeuvre set (altitude change, hold, reroute) end-to-end back into SITL.

- Next: publish scenario metrics once runs are repeatable; publish tracks and alerts into the common operating picture; add a third scripted scenario family (beacon drop-out mid-conflict) to test degraded-track behaviour.

## Related Builds

- Canadian Defence Hardware Program, the program hub; this manager is one of the sky builds.

- Multi-Domain Common Operating Picture, where this manager's tracks and alerts ultimately flow.

- Thermal Search-and-Rescue Drone, the real aircraft this manager would one day share airspace with; also SITL-first pending Transport Canada compliance.

- Operation LENTUS-Style Drone Mapping, the simulation-side drone workflow that reuses the same ArduPilot SITL environment.

## Build Narrative: Phase by Phase

Phase 1: simulation environment. Several ArduPilot SITL drone instances fly missions on the homelab and stream MAVLink telemetry. Each instance gets a unique -I offset and sysid, after an early session where two instances fought over the same ports and the second one's telemetry silently went nowhere; the ingest path now runs a heartbeat check that screams instead of waiting forever.

Phase 2: telemetry ingest. pymavlink ingests the SITL streams into the manager. Default SITL telemetry rates made TCPA estimates jump, so the manager requests GLOBAL_POSITION_INT at 10 Hz with MAV_CMD_SET_MESSAGE_INTERVAL on connect.

Phase 3: physical stand-ins. Three cheap ESP32 tracker beacons broadcast stand-in positions so there is real RF hardware in the loop. The ESP32's default modem sleep batched radio traffic and made tracks jump toward false conflicts; WiFi.setSleep(false) in the firmware fixed it, confirmed with a packet-gap histogram.

Phase 4: conflict engine. Predicted conflicts come from time-to-closest-point-of-approach against a separation bubble and a lookahead horizon. A single-sample threshold flapped alerts several times a second on telemetry jitter, so raising now requires three consecutive violating predictions and release needs a clear margin, classic hysteresis.

Phase 5: geofences and resolutions. A dynamic 3D geofence service supports operator-drawn, moved, and resized volumes with live violation alerts. Resolution manoeuvres (climb, hold, reroute) run end to end back into SITL. The manager is advisory only: it proposes, a human approves every resolution, mirroring how military airspace control actually works.

Phase 6: test harness. A scripted test-case harness restarts instances and wipes state (sim_vehicle.py -w) before every run, because leftover waypoints and parameters made run 2 never match run 1. Result sheets are signed so repeats are comparable.

## What You Need

The cheapest build in the program on purpose: deconfliction is a software and doctrine problem, not a hardware procurement. The only real cost is compute you already own.

| Category | Item | Notes |
| --- | --- | --- |
| Hardware | 3 ESP32 tracker beacons | Cheap boards as live RF stand-ins; disable modem sleep in the firmware |
| Hardware | Compute | Existing laptop or homelab node for the SITL instances and the manager |
| Software | ArduPilot SITL | Free; several drone instances with unique -I offsets and sysids |
| Software | pymavlink, Python | MAVLink ingest at 10 Hz, the common track model, the conflict engine |
| Software | Web dashboard | Operator view with the alert queue and the approve/reject flow |
| Skills | Python, MAVLink basics, software testing | Scenario design, hysteresis tuning, disciplined repeatable test harnesses |
| Accounts | None | No accounts or licenses required |

## Challenges and Lessons Learned

- The second SITL instance never connected. I forgot the -I instance offset, so both instances fought over the same ports. Lesson: unique -I and sysid per instance, and a heartbeat check in the ingest path that screams instead of waiting forever.

- Beacons dropped packets in bursts. ESP32 modem sleep batched radio traffic and stand-in tracks jumped, nearly triggering false conflicts. Lesson: WiFi.setSleep(false) in beacon firmware, confirmed with a packet-gap histogram.

- Alerts flapped at the bubble boundary. A single-sample threshold raised and cleared the same conflict several times a second. Lesson: three consecutive violations to raise, a clear margin to release, classic hysteresis.

- Predictions were useless at default telemetry rates. 1 Hz position updates made TCPA estimates jump. Lesson: request 10 Hz GLOBAL_POSITION_INT on connect with MAV_CMD_SET_MESSAGE_INTERVAL.

- Repeatable scenarios were not repeatable. SITL kept leftover waypoints and parameters between runs. Lesson: the harness restarts instances and wipes state before every run.

## What Is Next

- Publish scenario metrics once runs are fully repeatable: detection lead time, false-alert rate, resolution success.

- Publish tracks and alerts into the multi-domain common operating picture.

- Add a third scripted scenario family: beacon drop-out mid-conflict, testing how the engine behaves when a track degrades during an active alert.

- Tune the lookahead horizon against the scenario data rather than by feel.

- Longer term, feed real outdoor flight tracks (from the thermal SAR drone) into the manager as live data alongside the beacons.

## Frequently Asked Questions

**Q: How do I fix 'Second SITL instance never connected'?**

A: I forgot the -I instance offset, so both instances fought over the same ports and the second one's telemetry silently went nowhere. Fix: unique -I and --sysid per instance, and a heartbeat check in the ingest path that screams instead of waiting forever.

**Q: How do I fix 'Beacons dropped packets in bursts'?**

A: the ESP32's default modem sleep batches radio traffic, which made stand-in tracks jump and nearly triggered false conflicts. Fix: WiFi.setSleep(false) in the beacon firmware, confirmed with a packet-gap histogram.

**Q: How do I fix 'Alerts flapped at the bubble boundary'?**

A: a single-sample threshold raised and cleared the same conflict several times a second as telemetry jittered. Fix: require three consecutive violating predictions to raise, and a clear margin to release, classic hysteresis.

**Q: How do I fix 'Predictions were useless at default telemetry rates'?**

A: SITL streams position slowly unless asked, and 1 Hz updates made TCPA estimates jump around. Fix: request GLOBAL_POSITION_INT at 10 Hz with MAV_CMD_SET_MESSAGE_INTERVAL on connect.

**Q: How do I fix '"Repeatable" scenarios were not repeatable'?**

A: SITL kept leftover waypoints and parameters between runs, so run 2 never matched run 1. Fix: the harness restarts instances and wipes state (sim_vehicle.py -w) before every run.

## Cite This Page

**Q: Citation formats**

A: Plain text
