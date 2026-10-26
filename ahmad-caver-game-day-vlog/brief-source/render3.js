const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:794,height:1123} });
  await p.goto('file://' + path.resolve('shoot.html'), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  console.log(JSON.stringify(await p.evaluate(() => [...document.querySelectorAll('.page')].map((pg,i)=>{ const f=pg.querySelector('.foot'); const kids=[...pg.querySelector('.doc').children].filter(c=>c!==f); return {page:i+1, room: Math.round(f.getBoundingClientRect().top - kids[kids.length-1].getBoundingClientRect().bottom), overflow: pg.scrollHeight - pg.clientHeight}; }))));
  await p.pdf({ path: 'shoot.pdf', format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
