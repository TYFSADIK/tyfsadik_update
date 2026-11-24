from svgdiagram import Bars, Flow, Sequence, Stack, Timeline

PAGE = "work/defence/surveillance-of-space.html"

platform = (
    Flow("sos-platform", "From public data to a protected catalogue",
         "Every element set ever fetched is kept, so the catalogue has a history. Each ingest is followed by the "
         "derived products: the GEO belt, manoeuvres, and a conjunction screening run, all in PostgreSQL/PostGIS.", cols=4)
    .node("ct", "CelesTrak", "GP element sets, SATCAT, every 2 hours", at=(0, 0), color="grey")
    .node("in", "Ingest", "respects the update cycle; logs refusals", at=(0, 1), color="blue")
    .node("db", "PostgreSQL / PostGIS", "every element set, catalogue, runs, history", at=(0, 2), color="purple")
    .node("api", "API + 3D viewer", "CesiumJS: positions, orbits, metadata, freshness", at=(0, 3), color="yellow")
    .node("sgp", "SGP4 propagation", "vectorised, about 2.5 million positions a second", at=(1, 1), color="blue")
    .node("cj", "Conjunction screening", "k-d tree, linear pre-filter, SGP4 refinement, probability", at=(1, 2), color="red")
    .node("gf", "Grafana", "catalogue health, freshness, conjunctions, Canadian GEO", at=(1, 3), color="green")
    .node("cal", "Uncertainty model", "measured against operator orbits and NASA", at=(2, 1), color="orange")
    .node("opt", "Optical sensor", "camera on a tracking mount, independent positions", at=(2, 2), color="orange")
    .edge("ct", "in").edge("in", "db").edge("db", "api").edge("db", "cj", exit="b", enter="t")
    .edge("sgp", "cj").edge("cj", "gf").edge("cal", "sgp", exit="t", enter="b")
)

screening = (
    Flow("sos-screening", "How the conjunction screen works",
         "The same idea as operational screening, sized for a laptop: cheap filters first, SGP4 itself last.", cols=4)
    .node("p", "Propagate everything", "every 20 s across the window", at=(0, 0), color="blue")
    .node("k", "k-d tree", "pairs closer than 5 km plus half a step at 16 km/s", at=(0, 1), color="blue")
    .node("l", "Linear pre-filter", "closest approach within the step from relative motion", at=(0, 2), color="yellow")
    .node("r", "SGP4 refinement", "bounded minimisation of the true separation", at=(0, 3), color="purple")
    .node("c", "Co-located?", "relative speed under 10 m/s: docked or formation", at=(1, 3), color="grey")
    .node("pc", "Probability", "measured covariance, encounter plane, hard-body circle", at=(1, 2), color="red")
    .edge("p", "k").edge("k", "l").edge("l", "r").edge("r", "c", exit="b", enter="t").edge("c", "pc")
)

optical = (
    Sequence("sos-optical", "One frame of the GEO belt",
             "In the rehearsal the satellites are drawn where their operators say they are; the pipeline never sees that truth.",
             [("cam", "Camera", "grey"), ("det", "Detection", "blue"), ("ast", "Astrometry", "purple"),
              ("sub", "Star subtraction", "yellow"), ("cor", "Correlation", "red"), ("cat", "Catalogue", "green")])
    .msg("cam", "det", "2 s frame: round stars, short satellite streaks")
    .msg("det", "ast", "stars matched to the catalogue")
    .msg("ast", "sub", "cubic plate solution, 1.4 arcsec RMS")
    .msg("sub", "cor", "streaks measured at mid-exposure")
    .msg("cat", "cor", "predicted positions", dashed=True)
    .msg("cor", "cat", "match, uncorrelated track, or manoeuvre flag")
)

stack = (
    Stack("sos-stack", "Software stack",
          "Open source throughout; the screener, uncertainty model, GEO characterisation and optical pipeline are my own.")
    .layer("Data", ["CelesTrak\nGP + SATCAT", "SupGP\noperator orbits", "NASA\nISS ephemeris", "SOCRATES\nvalidation"], "grey")
    .layer("Astrodynamics", ["SGP4\nvectorised", "Skyfield\nframes, sites", "SciPy\nk-d tree, minimise"], "blue")
    .layer("Store", ["PostgreSQL 16\nhistory", "PostGIS\nencounter geography"], "purple")
    .layer("Products", ["Conjunctions\n+ probability", "GEO belt\ncharacterisation", "Manoeuvres\nfrom history"], "red")
    .layer("View", ["FastAPI", "CesiumJS\n3D globe", "Grafana\ncatalogue health"], "green")
)

timeline = (
    Timeline("sos-timeline", "Build status",
             "The platform runs end to end in Docker on live public data and is validated; the optical sensor is "
             "rehearsed on synthetic frames and is the next physical step.")
    .phase("Catalogue + history", "CelesTrak, PostGIS", "done")
    .phase("Screening + validation", "against SOCRATES", "done")
    .phase("Uncertainty, GEO", "measured", "done")
    .phase("Optical sensor", "lens, camera, mount", "doing")
    .phase("Real observations", "Gaia astrometry", "next")
)

iss = (
    Bars("sos-iss", "The ISS's public element set against NASA's ephemeris (km)",
         "One element set propagated with SGP4, compared with the trajectory NASA publishes. Almost all of the error "
         "is along the track: a small mismatch in the predicted decay that grows faster than linearly.", unit="km")
    .bar("0.5 days after epoch", 0.16, "", "green")
    .bar("1.0 days after epoch", 0.79, "", "green")
    .bar("2.0 days after epoch", 0.30, "", "green")
    .bar("3.0 days after epoch", 0.98, "", "green")
    .bar("5.0 days after epoch", 2.91, "", "yellow")
    .bar("7.0 days after epoch", 12.72, "", "yellow")
    .bar("10.0 days after epoch", 38.03, "", "red")
    .bar("14.0 days after epoch", 85.39, "", "red")
)

DIAGRAMS = [platform, screening, iss, optical, stack, timeline]
