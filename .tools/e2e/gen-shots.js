const { chromium } = require('playwright-core');
const path = require('path');
const ROOT = path.resolve(__dirname, '../..');
(async () => {
  const server = require('child_process').spawn('python3', ['-m','http.server','8978','--bind','127.0.0.1'], {cwd: ROOT, stdio:'ignore'});
  await new Promise(r => setTimeout(r, 1000));
  const browser = await chromium.launch({ channel: 'chrome' });
  let page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  await page.goto('http://127.0.0.1:8978/index.html', { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(ROOT, 'images/screenshot-wide.png') });
  await page.close();
  page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await page.goto('http://127.0.0.1:8978/index.html', { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(ROOT, 'images/screenshot-narrow.png') });
  await browser.close(); server.kill();
  console.log('screenshots written');
})();
