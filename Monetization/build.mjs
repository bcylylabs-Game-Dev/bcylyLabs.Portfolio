import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const sourceRoot = path.dirname(root);
const esc = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const slug = value => value.toLowerCase().replace(/[`*]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const chapters = [
  { key: 'overview', file: 'README.md', title: 'Documentation Index', label: 'Start here', desc: 'Find your way through the package: setup, network configuration, runtime integration and verification.' },
  { key: 'user-guide', file: 'USER_GUIDE.md', title: 'User Guide', label: 'Setup & workflow', desc: 'Configure the Hub, select a provider, connect ad formats and test the player experience.' },
  { key: 'developer', file: 'DEVELOPER_REFERENCE.md', title: 'Developer Reference & API Examples', label: 'Runtime reference', desc: 'Integrate ads through the public API, events, rewarded callbacks and no-ads controls.' },
  { key: 'testing', file: 'TESTING_AND_TROUBLESHOOTING.md', title: 'Testing & Troubleshooting', label: 'Verify & release', desc: 'Test beyond the happy path, diagnose common issues and prepare a deliberate network configuration.' }
];

function generalize(text) {
  return text.replace(/\[User Guide\]\(USER_GUIDE\.md\)/g, '[User Guide](#user-guide)')
    .replace(/\[Developer Reference\]\(DEVELOPER_REFERENCE\.md\)/g, '[Developer Reference](#developer)')
    .replace(/\[Testing and Troubleshooting\]\(TESTING_AND_TROUBLESHOOTING\.md\)/g, '[Testing and Troubleshooting](#testing)');
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
  "user-guide-2-configure-formats-and-pacing": [
    [
      "general-pacing.png",
      "General and Pacing tab",
      "General & Pacing: startup loads, enabled formats, cooldowns and watchdogs. The pictured two-second intervals are demonstration values."
    ]
  ],
  "user-guide-3-use-the-dummy-simulator": [
    [
      "dummy.png",
      "Dummy simulator configuration",
      "Dummy (Mock): banner layout, simulation timing and the optional late-reward outcome. No third-party SDK is required."
    ]
  ],
  "user-guide-4-configure-google-admob": [
    [
      "admob.png",
      "Google AdMob configuration",
      "AdMob: SDK installation, app IDs, ad unit IDs and privacy options. The screenshot uses test identifiers and shows the SDK as missing."
    ]
  ],
  "user-guide-5-configure-applovin-max": [
    [
      "applovin.png",
      "AppLovin MAX configuration",
      "MAX: SDK setup, platform unit IDs and exposed banner options. Placeholder unit names must be replaced; some options are not yet honored by the handler."
    ]
  ],
  "user-guide-6-configure-unity-levelplay": [
    [
      "levelplay.png",
      "Unity LevelPlay configuration",
      "LevelPlay: SDK package installation, per-platform app keys and ad unit IDs. Resolve the documented adapter compile issue before activation."
    ]
  ],
  "user-guide-7-configure-unity-ads": [
    [
      "unity-ads.png",
      "Unity Ads configuration",
      "Unity Ads: game IDs, test mode, banner position and placements. Configure the placement values for the intended platform."
    ]
  ]
};

function figure([file, alt, caption]) {
  const png = fs.readFileSync(path.join(root, 'assets/images', file));
  const width = png.readUInt32BE(16), height = png.readUInt32BE(20);
  return `<figure class="doc-figure"><a class="doc-image-frame" href="assets/images/${file}" data-lightbox aria-label="Enlarge: ${esc(alt)}"><img src="assets/images/${file}" alt="${esc(alt)}" loading="lazy" width="${width}" height="${height}" /><span class="image-expand">↗ Expand screenshot</span></a><figcaption>${esc(caption)}</figcaption></figure>`;
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

const logo = `<svg viewBox="0 0 40 40" fill="none" aria-hidden="true"><rect x="4" y="6" width="32" height="28" rx="7" stroke="currentColor" stroke-width="1.5"/><path d="m17 14 10 6-10 6V14Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M10 11h3m14 18h3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>`;
const arrow = '<span aria-hidden="true">↗</span>';
const nav = chapters.map((chapter, i) => `<div class="sidebar-group"><a class="nav-chapter" href="#${chapter.key}" data-search="${esc(chapter.title.toLowerCase())}"><span>${String(i + 1).padStart(2, '0')}</span>${esc(chapter.title)}</a><ul>${chapter.headings.map(h => `<li><a class="nav-section" href="#${h.id}" data-search="${esc((chapter.title + ' ' + h.title).toLowerCase())}">${esc(h.title)}</a></li>`).join('')}</ul></div>`).join('');
const body = chapters.map((chapter, i) => `<article class="manual-chapter" id="${chapter.key}" aria-labelledby="${chapter.key}-title"><header class="page-header"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="#top">Documentation</a><span aria-hidden="true">›</span><strong>${esc(chapter.title)}</strong></nav><div class="page-meta"><span class="primary-badge">${esc(chapter.label)}</span><span>Chapter ${String(i + 1).padStart(2, '0')}</span></div><h1 id="${chapter.key}-title">${esc(chapter.title)}</h1><p>${esc(chapter.desc)}</p></header>${chapter.html}<nav class="page-pagination" aria-label="Chapter navigation">${i ? `<a class="page-link previous" href="#${chapters[i - 1].key}"><span><small>Previous chapter</small><strong>← ${esc(chapters[i - 1].title)}</strong></span></a>` : '<span></span>'}${i < chapters.length - 1 ? `<a class="page-link next" href="#${chapters[i + 1].key}"><span><small>Next chapter</small><strong>${esc(chapters[i + 1].title)} →</strong></span></a>` : '<a class="page-link next" href="#top"><span><small>Manual complete</small><strong>Back to overview ↑</strong></span></a>'}</nav></article>`).join('');
const html = `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="Complete bcylyLabs Monetization package manual: visual setup, ad networks, Unity ad APIs, rewarded flows, testing and troubleshooting."><meta name="color-scheme" content="light"><title>bcylyLabs Monetization | Complete Documentation</title><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css"><link rel="stylesheet" href="assets/monetization.css"><script src="assets/manual.js" defer></script></head>
<body class="monetization-documentation"><a class="skip-link" href="#content">Skip to documentation</a><button class="sidebar-overlay" id="sidebarOverlay" type="button" aria-label="Close navigation" hidden></button>
<aside class="docs-sidebar" id="docsSidebar" aria-label="Documentation navigation"><div class="sidebar-brand-area"><a class="brand-lockup sidebar-brand" href="#top"><span class="brand-mark">${logo}</span><span><strong>bcylyLabs Monetization</strong><small>Package documentation</small></span></a><label class="sidebar-search"><span aria-hidden="true">⌕</span><input type="search" id="navSearchInput" placeholder="Search documentation…" aria-label="Search documentation navigation"><kbd>/</kbd></label></div><nav class="sidebar-scroll" id="sidebarNavContainer"><a class="overview-nav" href="#top">⌂ &nbsp; Manual overview</a>${nav}<p class="no-search-results" id="noSearchResults" role="status" hidden>No matching section. Try “rewarded”, “consent” or “AdMob”.</p></nav><div class="sidebar-footer"><span class="status-dot"></span><span>Version 1.0.0</span><small>Unity package · Complete manual</small><a href="https://bcylylabs-game-dev.github.io/bcylyLabs.Portfolio/" target="_blank" rel="noopener noreferrer">bcylyLabs ${arrow}</a></div></aside>
<div class="docs-main-shell"><header class="docs-topbar"><div><button class="sidebar-toggle-btn" id="menuToggle" type="button" aria-label="Open documentation navigation" aria-controls="docsSidebar" aria-expanded="false">☰</button><span>bcylyLabs <span class="topbar-divider">/</span> Ad Management</span></div><div><button class="print-button" id="printManual" type="button">Print manual</button><span class="version-pill">v1.0.0</span></div></header>
<main id="content"><section class="manual-hero" id="top"><div class="eyebrow"><span class="status-dot"></span> UNITY AD MANAGEMENT TOOLKIT</div><h1>One interface.<br><span>Your complete ad workflow.</span></h1><p class="hero-intro">The bcylyLabs Monetization manual. Configure networks, connect your game, manage rewarded offers and test every step—from the Editor simulator to native ad lifecycles.</p><div class="hero-actions"><a class="primary-action" href="#user-guide">Start with setup <span aria-hidden="true">→</span></a><a class="secondary-action" href="#developer">Explore the API</a></div><div class="hero-facts"><span>04 complete chapters</span><span>06 illustrated editor views</span><span>Offline-ready static manual</span></div><div class="hero-preview"><div class="preview-label"><span class="status-dot"></span> THE MONETIZATION HUB <span>One-window configuration</span></div><a href="assets/images/general-pacing.png" data-lightbox aria-label="Enlarge Monetization Hub overview"><img src="assets/images/general-pacing.png" alt="bcylyLabs Monetization Hub showing provider selection, enabled formats, pacing and rewarded watchdog controls" width="1007" height="733" fetchpriority="high"></a></div><p class="screenshot-note">Screenshots use sample IDs, missing-SDK states and short demo intervals. Follow the configuration guidance rather than copying pictured release settings.</p></section>
<div class="chapter-cards" aria-label="Manual chapters">${chapters.map((ch, i) => `<a href="#${ch.key}"><span class="card-number">0${i + 1}</span><strong>${esc(ch.title)}</strong><p>${esc(ch.desc)}</p><span class="card-link">Read chapter →</span></a>`).join('')}</div>
<div class="docs-layout"><div class="compiled-manual">${body}<footer class="manual-footer"><a class="brand-lockup" href="#top"><span class="brand-mark">${logo}</span><strong>bcylyLabs Monetization</strong></a><p>Package documentation · v1.0.0 · Reviewed 30 October 2026</p><p>Setup · Runtime APIs · Ad lifecycles · Testing</p></footer></div><aside class="table-of-contents" aria-label="On this page"><strong>IN THIS MANUAL</strong><nav>${chapters.map(ch => `<a href="#${ch.key}">${esc(ch.title)}</a>`).join('')}</nav><div class="reading-note"><span>READING GUIDE</span><p>New to the package?<br>Begin with the User Guide.</p><a href="#user-guide-3-use-the-dummy-simulator">Try the simulator →</a></div><a class="back-top" href="#top">Back to top ↑</a></aside></div></main></div>
<dialog id="imageDialog" aria-label="Screenshot viewer"><div class="lightbox-toolbar"><span id="imageTitle">Screenshot</span><button id="closeImage" type="button" aria-label="Close screenshot">Close ×</button></div><img id="expandedImage" alt=""><p>Use Escape to close · Open image in a new tab for native resolution</p></dialog>
</body></html>`;
fs.writeFileSync(path.join(root, 'index.html'), html);
fs.mkdirSync(path.join(root, 'content'), {recursive: true});
for (const chapter of chapters) fs.writeFileSync(path.join(root, 'content', chapter.file), chapter.markdown);
console.log(`Built index.html: ${chapters.length} chapters, ${chapters.reduce((n, ch) => n + ch.headings.length, 0)} sections, 6 screenshots.`);
