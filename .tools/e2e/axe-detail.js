// Detail run: get axe node targets for color-contrast on failing pages
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(__dirname, '../..');

(async () => {
  const server = require('child_process').spawn('python3', ['-m','http.server','8972','--bind','127.0.0.1'], {cwd: ROOT, stdio:'ignore'});
  await new Promise(r => setTimeout(r, 1000));
  const browser = await chromium.launch({ channel: 'chrome' });
  const axeSrc = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
  for (const p of ['blog/labs/index.html', 'blog/labs/databases/azure-sql-deployment.html']) {
    const page = await browser.newPage();
    await page.goto('http://127.0.0.1:8972/' + p, { waitUntil: 'networkidle' });
    await page.addScriptTag({ content: axeSrc });
    const res = await page.evaluate(async () => await axe.run(document, { resultTypes: ['violations'] }));
    for (const v of res.violations) {
      if (v.id !== 'color-contrast') continue;
      const sel = [...new Set(v.nodes.map(n => n.target.join(' ')))];
      const colors = [...new Set(v.nodes.map(n => JSON.stringify(n.any[0]?.data || {})))];
      console.log(p);
      console.log(' selectors:', sel.slice(0, 8));
      console.log(' data:', colors.slice(0, 4));
    }
    await page.close();
  }
  await browser.close();
  server.kill();
})();
