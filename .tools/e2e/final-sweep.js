const { execFileSync } = require('child_process');
const path = require('path'); const fs = require('fs');
const ROOT = path.resolve(__dirname, '../..');
const PAGES = ['index.html','about.html','work.html','resume.html','blog.html',
  'blog/labs/index.html','blog/labs/databases/azure-sql-deployment.html',
  'work/defence/sky-passive-radar-node.html','contact.html','how-this-portfolio-is-built.html'];
(async () => {
  const server = require('child_process').spawn('python3', ['-m','http.server','8979','--bind','127.0.0.1'], {cwd: ROOT, stdio:'ignore'});
  await new Promise(r => setTimeout(r, 1000));
  const lhBin = require.resolve('lighthouse/cli/index.js');
  const rows = [];
  for (const p of PAGES) {
    const out = `/tmp/lhfinal-${p.replace(/[\/\.]/g,'-')}.json`;
    execFileSync('node', [lhBin, 'http://127.0.0.1:8979/' + p, '--quiet', '--chrome-flags=--headless=new',
      '--form-factor=mobile', '--screenEmulation.mobile=true',
      '--only-categories=performance,accessibility,best-practices,seo',
      '--output=json', '--output-path=' + out], { stdio: 'ignore', timeout: 240000 });
    const d = JSON.parse(fs.readFileSync(out));
    const c = Object.fromEntries(Object.entries(d.categories).map(([k,v])=>[k,Math.round(v.score*100)]));
    rows.push({page: p, ...c,
      lcp: d.audits['largest-contentful-paint'].displayValue,
      cls: d.audits['cumulative-layout-shift'].displayValue,
      tbt: d.audits['total-blocking-time'].displayValue});
    console.log(p, JSON.stringify(c));
  }
  fs.writeFileSync(path.resolve(ROOT, 'docs/baseline/final-lighthouse.json'), JSON.stringify(rows, null, 2));
  server.kill();
})();
