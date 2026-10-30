const sidebar = document.querySelector('#docsSidebar');
const menu = document.querySelector('#menuToggle');
const overlay = document.querySelector('#sidebarOverlay');
const search = document.querySelector('#navSearchInput');

function setMenu(open) {
  sidebar.classList.toggle('open', open);
  overlay.hidden = !open;
  menu.setAttribute('aria-expanded', String(open));
  menu.setAttribute('aria-label', open ? 'Close documentation navigation' : 'Open documentation navigation');
  if (matchMedia('(max-width: 900px)').matches) sidebar.inert = !open;
  document.body.style.overflow = open ? 'hidden' : '';
}
menu.addEventListener('click', () => setMenu(!sidebar.classList.contains('open')));
overlay.addEventListener('click', () => { setMenu(false); menu.focus(); });
sidebar.querySelectorAll('a[href^="#"]').forEach(link => link.addEventListener('click', () => {
  if (matchMedia('(max-width: 900px)').matches) {
    setMenu(false);
    const target = document.getElementById(link.hash.slice(1));
    if (target) { target.tabIndex = -1; target.focus({preventScroll: true}); }
  }
}));
const breakpoint = matchMedia('(max-width: 900px)');
function syncMenu() { setMenu(false); sidebar.inert = breakpoint.matches; }
breakpoint.addEventListener('change', syncMenu);
syncMenu();

search.addEventListener('input', () => {
  const query = search.value.trim().toLowerCase();
  let total = 0;
  document.querySelectorAll('.sidebar-group').forEach(group => {
    const chapterMatch = group.querySelector('.nav-chapter').dataset.search.includes(query);
    let visible = 0;
    group.querySelectorAll('.nav-section').forEach(link => {
      const match = chapterMatch || link.dataset.search.includes(query);
      link.parentElement.hidden = !match;
      if (match) visible++;
    });
    group.hidden = visible === 0;
    total += visible;
  });
  document.querySelector('#noSearchResults').hidden = total > 0;
});
document.addEventListener('keydown', event => {
  const editing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) || document.activeElement.isContentEditable;
  if (event.key === '/' && !editing && !event.ctrlKey && !event.metaKey) {
    event.preventDefault();
    if (breakpoint.matches) setMenu(true);
    search.focus();
  }
  if (event.key === 'Escape' && sidebar.classList.contains('open')) { setMenu(false); menu.focus(); }
  if (event.key === 'Tab' && sidebar.classList.contains('open') && breakpoint.matches) {
    const focusables = [menu, ...sidebar.querySelectorAll('a[href],input')].filter(el => el.getClientRects().length);
    const first = focusables[0], last = focusables.at(-1);
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  }
});

async function copyText(value) {
  if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(value);
  const area = document.createElement('textarea');
  area.value = value; area.style.position = 'fixed'; area.style.opacity = '0';
  document.body.append(area); area.select();
  const ok = document.execCommand('copy'); area.remove();
  if (!ok) throw new Error('Clipboard unavailable');
}
document.querySelectorAll('.copy-code').forEach(button => {
  button.addEventListener('click', async () => {
    try { await copyText(button.closest('.code-block').querySelector('code').textContent); button.textContent = 'Copied!'; }
    catch { button.textContent = 'Select code to copy'; }
    setTimeout(() => { button.textContent = 'Copy code'; }, 2000);
  });
});
document.querySelector('#printManual').addEventListener('click', () => window.print());

const dialog = document.querySelector('#imageDialog');
let previousFocus;
document.querySelectorAll('[data-lightbox]').forEach(link => {
  link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || !dialog.showModal) return;
    event.preventDefault(); previousFocus = link;
    const image = link.querySelector('img');
    const expanded = document.querySelector('#expandedImage');
    expanded.src = link.href; expanded.alt = image.alt;
    document.querySelector('#imageTitle').textContent = image.alt;
    dialog.showModal();
  });
});
document.querySelector('#closeImage').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
dialog.addEventListener('close', () => previousFocus?.focus());

const sections = [...document.querySelectorAll('.manual-chapter,.doc-section')];
const navLinks = [...document.querySelectorAll('.sidebar-scroll a[href^="#"],.table-of-contents nav a')];
let queued = false;
function updateLocation() {
  let current = null, chapter = null;
  sections.forEach(section => {
    if (section.getBoundingClientRect().top <= 155) {
      current = section.id;
      chapter = section.closest('.manual-chapter')?.id || section.id;
    }
  });
  navLinks.forEach(link => {
    const target = link.hash.slice(1);
    const active = link.closest('.table-of-contents') ? target === chapter : target === current;
    if (active) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current');
  });
  queued = false;
}
window.addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(updateLocation); } }, {passive: true});
updateLocation();
