# Convoy-Following Robots on a Degraded Mesh

Written by [Taki Sadik](../../about.html) · Last updated 2026-10-22 · Status: Building · 31 min read

Two rovers convoy behind a lead vehicle over a 915 MHz LoRa broadcast link with a Wi-Fi fallback, hold formation through induced link drops, and recover on reconnect, the Army resupply-convoy and DDIL communications problem, reproduced on my bench.

## Overview

This build is a two-rover convoy that keeps behaving when the radio link gets bad.
        A lead rover drives a course while broadcasting its position, heading, and speed over a 915 MHz
        LoRa link (with Wi-Fi as a fallback path); the follower runs a gap-following controller that
        holds a set distance and offset behind it. Then I degrade the link on purpose and measure what
        the convoy does: how formation error grows with packet loss, how the follower behaves when the
        link drops entirely, and how fast it rejoins when the link comes back.

A note on the word "mesh" in the title: the demonstrated link is a point-to-point LoRa
        broadcast between the two rovers plus the Wi-Fi fallback, not multi-hop mesh routing.
        The title keeps the word because this build is the bench rehearsal for the degraded-mesh
        regime the seismic perimeter nodes already run in; true mesh routing on the convoy link
        is future work, and this page does not claim it is done.

Why this specific problem: the Defence Drone Initiative (launched July 23, 2026)
        names ground robots for resupply, casualty evacuation, and terrain too hazardous for personnel
        as a first-priority area, and DRDC tests convoying and resilient operation on exercises
        like Operation NANOOK. A resupply convoy that falls apart the moment the radio link
        degrades is useless, in the North, on a damaged road, or under deliberate interference, the
        link will degrade. The interesting engineering is not the following; it is the
        denied, degraded, intermittent, and limited (DDIL) behaviour: what the machine
        does in the gap between "link fine" and "link dead," and how gracefully it recovers.

Everything here is already bought and on my bench. The chassis, compute, and drive electronics
        are shared with my [GPS-denied navigation rover](gps-denied-navigation-rover.html),
        and the LoRa boards come from the same Phase 3 mesh stock as the seismic perimeter nodes, so
        this build reuses proven hardware and adds the convoy link, the follow controller, and a
        disciplined degraded-link test protocol.

## Proof of Build

What each part of the photo does:

- Rover R1, the lead: drives the route and broadcasts its position and commands over the mesh.

- Rover R2, the follower: follows R1 using those messages, and has to behave safely when they stop arriving.

- 915 MHz LoRa whip antennas: the radio link between the rovers. I deliberately degrade it during tests to see what breaks.

- Mesh-node schematic: where I worked out the packet format on paper.

- Laptop topology view: shows every link and its status live while I induce packet loss.

## Bill of Materials

All of this is purchased and on hand. The chassis, compute, motor driver, and power train are
        shared with the GPS-denied rover build, so the marginal cost of this project was mostly the
        LoRa boards and the follower's payload.

| Item | What I used | Est. US$ |
| --- | --- | --- |
| Chassis | 2 metal 4WD chassis with wheel encoders (shared with the GPS-denied rover build) | 80-150 each |
| Compute | Pi 5 8 GB per rover, active cooler | ~145 each |
| Radios | ESP32 LoRa boards, 915 MHz (from the Phase 3 mesh stock) | 20-40 each |
| Motor driver | Dual driver (BTS7960 or similar) | 20-60 |
| Payload | Dummy payload (weighted box standing in for resupply cargo) | ~0-20 |
| Power | Li-ion pack with BMS, DC-DC 5 V/5 A, physical e-stop switch | 60-100 |

## Architecture

Follower Rover R2

Lead Rover R1

pose/heading/speedfixed-rate packets

same packetsfallback path

telemetry

Pose source(wheel odometry + IMU)

ESP32 LoRa TX915 MHz

Wi-Fi fallback

ESP32 LoRa RX

Wi-Fi RX(tc netem impairment)

Link watchdogtimeout + hold

Pure-pursuit-stylegap-following controller

E-stop /safe-stop

BTS7960 driver+ wheel encoders

Laptop loggerloss vs control quality

Figure 1: the lead broadcasts its pose at a fixed rate over LoRa (with an impaired Wi-Fi fallback); the follower's watchdog arbitrates the link, and the controller drives through the e-stop interlock at all times.

Both paths carry the same packet format, so the follower does not care which radio delivered
        the update, the watchdog simply tracks the age of the newest good packet from either path.
        That is the DDIL lesson in miniature: degrade gracefully across heterogeneous links instead of
        betting the convoy on one of them.

## Watchdog States: the Heart of the Build

The watchdog is the only part of the follower that decides what happens to the motors, so
        it is worth seeing as a state machine. The controller from step 05 never sees a raw packet:
        it only ever receives goal points the watchdog has approved for the current state. The
        four states, with the thresholds straight from the firmware:

link degrades

link recovers

grace expires

fresh packet arrives

gap within tolerance

FOLLOW(packet age under 1.0 s)

HOLD(age 1.0 to 4.0 s)

SAFE_STOP(age over 4.0 s)

REJOIN(first fresh packet)

Figure 2: the watchdog as a state machine. FOLLOW tracks the newest packet; HOLD tracks an extrapolated vector while ramping speed down; SAFE_STOP ramps to a controlled stop and waits; REJOIN closes the gap from where the follower actually is, at half speed, instead of snapping to the lead.

### Why the grace window is a safety parameter

During HOLD the follower is driving on a prediction: where the lead should be,
          extrapolated from the last good packet. Every second of grace is a second of driving on
          a guess. The first version of this firmware used a 10 s grace window, and during a
          blackout test the follower tracked a stale vector into the lead's braking zone. The
          window is short now (4.0 s), and HOLD always decelerates, so the worst a guess can do
          is leave the follower standing still a little early. Tune this number like it controls
          a vehicle, because it does.

## Anatomy of a Blackout Run

The T4 blackout test is the run this build exists to survive. Here is what the design
        says should happen when the link drops completely mid-lap: packet age climbs from its
        steady 0.2 s (5 Hz broadcasts) past the 1.0 s fresh threshold into HOLD, past the 4.0 s
        grace threshold into a controlled SAFE_STOP, and on link restore the follower rejoins
        from its actual position. This diagram shows the design intent, using the watchdog
        thresholds from the code above; measured runs will replace it once the T4 series is logged.

Figure 3: design-intent timeline of a T4 blackout run: steady 5 Hz traffic, link loss, packet age climbing through the 1.0 s and 4.0 s thresholds, a controlled stop, then a limited-speed rejoin. Drawn from the watchdog constants in step 06, not from logged run data.

## Wiring & Connections

Both rovers are wired identically, which keeps spares and debugging simple, any harness I
        make fits either machine. The one asymmetry is the radio role (lead broadcasts, follower
        listens), and that is firmware, not wiring.

| From | To | Cable / interface | Notes |
| --- | --- | --- | --- |
| Li-ion pack | BMS input | XT60, 16 AWG | BMS handles over-current and low-voltage cutoff before anything else sees power |
| BMS output | E-stop switch, then BTS7960 B+/B- | 16 AWG silicone wire | The latching e-stop sits in series with the motor supply, pressing it kills drive power regardless of software state |
| BMS output | DC-DC buck (5 V / 5 A) to Pi 5 USB-C | 18 AWG, short leads | Logic power is separate from motor power so a stalled motor cannot brown out the Pi |
| Pi 5 GPIO (PWM pins) | BTS7960 RPWM / LPWM | Dupont jumpers | Common ground between Pi and driver is mandatory; a floating ground shows up as random motor twitch |
| Pi 5 GPIO | BTS7960 R_EN / L_EN | Dupont jumpers, pull-downs | Enable lines held low until ROS bringup finishes, so the rover cannot lurch at boot |
| Wheel encoders (A/B) | Pi 5 GPIO with pull-ups | 3-wire per encoder | A swapped A/B pair reads as rotation while driving straight, caught in the taped-square check (step 01) |
| BNO085 IMU | Pi 5 I2C (SDA/SCL) | Qwiic-style cable | Same breakout as the GPS-denied rover, strapped for I2C mode here (PS0/PS1 select the protocol; the rover build uses UART). Mounted on standoffs over the chassis centreline, routed away from motor leads to keep magnetometer and gyro quiet |
| Pi 5 UART (GPIO14/15) | ESP32 LoRa board RX/TX | Dupont, cross-wired | Serial console must be disabled on the Pi first (see Troubleshooting) or the ESP32 drowns in boot messages |
| ESP32 LoRa board | 915 MHz whip antenna | SMA / u.FL coax pigtail | Never transmit without the antenna attached, an open port can damage the SX1262 power amplifier |

## How I Built It

**Q: Build steps (10 steps with code; expand to read)**

A: Rover R2 is a deliberate copy of R1: the same metal 4WD chassis with wheel encoders, a Pi 5 8 GB with an active cooler running Ubuntu 24.04, and two BTS7960 full-bridge modules (one per side). The drive stack is ROS 2 Jazzy with the same differential-drive bringup I already tuned on the GPS-denied rover: encoder ticks feed wheel odometry, and a BNO085 IMU feeds the heading estimate. Cloning first means any convoy weirdness I see later is a convoy problem, not a "why is this rover different" problem.

## Testing & Metrics

The protocol is built around repeatable, scripted impairment rather than "drive around and see
        what happens." Six run series, each with a fixed setup, procedure, and metric. Everything below
        is a target or a plan, no measured results are published yet, and none will be until the runs
        actually happen.

- T1, Baseline laps. Setup: both links clean, no payload, oval course taped on the floor. Procedure: lead drives 10 laps under teleop at convoy speed while the follower holds a set distance and offset. Metric: mean and worst-case lateral and along-track gap error, the floor every degraded run is compared against.

- T2, Wi-Fi loss sweep. Setup: T1 course, LoRa path recording but Wi-Fi carrying the control traffic. Procedure: repeat the laps with netem loss stepped through 5, 10, 20, 30, and 40 percent, one loss level per lap set. Metric: gap error at each loss level, the loss-vs-control-quality curve.

- T3, LoRa duty-cycle sweep. Setup: control traffic moved to the LoRa path. Procedure: firmware drops every 2nd, then every 4th, then every 8th packet, plus RSSI logged at the receiver. Metric: same gap-error curve against an air-link impairment, cross-checked with the Wi-Fi curve.

- T4, Blackout runs. Setup: T1 course. Procedure: scripted full link loss of 5, 15, 30, and 60 seconds mid-lap on both paths. Metric: grace-window behaviour, safe-stop distance from the hold point, and recovery time from first good packet back to within formation tolerance.

- T5, Payload repeats. Setup: weighted dummy payload strapped to the follower. Procedure: T2 and T4 repeated under load. Metric: how cargo mass changes braking distance, gap error, and rejoin behaviour.

- T6, E-stop drill. Setup: clear course, hand on the e-stop. Procedure: manual e-stop press mid-lap during a degraded-link run. Metric: motor power cuts immediately, verified by inspection of the interlock, every time, before any T2-T5 series starts.

| Metric | Target | Current status |
| --- | --- | --- |
| Formation gap error, clean link (T1) | Hold the set distance with sub-metre lateral error across full laps | In progress, controller tuning under way |
| Formation stability at 20% sustained loss (T2/T3) | Convoy holds formation without triggering safe-stop | In progress, impairment profiles scripted, sweep not yet run |
| Safe-stop on full link loss (T4) | Controlled stop at the hold point, no contact with the lead | In progress, watchdog state machine implemented, blackout series pending |
| Recovery time after blackout (T4) | Rejoin to within formation tolerance with no human input | In progress, analysis script validated on fixtures, awaiting run data |
| Packet-loss tolerance (T2/T3) | Characterise the sustained loss rate that forces a safe-stop | Not started, depends on completed loss sweeps |
| Payload effect (T5) | Quantify braking-distance and gap-error change under load | Not started, follows the no-payload baseline |

Measured numbers from these series will be published here with the CSV logs and plots once the
        runs are complete. I am not publishing figures before the data exists.

## Troubleshooting & Lessons

- Serial garbage on the Pi's UART. The ESP32 received a wall of boot messages and login prompts instead of packets. Cause: the Pi's serial console is enabled by default on the GPIO UART. Fix: remove console=serial0,115200 from /boot/firmware/cmdline.txt, keep enable_uart=1 in config.txt, reboot, and confirm with a loopback test before reconnecting the radio.

- Odometry rotated while driving straight. R2's /odom reported a slow turn on a straight line. Cause: encoder A/B channels swapped on one motor pair. Fix: swap the channels in the bringup config. Lesson: the taped 2 m square from step 01 is not optional ceremony, it catches exactly this class of wiring mistake before it poisons convoy data.

- Motors twitched at boot. Both rovers lurched for a second when power was applied, before ROS came up. Cause: the BTS7960 enable lines were floating during boot. Fix: pull-down resistors on R_EN/L_EN and firmware that holds enable low until bringup completes. An e-stop is essential, but a rover should also be inert by default.

- Impairment that wasn't. One blackout run logged zero sequence gaps, suspiciously perfect data. Cause: the netem rule had been applied to the laptop's interface, not the follower's wlan0. Fix: tc -s qdisc show dev wlan0 on the follower before every run, and the sequence-gap log must agree with the configured loss rate or the run is void.

- Grace window too generous. With an early 10-second grace window, the follower tracked a stale extrapolated vector into the lead's braking zone during a blackout test. Fix: a much shorter grace window and mandatory deceleration in HOLD. Lesson: every degraded-link parameter is a safety parameter, tune it like one.

## Safety & Canada Notes

## Status & Roadmap

- Done: both rovers built on the shared drive stack (chassis, Pi 5, BTS7960, e-stops) and driving under ROS 2 teleop; ESP32 LoRa boards flashed with the RadioLib-based broadcast/receive firmware; convoy packet format (ID, sequence, timestamp, pose, heading, speed, CRC) defined and flowing lead-to-follower; bench topology monitor showing per-link status; blackout/impairment scripts written; analysis script validated on fixtures.

- In progress: pure-pursuit-style gap-following controller tuning at a fixed following distance; watchdog hold-stop-rejoin state machine refinement after early grace-window testing; logging pipeline hardening (rosbag + CSV) ahead of the T1 baseline series.

- Next: T1 baseline clean-link laps, then the T2/T3 loss sweeps and T4 blackout runs; T5 payload runs with the weighted dummy cargo; publish following-error, recovery-time, and loss-tolerance results with the raw logs.

## Related Builds

- Canadian Defence Hardware Program, the hub page: the full program, all eleven builds, and the shared parts phases this convoy draws from.

- GPS-Denied Navigation Rover, the donor build: same chassis, drive stack, and ROS 2 odometry this convoy is cloned from.

- DDIL-Proof DevOps, the software-side version of the same problem: store-and-forward and graceful degradation over denied, intermittent links.

- Multi-Domain Common Operating Picture, where these rovers eventually report: every node buffers through dead links and syncs on reconnect into one fused picture.

## Build Narrative: Phase by Phase

Phase 1: reuse the proven stack. Both rovers are built on the GPS-denied rover's drive stack (chassis, Pi 5, BTS7960, e-stops) driving under ROS 2 teleop. Nothing in this build re-proves the wheels; it adds the convoy link, the follow controller, and the degraded-link test protocol.

Phase 2: the convoy link. ESP32 LoRa boards flashed with RadioLib-based broadcast/receive firmware carry the lead's position, heading, and speed over 915 MHz, with Wi-Fi as a fallback path. The packet format (ID, sequence, timestamp, pose, heading, speed, CRC) was defined before the controller, so loss and corruption are measurable from the sequence numbers.

Phase 3: gap following. The follower runs a pure-pursuit-style gap-following controller holding a set distance and offset behind the lead, tuned on a bench topology monitor showing per-link status before any outdoor laps.

Phase 4: degraded-link behaviour. The engineering is in the watchdog hold-stop-rejoin state machine and its grace window: how long the follower coasts on the last good vector, when it must decelerate to a stop, and how it rejoins when the link returns. Early grace-window testing already forced a shorter window plus mandatory deceleration in HOLD after the follower tracked a stale vector into the lead's braking zone.

Phase 5: measurement tooling. Blackout and impairment scripts degrade the link on purpose; the logging pipeline (rosbag plus CSV) and the analysis script, validated on fixtures, compute formation error versus packet loss, blackout behaviour, and rejoin time. A serial-console mistake (Pi boot messages on the GPIO UART) and a misapplied netem rule (on the laptop's interface, not the follower's wlan0) were both caught by the discipline of checking before every run.

## What You Need

Everything mechanical is already proven by the rover build. The new parts are the radios, the controller, and the willingness to break your own link on purpose.

| Category | Item | Notes |
| --- | --- | --- |
| Hardware | Two rover builds | The GPS-denied rover's chassis stack, doubled: chassis, Pi 5, BTS7960, e-stops |
| Hardware | ESP32 LoRa boards | 915 MHz broadcast/receive firmware via RadioLib; Wi-Fi as the fallback path |
| Hardware | Payload dummy | Weighted cargo for the T5 payload runs |
| Software | ROS 2, pymavlink-free | Gap-following controller, watchdog state machine, bench topology monitor |
| Software | rosbag + CSV analysis | Formation error vs loss curves computed from sequence gaps in the logs |
| Software | Impairment scripts | Deliberate loss, delay, and blackout on the follower's interface; always verify with tc qdisc show before the run |
| Skills | ROS 2, control basics, RF | Pure-pursuit tuning, state-machine design, LoRa link behaviour under loss |
| Accounts | None | No accounts or licenses required |

## Challenges and Lessons Learned

- Serial garbage on the Pi's UART. The ESP32 received boot messages and login prompts instead of packets because the Pi's serial console owned the GPIO UART. Lesson: strip console=serial0,115200 from cmdline.txt, keep enable_uart=1, and confirm with a loopback test before reconnecting the radio.

- Odometry rotated while driving straight. One follower reported a slow turn on a straight line from swapped encoder A/B channels on one motor pair. Lesson: the taped 2 m square from step 01 is not optional ceremony, it catches this class of wiring mistake before it poisons convoy data.

- Motors twitched at boot. Both rovers lurched on power-up because the BTS7960 enable lines floated before ROS came up. Lesson: pull-down resistors on R_EN/L_EN and firmware that holds enable low until bringup completes; a rover should be inert by default, the e-stop is the last resort, not the first.

- An impairment that was not. A blackout run logged zero sequence gaps because the netem rule landed on the laptop's interface instead of the follower's wlan0. Lesson: the sequence-gap log must agree with the configured loss rate or the run is void.

- The grace window was too generous. A 10-second window let the follower track a stale extrapolated vector into the lead's braking zone during a blackout test. Lesson: every degraded-link parameter is a safety parameter, tune it like one.

## What Is Next

- T1 baseline clean-link laps: the formation error the controller achieves when the radio is perfect.

- T2 and T3 loss sweeps: formation error as a function of packet loss rate, plus the delay sweep.

- T4 blackout runs: full link loss, hold-stop behaviour, and measured rejoin time.

- T5 payload runs with the weighted dummy cargo, checking whether load changes the follower dynamics.

- Publish following error, recovery time, and loss tolerance with the raw logs, so the curves are checkable, not just the conclusions.

- Feed convoy telemetry into the common operating picture so the lead-follower pair shows up as one track with a health indicator.

## Frequently Asked Questions

**Q: How do I fix 'Serial garbage on the Pi's UART.'?**

A: The ESP32 received a wall of boot messages and login prompts instead of packets. Cause: the Pi's serial console is enabled by default on the GPIO UART. Fix: remove console=serial0,115200 from /boot/firmware/cmdline.txt, keep enable_uart=1 in config.txt, reboot, and confirm with a loopback test before reconnecting the radio.

**Q: How do I fix 'Odometry rotated while driving straight.'?**

A: R2's /odom reported a slow turn on a straight line. Cause: encoder A/B channels swapped on one motor pair. Fix: swap the channels in the bringup config. Lesson: the taped 2 m square from step 01 is not optional ceremony, it catches exactly this class of wiring mistake before it poisons convoy data.

**Q: How do I fix 'Motors twitched at boot.'?**

A: Both rovers lurched for a second when power was applied, before ROS came up. Cause: the BTS7960 enable lines were floating during boot. Fix: pull-down resistors on R_EN/L_EN and firmware that holds enable low until bringup completes. An e-stop is essential, but a rover should also be inert by default.

**Q: How do I fix 'Impairment that wasn't.'?**

A: One blackout run logged zero sequence gaps, suspiciously perfect data. Cause: the netem rule had been applied to the laptop's interface, not the follower's wlan0. Fix: tc -s qdisc show dev wlan0 on the follower before every run, and the sequence-gap log must agree with the configured loss rate or the run is void.

**Q: How do I fix 'Grace window too generous.'?**

A: With an early 10-second grace window, the follower tracked a stale extrapolated vector into the lead's braking zone during a blackout test. Fix: a much shorter grace window and mandatory deceleration in HOLD. Lesson: every degraded-link parameter is a safety parameter, tune it like one.

## Cite This Page

**Q: Citation formats**

A: Plain text
