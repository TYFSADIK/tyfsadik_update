// Lighthouse budgets for CI. Uses CHROME_PATH if set (GitHub Actions
// setup-chrome), otherwise Lighthouse finds a local Chrome itself.
//
// Performance scores on shared CI runners swing +/- 15 points versus a
// quiet local machine, so each page is measured 3 times and the median is
// used. Functional categories (accessibility, best-practices, seo) are
// deterministic and stay at a hard 100. Local targets (see
// docs/FINAL-REPORT.md) are stricter: index >= 95, lab pages >= 85.
const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const ROOT = path.resolve(__dirname, '../..');
const RUNS = parseInt(process.env.LH_RUNS || '3', 10);

const PAGES = [
  { url: 'index.html', min: { performance: 90, accessibility: 100, 'best-practices': 100, seo: 100 } },
  { url: 'blog/labs/databases/azure-sql-deployment.html', min: { performance: 75, accessibility: 100, 'best-practices': 100, seo: 100 } },
];

function runOnce(lhBin, url, out) {
  execFileSync('node', [lhBin, 'http://127.0.0.1:8977/' + url, '--quiet',
    '--chrome-flags=--headless=new --no-sandbox --disable-dev-shm-usage --disable-gpu',
    '--form-factor=mobile', '--screenEmulation.mobile=true',
    '--only-categories=performance,accessibility,best-practices,seo',
    '--output=json', '--output-path=' + out], { stdio: ['ignore', 'pipe', 'pipe'], timeout: 240000 });
  const d = JSON.parse(fs.readFileSync(out));
  return Object.fromEntries(Object.entries(d.categories).map(([k, v]) => [k, Math.round(v.score * 100)]));
}

(async () => {
  const server = require('child_process').spawn('python3', ['-m', 'http.server', '8977', '--bind', '127.0.0.1'], { cwd: ROOT, stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 1000));
  const lhBin = require.resolve('lighthouse/cli/index.js');
  let fail = 0;
  for (const { url, min } of PAGES) {
    const runs = [];
    for (let i = 0; i < RUNS; i++) {
      try {
        runs.push(runOnce(lhBin, url, `/tmp/lhci-${url.replace(/[\/\.]/g, '-')}-${i}.json`));
      } catch (e) {
        console.log(`FAIL ${url} run ${i}: lighthouse exited ${e.status}`);
        if (e.stderr) console.log(String(e.stderr).slice(0, 2000));
        fail = 1;
      }
    }
    if (!runs.length) continue;
    const median = {};
    for (const cat of Object.keys(min)) {
      const vals = runs.map(r => r[cat]).sort((a, b) => a - b);
      median[cat] = vals[Math.floor(vals.length / 2)];
    }
    console.log(url, 'median of', runs.length, median, '(runs:', runs.map(r => r.performance).join(','), 'perf)');
    for (const [cat, floor] of Object.entries(min)) {
      if ((median[cat] ?? 0) < floor) {
        console.log(`FAIL ${url} ${cat}: median ${median[cat]} < ${floor}`);
        fail = 1;
      }
    }
  }
  server.kill();
  process.exit(fail);
})();
