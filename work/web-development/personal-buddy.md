# Personal Buddy

Written by [Taki Sadik](../../about) · Last updated 2026-11-14 · 5 min read

Product website for a made-to-order 3D printed robot and desk companion from Halifax

## Overview

Personal Buddy is a made-to-order 3D printed robot and desk companion from Halifax, with real electronics inside: clocks, alarms, sensors, RGB lighting and animated faces. Its site at personalbuddy.ca explains the product and walks a buyer through choosing one.

## What the Site Does

- "More than a 3D print: real electronics inside" product introduction

- Pick a starting point, then Build Your Buddy (a step-by-step choice flow)

- What it can do, three ways to own it, and a four-step idea-to-desk process

- A testing section ("We don't just print it. We test it.") and a 9-question FAQ

## How I Built It

A single-page application built with React and bundled by Vite into static files, so the interactive builder runs entirely in the browser with no server to maintain.

- React components for each section and the builder flow

- Vite production build to static assets

- Product, offer and FAQ structured data in the page

## Hosting and Delivery

The built files are hosted on GitHub Pages under the personalbuddy.ca domain, with Cloudflare in front for DNS, TLS and caching.

## Domain Email

No email is configured on this domain yet. The order form opens a message to support@personalbuddy.ca, so the domain needs mail records (for example Cloudflare Email Routing) before those messages can arrive.

## Search and AI Discoverability

The page declares 6 products with 9 offers and a 9-question FAQ in schema.org structured data, publishes a 12-URL sitemap, and has an llms.txt for AI assistants.

## How a Visit Works

- A visitor lands on the product story

- They pick a starting point and build their Buddy

- They send the order request

## What Is Next

- Set up domain email so the support@personalbuddy.ca address used by the order form receives messages

- Replace the mailto order form with a form service or checkout

## Frequently Asked Questions

**Q: What is personalbuddy.ca built with?**

A: React, bundled by Vite into a static single-page app, hosted on GitHub Pages with Cloudflare in front.

**Q: How do customers order?**

A: Through the Build Your Buddy flow and an order form; the form currently opens an email, so domain email still needs to be set up.

## Related Projects

- Jhilik, a brand launch page.

- Felixous Technology, a Next.js business site with tools and a shop.

- TaxGlobe, another browser-only web app.
