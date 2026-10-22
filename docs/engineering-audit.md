# Engineering Audit — tyfsadik.org

Internal development document. Records discovered architecture, project inventory status,
limitations, and prioritized work. No secrets, internal IPs, serial numbers, or private
topology details are recorded here. Public-facing equivalents live under `docs/` on the site.

Last reconciled: 2026-10-21.

## 1. Platform baseline

- Static HTML/CSS/JS site, no build step. Deployed via GitHub Pages with a CNAME for
  tyfsadik.org. Local working copy is not itself a git repository; changes are synced to the
  published repository by the owner.
- Styling: `css/style.css` (single stylesheet, design tokens inline). Script: `js/main.js`
  (navigation, back-to-top, Mermaid init, copy buttons on all `pre` and `.command` blocks).
- Mermaid: mermaid@11 via jsDelivr CDN, initialized globally in `js/main.js`.
- Favicons: orange brand mark at all sizes (`favicon.png` 36x64 original plus square 16/32/48,
  `apple-touch-icon.png` 180, `icon-192/512.png`, `brand-*` duplicates). Generator script:
  `.tools/make_square_favicon.py` (pure-Python PNG codec; no PIL on this machine).
- Tooling: `.tools/check_links.py`, `.tools/seo_audit.py` (writes `.tools/seo_audit.json`),
  `.tools/audit_mermaid.py`. Known false positives in check_links: no URL-decoding of `%20`,
  no mapping of root-absolute `/...` paths.
- No analytics, no third-party trackers, no credentials in repo.

## 2. Content inventory (routes)

- 194 URLs in sitemap.xml after this round: 5 top-level pages, `docs/` section (4 pages),
  blog/labs indexes, 44 project pages under `work/` (5 categories), lab/assignment pages,
  `404.html` (noindexed).
- Project counts: infrastructure 15, defence 11, applications, games, web development;
  total 44 as shown on `work.html` and in `site-data.json` (`projects_built: "44"`).

## 3. Structured data and metadata baseline

- 639 JSON-LD blocks site-wide, all parse-valid (checked with a Python extractor).
- Person entity: `@id https://tyfsadik.org/#person`, referenced from 190 files / 244 refs.
  Image array on index.html and about.html includes `images/taki-sadik-headshot.jpg`,
  `Portrait.png`, `images/portrait.jpg`.
- robots.txt allows all content, disallows tooling/internal dirs. llms.txt present and updated
  with the new docs section. sitemap.xml lastmod dates kept accurate for changed pages.

## 4. Infrastructure evidence status

Physical layer (CONFIRMED, photographed): 3 desktop Proxmox VE 8.x hosts, 4 laptop Proxmox
hosts, managed switch (VLANs 10/20/30), router (NAT/DHCP/inter-VLAN), 5 GHz bridge radio,
ops desk. See `work/infrastructure/homelab-server-room.html`.

Logical layer (CONFIRMED via documentation): 7-VM kubeadm Kubernetes cluster; pinned versions
used in docs: Kubernetes packages v1.30, Calico v3.28.0, MetalLB v0.14.5, Longhorn v1.6.2,
cert-manager v1.15.0, ingress-nginx v1.10.1, Ubuntu 24.04 guests, Proxmox VE 8.x.

Owner-stated expansion (PARTIALLY VERIFIED / UNKNOWN, evidence source = owner
statement 2026-10-21, updated the same day with configuration-level testimony): 3 hosting
racks plus a separate large GPU stack and a small standalone Raspberry Pi position; 24x
OptiPlex 5060 SFF hosting fleet (owner-stated workloads: self-hosted media library for
movies/series/anime, Chakor AI serving ai.tyfsadik.org, general self-hosted services); 4 JBOD
enclosures with ~2 PB intended raw aggregate; Cisco switching (models UNKNOWN); Raspberry Pi
utility server running Pi-hole, security monitoring, and a domain watchdog (board model/count
UNKNOWN); GPU rental stack of 20x OptiPlex 5060 SFF (owner-stated per unit: i7-8700 6C/12T,
16 GB DDR4-2666 2x8, 2x DP, GbE only) each with an RTX 4090-class GPU. Owner spec says
"4090 Ti"; no such NVIDIA SKU exists as of 2026-10-21, recorded as 4090-class pending
nvidia-smi evidence. Chassis/PSU/cooling infeasible in unmodified SFF, so the power and
mechanical integration method is the top open documentation gap (see
`docs/asset-register.html` for the analysis and citations).

Editorial decision: one owner-stated workload was deliberately left off the public site because
publishing it would create copyright, professional, and hosting-ToS exposure for the owner.
It is not recorded in this repository either; it was flagged to the owner directly in the
session summary.

## 5. Known limitations

- Per-host makes/models, CPU/RAM, drive populations, wattage: not yet measured or published.
- No UPS instrumentation; no environmental sensors in the server room.
- Mermaid diagrams on the two deepened pages (tyf-ai-platform, data-sovereignty-stack) have
  not been browser-render-verified; the shared renderer is the same one used by audited pages.
- Local link checker has false positives (see section 1); manual spot checks compensate.
- Files in the working copy were externally reverted once during this engagement (sync or
  re-extraction). All changes were re-applied and verified; deploy/commit promptly after
  future sessions to minimize the window.

## 6. Prioritized work

1. Collect per-host evidence (lshw/dmidecode/SMART/switch configs/photos) to move
   PARTIALLY VERIFIED asset rows to CONFIRMED (`docs/asset-register.html` checklist).
2. GPU cluster: resolve host platform before purchase (tower workstations, open frames, or
   SFF-class GPUs); commission electrical/HVAC assessment for a multi-kW continuous load.
3. Add UPS units with NUT telemetry into Prometheus; add room temperature/humidity sensor.
4. Inline power metering per circuit/rack; publish measured wattage.
5. Continue deepening thin project pages to the case-study standard.
