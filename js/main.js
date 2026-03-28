/* TYFSADIK.ORG — Main JS */

// --- Mermaid initialization ------------------------------
if (typeof mermaid !== 'undefined') {
  mermaid.initialize({
    startOnLoad: true,
    theme: 'base',
    themeVariables: {
      darkMode: true,
      background: '#111111',
      primaryColor: '#1a1a2e',
      primaryTextColor: '#e0e0e0',
      primaryBorderColor: '#00d4ff',
      lineColor: '#00d4ff',
      secondaryColor: '#0d1117',
      tertiaryColor: '#181818',
      edgeLabelBackground: '#111111',
      clusterBkg: '#181818',
      clusterBorder: '#1e1e1e',
      titleColor: '#00d4ff',
      nodeTextColor: '#e0e0e0',
      attributeBackgroundColorEven: '#111111',
      attributeBackgroundColorOdd: '#181818',
    },
    flowchart: { curve: 'basis', padding: 20 },
    sequence: {
      actorFontFamily: 'IBM Plex Mono, monospace',
      noteFontFamily: 'IBM Plex Mono, monospace',
      messageFontFamily: 'IBM Plex Mono, monospace',
      actorFontSize: 13,
      mirrorActors: false,
    },
  });
}

// --- Mobile nav toggle -----------------------------------
const navToggle = document.querySelector('.nav-mobile-toggle');
const navLinks  = document.querySelector('.nav-links');
if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('open');
  });
  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
      navLinks.classList.remove('open');
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

// --- Smooth scroll for anchor links ----------------------
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', (e) => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const offset = 56 + 24; // nav height + padding
      const top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  });
});
