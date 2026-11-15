# HomeBound Aisha

Written by [Taki Sadik](../../about) · Last updated 2026-10-22 · 8 min read

Responsive business website for a home-based service provider

## Overview

HomeBound Aisha is a multi-page responsive website delivered as a real client project for a home-based cleaning and domestic service provider. The site presents the business professionally across four pages: a landing page with a hero section and service highlights, a dedicated services page with detailed listings and pricing tiers, an about page establishing trust through the owner's story and credentials, and a contact page with a validated enquiry form. The layout was engineered mobile-first, meaning base styles target small screens and progressive enhancements are layered on at wider breakpoints. The project is published on GitHub and demonstrated a complete client delivery workflow from brief to deployed product on GitHub Pages.

## Architecture

Shared Components (CSS classes)

JavaScript

Stylesheets

Pages

index.htmlHero + Service Highlights

services.htmlFull Service Listings

about.htmlOwner Story + Trust Signals

contact.htmlEnquiry Form

style.cssVariables · Layout · Components

responsive.cssMedia Queries · Breakpoints

main.jsForm Validation · Smooth Scroll · Mobile Menu

nav - .nav · .nav-links · .nav-mobile-toggle

footer - .footer · .footer-links

## Tech Stack

- HTML5, Semantic elements: nav, main, section, article, footer with ARIA labels throughout

- CSS3, Custom properties (variables), Flexbox for nav and card rows, CSS Grid for service and testimonial layouts

- Responsive Design, Mobile-first base styles with @media (min-width) breakpoints at 480 px, 768 px, and 1024 px

- Vanilla JavaScript, Contact form validation, smooth scroll via scrollIntoView, mobile navigation toggle

- GitHub Pages, Static hosting with custom domain support

## Build Process

Gathered client brief: services offered, target audience (residential households), geographic focus, and preferred aesthetic. Defined a CSS variable design system, color palette (--color-primary, --color-accent, --color-bg), font stack, and spacing scale, so all four pages share a consistent visual identity.

/* style.css - design tokens */
:root {
  --color-primary: #2c6e49;
  --color-accent:  #80b918;
  --color-bg:      #fafafa;
  --color-text:    #1a1a1a;
  --font-body:     'Inter', sans-serif;
  --space-md:      1.5rem;
  --space-lg:      3rem;
}

Each page was structured with proper landmark elements, <nav aria-label="Main navigation">, <main>, named <section aria-labelledby>, and <footer>. Service cards used <article> to give screen readers meaningful document structure. Heading hierarchy was enforced: one h1 per page, h2 for sections, h3 for cards.

Base styles target a single-column, small-screen layout. Progressive enhancements at each breakpoint add columns and larger spacing. BEM-style class names (.service-card, .service-card__title, .service-card-featured) eliminate specificity conflicts between base and responsive overrides.

/* responsive.css */
/* Base: single column */
.services-grid { display: grid; grid-template-columns: 1fr; gap: 1rem; }

@media (min-width: 480px) {
  .services-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 768px) {
  .services-grid { grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
}

@media (min-width: 1024px) {
  .services-grid { gap: 2rem; }
}

Three behaviours were implemented in main.js: (1) Mobile menu toggle, adds/removes .is-open class on the nav drawer, trapping focus inside when open. (2) Smooth scroll, document.querySelectorAll('a[href^="#"]') with scrollIntoView({ behavior: 'smooth' }). (3) Contact form validation, checks required fields, validates email format with a regex, and shows inline error messages before allowing submission.

// main.js - form validation excerpt
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

form.addEventListener('submit', (e) => {
  let valid = true;
  if (!nameInput.value.trim()) { showError(nameInput, 'Name is required'); valid = false; }
  if (!emailRegex.test(emailInput.value)) { showError(emailInput, 'Valid email required'); valid = false; }
  if (!valid) e.preventDefault();   // block submission only when invalid
  else showSuccess('Opening your email client to send the enquiry.');
});

Tested in Chrome, Firefox, Safari, and Edge. Ran HTML through the W3C Markup Validation Service and CSS through the W3C CSS Validator, resolved all errors and warnings. Verified mobile rendering on both Android and iOS using browser DevTools responsive simulation and physical device testing.

Pushed to the main branch of the GitHub repository. Enabled GitHub Pages from repository settings, selecting main as the source branch. The site became live at the auto-generated github.io subdomain. Verified all relative asset paths resolved correctly in the deployed environment.

## User Interaction Flow

Navigates

Opens Mobile Menu

Submits Contact Form

Invalid

Valid

User Loads Page

HTML Parsed & Rendered

CSS AppliedMobile-First Base Styles

JS InitialisesMenu · Scroll · Form Listeners

User Action

Smooth Scrollto Section

Nav Drawer OpensFocus Trapped

JS Validates Fields

Inline ErrorMessages Shown

mailto: Opensor Success Message

User SeesConfirmation

## Challenges & Solutions

CSS Specificity Conflicts on Responsive Overrides. Adding media query overrides to flat class names caused specificity battles where mobile styles leaked into desktop layouts and vice versa. The solution was adopting BEM-style naming (.service-card, .service-card__title) and keeping all responsive rules in a separate responsive.css file, which enforced a clear override order and made the responsive layer easy to audit in isolation.

Contact Form Without a Backend. The client needed a working contact form but the site is hosted statically on GitHub Pages with no server. The solution combined a mailto: action attribute on the form (which opens the user's email client pre-populated) with JavaScript-driven client-side validation and a confirmation message. For a more robust no-backend solution, the form was architected to be easily swapped for a Formspree or Netlify Forms endpoint in future.

## What I Learned

- How to structure a genuine client project from brief through delivery, including managing scope and collecting feedback iteratively

- Mobile-first CSS methodology and why starting from small screens produces cleaner, less overridden stylesheets than the reverse

- The value of BEM naming conventions for preventing specificity conflicts in multi-file CSS projects

- Implementing accessible navigation: ARIA labels, focus management in modal/drawer patterns, and keyboard navigation

- The limitations of static hosting for form handling and the patterns available to work around them

- W3C HTML and CSS validation as a quality gate before deployment

## How I Built It

Phase 1: Client brief and scope. This was a genuine client project, so it started with a brief: who the site serves, what pages it needs, and how the client would request changes. Agreeing scope upfront kept the build focused and the feedback rounds short.

Phase 2: Mobile-first styles with BEM. The CSS was written mobile-first and organised with BEM-style naming (.service-card, .service-card__title), so responsive overrides in the separate responsive.css file never fought with base styles. The override order is explicit and auditable in isolation.

Phase 3: Accessible components. Navigation, the mobile drawer, and the contact form were built with keyboard navigation and ARIA labels from the start, including focus management in the drawer pattern.

Phase 4: The no-backend contact form. GitHub Pages has no server to process forms, so the form uses a mailto: action with JavaScript client-side validation and a confirmation message. The markup is structured so a Formspree or Netlify Forms endpoint can replace the mailto action later without restructuring.

Phase 5: Validation and delivery. The HTML and CSS passed W3C validation as a quality gate, the client reviewed and approved, and the site shipped.

## What You Need

| Category | Item | Notes |
| --- | --- | --- |
| Tool | A modern web browser | Static site; keyboard and screen-reader testing recommended |
| Software | Code editor | Used for the HTML, split CSS files, and form script |
| Software | W3C validators | HTML and CSS validation as the pre-deployment quality gate |
| Skill | Mobile-first CSS | Base styles for small screens, additive responsive overrides |
| Skill | BEM naming | Prevents specificity conflicts in multi-file CSS |
| Skill | Accessible navigation patterns | ARIA labels, keyboard support, focus management in drawers |
| Skill | Client project management | Brief, scope control, and iterative feedback collection |
| Account | GitHub Pages | Static hosting; no server, so forms need a no-backend strategy |

## Challenges and Lessons Learned

Specificity conflicts on responsive overrides. Flat class names plus scattered media queries created leaks between mobile and desktop styles. BEM naming plus a dedicated responsive.css file ended the fighting. Lesson: CSS architecture is decided by naming and file organisation, not by clever selectors.

Forms without a backend. A mailto: action is a compromise: it works everywhere but depends on the visitor's email client. Architecting the form so a real endpoint can be swapped in later was the right middle ground for a static host, and it taught me to always design for the upgrade path even when the budget says otherwise.

Real client, real constraints. Collecting feedback iteratively and managing scope with an actual client was as valuable as the technical work. Shipping means deciding what is good enough, not what is perfect.

## What Is Next

- Replace the mailto form with a Formspree or Netlify Forms endpoint for reliable submissions

- Booking or scheduling integration for the services offered

- Testimonials section with client-approved quotes

- Blog or news section so the client can publish updates without code changes

- Performance and SEO audit with Core Web Vitals targets

## Related Projects

- Pharmacy Website, a medical and pharmacy site.

- Hakimi Fruits, an online presence for a produce business.

- Birthday Project, an interactive celebration page.
