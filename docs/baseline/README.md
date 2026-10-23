# Baseline Summary (2026-10-22, branch seo-overhaul, before changes)

favicon.png sha256: `4a95fe99473fd1711d5fd1735387e67d9abb046d5f8fbdc1bff983b24198379f`

## Lighthouse (local server, system Chrome headless)

| Page | Perf | A11y | Best Practices | SEO |
|---|---|---|---|---|
| about.desktop | 95 | 100 | 100 | 100 |
| about.mobile | 61 | 100 | 100 | 100 |
| blog-labs-databases-azure-sql-deployment.desktop | 95 | 92 | 100 | 100 |
| blog-labs-databases-azure-sql-deployment.mobile | 56 | 92 | 100 | 100 |
| blog-labs-index.desktop | 94 | 96 | 100 | 100 |
| blog-labs-index.mobile | 58 | 96 | 100 | 100 |
| blog.desktop | 95 | 100 | 100 | 100 |
| blog.mobile | 59 | 100 | 100 | 100 |
| index.desktop | 95 | 100 | 100 | 92 |
| index.mobile | 56 | 100 | 100 | 92 |
| resume.desktop | 94 | 100 | 100 | 100 |
| resume.mobile | 58 | 100 | 100 | 100 |
| work-defence-sky-passive-radar-node.desktop | 92 | 100 | 100 | 100 |
| work-defence-sky-passive-radar-node.mobile | 57 | 100 | 100 | 100 |
| work.desktop | 95 | 100 | 100 | 100 |
| work.mobile | 57 | 100 | 100 | 100 |

## axe-core violations

- blog/labs/index.html: color-contrast (serious, 27 nodes)
- blog/labs/databases/azure-sql-deployment.html: color-contrast (serious, 16 nodes), empty-table-header (minor, 1)
- resume.html: empty-table-header (minor, 3)
- work/defence/sky-passive-radar-node.html: empty-table-header (minor, 4)

## Horizontal overflow (scrollWidth > clientWidth)

- resume.html @ 320px
- blog/labs/databases/azure-sql-deployment.html @ 320, 375px
- work/defence/sky-passive-radar-node.html @ 320, 375, 768px

## Key performance findings

- Mobile performance 56-61, desktop 92-95. Dominant issue: 679 KiB unused JavaScript (Mermaid loaded on every page regardless of need).
- LCP mobile ~6-8 s simulated, desktop ~1.2 s. CLS near zero except index mobile (0.10).
- index SEO 92 (investigate: likely the visually hidden h1 pattern or crawlable anchors).

## HTML validation

- html-validate baseline: 3131 findings (see html-validate.txt). After Phase 1 structural repairs: 0 errors with style-opinion rules disabled (.htmlvalidate.json).

## Links

- check_links.py: 199 pages, 0 broken refs, 0 nav problems (link-check.txt).
