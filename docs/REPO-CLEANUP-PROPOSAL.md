# Repo Cleanup Proposal (REPORT ONLY - nothing here has been deleted or moved)

Per hard rule 10, this file only lists candidates. The owner decides. Grep proof
(`grep -rl <name>` over the repo, excluding .git, node_modules, .tools) recorded
2026-10-22 on branch seo-overhaul.

| Item | What it is | Referenced? | Recommendation |
|---|---|---|---|
| `__pycache__/` | Python bytecode caches from old lab scripts | Yes: robots.txt (Disallow), SEO-IMPLEMENTATION.md, one python lab page mentions it | Safe to delete from the repo and add to .gitignore; regenerated locally whenever the scripts run. Owner decision. |
| `.tools/` | Build/validation scripts + node e2e harness | Yes: DESIGN_NOTES.md, ENGINEERING-REPORT.md, robots.txt, and now required by the build script and CI | KEEP. It is the site's tooling. Add `.tools/e2e/node_modules/` to .gitignore instead. |
| `Prove/` | 10 defence hardware bench photos with spaces in filenames | Yes: referenced by all 11 defence project pages and both labs indexes | KEEP. The filenames with spaces are valid (URL-encoded) but a rename would simplify URLs; NOT done (rule 1). |
| `round4-logs/seo_harden.py` | Old one-off SEO script | Only robots.txt and SEO-IMPLEMENTATION.md | Candidate for deletion or archive; owner decision. |
| `ENGINEERING-REPORT.md` | Session engineering reports | Only the baseline manifest | KEEP as living documentation, or fold into docs/. Owner decision. |
| `DESIGN_NOTES.md` | Design system notes | Referenced by css/style.css comment | KEEP (referenced by the stylesheet). |
| `SEO-IMPLEMENTATION.md` | Prior SEO round documentation | Only the baseline manifest | KEEP as history, or fold into docs/. Owner decision. |
| `Portrait.png` (root, 1.5 MB) | Original portrait source | Yes: about.html and index.html Person schema image arrays | KEEP (referenced in structured data). Consider compressing; NOT done (rule 1). |
| `mine.jpeg` (root) | Duplicate of images/mine.jpg? | Only DESIGN_NOTES.md and the manifest | Appears unused by any page. Candidate for deletion after visual comparison with images/mine.jpg. Owner decision. |
| `images/portrait.jpg` vs `images/mine.jpg` | Two portrait files | Both referenced (about.html, index.html) | KEEP both (both referenced). |
| `brand-icon-*.png`, `brand-apple-touch-icon.png` | Duplicate icon set from an earlier naming scheme | Only homelab-server-room.html references brand-icon-48/192 + brand-apple-touch-icon; brand-icon-512 unreferenced | Duplicates of favicon-48 / icon-192 / apple-touch-icon. Candidates for deletion after repointing that one page; NOT done (rule 1). |
| `icon-192.png`, `icon-512.png` | Manifest icons | site.webmanifest + pages | KEEP (required by the web app manifest). |

Notes:
- `.tools/e2e/node_modules/` should be gitignored (added in this branch) to keep the repo lean.
- No action has been taken on any item above. Deleting anything requires explicit owner approval.
