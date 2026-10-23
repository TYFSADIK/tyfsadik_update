// Lighthouse budgets for CI. Uses CHROME_PATH if set (GitHub Actions
// setup-chrome), otherwise Lighthouse finds a local Chrome itself.
const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const ROOT = path.resolve(__dirname, '../..');

// Budgets are honest: lab pages share one stylesheet, so their unused-CSS
// penalty caps performance around 90-93. Index must stay >= 95.
const PAGES = [
  { url: 'index.html', min: { performance: 95, accessibility: 100, 'best-practices': 100, seo: 100 } },
  { url: 'blog/labs/databases/azure-sql-deployment.html', min: { performance: 85, accessibility: 100, 'best-practices': 100, seo: 100 } },
];

(async () => {
  const server = require('child_process').spawn('python3', ['-m', 'http.server', '8977', '--bind', '127.0.0.1'], { cwd: ROOT, stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 1000));
  const lhBin = require.resolve('lighthouse/cli/index.js');
  let fail = 0;
  for (const { url, min } of PAGES) {
    const out = `/tmp/lhci-${url.replace(/[\/\.]/g, '-')}.json`;
    let ok = true;
    try {
      execFileSync('node', [lhBin, 'http://127.0.0.1:8977/' + url, '--quiet',
        '--chrome-flags=--headless=new --no-sandbox --disable-dev-shm-usage --disable-gpu',
        '--form-factor=mobile', '--screenEmulation.mobile=true',
        '--only-categories=performance,accessibility,best-practices,seo',
        '--output=json', '--output-path=' + out], { stdio: ['ignore', 'pipe', 'pipe'], timeout: 240000 });
    } catch (e) {
      console.log(`FAIL ${url}: lighthouse exited ${e.status}`);
      if (e.stderr) console.log(String(e.stderr).slice(0, 2000));
      fail = 1; ok = false;
    }
    if (!ok) continue;
    const d = JSON.parse(fs.readFileSync(out));
    const scores = Object.fromEntries(Object.entries(d.categories).map(([k, v]) => [k, Math.round(v.score * 100)]));
    console.log(url, scores);
    for (const [cat, floor] of Object.entries(min)) {
      if ((scores[cat] ?? 0) < floor) {
        console.log(`FAIL ${url} ${cat}: ${scores[cat]} < ${floor}`);
        fail = 1;
      }
    }
  }
  server.kill();
  process.exit(fail);
})();
