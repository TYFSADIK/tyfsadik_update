# DESIGN_NOTES.md — Redesign after littlesvr.ca

Visual redesign of tyfsadik.org to match the look of littlesvr.ca
(colors, layout, typography, component styles). All site content, URLs,
file names and functionality are unchanged. No text, logo or photos were
taken from the reference site — only design tokens.

Backup of the pre-redesign site: `../tyfsadik_backup/`.

## 1. Extracted design tokens (from littlesvr.ca via getComputedStyle + CSS)

### Colors

| Role | Hex |
|---|---|
| Page background | `#333333` |
| Outer panel (menu/banner panel, content wrapper) | `#3C3B3B` |
| Inner content box / menu box | `#262626` |
| Heading bars, nav items | `#161616` |
| Nav item hover | `#0D0D0D` |
| Menu ring | `#000000` (1px) + inner border `#313131` |
| Body text | `#DBDADA` |
| Emphasized text / headings | `#FFFFFF` |
| Links (normal + visited) | `#5B93EF`, underlined |
| Link hover | same color, underline removed |
| Nav links | `#9FA2A4`, white on hover/current |
| Image frames | 10px solid `#000000` |

### Typography

- `Georgia, "Times New Roman", Times, serif` everywhere; base 14px / 1.5.
- Section headings: 20px bold white on a `#161616` bar (padding 8px 10px).
- Nav links 16px Georgia.
- Departure Mono (existing site font) kept **only** for code blocks, inline
  code, command blocks and terminal sessions, per project instruction.

### Layout

- Fixed 960px container (+10px padding each side → 980px), centered.
- Top panel: 130px tall, site name (32px) + italic tagline left, contact
  link right.
- Menu/banner panel: `#3C3B3B`, 10px padding; 280px vertical nav box on the
  left (black ring + `#262626` inner box, items `#161616`, 4px gaps, `›`
  arrow markers), photo banner filling the rest (~280px tall).
- Content wrapper `#3C3B3B` (10px padding) around a `#262626` content box
  (30px padding).
- Home: 220px sidebar ("Latest Labs" news items: bold white category line,
  bold blue title, excerpt ending in "Read more") + main column ("Who is…?"
  intro with photo, then 2-column project cards).
- Footer: centered, dim text, links white on hover.

The reference has **no responsive behavior at all** (fixed 960px, overflows
on phones). Responsive support was added from scratch per project
requirements: below 860px the nav collapses behind a MENU button, the
banner shrinks, sidebar stacks above the main column, cards go full width.

## 2. Mapping decisions

- **Same class names kept everywhere.** All 174 HTML pages were re-chromed
  by script (`.tools/update_nav.py`): old fixed top-nav replaced by the
  top-panel + vertical-menu + banner header, and content wrapped in
  `.content-box`. The stylesheet keeps every existing class (`.card`,
  `.timeline`, `.lab-meta`, `.step`, …) so no content markup changed.
- **CSS variables kept, values replaced** — inline styles referencing
  `var(--text-muted)` etc. keep working with the new palette.
- **Nav items**: About Me · Work · Blog/Labs · Résumé · Contact, per spec.
  The site name in the banner links home (as on the reference). Current
  section shown in white. Labs/assignments pages highlight "Blog/Labs".
- **Nav structure**: the spec's notes described a horizontal nav bar, but
  the actual reference uses a vertical menu box beside a photo banner —
  the signature element of the design — so the vertical version was
  replicated. On mobile it collapses to a MENU button (spec requirement).
- **Banners**: home + about use a wide crop of `mine.jpeg`
  (`images/banner-mine.jpg`, 1300×560); all other pages use the existing
  `images/black-hole.jpg` art (`images/banner-space.jpg`). No external
  photos used.
- **Photo**: `images/mine.jpg` — 400px-wide portrait crop of `mine.jpeg`
  (original kept in root untouched), used on home "Who is Taki Sadik?" and
  About. Shown with the reference's 10px black frame.
- **Thumbnails**: the reference cards have photo thumbnails; the site has
  no project thumbnails and none were invented. Cards use the reference's
  title-bar + blurb + "Read more" anatomy without images.
- **Resume page**: reference shows page images; we have none, so the
  existing online résumé content is kept under an "Online View" heading,
  with a "Download My Résumé" header + PDF link (per spec).
- **Contact page**: new `contact.html` (linked from every nav). No backend
  exists, so it is a label/field table with the existing contact details
  (email, phone from the site's own JSON-LD, LinkedIn, GitHub, location)
  plus a mailto button — no form service was invented.
- **Mermaid diagrams**: theme variables in `js/main.js` recolored to the
  new palette (`#161616`/`#262626` surfaces, `#5B93EF` borders).
- **Contrast (WCAG AA)**: reference link blue `#5B93EF` on `#262626`
  ≈ 4.9:1 — passes AA. Difficulty-badge colors were minimally brightened
  for AA on dark surfaces (green `#6FCF6F`, yellow `#E6C947`, red
  `#E06060`). Muted text uses `#B5B4B4` / `#9FA2A4`, both ≥ 4.5:1.

## 3. Files changed

- `css/style.css` — rewritten around the reference tokens (same class API).
- `js/main.js` — mermaid palette, `aria-expanded` on the nav toggle,
  anchor-scroll offset (header is static now).
- All 174 existing `.html` files — header/nav replaced + `.content-box`
  wrapper via `.tools/update_nav.py` (scriptable, idempotent).
- `index.html` — restructured to the reference home layout (sidebar latest
  labs + stats, main "Who is" + featured projects + contact).
- `about.html` — added portrait photo; `theme-color` updated.
- `resume.html` — "Download My Résumé" header + "Online View" section;
  `theme-color` updated.
- `contact.html` — new page.
- `images/mine.jpg`, `images/banner-mine.jpg`, `images/banner-space.jpg` —
  new optimized images derived from existing assets.
- Unchanged: CNAME, favicon, LICENSE, README, the résumé PDF, all URLs,
  `site-data.json` mechanism (verified rendering: stats, latest labs,
  featured projects).

## 4. Verification

- Served with `python3 -m http.server`; screenshotted 10 templates ×
  {1280, 375}px (`.tools/shots/`) and compared against reference shots.
- `.tools/check_links.py`: 175 pages, 0 broken internal refs, identical
  nav on every page.
- Horizontal-overflow audit at 1280px: fixed a `.step-body` grid overflow.
- Mobile nav toggle verified (opens, sets `aria-expanded`).

## 5. Notes / things you may want to supply

- Project thumbnails if you want the reference's full card look on the
  Work page.
- Résumé page images if you want the reference's page-per-image online
  view (currently the existing HTML résumé is shown instead).
- `.tools/` contains the redesign tooling (venv, reference snapshots,
  screenshots, scripts). Dot-folders are excluded from GitHub Pages/Jekyll
  builds; delete it if you don't want it in the repo.

## 6. Addendum - content update (Sep 2026)

- All em dashes (`—` / `&mdash;`) removed from every HTML page and
  `site-data.json`, replaced with hyphens or commas. (Repair note: the
  first pass also collapsed `--` sequences; `var(--...)`, `<!--` and `-->`
  were restored and verified.)
- `index.html` expanded: "Current Focus: Defence & DevOps" (career goal,
  honestly framed, linking CAF digital-transformation coverage), "DevOps in
  Practice" (links to 7 real, existing labs with their own descriptions),
  "What I'm Building Next" (clearly labeled homelab roadmap), and a
  "Currently Pursuing" sidebar box (Security+, CCNA).
- No fabricated projects or claims were added; everything on the site
  reflects real work or clearly-labeled future plans.
