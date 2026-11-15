# Pharmacy Website

Written by [Taki Sadik](../../about) · Last updated 2026-10-22 · 9 min read

Medical/pharmacy website with product listings and service information

## Overview

The Pharmacy Website is a professional multi-page site for a retail pharmacy, built with accessibility as a primary design constraint rather than an afterthought. The site covers: a landing page with a services summary and pharmacy hours, a products page with categorised OTC medications, vitamins, and health devices, a services page detailing prescription handling, consultation, and delivery, and a contact/location page with an embedded map and enquiry form. The colour palette was engineered to meet WCAG AA contrast ratios (minimum 4.5:1 for normal text), and every interactive element is fully keyboard-navigable. Product categories are marked up with structured schema.org-compatible data attributes to support search engine rich results. JavaScript provides a real-time product search/filter and mobile navigation, while the HTML5 validation layer covers the contact form before any script runs.

## Architecture

JavaScript

Styles

Pages

index.htmlHero · Services Summary · Hours

products.htmlCategorised Product Listings + Search

services.htmlPrescriptions · Consultations · Delivery

contact.htmlMap Embed · Enquiry Form

style.cssWCAG-compliant Palette · Components · Grid

Responsive Breakpoints480px · 768px · 1024px

main.jsProduct Search/Filter · Mobile Menu · Form Validation

## Tech Stack

- HTML5, Semantic landmark elements throughout; aria-label, aria-labelledby, role attributes for screen-reader accessibility; tabindex management for keyboard navigation

- CSS3, WCAG AA-compliant colour palette; CSS Grid for product category sections; Flexbox for navigation and service cards; CSS custom properties for consistent token usage

- Responsive Design, Mobile-first base styles; breakpoints at 480 px, 768 px, and 1024 px; tested with screen readers and keyboard-only navigation at all sizes

- Vanilla JavaScript, Live product search (filtering cards as the user types), category filter tabs, mobile menu toggle, contact form validation with accessible error announcements

- Google Maps Embed, Location page uses a responsive iframe embed for the pharmacy map; width and height set in CSS to maintain aspect ratio across viewports

## Build Process

Before any visual design work, the landmark and heading structure was defined on paper: one <main> per page, named <section> elements with aria-labelledby pointing to their <h2>, and ARIA roles where native elements are insufficient. Keyboard navigation paths were planned to ensure logical tab order throughout.

The medical white/blue palette was tested against WCAG 2.1 AA requirements (4.5:1 ratio for normal text, 3:1 for large text and UI components) using the WebAIM Contrast Checker. The initial blue measured #3b82f6 on white at only 3.7:1, which fails WCAG AA for normal text; it was darkened to #1d5fa6 to reach 6.5:1.

:root {
  --color-primary:  #1d5fa6;  /* 6.5:1 on white - WCAG AA pass */
  --color-bg:       #ffffff;
  --color-surface:  #f0f4f9;
  --color-text:     #1a2332;  /* 15.8:1 on white */
  --color-muted:    #5a6474;  /* 6.0:1 on white - AA pass */
  --color-success:  #1a6e38;  /* 6.3:1 on white */
  --color-error:    #b91c1c;  /* 6.5:1 on white */
}

Products are organised into three categories, OTC Medications, Vitamins & Supplements, and Health Devices. Each product card has a data-category attribute and a data-name attribute that the live search queries against. The HTML structure follows the same <article>-based card pattern as other projects, with an additional itemscope/itemprop layer for schema.org/Product structured data.

A search input on the products page filters cards in real time as the user types. The query is compared case-insensitively against the data-name attribute. An accessible live region announces the result count to screen readers via aria-live="polite".

const searchInput = document.getElementById('product-search');
const cards = document.querySelectorAll('.product-card');
const liveRegion = document.getElementById('search-status');

searchInput.addEventListener('input', () => {
  const query = searchInput.value.toLowerCase().trim();
  let visible = 0;
  cards.forEach(card => {
    const match = card.dataset.name.toLowerCase().includes(query);
    card.style.display = match ? '' : 'none';
    if (match) visible++;
  });
  liveRegion.textContent = `${visible} product${visible !== 1 ? 's' : ''} shown`;
});

The location page uses a responsive Google Maps embed wrapped in a container that maintains a 16:9 aspect ratio via aspect-ratio: 16 / 9 on the wrapper and width: 100%; height: 100% on the <iframe>. The contact form validates name, email, and message fields before submission; error messages use role="alert" so screen readers announce them immediately.

Tested the complete site with keyboard-only navigation, VoiceOver on macOS, and NVDA on Windows at each breakpoint. Verified tab order, focus visible indicators (minimum 2px outline), and screen reader announcement of dynamic content (search results, form errors). Cross-browser tested in Chrome, Firefox, Safari, and Edge.

## Patient / Customer Journey Flow

Find a product

Learn about services

Get directions

Patient / CustomerArrives on Site

What do they need?

products.htmlSearch or Browse by Category

services.htmlPrescriptions · Consultations

contact.htmlMap + Hours

Filters / SearchesJS Updates Result Count via aria-live

Finds ProductViews Details

Reads Service InfoScrolls Landmark Sections

Views Map EmbedChecks Opening Hours

Submits Enquiry FormValidated + aria alert

## Challenges & Solutions

WCAG Colour Contrast Requirements. The initial design used a mid-range blue (#3b82f6) as the primary colour on white backgrounds, a ratio of only 3.7:1, which fails WCAG AA for normal text. Adjusting to #1d5fa6 achieved a 6.5:1 ratio without significantly changing the intended visual feel. The muted text colour was also checked: #6b7280 measured 4.8:1, already a pass, but it was darkened to #5a6474 (6.0:1) to hold a comfortable margin above the 4.5:1 threshold. Every colour decision was validated with the WebAIM Contrast Checker before being committed.

Structured Product Data for SEO. Adding schema.org/Product markup required careful decisions about which properties to include without a backend to generate structured data dynamically. The solution was to embed itemscope, itemtype, and itemprop attributes directly in the HTML product cards, manually. While this means updates require editing HTML, it keeps the site fully static and is validated using Google's Rich Results Test tool.

## What I Learned

- Accessibility is most effectively treated as a design constraint from the start, retrofitting ARIA roles and contrast fixes after the fact is much harder than planning landmark structure and colour ratios upfront

- WCAG AA requires a 4.5:1 contrast ratio for normal text, 3:1 for large text and UI elements; these ratios must be verified with a tool, not estimated visually

- aria-live="polite" on a live region is the correct mechanism for announcing dynamic DOM changes (search results, filter updates) to screen readers without interrupting ongoing reading

- role="alert" on form error messages triggers an immediate screen reader announcement, appropriate for errors, but not for status updates where polite is less disruptive

- Embedding structured schema.org/Product data in static HTML is viable for small catalogs and can be validated with Google's Rich Results Test

- The aspect-ratio property on an iframe wrapper with a 100% fill child is the cleanest CSS-only approach to responsive embedded maps and videos

## How I Built It

Phase 1: Accessibility-first design system. I started with the colour palette, not the layout: the primary blue was adjusted from #3b82f6 to #1d5fa6 to reach a 6.5:1 contrast ratio on white, and every muted text colour was verified with the WebAIM Contrast Checker to cross the WCAG AA 4.5:1 threshold before a single page was built.

Phase 2: Semantic page structure. The four pages (landing, products, services, contact/location) use semantic landmark elements with aria-label, aria-labelledby, and role attributes throughout, plus tabindex management so every interactive element is fully keyboard-navigable.

Phase 3: Product catalog with structured data. Product cards were marked up with itemscope, itemtype, and itemprop attributes directly in the HTML, embedding schema.org/Product data for search rich results without any backend. Each card was validated with Google's Rich Results Test.

Phase 4: Live search and responsive embeds. Vanilla JavaScript provides real-time product search and category filter tabs, with an aria-live="polite" region announcing dynamic updates to screen readers. The location page's embedded map uses the aspect-ratio wrapper technique for responsive iframes.

Phase 5: Accessible form errors and final audit. Contact form errors use role="alert" for immediate screen reader announcement, and the full site was re-checked at the 480, 768, and 1024 px breakpoints with keyboard-only navigation.

## What You Need

| Category | Item | Notes |
| --- | --- | --- |
| Tool | A modern web browser | Static site; test with a screen reader and keyboard-only navigation |
| Software | Code editor | Used for the semantic markup, accessible components, and search script |
| Software | WebAIM Contrast Checker | Every colour decision validated against WCAG AA ratios before commit |
| Software | Google's Rich Results Test | Validates the schema.org/Product markup in the product cards |
| Skill | WCAG 2.1 fundamentals | AA contrast ratios: 4.5:1 for normal text, 3:1 for large text; verified with a tool, not estimated visually |
| Skill | ARIA and landmark structure | aria-live regions for dynamic updates, role="alert" for errors, keyboard focus management |
| Skill | Vanilla JavaScript filtering | Live product search with accessible announcements |
| Account | Static host | The site is fully static with embedded map and search |

## Challenges and Lessons Learned

Accessibility as retrofit is painful. The first palette failed WCAG AA and fixing it after the design was done meant touching every component. The lesson was definitive: accessibility is a design constraint from the first sketch, not a QA phase at the end. The WebAIM checker is now a commit-time habit, not a pre-launch one.

Structured data without a backend. Hand-writing itemscope attributes into static HTML works for a small catalog, but every product edit is a code edit. That trade-off is honest and documented: the site is small enough that the simplicity is worth it, and the markup validates.

Announce, don't interrupt. Using aria-live="polite" for search updates and reserving role="alert" for errors gave screen-reader users the right amount of information at the right urgency. Accessibility details like this are invisible to sighted testers, which is exactly why they need deliberate attention.

## What Is Next

- Push key text elements toward WCAG AAA (7:1) where the design allows it

- Skip links and a visible focus indicator audit across all pages

- Product inventory data via a small JSON file so updates do not require HTML edits

- Prescription refill request flow with secure submission handling

- Multilingual content for the community the pharmacy serves

- Full accessibility audit with a screen reader user, not just automated checkers

## Related Projects

- HomeBound Aisha, a responsive business website.

- GTA High Glass, a business website for a glazing company.

- Practice Apps, TypeScript practice builds.
