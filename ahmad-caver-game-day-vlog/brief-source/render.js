const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 794, height: 1123 } });
  await p.goto('file://' + path.resolve('brief.html'), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const over = await p.evaluate(() => [...document.querySelectorAll('.page')].map((pg, i) => {
    const foot = pg.querySelector('.foot'); const kids = [...pg.children].filter(c => c !== foot);
    const last = kids[kids.length - 1].getBoundingClientRect().bottom; const f = foot.getBoundingClientRect().top;
    return { page: i + 1, gap_px: Math.round(f - last) };
  }));
  console.log(JSON.stringify(over));
  const fonts = await p.evaluate(() => [...document.fonts].map(f => f.family + ':' + f.status));
  console.log(fonts.join(' '));
  await p.pdf({ path: 'brief.pdf', format: 'A4', printBackground: true, preferCSSPageSize: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  await b.close();
})();
