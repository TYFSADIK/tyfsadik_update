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

## Phase 2: responsive, media, and performance fixes

### Horizontal overflow (320-768px)

- resume.html: fixed by the Phase 1 thead repair (verified clean after).
- Wrapped all 241 tables across 162 pages in `<div class="table-scroll">`
  (overflow-x auto) so wide tables scroll inside their own container.
  Verified no wrapper landed inside pre or script blocks; html-validate
  still reports 0 errors.
- `code` inline elements now wrap (`overflow-wrap: anywhere`); `pre code`
  unchanged so code blocks still scroll.
- Verified with Playwright at 320/375/768: zero document-level overflow on
  the three previously failing pages.

### Responsive hardening (css/style.css, additive block)

- `html { scroll-padding-top: 1rem; text-size-adjust: 100%; }`.
- `min-height: 100dvh` upgrade for body with @supports fallback.
- `env(safe-area-inset-*)` padding for notched devices.
- Viewport meta updated to include `viewport-fit=cover` (199 pages).
- 44px minimum tap targets for nav links, buttons, hero links, and lab TOC
  links (Lighthouse target-size failure on lab TOC fixed).
- Print stylesheet: hides banner/nav/buttons, black on white, page-break
  rules, link URLs shown for external links. Resume and lab pages print
  cleanly.

### Mermaid loaded on demand (the big mobile win)

- Before: `mermaid@11` CDN script (about 680 KiB JS, 3.5 MB source) loaded
  eagerly on all 197 pages, including the 17 with no diagrams. Baseline
  mobile performance was 56-61 largely because of this.
- After: js/main.js injects the script only when a `.mermaid` block exists,
  pinned to mermaid@11.17.2 with SRI sha384 and crossorigin. Pages with
  diagrams get a preconnect to cdn.jsdelivr.net. The eager script tag was
  removed from 197 pages (functional change, logged here; diagrams render
  identically).

### Images

- Generated .webp (q82) and .avif (q60) next to every raster image used by
  public pages (44 images; originals untouched). Example: the 2.2 MB
  kubernetes-infrastructure.jpg is now a 176 KB webp / 126 KB avif.
- Wrapped 46 `<img>` tags in `<picture>` with avif and webp sources, jpg/png
  fallback kept. Gifs and .tools/ref internal pages untouched.
- `decoding="async"` added to all imgs; hero portrait on index.html switched
  from lazy to fetchpriority="high".
- Each page's banner image (CSS background, the LCP element on most pages)
  now has a `<link rel="preload" as="image">` (199 pages).
- Font preload for DepartureMono-Regular.woff added to all pages
  (root-absolute on 404.html since it serves under arbitrary URLs).

### JavaScript and navigation

- `js/main.js` now loaded with `defer` on all pages (was render-blocking).
- Mobile menu: Escape now closes it and returns focus to the toggle;
  outside-click close also resets aria-expanded.

### Measured results (Lighthouse mobile, local server)

- index.html: performance 56 -> 99, accessibility 100, best-practices 100,
  SEO 92 -> 100. LCP 2.6s -> 2.0s, CLS 0.
- Lab page (azure-sql-deployment): performance ~60 -> 92, accessibility
  100, SEO 100. LCP 1.6s, CLS 0.
- axe sweep clean on all 10 key pages.

## Phase 3: titles, descriptions, meta, social

- Every page now has a unique 50-60 char title and 140-158 char meta
  description, verified by `.tools/phase3_titles.py` (rerunnable validator).
  11 titles and 27 descriptions rewritten; rewrites applied to title,
  DC.title, og:title, twitter:title, description, og:description, and
  twitter:description together so they never drift.
- `images/banner-mine.jpg` (1300x560) is now the FIRST og:image and the
  twitter:image on all 199 pages, with og:image:width/height/type/alt.
  Page-specific og:images remain as secondary images (documented resolution
  of the hard rule vs earlier per-page social images).
- 404.html gained a full og/twitter block and a keywords tag.
- Added to all pages: format-detection, color-scheme dark, referrer
  strict-origin-when-cross-origin, application-name, geo.region CA-ON,
  geo.placename North York Toronto, msapplication-TileColor,
  mobile/apple-mobile-web-app tags, Dublin Core title/creator/language,
  link rel=author (about page), rel=me (GitHub, LinkedIn).
- article:modified_time added to all article pages from git history.
- Homepage title kept as "Taki Sadik: Cybersecurity, IT, Defence Tech |
  TYFSADIK" (53 chars, brand first, all primary entities); the description
  already carried Toronto, 7-node Kubernetes, and 116 labs.
- Keywords meta kept everywhere and added where missing (404 only).

## Phase 4: structured data

- Audited all 652 JSON-LD blocks across 199 pages: all parse valid.
  Existing coverage confirmed: BreadcrumbList 198, TechArticle 116 labs +
  all work pages, LearningResource 116, HowTo 127, FAQPage 122,
  CollectionPage 13, Person 3, WebSite + speakable on the homepage,
  ProfilePage + speakable on About.
- Added: ProfilePage (mainEntity Person @id) to index.html and resume.html;
  SoftwareSourceCode for Chakor (TypeScript, Next.js 15, facts from the
  visible page). 404.html deliberately carries no JSON-LD (noindex).
- WebSite SearchAction deferred to Phase 8 (needs a real ?q= search first).

## Phase 5: technical SEO

- `sitemap.xml` regenerated by `.tools/build_sitemap.py`: 198 URLs (404
  excluded), lastmod from git history per page, image sitemap extension on
  the 35 pages with a local content image, original priority/changefreq
  scheme kept.
- Feeds: RSS `/feed.xml`, Atom `/atom.xml`, JSON Feed `/feed.json`,
  generated from site-data.json by `.tools/build_feeds.py` (53 items,
  git-dated). All 198 indexable pages link them with rel=alternate.
- IndexNow: key file `149c878bd7aba5f097a1e8ea75a473b8.txt` at root plus
  `.github/workflows/indexnow.yml` which submits changed URLs on each push
  to main (Bing ecosystem; ChatGPT search and Copilot lean on Bing).
- `humans.txt`, `/.well-known/security.txt` (Expires 2027-10-22), and
  `_config.yml` with `include: [".well-known"]` so the Jekyll pipeline
  serves the dotfile directory. The deploy workflow itself is untouched.
- All pages link humans.txt (rel=help) and security.txt (rel=security).
- Google Search Console and Bing verification meta placeholders (empty
  content) added to index.html with instructions in docs/MANUAL-TASKS.md.
  Tokens must come from the owner; nothing faked.
