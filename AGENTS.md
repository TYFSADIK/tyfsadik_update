# AGENTS.md - rules for any agent working on this repo

## What this is

Static portfolio site for MD. Taki Yasir Faraji Sadik (Taki Sadik), served at
https://tyfsadik.org via GitHub Pages (Jekyll pipeline, see
.github/workflows/jekyll-gh-pages.yml) with Cloudflare in front. Plain HTML,
one stylesheet (css/style.css), one script (js/main.js), no framework.

## Hard rules

1. REMOVE NOTHING. Do not delete, rename, or move any existing file, page,
   section, link, image, or text. Add or improve only. If something visibly
   breaks layout, fix it and log before/after in docs/CHANGES.md.
2. favicon.png must stay byte-identical. Baseline sha256:
   4a95fe99473fd1711d5fd1735387e67d9abb046d5f8fbdc1bff983b24198379f
3. images/banner-mine.jpg is the first og:image and the twitter:image on
   every page. Do not create per-page generated social images.
4. Do not invent facts: no employers, titles, dates, degrees, certifications,
   metrics, or testimonials that are not already on the site or in
   site-data.json. Open questions go in docs/CLAIMS-TO-VERIFY.md.
5. Structured data must describe content visible on the same page.
6. No spam tactics: no keyword stuffing, hidden text, cloaking, doorway
   pages, fake ratings, or fabricated authority.
7. No em dashes anywhere in copy. Use hyphens, commas, colons, semicolons.
   No filler words (passionate, cutting-edge, leverage, robust, seamless,
   delve, unlock, game-changing).
8. Keep the design language: dark grey panels, Georgia serif, Departure Mono
   for code/nav accents. Do not restyle for its own sake.
9. Work happens on feature branches (current: seo-overhaul), one commit per
   logical phase. Never force-push, never commit directly to main.

## Build scripts (all idempotent, run from repo root)

- python3 .tools/build_prerender.py    # inject site-data.json content into index.html
- python3 .tools/build_sitemap.py      # sitemap.xml with git lastmod + image extension
- python3 .tools/build_feeds.py        # feed.xml, atom.xml, feed.json
- python3 .tools/build_search_index.py # search-index.json for the labs search
- python3 .tools/build_md_mirrors.py   # .md mirrors + llms-full.txt
- python3 .tools/build_api.py          # api/{profile,projects,labs,skills}.json
- python3 .tools/phase3_titles.py      # validates every title/description length
- python3 .tools/check_links.py        # internal link checker
- python3 .tools/validate_jsonld.py    # parses every JSON-LD block
- python3 .tools/check_og_image.py     # banner-mine.jpg first og:image on every page
- bash tools/verify.sh [--full]        # local mirror of the CI quality gates
- .tools/e2e: npm project with playwright-core, lighthouse, axe-core,
  html-validate (uses system Chrome; set CHROME_PATH in CI)

After editing site-data.json, run build_prerender, build_feeds,
build_search_index, and build_api.

## Conventions

- Depth-0 pages use bare relative paths; depth-1 (docs/, about/) use ../;
  depth-2 (work/*/, blog/labs/*/) use ../../. 404.html uses root-absolute
  paths because it serves under arbitrary URLs.
- Mermaid diagrams: <div class="mermaid" role="img" aria-label="..."> with
  < escaped as &lt;. Diagrams are pre-rendered to inline SVG at build time
  (cd .tools/e2e && node prerender_mermaid.mjs); the source lives in an
  inert <template class="mermaid-source"> inside each div. After adding or
  editing a diagram, re-run the prerender script. js/main.js only loads the
  mermaid library for divs without data-prerendered (runtime fallback).
- New public pages need: unique 50-60 char title, 140-158 char description,
  canonical, og/twitter block (banner-mine first image), breadcrumb +
  BreadcrumbList, sitemap entry (rerun build_sitemap.py).
- .md files without front matter are served verbatim by the Jekyll pipeline;
  that is how the markdown mirrors work. Never add front matter to them.
- images are served with AVIF/WebP <picture> sources next to the original
  jpg/png; keep the originals.

## Where things live

- docs/CHANGES.md: every modification, with before/after
- docs/ASSUMPTIONS.md: decisions made without owner confirmation
- docs/CLAIMS-TO-VERIFY.md: facts the owner must confirm
- docs/MANUAL-TASKS.md: account-level tasks (Search Console, Bing, IndexNow)
- docs/SITE-INVENTORY.md: full page inventory
- docs/baseline/: Phase 0 measurements (Lighthouse, axe, screenshots)
