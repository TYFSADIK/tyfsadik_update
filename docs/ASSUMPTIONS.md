# ASSUMPTIONS

Decisions made autonomously during the seo-overhaul branch work, newest first.
Each entry: the choice, why, and what to change if it was wrong.

## 2026-10-22

1. **Branch and baseline commit.** The previous session's work was already committed to
   `main` (commit `9b7a5d9`). The overhaul happens on branch `seo-overhaul` cut from that
   commit, one commit per phase. `main` is never committed to directly.

2. **Real design tokens.** The site is NOT Tokyo Night and does not use JetBrains Mono or
   IBM Plex Sans. The actual palette is a gray theme (`--bg: #333333`, panels `#3C3B3B`,
   accent `#5B93EF`) with Georgia serif body text and Departure Mono (self-hosted in
   `fonts/`) for code. `theme-color: #333333` (added last session) matches the real
   background, so it stays. No restyling per hard rule 8.

3. **og:image policy.** Hard rule 3 (banner-mine.jpg as og:image and twitter:image on every
   page) conflicts with the per-project og:images added previously (rule 1 says remove
   nothing). Resolution: banner-mine.jpg becomes the FIRST og:image (the preview crawlers
   use) and the twitter:image on every page; existing page-specific og:image tags stay as
   secondary images. If a page-specific preview is preferred for a project page, revert that
   page's ordering; do not delete tags.

4. **favicon.png lock.** sha256 baseline:
   `4a95fe99473fd1711d5fd1735387e67d9abb046d5f8fbdc1bff983b24198379f` (36x64 original).
   Verified at the end of the branch work. The square variants (favicon-16/32/48,
   apple-touch-icon, icon-192/512) are separate files and stay untouched too.

5. **Tooling location.** New build/verify scripts go in `.tools/` (already used, already
   robots-disallowed) with the Node e2e harness in `.tools/e2e/` using system Chrome via
   playwright-core `channel: 'chrome'` (no browser download). Node dependencies are
   gitignored content; CI installs them fresh.

6. **Job title in Person schema.** The mission says jobTitle must match the header text
   ("Cybersecurity & IT Professional"). The existing schema says "Cybersecurity & IT
   Infrastructure Specialist". The header is the visible source of truth per rule 5, so
   schema is aligned to the header text. Both phrasings appear on the site; the header wins.

7. **alumniOf and employers.** Person schema already contains `alumniOf` (Seneca, U of T);
   both are stated in visible page copy, so the schema is consistent with rule 5 and stays.
   `worksFor` is NOT added anywhere. Employers named in visible copy (Microsoft, Felixous,
   CardiOCare) are listed in docs/CLAIMS-TO-VERIFY.md for the owner to confirm.

8. **GitHub Pages + .nojekyll.** The repo has no Jekyll config and is deployed as plain
   static files. An empty `.nojekyll` file is added so Pages skips Jekyll processing and
   `/.well-known/` and dotfile paths serve correctly. Verified the existing workflow does
   not conflict (see docs/baseline for the check).

9. **Owner-stated infrastructure.** The asset register's PARTIALLY VERIFIED rows (24-unit
   OptiPlex fleet, 4 JBODs, 2 PB raw target, GPU stack, Cisco and Pi gear) rest on owner
   testimony only. No new copy upgrades those claims; keyword work references only what the
   pages already state.

10. **Screenshot/Lighthouse scope.** The viewport matrix is run against 8 key pages (home,
    about, work, resume, blog, labs index, one lab, one defence project), not all 199.
    Full-site checks (links, headings, metadata, JSON-LD) cover every page.
