# Hakimi Fruits

Written by [Taki Sadik](../../about) · Last updated 2026-10-22 · 8 min read

Online presence for a fruit and produce business with product listings

## Overview

Hakimi Fruits is a website built for a local fruit and produce business to establish an online presence and let customers browse available stock before visiting or ordering. The site features a home page with a seasonal highlights banner, a products page with filterable listings organised by category (citrus, berries, tropical, seasonal), and a contact/order inquiry page. Each product card displays an image, name, price, and availability status. The design uses warm greens, oranges, and cream tones to evoke freshness and a friendly local-market character. JavaScript-powered category filtering lets customers narrow the product list without a page reload, and a CSS Grid auto-fill layout ensures product cards reflow cleanly from single-column mobile to multi-column desktop without explicit breakpoints on the grid.

## Architecture

Shared HTML Components (via CSS classes)

JavaScript

Styles

Pages

index.htmlHome · Seasonal Highlights

products.htmlProduct Listings + Filter

contact.htmlOrder Inquiry Form

style.cssDesign Tokens · Layout · Components

main.jsCategory Filter · Mobile Menu · Form Validation

.nav - shared navigation

.footer - shared footer

## Tech Stack

- HTML5, Semantic product cards using <article>; data-category attributes on each card drive the JavaScript filter

- CSS3, CSS custom properties for the warm colour palette; CSS Grid with auto-fill minmax(240px, 1fr) for the responsive product listing; Flexbox for navigation

- Vanilla JavaScript, Category filter (show/hide cards by data-category), mobile hamburger menu toggle, order form validation

- Responsive Design, Mobile-first base styles; breakpoints at 480 px and 768 px for typography and spacing adjustments; the product grid self-adapts via auto-fill

## Build Process

Defined the product taxonomy, citrus, berries, tropical, and seasonal, and planned the data attributes needed to support JavaScript filtering. Each product was given a consistent content model: image, name, price, availability badge (In Season / Limited / Out of Season), and a category tag.

Built the product card as a reusable HTML pattern with a consistent structure. The data-category attribute on each <article> is the single source of truth for the filter logic, no classes need to change when products are recategorised.

<article class="product-card" data-category="citrus">
  <img src="images/orange.jpg" alt="Navel Oranges" loading="lazy"
       width="400" height="300">
  <div class="product-card__body">
    <h3 class="product-card__name">Navel Oranges</h3>
    <span class="product-card__price">$3.99 / kg</span>
    <span class="product-card__badge product-card__badge-in">In Season</span>
  </div>
</article>

Used grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)) so the number of columns adapts automatically to viewport width. This eliminates the need for breakpoints on the grid declaration itself. A gap of 1.25rem provides consistent gutters at all sizes.

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.25rem;
  padding: var(--space-md) 0;
}

.product-card img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border-radius: 4px 4px 0 0;
}

Filter buttons have a data-filter attribute that maps to the card data-category values. On click, the script iterates all cards and sets display: none or display: '' depending on whether the category matches. An "All" button resets visibility. The active filter button receives an .is-active class for visual feedback.

const filterBtns = document.querySelectorAll('[data-filter]');
const cards = document.querySelectorAll('.product-card');

filterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const filter = btn.dataset.filter;
    filterBtns.forEach(b => b.classList.remove('is-active'));
    btn.classList.add('is-active');
    cards.forEach(card => {
      card.style.display =
        (filter === 'all' || card.dataset.category === filter) ? '' : 'none';
    });
  });
});

A hamburger button toggles an .is-open class on the <nav> element. The nav links are hidden at small viewports via display: none in the base styles and revealed as a full-width dropdown when the class is present. The toggle button is hidden at wider breakpoints using @media (min-width: 768px).

The order inquiry form includes fields for name, email, phone, preferred collection date, and a product selection textarea. JavaScript validates required fields and email format before submission. The form uses a mailto: action as the delivery mechanism, with a visible success message shown after valid submission.

## Customer Browsing Flow

Yes

No

Invalid

Valid

CustomerLands on Home

Views SeasonalHighlights

Goes toProducts Page

Filter byCategory?

Clicks Filter ButtonJS Hides Other Cards

Browses AllProduct Cards

Views FilteredProduct List

Finds DesiredProduct

contact.htmlOrder Inquiry Form

JS Validates Fields

Inline Error Shown

Inquiry Sentto Business

## Challenges & Solutions

Orphan Cards in CSS Grid Auto-Fill at Mid-Range Viewports. At certain viewport widths, the last grid row could hold a single card that looked visually inconsistent with the multi-column rows above it. The fix was to constrain the maximum card width with a max-width on the individual card and to use justify-items: start on the grid, so orphan cards retain their natural size instead of expanding into the leftover space.

Product Image Placeholder Sizing. Before final images were supplied, placeholder images of varying dimensions caused the product grid to have inconsistent card heights. Applying aspect-ratio: 4 / 3 and object-fit: cover to the <img> element resolved this and also ensured the final supplied images would always render at consistent proportions regardless of their source dimensions.

## What I Learned

- Using data-* attributes as a clean, semantic contract between HTML and JavaScript for filter interactions

- CSS Grid auto-fill with minmax() is extremely powerful for card grids but requires understanding of how orphan cards behave at edge-case widths

- The importance of setting aspect-ratio on images early, even with placeholder content, so the layout is stable before final assets arrive

- Structuring JavaScript filter logic to be driven by data attributes rather than CSS classes avoids tight coupling between styling and behaviour

- Mobile-first CSS naturally keeps the base stylesheet compact; responsive expansions are genuinely additive rather than corrective

## How I Built It

Phase 1: Mobile-first base styles. I wrote the base stylesheet for small screens first, so the responsive expansions at larger widths are genuinely additive rather than corrective. The product card grid uses auto-fill with minmax() for column behaviour that needs no per-breakpoint grid rewrites.

Phase 2: Data-driven product filtering. Product cards carry data-* attributes (category, name) that form the contract between HTML and JavaScript. The filter logic reads attributes rather than CSS classes, keeping styling and behaviour decoupled.

Phase 3: Placeholder-stable layout. Before final product images existed, placeholders of varying dimensions threatened card-height chaos. Setting aspect-ratio: 4 / 3 and object-fit: cover on the images from the start guaranteed a stable layout regardless of source dimensions.

Phase 4: Orphan card fix. At mid-range viewports the last grid row occasionally held a single stretched card. Constraining card max-width and setting justify-items: start on the grid keeps orphans at their natural size.

Phase 5: Contact and shipping. A contact section with business details and a simple enquiry form completed the site, followed by validation and deployment.

## What You Need

| Category | Item | Notes |
| --- | --- | --- |
| Tool | A modern web browser | Static site; nothing to install to view it |
| Software | Code editor | Used for the markup, styles, and filter script |
| Software | Image editor | For consistent product photo sizing before upload |
| Skill | HTML5 with data attributes | data-* as the contract for filter interactions |
| Skill | Mobile-first CSS Grid | auto-fill/minmax() card grids, orphan-row behaviour, image aspect ratios |
| Skill | Vanilla JavaScript filtering | Reading data attributes, toggling visibility, live search if needed |
| Account | Static host (e.g. GitHub Pages) | Where the live site is published |

## Challenges and Lessons Learned

Orphan cards in auto-fill grids. A single stretched card in the last row looks like a bug even when the grid is technically correct. The fix was small, but finding it required testing at many in-between widths rather than just the standard breakpoints. Lesson: test the continuum, not just the milestones.

Layout stability with placeholder content. Setting image aspect ratios before final assets arrive means the layout is correct from day one. It is far easier to hold a layout contract early than to retrofit one after content lands.

Attributes over classes for behaviour. Driving filters from data-* attributes kept a clean separation: classes describe appearance, attributes describe data. That contract survives redesigns that a class-based approach would break.

## What Is Next

- Live product search alongside the category filters

- Seasonal produce section that highlights what is fresh now

- Wholesale enquiry form with volume pricing tiers

- Multilingual product names for the local customer base

- Lightweight analytics to see which products visitors actually browse

## Related Projects

- GTA High Glass, a business website for a glazing company.

- Faiaz Shisha, a multi-page business site with booking.

- HomeBound Aisha, a responsive business website.
