/* TYFSADIK.ORG, Main JS */

// --- Mermaid: runtime fallback for diagrams without a pre-render ----
// Diagrams are pre-rendered to inline SVG at build time
// (.tools/e2e/prerender_mermaid.mjs), so the ~680 KiB library is only
// injected when a page contains a diagram that still needs rendering.
const mermaidTodo = document.querySelectorAll('.mermaid:not([data-prerendered])');
if (mermaidTodo.length) {
  const mermaidScript = document.createElement('script');
  mermaidScript.src = 'https://cdn.jsdelivr.net/npm/mermaid@11.17.2/dist/mermaid.min.js';
  mermaidScript.integrity = 'sha384-EOXBFmc3gx5mb+vn0vPvvGqACToJD24hhacX5Yx+8NUUQrHIle/Qi5Bg9o3zKwW2';
  mermaidScript.crossOrigin = 'anonymous';
  mermaidScript.onload = () => {
    mermaid.initialize({
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
    });
    mermaid.run({ nodes: mermaidTodo });
  };
  document.head.appendChild(mermaidScript);
}

// --- Mobile nav toggle -----------------------------------
const navToggle = document.querySelector('.nav-mobile-toggle');
const navLinks  = document.querySelector('.nav-links');
if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    const open = navLinks.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
      navLinks.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
    }
  });
  // Escape closes the menu and returns focus to the toggle
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && navLinks.classList.contains('open')) {
      navLinks.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
      navToggle.focus();
    }
  });
}

// --- Back to top -----------------------------------------
const btt = document.querySelector('.back-to-top');
if (btt) {
  window.addEventListener('scroll', () => {
    btt.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });
  btt.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

// --- Filter system ---------------------------------------
const filterBtns = document.querySelectorAll('.filter-btn');
if (filterBtns.length) {
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const filter = btn.dataset.filter;
      // Update active state
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      // Show/hide items
      document.querySelectorAll('[data-category]').forEach(item => {
        const cats = item.dataset.category || '';
        item.style.display = (filter === 'all' || cats.includes(filter)) ? '' : 'none';
      });
      // Show/hide section headers
      document.querySelectorAll('.category-section').forEach(section => {
        const cat = section.dataset.section || '';
        if (filter === 'all') {
          section.style.display = '';
        } else {
          section.style.display = (cat === filter) ? '' : 'none';
        }
      });
    });
  });
}

// --- Copy-to-clipboard for command blocks ----------------
// Covers .command-block .command and any standalone <pre><code> block.
document.querySelectorAll('.command-block .command, pre').forEach(cmd => {
  const codeEl = cmd.querySelector('code');
  if (!codeEl) return;
  const btn = document.createElement('button');
  btn.className = 'copy-btn';
  btn.type = 'button';
  btn.textContent = 'Copy';
  btn.setAttribute('aria-label', 'Copy command to clipboard');
  btn.addEventListener('click', async (e) => {
    e.preventDefault();
    const text = codeEl.innerText;
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
      } else {
        const ta = document.createElement('textarea');
        ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
        document.body.appendChild(ta); ta.select();
        document.execCommand('copy'); document.body.removeChild(ta);
      }
      btn.textContent = '✅ Copied!';
      btn.classList.add('copied');
      console.log('Command copied: ' + text.slice(0, 50));
    } catch (err) {
      btn.textContent = 'Error';
    }
    setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
  });
  cmd.appendChild(btn);
});

// --- Step progress tracker -------------------------------
// Builds a floating "Step X of Y" indicator for tutorial pages with a .steps list.
(function stepTracker() {
  const steps = document.querySelectorAll('.steps .step');
  if (steps.length < 5) return; // only worthwhile for longer tutorials
  const bar = document.createElement('div');
  bar.className = 'step-tracker';
  bar.setAttribute('aria-live', 'polite');
  bar.textContent = 'Step 1 of ' + steps.length;
  document.body.appendChild(bar);
  let current = 1;
  const io = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if (en.isIntersecting) {
        const idx = [...steps].indexOf(en.target) + 1;
        if (idx) { current = idx; bar.textContent = 'Step ' + current + ' of ' + steps.length; }
        en.target.classList.add('step-seen');
      }
    });
  }, { rootMargin: '-45% 0px -45% 0px' });
  steps.forEach(s => io.observe(s));
  window.addEventListener('scroll', () => {
    bar.classList.toggle('visible', window.scrollY > 300);
  }, { passive: true });
})();

// --- Glossary tooltips -----------------------------------
// Any <span class="glossary-term" data-definition="..."> gets an accessible tooltip.
document.querySelectorAll('.glossary-term[data-definition]').forEach(t => {
  t.setAttribute('tabindex', '0');
  t.setAttribute('role', 'button');
  t.setAttribute('aria-label', t.textContent + ': ' + t.dataset.definition);
});

// --- Smooth scroll for anchor links ----------------------
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', (e) => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const offset = 24; // header is static (not fixed), small padding only
      const top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  });
});

// --- Static site search (labs index and 404) ---------------
// Fetches /search-index.json once, filters client side, and supports ?q=
// so the WebSite SearchAction schema and the 404 search form work.
(function initSiteSearch() {
  const form = document.getElementById('lab-search-form');
  const resultsBox = document.getElementById('search-results');
  if (!form || !resultsBox) return;
  const input = form.querySelector('input[type="search"]');
  const base = form.getAttribute('data-root') || '../../';
  let indexPromise = null;
  const loadIndex = () => {
    if (!indexPromise) {
      indexPromise = fetch(base + 'search-index.json').then(r => r.json());
    }
    return indexPromise;
  };
  const render = (items, q) => {
    if (!q) { resultsBox.innerHTML = ''; return; }
    const terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    const hits = items.filter(it => {
      const hay = (it.title + ' ' + it.description + ' ' + it.track + ' ' + it.kind).toLowerCase();
      return terms.every(t => hay.includes(t));
    }).slice(0, 20);
    if (!hits.length) {
      resultsBox.innerHTML = '<p class="search-status">No matches for &ldquo;' +
        q.replace(/[<>&]/g, '') + '&rdquo;. Try a shorter term.</p>';
      return;
    }
    resultsBox.innerHTML = '<p class="search-status">' + hits.length + ' result' +
      (hits.length === 1 ? '' : 's') + ' for &ldquo;' + q.replace(/[<>&]/g, '') + '&rdquo;</p>' +
      '<ul class="search-results">' + hits.map(it =>
        '<li><a href="' + base + it.url + '"><strong>' + it.title + '</strong></a>' +
        ' <span class="search-kind">' + it.track + ' ' + it.kind + '</span><br>' +
        '<span class="search-desc">' + it.description + '</span></li>'
      ).join('') + '</ul>';
  };
  const run = () => {
    const q = (input.value || '').trim();
    if (q.length < 2) { resultsBox.innerHTML = ''; return; }
    loadIndex().then(items => render(items, q)).catch(() => {
      resultsBox.innerHTML = '<p class="search-status">Search index failed to load.</p>';
    });
  };
  form.addEventListener('submit', (e) => { e.preventDefault(); run(); });
  input.addEventListener('input', run);
  const initial = new URLSearchParams(location.search).get('q');
  if (initial) { input.value = initial; run(); }
})();

// --- Keyboard access to sideways-scrolling regions ---------
// Wide tables and diagrams scroll horizontally on phones; a region that
// actually overflows gets tabindex so keyboard users can scroll it too.
(function initScrollRegions() {
  const regions = document.querySelectorAll('.table-scroll, figure[class*="diagram"]');
  if (!regions.length) return;
  const update = () => regions.forEach(el => {
    if (el.scrollWidth > el.clientWidth + 1) {
      el.tabIndex = 0;
      if (!el.hasAttribute('aria-label')) el.setAttribute('aria-label', 'Scrollable ' + (el.matches('figure') ? 'diagram' : 'table'));
    } else {
      el.removeAttribute('tabindex');
    }
  });
  update();
  let t;
  window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(update, 150); });
})();

// --- Picture protection (every page) ---------------------
// Pictures cannot be opened, saved or dragged out through the browser's
// own menus: no right-click menu, no drag into a new tab, no long-press menu
// on phones. A deterrent only: screenshots and developer tools still work.
// Page zoom is deliberately left alone, because blocking it locks out
// people who need to enlarge the page to read it.
(function protectImages() {
  const isPicture = (el) => el instanceof Element && el.closest('img, picture');
  document.addEventListener('contextmenu', (e) => { if (isPicture(e.target)) e.preventDefault(); });
  document.addEventListener('dragstart', (e) => { if (isPicture(e.target)) e.preventDefault(); });
  document.querySelectorAll('img').forEach((img) => { img.draggable = false; });
})();

// --- Service worker registration -------------------------
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {});
  });
}
