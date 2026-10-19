const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage(); p.on('console', m => console.log('console:', m.text()));
  p.on('pageerror', e => console.log('err:', e.message));
  await p.goto('http://localhost:8765/compile/compile.html');
  await p.waitForFunction('window.ready');
  const b64 = await p.evaluate(() => window.run());
  fs.writeFileSync(process.argv[2], Buffer.from(b64, 'base64'));
  console.log('done', fs.statSync(process.argv[2]).size);
  await b.close();
})();
