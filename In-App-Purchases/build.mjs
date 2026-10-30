import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const sourceRoot = path.dirname(root);
const esc = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const slug = value => value.toLowerCase().replace(/[`*]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const chapters = [
  { key: 'overview', file: 'README.md', title: 'Documentation Index', label: 'Start here', desc: 'Find your way through the package: setup, shop UI, runtime integration and verification.' },
  { key: 'user-guide', file: 'USER_GUIDE.md', title: 'User Guide', label: 'Setup & workflow', desc: 'Configure the Hub, build a catalog, connect your shop and test the complete purchase experience.' },
  { key: 'developer', file: 'DEVELOPER_REFERENCE.md', title: 'Developer Reference & API Examples', label: 'Runtime reference', desc: 'Integrate purchases with your game through the public API, events and durable fulfillment contracts.' },
  { key: 'testing', file: 'TESTING_AND_TROUBLESHOOTING.md', title: 'Testing & Troubleshooting', label: 'Verify & release', desc: 'Test beyond the happy path, diagnose common issues and prepare a deliberate store configuration.' }
];

function generalize(text, key) {
  text = text.replace(/^\| \[Goods Sort Integration\].*\r?\n/gm, '');
  text = text.replace('This project uses Unity 6000.3.6f1 and Unity Purchasing 5.4.3.', 'The source reviewed for this guide uses Unity 6000.3.6f1 and Unity Purchasing 5.4.3. These are the reviewed environment versions, not a minimum-version guarantee.');
  text = text.replace("starter keys that differ from this project's catalog", 'starter keys that differ from your catalog');
  text = text.replace('in this project', 'in this implementation').replace('in this project', 'in this implementation');
  text = text.replace("See [Goods Sort Integration](GOODS_SORT_INTEGRATION.md) for the active catalog in this project.", 'Verify the selected profile in the Hub before editing or building.');
  text = text.replace(/See \[Goods Sort Integration\]\(GOODS_SORT_INTEGRATION\.md\) for the active catalog in this implementation\./g, 'Verify the selected profile in the Hub before editing or building.');
  text = text.replace('or provide a spending API.', 'or provide a spending API.');
  text = text.replace('PlayerData', 'your game wallet');
  text = text.replace('Goods Sort\'s current handler does not persist transaction deduplication.', 'An application handler must persist its own transaction deduplication.');
  text = text.replace('current game handler needs improvement here', 'requires an idempotent application handler');
  text = text.replace('This documentation update did not run Unity tests or native store transactions.', 'This guide describes the implementation; run the verification steps against your own build and test accounts.');
  text = text.replace('current game handler', 'application reward handler');
  text = text.replace('These guides describe existing behavior;', 'This manual describes existing behavior;');
  text = text.replace(/\[User Guide\]\(USER_GUIDE\.md\)/g, '[User Guide](#user-guide)').replace(/\[Developer Reference\]\(DEVELOPER_REFERENCE\.md\)/g, '[Developer Reference](#developer)').replace(/\[Testing and Troubleshooting\]\(TESTING_AND_TROUBLESHOOTING\.md\)/g, '[Testing and Troubleshooting](#testing)');
  if (key === 'overview') text = text.replace('Documentation for the source included in this project, reviewed 29 October 2026.', 'Package manual · Version 1.0.0 · Reviewed 29 October 2026.');
  return text;
}

function inline(value) {
  const tokens = [];
  const token = html => `@@TOKEN${tokens.push(html) - 1}@@`;
  value = value.replace(/`([^`]+)`/g, (_, code) => token(`<code>${esc(code)}</code>`));
  value = value.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => token(`<a href="${esc(href)}"${href.startsWith('https:') ? ' target="_blank" rel="noopener noreferrer"' : ''}>${esc(label)}</a>`));
  value = esc(value).replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  return value.replace(/@@TOKEN(\d+)@@/g, (_, i) => tokens[Number(i)]);
}

const imageDefs = {
  'user-guide-2-open-the-setup-tools': [['menu.png', 'Open the IAP tools', 'Unity menu entry for the IAP Hub, settings selection, demo scene and catalog export.']],
  'user-guide-select-the-correct-settings-asset': [['hub-overview.png', 'IAP Hub Overview tab', 'Overview: active profile, provider status, simulation settings and product summary. Profile names and catalog counts are examples.']],
  'user-guide-4-add-products': [['catalog.png', 'Product catalog editor', 'Products: developer keys, store IDs, billing types and fulfillment. The pictured IDs are sample values; use your own registered store IDs.']],
  'user-guide-9-test-a-purchase': [['sandbox.png', 'Simulator Sandbox tab', 'Sandbox tools: isolated profiles, reset actions and instant Play Mode purchase simulation.']],
  'developer-validation': [['settings.png', 'Receipt validation and lifecycle settings', 'Settings Inspector: validation modes, store public key, server URL, scope guards and lifecycle options. The screenshot shows a simulation configuration, not recommended live settings.']],
  'overview-quick-start': [['demo-shop.png', 'IAP demo shop', 'Demo scene: example products, ownership feedback, restore, sandbox reset and runtime diagnostics.'], ['purchase-modal.png', 'Simulated purchase confirmation sheet', 'Dummy purchase sheet: test-mode notice, simulated price, purchase approval and cancellation. No real payment is made.']]
};

function figure([file, alt, caption]) {
  const portrait = ['demo-shop.png', 'purchase-modal.png'].includes(file);
  return `<figure class="doc-figure${portrait ? ' portrait' : ''}"><a class="doc-image-frame" href="assets/images/${file}" data-lightbox aria-label="Enlarge: ${esc(alt)}"><img src="assets/images/${file}" alt="${esc(alt)}" loading="lazy" width="${portrait ? 342 : 1024}" /><span class="image-expand">↗ Expand screenshot</span></a><figcaption>${esc(caption)}</figcaption></figure>`;
}

function compile(markdown, chapter) {
  const lines = markdown.split(/\r?\n/);
  let html = '', sectionOpen = false, headings = [], currentHeading = '';
  const images = id => {
    const defs = imageDefs[id];
    return defs ? `<div class="${defs.length > 1 ? 'screenshot-pair' : 'screenshot-single'}">${defs.map(figure).join('')}</div>` : '';
  };
  for (let i = 0; i < lines.length;) {
    const line = lines[i];
    if (!line.trim() || /^# /.test(line)) { i++; continue; }
    if (line.startsWith('```')) {
      const lang = line.slice(3).trim() || 'text'; const code = [];
      i++;
      while (i < lines.length && !lines[i].startsWith('```')) code.push(lines[i++]);
      i++;
      html += `<div class="code-block"><div class="code-header"><span>${esc(lang)}</span><button class="copy-code" type="button">Copy code</button></div><pre tabindex="0"><code>${esc(code.join('\n'))}</code></pre></div>`;
      continue;
    }
    const heading = /^(#{2,3}) (.+)$/.exec(line);
    if (heading) {
      const level = heading[1].length;
      const id = `${chapter.key}-${slug(heading[2])}`;
      if (level === 2) {
        if (sectionOpen) html += '</section>';
        html += `<section class="doc-section" id="${id}"><h2>${inline(heading[2])}<a class="heading-anchor" href="#${id}" aria-label="Link to this section">#</a></h2>`;
        sectionOpen = true;
        headings.push({id, title: heading[2]});
      } else html += `<h3 id="${id}">${inline(heading[2])}</h3>`;
      currentHeading = id;
      html += images(id);
      i++; continue;
    }
    if (line.startsWith('|') && i + 1 < lines.length && /^\|[\s:|-]+\|$/.test(lines[i + 1])) {
      const cells = row => row.trim().replace(/^\||\|$/g, '').split('|').map(x => inline(x.trim()));
      const headers = cells(line);
      html += `<div class="table-wrap"><table><thead><tr>${headers.map(x => `<th scope="col">${x}</th>`).join('')}</tr></thead><tbody>`;
      i += 2;
      while (i < lines.length && lines[i].startsWith('|')) html += `<tr>${cells(lines[i++]).map(x => `<td>${x}</td>`).join('')}</tr>`;
      html += '</tbody></table></div>'; continue;
    }
    if (/^[-*] /.test(line) || /^\d+\. /.test(line)) {
      const ordered = /^\d+\. /.test(line), items = [];
      const re = ordered ? /^\d+\. (.+)$/ : /^[-*] (.+)$/;
      while (i < lines.length && re.test(lines[i])) items.push(lines[i++].replace(re, '$1'));
      html += ordered ? `<ol class="step-list">${items.map((x, j) => `<li><span aria-hidden="true">${String(j + 1).padStart(2, '0')}</span><div>${inline(x)}</div></li>`).join('')}</ol>` : `<ul class="doc-bullets">${items.map(x => `<li>${inline(x)}</li>`).join('')}</ul>`;
      continue;
    }
    const paragraph = [line]; i++;
    while (i < lines.length && lines[i].trim() && !/^(#{1,3} |```|\||[-*] |\d+\. )/.test(lines[i])) paragraph.push(lines[i++]);
    const text = paragraph.join(' ');
    const important = /^(Do not |Never |Despite |The current |A simulated success|The journal calls)/.test(text);
    html += important ? `<aside class="doc-callout important"><strong>Implementation note</strong><p>${inline(text)}</p></aside>` : `<p>${inline(text)}</p>`;
  }
  if (sectionOpen) html += '</section>';
  return {html, headings};
}

for (const chapter of chapters) {
  chapter.markdown = generalize(fs.readFileSync(path.join(sourceRoot, chapter.file), 'utf8'), chapter.key);
  const built = compile(chapter.markdown, chapter);
  Object.assign(chapter, built);
}

const logo = `<svg viewBox="0 0 40 40" fill="none" aria-hidden="true"><rect x="4" y="4" width="32" height="32" rx="9" stroke="currentColor" stroke-width="1.5"/><path d="M12 16h16l-2 13H14l-2-13Z" stroke="currentColor" stroke-width="1.5"/><path d="M16 17v-4a4 4 0 0 1 8 0v4" stroke="currentColor" stroke-width="1.5"/><path d="m17 23 2 2 4-4" stroke="currentColor" stroke-width="1.5"/></svg>`;
const arrow = '<span aria-hidden="true">↗</span>';
const nav = chapters.map((chapter, i) => `<div class="sidebar-group"><a class="nav-chapter" href="#${chapter.key}" data-search="${esc(chapter.title.toLowerCase())}"><span>${String(i + 1).padStart(2, '0')}</span>${esc(chapter.title)}</a><ul>${chapter.headings.map(h => `<li><a class="nav-section" href="#${h.id}" data-search="${esc((chapter.title + ' ' + h.title).toLowerCase())}">${esc(h.title)}</a></li>`).join('')}</ul></div>`).join('');
const body = chapters.map((chapter, i) => `<article class="manual-chapter" id="${chapter.key}" aria-labelledby="${chapter.key}-title"><header class="page-header"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="#top">Documentation</a><span aria-hidden="true">›</span><strong>${esc(chapter.title)}</strong></nav><div class="page-meta"><span class="primary-badge">${esc(chapter.label)}</span><span>Chapter ${String(i + 1).padStart(2, '0')}</span></div><h1 id="${chapter.key}-title">${esc(chapter.title)}</h1><p>${esc(chapter.desc)}</p></header>${chapter.html}<nav class="page-pagination" aria-label="Chapter navigation">${i ? `<a class="page-link previous" href="#${chapters[i - 1].key}"><span><small>Previous chapter</small><strong>← ${esc(chapters[i - 1].title)}</strong></span></a>` : '<span></span>'}${i < chapters.length - 1 ? `<a class="page-link next" href="#${chapters[i + 1].key}"><span><small>Next chapter</small><strong>${esc(chapters[i + 1].title)} →</strong></span></a>` : '<a class="page-link next" href="#top"><span><small>Manual complete</small><strong>Back to overview ↑</strong></span></a>'}</nav></article>`).join('');
const html = `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="Complete bcylyLabs IAP package manual: visual setup, product catalogs, Unity purchase APIs, custom fulfillment, testing and troubleshooting."><meta name="color-scheme" content="light"><title>bcylyLabs IAP | Complete Documentation</title><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css"><link rel="stylesheet" href="assets/iap.css"><script src="assets/manual.js" defer></script></head>
<body class="iap-documentation"><a class="skip-link" href="#content">Skip to documentation</a><button class="sidebar-overlay" id="sidebarOverlay" type="button" aria-label="Close navigation" hidden></button>
<aside class="docs-sidebar" id="docsSidebar" aria-label="Documentation navigation"><div class="sidebar-brand-area"><a class="brand-lockup sidebar-brand" href="#top"><span class="brand-mark">${logo}</span><span><strong>bcylyLabs IAP</strong><small>Package documentation</small></span></a><label class="sidebar-search"><span aria-hidden="true">⌕</span><input type="search" id="navSearchInput" placeholder="Search documentation…" aria-label="Search documentation navigation"><kbd>/</kbd></label></div><nav class="sidebar-scroll" id="sidebarNavContainer"><a class="overview-nav" href="#top">⌂ &nbsp; Manual overview</a>${nav}<p class="no-search-results" id="noSearchResults" role="status" hidden>No matching section. Try “purchase”, “restore” or “validation”.</p></nav><div class="sidebar-footer"><span class="status-dot"></span><span>Version 1.0.0</span><small>Unity package · Complete manual</small><a href="https://bcylylabs-game-dev.github.io/bcylyLabs.Portfolio/" target="_blank" rel="noopener noreferrer">bcylyLabs ${arrow}</a></div></aside>
<div class="docs-main-shell"><header class="docs-topbar"><div><button class="sidebar-toggle-btn" id="menuToggle" type="button" aria-label="Open documentation navigation" aria-controls="docsSidebar" aria-expanded="false">☰</button><span>bcylyLabs <span class="topbar-divider">/</span> In-App Purchasing</span></div><div><button class="print-button" id="printManual" type="button">Print manual</button><span class="version-pill">v1.0.0</span></div></header>
<main id="content"><section class="manual-hero" id="top"><div class="eyebrow"><span class="status-dot"></span> UNITY IN-APP PURCHASING TOOLKIT</div><h1>One catalog.<br><span>A complete purchase workflow.</span></h1><p class="hero-intro">The bcylyLabs IAP manual. Configure your products, connect your shop, integrate rewards and test every step—from the Editor simulator to store validation.</p><div class="hero-actions"><a class="primary-action" href="#user-guide">Start with setup <span aria-hidden="true">→</span></a><a class="secondary-action" href="#developer">Explore the API</a></div><div class="hero-facts"><span>04 complete chapters</span><span>07 annotated screenshots</span><span>Offline-ready static manual</span></div><div class="hero-preview"><div class="preview-label"><span class="status-dot"></span> THE IAP HUB <span>One-window configuration</span></div><a href="assets/images/hub-overview.png" data-lightbox aria-label="Enlarge IAP Hub overview"><img src="assets/images/hub-overview.png" alt="bcylyLabs IAP Hub showing profile, provider settings and product summary" width="1024" height="760" fetchpriority="high"></a></div><p class="screenshot-note">Screenshots use example profiles, products and store IDs. Follow the configuration guidance rather than copying pictured release settings.</p></section>
<div class="chapter-cards" aria-label="Manual chapters">${chapters.map((ch, i) => `<a href="#${ch.key}"><span class="card-number">0${i + 1}</span><strong>${esc(ch.title)}</strong><p>${esc(ch.desc)}</p><span class="card-link">Read chapter →</span></a>`).join('')}</div>
<div class="docs-layout"><div class="compiled-manual">${body}<footer class="manual-footer"><a class="brand-lockup" href="#top"><span class="brand-mark">${logo}</span><strong>bcylyLabs IAP</strong></a><p>Package documentation · v1.0.0 · Reviewed 29 October 2026</p><p>Setup · Runtime APIs · Fulfillment · Testing</p></footer></div><aside class="table-of-contents" aria-label="On this page"><strong>IN THIS MANUAL</strong><nav>${chapters.map(ch => `<a href="#${ch.key}">${esc(ch.title)}</a>`).join('')}</nav><div class="reading-note"><span>READING GUIDE</span><p>New to the package?<br>Begin with the User Guide.</p><a href="#user-guide-9-test-a-purchase">Try the simulator →</a></div><a class="back-top" href="#top">Back to top ↑</a></aside></div></main></div>
<dialog id="imageDialog" aria-label="Screenshot viewer"><div class="lightbox-toolbar"><span id="imageTitle">Screenshot</span><button id="closeImage" type="button" aria-label="Close screenshot">Close ×</button></div><img id="expandedImage" alt=""><p>Use Escape to close · Open image in a new tab for native resolution</p></dialog>
</body></html>`;
fs.writeFileSync(path.join(root, 'index.html'), html);
fs.mkdirSync(path.join(root, 'content'), {recursive: true});
for (const chapter of chapters) fs.writeFileSync(path.join(root, 'content', chapter.file), chapter.markdown);
console.log(`Built index.html: ${chapters.length} chapters, ${chapters.reduce((n, ch) => n + ch.headings.length, 0)} sections, 7 screenshots.`);
