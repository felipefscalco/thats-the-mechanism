// Render individual papercut-explainer (MIT) procedural SFX to WAV, one file per effect.
import puppeteer from 'puppeteer-core';
import {readFileSync, writeFileSync, mkdirSync} from 'node:fs';
const LIB = process.env.PAPERCUT_AUDIO || 'research/repos/papercut-explainer/library/audio', names = process.argv.slice(2), out = process.env.PAPERCUT_OUT || 'sfx/papercut';
mkdirSync(out, {recursive: true});
const js = [readFileSync(LIB + '/engine.js', 'utf8'), ...names.map((n) => readFileSync(LIB + '/sfx/' + n + '.js', 'utf8'))].join('\n');
const bed = JSON.parse(readFileSync(LIB + '/beds/marimba-F-108.json', 'utf8'));
const browser = await puppeteer.launch({executablePath: '/usr/bin/google-chrome', headless: true, args: ['--no-sandbox']});
const page = await browser.newPage();
page.on('console', (m) => console.error('[page]', m.text()));
await page.setContent('<!doctype html><meta charset="utf-8"><script>' + js + '</script>');
for (const n of names) {
  const b64 = await page.evaluate((c, b) => window.renderScore(c, 'fx', b), {dur: 2.5, cues: [{t: 0.05, type: n}]}, bed);
  writeFileSync(out + '/' + n + '.wav', Buffer.from(b64, 'base64'));
}
await browser.close(); console.log('rendered', names.length);
