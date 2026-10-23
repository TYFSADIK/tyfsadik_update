const sharp = require('sharp');
const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const files = process.argv.slice(2);
(async () => {
  for (const rel of files) {
    const src = path.join(ROOT, rel);
    const base = src.replace(/\.(jpe?g|png)$/i, '');
    try {
      const img = sharp(src);
      await img.clone().webp({ quality: 82 }).toFile(base + '.webp');
      await img.clone().avif({ quality: 60 }).toFile(base + '.avif');
      const o = fs.statSync(src).size, w = fs.statSync(base + '.webp').size, a = fs.statSync(base + '.avif').size;
      console.log(`${rel}: ${(o/1024).toFixed(0)}K -> webp ${(w/1024).toFixed(0)}K, avif ${(a/1024).toFixed(0)}K`);
    } catch (e) { console.log('FAIL', rel, e.message); }
  }
})();
