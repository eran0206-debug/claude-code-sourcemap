const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + path.resolve('brief.html'), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  console.log([...await p.evaluate(() => [...document.fonts].map(f => f.family + ':' + f.status))].join(' '));
  await p.pdf({ path: 'brief.pdf', format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
