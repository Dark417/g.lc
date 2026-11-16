const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ channel: 'msedge', headless: true });
  const pg = await (await b.newContext({ viewport: { width: 1100, height: 800 } })).newPage();
  const out = {};
  await pg.goto('http://localhost:8765/'); await pg.waitForSelector('.row');
  out.strike = await pg.evaluate(() => { const e = document.querySelector('li.done > .row .txt'); return e ? getComputedStyle(e).textDecorationLine : 'no done row'; });
  out.sq = await pg.evaluate(() => [1,2,3,4].map(l => document.querySelectorAll('.sq.l' + l).length));
  const first = await pg.evaluate(() => document.querySelectorAll('.sq.l4').length); out.l4Off = first;
  await pg.click('#l4Btn');
  out.l4OnClosed = await pg.evaluate(() => document.querySelectorAll('.sq.l4').length);
  out.l4Btn = await pg.evaluate(() => getComputedStyle(document.getElementById('l4Btn')).backgroundColor);
  // open first level-3 node that has kids
  const opened = await pg.evaluate(() => { const rows = [...document.querySelectorAll('.row')].filter(r => r.querySelector('.sq.l3') && r.querySelector('.tw').textContent === '▸'); if (!rows.length) return 0; rows[0].querySelector('.tw').click(); return rows.length; });
  out.l3Closed = opened;
  out.l4AfterOpen = await pg.evaluate(() => document.querySelectorAll('.sq.l4').length);
  out.indentL3 = await pg.evaluate(() => { const a = document.querySelector('.sq.l2'), c = document.querySelector('.sq.l3'); return c && a ? Math.round(c.getBoundingClientRect().left - a.getBoundingClientRect().left) : null; });
  await pg.click('#l4Btn'); // back off
  await pg.click('#mapBtn'); await pg.waitForSelector('#map .me-tpc', { timeout: 20000 }); await pg.waitForTimeout(1200);
  out.mdone = await pg.evaluate(() => document.querySelectorAll('#map .me-tpc.mdone').length);
  out.mdoneStyle = await pg.evaluate(() => { const e = document.querySelector('#map .me-tpc.mdone .text'); return e ? getComputedStyle(e).textDecorationLine : null; });
  out.hasMove = await pg.evaluate(() => typeof window.mind);
  const pos = () => pg.evaluate(() => { const e = document.querySelector('#map .me-tpc'); const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top)]; });
  const p0 = await pos();
  await pg.mouse.move(600, 500); await pg.keyboard.press('h');
  out.handClass = await pg.evaluate(() => document.getElementById('map').classList.contains('hand'));
  await pg.mouse.down(); await pg.mouse.move(700, 560, { steps: 8 }); await pg.mouse.up();
  const p1 = await pos(); out.pan = [p1[0] - p0[0], p1[1] - p0[1]];
  out.nodeCountSame = await pg.evaluate(() => document.querySelectorAll('#map .me-tpc').length);
  await pg.keyboard.press('h');
  out.handOff = await pg.evaluate(() => !document.getElementById('map').classList.contains('hand'));
  out.mapBtn = await pg.evaluate(() => getComputedStyle(document.getElementById('mapBtn')).backgroundColor);
  out.treeBtn = await pg.evaluate(() => getComputedStyle(document.getElementById('treeBtn')).backgroundColor);
  out.status = await pg.evaluate(() => document.getElementById('status').textContent);
  console.log(JSON.stringify(out)); await b.close();
})().catch(e => { console.log('FAIL ' + e.message); process.exit(1); });
