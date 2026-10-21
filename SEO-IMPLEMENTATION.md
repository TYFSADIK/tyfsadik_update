# SEO / AI-Discoverability Implementation Report (Round 5)

Date: 2026-10-20. Scope: additive improvements only; no existing page, content,
design element, or metadata was removed except where explicitly noted as a
correction of invalid markup.

## Baseline audit findings

- Static HTML site, 193 public pages, GitHub Pages (CNAME `tyfsadik.org`), no build step.
- Prior SEO rounds already provided: unique titles, meta descriptions, canonicals,
  OG/Twitter cards, BreadcrumbList JSON-LD on all 193 pages, FAQPage JSON-LD on
  labs and defence pages, and a sitemap covering 193/193 pages.
- Gaps found and fixed in this round: see below.

## What was implemented

### Favicon and headshot (Google favicon eligibility)

- The existing `favicon.png` (orange brand mark, 36x64) is preserved untouched on
  every page. Google requires a square icon that is a multiple of 48x48, so new
  icons were generated from the real headshot `Portrait.png` (896x1194,
  square center-crop, resampled with sips):
  - `favicon-48.png`, `favicon-32.png`, `favicon-16.png`
  - `icon-192.png`, `icon-512.png`
  - `apple-touch-icon.png` (180x180)
- `site.webmanifest` added (name, description, 192/512 icons, theme `#333333`).
- All 193 pages now link the new icons and the manifest, appended after the
  existing favicon link, using the same relative-path convention as the
  stylesheet links (`.tools/add_icons.py`).

### Person entity and Knowledge Panel readiness

- Single canonical entity `https://tyfsadik.org/#person` now reused everywhere:
  244 inline `author`/`about` Person references across 190 files gained the
  matching `@id` (`.tools/person_id.py`).
- `about.html` Person JSON-LD corrections:
  - `image` changed from `favicon.png` (a 36x64 logo) to the real portraits
    `Portrait.png` and `images/portrait.jpg`.
  - `worksFor` aligned with the visible work experience (Microsoft,
    Felixous Technology Inc.); two organizations not present in the visible
    content were removed from the structured data.
- `index.html` Person JSON-LD gained `@id` and `image`, so the homepage and
  About page describe the same entity.
- `about.html` gained the portrait as an additional `og:image` (896x1194);
  the existing banner image remains.
- Removed the deprecated `SearchAction` (sitelinks search box) from the
  homepage WebSite JSON-LD; Google retired that feature and the targeted
  `?s=` endpoint does not exist on this site. Replaced with a `publisher`
  reference to `#person`.

### AEO: real FAQ on the About page

- New visible "Frequently Asked Questions" section on `about.html` (six Q&As,
  all answers consistent with the visible page content), plus matching
  `FAQPage` JSON-LD. Note: Google only shows FAQ rich results for a small set
  of authoritative sites; this markup primarily helps answer engines and
  LLM-based retrieval.

### Images, performance, CLS

- 32 `<img>` tags that lacked `width`/`height` received correct intrinsic
  dimensions plus `loading="lazy"` (project hero images, 1600x1067 and
  1536x1024), reducing layout shift.
- All images already had descriptive `alt` text (verified: zero missing).

### Crawl hygiene and supporting files

- `robots.txt`: added `Disallow` for `/.tools/`, `/__pycache__/`,
  `/round4-logs/` (repo tooling published with the site but not content).
  All content, CSS, JS, and images remain fully crawlable. No AI crawler is
  blocked; the wildcard allow covers them.
- `sitemap.xml`: all 193 `<lastmod>` values refreshed to 2026-10-20; coverage
  re-verified at 193/193 public pages.
- `llms.txt`: new, optional site map for LLM/agent consumers (identity, key
  pages, project collections, lab tracks, fetch notes).
- `404.html`: new design-consistent error page (site header/footer, links to
  main sections, `noindex, follow`, root-absolute asset paths so it renders at
  any URL depth on GitHub Pages).

### HTML validity fixes

- Removed a stray `">>` (double closing bracket) after meta tags in 6 files:
  `about.html`, `resume.html`, `blog/labs/linux-fundamentals/index.html`,
  `number-systems.html`, `startup-files.html`, `nested-vms-kvm.html`.

## Validation performed

- All 639 JSON-LD blocks across the site parse as valid JSON (0 invalid).
- `sitemap.xml` is well-formed XML; `site.webmanifest` and `site-data.json`
  are valid JSON.
- `.tools/seo_audit.py`: 193/193 content pages fully covered (title, meta
  description, canonical, OG, Twitter, JSON-LD). The only page without those
  tags is `404.html`, intentionally (`noindex`).
- `.tools/check_links.py`: 0 nav problems. Remaining "MISSING" entries are
  checker false positives: it does not URL-decode `%20` (Prove/ image paths)
  and does not map site-root-absolute paths (`/contact.html` in 404.html).
  All were verified to return HTTP 200 through a local server.
- Local server smoke test (`python3 -m http.server`): 200 for `/`, about,
  404, all new icons, manifest, llms.txt, robots.txt, sitemap.xml,
  Portrait.png, a nested lab page, a nested project page, and a
  percent-encoded Prove image path.

## What was intentionally NOT done

- No `noindex` on any content page; no canonicals pointed at the homepage.
- No keyword changes to existing titles/descriptions; no content removed.
- The orange `favicon.png` brand mark remains in place on all pages.
- No favicon.ico was generated (no ICO encoder available offline; PNG icons
  plus apple-touch-icon cover Google Search and all modern browsers).
- No Google Business Profile, no fake local listing, no app-store metadata
  (no published app exists in this repo), no Search Console action (no
  authorized access from this environment).

## Outstanding external steps (require authorized accounts)

1. Google Search Console: verify the `tyfsadik.org` domain property, submit
   `https://tyfsadik.org/sitemap.xml`, and request indexing for the homepage
   and About page via URL Inspection.
2. Bing Webmaster Tools: same sitemap submission.
3. LinkedIn/GitHub: ensure the profile "website" fields point to
   https://tyfsadik.org/ so `sameAs` links are reciprocal (helps entity
   reconciliation for a Knowledge Panel).
4. Knowledge Panels are assigned by Google automatically; structured data only
   makes the site eligible. There is no submission mechanism for personal
   panels.
