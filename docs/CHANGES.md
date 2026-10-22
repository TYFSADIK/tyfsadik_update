# CHANGES.md - SEO Overhaul Change Log

Every modification made during the seo-overhaul branch work, with before/after
context. Per hard rule 1, nothing was deleted; layout fixes are logged here.

## Phase 0 (commit 5dc6512)

- Added `docs/SITE-INVENTORY.md`, `docs/ASSUMPTIONS.md`,
  `docs/REPO-CLEANUP-PROPOSAL.md`, `docs/baseline/` (manifest, Lighthouse,
  axe, screenshots, html-validate, link check).
- No page content changed.

## Phase 1: bug fixes

### Regression repairs from earlier rounds

- Repaired `<th scope="col"ead>` corruption (a broken `<thead>` tag) across
  ~160 pages back to `<thead>`. Before: invalid tag broke table header
  rendering semantics. After: valid thead, no visual change.
- Removed duplicated `aria-current="page"` attributes on nav links in 20
  files. Before: duplicate attribute (invalid HTML). After: single attribute.
- Escaped raw `<` characters inside Mermaid diagram source blocks
  (`<-->`, `<--`) as `&lt;` in 6 files, and raw `<` inside `<pre>` blocks in
  7 files. Before: html-validate errors. After: 0 errors across 199 pages.
- Removed 5 stray `</div>` end tags at line ends in databases lab pages
  (azure-sql-deployment, backup-recovery, cloud-database-config,
  constraints-keys, joins-complex-queries). Content unchanged.
- Added `aria-label="Breadcrumb"` to 142 breadcrumb `<nav>` elements.
- Added `type="button"` to 421 `<button>` elements missing an explicit type.
- Fixed `&2;` typo entity to `&amp;2;` in 1 file.
- Wrapped header rows in `<thead>` with `<th scope="col">` in
  `work/infrastructure/tyf-ai-platform.html` and
  `blog/labs/cloud-azure/cost-management.html`.
- Result: `html-validate` reports 0 errors on all 199 pages.

### Color contrast (WCAG 2.2 AA)

- `css/style.css`: `--accent` changed from `#5B93EF` to `#64A0F2`.
  Before: 4.4:1 or less on elevated surfaces, axe color-contrast serious on
  blog/labs/index.html (27 nodes) and one lab page (16 nodes).
  After: passes 4.5:1 on both #2E2E2E and #333333. axe sweep: clean on all 10
  key pages.
- `css/style.css`: `.difficulty-advanced` badge text color changed from
  `var(--red)` (#E06060, 3.83:1) to `#E87A7A` (4.77:1). Badge still reads as
  red; only brightness increased.

### Lab track anchors and homepage links

- `blog/labs/index.html`: added ids to the 9 category headers
  (`linux-fundamentals`, `linux-server-administration`, `networking`,
  `security`, `python-automation`, `databases`, `cloud-azure`,
  `containers-kubernetes`, `version-control-devops`).
- `index.html`: the 9 "DevOps in Practice" links previously all pointed to
  `blog/labs/index.html`. They now point to `blog/labs/index.html#<track>`
  matching the anchors above. No link removed; the plain index links at other
  spots on the page are unchanged.

### "What I Did" section (index.html)

- The heading "What I'm Doing, What I Did, What's Next" had no "What I Did"
  content. Added `<h3>What I did</h3>` with 6 bullets drawn only from facts
  already published on the site (25% MTTR cut, 30+ automated alerts, 7-node
  Kubernetes cluster, zero-trust Proxmox cloud, 116 labs, 99%+ healthcare
  uptime, 25+ certifications), linking to the existing project/lab/resume
  pages. No new claims introduced.

### No-JavaScript pre-render (index.html)

- Before: `#recent-labs`, `#featured-projects`, and the four At a Glance
  counters were empty (or "-") with JavaScript disabled.
- After: `.tools/build_prerender.py` reads `site-data.json` and injects
  static HTML between `PRERENDER` marker comments for the labs and featured
  cards; the counters now carry hardcoded fallback values (4+, 25+, 44, 9)
  matching site-data.json. The existing JS still replaces the content via
  innerHTML at runtime, so there is no duplication.
- Descriptive link text: the injected "Read more" links (also in the JS
  template) became "Read the {title} lab". Before: Lighthouse SEO 92
  (link-text failure). After: link text describes the destination.

### External link hardening

- All `target="_blank"` links across 199 pages now use
  `rel="noopener noreferrer"` (previously `noopener` only). 199 files
  touched by scripted attribute addition; no URLs changed.

### 404 page

- `404.html`: added a labelled search form (GET to the labs index, `?q=`)
  and a "Popular pages" list (Kubernetes cluster, Defence Hardware Program,
  VLAN lab, SOC pipeline lab, Chakor). Kept `noindex, follow` and all
  existing links. Added matching form styles to `css/style.css` (new
  additive block: `form[role="search"]`, input focus states, 44px targets).

### Person schema jobTitle alignment

- `index.html`, `about.html`, `resume.html`: JSON-LD `jobTitle` changed from
  "Cybersecurity & IT Infrastructure Specialist" to "Cybersecurity & IT
  Professional", matching the site tagline visible in every page header.
  Listed in CLAIMS-TO-VERIFY.md for confirmation.

## External link check

- `.tools/check_external_links.py` collects unique outbound URLs and checks
  status. Results in `.tools/external-links.json`: 79 unique URLs, 15 non-200.
- Fixed: `pve.proxmox.com/wiki/Deploy_Hyper_Converged_Ceph_Cluster` (404) to
  the current `Deploy_Hyper-Converged_Ceph_Cluster` (200) in
  `work/infrastructure/proxmox-zero-trust.html`.
- Not changed (need owner decision, logged in CLAIMS-TO-VERIFY.md): nine
  GitHub repo URLs returning 404 (private or renamed repos), and one dead
  senecac.on.ca link that exists only in the internal `.tools/ref/` folder.
- 403 responses from dell.com, rsync.net, and linkedin.com are bot blocking;
  the links work in a browser.
