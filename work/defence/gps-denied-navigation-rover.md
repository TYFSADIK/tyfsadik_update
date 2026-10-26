# GPS-Denied Navigation Rover

Written by [Taki Sadik](../../about.html) · Last updated 2026-10-22 · Status: Building · 33 min read

A ROS 2 rover that keeps navigating after GNSS is cut: wheel odometry, a BNO085 IMU, and 2D LiDAR fused with an Extended Kalman Filter, with position drift measured against a u-blox reference track (meter-class GNSS, not survey grade).

## Overview

This build is a wheeled skid-steer rover (a 4WD metal chassis) that keeps an
        honest estimate of where it is after its satellite navigation is taken away.
        Wheel encoders, a BNO085 IMU, and a 2D LiDAR feed an Extended Kalman Filter running on a
        Raspberry Pi 5 under ROS 2. The u-blox M9N GNSS module rides along only as a reference track: I
        drive a known loop with GNSS on, then switch it off and measure how fast the estimated
        position drifts away from reality, expressed as error versus distance travelled.

Why this matters in Canada: DRDC is testing GPS-denied navigation, convoying, and
        cold-weather performance on exercises like Operation NANOOK, because GNSS jamming
        and denial are now baseline assumptions in any real operating area, and because the high
        Arctic adds weak satellite geometry on top. The Army's MINERVA challenges and the Defence
        Drone Initiative (launched July 23, 2026) both name ground robots that must keep working in
        exactly these conditions.

The build pattern is not mine. Published research (including work on arXiv) shows
        terrain-referenced and dead-reckoning localization for ground vehicles that fuses wheel
        odometry and IMU in GNSS-denied environments, with scan matching to arrest drift. This rover
        reproduces that pattern at hobby scale, on hardware already on my bench, with the drift
        numbers measured and published rather than assumed.

## Proof of Build

What each part of the photo does:

- 4WD skid-steer chassis: the wheeled base. Its wheel encoders give odometry, the starting point for knowing where it is without GPS.

- LiDAR puck: scans the room. Matching scans corrects the drift that builds up from the wheels and the IMU.

- Pi Camera Module 3: visual verification, so a run can be checked against what the robot actually saw.

- Raspberry Pi 5: runs the ROS 2 navigation stack.

- Laptop with RViz: shows the fused map, the planned path, and live battery and IMU telemetry.

## Bill of Materials

Everything below is purchased and on the bench. The u-blox M9N GNSS module used for ground
        truth is shared from the program's Phase 0 kit. Software (Ubuntu 24.04, ROS 2 Jazzy) is free.

| Part | Role | Details | Est. US$ |
| --- | --- | --- | --- |
| Chassis | Wheeled skid-steer base | 2 metal 4WD chassis with wheel encoders | 80-150 each |
| Compute | ROS 2 navigation stack | Pi 5 8 GB per rover, active cooler | ~145 each |
| Motor driver | Skid-steer drive | 2x BTS7960 full-bridge modules, one per side (each module is two BTS7960 half-bridges) | 20-60 |
| LiDAR | External drift witness | 2D LiDAR (LD19 / RPLIDAR A1 class), one rover first | 70-150 |
| IMU | Heading and attitude | BNO085 breakout, 9-axis on-chip fusion | 25-40 |
| Camera | Visual verification | Pi Camera Module 3 | 25-50 |
| Power | Split-rail power and safety | Li-ion pack with BMS, DC-DC 5 V/5 A, physical e-stop switch | 60-100 |

## Wiring & Connections

The full interconnect map. Two rules govern everything: motor power and logic power never
        share a rail, and every signal pair gets a common ground reference back to the Pi.

| From | To | Cable or interface | Notes |
| --- | --- | --- | --- |
| Li-ion pack | BMS, then main fuse (10 A) | 18 AWG silicone wire, XT60 | Fuse within 10 cm of the pack; BMS handles cell protection and balancing |
| Fused pack output | BTS7960 B+ / B- (motor power) | 18 AWG, through the e-stop switch | Latching mushroom e-stop in series; cuts motor power only, never the Pi |
| Fused pack output | DC-DC buck to 5 V / 5 A | 18 AWG in, USB-C breakout out | Separate branch from the motor rail, fused at 3 A; powers Pi 5 and sensors |
| Pi 5 GPIO 12, 13 (PWM0) / 18, 19 (PWM1) | BTS7960 RPWM / LPWM per side | 22 AWG jumper, 20 cm max | Hardware PWM channels; BTS7960 R_EN / L_EN tied high through a GPIO kill line |
| BTS7960 B- | Pi 5 GND | 22 AWG | Common ground is mandatory, without it PWM levels float and the motors twitch |
| Wheel encoders (A/B quadrature, x4) | Pi 5 GPIO inputs | Twisted pair per encoder | Hall encoders, 3.3 V pull-ups; counted by pigpio hardware-timed callbacks |
| BNO085 breakout | Pi 5 UART0 (GPIO 14 TX / 15 RX, /dev/serial0) | 4-wire: VIN 3.3 V, GND, TX, RX | PS1 high and PS0 low select UART-SHTP (3 Mbit/s), not the UART-RVC heading-only mode; udev symlink /dev/imu |
| LD19 LiDAR | Pi 5 USB-A (via its UART-USB adapter board) | USB cable from the adapter board | 230400 baud serial; udev symlink /dev/lidar; powered from the 5 V rail |
| Pi Camera Module 3 | Pi 5 CSI port | 15-to-22-pin FPC ribbon | Kept short and away from the motor wiring to avoid noise on the ribbon |
| u-blox M9N (ground truth) | Pi 5 USB-A | USB cable | Logging only, never wired into the estimator; antenna on a ground plate away from the LiDAR |

## Architecture

Wheel encoders4WD chassis

BNO085 IMUUART / I2C

LD19 2D LiDAR/scan topic

Pi Camera Module 3visual record

ros2_controldiff-drive stack

Wheel odometry/odom

robot_localization EKFwheel odom + IMU

rf2o scan matcherLiDAR odometry

SLAM Toolboxmap + pose

Nav2 path planningand control

u-blox M9N GNSSground truth only

rosbag2 loggingdrift analysis

Figure 1: sensors feed the EKF estimate that drives Nav2; GNSS logs alongside as ground truth and never enters the control loop.

The key discipline: GNSS is not an input to the estimator. It is logged in
        parallel so that when I switch it off, the comparison between the EKF's belief and the last
        known true track gives a clean, honest drift measurement. The rover navigates the whole time
        on what it can sense on board.

## What the EKF Fuses, and What It Refuses to Know

The extended Kalman filter in robot_localization is not a blender; it is a
          referee. Each sensor reports a pose fragment plus a covariance that says how
          much the filter should trust it. The wheel encoders report translation and rotation, but they
          are slip-blind: a spinning wheel in mud reports motion the chassis never
          made, and the encoders cannot tell. The BNO085 reports heading and attitude from its on-chip
          SH-2 fusion (accelerometer, gyro, and magnetometer fused on an ARM core inside the sensor),
          but it measures no translation at all. The LiDAR, through rf2o scan matching, is the only
          external witness: it compares consecutive scans against the world and
          reports how the world actually moved, which arrests the drift the first two accumulate.

The discipline of the experiment is which sensors are allowed in each run. Run 3
          feeds the EKF encoders and IMU only, so the drift curve measures proprioception alone; Run 4
          adds the LiDAR witness, so the difference between the curves is the LiDAR's contribution.
          GNSS is logged beside all of it and subscribed to by nothing, which is what makes the Run 5
          cut honest: the truth log is independent of the belief being measured.

## How I Built It

**Q: 01 Chassis and drive train**

A: WHAT: assembled the metal 4WD chassis, mounted the four gear motors with their Hall encoders, and wired each side's two motors in parallel to one BTS7960 full-bridge module (two modules total, one per side), giving classic skid-steer (left channel, right channel). WHY: skid-steer needs no steering servo and turns in place, which is exactly what a survey-and-verify rover wants, at the cost of wheel scrub, which is precisely the odometry problem this build exists to measure.

**Q: 02 Power system and e-stop**

A: WHAT: the Li-ion pack feeds two fused branches, one through the latching e-stop to the BTS7960 motor input, one through a DC-DC buck producing a clean 5 V/5 A rail for the Pi 5, LiDAR, IMU, and camera. WHY: a stalled 4WD drivetrain pulls many amps and drags an unprotected shared rail down with it; the instant the Pi browns out, your estimator dies and the log with it. Separating the rails is the single most important reliability decision on the build.

**Q: 03 Ubuntu and ROS 2 Jazzy install**

A: WHAT: Ubuntu 24.04 Server (64-bit) flashed to a high-endurance microSD, then ROS 2 Jazzy from the official apt repository. WHY: Jazzy is the current LTS ROS 2 release and pairs natively with Ubuntu 24.04 (noble); staying on the supported pairing means every package I need, robot_localization, slam_toolbox, Nav2, installs from binary debs instead of source builds on an ARM board.

**Q: 04 URDF and TF tree**

A: WHAT: wrote the robot_description URDF for the chassis, base_link at the geometric center, four wheel links at measured offsets, imu_link at the BNO085's physical location, laser_link at the LiDAR puck's rotation center. WHY: the EKF, the scan matcher, and SLAM all fuse data through TF transforms; if laser_link is 5 cm off its real position, every fused estimate inherits that bias and it shows up as a mystery drift that no amount of covariance tuning fixes.

**Q: 05 ros2_control diff-drive stack**

A: WHAT: brought up the ros2_control framework with diff_drive_controller commanding the motors through a custom hardware interface that exports PWM duty to the BTS7960 through the Pi 5's hardware PWM channels (GPIO 12/13 and 18/19 via /dev/pwmchip; pigpio does not support the Pi 5's RP1), and reads the four encoder channels back as wheel joint states via gpiod. WHY: diff_drive_controller gives me a calibrated /odom topic and a /cmd_vel interface for free, the same interface Nav2 expects, as long as wheel_separation and wheel_radius are honest.

**Q: 06 BNO085 IMU bring-up**

A: WHAT: wired the BNO085 breakout over UART (Pi 5 /dev/serial0, GPIO 14/15) with I2C as fallback, and publish sensor_msgs/Imu from a small node I wrote wrapping the Adafruit CircuitPython BNO08x library over the SHTP protocol. WHY: the BNO085 does sensor fusion on-chip, it outputs rotation-vector orientation already filtered against gyro drift, which at this price point is far better than anything I would integrate from raw gyro rates on the Pi.

**Q: 07 LD19 LiDAR bring-up**

A: WHAT: the LD19 2D LiDAR (360-degree triangulation scanner, 12 m class range on high-reflectivity targets, less on dark ones) connects through its UART-to-USB adapter board and publishes sensor_msgs/LaserScan on /scan via the vendor's ROS 2 driver. WHY: LiDAR is the only sensor on the rover that observes the world rather than the wheels, wheel odometry and IMU are both proprioceptive and both drift, while scan matching against static walls gives an external reference that arrests that drift.

**Q: 08 EKF odometry fusion**

A: WHAT: the robot_localization package runs an Extended Kalman Filter (ekf_node) fusing wheel odometry (x and yaw velocities) with the BNO085's fused orientation and angular velocity, publishing the odom->base_link transform on /odometry/filtered. WHY: the encoders are good at short-range translation but blind to slip; the IMU is excellent at heading but can't measure translation at all. The EKF is where each sensor covers the other's blind spot, with honest covariances so the filter knows how much to trust each input.

**Q: 09 LiDAR aiding**

A: WHAT: two additions on top of the EKF. First, rf2o_laser_odometry (RF2O, dense range-flow scan-to-scan matching) publishes a LiDAR-based odometry estimate that becomes a third EKF input. Second, slam_toolbox runs in online async mode to maintain a map and the map->odom correction. WHY: on a skid-steer chassis, wheel slip is not an edge case, it is every turn. RF2O measures actual motion over the ground from the scans themselves, so when the wheels lie, the filter has a witness that doesn't.

**Q: 10 Reference track, the cut, and publish**

A: WHAT: the u-blox M9N logs a GNSS track over a known loop (measured on the ground with markers) as a reference track, published on /fix by the nmea_navsat_driver but never subscribed by the estimator. Once fix quality is stable, I switch GNSS off on my own receiver, stopping the receiver's navigation output with a UBX command, and the rover keeps driving on odometry + IMU + LiDAR. WHY: this is the whole point of the build. Because the estimator never sees GNSS in either phase, the cut simulates the denied condition; after the cut there is no truth receiver anymore, so drift is scored by loop closure, the distance between the EKF's estimated end pose and the surveyed start marker, with the M9N reference validating the pre-cut segment. There is zero ambiguity about where each number came from.

## Why Skid-Steer Odometry Lies

A skid-steer rover turns by driving its left and right wheels at different speeds and letting
          the tires scrub sideways across the ground; there is no steering geometry to
          measure. Every turn therefore slips, and slip is unobservable to the encoders:
          the ticks say the wheel rotated, nothing says whether the ground agreed. Worse, the slip
          depends on surface, load, and speed, so no fixed correction works everywhere. That is why Run 2
          calibrates an effective wheel separation on the 5 m line instead of trusting
          the tape measure: the number that matters is the one that predicts how far the rover turned,
          not how far apart the wheels sit.

Drive loop(GNSS on, truth logging)

CUT(navigation output off)

Keep driving(odom + IMU only)

Keep driving(odom + IMU + LiDAR)

Compare EKF posevs truth track

Error vs distance(drift curve)

Figure 2: the Run 5 GNSS-cut experiment. The rover drives the surveyed loop with GNSS logging truth, the navigation output is switched off mid-loop, and driving continues in both estimator configurations; the comparison of EKF belief against the truth track is the drift measurement.

Figure: the target error envelope the build is aiming at, not measured data. The dashed line is the 2% loop-closure target (Run 3, EKF only); the dotted line is the rough expectation with LiDAR aiding (Run 4). Real curves land here once the loop runs are scored against the GNSS truth log.

## Testing & Metrics

The protocol is fixed before the runs so the numbers mean something: same loop, same speed,
        same logging, one variable changed at a time. Each run below lists setup, procedure, and the
        metric it produces.

- Run 1, Bench spin test. Setup: wheels off the ground, rover chocked. Procedure: command fixed velocities in both directions per side. Metric: encoder ticks per revolution consistency and command-to-count linearity; catches wiring or decoding faults before they masquerade as odometry error.

- Run 2, Straight-line calibration. Setup: taped 5 m straight line on smooth floor. Procedure: drive the line at constant speed, ten repetitions. Metric: actual versus commanded distance (calibrates effective wheel radius) and lateral/heading error at the line end (calibrates effective wheel separation, skid-steer scrub makes the geometric value wrong).

- Run 3, EKF-only known loop. Setup: surveyed closed loop with marked waypoints, GNSS logging as truth. Procedure: drive the loop at constant speed with the EKF fed by wheel odometry + IMU only. Metric: position error versus distance travelled (EKF pose against the GNSS track and the markers), plus heading error growth and loop-closure error at the return point.

- Run 4, EKF + LiDAR aiding, same loop. Setup: identical to Run 3, with rf2o added as the third EKF input and SLAM Toolbox maintaining the map frame. Procedure: same loop, same speed, same logging. Metric: the same error-versus-distance curve; the comparison against Run 3 is the experiment, and the LiDAR's contribution shows up directly in the drift numbers.

- Run 5, The GNSS cut. Setup: Run 4 configuration, GNSS at a stable 3D fix. Procedure: drive the loop with GNSS on to establish truth, switch the receiver's navigation output off mid-loop, keep driving several more laps. Metric: drift growth rate after the cut, error versus distance travelled with GNSS denied, with and without LiDAR aiding.

- Run 6, Cold-weather repeat (planned). Setup: Run 5 repeated outdoors in winter. Procedure: identical loop and logging, battery and IMU temperatures logged alongside. Metric: the same drift curves against temperature, DRDC's NANOOK cold-weather thread at bench scale. The cold-soak rig characterizes the battery side of the same question.

Per-run conditions (surface, temperature, battery state) are logged with the bag, since all
        three move the numbers. Targets below are what I am aiming at, not results I have:

| Metric | Target | Measured to date | Current status |
| --- | --- | --- | --- |
| Loop-closure error, EKF only (Run 3) | Under 2% of distance travelled | Not yet measured | In progress, tuning passes underway, not yet measured against truth |
| Loop-closure error, EKF + LiDAR aiding (Run 4) | Measurably better than Run 3 on the same loop | Not yet measured | In progress, rf2o integration benched, comparison runs not yet done |
| Drift growth after GNSS cut (Run 5) | Published error-versus-distance curve, both configurations | Not yet measured | In progress, logging pipeline ready, first cut runs planned |
| Heading error growth, GNSS denied | Quantified per 100 m travelled | Not yet measured | In progress |
| IMU bias stability across a run | No visible yaw drift in a static 10-minute log | Not yet measured | In progress, static logs collected, analysis pending |
| Cold-weather drift delta (Run 6) | Same protocol repeated at winter temperatures | No data, waiting on winter | Planned, waiting on weather |

No drift numbers are published yet because I won't quote figures I haven't measured. The
        dataset and plots go up with the build write-up once the loop runs are complete.

## Troubleshooting & Lessons

- Motors twitching with no command. Symptom: random wheel jerks at idle. Cause: the BTS7960's ground was not tied to the Pi's ground, so PWM levels floated. Fix: dedicated 22 AWG ground wire from driver B- to Pi GND; verified with a continuity check, twitching gone. Lesson: on a mixed-voltage robot, "obviously it's grounded" is a claim, not a measurement.

- Pi browning out when motors stalled. Symptom: vcgencmd get_throttled returning under-voltage flags and the Pi rebooting mid-run. Cause: Pi and motors shared one rail; a stall dragged it below the Pi's cutoff. Fix: split the rails (step 02), separate fused DC-DC branch for logic, re-ran the stall test with flags staying at 0x0. This is also why the e-stop cuts motors only, a logging Pi during an incident is a feature.

- Silent IMU, node timing out on the UART. Symptom: /dev/imu opened but no SHTP packets arrived. Cause: the BNO085 breakout shipped with PS1 floating, so it was in I2C mode, not UART. Fix: soldered the PS1 strap high (PS0 low, UART-SHTP) per the datasheet. Lesson: verify the mode pins before suspecting the software; I burned an evening on a driver that was never the problem.

- Odometry TF fighting in RViz. Symptom: the robot flickered between two positions a metre apart. Cause: both diff_drive_controller and the EKF were publishing odom->base_link. Fix: enable_odom_tf: false on the controller so the EKF owns the transform. Lesson: exactly one publisher per TF frame, always, check with ros2 run tf2_ros tf2_echo odom base_link when in doubt.

- Scan matcher diverging along a blank wall. Symptom: /odom_rf2o froze or jumped while driving past a featureless wall. Cause: scan matching has nothing to lock onto without features, a known RF2O limitation, not a bug. Fix: RF2O enters the EKF with a larger covariance than wheel odometry, so the filter degrades gracefully toward encoder+IMU behaviour. Lesson: every aiding sensor needs a designed failure mode, not just a happy path.

## Safety & Legal Notes

## Status & Roadmap

- Done: chassis assembled with encoders wired, BTS7960 drive train and power rail benched (stall-tested, no brownouts after the rail split), e-stop installed and tested, Ubuntu 24.04 + ROS 2 Jazzy on the Pi 5, URDF measured and TF-verified, diff-drive ros2_control stack driving the rover, BNO085 and LD19 publishing at rate, Runs 1-2 (bench spin, straight-line calibration) complete.

- In progress: EKF tuning in robot_localization (covariance work), rf2o integration, first GNSS-cut loop runs with rosbag logging, drift analysis scripts.

- Next: LiDAR aiding comparison runs (Runs 3-5), publish the dataset and drift plots, winter cold-weather repeat (Run 6); second rover becomes the convoy follower.

## Related Builds

This rover is Phase 4 of my defence hardware program:

- Canadian Defence Hardware Program, the hub: every build, full BOMs, and the stated Canadian requirements each one answers.

- Convoy-Following Robots on a Degraded Mesh, the second rover follows a lead over a lossy LoRa/Wi-Fi mesh; it depends on this page's localization stack.

- Ground Seismic & Acoustic Perimeter Mesh, the mesh detects, and this rover is the human-tasked verify asset that drives out to look.

- Multi-Domain Common Operating Picture, where this rover's signed tracks eventually publish alongside the sky, water, and ground nodes.

## Build Narrative: Phase by Phase

Phase 1: chassis and power. A 4WD metal skid-steer chassis with wheel encoders, driven by BTS7960 H-bridges. The power rail was split early after stall testing showed the Pi and motors sharing one rail: a stall dragged the rail below the Pi's cutoff and rebooted it mid-run. Now a fused DC-DC branch feeds logic separately, an e-stop cuts motor power only (a logging Pi during an incident is a feature), and a dedicated ground wire from driver B- to Pi GND ended the mysterious idle wheel jerks.

Phase 2: compute and bringup. Ubuntu 24.04 with ROS 2 Jazzy on the Pi 5. The URDF was measured against the real chassis and TF-verified, and a diff-drive ros2_control stack drives the rover. Exactly one publisher owns each TF frame: the controller's enable_odom_tf is off so the EKF owns odom-to-base_link.

Phase 3: sensor stack. A BNO085 IMU (with its PS1 mode strap soldered high for UART, after an evening lost to a driver that was never the problem), an LD19 2D LiDAR, and wheel encoders feed the estimator. The u-blox M9N GNSS module rides along as ground truth only: known loops are driven with GNSS on, then GNSS is switched off and drift is measured as error versus distance travelled.

Phase 4: estimation. The Extended Kalman Filter runs in robot_localization with covariance tuning as the current work item. rf2o scan matching enters the filter with a larger covariance than wheel odometry, so in featureless areas (a blank wall the matcher cannot lock onto) the filter degrades gracefully toward encoder-plus-IMU behaviour instead of diverging.

Phase 5: test discipline. Runs 1 and 2 (bench spin, straight-line calibration) are complete with rosbag logging. The taped 5 m line in Run 2 caught a swapped encoder channel before it could poison convoy data. First GNSS-cut loop runs and drift-analysis scripts are in progress now.

## What You Need

This is the one build in the program where the software stack outweighs the hardware cost. ROS 2 fluency is assumed; the table lists what is not obvious.

| Category | Item | Notes |
| --- | --- | --- |
| Hardware | 4WD metal chassis + encoders | Skid-steer platform with quadrature wheel encoders; metal survives repeated outdoor loop runs |
| Hardware | Raspberry Pi 5 | Runs Ubuntu 24.04 and the full ROS 2 Jazzy stack, including the EKF |
| Hardware | BNO085 IMU, LD19 LiDAR | Orientation and 2D scan matching; verify the IMU mode-strap pins against the datasheet before trusting the driver |
| Hardware | u-blox M9N GNSS | Ground truth only: it measures drift, it never aids the filter |
| Hardware | BTS7960 drivers, split power rail, e-stop | Fused logic branch separate from motor rail; e-stop cuts motors only |
| Software | ROS 2 Jazzy, robot_localization, rf2o | Diff-drive control, the EKF, and laser scan matching |
| Software | rosbag2, Python analysis | Every run is recorded; drift is computed offline as error versus distance travelled |
| Skills | ROS 2, state estimation basics, Linux | URDF/TF debugging, covariance reasoning, covariance tuning, rosbag workflows |
| Accounts | None | No accounts or licenses required; the whole stack is open source |

## Challenges and Lessons Learned

- Motors twitched with no command. Random idle wheel jerks came from the BTS7960 ground not being tied to the Pi's ground, so PWM levels floated. Lesson: on a mixed-voltage robot, grounded is a measurement (continuity check), not an assumption.

- The Pi browned out when motors stalled. Shared-rail stall current dragged the logic rail below cutoff and rebooted the Pi mid-run, with vcgencmd get_throttled under-voltage flags as the proof. Lesson: split the rails, fuse the logic branch, and re-run the stall test with flags staying at 0x0.

- A silent IMU on the UART. The BNO085 breakout shipped with PS1 floating, so it was in I2C mode, not UART, and no SHTP packets arrived. Lesson: verify mode pins before suspecting software; the driver was innocent.

- Odometry TF fighting in RViz. The robot flickered between two positions a metre apart because both the diff-drive controller and the EKF published odom-to-base_link. Lesson: exactly one publisher per TF frame, always.

- Scan matcher diverging on a blank wall. rf2o has nothing to lock onto without features, a known limitation, not a bug. Lesson: every aiding sensor needs a designed failure mode (larger covariance, graceful degradation), not just a happy path.

## What Is Next

- LiDAR-aiding comparison runs (Runs 3 to 5): same loops with and without scan matching, to measure how much LiDAR actually buys against encoder-plus-IMU drift.

- Publish the dataset and the drift plots: measured error versus distance travelled, GNSS-cut loops, all of it.

- Winter cold-weather repeat (Run 6): the same loops in Toronto winter, because cold changes batteries, lubricants, and sensor behaviour, and the MINERVA documents specifically complain about it.

- The second rover becomes the convoy follower in the degraded-mesh build, reusing this chassis stack.

- Longer term, evaluate terrain-referenced aiding (the published arXiv pattern this build follows) as a next aid source for the EKF.

## Frequently Asked Questions

**Q: How do I fix 'Motors twitching with no command.'?**

A: Symptom: random wheel jerks at idle. Cause: the BTS7960's ground was not tied to the Pi's ground, so PWM levels floated. Fix: dedicated 22 AWG ground wire from driver B- to Pi GND; verified with a continuity check, twitching gone. Lesson: on a mixed-voltage robot, "obviously it's grounded" is a claim, not a measurement.

**Q: How do I fix 'Pi browning out when motors stalled.'?**

A: Symptom: vcgencmd get_throttled returning under-voltage flags and the Pi rebooting mid-run. Cause: Pi and motors shared one rail; a stall dragged it below the Pi's cutoff. Fix: split the rails (step 02), separate fused DC-DC branch for logic, re-ran the stall test with flags staying at 0x0. This is also why the e-stop cuts motors only, a logging Pi during an incident is a feature.

**Q: How do I fix 'Silent IMU, node timing out on the UART.'?**

A: Symptom: /dev/imu opened but no SHTP packets arrived. Cause: the BNO085 breakout shipped with PS1 floating, so it was in I2C mode, not UART. Fix: soldered the PS1 strap high (PS0 low, UART-SHTP) per the datasheet. Lesson: verify the mode pins before suspecting the software; I burned an evening on a driver that was never the problem.

**Q: How do I fix 'Odometry TF fighting in RViz.'?**

A: Symptom: the robot flickered between two positions a metre apart. Cause: both diff_drive_controller and the EKF were publishing odom->base_link. Fix: enable_odom_tf: false on the controller so the EKF owns the transform. Lesson: exactly one publisher per TF frame, always, check with ros2 run tf2_ros tf2_echo odom base_link when in doubt.

**Q: How do I fix 'Scan matcher diverging along a blank wall.'?**

A: Symptom: /odom_rf2o froze or jumped while driving past a featureless wall. Cause: scan matching has nothing to lock onto without features, a known RF2O limitation, not a bug. Fix: RF2O enters the EKF with a larger covariance than wheel odometry, so the filter degrades gracefully toward encoder+IMU behaviour. Lesson: every aiding sensor needs a designed failure mode, not just a happy path.

## Cite This Page

**Q: Citation formats**

A: Plain text
