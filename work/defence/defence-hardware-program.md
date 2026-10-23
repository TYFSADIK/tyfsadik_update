# Canadian Defence Hardware Program

Eleven hands-on hardware builds across sky, water, and ground, each one mapped to a stated Canadian Armed Forces requirement, with full bills of materials, prices, step-by-step build guides, and bench photos of the real rigs.

## Why This Program Exists

In 2026 Canada started saying, in public documents, exactly what it wants built. I read those
        documents as free requirements specs and started building against them in my own lab:

- Defence Drone Initiative (DDI), launched July 23, 2026. First priority areas: low-cost tactical ISR drones, and ground robots for resupply, casualty evacuation, and terrain too hazardous for personnel.

- Army MINERVA challenges, the Army states it has bought foreign robotic systems of mixed quality, with problems in cold-weather operation and components from unstable supply chains, and that it currently lacks a drone that can do ISR in Arctic conditions. The Arctic drone call closed September 24, 2026; the full text reads like an evaluator's checklist.

- DRDC field trials, GPS-denied navigation, convoying, cold-weather performance, and resilient operation, exercised on events like Operation NANOOK.

- NRC + DRDC counter-drone work, a detection system that picks up the signature of a drone's rotating propellers without emitting any radio signal that could reveal its own location.

- Airspace deconfliction, the Army is studying how to manage airspace shared by many uncrewed aircraft at once.

These calls are aimed at companies, not students, so I treat them as requirements documents,
        not application forms. Every build below answers one of them at hobby scale, with real
        hardware, honestly reported measurements, and published datasets or dashboards landing as each build matures, see each page's status section for what is done, in progress, or still a target.

### Requirement Source 1: Defence Drone Initiative (DDI)

The DDI, launched July 23, 2026, names its first priority areas plainly: low-cost tactical ISR
        drones, and ground robots for resupply, casualty evacuation, and terrain too hazardous for
        personnel. Read as a spec, that is three requirements: cheap enough to be attritable, useful
        sensors on board, and autonomy that keeps working when the operator link does not. The
        [thermal SAR drone](thermal-sar-drone.html) answers the ISR line, an X500-class
        airframe with edge detection so the platform is useful even with a degraded downlink. The
        [GPS-denied rover](gps-denied-navigation-rover.html) and
        [convoy robots](convoy-robots-degraded-mesh.html) answer the ground-robot line,
        with the emphasis on continuing the mission through link loss rather than stopping and
        waiting. The DDI also talks about supply-chain integrity for uncrewed systems, which is the
        requirement the [secure fleet updates](secure-fleet-updates.html) build takes on
        directly: secure boot, TPM, signed OTA images, and automatic rollback.

### Requirement Source 2: Army MINERVA Challenges

The MINERVA challenge text is unusually candid: the Army says it has bought foreign robotic
        systems of mixed quality, with problems in cold-weather operation and components from
        unstable supply chains, and that it currently lacks a drone able to do ISR in Arctic
        conditions. The Arctic drone call closed September 24, 2026, and the full text reads like an
        evaluator's checklist, endurance in the cold, sensors that work in snow and low light,
        operation alongside Canadian Rangers. Two of my builds map straight onto it: the
        [cold-soak characterization rig](cold-soak-battery-rig.html) attacks the stated
        cold-weather pain point head-on by publishing runtime, voltage sag, and failure-mode data
        against temperature, and the [thermal SAR drone](thermal-sar-drone.html) matches
        the Arctic-sovereignty and SAR-with-Rangers requirement with a thermal camera and on-board
        person detection. The supply-chain complaint is covered by the secure-updates build above.

### Requirement Source 3: DRDC Field Trials and Operation NANOOK

DRDC's field-trial pattern, exercised on events like Operation NANOOK, keeps returning to
        the same four themes: GPS-denied navigation, convoying, cold-weather performance, and
        resilient operation when communications are degraded. These are trial scenarios, so my
        builds mirror them as test protocols rather than as products: the
        [GPS-denied rover](gps-denied-navigation-rover.html) cuts GNSS deliberately and
        measures EKF drift against a recorded reference track; the
        [convoy robots](convoy-robots-degraded-mesh.html) hold formation through induced
        link drops on a LoRa/Wi-Fi mesh; and the [cold-soak
        rig](cold-soak-battery-rig.html) reproduces the cold-weather axis in a freezer and in a real Canadian winter. The
        point is not to replicate NANOOK, it is to have bench-scale evidence on the same variables
        the trials measure.

### Requirement Source 4: NRC + DRDC Counter-Drone Work

The NRC/DRDC counter-drone direction asks for a detection system that picks up the signature
        of a drone's rotating propellers without emitting any radio signal that could reveal its
        own location. That constraint, receive-only, is the interesting part, and it shapes
        two builds. The [passive acoustic drone detector](acoustic-drone-detector.html)
        listens for rotor harmonics with a MEMS microphone array, rejects birds and aircraft, and
        estimates direction of arrival by beamforming. Its RF sibling, the
        [passive radar node](sky-passive-radar-node.html), detects aircraft by listening
        to reflections of someone else's broadcast transmitters, again emitting nothing. Both feed
        detections into the common operating picture, because a single passive sensor is a hint and
        two agreeing sensors are a track.

### Requirement Source 5: Airspace Deconfliction

The Army is studying how to manage airspace shared by many uncrewed aircraft at once, the
        problem that appears the moment cheap drones stop being rare. The
        [mini airspace deconfliction manager](airspace-deconfliction-manager.html)
        builds this at simulation scale: ESP32 beacons plus ArduPilot SITL simulated drones, dynamic
        geofences, conflict alerts, and a human-in-the-loop override. It also doubles as the traffic
        layer for the [multi-domain common
        operating picture](multi-domain-common-operating-picture.html), since a fused air picture is exactly what a deconfliction cell would
        need to look at.

## What Canada Is Building (and Where I Fit)

Sky: the Arctic Over-the-Horizon Radar (based on Australia's JORN design,
        adapted for RCAF/NORAD, initial capability due December 2029) will give long-range
        early-warning coverage of the northern approaches, feeding a layered picture of conventional
        radar, intelligence, airborne, and space-based sensors. Its companion program, Crossbow, is
        a classified Canada-US non-radar sensor network, you can't copy it and shouldn't try.

Water: Canada's Arctic sensor direction aims for persistent
        surveillance from seabed to space. DRDC's Northern Watch demonstration ran into problems
        with installation, ice, technical issues, and data management. In DRDC-linked work at
        Dalhousie, uncrewed vehicles act as sensor hosts that dock at seabed nodes to recharge and
        download data.

The pattern in both: the hard parts are data management, fusion, and keeping sensors
        alive in harsh conditions, which is exactly where my DevOps and infrastructure
        background is an advantage. My builds target that layer: cheap nodes that survive the cold,
        buffer through dead links, sign their data, and fuse into one picture.

## The Builds

Each build has its own page with the full step-by-step guide, parts list, and bench photos.

### Flagship Sensor Nodes

- Sky: Passive Aerial Early-Warning Node, KrakenSDR five-channel coherent receiver listening to FM/TV broadcast reflections off aircraft; the radar front end is receive-only and emits nothing of its own. RTL-SDR ADS-B receiver as a reference feed, pyAPRiL for clutter filtering and DoA, with ADS-B scoring of detection runs underway.

- Water: Passive Acoustic Vessel Monitor, hydrophone + Pi 5 at a dock, spectrogram classifier for boat type and direction in training, RTL-SDR AIS receiver as a reference feed, solar powered, IP67 housing.

- Ground: Seismic & Acoustic Perimeter Mesh, solar LoRa mesh nodes with ADXL355 accelerometers (geophone upgrade path), edge classification of vehicles vs footsteps vs wind, with a rover or drone as a human-tasked verify asset.

### Robots & Drones

- GPS-Denied Navigation Rover, ROS 2 rover fusing IMU, wheel odometry, and LiDAR with an Extended Kalman Filter; GNSS gets cut and drift is measured against the u-blox reference track.

- Convoy-Following Robots on a Degraded Mesh, two rovers follow a lead over LoRa/Wi-Fi mesh, hold formation through link drops, and recover, the DDIL problem at bench scale.

- Thermal Search-and-Rescue Drone, X500-class airframe with a FLIR Lepton thermal camera and Hailo AI HAT+ edge detection of people in snow and brush, pushed to a live map. Matches the Army's stated Arctic sovereignty and SAR-with-Rangers requirement.

- Passive Acoustic Drone Detector, MEMS microphone array on a Pi detecting rotor harmonics, rejecting birds and aircraft, estimating direction of arrival by beamforming. The microphone front end emits nothing of its own; echoes the NRC/DRDC direction at hobby scale.

- Mini Airspace Deconfliction Manager, ESP32 beacons plus ArduPilot SITL simulated drones, dynamic geofences, conflict alerts, and human-in-the-loop override.

### Cold & Trust

- Cold-Soak Characterization Rig, heated, instrumented battery bay tested in a freezer and real Canadian winter; publishes runtime, voltage sag, and failure data against temperature, a clean dataset on a stated Army pain point.

- Secure Robot-Fleet Updates, secure boot, TPM 2.0, signed over-the-air updates, automatic rollback, tested in a cold chamber. Supply-chain integrity from the DDI, applied to my own fleet.

### The Piece That Ties It Together

- Multi-Domain Common Operating Picture, every node publishes signed detections over MQTT/Zenoh; a central Kalman-filter tracker fuses air, water, and ground tracks; nodes buffer through dead links and sync on reconnect; a human makes every decision. Chaos-tested by cutting links and killing nodes.

## Program Architecture

Figure 1: every node is receive-only or self-contained, signs its output, and feeds one fused picture with a human deciding.

## Build Roadmap

Figure 2: seven phases in build order; the COP fusion layer grows alongside them and gets chaos-tested once the nodes are feeding it.

The order is the strategy. Phase 0 puts up the bench so every later build inherits it.
        Phase 1 starts with the ADS-B receiver because it is the cheapest ground-truth instrument
        in the whole program: a real-time aircraft map on screen from week one, and a log that
        accumulates weeks before the passive-radar chain needs anything scored against it. The
        simulation spine goes up during the shipping wait, so rover and drone logic gets exercised
        where crashes are free. Cold-weather work (Phase 6) starts in the freezer early because a
        Canadian winter is a use-it-or-lose-it field trial window. The COP is the last piece to
        stand up in full, but every node publishes signed detections from the day it is built, so
        fusion is integration, not a rewrite.

## Bill of Materials by Phase

Everything below is already purchased and on my bench. Total program cost lands around
        US$5,250-7,950, plus 13% HST, shipping, and possible duties on US orders.
        Canadian sources (PiShop.ca, RobotShop, Digi-Key Canada, Mouser Canada, Amazon.ca) avoid
        some cross-border fees; KrakenRF sells through Crowd Supply and Mouser.

### Phase 0, Workshop & Shared Infrastructure (~US$650-1,050)

| Item | What I bought | Est. US$ |
| --- | --- | --- |
| Soldering | Pinecil / Hakko-class station, solder, flux, wick | 60-110 |
| Multimeter | Auto-ranging, with continuity and current | 30-60 |
| Hand tools | Strippers, flush cutters, precision drivers, hex set, heat shrink, heat gun | 60-100 |
| Prototyping | Breadboards, jumpers, XT60/JST connectors, resistor/cap kit, crimp tool | 50-80 |
| Bench supply (optional) | Adjustable 30 V / 5 A | 50-70 |
| Safety | LiPo bag, ABC fire extinguisher, safety glasses | 40-60 |
| Network | 8-port gigabit switch, Ethernet cables, OpenWrt-capable router | 80-120 |
| Storage | 256 GB NVMe + Pi 5 M.2 HAT, 5 high-endurance microSD cards | 100-140 |
| Power | 4 official 27 W Pi 5 supplies, 2 USB-C PD power banks | 80-110 |
| Enclosures | IP65 boxes, cable glands, mounting hardware | 60-90 |
| Time sync | 2 u-blox M9N-class GNSS modules with PPS (clock-disciplining nodes) | 60-100 |

Phase notes: Phase 0 arrived first, by design, every later phase sits on this
        bench. Two choices deserve explanation. I paid for the official 27 W Pi 5 supplies instead of
        cheaper third-party USB-C bricks because undervoltage on a Pi 5 causes crashes and can
        corrupt the filesystem on writes, and I added the NVMe HAT for the same reason: continuous sensor
        logging wears out microSD cards. The two GNSS/PPS modules were bought as a pair on purpose,
        one disciplines the sensor-node clocks, the other becomes the rover reference track before being
        switched off for drift tests. The alternative to a dedicated bench supply was powering
        everything from USB-C, which works until you need a clean, current-limited 12 V rail for the
        hydrophone rig or the rover motors. This phase is consumed by literally every build page:
        it is the shared infrastructure the other ten stand on.

### Phase 1, Sky Node: Passive Radar + ADS-B Truth (~US$1,100-1,350)

| Item | What I bought | Est. US$ |
| --- | --- | --- |
| KrakenSDR | 5-channel coherent receiver | 499 |
| Antennas | KrakenRF 5-antenna set for testing | 199 |
| Directional antennas | 2 Yagi / log-periodic for FM and UHF TV reference/surveillance | 80-160 |
| Compute | Mini PC (Intel N100 or i5, 16 GB, 4+ cores) running Ubuntu | 150-250 |
| ADS-B truth | RTL-SDR Blog V4, 1090 MHz antenna, coax | 50-80 |
| RF accessories | SMA adapters, low-loss coax, optional FM/UHF filter or LNA | 60-100 |
| NanoVNA (optional) | Antenna tuning | 50-70 |

Started with just the ADS-B kit (~US$100): live aircraft map and dashboard first, then the KrakenSDR.

Phase notes: the KrakenSDR was the anchor purchase, it is the only
        sub-US$500 receiver with five phase-coherent channels sharing one clock, and the realistic
        alternative (five independent RTL-SDRs with an external clock distribution board and
        per-channel calibration) costs nearly as much and takes months of frustration. The KrakenRF
        antenna set is for bench bring-up; the Yagi and log-periodic are what actually do the radar
        geometry, because the reference channel needs gain pointed at the transmitter. The RTL-SDR
        Blog V4 for ADS-B truth arrived first and was logging aircraft weeks before the KrakenSDR
        shipped, that ordering was deliberate, since a passive radar without independent ground
        truth is just a screensaver. This phase is consumed by the
        [sky passive radar node](sky-passive-radar-node.html) build page, and its
        detections feed the [multi-domain common
        operating picture](multi-domain-common-operating-picture.html).

### Phase 2, Water Node: Hydrophone + AIS (~US$700-1,000)

| Item | What I bought | Est. US$ |
| --- | --- | --- |
| Hydrophone | Aquarian A5 (3.5 mm) or H2d-XLR (3 m) | 230-320 |
| Audio interface | USB interface with 48 V phantom power (required for XLR version) | 120-180 |
| Compute | Pi 5 4 GB, active cooler, case | ~105 |
| AIS receiver | RTL-SDR Blog V4 + VHF marine antenna (162 MHz) | 60-90 |
| Housing | IP67 box, cable glands, hydrophone weight assembly | 40-70 |
| Power | 12 V battery, 30-50 W solar panel, MPPT controller, DC-DC buck | 150-250 |

Phase notes: the one real fork in this phase is the hydrophone connector.
        The Aquarian A5 with a 3.5 mm jack is plug-and-play into a USB audio interface; the H2d-XLR
        version has better low-frequency response but demands 48 V phantom power, which is why the
        audio interface line exists at all, a bare Pi has no mic input worth using. The solar power
        chain was sized for the worst case (a dock with no outlet), not the average case; the MPPT
        controller rather than a cheap PWM one, because Canadian winter sun is a scarce resource and
        PWM throws away a chunk of it. The RTL-SDR V4 for AIS is the same part as the ADS-B truth
        receiver from Phase 1, which keeps spares interchangeable. The Pi 5 and RTL-SDR arrived
        first; the hydrophone and solar gear came later. This phase is consumed by the
        [water passive acoustic vessel
        monitor](water-passive-acoustic-vessel-monitor.html) build page.

### Phase 3, Ground Mesh & Deconfliction Beacons (~US$500-750)

| Item | What I bought | Est. US$ |
| --- | --- | --- |
| Node boards | 5 ESP32 LoRa boards, 915 MHz (Heltec V3 / LilyGO T-Beam class) | 20-40 each |
| Sensors | 4 ADXL355-class accelerometer breakouts | 15-40 each |
| Upgrade (optional) | 3 SM-24 geophones + precision ADC | 100-180 |
| Node power | 18650 cells, protected holders, small solar panel, charge board, weatherproof box | 25-40 each |
| Gateway | LoRa HAT / gateway board for a Pi | 40-80 |
| Beacons | 3 cheap ESP32 boards for airspace-deconfliction simulation | 6-12 each |

Phase notes: the 915 MHz boards are non-negotiable, that is the North
        American ISM band, and the 868 MHz variants that dominate European tutorials are the wrong
        hardware for Canada. Between Heltec V3 and LilyGO T-Beam I went with whichever was in stock
        in Canada at the time; the firmware targets the common SX1262 radio either way. The ADXL355
        breakouts are the honest starting sensor: cheap, low-noise for a MEMS part, and good enough
        to prove the edge-classification pipeline before spending on real geophones, the SM-24s are
        the upgrade path, not the starting point, because a precision ADC front end doubles the cost
        of each node. The three bare ESP32 beacons are deliberately the cheapest boards in the whole
        program; they only need to blink a position report for the deconfliction simulation. The
        node boards arrived first, sensors a week later. This phase is consumed by the
        [ground seismic perimeter mesh](ground-seismic-perimeter-mesh.html) and the
        [mini airspace deconfliction manager](airspace-deconfliction-manager.html).

### Phase 4, Rovers: GPS-Denied Navigation & Convoy (~US$800-1,300)

| Item | What I bought | Est. US$ |
| --- | --- | --- |
| Chassis | 2 metal 4WD chassis with wheel encoders | 80-150 each |
| Compute | Pi 5 8 GB per rover, active cooler | ~145 each |
| Motor driver | Dual driver (BTS7960 or similar) | 20-60 |
| LiDAR | 2D LiDAR (LD19 / RPLIDAR A1 class), one rover first | 70-150 |
| IMU | BNO085 breakout | 25-40 |
| Camera | Pi Camera Module 3 | 25-50 |
| Power | Li-ion pack with BMS, DC-DC 5 V/5 A, physical e-stop switch | 60-100 |

Software is ROS 2 on Ubuntu 24.04 (free). The Phase 0 GNSS module provides the reference track, then gets switched off to measure drift.

Phase notes: the chassis choice was driven by one requirement, encoders on
        every wheel, because wheel odometry is an input to the EKF, not an accessory. Two identical
        chassis were bought so the convoy build has a matched pair; running a convoy of two different
        platforms turns every tuning problem into a two-variable problem. The BNO085 was chosen over
        cheaper MPU-class IMUs because it runs its own sensor fusion on-chip and outputs quaternions
        directly, which removes a whole calibration rabbit hole from the rover pipeline. The LiDAR
        was bought for one rover first, deliberately, so the EKF could be tuned with and without it
        before duplicating the cost. The 8 GB Pi 5s were picked over 4 GB because SLAM and
        visualization on the robot eat RAM, and the physical e-stop switch is in the BOM because a
        software stop is not a stop. This phase is consumed by the
        [GPS-denied navigation rover](gps-denied-navigation-rover.html) and the
        [convoy robots on a degraded mesh](convoy-robots-degraded-mesh.html).

### Phase 5, Drone: Thermal SAR + Acoustic Detector (~US$1,300-1,950)

| Item | What I bought | Est. US$ |
| --- | --- | --- |
| Airframe | Holybro X500-class kit with Pixhawk-class controller and GPS | 500-800 |
| Radio | ELRS transmitter (RadioMaster class) + receiver | 80-150 |
| Batteries/charger | 4 LiPo packs, balance charger, LiPo bag | 200-300 |
| Companion computer | Pi 5 4 GB | ~85 |
| Thermal camera | FLIR Lepton 3.5 module or USB thermal camera (256x192 class) | 200-300 |
| AI accelerator | Hailo AI HAT+ for the Pi 5 | 70-110 |
| Acoustic array | ReSpeaker-class 4-mic USB array | 70-100 |
| Spares | Props, prop guards, connectors, landing pad | 60-100 |

First weeks happen in simulation, ArduPilot SITL and Gazebo, both free, before flight hardware leaves the bench.

Phase notes: the X500-class kit was chosen because it is the airframe the
        ArduPilot documentation and the Gazebo simulation models are built around, matching the
        sim to the real frame means the SITL tuning transfers instead of starting over. The FLIR
        Lepton 3.5 is the expensive-but-right option for thermal; the USB thermal camera alternative
        (256x192 class) is listed because it gets the detection pipeline running at a third of the
        price while the Lepton waits in the budget. The Hailo AI HAT+ exists in this BOM because
        running person-detection inference on the Pi's CPU alone does not leave headroom for anything
        else on a flying platform. Four LiPo packs is the minimum for a useful field day, one in the
        air, one on the charger, one cooling, one spare. The ELRS radio arrived first (it also works
        with the simulator for stick time), the airframe second, and the thermal camera last. This
        phase is consumed by the [thermal SAR drone](thermal-sar-drone.html) and the
        [passive acoustic drone detector](acoustic-drone-detector.html), the ReSpeaker
        array lives in this phase because it shares the drone's bench time, though the detector
        itself is a ground node.

### Phase 6, Cold-Soak Testing & Secure Updates (~US$200-550)

| Item | What I bought | Est. US$ |
| --- | --- | --- |
| Sensors | 6 DS18B20 or thermocouple amps, 2 INA228 power monitors | 40-70 |
| Battery heater | Kapton heater pads, MOSFET, foam insulation | 20-40 |
| Cold chamber | A Canadian winter (free), or a cheap chest freezer | 0-300 |
| TPM | TPM 2.0 add-on board for the Pi | 25-40 |
| Signing keys | 2 YubiKeys (one backup) | 100-110 |

Phase notes: this is the cheapest phase and the one that makes the rest of
        the program credible. The DS18B20 sensors were picked for boring reasons, one-wire bus,
        waterproof probe variants, Linux kernel support without any driver work, and the INA228
        monitors give bus voltage and current over I2C so the voltage-sag curves need no analog
        front end. The cold chamber line is honest: a chest freezer is the controlled environment,
        and January in Toronto is the field trial. The two YubiKeys are not a luxury, a signing
        key with no backup is a single point of failure that bricks your own fleet, so one lives
        on the bench and one lives in a drawer off-site. The TPM board was the last item to arrive
        and the only one that needed a cross-border order. This phase is consumed by the
        [cold-soak characterization rig](cold-soak-battery-rig.html) and the
        [secure robot-fleet updates](secure-fleet-updates.html) build pages.

## Workshop Setup and Safety

A program with this many parallel builds lives or dies on bench discipline, so the workshop
        got set up like a small lab rather than a desk with a soldering iron on it. The bench is
        split into three zones: a solder zone (iron, fume extraction, task light,
        heat-resistant mat), an RF zone (SDRs, antennas, and coax kept physically
        away from the soldering iron and the bench supply, because stray noise and ESD both kill RF
        front ends), and a clean assembly zone where drones and rovers get worked
        on without solder splatter or metal filings. The floor beside the bench is the robot test
        area, rovers never get powered with wheels on the bench.

ESD: the assembly zone has a grounded ESD mat and a wrist strap, and they
        get used every time a bare board is handled, the ADXL355 breakouts, the Hailo HAT+, and the
        KrakenSDR's RF inputs are all the kind of parts that die silently and fail mysteriously a
        week later. The strap gets a continuity check with the multimeter before the first session
        of the day, not just the first session ever.

LiPo charging station: the drone batteries have their own rules, written
        on an index card taped above the charger:

- Charge only on a concrete or tile surface, inside a LiPo bag, with nothing flammable within a metre.

- Never charge unattended, if I leave the room, the charger stops.

- Never charge a cold or frozen pack; after a cold-soak or winter field run, the pack warms to room temperature first.

- Balance charge, always; storage-charge to ~3.8 V per cell for anything sitting more than a few days.

- Any pack that is puffed, dented, or crashed is retired to the discharge bucket, not back to the shelf.

Fume extraction: a small solder fume extractor with a carbon filter sits
        behind the iron, and rosin-core work also gets the window cracked, the filter slows the
        exposure, it does not eliminate it. Fire: an ABC dry-chemical extinguisher
        hangs within arm's reach of the bench (not across the room), and the LiPo bag lives beside
        the charger, not in a drawer. A LiPo fire is a lithium-ion thermal-runaway fire, not a
        lithium-metal fire: water cools the cells and stops the runaway spreading, while the ABC
        extinguisher is for anything else burning around it. The plan is bag, distance, water on
        the pack if it is safe to do so, extinguisher for surrounding combustibles, and the door
        if it is not.

Checkout procedure: every new board meets the multimeter before it meets
        power, continuity between the power rails to rule out a dead short, then a first power-up
        from the bench supply with the current limit set low, so a mistake costs a current-limited
        brown-out instead of a dead board. The bench supply's voltage display gets verified against
        the multimeter before I trust it for the day. That routine is written down as a checklist,
        because the day you skip it is the day you need it:

BENCH POWER-ON CHECKLIST

# Bench power-on checklist - run at the start of every work session
# 1. Bench supply OFF, voltage knob at minimum, current limit at minimum
# 2. Verify supply display against multimeter (set 5.00 V, compare readings)
# 3. ESD strap: continuity check strap -> mat -> ground point (about 1 Mohm expected,
#    that is the strap's built-in safety resistor; near-zero or open means the strap failed)
# 4. New board: meter in continuity mode, check VCC-GND rails for shorts
#    - any beep on power rails = stop, find the short before powering
# 5. First power-up: set current limit to ~100 mA for a bare board,
#    ~500 mA for a Pi, never straight to full current
# 6. Power on, watch the current draw for 10 seconds before touching anything
#    - near-zero draw or pegged-at-limit both mean: power off, investigate
# 7. LiPo check: charger on concrete, LiPo bag open and ready,
#    extinguisher pin checked, nothing flammable within 1 m
# 8. Log the session start in the lab notebook (date, boards on bench, goal)

None of this is glamorous, and that is the point: the checklist exists so the boring safety
        steps happen on the exciting days too, the day the KrakenSDR arrives, the day the drone
        first arms.

## Procurement Notes for Canada

The headline total of US$5,250-7,950 is only the start of the real number.
        Buying this program in Canada adds three layers on top: 13% HST in Ontario
        on essentially everything, shipping that is rarely free at this basket size
        for heavy items like chassis and batteries, and duties and brokerage on
        anything that crosses the border. The duty itself is often zero under the electronics
        tariff headings, the sting is the courier brokerage fee, a flat charge for "clearing" your
        own parcel that can add a meaningful percentage to a small US order. The practical rule:
        one consolidated cross-border order beats five small ones, and Canadian stock beats US
        stock even at a slightly higher sticker price.

What was bought where:

- PiShop.ca, all four Pi 5 boards, the official 27 W power supplies, active coolers, the M.2 HAT, and Pi Camera Module 3. Canadian Pi stock with no border risk; this was the single largest domestic order.

- RobotShop (Quebec), the two 4WD rover chassis with encoders, the BTS7960 motor driver, and misc brackets. Domestic robotics stock, reasonable shipping to Ontario, and no brokerage surprises.

- Digi-Key Canada, the ADXL355 breakouts' companion parts, INA228 modules, DS18B20 probes, connectors, and the resistor/cap kits. Digi-Key's Canadian site prices in CAD with duties handled at checkout, which makes the landed cost predictable.

- Mouser Canada, the TPM 2.0 board and some RF connectors that nobody else had in stock domestically.

- Amazon.ca, the unglamorous bulk: IP65/IP67 enclosures, cable glands, heat shrink, the ESD mat, the LiPo bags, the ABC extinguisher, and the heat gun. Not the cheapest per item, but fast and returnable when a box arrives the wrong size.

- KrakenRF, the KrakenSDR and its five-antenna set sell through Crowd Supply and Mouser; this was the one unavoidable cross-border order, and it went through Mouser's Canadian checkout so the landed cost was known up front instead of being a roulette wheel at the door.

- Direct, the two YubiKeys came from Yubico's store; security keys are not something to buy from a marketplace reseller.

Two Canada-specific traps worth recording. First, radio band plans: LoRa
        gear listed on marketplaces is often the 868 MHz European variant, and Canadian listings are
        not always labelled clearly, every board in Phase 3 was checked for 915 MHz before checkout.
        Second, winter shipping and batteries: LiPo and Li-ion packs have carrier
        restrictions, and a pack that sits in a frozen depot over a weekend arrives cold-soaked,
        which, per the safety rules, means it warms to room temperature before its first charge,
        not straight onto the charger.

## Canada-Specific Notes

## Status: Did / Doing / Next

- Did: bought and benched the full workshop (Phase 0) and the Phase 1-6 hardware; ADS-B receiver live with a real-time aircraft map; ROS 2 + Gazebo + ArduPilot SITL simulation environment running on the homelab cluster; first cold-soak freezer runs logged.

- Doing: KrakenSDR passive-radar processing chain (range-Doppler plots scored against ADS-B); rover EKF tuning with GNSS-cut drift tests; hydrophone + AIS capture rig; ESP32 LoRa mesh firmware; thermal detection pipeline on the Hailo HAT+.

- Next: publish the cold-soak dataset (runtime, voltage sag, failure mode vs temperature); multi-node passive-radar fusion; signed OTA rollout across the rover fleet with cold-chamber rollback tests; the multi-domain common operating picture tying every node together with chaos tests.

### Designed vs Built vs Measured by Phase

Designed means the build protocol is written down, built means the hardware is benched and running, measured means a dataset or dashboard result is published.

| Phase | Designed | Built | Measured |
| --- | --- | --- | --- |
| Phase 0: Workshop and shared infrastructure | Yes | Yes (benched) | Not applicable |
| Phase 1: Sky node (passive radar + ADS-B truth) | Yes | ADS-B receiver live with real-time aircraft map; KrakenSDR processing chain in progress | ADS-B map operational; no radar scoring published yet |
| Phase 2: Water node (hydrophone + AIS) | Yes | In progress (capture rig) | No measurements published yet |
| Phase 3: Ground mesh and deconfliction beacons | Yes | In progress (ESP32 LoRa mesh firmware) | No measurements published yet |
| Phase 4: Rovers (GPS-denied navigation + convoy) | Yes | In progress (ROS 2 + Gazebo + ArduPilot SITL environment running; EKF tuning) | No published drift figures yet |
| Phase 5: Drone (thermal SAR + acoustic detector) | Yes | In progress (thermal detection pipeline on Hailo HAT+) | No measurements published yet |
| Phase 6: Cold-soak rig + secure fleet updates | Yes | Rig built; first freezer runs logged; secure updates in progress | Initial runs logged; dataset not yet published |
| Multi-domain COP | Yes | In progress (dashboard live on homelab cluster, seismic mesh feeding it) | Chaos-test metrics pending |

**Q: Build Log (Narrative)**

A: The Did/Doing/Next list is the snapshot; this is the trail. Weeks are approximate, some
        ran long, some overlapped, but the order is real, and the order was the strategy.

## Related Software Projects

This hardware program builds on my software-side defence work:

- Arctic Domain Awareness Digital Twin, the same fusion problem over open satellite/AIS/ADS-B data.

- DDIL-Proof DevOps, the store-and-forward patterns the field nodes reuse.

- Counter-Drone Sensor Fusion Simulator, the simulation sibling of the acoustic detector and passive radar.

- Zero-Trust Air-Gapped Supply Chain, the signing and provenance discipline behind the fleet OTA system.

- Decision Black Box, the tamper-evident audit log the common operating picture writes to.

- Operation LENTUS-Style Drone Mapping, the simulation basis for the thermal SAR drone's mapping workflow.

## How I Built It

The first two weeks went entirely into Phase 0 infrastructure: bench zones laid out, ESD mat grounded, network switch and OpenWrt router configured, the Pi 5s imaged onto NVMe instead of microSD, and the power-on checklist written down and actually followed. Every later build inherited that bench.

The ADS-B kit went live weeks before the KrakenSDR shipped, logging aircraft so the passive-radar chain had something to score against from day one. The same pattern repeats everywhere: the AIS receiver arrives with the hydrophone, and the u-blox module gives the rover its reference track before GNSS gets cut for drift tests.

ROS 2, Gazebo, and ArduPilot SITL went up while hardware was in transit, so rover and drone logic got exercised where crashes cost a restarted container instead of a broken airframe. The MQTT/Zenoh bus design was sketched in this window too, because every later node had to publish into it.

Each node publishes signed detections into the bus from the day it is built. The common operating picture is integration later, not a rewrite, because the message contract was fixed before the first sensor was soldered.

The cold-soak rig was assembled early and the first freezer runs logged before the deep cold arrived, because a Canadian winter is a use-it-or-lose-it field trial window. A real cold snap doubled as the field trial.

Five workstreams now advance in parallel (radar processing, rover EKF tuning, hydrophone capture, LoRa mesh firmware, thermal pipeline), each documented on its own build page as it matures. The rule that keeps the program honest: nothing is called done until there is a dataset or a dashboard to point at.

## What You Need

| Category | Item | Notes |
| --- | --- | --- |
| Workshop | Soldering station, multimeter, hand tools, ESD mat and strap, bench supply, LiPo bags, ABC extinguisher | The power-on checklist runs at the start of every session; the full safety routine is in the Workshop section above |
| Shared infrastructure | Four Pi 5 boards, official 27 W supplies, NVMe storage, network switch, OpenWrt router, two u-blox GNSS/PPS modules for time sync | Phase 0, roughly US$650-1,050; every later phase sits on this bench |
| Simulation | ArduPilot SITL, Gazebo, ROS 2 on Ubuntu 24.04 | Free; carries the early software work for rovers and drones |
| Per-build hardware | KrakenSDR, hydrophone, ESP32 LoRa nodes, rover chassis and LiDAR, X500 airframe, FLIR Lepton, Hailo HAT+, TPM board, YubiKeys | Full BOMs per phase on this page; program total around US$5,250-7,950 plus 13% HST, shipping, and possible duties |
| Skills | Soldering, Linux, Python, embedded basics for ESP32, ROS 2, RF fundamentals for the radar and SDR builds | Each build page lists its own specifics; the program rewards breadth |
| Sourcing (Canada) | PiShop.ca, RobotShop, Digi-Key Canada, Mouser Canada, Amazon.ca | Check every LoRa board for 915 MHz (North America); 868 MHz parts are for Europe. Consolidate cross-border orders to avoid repeated brokerage fees |

## Challenges and Lessons Learned

- Bench discipline beats gear. The checkout routine (continuity on power rails, current-limited first power-up, supply display verified against the multimeter) exists so the boring safety steps happen on the exciting days too: the day the KrakenSDR arrives, the day the drone first arms.

- Ground truth is the difference between a sensor and a screensaver. Passive radar without independent ADS-B truth is just moving plots. Putting the cheapest ground-truth instrument live first was the highest-leverage decision in the program.

- Export control needs care. The KrakenSDR team once pulled its passive-radar code over export-control concerns, so radar code gets checked against Canada's export control rules before publishing, or the write-up, data, and metrics go up instead of the code. Handling that carefully is itself a good signal.

- Radio rules are not optional. Passive builds stay receive-only; jamming is illegal in Canada. The acoustic nodes are tuned to narrow-band machinery signatures, not speech, and run only on land I control.

- Cold changes everything. Batteries ship cold in winter, packs never charge frozen, and the cold-soak dataset exists because the Army's MINERVA text names cold-weather operation as a stated pain point. The freezer is the controlled environment; January in Toronto is the field trial.

## What Is Next

- Publish the cold-soak dataset: runtime, voltage sag, and failure mode against temperature.

- Multi-node passive-radar fusion scored against ADS-B.

- Signed OTA rollout across the rover fleet with cold-chamber rollback tests.

- The multi-domain common operating picture tying every node together, chaos-tested by cutting links and killing nodes.

- Each build page graduates from protocol to measured results as its dataset or dashboard lands.
