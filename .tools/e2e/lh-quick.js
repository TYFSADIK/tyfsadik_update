const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const ROOT = path.resolve(__dirname, '../..');
(async () => {
  const server = require('child_process').spawn('python3', ['-m','http.server','8976','--bind','127.0.0.1'], {cwd: ROOT, stdio:'ignore'});
  await new Promise(r => setTimeout(r, 1000));
  const lhBin = require.resolve('lighthouse/cli/index.js');
  for (const p of ['index.html','blog/labs/databases/azure-sql-deployment.html']) {
    const out = `/tmp/lh-${p.replace(/[\/\.]/g,'-')}.json`;
    try {
      execFileSync('node', [lhBin, 'http://127.0.0.1:8976/' + p, '--quiet', '--chrome-flags=--headless=new',
        '--form-factor=mobile', '--screenEmulation.mobile=true',
        '--only-categories=performance,accessibility,best-practices,seo',
        '--output=json', '--output-path=' + out], { stdio: 'ignore', timeout: 180000 });
      const d = JSON.parse(fs.readFileSync(out));
      const c = d.categories;
      console.log(p, Object.fromEntries(Object.entries(c).map(([k,v])=>[k,Math.round(v.score*100)])),
        'LCP', d.audits['largest-contentful-paint'].displayValue,
        'CLS', d.audits['cumulative-layout-shift'].displayValue);
    } catch (e) { console.log('FAIL', p, String(e).slice(0,300)); }
  }
  server.kill();
})();
