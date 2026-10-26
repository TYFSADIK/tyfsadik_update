# Passive Acoustic Drone Detector

Written by [Taki Sadik](../../about.html) · Last updated 2026-10-22 · Status: Building · 28 min read

A MEMS microphone array on a Raspberry Pi that listens for the harmonic comb of drone rotors, rejects birds and aircraft, and estimates direction of arrival by beamforming. The sensing front end emits nothing at all; only network reporting leaves the box.

## Overview

NRC and DRDC have built a counter-drone detection system that picks up the
        signature of a drone's rotating propellers without emitting any radio signal that could
        reveal its own location. This build is that idea at hobby scale: a ReSpeaker-class 4-mic
        USB array on a Raspberry Pi 5 that does nothing but listen. The microphone front end emits no RF, so the sensing itself reveals no radio signature; reporting detections over the network still transmits, so the node is RF-quiet, not RF-invisible, and a powered Pi can be found by other means.

Small multirotor drones announce themselves acoustically whether they want to or not. Each
        rotor spins at a fixed rate per flight phase, producing a fundamental blade-pass
        frequency in the ~100-500 Hz band plus a comb of evenly spaced harmonics that
        persists as long as the motors run. Birds flap (intermittent, broadband), fixed-wing
        aircraft drone on much lower frequencies at much greater distance, and traffic noise is
        broadband and unstructured. That harmonic comb is a fingerprint, and it is what this
        sensor keys on.

The context is the same one driving the whole program: Canada's
        Defence Drone Initiative (launched July 23, 2026) and the Army MINERVA
        challenges both assume small drones are cheap, common, and hard to see. A receive-only
        acoustic node is the cheapest possible layer of counter-drone awareness, it costs about
        as much as a dinner out, runs off a USB power bank, and feeds its detections into the same
        common operating picture as my passive radar node.

## Proof of Build

What each part of the photo does:

- Circular 4-mic MEMS array: four microphones at known positions. A drone's sound reaches each one at a slightly different time, and those tiny delays give its direction.

- Raspberry Pi: runs the DSP chain: it filters the audio, looks for rotor harmonics, and estimates the direction of arrival.

- Oscilloscope: shows the four mic channels side by side, so I can confirm they are sampled in sync before trusting any direction estimate.

- Laptop polar plot: the direction-of-arrival tracker. In the photo it is locked onto rotor harmonics near 660 Hz from one of my own drones.

## Bill of Materials

| Item | What I used | Est. US$ |
| --- | --- | --- |
| Microphone array | ReSpeaker-class 4-mic USB array | 70-100 |
| Compute | Raspberry Pi (Pi 5 4 GB from program stock) | ~85 |
| Enclosure | IP65 box, cable glands, mounting hardware | 20-40 |
| Storage | High-endurance microSD / NVMe HAT (shared workshop stock) | - |
| Power | Official 27 W Pi 5 supply or USB-C PD power bank | 25-55 |

Everything is already on the bench. Total build cost lands around US$200-280 depending on
        the power option, the Pi, storage, and power gear come from the shared Phase 0 workshop
        stock bought for the whole program.

## Wiring & Connections

There is deliberately little to wire, no SDR front end, no antennas, no RF anything. The
        whole node is the array, the Pi, and power; everything else is network.

| From | To | Cable or interface | Notes |
| --- | --- | --- | --- |
| 4-mic MEMS array | Pi 5 USB-A port | USB-C to USB-A cable (direct) | Enumerates as a USB Audio Class device; plug directly into the Pi, never through an unpowered hub, brownouts corrupt audio streams silently |
| Pi 5 | Official 27 W supply / PD power bank | USB-C PD | Must negotiate the 5 V / 5 A profile; check for undervoltage with vcgencmd get_throttled |
| Pi 5 | Bench laptop | Ethernet (gigabit) | SSH for development, scp for pulling test recordings, polar-plot dashboard over LAN |
| Pi 5 | MQTT broker (homelab) | Wi-Fi or Ethernet LAN | Detections only; node buffers to local disk when the link drops and forwards on reconnect |
| Mic array | Bench stand / enclosure lid | 1/4" thread + standoffs | Mounted clear of the bench so reflections off the tabletop do not smear the DoA solution |
| Pi 5 | Laptop acoustic view | SSH + X-forwarded matplotlib / web dashboard | The four-channel scope-style view in the bench photo is rendered from the captured USB stream, not from probe leads, there is nothing analog to probe |

## Architecture

4-mic MEMS array(USB audio)

CaptureALSA / arecord4 channels synced

STFT spectrogramsper channel

Harmonic-comb detectorfundamental ~100-500 Hzplus spaced harmonics

Classifierdrone vs bird vs aircraft(thresholds / SVM)

DoA beamformingGCC-PHAT / SRP-PHATazimuth estimate

Tracker + polar plotazimuth vs time

MQTT publishersigned detections

Common operating picturefused with passive radar

Figure 1: capture, spectrogram, harmonic-comb detection, classification, beamforming, and reporting. Everything runs on the Pi; only signed detections leave the node.

The two analysis branches share one spectrogram stage. Detection and classification work
        on the summed audio (best signal-to-noise), while direction of arrival works on the phase
        differences between channels. Raw audio is processed in memory in short windows
        and discarded, only detection events with azimuth, timestamp, and confidence are kept.

## Why PHAT Weighting Works on Rotor Combs

GCC-PHAT (generalized cross-correlation with phase transform) is doing something clever
        that maps directly onto how a drone sounds. A rotor comb is a set of narrowband peaks:
        one or two harmonics are usually much louder than the rest. If you cross-correlate two
        mic channels directly, those loud peaks dominate the correlation, and the delay estimate
        locks onto the loudest tone instead of the wavefront as a whole, including its echoes
        off the ground and nearby objects.

1 s window(4 channels)

FFTper channel

Cross-spectrum(R = SIG times conj of REF)

PHAT whitening(R divided by its magnitude)

Inverse FFT(cross-correlation)

Peak lag(time delay estimate)

SRP-PHAT scan(steer candidate delaysper azimuth, max energy)

Figure 2: the GCC-PHAT delay pipeline. PHAT whitening is the key step: after dividing by the magnitude, every frequency bin contributes equally to the correlation, so the broadband wavefront wins over the loudest single harmonic.

### The whitening intuition

Think of each frequency bin as a voter on the question "which channel heard it first".
          Without whitening, the loud bins get a thousand votes each and the quiet bins get one:
          the election is decided by whoever is shouting. PHAT divides the cross-spectrum by its
          own magnitude, which gives every bin exactly one vote. Now the verdict comes from the
          one thing all the frequencies share, the geometry of the wavefront crossing the
          array, instead of from the accidental loudness of one harmonic. That is why the bench
          track in the photo locks onto the comb containing a strong spectral line near 660 Hz as a direction rather than
          locking onto that line as a tone.

SRP-PHAT (steered-response power with phase transform) extends the same idea to bearing.
        For each candidate azimuth, I compute what time delay each mic should see from
        that direction (given the measured array geometry below), steer the channels by those delays, and
        combine them with steered delay-and-sum into a steered power estimate. The azimuth whose delays line up best wins. The allowed correlation lag range is derived from the measured mic spacing: the maximum physically possible delay is the mic spacing divided by the speed of sound, and step 08 restricts the GCC-PHAT search to that window before picking a peak, because a lag outside it would be a bug, not a bearing.

## Array Geometry

The whole bearing estimate rests on four mics in a measured geometry. Microphone
        positions and channel mapping on this installed board were measured directly (tape measure on
        the board plus the tap-test map from step 02); published figures for one ReSpeaker variant
        do not transfer to another, and no geometry from a datasheet is used unmeasured here. The
        tap-test map from step 02 is the ground truth for which channel is which; the datasheet is
        only the starting guess.

Figure 3: illustration of a generic circular 4-mic array layout, not a measured plot of this board: four mics in a circle with the channel map from the tap test. A sound arriving from the bearing shown reaches ch1 first and ch3 last; GCC-PHAT turns that few-microsecond stagger into an azimuth. The installed board's actual mic positions must be measured, not taken from a datasheet figure.

## How I Built It

**Q: Build steps (10 steps with code; expand to read)**

A: The ReSpeaker-class 4-mic USB array enumerates on the Pi 5 as a standard USB Audio
              Class device, no vendor drivers needed, which is exactly why I picked this class of
              hardware. The chain runs at the documented 16 kHz maximum sample rate of the
              ReSpeaker Mic Array v2.0 (XMOS XVF-3000); no vendor 48 kHz raw four-channel firmware
              was found for this board, so 16 kHz is the honest operating point, giving an 8 kHz
              Nyquist that covers the rotor comb band. Some firmware variants expose 6
              channels (4 mics + 2 playback loopback), I capture 4 and ignore the loopback pair.

## Testing & Metrics

Test targets are my own drones and recorded samples only, never other people's aircraft.
        Every run logs conditions (wind, background noise, drone model, throttle state, distance)
        so results are comparable over time. Results stay unpublished until the run count is
        honest; everything below is protocol and targets, not measurements.

### Test Runs

Setup: array on the bench stand, speaker playing a recorded drone track at measured azimuths (0, 45, 90, ... 315 degrees, by protractor, ~2 m). Procedure: 30 seconds per position, tracker logging. Metric: reported azimuth vs. known bearing, per position.

Setup: my quad hovering at a series of measured distances along a line of sight, in quiet suburban conditions. Procedure: repeated hover runs per distance, alternating direction. Metric: detection yes/no per run; first-detection distance on approach runs.

Setup: the quad flying past the node at a fixed altitude and offset, logging its own GPS track. Procedure: repeated passes at different speeds. Metric: track continuity (fraction of flight with a live track) and DoA error against the true bearing computed from the drone's GPS log.

Setup: node running in ordinary environments with no drone present, park ambience, road traffic, birds, and a gas lawnmower at measured distances. Procedure: timed sessions per source. Metric: false alarms per hour, by source type.

Setup: node on power-bank power, running unattended. Procedure: continuous operation with health logging (CPU, temperature, memory, outbox depth). Metric: uptime, restart count, memory growth, battery runtime.

Setup: this node and the passive radar node pointed at the same airspace during a T3-style fly-past. Procedure: both publish to the common operating picture. Metric: time from detection to fused track, and agreement between the acoustic azimuth and the RF track.

### Targets & Current Status

| Metric | Target | Current status |
| --- | --- | --- |
| Bench DoA error (T1) | Sector-level agreement with known bearings, accurate enough to cue a camera or second sensor | In progress, calibration rig works, full 8-position series not yet logged |
| Detection envelope (T2) | A clear, repeatable detection range against my own quads in quiet conditions | In progress, bench detection confirmed, outdoor run series not yet done |
| Track continuity (T3) | A continuous track through a fly-past, with DoA error bounded against the drone's GPS flight log as a reference | In progress, tracker locks on the bench; fly-past series not yet done |
| False-alarm rate (T4) | Low enough that a human reviewing the alert queue is not numbed by noise; measured per source, not assumed | In progress, lawnmower and traffic sessions collected, more sources pending |
| Long-soak stability (T5) | Multi-day unattended uptime with no manual intervention | In progress, service hardening done, soak runs not yet logged |
| Fusion latency (T6) | Acoustic and RF tracks fused into one track in the common operating picture | Next, waiting on the passive radar node's reporting feed |

The bench rig detects and tracks rotor harmonics today (see the photo above), but no
        field-range numbers are published here yet, they land only after the T2/T3 run series,
        not from a handful of anecdotes.

## Troubleshooting & Lessons

- The capture device moved after a reboot. hw:1,0 became
          hw:2,0 and the detector captured silence from the wrong device. Fix: resolve
          the array by name from /dev/snd/by-id/ at startup and fail loudly if it is
          absent, instead of opening whatever card 1 happens to be.

- Input overflows corrupted analysis windows. Early versions ran the STFT
          inside the audio callback; one slow frame stalled the stream and PortAudio dropped
          blocks mid-window, producing spectrograms with invisible gaps. Fix: the callback now only
          copies to a queue, a worker thread does the DSP, and any overflow invalidates the run.
          Lesson: never do arithmetic in a real-time callback.

- Wind looked like a drone. Strong gusts raised the sub-100 Hz floor and
          the peak picker found phantom "fundamentals" in the rumble. Fix: an 80 Hz high-pass
          before the STFT, the adaptive per-bin noise floor, and a foam windscreen on the array.
          Verified with a bench fan aimed at the mics, gusty, but no combs.

- A gas lawnmower passed every threshold. It is a real engine with real
          harmonics, persistence and spacing alone could not reject it. Fix: lawnmower sessions
          went into the training set as hard negatives, and the SVM (with
          class_weight="balanced") learned the differences in harmonic count and
          bandwidth. It remains the hardest negative source; helicopters are the next one.

- The azimuth was mirrored. Bench calibration showed tracks moving
          clockwise on the plot while the source moved counterclockwise, two channels were swapped
          relative to the assumed geometry. Fix: the tap-test channel map from step 02 is now
          printed at startup and asserted against the config, and the speaker-at-known-bearing
          test (T1) runs after any hardware change. Lesson: calibrate the geometry with sound,
          not with the datasheet.

## Legal & Safety Notes

## Status & Roadmap

- Done: array running its documented 16 kHz firmware; per-channel capture verified with arecord and the tap-test map; channel sync confirmed by cross-correlation; streaming capture loop with overflow handling; STFT + adaptive noise floor + harmonic-comb detector running on the Pi; GCC-PHAT/SRP-PHAT polar-plot tracker tracking my own drones on the bench (photo above); systemd service with restart and NTP wait; signed MQTT event schema defined.

- In progress: classifier training set (own drones + negative sources, split by session); SVM tuning against the threshold baseline; T1 bench azimuth calibration series; negative-source false-alarm sessions (T4).

- Next: outdoor T2/T3 run series for detection envelope and tracking accuracy; long-soak runs (T5); IP65 enclosure and power-bank field kit; signed MQTT feed into the common operating picture and the T6 fusion dry run with the passive radar node.

## Related Builds

- Canadian Defence Hardware Program, the program hub; this node is part of the counter-drone layer.

- Sky: Passive Aerial Early-Warning Node, the other receive-only air sensor; its RF tracks fuse with this node's acoustic tracks.

- Counter-Drone Sensor Fusion Simulator, the simulation sibling where acoustic + passive-radar fusion logic gets exercised.

- Multi-Domain Common Operating Picture, where this node's signed MQTT detections end up.

## Build Narrative: Phase by Phase

Phase 1: array bringup. A ReSpeaker-class 4-mic USB array on a Raspberry Pi 5, running the documented 16 kHz firmware (no 48 kHz raw four-channel firmware was found for this board). Per-channel capture was verified with arecord and a tap-test map, and channel synchronization was confirmed by cross-correlation. The array is resolved by name from /dev/snd/by-id/ at startup after an early lesson where hw:1,0 became hw:2,0 across a reboot and the detector captured silence from the wrong device.

Phase 2: streaming capture loop. The audio callback copies to a queue and a worker thread does the DSP; any overflow invalidates the run. This came from the hard lesson that running the STFT inside the callback stalled the stream and dropped blocks mid-window, leaving invisible gaps in the spectrograms.

Phase 3: harmonic-comb detector. The detection chain is STFT plus an adaptive per-bin noise floor plus harmonic-comb matching against the rotor harmonic comb (candidate fundamental band ~100-500 Hz for my quads, an engineering choice, not a universal drone signature). An 80 Hz high-pass ahead of the STFT and a foam windscreen keep gusts out of the detector.

Phase 4: bearing by GCC-PHAT. GCC-PHAT/SRP-PHAT across the mic pairs feeds a polar-plot tracker that follows bearing over time. Bench calibration with a speaker at a known bearing is the ground truth for geometry, after an early session where two swapped channels mirrored the azimuth on the plot.

Phase 5: classifier. An SVM with class_weight=balanced learns drone versus negative sources from labelled sessions split by session. The gas lawnmower earned its place in the training set as the hardest negative: a real engine with real harmonics that persistence and spacing alone could not reject.

Phase 6: services and reporting. The detector runs under systemd with restart and an NTP wait, and every detection is emitted as a signed MQTT event in the program's common schema.

## What You Need

The cheapest counter-drone layer in the program: about the cost of a dinner out, running off a USB power bank. The expensive part is the labelled training data, which you collect yourself.

| Category | Item | Notes |
| --- | --- | --- |
| Hardware | 4-mic USB array | ReSpeaker-class, 16 kHz documented maximum; resolve it by name, never by card index |
| Hardware | Raspberry Pi 5 + USB power bank | Streaming capture, STFT, and the SVM all run on the node |
| Hardware | Foam windscreen, IP65 enclosure | Wind rejection at the mic; the enclosure is the T5 field-kit item |
| Software | ALSA, Python numpy/scipy | Capture and the STFT + GCC-PHAT pipeline |
| Software | scikit-learn | SVM classifier with balanced class weights, trained on labelled sessions |
| Software | systemd, mosquitto | Service supervision with NTP wait, signed MQTT detection events |
| Skills | DSP basics, Linux audio | Reading spectrograms, understanding beamforming geometry, real-time capture discipline |
| Accounts | None | No accounts or licenses required for a passive microphone array |

## Challenges and Lessons Learned

- The capture device moved after a reboot. hw:1,0 became hw:2,0 and the detector captured silence from the wrong card. Lesson: resolve by name from /dev/snd/by-id/ at startup and fail loudly if the array is absent.

- Input overflows corrupted analysis windows. Running the STFT inside the audio callback stalled the stream and dropped blocks mid-window. Lesson: never do arithmetic in a real-time callback; the callback copies, a worker thread computes, and overflows invalidate the run.

- Wind looked like a drone. Strong gusts raised the sub-100 Hz floor and the peak picker found phantom fundamentals in the rumble. Lesson: high-pass before detection, adapt the noise floor per bin, and verify with a bench fan aimed at the mics, gusty but no combs.

- A gas lawnmower passed every threshold. It is a real engine with real harmonics. Lesson: hard negatives go into the training set, and the SVM with balanced weights learns harmonic count and bandwidth where simple thresholds cannot. Helicopters are the next hard negative.

- The azimuth was mirrored. Tracks moved clockwise while the source moved counterclockwise, two channels swapped relative to the assumed geometry. Lesson: calibrate geometry with sound (speaker at a known bearing), not with the datasheet; print and assert the tap-test channel map at startup.

## What Is Next

- Outdoor T2 and T3 run series: measured detection envelope and tracking accuracy in real air, not the bench.

- Negative-source false-alarm sessions (T4): lawnmower, helicopters, traffic, and weather as scored runs.

- Long-soak runs (T5) with the IP65 enclosure and power-bank field kit.

- Signed MQTT feed into the common operating picture, fused with the passive radar node's tracks.

- The T6 fusion dry run with the passive radar node: two receive-only sky sensors scoring the same targets.

## Cite This Page

**Q: Citation formats**

A: Plain text
