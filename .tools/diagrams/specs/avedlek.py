from svgdiagram import Bars, Flow, Sequence, Stack, Timeline

PAGE = "work/defence/avedlek-northern-groundstation.html"

architecture = (
    Flow("avedlek-architecture", "Ground station software architecture",
         "Public orbital data and three frame sources (the simulated AVD-SAT, a real radio, and the SatNOGS "
         "network) feed one decoder. Orbit prediction gives every frame its expected elevation, Doppler and "
         "signal strength; integrity checks quarantine frames that could not have come from the satellite; "
         "telemetry goes to TimescaleDB, the analytics models score it, and Grafana shows it all. Quarantined frames are "
         "stored too, flagged, but never become telemetry.", cols=4)
    .node("tle", "Public orbital data", "CelesTrak TLEs every 6 h", at=(0, 0), color="grey")
    .node("sim", "Virtual ground station", "AVD-SAT physics, software radio", at=(0, 1), color="purple")
    .node("rf", "Real radio", "RTL-SDR, GNU Radio, Direwolf", at=(0, 2), color="orange")
    .node("net", "SatNOGS network", "frames from stations worldwide", at=(0, 3), color="orange")
    .node("orb", "Orbit prediction", "Skyfield SGP4: passes, look angles, Doppler", at=(1, 0), color="blue")
    .node("dec", "Telemetry decoder", "AX.25, beacon formats in YAML", at=(1, 1), span=2, color="cyan")
    .node("chk", "Integrity checks", "horizon, Doppler, SNR, replay, clock", at=(1, 3), color="red")
    .node("db", "TimescaleDB", "frames, telemetry, passes, findings", at=(2, 1), span=2, color="green")
    .node("ai", "Analytics", "limits, context, relations, Isolation Forest", at=(2, 3), color="yellow")
    .node("dash", "Ground station dashboard", "Grafana: track, passes, telemetry, findings", at=(2, 0), color="blue")
    .edge("tle", "orb").edge("sim", "dec").edge("rf", "dec").edge("net", "dec")
    .edge("orb", "dec", "expected el, Doppler, SNR")
    .edge("dec", "chk").edge("dec", "db")
    .edge("db", "ai", "telemetry; findings back")
    .edge("db", "dash")
)

station = (
    Flow("avedlek-station", "Physical receive station",
         "The physical part: a V-dipole with an LNA at the antenna, short coax through a lightning arrestor to an "
         "RTL-SDR on a Raspberry Pi, which runs the SatNOGS client or Gqrx and Direwolf, and sends frames to the "
         "Docker stack. A rotator and Yagi are an optional upgrade driven by the tracker service.", cols=4)
    .node("ant", "V-dipole antenna", "16.5 cm arms at 120 deg, horizontal, N-S", at=(0, 0), color="orange")
    .node("lna", "LNA at the antenna", "powered over the coax (bias-tee)", at=(0, 1), color="orange")
    .node("arr", "Coax + arrestor", "3-5 m, bonded to building ground", at=(0, 2), color="grey")
    .node("sdr", "RTL-SDR Blog V4", "USB 3 on a short extension", at=(0, 3), color="blue")
    .node("pi", "Raspberry Pi 5", "SatNOGS client, or Gqrx + Direwolf", at=(1, 3), color="green")
    .node("dock", "Docker stack", "orbit, decoder, analytics, Grafana", at=(1, 2), color="cyan")
    .node("trk", "Tracker service", "Hamlib: rotator, and Doppler tuning of Gqrx", at=(1, 1), color="purple")
    .node("rot", "Rotator + Yagi (optional)", "points the antenna during passes", at=(1, 0), color="purple")
    .edge("ant", "lna").edge("lna", "arr").edge("arr", "sdr").edge("sdr", "pi")
    .edge("pi", "dock", "KISS frames")
    .edge("dock", "trk", "next pass")
    .edge("trk", "rot", "az / el")
)

radio = (
    Flow("avedlek-radio", "The software radio, frame by frame",
         "Every simulated frame goes through a real modulation and demodulation chain: AX.25 with a CRC, HDLC "
         "framing, NRZI and 1200 baud AFSK, then FM shifted by the true Doppler and buried in noise at the "
         "link-budget SNR. The receiver removes the predicted Doppler, filters the channel and demodulates. A frame "
         "counts only if its CRC checks.", cols=4)
    .node("b", "Beacon", "32 bytes from the spacecraft model", at=(0, 0), color="purple")
    .node("ax", "AX.25 + CRC-16", "HDLC flags, bit stuffing, NRZI", at=(0, 1), color="purple")
    .node("afsk", "AFSK 1200 baud", "1200 / 2200 Hz tones", at=(0, 2), color="purple")
    .node("fm", "FM + true Doppler", "up to about +/-10 kHz at 437.5 MHz", at=(0, 3), color="orange")
    .node("noise", "Channel noise", "SNR from range: about 9 to 15 dB", at=(1, 3), color="grey")
    .node("corr", "Remove predicted Doppler", "from the orbit, with a per-pass error", at=(1, 2), color="blue")
    .node("disc", "15 kHz filter + FM discriminator", "also measures SNR and leftover offset", at=(1, 1), color="blue")
    .node("dem", "Tone detection + HDLC", "CRC must check, or the frame is lost", at=(1, 0), color="green")
    .edge("b", "ax").edge("ax", "afsk").edge("afsk", "fm").edge("fm", "noise")
    .edge("noise", "corr").edge("corr", "disc").edge("disc", "dem")
)

integrity = (
    Flow("avedlek-integrity", "Is this frame really from the satellite?",
         "Small-satellite telemetry is rarely authenticated, so anyone with a transmitter can forge or replay it. "
         "Each frame is checked against physics a ground transmitter cannot easily fake. A frame that fails any "
         "check is stored and flagged but kept out of the telemetry, so a forged alarm cannot trigger a false one.", cols=4)
    .node("fr", "Decoded frame", "with measured SNR and carrier offset", at=(0, 0), color="cyan")
    .node("hz", "Above the horizon?", "predicted elevation at receive time", at=(0, 1), color="yellow")
    .node("dp", "Doppler fits the orbit?", "leftover offset under 1.5 kHz", at=(0, 2), color="yellow")
    .node("sn", "Signal plausible?", "SNR under link budget + 12 dB", at=(0, 3), color="yellow")
    .node("rp", "New counter, steady clock?", "no replayed counter, uptime tracks ground time", at=(1, 3), color="yellow")
    .node("ok", "Accepted", "telemetry stored, models score it", at=(1, 0), span=3, color="green")
    .node("q", "Quarantined", "kept with a SHA-256, integrity finding raised, never becomes telemetry", at=(2, 0), span=4, color="red")
    .edge("fr", "hz").edge("hz", "dp").edge("dp", "sn").edge("sn", "rp").edge("rp", "ok", "all pass")
    .edge("rp", "q", "any check fails")
)

contact = (
    Sequence("avedlek-pass", "One pass, end to end",
             "What happens during a satellite pass at a real station: the orbit service predicts it, the tracker "
             "points and tunes, the radio chain decodes frames, the decoder checks and stores them, and the analytics "
             "service scores the new telemetry within a minute.",
             [("orbit", "Orbit service", "blue"), ("trk", "Tracker", "purple"), ("radio", "Radio chain", "orange"),
              ("dec", "Decoder", "cyan"), ("ai", "Analytics", "yellow"), ("op", "Operator", "green")])
    .msg("orbit", "trk", "next pass: AOS, TCA, LOS, max elevation")
    .msg("trk", "radio", "every second: az/el and carrier + Doppler")
    .msg("radio", "dec", "AX.25 frames (KISS)")
    .msg("dec", "dec", "parse, predict, integrity checks")
    .msg("dec", "ai", "accepted telemetry")
    .msg("ai", "op", "findings with the reason, on the dashboard")
    .msg("trk", "trk", "LOS: park the antenna", dashed=True)
)

sites = (
    Bars("avedlek-sites", "Passes per satellite per day, by site",
         "Computed with tools/compare_sites.py from current CelesTrak orbits of 40 low-orbit weather satellites, "
         "over two days from 2026-11-22, minimum elevation 5 degrees.", unit="", max_value=12)
    .bar("Toronto, 43.8 N", 4.69, "", "blue")
    .bar("Ottawa, 45.4 N", 4.72, "", "blue")
    .bar("Iqaluit, 63.7 N", 7.41, "", "cyan")
    .bar("Inuvik, 68.4 N", 8.32, "1.8x Toronto", "cyan")
    .bar("Alert, 82.5 N", 11.72, "2.5x Toronto", "green")
)

stack = (
    Stack("avedlek-stack", "Software stack",
          "Five layers, all open source: the radio, orbits, the decoder and its checks, storage, and the "
          "analytics and dashboard.")
    .layer("Radio", ["RTL-SDR\nV-dipole + LNA", "GNU Radio 3.10\nDoppler receiver", "Direwolf\n1k2 AFSK modem",
                     "SatNOGS client\nnetwork station", "Software radio\nNumPy, simulator"], "orange")
    .layer("Orbits", ["CelesTrak\npublic TLEs", "Skyfield + SGP4\npasses, Doppler", "Hamlib\nrotator, radio"], "blue")
    .layer("Decoding", ["AX.25 + KISS\nown code", "Beacon formats\nYAML", "Integrity checks\n5 checks"], "cyan")
    .layer("Storage", ["PostgreSQL 16\n+ TimescaleDB", "Hypertables\ncompression, roll-ups"], "green")
    .layer("Analytics and display", ["scikit-learn\nIsolation Forest", "Context + relation\nmodels", "Battery trend\nforecast",
                                     "Grafana 11\ndashboard"], "yellow")
)

timeline = (
    Timeline("avedlek-timeline", "Build status",
             "The software, the virtual station and the evaluation are done and run end to end in Docker; the "
             "physical receive station is next, then real passes and SatNOGS.")
    .phase("Software", "5 services, 43 tests", "done")
    .phase("Virtual station", "radio, faults, spoofer", "done")
    .phase("Evaluation", "5 sites, 7 scenarios", "done")
    .phase("Physical station", "antenna, LNA, SDR, Pi", "doing")
    .phase("Real passes", "SatNOGS, own decodes", "next")
)


ttd = (
    Bars("avedlek-ttd", "Mean hours to detect a fault, by station layout",
         "Mean time from a fault starting to the first finding, over five fault types and six start times each, "
         "with every frame through the full software radio (tools/evaluate.py --rf --starts 6).", unit="h")
    .bar("Ottawa", 4.71, "5 passes/day", "blue")
    .bar("Toronto", 3.45, "6 passes/day", "blue")
    .bar("Inuvik", 2.06, "10 passes/day", "cyan")
    .bar("Inuvik + Toronto", 1.18, "16 passes/day", "purple")
    .bar("Alert", 0.65, "15 passes/day", "green")
)

DIAGRAMS = [architecture, station, radio, integrity, contact, sites, ttd, stack, timeline]
