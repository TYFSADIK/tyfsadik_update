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

## Phase 6: GEO / AEO

- Visible FAQ sections (details/summary, keyboard accessible) generated from
  the existing FAQPage JSON-LD on 122 pages. Before: FAQ structured data
  existed with no visible FAQ content, which violated the "schema must match
  visible content" rule. After: every FAQPage block has a matching visible
  section. about.html already had a visible FAQ, so the generated duplicate
  there was removed (the original stays).
- New page: /about/facts.html, the canonical entity sheet (name variants,
  role, location, focus areas, profiles, key numbers), linked from the About
  page header and llms.txt. AboutPage schema with speakable.
- "Cite This Page" blocks (plain text, BibTeX, APA in a collapsible details)
  on 148 lab and project pages; bylines "Written by Taki Sadik, Last updated
  <git date>" on 170 lab/work pages.
- Markdown mirrors: .tools/build_md_mirrors.py generates 42 .md mirrors
  (home, about, work, resume, contact, blog, labs index, all 9 track
  indexes, docs pages, all 18 defence projects, key infrastructure pages)
  plus llms-full.txt. No YAML front matter, so the Jekyll pipeline serves
  them verbatim (verified assumption documented in ASSUMPTIONS.md).
  rel=alternate type="text/markdown" links added on the 38 mirrored pages.
- llms.txt expanded: per-track lab links with anchors, facts page, feeds,
  markdown mirrors, llms-full.txt, future /api endpoints, citation note.
- robots.txt: explicit allow rules for search crawlers and AI retrieval /
  user-triggered agents (OAI-SearchBot, ChatGPT-User, Claude-SearchBot,
  Claude-User, PerplexityBot, Perplexity-User, Google-Extended,
  Applebot-Extended), plus a commented one-edit switch block to opt out of
  training crawlers (GPTBot, ClaudeBot, CCBot, Bytespider).

## Phase 7: voice search optimization

- speakable (SpeakableSpecification, cssSelector .lead and .faq) added to
  the TechArticle JSON-LD on 160 lab and project pages; homepage and About
  already carried speakable. FAQ questions are already conversational
  ("How do I fix ...?") with direct first-sentence answers, and answer-first
  .lead paragraphs sit at the top of every lab.
- 654 JSON-LD blocks re-validated after the edit, all parse.

## Phase 8: search experience (SXO)

- Static client-side search: `.tools/build_search_index.py` generates
  `search-index.json` (177 items: labs, assignments, projects). A search bar
  on the labs index page filters live, supports `?q=` URLs, and renders
  results without third-party calls (tested in headless Chrome: "vlan"
  returns 6 results). The 404 search form targets the same `?q=` flow.
- WebSite SearchAction added to the homepage JSON-LD, pointing at the real
  `?q=` search (only valid because the search now exists).
- Homepage hero now leads with proof (Toronto, 25% MTTR cut, 7-node
  Kubernetes homelab, 116 labs) with links; the original hero text is
  untouched below it.
- Reading time ("N min read", 200 wpm) added to 170 lab/work page bylines.
- Status added to every defence build byline ("Status: Building"; thermal
  SAR drone: "Building, first results published"), matching the existing
  Status and Roadmap sections. No inflation.
- Copy buttons on code blocks, back-to-top, filter buttons, lab TOCs, and
  scroll progress already existed and are unchanged.

## Phase 9: agent optimization (AAO)

- contact.html: fixed a garbage phone row (tel:+109080808080880808 labeled
  "Vulew Na") to "Shared after an intro email". Placeholder data, not a real
  number; logged here and in CLAIMS-TO-VERIFY.md. ContactPage schema
  description updated to match.
- Added taki-sadik.vcf (no street address) and linked it plus the resume PDF
  from the contact page.
- Static machine-readable endpoints generated by .tools/build_api.py:
  api/profile.json, api/projects.json (44), api/labs.json (116),
  api/skills.json (166 terms from visible project tech stacks).
- data-lab-id and data-track attributes on all 116 lab page <main> elements
  (data-section already existed on the labs index).
- AGENTS.md at the repo root documents the structure, build scripts, and
  hard rules for future agents.

## Phase 10: installability (PWA)

- site.webmanifest upgraded: id, standalone display, lang en-CA, dir,
  categories, 4 shortcuts (Labs, Defence Program, Resume, Contact), wide and
  narrow screenshots (Playwright captures of the real homepage), and
  maskable icon variants.
- New icon files icon-maskable-192.png and icon-maskable-512.png generated
  from the existing icons with safe-zone padding on the site background.
  favicon.png untouched (hash verified at each commit boundary).
- sw.js: minimal service worker, network-first for navigations (fresh HTML
  wins), cache-first for static assets, versioned cache name, skipWaiting +
  clients.claim so deploys take over immediately and stale HTML is never
  served. Offline fallback at /offline.html (noindex, excluded from the
  sitemap). Registration added at the end of js/main.js, load-gated.

## Phase 11: local and map search (MSEO)

- Person schema on index.html and resume.html gained address
  (locality/region/country only, no street) and areaServed (Toronto, North
  York, GTA, Ontario, Canada). about.html already had the address block.
- New page work-with-me.html: services the site already demonstrates
  (small business websites, infrastructure and homelab builds, security
  work), each linked to proof pages, with ProfessionalService schema
  (areaServed, no street address). No doorway pages, one page only.
- contact.html: visible availability line (North York, GTA, remote in
  Canada) and a link to Work With Me.
- docs/MANUAL-TASKS.md: Google Business Profile service-area setup (address
  hidden), Bing Places, and NAP consistency instructions.

## Phase 12: keyword system

- .tools/build_keywords.py generates docs/seo/: keywords-master.txt (6193
  unique phrases), keyword-map.md + keyword-map.json (all 202 pages, one
  primary keyword each derived from its unique title, secondaries from the
  page's own keywords meta, long-tail and question phrases), entity-list.md
  (166 tools/standards/products from site-data.json tech stacks and tags).
- docs/seo/content-gaps.md: 10 prioritized gaps written by hand, including
  what NOT to build (doorway pages) and what needs owner verification first.
- Link checker now exempts 404.html and offline.html from the nav rule.

## Phase 13: portfolio build case study
- Added `how-this-portfolio-is-built.html`: a case study of this site's architecture, build pipeline, measured Lighthouse and Web Vitals results, accessibility results, discovery strategy, and open improvements, with a mermaid pipeline diagram, visible FAQ plus matching FAQPage JSON-LD, cite block, and byline.
- Linked it from the index.html footer ("How this site is built") so it is crawlable, not sitemap-only.
- Regenerated sitemap.xml (now 201 URLs).
- Lengthened the offline.html title and description and the work-with-me.html description to meet the 50-60 / 140-158 character rules introduced in Phase 3.

## Phase 14: performance build step and Cloudflare security docs
- Added `.tools/minify_deploy.py`: dependency-free CSS/JS minifier with balance checks, run only in the CI build workspace (repo sources stay readable).
- Extended `.github/workflows/jekyll-gh-pages.yml`: regenerates prerender/sitemap/feeds/api/search-index and minifies CSS+JS before `jekyll build` (fetch-depth: 0 for git-based lastmod).
- Measured with Lighthouse mobile on the minified output: index 100/100/100/100 (LCP 1.7s, CLS 0), representative lab page 90/100/100/100 (LCP 1.4s). Lab pages are bounded by the shared stylesheet's unused rules; per-page CSS splitting is logged as future work, not done, to avoid breaking any page.
- Wrote `docs/CLOUDFLARE-SETUP.md`: Transform Rule headers (HSTS, nosniff, Referrer-Policy, Permissions-Policy, report-only CSP tuned to actual loads), cache rules, Brotli/HTTP-3/always-HTTPS, www to apex redirect, and SPF/DKIM/DMARC/MTA-STS/TLS-RPT email hardening path.

## Phase 15: CI quality gates and local verification
- Added `.github/workflows/quality.yml` (runs on PRs to main): favicon sha256 check, no-deleted-files check, html-validate, internal link check, title/description length and uniqueness, JSON-LD parse validation, og:image rule check, axe-core sweep, and Lighthouse budgets.
- Added `.tools/validate_jsonld.py` (659 blocks, all valid) and `.tools/check_og_image.py` (203 pages compliant after adding social tags to offline.html).
- `phase3_titles.py` and `check_links.py` now exit non-zero on failures so CI can gate on them.
- `axe-sweep.js` honors CHROME_PATH for CI runners without a preinstalled Chrome.
- Added `.tools/e2e/lh-ci.js` with honest budgets: index perf >= 95, lab pages perf >= 85 (shared stylesheet caps them around 90-93), accessibility/best-practices/SEO 100 everywhere.
- Added `tools/verify.sh` (local mirror of CI; `--full` adds axe and Lighthouse). Full local run passes.

## Post-Phase 16 fixes
- quality.yml: Node 20 -> 22. html-validate 11 uses fs.globSync, which only exists in Node 22.14+; the HTML validation step failed in CI with "fs.globSync is not a function".
