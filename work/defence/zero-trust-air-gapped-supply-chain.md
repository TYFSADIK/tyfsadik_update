# Zero-Trust Air-Gapped Software Supply Chain

Written by [Taki Sadik](../../about.html) · Last updated 2026-10-22 · Status: Building · 15 min read

A pipeline that builds container images reproducibly, generates SBOMs with syft, signs everything with sigstore/cosign, then transfers artifacts across a simulated one-way data diode into an offline Harbor registry, with controls mapped to Canadian Centre for Cyber Security guidance.

## Overview

Software that ends up on disconnected networks, ships, forward operating bases, classified
        enclaves, still has to come from somewhere. This project builds the supply chain
        that gets it there safely: every artifact is built reproducibly, inventoried with a
        software bill of materials (SBOM), cryptographically signed, and only then moved across a
        simulated one-way transfer (a data diode) into an offline registry that disconnected
        environments pull from.

The core problem is trust across a boundary you cannot query back through. Once an artifact
        crosses into the air-gapped side, the low side can never ask "did you get it intact?", so
        every check, hash verification, signature validation, SBOM diff, has to happen either before
        the transfer or entirely on the receiving side. That constraint shapes the whole design, and
        it is exactly the constraint real isolated networks live with.

This is a DevOps-engineering take on a defence-grade problem. I am mapping each control to
        published Canadian Centre for Cyber Security guidance, including ITSM.10.071
        (Protecting your organization from software supply chain threats), ITSAP.10.070 (Cyber supply
        chain: an approach to assessing risk), and ITSAP.10.096 (How updates secure your device, the
        patch-integrity publication), so the project doubles as a practical study
        of how that guidance turns into pipeline code. Everything runs on open-source tooling in my
        homelab; there is no weapons logic, no classified data, and nothing here touches a real
        operational network.

## Architecture

Disconnected Side (High)

Connected Side (Low)

approved bundle

Git repo(pinned deps,lockfiles)

CI runner(reproducible build,SOURCE_DATE_EPOCH)

SBOM generation(syft, SPDX + CycloneDX)

Signing(cosign, keyless+ local key)

Attestations(SLSA provenance,in-toto)

Verification gatesignatures + scan+ SBOM policy

Data diode simulation(one-way UDP,no return path)

Receiver / importerhash-chain check

Harbor registry(offline, internal CA)

Offline re-scan(grype, cached DB)

Disconnected consumers(k3s, workstations)

Figure 1: build, attest, verify, one-way transfer, and offline distribution stages.

The low side is a normal CI pipeline with one extra property: the build is reproducible,
        meaning the same source and pinned toolchain produce a bit-identical image digest. The
        verification gate refuses to release anything whose cosign signature, vulnerability scan,
        or SBOM policy check fails. The bundle that crosses the diode is a tarball containing the
        image, its SBOM, its signatures and attestations, and a manifest that ties them together by
        digest, so the high side can re-verify everything without ever talking back.

## One-Way Transfer and Verification

Figure 2: store-and-forward transfer with hash-chain integrity checking and re-verification on the high side.

- No acknowledgements: a real data diode physically cannot send data back, so the sender retransmits on a schedule and the receiver detects gaps by chunk numbering rather than requesting resends.

- Hash chain: each chunk carries the hash of the previous chunk, so a missing or corrupted chunk anywhere invalidates the chain root and the bundle is quarantined, never partially imported.

- Re-verification on arrival: the high side runs cosign verify and cosign verify-attestation itself, because trusting the low side's checks would defeat the point of a zero-trust boundary. (Honest tension: offline verification cannot query the live Rekor log, so it checks the inclusion proof that travelled with the bundle; trust then rests on the Sigstore root of trust pinned in the cosign distribution that crossed the diode, and refreshing that root needs another out-of-band transfer.)

- Simulation approach: my homelab diode is two VMs connected by a UDP-only forwarder with firewall rules blocking all return traffic, plus a small forwarder daemon doing the chunking. Not hardware, but it enforces the same one-way contract.

### What a data diode actually enforces

A data diode is a hardware-enforced one-way channel: bits can travel from the low side to
        the high side and physically cannot travel back, because the return path does not exist in
        the hardware. That single property changes the security model. There are no
        acknowledgements, so reliability comes from the protocol: scheduled retransmission on the
        sender, gap detection by chunk numbering on the receiver, and hash chaining so a missing
        or corrupted chunk invalidates the bundle instead of letting a partial image through.
        Software diodes simulate this contract with firewalls and forwarders; the discipline is
        the same, which is why the two-VM UDP simulator is a valid prototype even though it is
        not a hardware diode.

### How reproducible builds prove supply-chain integrity

A reproducible build means the same source, built with the same toolchain in a controlled
        environment, produces byte-identical output, verified here by matching image digests
        across clean BuildKit builds. That is a verification result, not a performance benchmark:
        it proves nothing was injected between source and image. Paired with an SBOM generated at
        build time and a cosign signature over the digest, the chain answers three questions in
        order: what is in this image (SBOM), is it exactly what the pipeline built (signature),
        and can it reach the isolated network without modification (diode transfer with
        hash-chained chunks and re-verification on arrival). Policy mapping to the Canadian
        Centre for Cyber Security guidance is the remaining step that turns this into an
        auditable posture.

## Stack

| Layer | Technology | Why |
| --- | --- | --- |
| Build | GitHub Actions / GitLab CI + BuildKit | Pinned base images, SOURCE_DATE_EPOCH for reproducibility |
| SBOM | syft (SPDX + CycloneDX) | Standard formats, diffable between releases |
| Signing and provenance | cosign (Sigstore: Fulcio certificates, Rekor transparency log), in-toto attestations | Keyless signing plus offline local keys for the air-gapped case |
| Vulnerability scanning | trivy (low side), grype with cached DB (high side) | grype consumes the syft SBOM and works fully offline |
| One-way transfer | Custom UDP forwarder (Python), UDPcast for bulk | Simulates a data diode on commodity VMs |
| Offline registry | Harbor (internal CA, robot accounts) | Artifact plus signature plus SBOM storage with RBAC |
| Verification and policy | cosign verify, OPA/Conftest on SBOM | Policy-as-code release gate |
| Orchestration | Kubernetes (homelab cluster) + Terraform | Whole environment reproducible from Git |

## How I'm Building It

A reference service builds through BuildKit with pinned base-image digests, locked dependency files, and SOURCE_DATE_EPOCH set from the commit timestamp. Two clean builds must produce the same image digest before anything else proceeds.

syft runs against the built image and emits both SPDX and CycloneDX documents, stored as registry artifacts alongside the image so consumers get the inventory without re-deriving it.

cosign sign covers the image digest, and cosign attest attaches SLSA-style provenance (builder identity, source commit, build parameters) as an in-toto attestation. I use keyless signing on the connected side and a local key pair whose public half crosses with the bundle.

A Python forwarder on the low VM chunks the release bundle, hashes each chunk, and streams over UDP to the high VM. nftables rules on the receiver block every outbound packet, enforcing the one-way property at the firewall, not just by convention.

The receiver verifies the hash chain, runs cosign verify and cosign verify-attestation locally, pushes to Harbor, and re-scans with grype using a vulnerability database that itself crossed the diode on a schedule.

Each control is documented against the Cyber Centre publication it implements, so the repo reads as both a working pipeline and a traceable compliance artifact.

## How Defence Could Implement This

Disconnected and classified networks are the norm in Canadian defence, not the exception,
        and they all face the same question this project answers: how do you patch and update
        software you cannot reach. A realistic implementation looks like:

- Classified enclave updates: DND networks at different classification levels already exchange data through accredited cross-domain solutions and hardware diodes. A signed, SBOM-inventoried bundle format gives the receiving enclave independent proof of what it just imported, instead of trusting the transfer process alone.

- Ships and deployed platforms: RCN vessels and forward units under operations like LENTUS or deployed task groups sync over intermittent satellite links. A store-and-forward model with hash-chain integrity tolerates dropouts, and reproducible builds let a ship verify that the update it received matches the exact bits the vendor or ADM(IM) produced.

- NORAD modernization and infrastructure hardening: the Cyber Centre's guidance on supply chain integrity (ITSM.10.071 on software supply chain threats, ITSAP.10.070 on supply chain risk assessment, and ITSAP.10.096 on how updates secure a device) maps directly onto SBOM generation, signature verification, and provenance attestation. A pipeline like this is how that guidance becomes an auditable control rather than a checklist item.

- Coalition interoperability: SBOMs in SPDX or CycloneDX are the emerging common language for allied software exchange, so a Canadian pipeline that already speaks them slots into combined programs without translation work.

The homelab version uses simulation throughout. An operational version swaps my UDP
        forwarder for an accredited hardware diode and my self-signed CA for the departmental PKI,
        while the pipeline stages stay identical.

**Q: How to Build This Yourself (step-by-step guide)**

## Status & Roadmap

- Done: reference service with reproducible BuildKit build (matching digests across clean builds), syft SBOM generation in both formats, cosign keyless signing in CI.

- In progress: in-toto provenance attestation, two-VM UDP diode simulator with chunk hash chain, Harbor deployment on the isolated VM with internal CA.

- Next: high-side re-verification automation, offline grype scanning with a diode-transferred vulnerability database, OPA policy gate on SBOM contents, and the full Cyber Centre guidance mapping document.

### Designed vs Built vs Measured

| Subsystem | Designed | Built | Measured |
| --- | --- | --- | --- |
| Reproducible BuildKit builds (matching digests) | Yes | Yes | Verified: digests match across clean builds (a verification result, not a performance benchmark) |
| syft SBOM generation (both formats) | Yes | Yes | Verified: SBOMs generated |
| Cosign signing in CI | Yes | Yes | Verified: signatures validate |
| in-toto provenance attestation | Yes | In progress | No measured results yet |
| Two-VM UDP diode simulator with chunk hash chain | Yes | In progress | No measured results yet |
| Harbor on isolated VM with internal CA | Yes | In progress | No measured results yet |
| High-side re-verification automation | Yes | No | No measured results yet |
| Offline grype scanning with diode-transferred DB | Yes | No | No measured results yet |
| OPA policy gate on SBOM contents | Yes | No | No measured results yet |
| Cyber Centre guidance mapping document | Yes | No | No measured results yet |

Reproducible builds with matching digests and SBOM generation exist and are verified, but
        that is a verification result, not a performance benchmark. The diode simulator, Harbor
        automation, offline rescanning, and policy mapping remain incomplete, and no performance
        benchmark has been run.

## How I Built It

A reference service builds through BuildKit with pinned base-image digests, locked dependency files, and SOURCE_DATE_EPOCH set from the commit timestamp. Two clean builds must produce the same image digest before anything else proceeds; if they differ, the layers get diffed until the nondeterminism is found.

syft runs against the built image and emits both SPDX and CycloneDX documents, stored as registry artifacts alongside the image so consumers get the inventory without re-deriving it.

cosign sign covers the image digest, and cosign attest attaches SLSA-style provenance (builder identity, source commit, build parameters) as an in-toto attestation. Keyless signing on the connected side; a local key pair whose public half crosses with the bundle for the air-gapped side.

A Python forwarder on the low VM chunks the release bundle, hashes each chunk, and streams over UDP to the high VM. nftables rules on the receiver block every outbound packet, enforcing the one-way property at the firewall, not just by convention.

The receiver verifies the hash chain, runs cosign verify and cosign verify-attestation locally, pushes to Harbor with an internal CA, and re-scans with grype using a vulnerability database that itself crossed the diode on a schedule.

Each control is documented against the Cyber Centre publication it implements, including ITSM.10.071, so the repo reads as both a working pipeline and a traceable compliance artifact.

## What You Need

| Category | Item | Notes |
| --- | --- | --- |
| Hardware | Two VMs or two machines on isolated networks | The isolation must be real; do not cheat with TCP, the absence of ACKs is the whole lesson |
| Software | BuildKit, syft, cosign, trivy (low side), grype (high side), Harbor, Python for the forwarder, nftables, OPA or Conftest, Kubernetes + Terraform for the environment | All open source |
| Skills | CI/CD pipelines, container image internals, basic firewalling and networking | Comfort with digests, SBOM formats, and signature verification is the core of it |
| Accounts | None required | Keyless Sigstore signing is optional on the connected side; the air-gapped side needs no accounts at all |

## Challenges and Lessons Learned

- No acknowledgements changes everything. Reliability has to come from the protocol: scheduled retransmission on the sender, gap detection by chunk numbering on the receiver, and hash chaining so a missing or corrupted chunk invalidates the bundle instead of letting a partial image through. A failed bundle is quarantined, never partially imported.

- The high side re-verifies everything. Trusting the low side's checks would defeat the point of a zero-trust boundary. cosign verify and the hash-chain check run again after transfer, because the high side trusts the math, not the sender.

- Reproducibility is a debugging problem first. Timestamp and file-ordering nondeterminism has to be hunted down with layer diffs before the pipeline can claim bit-identical digests. The SOURCE_DATE_EPOCH step looks trivial and is not.

- Key management for the offline side needs a plan. The local key pair's public half crosses with the bundle, which works for day one; rotation and revocation need an answer before the fleet grows past a bench.

- SBOMs are easy; enforcement is the work. Generating the inventory takes minutes. The OPA/Conftest policy gate that refuses a release based on the SBOM's contents is the control that actually matters, and it is still on the roadmap.

## What Is Next

- High-side re-verification automation and the offline grype scanning schedule.

- OPA policy gate on SBOM contents.

- The full Cyber Centre guidance mapping document.

- Transfer and verification timings as measured results. Reproducible digests and SBOM generation are verified results today, not performance benchmarks, and the page says so explicitly.

## Related Builds

- Secure Robot Fleet Updates, where these signed artifacts land: measured boot and YubiKey-signed OTA on real robots.

- DDIL-Proof DevOps, the CI/CD system that produces the signed artifacts this pipeline verifies.

- Decision Black Box, tamper-evident logging that records what the trusted software decided.

## Cite This Page

**Q: Citation formats**

A: Plain text
