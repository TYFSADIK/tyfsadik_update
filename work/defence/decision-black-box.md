# Decision Black Box

Written by [Taki Sadik](../../about.html) · Last updated 2026-10-22 · Status: Building · 14 min read

A tamper-evident audit layer for human-in-the-loop decisions in a simulated airspace-deconfliction scenario: a hash-chained, signed, append-only log in the style of certificate transparency, a replay tool that reconstructs any decision state, and OPA policy-as-code checks on every entry.

## Overview

When a decision support system recommends something and a human approves it, someone has to
        be able to answer afterwards: what did the operator see, what did the system recommend,
        which policy version was in force, and who signed off? This project is a
        flight recorder for decisions, built around a fictional
        airspace-deconfliction simulator. Every recommendation, override, and approval is written
        to an append-only log that cannot be edited or quietly reordered after the fact.

The core is a hash-chained, signed log modelled on certificate
        transparency (RFC 6962): each entry includes the hash of the previous one, the log operator
        signs Merkle tree heads, and auditors can request inclusion and consistency proofs. On top
        of that sit two tools: a replay engine that rebuilds the exact state of the
        simulated airspace picture at any entry in the log, and OPA policy-as-code
        checks that evaluate every decision against the rules of engagement simulated for
        the scenario (for example: no deconfliction approval without two-operator confirmation).

Why bother: accountability and responsible AI are treated seriously in Canadian defence
        circles, and DND/CAF has published AI strategy commitments around traceability and human
        oversight. I wanted to practice the engineering behind those commitments. Everything here
        runs on simulated data I generate myself. There is no weapons logic, no real targeting
        information, and nothing classified anywhere in this project.

## Architecture

Audit Layer

Simulation (open data only)

Airspace scenario generator(fictional tracks, Python)

Decision support stub(rule-based recommender)

Ingestion API(Go, HTTP + gRPC)

Append-only loghash chain + Merkle tree

Signer(Ed25519, key in KMS-style seal)

OPA sidecar(Rego policies)

Event store(PostgreSQL, WORM semantics)

Signed tree headsgossip endpoint

Replay toolrebuild state at entry N

Audit dashboard(proofs, policy verdicts)

Figure 1: simulated sources feed the ingestion API; every event is policy-checked, chained, signed, and stored before it can be replayed or audited.

The ingestion API is the only writer. An event (sensor observation, recommendation,
        operator decision) is validated, sent to the OPA sidecar for a policy verdict, then
        appended to the log. The append is atomic with the hash-chain link: the new entry commits
        the SHA-256 of its canonical JSON encoding plus the previous entry's hash, so any edit to
        history invalidates every subsequent link. Periodically the signer folds the log into a
        Merkle tree, signs the tree head with an Ed25519 key (Ed25519 public keys are 32 bytes and
        signatures are 64 bytes, per RFC 8032), and publishes it, which is what lets
        an outside auditor verify the log without trusting me.

## Hash-Chain Verification and Replay

no

yes

no

yes

Auditor requests prooffor entry N

Fetch Merkle inclusion proofentry N vs signed tree head

Hash path recomputesto signed root?

TAMPER: entry or treedoes not match signed head

Fetch signed tree headsT_old and T_new

Consistency proof valid?(T_old is a prefix of T_new)

TAMPER: history was rewrittenor forked

Log verified:append-only, untampered

Replay: fold events 1..Nthrough the state machine

Reconstructed decision state:tracks, recommendations, approvals,policy verdicts at that moment

Figure 2: verification proves the log is append-only before replay reconstructs the state at any entry.

- Inclusion proof: an auditor gets the Merkle path for a single entry and checks it against a signed tree head, the same proof a certificate transparency monitor runs.

- Consistency proof: two signed tree heads are compared to prove the log only ever grew; this is the property that catches silent history rewrites.

- Replay: events are folded in order through a deterministic state machine, so state at entry N is always reproducible. The same code path backs the audit dashboard and any after-action review.

### How the tamper-evidence chain works (and its limits)

Every entry carries the hash of the previous entry, so altering any record breaks every
        link after it, and the Merkle tree over the log lets an auditor verify a single entry
        against a signed tree head with a short inclusion proof. Consistency proofs show that a
        newer tree head is a strict extension of an older one, which is what catches a silent
        history rewrite or a fork. This is the Certificate Transparency pattern: append-only
        Merkle logs with signed tree heads make tampering detectable, not impossible. A
        verifier that nobody runs is decoration, which is why the rescan verifier exists and why
        the gossip endpoint is on the roadmap: the protection comes from independent parties
        comparing tree heads, not from the hash function alone.

### How OPA gates an action

When a write path needs a policy decision, the service hands OPA a JSON input describing
        the proposed action: who requested it, what resource it touches, and the current context.
        OPA evaluates the Rego policy against that input and returns a JSON verdict, allow or
        deny, with the reasons. The service enforces the verdict and writes both the request and
        the verdict into the log, so the policy decision itself becomes auditable evidence. The
        first policy on the roadmap is two-person approval: an action above a threshold needs two
        distinct authorised identities, and OPA is what checks that before anything is written.

## Stack

| Layer | Technology | Why |
| --- | --- | --- |
| Audit log core | Go (stdlib crypto, x/crypto Ed25519) | Static binaries, strong typing for a component that must not be ambiguous |
| Transparency design | RFC 6962-style Merkle tree (Trillian-inspired) | Battle-tested inclusion and consistency proofs |
| Policy as code | Open Policy Agent (Rego), sidecar over HTTP | Policies versioned in Git, evaluated per decision, independently auditable |
| Event store | PostgreSQL (append-only table, no UPDATE/DELETE grants) | WORM semantics with boring, well-understood tooling |
| Simulation | Python scenario generator (fictional tracks) | Deterministic seeded runs so reviews are reproducible |
| Deployment | Docker Compose on my homelab, Terraform later | Whole stack reproducible from Git |

## How I'm Building It

A versioned JSON schema for the three event types (observation, recommendation, decision), stored in PostgreSQL with a role that physically cannot run UPDATE or DELETE. Inserts compute the chain hash in a trigger-checked transaction.

A Go service that folds pending entries into a Merkle tree every N seconds, signs the tree head with an Ed25519 key held behind a software seal, and publishes signed heads to a gossip-style endpoint so forks are detectable.

Rego policies evaluate every decision event before it is committed. Current example: a simulated deconfliction approval requires two distinct operator identities within a time window. The verdict (allow/deny plus policy version) is logged alongside the event, so policy changes are visible in history.

A seeded Python generator produces fictional aircraft tracks, the rule-based stub issues recommendations (re-route, hold, handoff), and scripted operators approve or override. Deterministic seeds mean any reviewer can reproduce an incident exactly.

A CLI (replay --entry N) folds events through the state machine and renders the picture at that moment; a small web UI shows the log, proof status, and policy verdicts per decision.

## How Defence Could Implement This

The accountability pattern here is deliberately generic, which is what makes it transferable
        to real CAF and NORAD contexts:

- Command and control audit: any C2 system that surfaces machine recommendations (air tasking, track classification aids, logistics triage) could write the same three event types to a tamper-evident log, giving boards of inquiry and after-action reviews a trustworthy record of who saw what and decided what.

- Responsible AI assurance: DND/CAF AI strategy commitments call for traceable, human-accountable AI. OPA-style policy gates are a concrete mechanism: rules like "human confirmation required" stop being documentation and become enforced, logged code.

- Cross-network integrity: signed tree heads are small and one-way friendly. A consistency proof can cross a classification boundary where the full log cannot, so a higher-side auditor can verify a lower-side log was not rewritten without the data itself moving.

- Multi-party verification: in NORAD or coalition settings, each party can hold signed tree heads from the others, so no single operator can quietly edit a shared decision record.

- Domestic operations: the same pattern applies outside combat contexts, for example Operation LENTUS tasking, where provincial and military decisions interleave and a clean audit trail matters for public accountability.

None of this requires new sensors or new platforms. It is an integrity layer over systems
        that already exist, and it can be prototyped at homelab scale, which is exactly what I am
        doing with simulated data.

**Q: How to Build This Yourself (step-by-step guide)**

## Status & Roadmap

- Done: event schema, append-only PostgreSQL store with insert-time hash chaining, chain rescan verifier, Docker Compose baseline.

- In progress: Merkle tree and Ed25519 tree-head signer, inclusion proof endpoint, first OPA policy (two-person approval) on the write path.

- Next: consistency proofs and gossip endpoint, seeded scenario simulator, replay CLI, then the audit dashboard.

### Designed vs Built vs Measured

| Subsystem | Designed | Built | Measured |
| --- | --- | --- | --- |
| Event schema | Yes | Yes | Not applicable |
| Append-only PostgreSQL store with hash chaining | Yes | Yes | Not applicable |
| Chain rescan verifier | Yes | Yes | No verification benchmark yet |
| Docker Compose baseline | Yes | Yes | Not applicable |
| Merkle tree + Ed25519 tree-head signer | Yes | In progress | No measured results yet |
| Inclusion proof endpoint | Yes | In progress | No measured results yet |
| OPA policy gate (two-person approval) | Yes | In progress | No measured results yet |
| Consistency proofs + gossip endpoint | Yes | No | No measured results yet |
| Scenario simulator and replay CLI | Yes | No | No measured results yet |
| Audit dashboard | Yes | No | No measured results yet |

The schema, the append-only store, the hash-chain verifier, and the Compose baseline
        exist. Merkle proofs, the signer, the OPA gate, replay, and the dashboard are incomplete,
        and no benchmark has been run, so verification claims above are designs and protocols.

## How I Built It

A versioned JSON schema for three event types (observation, recommendation, decision), stored in PostgreSQL with a writer role that physically cannot run UPDATE, DELETE, or TRUNCATE. Inserts compute the chain hash in a trigger-checked transaction. Deletion was tested to fail, not assumed to fail.

A verifier that recomputes every hash link across the table. Any edit to history invalidates every subsequent link, so tampering shows up as a broken chain, not a missing row.

A Go service folds pending entries into an RFC 6962-style Merkle tree every N seconds, signs the tree head with an Ed25519 key held behind a software seal, and publishes signed heads to a gossip-style endpoint so forks are detectable.

Rego policies evaluate every decision event before it is committed. The first policy is two-person approval: a simulated deconfliction approval needs two distinct operator identities within a time window. The verdict (allow or deny, plus the policy version) is logged alongside the event.

A seeded Python generator produces fictional aircraft tracks, a rule-based stub issues recommendations (re-route, hold, handoff), and scripted operators approve or override. Deterministic seeds mean any reviewer can reproduce an incident exactly.

A CLI (replay --entry N) folds events 1 through N through the state machine and renders the picture at that moment; a small web UI shows the log, proof status, and policy verdicts per decision.

## What You Need

| Category | Item | Notes |
| --- | --- | --- |
| Hardware | Any laptop or desktop | Everything runs in Docker Compose on the homelab |
| Software | Go, PostgreSQL, Open Policy Agent, Python, Docker Compose | Ed25519 via Go x/crypto; RFC 6962 describes the Merkle proof design this follows |
| Skills | Go or Python, SQL, basic Rego for OPA policies, comfort reading an RFC | The Merkle tree is the steepest part; Trillian's design documentation is the best study material |
| Accounts | None | No external services involved; the scenario data is generated locally |

## Challenges and Lessons Learned

- Append-only has to be real. The database role enforces it; convention does not. (One honest caveat: grants bind the writer role, not the table owner or a superuser, so ownership stays with a separate admin role.) The self-attack tests (edit a middle row, delete rows, fork the tree) must all be caught by verification, or the design is decoration. I wrote those tests before trusting the chain.

- Hashes make tampering detectable, not impossible. The protection comes from independent parties comparing signed tree heads, which is why the gossip endpoint matters more than the hash function. A verifier nobody runs is decoration.

- Policy decisions are evidence too. Logging the OPA verdict and the policy version with every event keeps policy changes visible in history, so a rule change cannot hide inside a quiet deploy. Policy-as-code is only auditable if the code version is in the log.

- Replay is a fold, not a query. State at entry N is a pure function of events 1 through N. That single property is what makes after-action review reproducible, and it forced the state machine to stay deterministic.

- Inclusion and consistency proofs answer different questions. Inclusion proves an entry is in the log; consistency proves the log only ever grew. An auditor needs both, which is why the roadmap has both endpoints.

## What Is Next

- Consistency proofs and the gossip endpoint.

- Seeded scenario simulator and the replay CLI.

- Audit dashboard with per-decision proof status and policy verdicts.

- Verification benchmarks (proof generation and verification cost at log scale) as measured results. Until then, verification claims on this page are designs and protocols.

## Related Builds

- Secure Robot Fleet Updates, signed, measured boot and OTA updates, the integrity companion to audit logging.

- DDIL-Proof DevOps, the resilient CI/CD pipeline that ships the software this audit layer watches.

- Zero-Trust Air-Gapped Supply Chain, signed artifacts end to end, so the black box records only trustworthy software.

## Cite This Page

**Q: Citation formats**

A: Plain text
