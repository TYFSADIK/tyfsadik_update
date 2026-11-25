from svgdiagram import Bars, Flow, Sequence, Stack, Timeline

PAGE = "work/defence/multi-source-intelligence-fusion.html"

platform = (
    Flow("cjim-platform", "From five sources to a reviewed report",
         "Five independent sources stream into Redpanda. vLLM reads the free text into structured observations; the "
         "fuser removes copies, corrects clocks, groups observations into events and scores them; vLLM writes a cited "
         "summary, a checker verifies every sentence, and an analyst approves or rejects it.", cols=4)
    .node("src", "Five sources", "sensor, patrol, radio log, imagery, social media", at=(0, 0), color="grey")
    .node("bus", "Redpanda", "one topic per source, in arrival order", at=(1, 0), color="grey")
    .node("norm", "Normaliser", "vLLM reads free text into a JSON schema", at=(0, 1), color="blue")
    .node("store", "PostGIS, OpenSearch, Qdrant", "record, words, meaning", at=(1, 1), color="blue")
    .node("fuse", "Fuser", "copies, clocks, association, confidence", at=(0, 2), color="yellow")
    .node("rep", "Summary + checker", "vLLM writes, every sentence verified", at=(1, 2), color="red")
    .node("llm", "vLLM on the GPU", "Qwen3.5 2B, Qwen3 embeddings", at=(2, 1), color="purple")
    .node("ana", "Analyst", "map, citations, approve or reject", at=(0, 3), color="green")
    .node("graf", "Grafana", "pipeline and review status", at=(1, 3), color="green")
    .edge("src", "bus").edge("bus", "norm", exit="b", enter="t").edge("norm", "store")
    .edge("store", "fuse", exit="b", enter="t").edge("fuse", "rep").edge("llm", "norm", exit="l", enter="r")
    .edge("llm", "rep", exit="b", enter="r").edge("rep", "ana", exit="b", enter="t").edge("rep", "graf")
)

rumour = (
    Sequence("cjim-rumour", "A rumour, step by step",
             "Two social media posts say a navy ship ran aground. Both come from one low-grade source, nothing else "
             "reports it, and the summary's claim of independent corroboration is caught.",
             [("osint", "Social media", "grey"), ("fuse", "Fuser", "yellow"), ("llm", "vLLM", "purple"),
              ("chk", "Checker", "red"), ("ana", "Analyst", "green")])
    .msg("osint", "fuse", "two posts: navy ship aground at North Spit (graded D4)")
    .msg("fuse", "fuse", "one source, no other report: confidence 0.315, low")
    .msg("fuse", "llm", "write the summary; cite only these two posts")
    .msg("llm", "chk", "\"corroborated by two independent sources\"")
    .msg("chk", "ana", "flagged: the event has 1 independent source")
)

results = (
    Bars("cjim-results", "Keyword baseline against vLLM",
         "The same pipeline with free text read by keyword rules or by vLLM (Qwen3.5 2B on a MacBook Air). Scored "
         "against the scenario's ground truth.", unit="%")
    .bar("Event type right, keywords", 64.8, "", "yellow")
    .bar("Event type right, vLLM", 92.4, "", "green")
    .bar("Association F1, keywords", 82.4, "", "yellow")
    .bar("Association F1, vLLM", 91.8, "", "green")
    .bar("Real events found, keywords", 88.3, "53 of 60", "yellow")
    .bar("Real events found, vLLM", 98.3, "59 of 60", "green")
    .bar("Summary sentences verified", 95.1, "155 of 163", "green")
)

stack = (
    Stack("cjim-stack", "Software stack",
          "Open source throughout. The scenario, normaliser, fusion rules, report checker and scoring are my own.")
    .layer("Sources", ["Scenario generator\n5 sources, ground truth", "Redpanda\nKafka API"], "grey")
    .layer("Models", ["vLLM Metal\nApple GPU", "Qwen3.5 2B\nextraction, summaries", "Qwen3 Embedding\n0.6B"], "purple")
    .layer("Storage", ["PostGIS\nrecord, geometry", "OpenSearch\nwords", "Qdrant\nmeaning"], "blue")
    .layer("Fusion", ["Copies and\ncorrections", "Clock and\ntime zone", "Association", "Confidence\nNATO grading"], "yellow")
    .layer("Review", ["Report\nchecker", "FastAPI +\nLeaflet", "Grafana"], "green")
)

timeline = (
    Timeline("cjim-timeline", "Build status",
             "The pipeline runs end to end and is scored against ground truth; next is a larger model on a GPU server "
             "and messier, more varied sources.")
    .phase("Scenario", "5 sources, truth", "done")
    .phase("Fusion", "copies, clocks, events", "done")
    .phase("vLLM", "extract, summarise", "done")
    .phase("Live stack", "same scores", "done")
    .phase("Larger model", "GPU server", "next")
    .phase("Real formats", "messier sources", "next")
)

DIAGRAMS = [platform, rumour, results, stack, timeline]
