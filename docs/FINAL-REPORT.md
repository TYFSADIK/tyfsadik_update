# Final report: seo-overhaul branch

Scope: full SEO, GEO, AEO, accessibility, performance, and machine-readability
overhaul of tyfsadik.org on the `seo-overhaul` branch. 16 phases, one commit
per phase. Nothing was deleted; every change is additive or a logged fix.

## Measured results (Lighthouse, mobile, local server)

| Page | Perf before | Perf after | A11y before | A11y after | Best practices | SEO before | SEO after |
|---|---|---|---|---|---|---|---|
| index.html | 56 | 99 | 100 | 100 | 100 | 92 | 100 |
| about.html | 61 | 99 | 100 | 100 | 100 | 100 | 100 |
| work.html | 57 | 91 | 100 | 100 | 100 | 100 | 100 |
| resume.html | 58 | 99 | 100 | 100 | 100 | 100 | 100 |
| blog.html | 59 | 100 | 100 | 100 | 100 | 100 | 100 |
| blog/labs/index.html | 58 | 99 | 96 | 100 | 100 | 100 | 100 |
| lab page (azure-sql-deployment) | 56 | 90 | 92 | 100 | 100 | 100 | 100 |
| defence page (sky-passive-radar-node) | 57 | 96 | 100 | 100 | 100 | 100 | 100 |
| contact.html | not in baseline | 100 | not in baseline | 100 | 100 | not in baseline | 100 |
| how-this-portfolio-is-built.html | new page | 90 | new page | 100 | 100 | new page | 100 |

After-minification spot check: index 100, lab page 90. Lab pages are capped
around 90-93 by the shared stylesheet's unused rules; splitting CSS per page
is deliberately not done (one stylesheet keeps every page consistent and
cacheable). Baseline JSONs: docs/baseline/lighthouse/. Final JSONs:
docs/baseline/final-lighthouse.json. Numbers are lab measurements on a local
server; field data from CrUX/Search Console will differ.

Core Web Vitals on index after the overhaul: LCP 1.7-2.0 s, CLS 0, TBT near
zero. Zero horizontal overflow at 320, 375, and 768 px widths (checked by
script across the doc).

## Bugs fixed (full detail in docs/CHANGES.md)

- All 9 "DevOps in Practice" track links pointed to the labs index; each
  track now has its own anchor.
- The "What I'm Doing, What I Did, What's Next" heading had no "What I Did"
  section; added one built only from already-documented completed work.
- "At a Glance" counters, "Latest Labs", and "Featured Projects" were empty
  without JavaScript; index.html is now pre-rendered from site-data.json at
  build time with hardcoded fallbacks, and the deploy workflow regenerates it.
- Low-contrast text failed WCAG AA (axe): accent colour adjusted
  (#5B93EF to #64A0F2), advanced difficulty tag fixed. axe is clean on the
  10-page sweep.
- 199 pages missing rel="noopener noreferrer" on target=_blank links.
- 404 page had no search or recovery links; now has both plus noindex.
- Garbage phone row on contact.html ("Vulew Na", tel:+1090...) replaced with
  "Shared after an intro email"; ContactPage schema updated.
- Mermaid was loaded from the CDN eagerly on every page, including the ~180
  with no diagram; now loaded on demand with a pinned, SRI-hashed copy.
- Large images (up to 2.2 MB) had no modern formats or dimensions; 44 images
  now have .webp and .avif siblings, width/height attributes, and lazy
  loading below the fold.
- Tables and code blocks overflowed narrow screens; 241 tables wrapped in
  scroll containers, inline code wraps, 44px tap targets, print stylesheet,
  safe-area insets, 100dvh.
- Hamburger menu did not close on Escape or return focus; fixed.
- Broken Proxmox wiki external link corrected. 9 other external GitHub links
  404 (private or renamed repos); kept per the no-removal rule and listed in
  docs/CLAIMS-TO-VERIFY.md for the owner.

## Files added (111 non-image files, 70 generated .webp/.avif images, 0 deletions)

- New pages: how-this-portfolio-is-built.html, about/facts.html,
  work-with-me.html, offline.html, docs/index.html, docs/asset-register.html,
  docs/glossary.html, docs/decisions.html.
- Feeds: feed.xml, atom.xml, feed.json. Search: search-index.json plus
  client-side search with ?q= support on the labs index.
- Machine-readable: api/profile.json, api/projects.json, api/labs.json,
  api/skills.json; llms.txt expansion; llms-full.txt; 42 .md mirrors linked
  with rel=alternate; humans.txt; .well-known/security.txt; IndexNow key
  file; taki-sadik.vcf; site.webmanifest upgrade with screenshots and
  maskable icons; sw.js service worker (network-first HTML, cache-first
  assets, versioned).
- Docs: SITE-INVENTORY.md, CHANGES.md, ASSUMPTIONS.md, CLAIMS-TO-VERIFY.md,
  MANUAL-TASKS.md, REPO-CLEANUP-PROPOSAL.md, CLOUDFLARE-SETUP.md,
  FINAL-REPORT.md, TITLE-DESCRIPTION-TABLE.md, docs/seo/ (keywords-master.txt
  with 6193 phrases, keyword-map.md/.json for 202 pages, entity-list.md with
  166 entities, content-gaps.md), docs/baseline/ (manifest, Lighthouse runs,
  axe results, screenshots, overflow data).
- Tooling: .tools/ build and validation scripts, .tools/e2e/ (Playwright,
  Lighthouse, axe-core, html-validate, sharp), tools/verify.sh, AGENTS.md.
- CI: .github/workflows/quality.yml (PR gates) and indexnow.yml; the deploy
  workflow now regenerates derived content and minifies CSS/JS in the build
  workspace only.

## Per-page titles and descriptions

All 203 HTML pages: unique 50-60 character titles, 140-158 character
descriptions, canonical URLs, one H1 each, og/twitter tags with
banner-mine.jpg as the first og:image. Full table:
docs/TITLE-DESCRIPTION-TABLE.md.

## Structured data (659 JSON-LD blocks, all parse-valid)

BreadcrumbList 201, HowTo 127, FAQPage 123, TechArticle+LearningResource 116,
TechArticle 65, CollectionPage 13, Person 3, ProfilePage 3, WebPage 2,
AboutPage, Blog, ContactPage, WebSite (with SearchAction backed by the real
?q= search), SoftwareSourceCode (Chakor), ProfessionalService
(work-with-me). Rule: schema only describes visible content; visible FAQ
sections were generated on 122 pages to match pre-existing FAQPage blocks.

## Hard rule confirmations

1. Nothing deleted: `git diff --name-status main...seo-overhaul` shows 0 D
   lines (373 added, 209 modified). All existing URLs work; check_links.py
   reports 0 broken refs across 203 pages.
2. favicon.png byte-identical: sha256
   4a95fe99473fd1711d5fd1735387e67d9abb046d5f8fbdc1bff983b24198379f, checked
   in CI on every PR.
3. images/banner-mine.jpg (1300x560) is the first og:image and the
   twitter:image on all 203 pages (check_og_image.py). Pre-existing
   page-specific og:images were kept as secondary entries; the conflict is
   logged in docs/ASSUMPTIONS.md.
4. No invented facts: every metric (25% MTTR cut, 30+ alerts, 7-node cluster,
   116 labs, 11 hardware builds) traces to pre-existing site copy. Items I
   could not verify are listed in docs/CLAIMS-TO-VERIFY.md, not resolved by
   me.
5. Schema describes only visible content (visible FAQs added where needed).
6. No spam tactics: no hidden text, no keyword stuffing, no doorway pages,
   no fake ratings.
7. Writing style: no em dashes in any newly authored copy (grep-verified;
   the only em dashes in new files are verbatim conversions of pre-existing
   site text in generated markdown mirrors). No filler words.
8. Design unchanged: gray theme, Georgia serif, Departure Mono; theme-color
   #333333 untouched.
9. Branch rules: all work on seo-overhaul, one commit per phase, main
   untouched, no force-push.
10. Repo cleanup is report-only: docs/REPO-CLEANUP-PROPOSAL.md lists
    __pycache__, .tools, Prove, round4-logs, and duplicate assets with
    reference checks; nothing removed.

## What is unverified or blocked on external access

- Google Search Console and Bing verification tokens: placeholders are in
  index.html; owner must paste real tokens (docs/MANUAL-TASKS.md steps 1-2).
- IndexNow: key file is deployed; the ping workflow runs on deploy to main,
  so it activates after merge.
- Cloudflare headers, cache rules, and email DNS hardening: documented
  copy-paste steps in docs/CLOUDFLARE-SETUP.md; require dashboard/DNS access.
- Google Business Profile and Bing Places: step-by-step in
  docs/MANUAL-TASKS.md; require the owner's accounts.
- CLAIMS-TO-VERIFY.md: Seneca naming, employers, U of T B.Eng wording,
  metrics, and 9 external repo links need owner confirmation.
- The CI quality workflow runs on PRs to main; it proves itself on this PR.
- Rankings, indexing, and AI citations cannot be verified from here and are
  not claimed. Backlinks and time drive ranking; this branch removes the
  technical reasons not to rank.

## How to reproduce the checks

    bash tools/verify.sh          # fast gates
    bash tools/verify.sh --full   # adds axe-core and Lighthouse budgets
