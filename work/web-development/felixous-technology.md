# Felixous Technology

Written by [Taki Sadik](../../about) · Last updated 2026-11-14 · 5 min read

Next.js website for a managed IT and cybersecurity company in the Greater Toronto Area

## Overview

Felixous Technology is a managed IT and cybersecurity company in the Greater Toronto Area offering managed IT, cybersecurity, cloud support and ransomware protection to Canadian businesses. Its site at felixoustech.com is the company's storefront and lead engine.

## What the Site Does

- Three service tracks (managed IT, cybersecurity, cloud) and pricing tiers

- Free tools: scanners that show a business what is exposed before an attacker finds it

- A shop with cart, account login and registration

- A request-a-quote flow, an industries section and a support page

- A knowledge hub of 68 blog posts on IT and security topics

## How I Built It

Built with Next.js (React), which serves interactive pages such as the scanners, shop and accounts alongside content pages, rather than a purely static site.

- Next.js app with React components

- Separate routes for tools, shop, quote, pricing, industries and blog

- Organization and LocalBusiness structured data

## Hosting and Delivery

Unlike the static client sites, this one is not served from GitHub Pages: I host the Next.js application on the client's own server machine, with Cloudflare in front for DNS, TLS and protection, so the business owns its hardware and data.

## Domain Email

Incoming mail for the domain is handled by Cloudflare Email Routing (MX records on route1-3.mx.cloudflare.net, with a matching SPF record), which forwards messages sent to the business address into a real inbox.

## Search and AI Discoverability

The site declares the company as a schema.org Organization and LocalBusiness, publishes an 88-URL sitemap and an llms.txt, and builds topical authority through the 68-article knowledge hub.

## How a Visit Works

- A business owner searches for IT or security help

- They run a free scan and see their exposure

- They compare plans and request a quote or talk to the team

## What Is Next

- Add outgoing mail authentication (DKIM and DMARC) to match the other domains

- Publish service-area pages for the GTA cities served

## Frequently Asked Questions

**Q: What is felixoustech.com built with?**

A: Next.js (React), running on the client's own server machine behind Cloudflare rather than as a static GitHub Pages site.

**Q: What can visitors do on the site?**

A: Run free exposure scanners, read a 68-post knowledge hub, buy from the shop, and request a quote.

## Related Projects

- Apex Collision Center, a generated local business site.

- Daru, my self-hosted SIEM.

- Personal Buddy, a React and Vite product site.
