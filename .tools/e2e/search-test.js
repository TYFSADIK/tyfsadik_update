const { chromium } = require('playwright-core');
const path = require('path');
const ROOT = path.resolve(__dirname, '../..');
(async () => {
  const server = require('child_process').spawn('python3', ['-m','http.server','8977','--bind','127.0.0.1'], {cwd: ROOT, stdio:'ignore'});
  await new Promise(r => setTimeout(r, 1000));
  const browser = await chromium.launch({ channel: 'chrome' });
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:8977/blog/labs/index.html?q=vlan', { waitUntil: 'networkidle' });
  const txt = await page.textContent('#search-results');
  console.log('q=vlan:', txt.slice(0, 200));
  await browser.close(); server.kill();
})();
