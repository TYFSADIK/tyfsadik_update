# REA: Multi-Architecture ELF Analysis

Written by [Taki Sadik](../../about) · Last updated 2026-10-26 · 5 min read

Open-source contribution: extending REA's ELF layout analysis from x86-64 to eight CPU architectures

## Overview

[REA](https://github.com/morluto/rea) ("Reverse Engineer Anything") is an open-source tool that lets an AI agent, or a person at a terminal, inspect software without its source code: native binaries, JavaScript and Electron apps, .NET assemblies, Android packages, websites, captures and more. It runs as an MCP server, so agents such as Claude Code, Codex and Cursor can call it, and it returns findings together with the evidence and limitations behind them. REA is built and maintained by its author, [morluto](https://github.com/morluto), under the MIT licence.

My contribution is to one part of it: the offline ELF layout profile, which reads an ELF file's sections, segments, symbols and relocations through a pwntools bridge. Before the change it accepted only x86-64, 64-bit, little-endian files. My pull request, [morluto/rea#4871](https://github.com/morluto/rea/pull/4871), extends it to eight CPU architectures in 32 and 64-bit and both byte orders, and adds a verification fixture for each combination.

The pull request is open and under review. It has not been merged, so none of this is in a REA release yet; the page will say so until it is.

| Item | Details |
| --- | --- |
| Project | morluto/rea, MIT licence, npm package rea-agents |
| My fork | TYFSADIK/rea |
| Pull request | #4871: ELF multi-architecture support and quality fixes |
| Size | +544 and -112 lines across 61 files |
| Status | Open, under review (October 2026) |
| Languages | Python (pwntools bridge), JavaScript (verifier), TypeScript (service and tests) |

## What REA Does

REA's idea is that an agent should be able to answer "how does this feature work?" about software you only have as a compiled file, and show its working. It wraps tools such as Hopper, Ghidra, IDA, JADX and pwntools behind a consistent set of MCP tools, and each result says what was observed, how, and what remains unknown.

The ELF layout profile is one of those tools. Given an ELF file (the executable format used by Linux, Android and most embedded systems), it reports the file's layout: sections and segments, the original symbol and relocation tables, and static hints about mitigations such as RELRO and stack canaries. It never runs the file.

## The Problem

The layout profile refused anything that was not an x86-64 file. The bridge checked three things in the ELF header and gave up on the first mismatch:

# bridge/pwntools/layout_impl.py, before
if content[4] != 2 or content[5] != 1:
    raise LayoutFailure("unsupported-target", "Initial layout profile requires ELF64 little-endian objects.")
if int.from_bytes(content[18:20], "little") != 62:
    raise LayoutFailure("unsupported-target", "Initial layout profile requires x86-64 ELF objects.")

That ruled out most of the ELF files a reverse engineer actually meets: 32-bit ARM and AArch64 from phones and single-board computers, MIPS and PowerPC from routers and industrial devices, RISC-V from new embedded hardware, and 32-bit x86. It also hard-coded little-endian reads, so even the machine check would read the wrong number from a big-endian file.

## The Change

The identification bytes give the class (1 for 32-bit, 2 for 64-bit) and the data encoding (1 little-endian, 2 big-endian). The header size and the byte order for every later field now come from those, instead of being assumed.

elf_class = content[4]
elf_data = content[5]
if elf_class not in (1, 2):
    raise LayoutFailure("unsupported-target", "Layout profile requires 32-bit or 64-bit ELF objects.")
if elf_data not in (1, 2):
    raise LayoutFailure("unsupported-target", "Layout profile requires little-endian or big-endian ELF objects.")
header_size = 64 if elf_class == 2 else 52
if len(content) < header_size:
    raise LayoutFailure("format", "Selected ELF header is truncated.")
byte_order = "little" if elf_data == 1 else "big"
machine = int.from_bytes(content[18:20], byte_order)

Rather than accept any machine, the profile admits eight that pwntools 4.15.0 can model, and rejects everything else with the observed value in the message. Partial success on an unknown architecture would be worse than a clear refusal.

ADMITTED_MACHINES = {
    3: "EM_386", 8: "EM_MIPS", 20: "EM_PPC", 21: "EM_PPC64",
    40: "EM_ARM", 62: "EM_X86_64", 183: "EM_AARCH64", 243: "EM_RISCV",
}
ADMITTED_ARCHES = {
    "amd64", "aarch64", "i386", "arm", "riscv32", "riscv64",
    "mips", "mips64", "powerpc", "powerpc64",
}

REA attaches limitations to every result. The x86-64 wording became architecture-neutral ("the decoded native symbol structure" instead of Elf64_Sym), and a new limitation states exactly which machines, classes and byte orders are admitted.

The repository's binary-layout verifier builds small ELF objects by hand, byte by byte, and checks what the profile reports. I extended the builder to write 32 and 64-bit headers in either byte order, added a .rela.text relocation section that references the _start symbol, and added a relocatable (ET_REL) variant, so relocation decoding and symbol references are checked on every machine.

// One RELA entry referencing the _start symbol (index 1), exercising
// relocation decoding and schema reference checks for every machine.
const rela = is64
  ? packFields([u64(base), u64((1n << 32n) | 1n), s64(0)])
  : packFields([u32(base), u32((1 << 8) | 1), s32(0)]);

## Verification Fixtures

Twelve hand-built objects cover the matrix. Each has one loadable segment, a .text section, a symbol table, a string table, a relocation section and a section-name table, and the verifier checks the decoded machine, class, byte order, sections, symbol and relocation.

| Fixture | Machine | Class | Byte order | Type |
| --- | --- | --- | --- | --- |
| multi-arch-i386 | EM_386 (3) | 32-bit | little | executable |
| multi-arch-arm | EM_ARM (40) | 32-bit | little | executable |
| multi-arch-aarch64 | EM_AARCH64 (183) | 64-bit | little | executable |
| multi-arch-mips-le | EM_MIPS (8) | 32-bit | little | executable |
| multi-arch-mips-be | EM_MIPS (8) | 32-bit | big | executable |
| multi-arch-mips64-be | EM_MIPS (8) | 64-bit | big | executable |
| multi-arch-ppc | EM_PPC (20) | 32-bit | big | executable |
| multi-arch-ppc64-be | EM_PPC64 (21) | 64-bit | big | executable |
| multi-arch-ppc64-le | EM_PPC64 (21) | 64-bit | little | executable |
| multi-arch-riscv32 | EM_RISCV (243) | 32-bit | little | executable |
| multi-arch-riscv64 | EM_RISCV (243) | 64-bit | little | executable |
| multi-arch-riscv64-relocatable | EM_RISCV (243) | 64-bit | little | relocatable (ET_REL) |

x86-64 keeps its existing fixtures. Building the objects by hand, rather than compiling them, means the tests need no cross-compilers and every byte in them is known.

## Review Status

REA's contribution process is strict: each pull request states its scope, its contract and boundary impact, and how it was verified, and automated reviewers run before a maintainer looks. As of October 2026, #4871 is open. Until it is merged, the work lives in my fork and in the pull request, not in a REA release.

I also opened a small quality-gate clean-up (#4857, 6 lines) and a broader pull request (#4887). The broader one picked up an automated review finding about process output handling and merge conflicts with the main branch; it needs rework before it is ready, so it is not described as a contribution here.

## What I Learned

- How the ELF header is laid out, and why class and byte order must be read before anything else

- Contributing to a large, fast-moving project: small scoped pull requests review better than broad ones, and a fork drifts quickly (mine fell well behind main within days)

- Writing test fixtures byte by byte, so the test controls every field it checks

- Why a tool that reports evidence should refuse unknown input clearly instead of returning a partial answer

- How MCP lets an agent call local analysis tools, and what has to stay deterministic underneath

## What Is Next

- Respond to review on #4871 and rebase it onto the current main branch

- Close or split #4887 into small, separately reviewable fixes

- Add fixtures from real binaries for each architecture alongside the hand-built ones

- Use REA's multi-architecture layout profile on firmware from the homelab's network devices

## Related Projects

- TYF-AI Platform, a self-hosted AI platform.

- Zero-Trust Air-Gapped Supply Chain, verifying software before it runs.
