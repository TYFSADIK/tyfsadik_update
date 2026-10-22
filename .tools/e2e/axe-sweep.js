const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const PAGES = ['index.html','about.html','work.html','resume.html','blog.html',
  'blog/labs/index.html','blog/labs/databases/azure-sql-deployment.html',
  'work/defence/sky-passive-radar-node.html','404.html','contact.html'];
(async () => {
  const server = require('child_process').spawn('python3', ['-m','http.server','8973','--bind','127.0.0.1'], {cwd: ROOT, stdio:'ignore'});
  await new Promise(r => setTimeout(r, 1000));
  const browser = await chromium.launch({ channel: 'chrome' });
  const axeSrc = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
  let fail = 0;
  for (const p of PAGES) {
    const page = await browser.newPage();
    await page.goto('http://127.0.0.1:8973/' + p, { waitUntil: 'networkidle' });
    await page.addScriptTag({ content: axeSrc });
    const res = await page.evaluate(async () => await axe.run(document, { resultTypes: ['violations'] }));
    if (res.violations.length) {
      fail++;
      console.log(p, '->', res.violations.map(v => `${v.id}(${v.nodes.length})`).join(', '));
    } else console.log(p, '-> clean');
    await page.close();
  }
  await browser.close(); server.kill();
  process.exit(fail ? 1 : 0);
})();
