# Cold-Soak Battery Characterization Rig

Written by [Taki Sadik](../../about.html) · Last updated 2026-10-22 · Status: Building · 32 min read

A heated, instrumented drone battery bay soaked in a lab freezer and in real Canadian winter, logging runtime, voltage sag, and failure modes against temperature, and publishing it all as a reproducible dataset.

## Overview

LiPo batteries hate the cold, and cold is the default operating condition for a huge share of
        Canadian defence scenarios. The Army MINERVA challenges say it plainly: bought-in
        foreign robotic systems have had problems with cold-weather operation, and Canada currently lacks
        an ISR drone that works in Arctic conditions. The Defence Drone Initiative,
        launched July 23, 2026, makes low-cost tactical drones a stated national priority.

So this build is not a drone, it is the measurement rig that tells you whether a drone's power
        system survives the cold. A battery bay on a quadcopter frame carries Kapton heater pads,
        foam insulation, six temperature sensors, and two power monitors. The whole bay goes into a lab
        freezer (and later, the actual Toronto winter), and every run logs pack voltage, discharge and
        heater current, accumulated mAh, and four temperature channels against time.

The deliverable is deliberately boring and valuable: a clean, public dataset of battery
        behaviour versus temperature, measured against a stated Army pain point once the full
        run matrix and outdoor validation are complete, with a full protocol
        anyone can reproduce. Vendors publish marketing numbers; hobbyists publish anecdotes; a controlled,
        documented dataset at 0, -10, -20, and -30 °C is rare, easy to explain, and directly useful to
        anyone sizing an Arctic-capable platform, including the thermal SAR drone in this same program,
        whose packs are the test subjects here.

## Proof of Build

What each part of the photo does:

- Insulated battery bay: holds the pack on the quadcopter frame, with a Kapton heater pad to keep the cells warm before and during flight.

- Fluke multimeter and Pico datalogger: the measurement side: voltage, current and temperature are logged through the whole run.

- Lab freezer at -20 °C: cold-soaks the battery to Canadian winter temperatures before each test.

- Laptop graph: plots voltage sag under load, the number that shows whether a cold battery can still fly the drone safely.

- Hand-drawn schematic: the heating-system wiring, which I worked out on paper before building it.

## Bill of Materials

Everything below is purchased and on the bench; the logging host and test packs come from shared program stock.

| Part | Role | Details | Est. US$ |
| --- | --- | --- | --- |
| Sensors | Temperature and power logging | 6 DS18B20 temperature sensors or thermocouple amps, 2 INA228 power monitors | 40-70 |
| Battery heater | Controlled warming | Kapton heater pads, logic-level N-MOSFET, foam insulation | 20-40 |
| Cold chamber | Freezing environment | A Canadian winter (free), or a cheap chest freezer | 0-300 |
| Logging host | Sampling and storage | Raspberry Pi / ESP32 from program stock | - |
| Test subject | Cell under test | LiPo packs from the drone program | (shared) |

## Architecture

Sensing

Instrumented Battery Bay

1-Wire + I2C

LiPo pack(test subject)

Kapton heater pads

Foam insulation

6x DS18B20cell / bay / pad / ambient

2x INA228voltage + current + mAh

Logging hostRaspberry Pi / ESP32

MOSFET driver

Thermostat / pre-heat control

Fixed discharge load

DatasetCSV + plots

Figure 1: the instrumented bay is sensed over 1-Wire and I2C; the logging host drives the heater MOSFET and writes every run to the dataset.

One design decision shapes everything else: the logging host never enters the cold
        chamber. The Pi sits on the bench at room temperature; only the sensor leads, the heater
        feed, and the discharge leads pass into the freezer through the door gasket. Consumer SD cards,
        crystal oscillators, and USB hubs all get flaky below -20 °C, and a logger that dies at
        minute forty of a -30 °C soak is a wasted evening. Keeping the compute warm and the
        instruments cold is what makes the dataset trustworthy.

## Why Cold Steals Capacity (the Short Version)

A LiPo cell stores the same charge at -30 C as at room temperature; what changes is how fast
          the chemistry can deliver it. Cold slows ion mobility and raises internal
          resistance, so the same 4 A discharge drags the terminal voltage down much harder. The run
          ends not when the chemistry is empty, but when the sagging voltage hits the 12.8 V cutoff
          early, capacity is left stranded behind that wall. Two effects fight back. Discharge itself
          self-heats the cell (resistive heating is unavoidable), which can partially
          recover the curve mid-run; and a heater pad can keep the cell warm, but its energy comes from
          a battery too, so the honest question is never "does heating help", it is "does heating help
          net of its own cost". Run 6 exists to answer exactly that, and the
          heater-branch INA228 measures the cost so nobody has to guess. Cold derating is not a
          single number: it depends on cell chemistry, discharge C-rate, pack age, state of
          charge, and thermal history, which is exactly why this rig measures it per pack
          instead of quoting a generic derating factor.

One hard rule the page already states, and worth repeating: never charge a cold pack.
          Charging lithium below freezing plates lithium metal onto the anode, permanently and
          dangerously; every run in the matrix warms the pack to room temperature before recharge.

## Wiring & Connections

| From | To | Cable or interface | Notes |
| --- | --- | --- | --- |
| DS18B20 harness (VDD, GND, DATA) | Pi GPIO4 (pin 7), 3V3 (pin 1), GND (pin 6) | 1-Wire bus, 3-conductor 22 AWG | Powered 3-wire mode, 4.7 kΩ pull-up between 3V3 and DATA at the Pi end; leads pass through the freezer door gasket |
| INA228 #1 (discharge path) | Pi I2C1: SDA (pin 3), SCL (pin 5) | I2C, address 0x40 | A0/A1 tied to GND; sits in series between the pack and the fixed load |
| INA228 #2 (heater branch) | Same I2C1 bus | I2C, address 0x41 | A0 tied to VS+ to move it off 0x40; measures heater voltage, current, and mAh separately |
| Pi GPIO17 (pin 11) | MOSFET gate | Gate signal wire | 100 Ω series resistor at the gate, 10 kΩ pull-down to GND so the heater fails off during boot |
| 4S pack positive | Kapton pads positive | 18 AWG silicone, 5 A fuse inline | Fuse within 5 cm of the pack lead; heater energy comes from the pack itself, like a real aircraft |
| MOSFET drain | Kapton pads negative | 18 AWG silicone | Source to common GND shared with the Pi; low-side switching |
| Pack discharge lead (XT60) | Load resistor bank | 14 AWG silicone | Load mounted on a heatsink outside the bay, a 60+ W heat source inside the bay would corrupt the thermal data |
| Bench USB-C wall power | Pi 5 V rail | Official 27 W USB-C supply | The Pi stays on the bench at room temperature for every run |

## How I Built It

**Q: 01 Instrumented bay**

A: The battery bay on the quadcopter frame gets the full treatment: Kapton heater pads bonded flat against the bay walls with polyimide tape, a logic-level N-MOSFET switching the pads on the low side, and foam insulation wrapped around the whole bay. The insulation is not there to keep the pack warm for free, it is there to make the heat budget measurable, so watts in maps predictably to degrees gained instead of leaking into the freezer.

**Q: 02 Temperature sensor harness**

A: Six DS18B20 sensors go where the physics actually happens: taped to the cell surface, on the bay wall, directly on the heater pad, in ambient air inside the freezer, plus two spares for cross-checking. All six share one 1-Wire bus on GPIO4 with a single 4.7 kΩ pull-up, in powered 3-wire mode, parasite power over long freezer leads is asking for dropouts.

**Q: 03 INA228 power logging**

A: Two INA228 power monitors do the electrical accounting. One sits in series between the pack and the discharge load and logs bus voltage, shunt current, and accumulated charge; the second sits in the heater feed, so the energy spent on heating is costed separately from the energy delivered to the load. That separation is what makes the heater-strategy comparison in step 09 honest instead of hand-wavy.

**Q: 04 Logging service**

A: The logger is a small Python service on the Pi: each sensor sweep reads all six w1-therm files and both INA228s, integrates current into accumulated mAh, and appends one timestamped row to the run's CSV on the Pi's NVMe drive. One flat CSV per run, one schema for the whole dataset, no database, because a dataset people can open in anything is a dataset people actually check. A full sweep lands about once every few seconds: the DS18B20 needs up to 750 ms per conversion at 12-bit resolution, so six sequential reads through the kernel driver cannot sustain a true 1 Hz cadence, and the logger does not pretend otherwise.

**Q: 05 Heater control**

A: The thermostat strategy is a hysteresis (bang-bang) controller: heat on when the pad sensor falls below the band, off when it rises above it. Hysteresis instead of a single threshold keeps the MOSFET from chattering at the boundary, which both wears nothing mechanical but does pollute the current trace with switching noise the INA228 then has to average out.

**Q: 06 Fixed discharge load**

A: Every comparison in the dataset is only meaningful if the load is identical across runs, so the pack discharges through a fixed resistive bank sized for roughly three-quarter-C draw on the 5200 mAh drone packs (~4 A), close to a cruise-level pull rather than a full-throttle burst. The bank is series-wired chassis-mount power resistors bolted to a heatsink, and it lives outside the insulated bay: a 60-watt heater inside the bay would be the single best way to destroy the dataset's credibility.

**Q: 07 Freezer soak protocol**

A: Each run soaks a fully charged pack in the freezer at a fixed setpoint, 0, -10, -20, -30 °C, and waits until the cell-surface sensor (not the freezer's air, not the freezer's own display) has held within half a degree of the target for fifteen consecutive minutes. That half-degree band is a stability and repeatability criterion, not a claim of uncalibrated absolute accuracy at -30 °C (see the DS18B20 accuracy bands in step 02); it is enforced with cold-reference calibration, not assumed from the datasheet. The core temperature is what the chemistry feels; air temperature in a frost-free freezer swings several degrees with the defrost cycle, which is precisely why the freezer's thermostat is never part of the criterion.

**Q: 08 Winter runs**

A: The freezer is a controlled stand-in, not the real thing. The same protocol repeats outdoors through a Toronto winter, porch and balcony runs at whatever the weather delivers, to validate the freezer data against reality and to catch what a chest freezer physically cannot: wind stripping heat from the insulation, humidity and snow on the connectors, and the slow radiative chill of a clear night.

**Q: 09 Heater strategies**

A: Three strategies run at every setpoint, three repeats each: unheated (the baseline), thermostat-controlled (the step-05 loop holds the bay through the soak and discharge), and pre-heat-and-fly (heat on the ground, disconnect the heater, then discharge on stored warmth, the way a real drone actually launches). The matrix lives in a config file so the runs are driven by data, not by memory.

**Q: 10 Publish**

A: The end product is the dataset itself: per-run CSVs, the weather tags, the run matrix, the plotting code, and the written protocol, setpoints, soak criterion, load sizing, sensor placement, and safety rules, so anyone with a freezer and fifty dollars of sensors can reproduce or extend it. Every published figure regenerates from the raw CSVs with one script; there are no hand-edited plots, because a reviewer should be able to recompute every line on every graph.

## Bang-Bang with a Brain: the Hysteresis Thermostat

The heater loop is a bang-bang controller with hysteresis: the MOSFET is
          fully on or fully off, and the thresholds have a gap between them. A single threshold would
          chatter, flicking the heater on and off every time the pad sensor wiggles across the line;
          hysteresis says "turn on below X, stay on until Y, then stay off until X again", which keeps
          the duty cycle sane. The control sensor is the pad sensor (fast, local, the
          thing the heater can actually overheat), while the safety cutoff watches the
          cell-surface sensor (slow, the thing that matters). Two sensors, two jobs:
          control chases the pad, safety guards the cell. And the gate pull-down means a crashed Pi
          cannot leave the heater on inside an insulated box.

## Testing & Metrics

The protocol is fixed before the numbers are collected, so the results, whatever they turn out
        to be, mean something. Every run follows the same skeleton: charge, rest, soak (or weather),
        discharge at the fixed load, log everything, warm to room temperature, recharge, cross-check.

### Run Plan

- Run 1, Room-temperature baseline. Setup: pack charged to 16.8 V, rested one hour at room temperature, no heater. Procedure: discharge through the fixed 4 A bank to the 12.8 V cutoff while logging. Metric: delivered mAh, runtime, and the reference V(t) curve, every later run is normalized against this one.

- Run 2, Freezer ladder, unheated. Setup: soak per the step-07 criterion at 0, -10, -20, and -30 °C. Procedure: identical discharge to Run 1. Metric: runtime and delivered capacity vs. setpoint, initial sag depth, self-heating recovery, and the failure mode (graceful knee vs. hard cliff) at each temperature.

- Run 3, Freezer ladder, thermostat. Setup: same ladder, thermostat loop active through soak and discharge. Procedure: identical discharge. Metric: capacity recovered vs. Run 2, plus heater mAh from INA228 #2, the net gain or loss per setpoint.

- Run 4, Freezer ladder, pre-heat-and-fly. Setup: same ladder; heater warms the pack for the configured ground time, then disconnects. Procedure: discharge on stored warmth. Metric: capacity vs. Run 3 at zero in-flight heating cost, and how fast the bay bleeds heat after disconnect.

- Run 5, Outdoor winter validation. Setup: porch/balcony runs at real conditions, weather-tagged per step 08. Procedure: identical discharge. Metric: agreement between outdoor curves and the nearest freezer setpoint, this validates (or indicts) the freezer as a proxy.

- Run 6, Heater energy accounting. Setup: aggregated across Runs 3-4. Procedure: heater-branch mAh vs. recovered capacity per setpoint. Metric: the break-even temperature, below which heating pays for itself, above which it does not.

Charge(warm only)

Rest 1 h

Soak(cell within 0.5 Cof setpoint, 15 min)

Discharge(resistive, ~4 A nominal, to 12.8 V)

Log every few seconds(temp + power)

Warm to room temp

Recharge

Cross-check(Fluke vs INA228)

Publish(CSV + plots)

Figure: the per-run skeleton every run in the matrix follows. Charge and recharge only ever happen warm; the soak criterion is measured on the cell-surface sensor, not the freezer display.

Figure: sizing the fixed discharge load from the page's own numbers: ~4 A on a 4S pack (~16 V) means ~64 W of dissipation, so the bank of four 1 ohm 25 W resistors in series (100 W rating) carries it with headroom. The load sits on a heatsink outside the bay, since a 60+ W heat source inside would corrupt the thermal data.

### Targets, Measured Evidence, and Current Status

Honest bookkeeping: targets and progress states only. No measured numbers are published until the full matrix and the outdoor validation are complete.

| Metric | Target | Measured to date | Current status |
| --- | --- | --- | --- |
| Room-temperature baseline (Run 1) | 3+ repeats to bound run-to-run spread | Logged, not yet published | Done, baseline runs logged |
| Freezer ladder, unheated (Run 2) | 4 setpoints x 3 repeats | No numbers published yet | In progress, warmer setpoints logged, cold end pending |
| Freezer ladder, thermostat (Run 3) | 4 setpoints x 3 repeats | No numbers published yet | In progress, hysteresis tuning under way |
| Freezer ladder, pre-heat (Run 4) | 4 setpoints x 3 repeats | No numbers published yet | Next, follows Run 3 tuning |
| Outdoor validation (Run 5) | 2+ runs per winter condition band, weather-tagged | No data, waiting on weather | Next, waiting on sustained sub-zero weather |
| Break-even analysis (Run 6) | Net recovered capacity quantified per strategy and setpoint | No numbers published yet | Pending, derived from Runs 2-4 |
| Published dataset | CSVs + protocol + plotting code in a public repo | Not yet published | Not yet published |

Freezer runs are under way; the plotted dataset is not published yet, nothing on this page
        reports measured numbers until the repeated runs and outdoor validation are complete.

## Troubleshooting & Lessons

- Every sensor read exactly 85.000 °C after wiring. That value is the DS18B20's power-on default, not a real temperature, the bus was up but conversions were failing because the pull-up was at the far end of a long harness. Fix: moved the 4.7 kΩ pull-up to the Pi end. Lesson: finger-test every sensor and log the serial-to-position map before taping anything into the bay.

- Sensors vanished mid-run at freezer temperatures. Parasite power over long cold leads dropped the bus under load. Fix: rewired to powered 3-wire mode (VDD to 3V3) and shortened stub lengths. Lesson: parasite power is for short bench runs, not for a metre of wire into a -30 °C box.

- The heater came on for a second during Pi boot. The GPIO floats until the OS configures it, and the MOSFET gate happily followed the float. Fix: the 10 kΩ gate pull-down from step 01. Lesson: hardware fails-off first, software safety second, the control loop should never be the only thing between a LiPo and an unattended heater.

- Condensation attacked the bay on pull-out. Taking a -20 °C bay into room air frosts it instantly, and frost inside foam insulation becomes water inside foam insulation. Fix: the whole bay goes into a sealed bag before it leaves the cold, and warms up inside the bag, which dovetails with the never-charge-cold rule, since the pack cannot charge until it has warmed anyway.

- Both INA228s answered on 0x40. Two identical breakouts, one default address, the bus scans were chaos until A0 on the heater monitor went to VS+ for 0x41. Lesson: run i2cdetect -y 1 after every wiring change, not just when something breaks.

## Safety & Canada Notes

## Status & Roadmap

- Done: heater pads and MOSFET driver benched with fails-off gate pull-down; 1-Wire sensor harness installed in powered mode with serial-to-position map; both INA228s addressed, shunt-calibrated per the datasheet, and cross-checked against the Fluke (reported bench status; no measured dataset published yet); logging service running under systemd with restart-on-failure; room-temperature baseline and first freezer runs at the warmer setpoints logged; fixed discharge load verified against design math.

- In progress: repeated runs across the full setpoint ladder; thermostat-control tuning (hysteresis band and setpoint); plotting tooling for the voltage-sag curves.

- Next: pre-heat-and-fly matrix runs; outdoor winter validation with weather tagging; the break-even analysis; publish the dataset and full protocol.

## Related Builds

- Thermal Search-and-Rescue Drone, the airframe whose LiPo packs are this rig's test subjects; the dataset tells it how much winter endurance it really has.

- Secure Robot-Fleet Updates, the sibling "Cold & Trust" build, tested in the same cold chamber for cold-boot and rollback behaviour.

- Canadian Defence Hardware Program, the program hub: all eleven builds, full BOMs, and the defence context this rig answers.

## Build Narrative: Phase by Phase

Phase 1: heater driver, fails-off first. Kapton heater pads driven by a logic-level N-MOSFET, with a 10 k pull-down on the gate so the heater cannot fire during Pi boot when the GPIO floats. Hardware fails-off first, software safety second: the control loop is never the only thing between a LiPo and an unattended heater.

Phase 2: temperature harness. Six DS18B20 sensors wired in powered 3-wire mode (parasite power was abandoned after sensors vanished mid-run on long cold leads), with the 4.7 k pull-up at the Pi end of the harness. Every sensor was finger-tested and its serial number mapped to a physical position before anything was taped into the bay.

Phase 3: power monitors. Two INA228 power monitors on the I2C bus, addressed 0x40 and 0x41 (A0 strapped to VS+ on the heater monitor after both breakouts answered on the default 0x40). Both were calibrated and cross-checked against the Fluke multimeter, and i2cdetect -y 1 runs after every wiring change.

Phase 4: logging service. A logging service under systemd with restart-on-failure records pack voltage, discharge and heater current, accumulated mAh, and the temperature channels against time. Room-temperature baselines and the first freezer runs at the warmer setpoints are already logged.

Phase 5: protocol and tooling. The run protocol covers 0, -10, -20, and -30 C setpoints with repeated runs per setpoint, thermostat hysteresis tuning, and plotting tooling for the voltage-sag curves. The deliverable is a clean public dataset of battery behaviour versus temperature, reproducible from the published protocol.

## What You Need

The rig is deliberately boring: a freezer, sensors, and discipline. The most important item is the protocol, not the parts.

| Category | Item | Notes |
| --- | --- | --- |
| Hardware | 6x DS18B20 temperature sensors | Powered 3-wire mode for cold runs; pull-up at the host end; serial-to-position map before taping anything down |
| Hardware | 2x INA228 power monitors | Pack voltage, current, and accumulated mAh; set distinct I2C addresses before wiring |
| Hardware | Kapton heater pads + N-MOSFET | Controlled warming with a hardware fails-off gate pull-down |
| Hardware | Chest freezer or a Canadian winter | The cold chamber; foam insulation for the battery bay |
| Hardware | Logging host + test packs | Pi or ESP32 from program stock; the LiPo packs under test come from the drone program |
| Software | 1-Wire, i2c-tools, Python | Sensor bus, bus scans after every wiring change, logging and analysis |
| Software | systemd, plotting tooling | Restart-on-failure logging; matplotlib-class tooling for the voltage-sag curves |
| Skills | Soldering, I2C debugging, basic electronics | MOSFET drive, pull-up placement, multimeter cross-checks |
| Accounts | None | No accounts or licenses required |

## Challenges and Lessons Learned

- Every sensor read exactly 85.000 C after wiring. That is the DS18B20 power-on default, not a temperature: conversions were failing because the pull-up sat at the far end of a long harness. Lesson: move the pull-up to the Pi end, and finger-test every sensor before taping it in.

- Sensors vanished mid-run at freezer temperatures. Parasite power over long cold leads dropped the bus under load. Lesson: parasite power is for short bench runs; cold runs get powered 3-wire mode and short stubs.

- The heater came on for a second during Pi boot. The GPIO floats until the OS configures it, and the MOSFET gate followed the float. Lesson: hardware fails-off first (the 10 k gate pull-down), software safety second.

- Condensation attacked the bay on pull-out. A -20 C bay into room air frosts instantly, and frost inside foam insulation becomes water inside foam insulation. Lesson: the bay goes into a sealed bag before leaving the cold and warms up inside it, which dovetails with the never-charge-cold rule.

- Both INA228s answered on 0x40. Two identical breakouts, one default address. Lesson: strap A0 for a distinct address and run i2cdetect -y 1 after every wiring change, not just when something breaks.

## What Is Next

- Repeated runs across the full setpoint ladder (0, -10, -20, -30 C) until each point has enough repeats to be trustworthy.

- Thermostat-control tuning: hysteresis band and setpoint behaviour for the heater pads.

- Pre-heat-and-fly matrix runs: how much energy does pre-heating cost versus what it buys in usable capacity.

- Outdoor winter validation with weather tagging, taking the rig out of the freezer and into the actual Toronto winter.

- The break-even analysis: heater energy versus recovered capacity, the number that decides whether cold-weather heating is worth it.

- Publish the dataset and the full protocol so anyone can reproduce the curves.

## Frequently Asked Questions

**Q: How do I fix 'Every sensor read exactly 85.000 °C after wiring.'?**

A: That value is the DS18B20's power-on default, not a real temperature, the bus was up but conversions were failing because the pull-up was at the far end of a long harness. Fix: moved the 4.7 kΩ pull-up to the Pi end. Lesson: finger-test every sensor and log the serial-to-position map before taping anything into the bay.

**Q: How do I fix 'Sensors vanished mid-run at freezer temperatures.'?**

A: Parasite power over long cold leads dropped the bus under load. Fix: rewired to powered 3-wire mode (VDD to 3V3) and shortened stub lengths. Lesson: parasite power is for short bench runs, not for a metre of wire into a -30 °C box.

**Q: How do I fix 'The heater came on for a second during Pi boot.'?**

A: The GPIO floats until the OS configures it, and the MOSFET gate happily followed the float. Fix: the 10 kΩ gate pull-down from step 01. Lesson: hardware fails-off first, software safety second, the control loop should never be the only thing between a LiPo and an unattended heater.

**Q: How do I fix 'Condensation attacked the bay on pull-out.'?**

A: Taking a -20 °C bay into room air frosts it instantly, and frost inside foam insulation becomes water inside foam insulation. Fix: the whole bay goes into a sealed bag before it leaves the cold, and warms up inside the bag, which dovetails with the never-charge-cold rule, since the pack cannot charge until it has warmed anyway.

**Q: How do I fix 'Both INA228s answered on 0x40.'?**

A: Two identical breakouts, one default address, the bus scans were chaos until A0 on the heater monitor went to VS+ for 0x41. Lesson: run i2cdetect -y 1 after every wiring change, not just when something breaks.

## Cite This Page

**Q: Citation formats**

A: Plain text
