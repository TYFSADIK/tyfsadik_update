# Engineering Research Log

Internal log of research performed for this project. Format per directive: question, date,
source, evidence, alternatives, decision, unresolved items. External technical facts recorded
here do not imply local deployment.

## 2026-10-21 (update) — Owner testimony on the estate

- New owner statement: 3 hosting stacks + separate GPU stack + small Pi server position;
  24x OptiPlex 5060 SFF hosting fleet running media library, Chakor AI (ai.tyfsadik.org), and
  general services; 4 JBODs ~2 PB; Cisco switching; Raspberry Pi running Pi-hole, security
  monitoring, domain watchdog; GPU stack of 20x OptiPlex 5060 SFF (i7-8700, 16 GB DDR4-2666,
  2x DP, GbE only) each with a "4090 Ti".
- Decisions: statuses upgraded from PLANNED to PARTIALLY VERIFIED for the GPU stack (owner
  states it is built); "4090 Ti" recorded as RTX 4090-class because NVIDIA lists no such SKU
  (evidence: NVIDIA RTX 40 series power specifications page lists 4090, 4080, 4070 families
  only); build narrative added to `docs/asset-register.html` labeled as the owner's account.
- New open question: how the 450 W cards are powered and housed in 200 W SFF chassis (external
  PSU, riser, open frame, or different card). Evidence that resolves it: one open-chassis
  photo + `nvidia-smi --query-gpu=name,power.limit --format=csv` from one node.
- Editorial decision: one owner-stated workload was deliberately not published anywhere in this
  repository (legal/professional/ToS exposure); owner informed directly in the session summary.


## 2026-10-21 — Can an RTX 4090 operate inside a Dell OptiPlex 5060 SFF?

- Question: is the owner-stated plan of 20x OptiPlex 5060 + 20x RTX 4090-class GPUs physically
  and electrically viable without chassis/PSU redesign?
- Sources:
  - Dell, OptiPlex 5060 SFF Setup and Specifications, power supply section:
    https://www.dell.com/support/manuals/en-ca/optiplex-5060-sff/optiplex_5060_sff_setup_and_specs/power-supply?guid=guid-d91d1b07-1ab0-4633-8dd8-9ef84459bf19&lang=en-us
    Evidence: 200 W PSU (EPA Bronze / Platinum options).
  - Dell, OptiPlex 5060 SFF Setup and Specifications (chassis/expansion):
    https://www.dell.com/support/manuals/en-ca/optiplex-5060-sff
    Evidence: chassis 292 x 290 x 92.6 mm; 1x PCIe 3.0 x16 half-height + 1x PCIe 3.0 x4
    half-height; 4 DDR4 UDIMM slots, 64 GB max; factory GPU options GT 730 / R5 430 / RX 550
    (low profile, slot powered).
  - NVIDIA, GeForce RTX 40 Series Power Specifications (official forum post):
    https://www.nvidia.com/en-us/geforce/forums/geforce-graphics-cards/5/501736/geforce-rtx-40-series-power-specifications/
    Evidence: RTX 4090 TGP 450 W; minimum recommended system PSU 850 W; 16-pin 12VHPWR.
  - CNET RTX 4090 review spec table:
    https://www.cnet.com/tech/computing/nvidia-geforce-rtx-4090-review-a-monster-4k-gaming-gpu/
    Evidence: Founders Edition 304 x 137 mm, 3-slot, 24 GB GDDR6X, PCIe 4.0 x16.
  - IT Pro OptiPlex 5060 review: https://www.itpro.com/hardware/32199/dell-optiplex-5060-review-dull-yet-dependable
    Evidence: corroborates 93 mm chassis width.
- Alternatives considered: tower workstations with 750-1000 W+ PSUs; open-frame GPU rigs with
  server PSUs and risers; low-profile 70 W GPUs (RTX A2000 / RTX 4000 SFF Ada class) where SFF
  mounting is mandatory.
- Decision: published as a feasibility analysis in `docs/asset-register.html`. Verdict:
  incompatible unmodified on five independent constraints (PSU budget, aux power connectors,
  slot/bracket height, card length vs chassis depth, cooling). 20-GPU rental cluster remains
  PLANNED with the host platform unresolved. No performance, revenue, or deployment claims.
- Unresolved: exact per-unit configuration of the stated 24x 5060 fleet; which alternative
  platform the owner will adopt; electrical service capacity for a ~9-12 kW continuous load.

## 2026-10-21 — Raw vs usable storage for the stated ~2 PB aggregate

- Question: how should the site present the owner-stated ~2 PB across 4 JBOD enclosures?
- Evidence: drive population, enclosure models, and redundancy scheme are all UNKNOWN, so no
  measured split exists. Published framing: 2 PB is an intended RAW aggregate target; usable
  capacity depends on parity, filesystem overhead, and headroom; backup copies consume capacity
  again under a 3-2-1 posture. An illustrative arithmetic example (labeled as such) shows
  ~1.5 PB usable from 2.0 PB raw at 20% parity + ~3% filesystem overhead.
- Decision: never label the storage as "2 PB usable". Recompute and publish the measured split
  once the JBOD inventory is evidenced.
- Unresolved: enclosure models, bay counts, drive sizes, redundancy scheme, backup target media.

## Earlier rounds (summarized from session history)

- Mermaid rendering: mermaid@11 via jsDelivr, global init in js/main.js; chosen over a build-time
  SVG pipeline to keep the no-build static deployment intact. Diagram audit tool:
  `.tools/audit_mermaid.py`.
- Structured data: Person entity consolidated at `https://tyfsadik.org/#person`; TechArticle,
  BreadcrumbList, CollectionPage, FAQPage used only where visible content matches. SearchAction
  removed from index.html (no site search exists).
- Favicon: owner rejected headshot favicon; orange brand mark regenerated at all sizes with
  `.tools/make_square_favicon.py` (nearest-neighbor pad from the 36x64 original).
