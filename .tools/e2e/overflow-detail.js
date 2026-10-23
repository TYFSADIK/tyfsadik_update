const { chromium } = require('playwright-core');
const path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const PAGES = ['resume.html','blog/labs/databases/azure-sql-deployment.html','work/defence/sky-passive-radar-node.html'];
(async () => {
  const server = require('child_process').spawn('python3', ['-m','http.server','8974','--bind','127.0.0.1'], {cwd: ROOT, stdio:'ignore'});
  await new Promise(r => setTimeout(r, 1000));
  const browser = await chromium.launch({ channel: 'chrome' });
  for (const p of PAGES) {
    const page = await browser.newPage({ viewport: { width: 320, height: 568 } });
    await page.goto('http://127.0.0.1:8974/' + p, { waitUntil: 'networkidle' });
    const bad = await page.evaluate(() => {
      const out = [];
      const vw = document.documentElement.clientWidth;
      for (const el of document.querySelectorAll('*')) {
        const r = el.getBoundingClientRect();
        if (r.width > vw + 1) {
          out.push(`${el.tagName}.${(el.className||'').toString().slice(0,40)} w=${Math.round(r.width)}`);
          if (out.length > 9) break;
        }
      }
      return out;
    });
    console.log('==', p); bad.forEach(b => console.log('  ', b));
    await page.close();
  }
  await browser.close(); server.kill();
})();
