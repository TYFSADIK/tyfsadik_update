const { chromium } = require('playwright-core');
const path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const PAGES = ['resume.html','blog/labs/databases/azure-sql-deployment.html','work/defence/sky-passive-radar-node.html'];
(async () => {
  const server = require('child_process').spawn('python3', ['-m','http.server','8975','--bind','127.0.0.1'], {cwd: ROOT, stdio:'ignore'});
  await new Promise(r => setTimeout(r, 1000));
  const browser = await chromium.launch({ channel: 'chrome' });
  for (const p of PAGES) {
    for (const w of [320, 375, 768]) {
      const page = await browser.newPage({ viewport: { width: w, height: 700 } });
      await page.goto('http://127.0.0.1:8975/' + p, { waitUntil: 'networkidle' });
      const r = await page.evaluate(() => ({
        scrollW: document.documentElement.scrollWidth,
        clientW: document.documentElement.clientWidth,
        outside: [...document.querySelectorAll('*')].filter(el => {
          const b = el.getBoundingClientRect();
          if (b.width <= document.documentElement.clientWidth + 1) return false;
          return !el.closest('.table-scroll') && !el.closest('pre');
        }).map(el => `${el.tagName}.${(el.className||'').toString().slice(0,30)} w=${Math.round(el.getBoundingClientRect().width)}`).slice(0,5)
      }));
      console.log(p, w, 'docOverflow:', r.scrollW > r.clientW, r.outside.length ? r.outside : '');
      await page.close();
    }
  }
  await browser.close(); server.kill();
})();
