// Phase 0 baseline: Lighthouse (mobile+desktop), axe-core, screenshot matrix.
// Uses system Chrome via playwright-core channel:'chrome'. Run: node baseline.js
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const ROOT = path.resolve(__dirname, '../..');
const OUT = path.join(ROOT, 'docs/baseline');
const PAGES = ['index.html', 'about.html', 'work.html', 'resume.html', 'blog.html',
  'blog/labs/index.html', 'blog/labs/databases/azure-sql-deployment.html',
  'work/defence/sky-passive-radar-node.html'];
const VIEWPORTS = [
  [320,568],[360,640],[375,667],[390,844],[414,896],[430,932],
  [600,960],[768,1024],[820,1180],[1024,768],[1280,720],[1440,900],
  [1920,1080],[2560,1440],[3840,2160],
  [667,375],[844,390],[1024,768], // landscape phones/tablets (1024x768 repeats as tablet landscape)
  [344,882],[673,841] // foldable
];

async function main() {
  fs.mkdirSync(path.join(OUT, 'screenshots'), { recursive: true });
  const server = require('child_process').spawn('python3', ['-m', 'http.server', '8971', '--bind', '127.0.0.1'], { cwd: ROOT, stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 1200));
  const base = 'http://127.0.0.1:8971/';
  const browser = await chromium.launch({ channel: 'chrome' });
  const axeResults = {};
  const overflowReport = {};

  try {
    // axe-core + horizontal overflow check on key pages
    const axeSrc = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
    for (const p of PAGES) {
      const page = await browser.newPage();
      await page.goto(base + p, { waitUntil: 'networkidle' });
      await page.addScriptTag({ content: axeSrc });
      const res = await page.evaluate(async () => await axe.run(document, { resultTypes: ['violations'] }));
      axeResults[p] = res.violations.map(v => ({ id: v.id, impact: v.impact, nodes: v.nodes.length, help: v.help }));
      // horizontal overflow at common widths
      const ov = {};
      for (const [w, h] of [[320,568],[375,667],[768,1024],[1440,900]]) {
        await page.setViewportSize({ width: w, height: h });
        await page.waitForTimeout(200);
        ov[w] = await page.evaluate(() => ({
          scrollW: document.documentElement.scrollWidth,
          clientW: document.documentElement.clientWidth,
          overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth
        }));
      }
      overflowReport[p] = ov;
      await page.close();
    }

    // screenshot matrix
    for (const p of PAGES) {
      const slug = p.replace(/[\/\.]/g, '-').replace(/-html$/, '');
      for (const [w, h] of VIEWPORTS) {
        const page = await browser.newPage({ viewport: { width: w, height: h } });
        await page.goto(base + p, { waitUntil: 'networkidle' });
        await page.screenshot({ path: path.join(OUT, 'screenshots', `${slug}__${w}x${h}.png`), fullPage: false });
        await page.close();
      }
    }
  } finally {
    await browser.close();
  }

  fs.writeFileSync(path.join(OUT, 'axe-results.json'), JSON.stringify(axeResults, null, 1));
  fs.writeFileSync(path.join(OUT, 'overflow.json'), JSON.stringify(overflowReport, null, 1));

  // Lighthouse via CLI against the local server, desktop + mobile
  const lhDir = path.join(OUT, 'lighthouse');
  fs.mkdirSync(lhDir, { recursive: true });
  const lhBin = require.resolve('lighthouse/cli/index.js');
  for (const p of PAGES) {
    for (const mode of ['mobile', 'desktop']) {
      const slug = p.replace(/[\/\.]/g, '-').replace(/-html$/, '');
      const out = path.join(lhDir, `${slug}.${mode}.json`);
      try {
        execFileSync(process.execPath, [lhBin, base + p,
          '--output=json', `--output-path=${out}`, '--quiet', '--chrome-flags=--headless=new --no-sandbox',
          mode === 'desktop' ? '--preset=desktop' : '--form-factor=mobile'], { stdio: 'ignore', timeout: 120000 });
      } catch (e) { console.error('lighthouse failed', p, mode, String(e).slice(0, 200)); }
    }
  }
  server.kill();
  console.log('baseline complete');
}
main().catch(e => { console.error(e); process.exit(1); });
