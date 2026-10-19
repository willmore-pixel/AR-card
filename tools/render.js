// Render the card SVG to PNGs: full bleed print PNG and a preview with trim/safe guides.
const { chromium } = require('playwright');
const fs = require('fs');
const [svgPath, outDir] = process.argv.slice(2);
const svg = fs.readFileSync(svgPath, 'utf8');
const DPI = 600, MM = DPI / 25.4;
const W = 56.8, H = 94.9;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 1 });
  const pxW = Math.round(W * MM), pxH = Math.round(H * MM);
  const sized = svg.replace(/width="[\d.]+mm" height="[\d.]+mm"/, `width="${pxW}" height="${pxH}"`);
  await page.setViewportSize({ width: pxW, height: pxH });
  await page.setContent(`<html><body style="margin:0">${sized}</body></html>`);
  await page.screenshot({ path: `${outDir}/card-front-print-600dpi.png`, clip: { x: 0, y: 0, width: pxW, height: pxH } });

  // Preview: trimmed card on a neutral backdrop, with dashed trim/safe guides beside it
  const s = 10; // px per mm
  const trimmed = svg.replace(/width="[\d.]+mm" height="[\d.]+mm" viewBox="[^"]+"/,
    `width="${50.8 * s}" height="${88.9 * s}" viewBox="3 3 50.8 88.9"`);
  const guides = svg.replace(/width="[\d.]+mm" height="[\d.]+mm"/, `width="${W * s}" height="${H * s}"`)
    .replace('</svg>', `<rect x="3" y="3" width="50.8" height="88.9" fill="none" stroke="#e00" stroke-width="0.25" stroke-dasharray="1 0.6"/>
<rect x="6" y="6" width="44.8" height="82.9" fill="none" stroke="#06c" stroke-width="0.2" stroke-dasharray="0.6 0.6"/></svg>`);
  const html = `<html><body style="margin:0;background:#d9d6cf;font:14px Inter,sans-serif;color:#333">
  <div style="display:flex;gap:60px;padding:50px;align-items:flex-start">
    <div><div style="border-radius:8px;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,.25)">${trimmed}</div>
      <p style="text-align:center">Card as printed (2 x 3.5 in)</p></div>
    <div>${guides}<p style="text-align:center">Print file: red = cut line, blue = safe zone</p></div>
  </div></body></html>`;
  await page.setViewportSize({ width: 1300, height: 1100 });
  await page.setContent(html);
  await page.screenshot({ path: `${outDir}/card-front-preview.png`, fullPage: true });
  await browser.close();
})();
