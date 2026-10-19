const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream',
    '--use-file-for-fake-video-capture=/root/ar/test/cam.y4m', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const ctx = await b.newContext({ viewport: { width: 390, height: 694 }, permissions: ['camera'] });
  const p = await ctx.newPage();
  p.on('console', m => { if (!/GL Driver/.test(m.text())) console.log('console:', m.text()); });
  p.on('pageerror', e => console.log('err:', e.message));
  await p.goto('http://localhost:8766/index.html?autostart');
  for (let i = 0; i < 8; i++) {
    await p.waitForTimeout(1800);
    await p.screenshot({ path: `/root/ar/test/shot${i}.png` });
  }
  await b.close();
})();
