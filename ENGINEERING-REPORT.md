# Engineering Report — Hardware Inventory, Documentation Section, and Verification Round

Date: 2026-10-21. Scope: the mandatory physical hardware inventory and infrastructure
verification directive, plus completion of the `/docs/` documentation section. Preservation
policy held throughout: purely additive changes; no files deleted, no URLs broken, no existing
content replaced.

## 1. What was inspected

- Full repository: static HTML site (no build step), GitHub Pages + CNAME, `css/style.css`,
  `js/main.js` (nav, back-to-top, Mermaid init, copy buttons), 198 sitemap URLs, 44 projects,
  649 JSON-LD blocks.
- Git history: the local working copy is not a git repository; no commit history available.
  The site was therefore audited from file contents and the owner's statements.
- New hardware directive items checked against repository evidence: no configuration files,
  manifests, photos, or inventory captures exist for the expansion hardware (racks, OptiPlex
  fleet, JBODs, Cisco gear, Raspberry Pi boards, GPUs). These are recorded as owner-stated
  with explicit statuses, not as confirmed assets.

## 2. Files added

| File | Purpose |
|---|---|
| `docs/asset-register.html` | Physical + logical asset register with CONFIRMED / PARTIALLY VERIFIED / PLANNED / UNKNOWN statuses, master Mermaid architecture diagram, storage raw-vs-usable model, OptiPlex 5060 SFF vs RTX 4090 feasibility analysis with citations, dependency map, 6-step evidence-collection checklist |
| `docs/glossary.html` | 52-term plain-language engineering glossary (networking, orchestration, storage, security, AI/ML, defence terms) |
| `docs/decisions.html` | 6 reconstructed ADRs (Proxmox, kubeadm, Longhorn, MetalLB+ingress-nginx, zero-trust tunnel, local-first AI), honestly labeled as reconstructed |
| `docs/engineering-audit.md` | Internal audit: architecture, inventory, limitations, prioritized work |
| `docs/research-log.md` | Research log with questions, sources, decisions, unresolved items |

## 3. Files modified (additive edits only)

- `docs/index.html`: fixed 13 broken relative paths left by an interrupted earlier session
  (missing `../` prefixes on CSS, favicons, manifest, banner, nav, footer script); added the
  asset register to the Reference Documents list and to CollectionPage `hasPart`.
- `sitemap.xml`: +4 URLs (`/docs/`, asset-register, glossary, decisions). Now 198 URLs,
  valid XML.
- `llms.txt`: new "Engineering documentation" section listing the four docs pages.
- `work/infrastructure/homelab-server-room.html`: added asset-register link under Related Work.

## 4. Hardware directive findings

- The CONFIRMED lab remains: 3 desktop + 4 laptop Proxmox VE 8.x hosts, managed switch
  (VLANs 10/20/30), router, 5 GHz bridge, ops desk, photographed and in daily use.
- Owner-stated expansion (2026-10-21) recorded as PARTIALLY VERIFIED: 3 server racks, 24x
  OptiPlex 5060 SFF, 4 JBOD enclosures, ~2 PB intended RAW aggregate (never labeled usable).
  Recorded as UNKNOWN: Cisco models, Raspberry Pi counts, UPS/cooling. Recorded as PLANNED:
  20x OptiPlex + 20x RTX 4090-class GPU rental cluster.
- GPU feasibility verdict (with citations to Dell and NVIDIA specifications): an RTX 4090
  (450 W TGP, 304 mm, 3-slot full-height, 12VHPWR, 850 W minimum PSU) is incompatible with an
  unmodified OptiPlex 5060 SFF (200 W PSU, half-height PCIe slot, 292 x 290 x 92.6 mm chassis)
  on five independent constraints. Realistic alternatives documented; the cluster stays PLANNED.
  Electrical implication (~9-12 kW continuous) documented as its own project.

## 5. Validation performed

- JSON-LD: 649 blocks site-wide, 0 invalid (Python parse of every block).
- Link check: no problems on any docs/ page; remaining tool reports are known false positives
  (root-absolute paths in 404.html, %20-encoded `Prove/` image paths that exist on disk).
- SEO audit: 198/199 pages fully covered; the single exception is 404.html, deliberately
  noindex with no canonical/OG by design.
- Sitemap: parses as valid XML, 198 URLs.
- HTTP smoke test (local server): all new pages and assets return 200.
- Em-dash check: 0 in all four docs pages.

## 6. What could not be verified

- Mermaid diagrams on new pages were not browser-render-verified (Playwright unavailable in
  this environment). They use the identical mermaid@11 + `div.mermaid` pattern as previously
  audited pages. Recommend a one-time browser pass after deploy.
- No external service (GitHub Pages deploy, Search Console, DNS) was touched; indexing and
  deployment are not claimed.
- All PARTIALLY VERIFIED / PLANNED / UNKNOWN asset rows remain so until the evidence checklist
  on the asset register is executed on the physical hardware.

## 7. Operational note

Files in this working copy were externally reverted once during the engagement (Oct 20,
suspected sync/re-extraction). All changes were re-applied and re-verified. Commit and deploy
promptly after this session to minimize the risk window.

## 8. Round 2 update (2026-10-21): owner testimony integrated

The owner supplied configuration-level testimony about the estate. Changes:

- `docs/asset-register.html`: stated inventory table rebuilt with the detailed testimony
  (3 hosting stacks + separate GPU stack + Pi position; 24-unit hosting fleet roles: media
  library, Chakor AI at ai.tyfsadik.org, general services; GPU nodes specified per unit as
  i7-8700 / 16 GB DDR4-2666 / 2x DP / GbE; Raspberry Pi roles: Pi-hole, security monitoring,
  domain watchdog). GPU stack status changed PLANNED to PARTIALLY VERIFIED (owner-stated as
  built). Master Mermaid diagram redrawn (media node added, GPU stack moved into the
  owner-stated boundary). Feasibility section reframed: the stack is reported built, so the
  section now documents the three possible integration methods and the exact evidence
  (open-chassis photo + nvidia-smi output) that resolves the gap; "4090 Ti" recorded as
  RTX 4090-class because NVIDIA lists no such SKU. New sections: a 10-step build narrative
  (labeled as the owner's account) and a legal/licensing/operations considerations section.
- `work/infrastructure/homelab-server-room.html`: limitations section now points to the asset
  register for the larger stated estate.
- `docs/engineering-audit.md`, `docs/research-log.md`: testimony and decisions logged. One
  owner-stated workload was deliberately kept out of the entire repository (legal/professional
  exposure); the owner was informed directly.
- Validation re-run: JSON-LD valid (2 blocks on the register page), zero broken local
  references, zero em dashes, Mermaid subgraph/end balanced, link checker clean on changed
  pages, HTTP smoke 200 on both changed pages.

## 9. Round 3 update (2026-10-21): full-site audit and polish pass

Audited all 199 HTML pages across: titles, meta descriptions, canonicals, heading hierarchy,
image alt/dimensions, OG/Twitter completeness, favicon/manifest links, JSON-LD validity,
anchor targets, sitemap coverage, table semantics, link security, and accessibility markers.

Found and fixed (all additive or tag-level; no content removed):

- Heading hierarchy: 98 lab pages had h2 to h4 skips (challenge cards) and 18 had h1 to h3
  skips (objectives callouts). Re-leveled to h3 and h2 respectively across 116 files, with CSS
  updates (`.lab-challenge h3` pinned to the old h4 look; `.lab-objectives h2` neutralizes the
  h2 bar chrome) so the visual design is unchanged.
- Meta descriptions: 4 docs pages exceeded 170 chars; trimmed (visible text unchanged).
- Added site-wide: `theme-color` meta (173 pages), og:image width/height from measured
  dimensions via sips (175 pages, 44 distinct images), `scope="col"` on thead th cells
  (160 pages), skip-to-content links with `#main-content` targets (all pages), and
  `aria-current="page"` on active nav links (193 pages).
- CSS: new `.skip-link` rule (hidden until keyboard focus). Reduced-motion and focus styles
  were already present.
- Tooling: fixed `.tools/check_links.py` false positives (now URL-decodes percent-encoded
  paths, resolves root-absolute paths against the site root, and maps directory links to
  index.html). Result: 199 pages checked, 0 broken refs, 0 nav problems, no false positives.
- Sitemap lastmod bumped to 2026-10-21 for the 116 heading-fixed pages; sitemap remains
  valid XML.

Final state: comprehensive audit reports ALL CLEAN on 199 pages; 649 JSON-LD blocks valid;
SEO audit 198/199 fully covered (the exception is the deliberately noindex 404 page);
HTTP smoke 200 on sampled routes across all sections.
