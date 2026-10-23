const sharp = require('sharp');
const path = require('path');
const ROOT = path.resolve(__dirname, '../..');
(async () => {
  for (const size of [192, 512]) {
    const logo = await sharp(path.join(ROOT, 'icon-' + size + '.png'))
      .resize(Math.round(size * 0.72), Math.round(size * 0.72), { fit: 'contain', background: '#333333' })
      .toBuffer();
    await sharp({ create: { width: size, height: size, channels: 4, background: '#333333' } })
      .composite([{ input: logo, gravity: 'center' }])
      .png()
      .toFile(path.join(ROOT, 'icon-maskable-' + size + '.png'));
    console.log('icon-maskable-' + size + '.png written');
  }
})();
