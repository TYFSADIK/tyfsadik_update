from svgdiagram import Flow

PAGE = "work/applications/rea.html"

how = (
    Flow("rea-how", "Where REA sits",
         "An AI agent calls REA through MCP, or a person runs the same workflows from the rea command line. REA "
         "drives local analysis providers and returns findings with their evidence and limitations.", cols=4)
    .node("agent", "AI agent", "Claude Code, Codex, Cursor, Gemini CLI", at=(0, 0), color="cyan")
    .node("cli", "rea CLI", "same workflows from a terminal", at=(1, 0), color="cyan")
    .node("rea", "REA MCP server", "tools, workflows, evidence contracts", at=(0, 1), span=2, color="blue")
    .node("ev", "Findings", "code, references, evidence, unknowns", at=(0, 3), color="green")
    .node("nat", "Native providers", "Hopper, Ghidra, IDA", at=(1, 1), color="orange")
    .node("elf", "ELF layout profile", "pwntools bridge, my contribution", at=(1, 2), color="red")
    .node("web", "JS, .NET, Android, web", "static and runtime analysis", at=(1, 3), color="orange")
    .edge("agent", "rea", "MCP").edge("cli", "rea").edge("rea", "ev")
    .edge("rea", "nat").edge("rea", "elf").edge("rea", "web")
)

profile = (
    Flow("rea-elf", "The ELF layout profile after the change",
         "The header is read before pwntools loads the file: class (32 or 64-bit) and byte order (little or big) "
         "decide how every later field is decoded, and the machine must be one of eight admitted values. Anything "
         "else is rejected with a reason, never half-analysed.", cols=4)
    .node("in", "Selected object", "ELF file on disk", at=(0, 0), color="cyan")
    .node("id", "Identification", "EI_CLASS 1 or 2, EI_DATA 1 or 2", at=(0, 1), color="blue")
    .node("hdr", "Header", "52 or 64 bytes, read in the file's byte order", at=(0, 2), color="blue")
    .node("mach", "e_machine", "one of 8 admitted machines", at=(0, 3), color="blue")
    .node("rej", "Rejected", "unsupported-target with the observed value", at=(1, 3), color="red")
    .node("pwn", "pwntools ELF", "arch in the admitted set; EXEC, DYN or REL", at=(1, 2), color="orange")
    .node("dec", "Decode", "sections, segments, symbols, relocations, mitigation candidates", at=(1, 1), color="green")
    .node("out", "Evidence", "results plus stated limitations", at=(1, 0), color="green")
    .edge("in", "id").edge("id", "hdr").edge("hdr", "mach")
    .edge("mach", "rej", "other machine")
    .edge("mach", "pwn", "admitted", exit="b", enter="r", bend=0)
    .edge("pwn", "dec").edge("dec", "out")
)

DIAGRAMS = [how, profile]
