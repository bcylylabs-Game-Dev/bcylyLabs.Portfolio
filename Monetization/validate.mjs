import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const root = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(root,'index.html'),'utf8');
const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
assert.equal(new Set(ids).size, ids.length, 'Duplicate HTML IDs');
for (const match of html.matchAll(/\b(?:href|src)="([^"]+)"/g)) {
  const link = match[1];
  if (link.startsWith('#')) assert.ok(ids.includes(link.slice(1)), `Missing anchor ${link}`);
  else if (!/^[a-z]+:/i.test(link)) assert.ok(fs.existsSync(path.join(root,link)), `Missing file ${link}`);
}
assert.equal((html.match(/class="manual-chapter"/g)||[]).length,4,'Four chapters required');
assert.equal(fs.readdirSync(path.join(root,'assets/images')).filter(x=>x.endsWith('.png')).length,6,'Six screenshots required');
for (const image of fs.readdirSync(path.join(root,'assets/images'))) assert.ok(html.includes(`assets/images/${image}`), `Unused screenshot ${image}`);
assert.ok(!/Goods Sort|GOODS_SORT|TrippleMatch|TripleMatch|BcylyIAP|In-App Purchasing|product catalog|purchase-modal/.test(html),'Unrelated project or IAP template content leaked into manual');
assert.ok(!/\.md["#]/.test(html),'Uncompiled Markdown document link');
assert.ok(!/@@TOKEN\d+@@|undefined|\[object Object\]/.test(html),'Unresolved compiler output');
for (const match of html.matchAll(/<img\b([^>]+)>/g)) {
  assert.ok(/\balt="[^"]*"/.test(match[1]),'Image missing alt text');
}
assert.ok(!/@import|url\(['"]?https?:/.test(fs.readFileSync(path.join(root,'assets/style.css'),'utf8')),'Remote stylesheet dependency');
console.log(`PASS: 4 chapters, 6 screenshot assets, ${ids.length} unique anchors; all local references resolve; no game integration content or remote stylesheet dependencies.`);
