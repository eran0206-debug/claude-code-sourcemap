const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:794,height:1123} });
  await p.goto('file://' + path.resolve('questions.html'), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const fit = await p.evaluate(() => { const d=document.querySelector('.doc'); const f=document.querySelector('.foot'); const r=document.querySelector('.close'); return { gap: Math.round(f.getBoundingClientRect().top - r.getBoundingClientRect().bottom), footBottom: Math.round(f.getBoundingClientRect().bottom), page: 1123 }; });
  console.log(JSON.stringify(fit));
  await p.pdf({ path: 'questions.pdf', format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
