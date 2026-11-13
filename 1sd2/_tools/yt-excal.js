// Usage: node yt-excal.js <youtube-url | excalidraw-url> <out.png>
// 1) reads the video description  2) finds the Excalidraw link  3) exports the whole board as PNG (2x)
const { chromium } = require('playwright-core');
const fs = require('fs');
(async () => {
  const [video, out] = process.argv.slice(2);
  // arg 1 may be the Excalidraw link itself (use when YouTube blocks the description fetch)
  let link = /excalidraw\.com/.test(video) ? video : null;
  if (!link) {
    const html = await (await fetch(video, { headers: { 'Accept-Language': 'en-US' } })).text();
    const m = html.match(/"shortDescription":"((?:[^"\\]|\\.)*)"/);
    const desc = m ? JSON.parse('"' + m[1] + '"') : '';
    link = (desc.match(/https?:\/\/[^\s"]*excalidraw\.com[^\s"]*/) || [])[0];
  }
  if (!link) { console.log('NO_EXCALIDRAW_LINK'); process.exit(2); }
  console.log('link ' + link);
  const b = await chromium.launch({ channel: 'msedge', headless: true });
  const ctx = await b.newContext({ viewport: { width: 2400, height: 1500 } });
  // capture the exported file instead of a native save dialog
  await ctx.addInitScript(() => {
    window.showSaveFilePicker = async () => ({
      name: 'board.png',
      createWritable: async () => { const parts = [];
        return { write: async d => parts.push(d instanceof Blob ? d : (d && d.data) || d),
                 close: async () => { window.__blob = new Blob(parts); } }; } });
  });
  const p = await ctx.newPage();
  await p.goto(link, { waitUntil: 'networkidle', timeout: 90000 });
  const join = p.getByRole('button', { name: /join as a guest/i });
  if (await join.count()) await join.click();
  await p.waitForSelector('canvas', { timeout: 60000 });
  await p.waitForTimeout(8000);
  await p.mouse.click(1200, 750);
  await p.keyboard.press('Control+Shift+E');
  const btn = p.locator('button:has-text("PNG")').first();
  await btn.waitFor({ timeout: 15000 });
  const x2 = p.locator('button:has-text("2×")');
  if (await x2.count()) { await x2.first().click(); await p.waitForTimeout(1500); }
  await btn.click();
  await p.waitForFunction(() => window.__blob, null, { timeout: 30000 });
  const b64 = await p.evaluate(async () => { const buf = new Uint8Array(await window.__blob.arrayBuffer());
    let s = ''; for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode(...buf.subarray(i, i + 0x8000)); return btoa(s); });
  fs.writeFileSync(out, Buffer.from(b64, 'base64'));
  console.log('saved ' + out);
  await b.close();
})().catch(e => { console.error('FAILED ' + e.message.split('\n')[0]); process.exit(1); });
