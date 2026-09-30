# littlesvr.ca — Design Tokens & Layout Reference

Reference only: colors / fonts / spacing / structure. Do NOT copy any text,
logo, or photography from the source site. Template credit: templatemo.com.

## 1. Global design tokens

### Colors (exact hex, converted from computed rgb())

| Role | Hex | Notes |
|---|---|---|
| Page background | `#333333` | body |
| Outer panel background | `#3C3B3B` | menu/banner panel, content wrapper |
| Inner content background | `#262626` | content box, menu box |
| Section heading bar bg | `#161616` | `.header_01` bar |
| Menu item bg (normal) | `#161616` | each nav `<li>` |
| Menu item bg (hover) | `#0D0D0D` | `li:hover` |
| Menu frame (1px ring) | `#000000` bg + 1px padding | `#templatemo_menu_wrapper` |
| Menu inner border | `1px solid #313131` | `#templatemo_menu` |
| Body text | `#DBDADA` | default `color` |
| Emphasized text | `#FFFFFF` | `.em_text` paragraphs |
| Headings (`.header_01`) | `#FFFFFF` on `#161616` | |
| Link (normal + visited) | `#5B93EF` | underlined |
| Link (hover + active) | `#5B93EF` | **underline removed** on hover |
| Nav link (normal) | `#9FA2A4` | no underline |
| Nav link (hover / current) | `#FFFFFF` | li bg darkens to `#0D0D0D` on hover |
| Thumbnail frame | `10px solid #000000` border | images in main column |
| Button text (`.button_01`) | `#DCDADA`, 11px bold | on a dark button bg-image |

### Typography

- Font stack everywhere: `Georgia, "Times New Roman", Times, serif`
- Base: `font-size: 14px`, `line-height: 1.5em` (21px computed), weight 400
- Section heading (`.header_01`): 20px, white, on `#161616` bar,
  `padding: 8px 0 0 10px`, total bar height 35px, `margin-bottom: 20px`
- Alt heading (`.header_2` style in CSS as `.header_02`): 22px white
- Nav links: 16px Georgia
- Sidebar "news date": 14px bold white; "news title": 14px bold `#5B93EF`
- Paragraphs in main column: `margin-bottom: 15px`
- Form controls: browser defaults (inputs ~13.3px Arial/monospace, white bg)

### Layout / spacing

- **Fixed-width layout, no responsiveness.** Container `#templateo_container`
  (sic, typo in id): `width: 960px; padding: 0 10px; margin: 0 auto`
  → 980px total, centered. At 375px viewport the page simply overflows
  horizontally (no media queries, no collapsing nav, no hamburger).
- Top panel: 960×130px (110px + 10px vertical padding).
- Menu/banner panel: `#3C3B3B` box, 10px padding, 280px inner height.
- Content wrapper: `#3C3B3B` box, `padding: 10px; margin-top: 10px`,
  containing `#262626` content box with `padding: 30px`.
- Inside content: left sidebar column 220px float-left; main column 600px
  float-right. (880px inner = 220 + 60 gap + 600.)
- Card column: `.section_w280` = 280px wide float-left; left card of each pair
  gets `margin-right: 40px`; cards stack in 2-column pairs.
- Spacer divs: `.margin_bottom_10/15/20/30/40/50/60` = empty clearfix divs of
  that pixel height.
- Footer: 940px wide, centered text, `padding: 20px 10px`; footer links white,
  no underline. (Footer is empty on the reference site.)

## 2. Per-page structure

Common chrome (all 5 pages, identical):

```
#templateo_container
├─ #templatemo_top_panel            (960×130)
│  ├─ #site_logo  → a > img 450×110 (left; logo image w/ site name + tagline)
│  └─ #header_menu_section (right)  → .contact_menu a: 90×110 envelope-icon
│                                     image link to contact page
├─ #templatemo_menu_banner_panel    (#3C3B3B, 10px pad, ~300px tall)
│  ├─ #templatemo_menu_wrapper      (280×280, 1px black ring)
│  │  └─ #templatemo_menu           (#262626, 1px #313131 border, 14/28 pad)
│  │     └─ ul > 6 × li             (220×38, #161616 bg, 4px gap, 20px left pad)
│  │        └─ a (block, 10px top pad, 30px left pad for a small arrow-icon
│  │           bg image at left center; 16px #9FA2A4 → white on hover;
│  │           current page: a.current → white text)
│  │     Items, in order: About Me · Current Position · Open Source ·
│  │     Résumé · Trips · Contact   (last li has class "last")
│  └─ #templatemo_banner            (right, 650×280 incl. 50px padding)
│                                    per-page full-bleed photo strip via
│                                    inline background-image
├─ #templatemo_content_wrapper      (#3C3B3B, 10px pad, 10px top margin)
│  └─ #templatemo_content           (#262626, 30px pad)
│     ├─ #templatemo_side_column    (220px, left)
│     └─ #templatemo_main_content_column (600px, right)
└─ #templatemo_footer               (centered, empty on this site)
```

### index.php (home)
- Side column: `.header_01` heading + 3 "news" items. Each item: bold white
  date line, bold blue title line, excerpt paragraph ending in an underlined
  blue "Read more" link. Ends with `.button_01 a` — a 120×26px dark graphic
  button with 11px bold centered text.
- Main column: `.header_01` heading; a `.section_w600` block with one white
  `.em_text` intro paragraph followed by two normal paragraphs; then two
  side-by-side `.section_w280` cards (same anatomy as projects cards below).

### projects.php
- Side column: heading + two short white paragraphs.
- Main column: grid of `.section_w280` cards in pairs (7 cards + 1 empty
  filler card here). **Card anatomy**: `.header_01` title bar (280px wide);
  `.section_w280_content` (10px side padding) containing a thumbnail image
  (260×180 rendered: 240×160 image + 10px black border all around,
  5px bottom margin), then a white `.em_text` blurb paragraph ending in an
  underlined blue "Read more" link, then a 20px spacer.

### trips.php
- Identical card anatomy to projects, but 15 cards (7 pairs + 1). Side column
  has heading + two white paragraphs.

### resume.php
- Side column: heading + two paragraphs, second contains the blue underlined
  PDF download link.
- Main column: one `.header_01` heading, then five `.section_w600` blocks each
  holding a single large image (560×725, white background, standard 10px black
  image border, 15px paragraph spacing) — a page-per-image "online view".

### contact.php
- Side column: heading + three short white paragraphs.
- Main column: one `.section_w600` block with a form:
  - full-width `<textarea rows=15>` (rendered ~586×231, white bg, 1px gray
    border, monospace);
  - a 2-column table of label/field rows: label cell = white paragraph
    (labels: email address, file attachment, spam-check "type N in the box"
    with the number bolded); field cell = white text input (`width:100%`),
    file input, and a small `size=2` text input respectively;
  - a plain browser-default submit button ("Send": ~47×21, `#EFEFEF` bg,
    outset border). No custom styling on any control.

## 3. Responsive behavior at 375px

- None. The site is a fixed 960px (980px incl. padding) float layout with zero
  media queries. At 375px the whole page renders at full width and requires
  horizontal scrolling; the nav stays a 278px sidebar block, never collapses.
  If the reimplementation needs mobile support it must be added from scratch —
  a sensible mapping: stack top panel, nav (full-width list), banner (hidden
  or scaled), then sidebar above/below main column, cards full width.
