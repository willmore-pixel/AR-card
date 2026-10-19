// Usage: node compile_target.js <server-root-url> <target.png path under root> <out.mind>
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [root, target, out] = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage();
  p.on('pageerror', e => console.log('err:', e.message));
  await p.goto(`${root}/tools/compile.html`);
  await p.waitForFunction('window.ready');
  const b64 = await p.evaluate(src => window.run(src), `${root}/${target}`);
  fs.writeFileSync(out, Buffer.from(b64, 'base64'));
  await b.close();
})();
