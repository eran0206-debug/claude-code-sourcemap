const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + path.resolve('quote.html'));
  await p.waitForTimeout(300);
  await p.pdf({ path: process.argv[2], format: 'Letter', printBackground: true, margin: {top:0,right:0,bottom:0,left:0} });
  await b.close();
})();
