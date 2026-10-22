/* TYFSADIK.ORG, Main JS */

// --- Mermaid: load on demand only when a diagram exists ----
// The library is ~680 KiB, so it is injected only on pages that
// actually contain a .mermaid block (previously loaded site-wide).
if (document.querySelector('.mermaid')) {
  const mermaidScript = document.createElement('script');
  mermaidScript.src = 'https://cdn.jsdelivr.net/npm/mermaid@11.17.2/dist/mermaid.min.js';
  mermaidScript.integrity = 'sha384-EOXBFmc3gx5mb+vn0vPvvGqACToJD24hhacX5Yx+8NUUQrHIle/Qi5Bg9o3zKwW2';
  mermaidScript.crossOrigin = 'anonymous';
  mermaidScript.onload = () => {
    mermaid.initialize({
      startOnLoad: true,
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
