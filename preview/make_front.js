// Render a card-front SVG (from tools/build_card.py, print/<id>/card-front.svg) to preview/fronts/<id>.jpg,
// trimmed to the card edge, so the preview tool shows the real card.
// Usage: node preview/make_front.js print/<id>/card-front.svg <id>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const jobs = [[process.argv[2], path.join(__dirname, 'fronts', process.argv[3] + '.jpg')]];
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.setViewportSize({ width: 600, height: 1050 });
  for (const [svgPath, out] of jobs) {
    const svg = fs.readFileSync(svgPath, 'utf8').replace(/width="[\d.]+mm" height="[\d.]+mm" viewBox="[^"]+"/,
      'width="600" height="1050" viewBox="3 3 50.8 88.9" preserveAspectRatio="none"');
    await p.setContent(`<html><body style="margin:0">${svg}</body></html>`);
    await p.waitForTimeout(300);
    await p.screenshot({ path: out, type: 'jpeg', quality: 88, clip: { x: 0, y: 0, width: 600, height: 1050 } });
  }
  await b.close();
})();
