# Thermal Search-and-Rescue Drone

Written by [Taki Sadik](../../about.html) · Last updated 2026-10-22 · Status: Building, first results published · 26 min read

X500-class quadcopter with a FLIR Lepton thermal camera and a Hailo AI HAT+ running person detection at the edge, pushing georeferenced detections to a live map, the Army MINERVA Arctic ISR requirement at hobby scale.

## Overview

The Army's MINERVA challenges say it plainly: Canada currently lacks a drone that can do
        ISR in Arctic conditions. The Arctic requirement calls specifically for
        sovereignty operations and search and rescue with the Canadian Rangers.
        Detecting a person in snow or brush from a cheap thermal camera is the sharpest hobby-scale
        version of that requirement, and it is what this build does.

The airframe is an X500-class quadcopter with a Pixhawk-class flight
        controller. A Raspberry Pi 5 companion computer carries the payload brain: a
        FLIR Lepton 3.5 thermal camera for sensing and a Hailo AI HAT+
        running person detection at the edge, so the drone finds people on board rather than
        streaming raw video back to a ground station. Every detection is fused with the drone's
        telemetry into a lat/lon point and published to a live situational-awareness map.

The design rule throughout: the drone cues, a human confirms. Nothing beyond
        detection and notification is automated. In a real SAR sweep with the Rangers, the drone is
        the wide-area sensor and the person on the ground makes every call.

## Proof of Build

What each part of the photo does:

- X500-class quadcopter: the airframe, with a Pixhawk-class flight controller and GPS.

- Gimbal camera: keeps the camera steady and pointed at the ground while the drone moves.

- Pi 5 companion computer: runs person detection on the video on board, so the drone does not depend on a radio link to spot people.

- Laptop: shows the thermal live feed with detected people highlighted, and the search map with the planned flight path.

## Bill of Materials

Everything below is purchased and on my bench.

| Item | What I used | Est. US$ |
| --- | --- | --- |
| Airframe | Holybro X500-class kit with Pixhawk-class controller and GPS | 500-800 |
| Radio | ELRS transmitter (RadioMaster class) + receiver | 80-150 |
| Batteries/charger | 4 LiPo packs, balance charger, LiPo bag | 200-300 |
| Companion computer | Pi 5 4 GB | ~85 |
| Thermal camera | FLIR Lepton 3.5 module or USB thermal camera (256x192 class) | 200-300 |
| AI accelerator | Hailo AI HAT+ for the Pi 5 | 70-110 |
| Spares | Props, prop guards, connectors, landing pad | 60-100 |

## Sensor & Accelerator Specs

These are the numbers the whole payload design hinges on, taken from the FLIR Lepton
        engineering datasheet and the Hailo AI HAT+ product specification, not from bench
        anecdotes. The 8.7 Hz frame rate in particular is a hard ceiling that shapes everything
        downstream: at survey speed the drone moves measurably between frames, which is why
        step 08 timestamps frames at capture rather than on arrival.

## From Thermal Pixel to Map Marker

Step 08 does the math; here is the geometry it encodes. With the camera held near-nadir
        and the altitude known from the flight controller, each detection's bounding-box centre
        projects along a ray to the ground. The model is deliberately simple, a pinhole camera
        with a small-angle correction for the gimbal pitch, because cueing a ground team does
        not need survey-grade photogrammetry.

Figure 2: illustration of the simplified near-nadir projection model: pixel offset from frame centre becomes a look angle theta, altitude h turns it into a ground offset, and the local tangent plane turns the offset into lat/lon. Not a measured geometry.

### Where the error really comes from

The biggest contributor is not the camera, it is time. At a 10 m/s survey speed, a
          one-second lag between frame capture and the telemetry used to project it shifts the
          marker by 10 m. The second is attitude: a few degrees of gimbal pitch error at 120 m
          altitude moves the ground point by several metres. The pixel math itself is deterministic,
          but the projection model is approximate; the timestamps and the attitude dominate the
          error budget, and the model adds its own. That is why the pipeline timestamps
          frames at capture, matches telemetry by time rather than arrival order, and why T3
          measures against a surveyed marker instead of trusting the model on paper.

## Architecture

MAVLink / UART

FLIR Lepton 3.5thermal camera

Pi 5capture + preprocessing

Hailo AI HAT+person detection (HailoRT)

Pixhawk-class FCArduPilot

Pi 5 companionfusion + georeferencing

mavlink-routertelemetry split

Ground stationmission planner

MQTT broker

Leaflet live mapdetections + confidence

Human operatorconfirms every detection

Figure 1: thermal frames are acquired and preprocessed on the Pi 5, inference runs on the Hailo HAT+, detections fuse with flight telemetry on the Pi, and land on a live map where a human confirms each detection.

## Wiring & Connections

The whole payload chain fits on the X500's top and bottom plates. The two rules that
        saved me the most pain: common ground everywhere (the FC, the Pi, and the
        receiver must share a ground or serial links misbehave in ways that look like software
        bugs), and the Pi gets its own regulator, never power it from the flight
        controller's USB port.

| From | To | Cable / interface | Notes |
| --- | --- | --- | --- |
| Pixhawk TELEM2 | Pi 5 GPIO UART (GPIO14/15) | JST-GH 6-pin to Dupont | Cross TX to RX; common GND; 921600 baud, MAVLink 2 |
| ELRS receiver | Pixhawk RC input UART | JST servo-style | CRSF protocol; receiver antennas at 90 degrees to each other |
| GPS/compass module | Pixhawk GPS1 + I2C1 | JST-GH 6-pin and 4-pin | Mast-mounted, away from the power distribution board |
| 4S LiPo | Power distribution board | XT60 | First power-up through a smoke stopper, always |
| 5 V / 5 A BEC | Pi 5 USB-C power input | Buck converter, USB-C pigtail | Separate regulator; the Pi 5 browns out under 5 V with the HAT+ loaded |
| PureThermal 3 board (Lepton 3.5) | Pi 5 USB-A | USB 2.0 | Streams raw 16-bit (Y16) frames over UVC |
| Hailo AI HAT+ | Pi 5 40-pin header + PCIe FFC | M.2 HAT ribbon | Hailo-8L over PCIe; gen 3 negotiated in config.txt |
| Camera gimbal (pitch) | Pixhawk AUX out | PWM servo lead | Driven by ArduPilot mount parameters; nadir for search profile |

## How I Built It

**Q: Build steps (10 steps with code; expand to read)**

A: Before any flight hardware was powered, I stood up ArduPilot SITL and Gazebo (both
              free) on the homelab cluster and developed the mission logic there: lawn-mower search
              patterns, geofences, and failsafes for link loss, low battery, and geofence breach.
              This builds directly on the simulation environment from my
              LENTUS-style drone mapping work. The payoff is
              that every behaviour that could cost me an airframe got exercised in Gazebo first,
              with Mission Planner connected as the ground station, exactly as it will be flown for real.

## Testing & Metrics

The test protocol mirrors how a real SAR sensor would be evaluated, scaled down to what a
        bench and a backyard allow. Each run has a defined setup, procedure, and metric; nothing
        counts as measured until it is logged from an actual run. Flight-derived numbers are
        pending, the airframe is still inside the compliance gate, so results to date come from
        SITL and bench/ground payload runs.

### Test Runs

- T1, Bench thermal capture. Setup: Lepton on the Pi, known hot and cold
          references (mug of water at measured temperature, ice pack). Procedure: capture raw
          16-bit frames at each reference, record pixel means. Metric: capture rate in frames per
          second and monotonic response of pixel mean to reference temperature.

- T2, Detection performance, ground runs. Setup: a person standing,
          kneeling, and lying in snow and in brush, with the payload walked or tripod-mounted at
          increasing slant ranges. Procedure: run the Hailo pipeline on recorded and live frames,
          log every detection with confidence. Metric: recall per range band and false alarms per
          hour of empty-background footage. Target: high recall at short ranges with a false-alarm
          rate low enough that the human confirmer is not flooded.

- T3, Georeferencing error. Setup: a ground marker surveyed with the
          u-blox GNSS from my rover kit as a reference track (meter-class GNSS, not survey grade). Procedure: ground runs at several altitudes and
          off-nadir angles (payload elevated, not yet flown), compare reported lat/lon against
          the marker reference. Metric: horizontal error in metres, binned by altitude and angle. Target: error
          small enough to walk a ground team to the marker.

- T4, End-to-end latency. Setup: full live pipeline, camera, Hailo,
          fusion, MQTT broker, map, on the bench network. Procedure: introduce a warm target on a
          known timestamp and time its appearance as a map marker. Metric: frame-to-marker latency
          in seconds. Target: seconds, not minutes.

- T5, Failsafe behaviour. Setup: SITL first, then the real airframe with
          props off, then controlled flight after the compliance gate. Procedure: trigger link
          loss, low battery, and geofence breach in turn. Metric: correct mode transition (RTL or
          land) in every case, with the transition logged.

- T6, Mission endurance. Setup: fully loaded aircraft (payload, Pi, Hailo
          running) after the compliance gate. Procedure: fly the search pattern on one pack until
          the low-battery failsafe. Metric: usable minutes per pack; the cold-weather derating for
          these packs comes from my cold-soak
          characterization rig dataset rather than being invented here.

### Targets and Current Status

| Metric | Target | Current status |
| --- | --- | --- |
| Thermal capture rate (T1) | Sustained sensor-native frame rate with no dropped frames in 10-minute runs | In progress, capture path proven on the bench, long runs ongoing |
| Detection recall, short range (T2) | High recall on standing/kneeling/lying targets in snow and brush | In progress, model fine-tuning and ground-run data collection underway |
| False-alarm rate (T2) | Low enough that every alarm gets a human look without fatigue | In progress, empty-background soak tests running |
| Georeferencing error (T3) | Marker accuracy a ground team can walk to | In progress, ground-run setup built, measurements not yet published |
| Frame-to-marker latency (T4) | Seconds on the live pipeline | In progress, pipeline integrated, timing harness next |
| Failsafe correctness (T5) | Correct RTL/land in 100% of triggered scenarios | SITL scenarios exercised; real-airframe triggers pending |
| Endurance per pack (T6) | Search-pattern flight time with reserve margin, warm and cold | Not yet flown, blocked on the compliance gate; cold derating comes from the cold-soak dataset |

Measured figures will be published here once outdoor testing is lawful and complete. Until
        then, every number above is a target, not a result.

## Troubleshooting & Lessons

- Garbled or zero MAVLink on the Pi. Symptom: mavlink-router connects but
          heartbeats never parse. Causes found: the Pi's serial console still owned
          /dev/serial0, and TX/RX were not crossed on the JST-GH-to-Dupont adapter.
          Fix: disable the serial console in raspi-config, keep
          enable_uart=1, cross the lines, and share ground between FC and Pi. Lesson:
          with serial, verify the physical layer with a loopback test before touching software.

- Hailo AI HAT+ invisible to the OS. Symptom:
          hailortcli fw-control identify finds nothing. Cause: the Pi 5 ships with the
          external PCIe lane off, and a loosely seated FFC ribbon looks identical to a dead board.
          Fix: dtparam=pciex1 and dtparam=pciex1_gen=3 in
          config.txt, reseat the ribbon, then re-check enumeration.

- Thermal frames freeze for a beat, mid-run. Symptom: the Lepton stream
          stalls for a fraction of a second at intervals. Cause: the sensor's flat-field correction
          (FFC) shutter events, normal Lepton behaviour, not a bug. Fix: schedule FFC during
          non-critical moments (on the ground, or between search legs) and have the pipeline tag
          frames around FFC as degraded rather than feeding them to the detector.

- Radio failsafe triggers during a range walk. Symptom: RTL declared at a
          shorter distance than expected with the transmitter live. Cause: receiver antennas
          parallel to each other and shadowed by the frame. Fix: mount the two ELRS antennas at 90
          degrees, clear of carbon and the battery, then re-run the range check with props off.
          Lesson: a failsafe that fires early in testing is doing its job, fix the RF, not the
          threshold.

- Detections vanish when the field Wi-Fi drops. Symptom: markers stop
          appearing on the map and never catch up after reconnect. Cause: fire-and-forget MQTT
          publishes with no local buffer. Fix: QoS 1 plus an on-disk spool on the Pi that
          republishes in order on reconnect, the store-and-forward discipline from my DDIL work,
          applied at drone scale.

## Legal & Safety Notes (Canada)

## Status & Roadmap

- Done: all components purchased and on the bench; ArduPilot SITL + Gazebo environment running on the homelab cluster with search patterns, geofences, and failsafes exercised; airframe assembled with motor order/direction and radio failsafe bench-verified; Pi 5 talking MAVLink over UART through mavlink-router; raw 16-bit Lepton capture bench-verified in Python (transport verified; radiometric calibration still open).

- In progress: thermal person model fine-tuning and Hailo compilation; ground-run detection and georeferencing test runs (T2/T3); Leaflet map consuming MQTT detections; end-to-end latency harness.

- Next: Transport Canada registration and pilot certificate; NAV CANADA airspace check for the test area; first outdoor flight; measured detection and georeferencing results published here; feed detections into the multi-domain common operating picture.

## Related Builds

- Canadian Defence Hardware Program, the hub page: how this build fits the Defence Drone Initiative, MINERVA challenges, and the rest of the bench.

- LENTUS-Style Drone Mapping, the ArduPilot SITL + Gazebo simulation basis this drone's mission logic is built on.

- Cold-Soak Characterization Rig, the battery dataset that derates this drone's packs for Arctic operations.

- Passive Acoustic Drone Detector, the receive-only sibling: detecting other drones instead of people.

- Multi-Domain Common Operating Picture, where this drone's signed detections end up once the fusion layer is live.

## Build Narrative: Phase by Phase

Phase 1: airframe. An X500-class quadcopter with a Pixhawk-class flight controller. Motor order and direction and the radio failsafe were bench-verified before anything flew. A range walk later showed the ELRS failsafe declaring RTL earlier than expected, traced to receiver antennas mounted parallel and shadowed by the frame, fixed by mounting them at 90 degrees clear of carbon and the battery.

Phase 2: simulation first. ArduPilot SITL with Gazebo runs on the homelab cluster: search patterns, geofences, and failsafes are all exercised in simulation before outdoor flight. Nothing about the mission logic meets the real sky untested.

Phase 3: companion computer link. The Pi 5 talks MAVLink to the flight controller over UART through mavlink-router. Bringup fought the Pi's serial console owning /dev/serial0 and uncrossed TX/RX on the JST-GH-to-Dupont adapter; the fix sequence was disable the console in raspi-config, keep enable_uart=1, cross the lines, share ground. Serial gets a loopback test before software now.

Phase 4: thermal capture. The FLIR Lepton 3.5 (160x120 microbolometer, 8.7 Hz, 14-bit sensor output carried as raw 16-bit frames) streams frames captured in Python. The values are radiometric only with the sensor's radiometric mode and calibration metadata applied; the raw-capture path is bench-verified, calibration is still open. Its flat-field-correction shutter events stall the stream for a fraction of a second at intervals, which is normal Lepton behaviour: FFC is scheduled for non-critical moments and frames around FFC are tagged degraded rather than fed to the detector.

Phase 5: edge AI. The Hailo AI HAT+ runs person detection on board so the drone finds people without streaming raw video to a ground station. Bringup needed dtparam=pciex1 and pciex1_gen=3 in config.txt (the Pi 5 ships with the external PCIe lane off) plus a reseated FFC ribbon, confirmed with hailortcli fw-control identify.

Phase 6: georeferencing and map. Every detection fuses with the drone's telemetry into a lat/lon point and publishes to a Leaflet situational-awareness map over MQTT. An early fire-and-forget design lost detections whenever field Wi-Fi dropped; the fix was QoS 1 plus an on-disk spool that republishes in order on reconnect, the store-and-forward discipline from the DDIL work applied at drone scale.

## What You Need

The build assumes you already fly or are learning to fly responsibly. The regulatory items are not optional extras: they gate the outdoor flight tests.

| Category | Item | Notes |
| --- | --- | --- |
| Hardware | X500-class airframe + Pixhawk-class FC | Quadcopter kit with GPS; bench-verify motor order/direction and radio failsafe before flight |
| Hardware | ELRS radio system | RadioMaster-class transmitter and receiver; mount receiver antennas at 90 degrees, clear of carbon |
| Hardware | LiPo packs, balance charger, LiPo bag | Four packs for rotation through test days; charge and store safely |
| Hardware | Pi 5 4 GB + Hailo AI HAT+ | Companion computer and the edge accelerator; enable the Pi 5 PCIe lane in config.txt |
| Hardware | FLIR Lepton 3.5 thermal module | 160x120 LWIR microbolometer, 8.7 Hz, 14-bit sensor output in raw 16-bit frames (radiometric calibration still open); schedule FFC shutter events around detection windows |
| Software | ArduPilot, SITL + Gazebo | Flight stack and the simulation environment where missions are proven first |
| Software | mavlink-router, HailoRT, Python | Companion link, accelerator runtime, capture and georeferencing pipeline |
| Skills | Drone assembly, serial debugging, basic ML workflow | Soldering, UART bringup, model fine-tuning and compilation for an edge accelerator |
| Accounts | Transport Canada registration + pilot certificate | Required before outdoor flight, plus a NAV CANADA airspace check for the test area |

## Challenges and Lessons Learned

- Garbled or zero MAVLink on the Pi. The serial console owned /dev/serial0 and TX/RX were uncrossed on the adapter. Lesson: with serial, verify the physical layer with a loopback test before touching software.

- The Hailo AI HAT+ was invisible to the OS. The Pi 5 ships with the external PCIe lane off, and a loosely seated ribbon looks identical to a dead board. Lesson: dtparam=pciex1 and gen=3 first, reseat the ribbon second, then check enumeration.

- Thermal frames froze for a beat, mid-run. Lepton flat-field-correction shutter events, normal sensor behaviour, not a bug. Lesson: schedule FFC for non-critical moments and tag frames around it as degraded.

- Radio failsafe triggered during a range walk. Receiver antennas were parallel and shadowed by the frame. Lesson: a failsafe that fires early in testing is doing its job, fix the RF (90-degree antenna placement), not the threshold.

- Detections vanished when field Wi-Fi dropped. Fire-and-forget MQTT with no local buffer. Lesson: QoS 1 plus an on-disk spool that republishes in order on reconnect.

## What Is Next

- Transport Canada registration and the pilot certificate, then the NAV CANADA airspace check for the test area.

- First outdoor flight with the full payload chain live: thermal capture, Hailo person detection, georeferencing, map.

- Publish measured detection and georeferencing results: ranges, altitudes, false alarms, and how far the lat/lon points land from the truth.

- Feed detections into the multi-domain common operating picture as the air-domain node.

- Cold-weather flight validation, informed by the battery cold-soak dataset from the rig in this same program.

## Cite This Page

**Q: Citation formats**

A: Plain text
