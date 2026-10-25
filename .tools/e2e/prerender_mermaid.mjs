// Pre-render every <div class="mermaid"> block in the site's HTML to
// inline SVG at build time. Kills the 913 KiB mermaid.min.js runtime,
// removes the raw-source flash on slow connections, and makes diagrams
// visible with JavaScript disabled (SEO/no-JS crawlers).
//
// The original mermaid source is kept inside the div in an inert
// <template class="mermaid-source"> so diagrams can be re-rendered or
// edited later. Re-running this script is idempotent: divs marked
// data-prerendered are re-rendered from their template source, and any
// new unprerendered div is rendered from its text content.
//
// Usage: node prerender_mermaid.mjs [file ...]   (default: all html files with class="mermaid")

import { chromium } from 'playwright-core';
import { readFileSync, writeFileSync, readdirSync, statSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');

const MERMAID_CONFIG = {
  startOnLoad: false,
  theme: 'base',
  themeVariables: {
    darkMode: true,
    background: '#161616',
    primaryColor: '#262626',
    primaryTextColor: '#DBDADA',
    primaryBorderColor: '#5B93EF',
    lineColor: '#9FA2A4',
    secondaryColor: '#161616',
    tertiaryColor: '#2E2E2E',
    edgeLabelBackground: '#161616',
    clusterBkg: '#1c1c1c',
    clusterBorder: '#313131',
    titleColor: '#FFFFFF',
    nodeTextColor: '#DBDADA',
    attributeBackgroundColorEven: '#161616',
    attributeBackgroundColorOdd: '#262626',
  },
  flowchart: { curve: 'basis', padding: 20 },
  sequence: {
    actorFontFamily: 'Georgia, serif',
    noteFontFamily: 'Georgia, serif',
    messageFontFamily: 'Georgia, serif',
    actorFontSize: 13,
    mirrorActors: false,
  },
};

function decodeEntities(s) {
  return s
    .replace(/&gt;/g, '>')
    .replace(/&lt;/g, '<')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&');
}
function encodeEntities(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function* walk(dir) {
  for (const name of readdirSync(dir)) {
    if (name === 'node_modules' || name.startsWith('.')) continue;
    const p = join(dir, name);
    if (statSync(p).isDirectory()) yield* walk(p);
    else if (name.endsWith('.html')) yield p;
  }
}

// Extract each mermaid div: returns { full, attrs, inner, source, prerendered }
// Pre-rendered divs can contain </div> inside SVG foreignObject labels, so
// for those we anchor on the trailing </template></div> instead.
function extractDiagrams(html) {
  const out = [];
  const re = /<div class="mermaid"([^>]*)>/g;
  let m;
  while ((m = re.exec(html))) {
    const attrs = m[1] || '';
    const prerendered = attrs.includes('data-prerendered');
    let inner, full;
    if (prerendered) {
      const end = html.indexOf('</template></div>', m.index);
      if (end === -1) continue;
      full = html.slice(m.index, end + '</template></div>'.length);
      inner = html.slice(m.index + m[0].length, end + '</template>'.length);
    } else {
      const end = html.indexOf('</div>', m.index);
      if (end === -1) continue;
      full = html.slice(m.index, end + '</div>'.length);
      inner = html.slice(m.index + m[0].length, end);
    }
    const tmpl = inner.match(/<template class="mermaid-source">([\s\S]*?)<\/template>/);
    const source = tmpl ? decodeEntities(tmpl[1]) : decodeEntities(inner);
    out.push({ full, attrs: attrs.replace(/\s*data-prerendered="true"/, '').trim(), inner, source, prerendered });
  }
  return out;
}

const args = process.argv.slice(2);
let files;
if (args.length) {
  files = args.map(f => join(ROOT, f));
} else {
  files = [...walk(ROOT)].filter(f => readFileSync(f, 'utf8').includes('class="mermaid"'));
}

// Collect unique sources
const jobs = []; // { file, html, diagrams }
const uniqueSources = new Map(); // source -> null (placeholder for svg)
for (const file of files) {
  const html = readFileSync(file, 'utf8');
  const diagrams = extractDiagrams(html);
  if (!diagrams.length) continue;
  for (const d of diagrams) if (!uniqueSources.has(d.source)) uniqueSources.set(d.source, null);
  jobs.push({ file, html, diagrams });
}
console.log(`files: ${jobs.length}, diagrams: ${jobs.reduce((n, j) => n + j.diagrams.length, 0)}, unique: ${uniqueSources.size}`);

// Render unique sources in one headless page
const mermaidPath = join(dirname(fileURLToPath(import.meta.url)), 'node_modules', 'mermaid', 'dist', 'mermaid.min.js');
const mermaidJs = readFileSync(mermaidPath, 'utf8');

const browser = await chromium.launch({ channel: 'chrome' });
const page = await browser.newPage();
await page.setContent('<html><body></body></html>');
await page.addScriptTag({ content: mermaidJs });
await page.evaluate(cfg => {
  window.mermaid.initialize(cfg);
  // mermaid's class/state renderers use Math.random for path jitter;
  // seed it so re-runs produce byte-identical SVG (idempotent builds).
  let s = 0xC0FFEE;
  Math.random = () => {
    s |= 0; s = (s + 0x6D2B79F5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}, MERMAID_CONFIG);

const failures = [];
let n = 0;
for (const [source] of uniqueSources) {
  n++;
  try {
    const svg = await page.evaluate(async ({ src, id, cfg }) => {
      try {
        const { svg } = await window.mermaid.render(id, src);
        return { ok: true, svg };
      } catch (e) {
        // mermaid leaves error artifacts in the DOM; clean up
        document.querySelectorAll('.mermaid, [id^="dmermaid"], [id^="mermaid"]').forEach(el => {
          if (el.parentElement === document.body) el.remove();
        });
        return { ok: false, err: String(e && e.message || e).slice(0, 200) };
      }
    }, { src: source, id: 'mmd-' + n, cfg: MERMAID_CONFIG });
    if (svg.ok) uniqueSources.set(source, svg.svg);
    else failures.push({ source: source.slice(0, 80), err: svg.err });
  } catch (e) {
    failures.push({ source: source.slice(0, 80), err: String(e).slice(0, 200) });
  }
  if (n % 50 === 0) console.log(`rendered ${n}/${uniqueSources.size}`);
}
await browser.close();

// Rewrite files
let changed = 0, skipped = 0;
for (const job of jobs) {
  let html = job.html;
  let dirty = false;
  for (const d of job.diagrams) {
    const svg = uniqueSources.get(d.source);
    if (!svg) { skipped++; continue; } // failed render: leave the source div for the runtime loader
    const replacement =
      `<div class="mermaid"${d.attrs ? ' ' + d.attrs : ''} data-prerendered="true">${svg}` +
      `<template class="mermaid-source">${encodeEntities(d.source)}</template></div>`;
    if (d.full !== replacement) { html = html.replace(d.full, replacement); dirty = true; }
  }
  if (dirty) { writeFileSync(job.file, html); changed++; }
}
console.log(`files rewritten: ${changed}, diagrams skipped (render failed, runtime fallback kept): ${skipped}`);
if (failures.length) {
  console.log('FAILURES:');
  failures.forEach(f => console.log(' -', JSON.stringify(f)));
  process.exitCode = 1;
}
