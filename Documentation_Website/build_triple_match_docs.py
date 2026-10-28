import os
import re
import html

WORKSPACE = r"d:\bcylyLabs.Portfolio\Documentation_Website"
MD_PATH = r"d:\Unity Projects\Goods Sort\Documentation\Triple-Match-Item-Sorting-Kit-Setup-and-Customization-Guide.md"
TARGET_DIR = os.path.join(WORKSPACE, "triple-match")
DOCS_DIR = os.path.join(TARGET_DIR, "docs")
IMAGES_DIR = os.path.join(TARGET_DIR, "images")

os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

CHAPTER_DEFS = [
    {
        "num": 1,
        "slug": "quick-setup",
        "title": "Quick Setup",
        "group": "Getting started",
        "badge": "Must read",
        "desc": "Open the project with Unity 6000+, load the main game scene, and run Triple Match in Play Mode within minutes."
    },
    {
        "num": 2,
        "slug": "quick-reference",
        "title": "Find What You Want to Change",
        "group": "Getting started",
        "badge": "Reference",
        "desc": "A complete quick-lookup directory mapping every visual, gameplay, audio, and monetization feature to its asset path."
    },
    {
        "num": 3,
        "slug": "rebrand",
        "title": "Rebrand the Game",
        "group": "Getting started",
        "badge": "Branding",
        "desc": "Step-by-step instructions to replace app names, icons, loading screens, home panels, UI art, and auto-canvas scaling."
    },
    {
        "num": 4,
        "slug": "items",
        "title": "Add & Edit Items",
        "group": "Items & Level Design",
        "badge": "Asset Tool",
        "desc": "Import item sprites, batch generate ItemData ScriptableObjects with the Items Data Generator, and assign items to pools."
    },
    {
        "num": 5,
        "slug": "level-editor",
        "title": "Understand the Level Editor",
        "group": "Items & Level Design",
        "badge": "Core Tool",
        "desc": "Master the 4 Level Editor tabs, toolbar actions, level configurations, 2D/3D cabinet layouts, and solvability validation."
    },
    {
        "num": 6,
        "slug": "create-level",
        "title": "Create Your First Level",
        "group": "Items & Level Design",
        "badge": "Tutorial",
        "desc": "A guided hands-on walkthrough to manually paint shelves, place items, test triplet balance, and verify solvability."
    },
    {
        "num": 7,
        "slug": "manage-levels",
        "title": "Edit & Manage Levels",
        "group": "Items & Level Design",
        "badge": "Workflow",
        "desc": "Modify existing levels, duplicate variations, renumber levels, sync the Level Database, and test individual stages."
    },
    {
        "num": 8,
        "slug": "level-generator",
        "title": "Generate Levels Automatically",
        "group": "Items & Level Design",
        "badge": "Generator",
        "desc": "Use the Procedural Single-Level Auto-Generator and Batch Generator to create hundreds of balanced stages with difficulty scaling."
    },
    {
        "num": 9,
        "slug": "shelves-and-obstacles",
        "title": "Change Shelves & Obstacles",
        "group": "Gameplay & Mechanics",
        "badge": "Gameplay",
        "desc": "Customize shelf visuals, slot offsets, match rules, lock thresholds, restricted shelves, movers, and slot obstacles."
    },
    {
        "num": 10,
        "slug": "boosters",
        "title": "Manage Boosters",
        "group": "Gameplay & Mechanics",
        "badge": "Mechanics",
        "desc": "Configure 9 gameplay boosters: Hint, Undo, Shuffle, Freeze Time, Extra Time, Hammer, Magnet, Magic Wand, and Unlock."
    },
    {
        "num": 11,
        "slug": "economy-and-rewards",
        "title": "Coins, Lives & Rewards",
        "group": "Gameplay & Mechanics",
        "badge": "Economy",
        "desc": "Tune starting currencies, life recovery intervals, out-of-lives popups, win stars, time bonuses, and continue options."
    },
    {
        "num": 12,
        "slug": "game-flow",
        "title": "Game Flow & UI Architecture",
        "group": "Gameplay & Mechanics",
        "badge": "Architecture",
        "desc": "Understand the state machine, GameFlowController, UIManager, popup transitions, guided tutorial steps, and camera fitter."
    },
    {
        "num": 13,
        "slug": "shop-and-iap",
        "title": "Shop Products & IAP Rewards",
        "group": "Monetization & Audio",
        "badge": "In-App Purchase",
        "desc": "Configure IAP databases, create custom product packs without code, and connect purchase buttons to reward deliveries."
    },
    {
        "num": 14,
        "slug": "ad-flow",
        "title": "Choose When Ads Appear",
        "group": "Monetization & Audio",
        "badge": "Monetization",
        "desc": "Control banner triggers, app open ads, interstitial frequencies, mid-game timers, and rewarded continue integrations."
    },
    {
        "num": 15,
        "slug": "audio",
        "title": "Change Music & Sounds",
        "group": "Monetization & Audio",
        "badge": "Audio",
        "desc": "Edit AudioCollection ScriptableObjects, replace home and gameplay music tracks, configure SoundManager, and adjust mixer groups."
    },
    {
        "num": 16,
        "slug": "data-assets",
        "title": "Important Data Assets",
        "group": "Reference & QA",
        "badge": "Architecture",
        "desc": "A summary table of all reusable ScriptableObject data assets across the project and their respective guide chapters."
    },
    {
        "num": 17,
        "slug": "testing-checklist",
        "title": "Test Your Changes (Checklist)",
        "group": "Reference & QA",
        "badge": "QA Checklist",
        "desc": "An exhaustive quality assurance checklist covering UI, levels, items, boosters, economy, ads, and audio before publishing."
    },
    {
        "num": 18,
        "slug": "faq",
        "title": "Common Questions (FAQ)",
        "group": "Reference & QA",
        "badge": "Support FAQ",
        "desc": "Answers and troubleshooting solutions for common questions regarding items, level generation, boosters, database sync, and saving."
    }
]

# Read the full markdown file
with open(MD_PATH, "r", encoding="utf-8") as f:
    full_md = f.read()

# Fix multi-line question headings (e.g. in FAQ)
full_md = re.sub(r'### ([^\n]+)\n\s*\n### ([^\n]+)', r'### \1 \2', full_md)

# Split into chapters
raw_chapters = re.split(r'\n(?=## \d+\. )', full_md)
chapter_map = {}
for i, ch in enumerate(raw_chapters[1:], 1):
    chapter_map[i] = ch

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text if text else "section"

def format_inline(text):
    # Bold with backticks or plain
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Markdown links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # Highlight Unity file paths if naked
    text = re.sub(r'(?<![="\'/])\b(Assets/[A-Za-z0-9_\-\.\/]+[A-Za-z0-9_\-])\b', r'<code>\1</code>', text)
    return text

def parse_markdown_to_sections(raw_text, ch_num):
    lines = raw_text.strip().split('\n')
    title_line = lines[0] # e.g. ## 1. Quick setup
    body_lines = lines[1:]

    # Break into subheadings if any, or process as one section
    sections = []
    current_sec = {"title": None, "id": "overview", "lines": []}
    
    for line in body_lines:
        if line.startswith('### '):
            if any(l.strip() for l in current_sec["lines"]) or current_sec["title"]:
                sections.append(current_sec)
            sec_title = line[4:].strip()
            sec_id = slugify(sec_title)
            current_sec = {"title": sec_title, "id": sec_id, "lines": []}
        else:
            current_sec["lines"].append(line)
            
    if any(l.strip() for l in current_sec["lines"]) or current_sec["title"]:
        sections.append(current_sec)

    parsed_sections = []
    
    for sec in sections:
        sec_title = sec["title"]
        sec_id = sec["id"]
        slines = sec["lines"]
        
        # Render blocks
        html_blocks = []
        i = 0
        while i < len(slines):
            line = slines[i].strip()
            
            if not line:
                i += 1
                continue
                
            # Image
            img_match = re.match(r'!\[([^\]]*)\]\([<]?([^>)]+)[>]?\)', line)
            if img_match:
                alt = img_match.group(1).strip()
                src = img_match.group(2).strip()
                # Relative to docs page: ../../images/...
                if src.startswith('images/'):
                    rel_src = '../../' + src
                else:
                    rel_src = '../../images/' + src
                caption_html = f'<figcaption>{html.escape(alt)}</figcaption>' if alt else ''
                block = f'''<figure class="doc-figure">
  <div class="doc-image-frame">
    <img src="{rel_src}" alt="{html.escape(alt)}" loading="lazy" />
  </div>
  {caption_html}
</figure>'''
                html_blocks.append(block)
                i += 1
                continue
                
            # Table
            if line.startswith('|') and '|' in line[1:]:
                table_lines = []
                while i < len(slines) and slines[i].strip().startswith('|'):
                    table_lines.append(slines[i].strip())
                    i += 1
                if len(table_lines) >= 2:
                    header_cells = [c.strip() for c in table_lines[0].split('|')[1:-1]]
                    body_rows = []
                    for t_line in table_lines[2:]:
                        row_cells = [c.strip() for c in t_line.split('|')[1:-1]]
                        body_rows.append(row_cells)
                    
                    th_html = ''.join([f'<th>{html.escape(c)}</th>' for c in header_cells])
                    tbody_html = ''
                    for r in body_rows:
                        tds = []
                        for cell_idx, c in enumerate(r):
                            # In Chapter 16 or 2, format links or paths nicely
                            formatted_c = format_inline(c)
                            tds.append(f'<td>{formatted_c}</td>')
                        tbody_html += f'<tr>{"".join(tds)}</tr>'
                    
                    block = f'''<div class="table-wrap">
  <table>
    <thead><tr>{th_html}</tr></thead>
    <tbody>{tbody_html}</tbody>
  </table>
</div>'''
                    html_blocks.append(block)
                continue
                
            # Step list (numbered list 1. ...)
            if re.match(r'^\d+\.\s+', line):
                step_items = []
                while i < len(slines) and (re.match(r'^\d+\.\s+', slines[i].strip()) or (step_items and slines[i].strip() and not slines[i].strip().startswith(('###', '##', '|', '![')))):
                    cur_line = slines[i].strip()
                    m = re.match(r'^\d+\.\s+(.*)', cur_line)
                    if m:
                        step_items.append(m.group(1))
                    elif step_items:
                        step_items[-1] += " " + cur_line
                    i += 1
                
                li_html = ''
                for s_idx, item_text in enumerate(step_items, 1):
                    s_num = f"{s_idx:02d}"
                    bold_m = re.match(r'^\*\*([^*]+)\*\*[:\s-]*(.*)', item_text)
                    if bold_m:
                        item_head = bold_m.group(1)
                        item_body = bold_m.group(2)
                    else:
                        parts = item_text.split('.', 1)
                        if len(parts) > 1 and len(parts[0]) < 40:
                            item_head = parts[0]
                            item_body = parts[1]
                        else:
                            item_head = f"Step {s_idx}"
                            item_body = item_text
                    
                    li_html += f'''<li>
  <span>{s_num}</span>
  <div><strong>{format_inline(item_head)}</strong><p>{format_inline(item_body)}</p></div>
</li>\n'''
                block = f'<ol class="step-list">{li_html}</ol>'
                html_blocks.append(block)
                continue
                
            # Checklist (- [ ] or - [x])
            if line.startswith('- [ ]') or line.startswith('- [x]'):
                tasks = []
                while i < len(slines) and (slines[i].strip().startswith('- [ ]') or slines[i].strip().startswith('- [x]')):
                    task_line = slines[i].strip()[5:].strip()
                    tasks.append(task_line)
                    i += 1
                checklist_html = '<ul class="feature-checks" style="margin: 20px 0; display: grid; gap: 14px;">'
                for t in tasks:
                    checklist_html += f'''<li style="font-size: 14px; padding-left: 30px; display: flex; align-items: flex-start; gap: 8px;">
  <span>{format_inline(t)}</span>
</li>'''
                checklist_html += '</ul>'
                html_blocks.append(checklist_html)
                continue

            # Bullet list (- ...)
            if line.startswith('- '):
                bullets = []
                while i < len(slines) and slines[i].strip().startswith('- '):
                    b_text = slines[i].strip()[2:].strip()
                    bullets.append(b_text)
                    i += 1
                b_html = '<ul class="doc-bullets">'
                for b in bullets:
                    b_html += f'<li>{format_inline(b)}</li>'
                b_html += '</ul>'
                html_blocks.append(b_html)
                continue

            # Callout checks: Tip, Important, Warning, Result
            if line.startswith(('**Tip:**', '**Important:**', '**Result:**', '**To rebrand an existing item:**', '**Conflict choices:**', '**Current behavior:**', '**Ready to customize:**', '**Save before changing levels')):
                callout_type = "tip"
                if "Important" in line or "Save before" in line:
                    callout_type = "important"
                elif "Result" in line:
                    callout_type = "info"
                elif "Warning" in line:
                    callout_type = "warning"
                
                parts = line.split('**', 2)
                title = parts[1].strip().rstrip(':')
                rest = parts[2].strip() if len(parts) > 2 else ""
                
                block = f'''<aside class="doc-callout {callout_type}">
  <strong>{format_inline(title)}</strong>
  <p>{format_inline(rest)}</p>
</aside>'''
                html_blocks.append(block)
                i += 1
                continue
                
            # Regular paragraph
            p_text = line
            i += 1
            while i < len(slines) and slines[i].strip() and not slines[i].strip().startswith(('###', '##', '|', '!<', '![-', '- ', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '**Tip:', '**Important:', '**Result:')):
                p_text += " " + slines[i].strip()
                i += 1
                
            html_blocks.append(f'<p>{format_inline(p_text)}</p>')

        content_html = "\n".join(html_blocks)
        if content_html.strip() or sec_title:
            parsed_sections.append({
                "title": sec_title,
                "id": sec_id,
                "html": content_html
            })
        
    return parsed_sections

def generate_sidebar_html(current_slug):
    groups = {}
    for ch in CHAPTER_DEFS:
        g = ch["group"]
        if g not in groups:
            groups[g] = []
        groups[g].append(ch)

    sidebar_html = f'''
  <!-- Sidebar Mobile Backdrop -->
  <div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleMobileSidebar()"></div>

  <!-- Sidebar -->
  <aside class="docs-sidebar" id="docsSidebar" style="width: var(--sidebar-width); flex-shrink: 0; height: 100vh; position: sticky; top: 0; background: var(--navy-900); border-right: 1px solid var(--sidebar-border); display: flex; flex-direction: column;">
    <div class="sidebar-brand-area" style="padding: 18px 14px 12px; border-bottom: 1px solid #293344;">
      <a class="brand-lockup sidebar-brand" href="../../index.html" style="color: #fff; margin-bottom: 15px;">
        <span class="brand-mark"><img src="../../images/icon.png" alt="Triple Match" /></span>
        <span><strong>Triple Match</strong><small>Item Sorting Kit</small></span>
      </a>
      <label class="sidebar-search">
        <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <input id="navSearchInput" aria-label="Search documentation navigation" placeholder="Search documentation" oninput="filterNavigation(this.value)" />
      </label>
    </div>

    <div class="sidebar-scroll" style="flex: 1; overflow-y: auto; padding: 8px 6px 18px;" id="sidebarNavContainer">
      <div class="sidebar-group" data-group="Overview">
        <ul style="list-style: none; padding: 0; margin: 0;">
          <li style="margin: 2px 0;">
            <a data-slot="sidebar-menu-button" 
               data-active="{"true" if current_slug == "overview" else "false"}" 
               data-title="kit overview home main"
               class="" 
               href="../../index.html" 
               style="display: flex; align-items: center; gap: 8px; padding: 7px 12px; border-radius: 6px; font-size: 12px; font-weight: 550; text-decoration: none; transition: background 0.15s ease;">
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
              <span>Main Overview</span>
            </a>
          </li>
        </ul>
      </div>
'''

    for g_name, g_items in groups.items():
        sidebar_html += f'''
      <div class="sidebar-group" data-group="{g_name}">
        <div data-slot="sidebar-group-label" style="padding: 10px 12px 6px; color: #77869b; font-size: 9px; text-transform: uppercase; letter-spacing: .14em; font-weight: 800;">{g_name}</div>
        <ul style="list-style: none; padding: 0; margin: 0;">
'''
        for item in g_items:
            is_active = (item["slug"] == current_slug)
            featured_cls = "featured-nav-item" if item["slug"] in ["quick-setup", "level-editor"] else ""
            num_str = f"{item['num']}. "
            
            sidebar_html += f'''
          <li style="margin: 2px 0;">
            <a data-slot="sidebar-menu-button" 
               data-active="{"true" if is_active else "false"}" 
               data-title="{item["title"].lower()} {num_str.lower()}"
               class="{featured_cls}" 
               href="../{item["slug"]}/index.html" 
               style="display: flex; align-items: center; gap: 8px; padding: 7px 12px; border-radius: 6px; font-size: 12px; font-weight: 550; text-decoration: none; transition: background 0.15s ease;">
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
              <span>{num_str}{item["title"]}</span>
            </a>
          </li>
'''
        sidebar_html += '        </ul></div>\n'

    sidebar_html += '''
      <p class="no-search-results" id="noSearchResults" style="display: none; padding: 18px; color: #6f7d90; font-size: 11px;">No matching page.</p>
    </div>

    <div class="sidebar-footer">
      <span><i class="status-dot"></i> Documentation v1.0.0</span>
      <small>Triple Match item sorting kit by bcyly Labs</small>
    </div>
  </aside>
'''
    return sidebar_html

def build_docs_page(ch_def, prev_ch, next_ch, sections):
    slug = ch_def["slug"]
    title = f"{ch_def['num']}. {ch_def['title']}"
    group = ch_def["group"]
    badge = ch_def["badge"]
    desc = ch_def["desc"]

    sidebar_html = generate_sidebar_html(slug)

    # Build TOC items
    toc_links = []
    sections_html = []
    
    for s_idx, sec in enumerate(sections):
        s_title = sec["title"]
        s_id = sec["id"]
        s_html = sec["html"]
        
        if not s_html.strip():
            continue
            
        if s_title:
            toc_links.append(f'<a href="#{s_id}">{html.escape(s_title)}</a>')
            if ch_def["num"] == 18:
                header_markup = f'<span class="section-eyebrow">Question {s_idx}</span><h2>{html.escape(s_title)}</h2>'
            elif re.match(r'^(Step|\d+\.|\d+)', s_title):
                header_markup = f'<h2>{html.escape(s_title)}</h2>'
            else:
                header_markup = f'<span class="section-eyebrow">Section {ch_def["num"]}.{s_idx}</span><h2>{html.escape(s_title)}</h2>'
            sec_markup = f'''<section class="doc-section" id="{s_id}">
  {header_markup}
  {s_html}
</section>'''
        else:
            # Chapter overview
            toc_links.append(f'<a href="#{s_id}">Overview</a>')
            sec_markup = f'''<section class="doc-section" id="{s_id}">
  {s_html}
</section>'''
        sections_html.append(sec_markup)

    article_content = "\n".join(sections_html)
    toc_nav = "".join(toc_links)

    prev_html = ""
    if prev_ch:
        prev_html = f'''
        <a class="page-link previous" href="../{prev_ch["slug"]}/index.html">
          <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>
          <span>
            <small>Previous</small>
            <strong>{prev_ch["num"]}. {prev_ch["title"]}</strong>
          </span>
        </a>'''
    else:
        prev_html = f'''
        <a class="page-link previous" href="../../index.html">
          <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>
          <span>
            <small>Previous</small>
            <strong>Main Overview</strong>
          </span>
        </a>'''

    next_html = ""
    if next_ch:
        next_html = f'''
        <a class="page-link next" href="../{next_ch["slug"]}/index.html">
          <span>
            <small>Next</small>
            <strong>{next_ch["num"]}. {next_ch["title"]}</strong>
          </span>
          <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
        </a>'''
    else:
        next_html = f'''
        <a class="page-link next" href="../../index.html">
          <span>
            <small>Next</small>
            <strong>Back to Overview</strong>
          </span>
          <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
        </a>'''

    page_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)} | Triple Match Documentation</title>
  <link rel="icon" type="image/png" href="../../images/icon.png" />
  <link rel="stylesheet" href="../../../assets/style.css" />
</head>
<body style="margin: 0; background: var(--canvas); color: var(--text); min-height: 100vh; display: flex;">

  {sidebar_html}

  <!-- Main Content Shell -->
  <div class="docs-main-shell" style="flex: 1; min-width: 0; display: flex; flex-direction: column; background: var(--canvas);">
    <header class="docs-topbar">
      <div style="display: flex; align-items: center; gap: 12px;">
        <button class="sidebar-toggle-btn" onclick="toggleMobileSidebar()" aria-label="Toggle documentation navigation">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/></svg>
        </button>
        <span style="font-weight: 700; color: #fff; letter-spacing: -0.01em;">Triple Match item sorting kit</span>
      </div>
      <div style="display: flex; align-items: center; gap: 14px;">
        <a href="../../triple-match-sorting-kit-bcyly-labs.apk" download class="top-link" style="color: #34d399; font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">
          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Download APK
        </a>
        <a href="../../Triple-Match-Item-Sorting-Kit-Setup-and-Customization-Guide.pdf" download class="top-link" style="color: #60a5fa; font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">
          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          PDF
        </a>
        <span class="version-pill">v1.0.0</span>
      </div>
    </header>

    <div class="docs-layout">
      <article class="docs-article">
        <nav class="breadcrumbs" aria-label="Breadcrumb">
          <a href="../../index.html">Documentation</a>
          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
          <span>{html.escape(group)}</span>
          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
          <strong>{html.escape(ch_def["title"])}</strong>
        </nav>

        <header class="page-header">
          <div class="page-meta">
            <span class="primary-badge">{html.escape(badge)}</span>
            <span>Chapter {ch_def["num"]} &middot; {html.escape(group)}</span>
          </div>
          <h1>{html.escape(title)}</h1>
          <p>{html.escape(desc)}</p>
        </header>

        {article_content}

        <nav class="page-pagination" aria-label="Documentation page navigation">
          {prev_html}
          {next_html}
        </nav>
      </article>

      <aside class="table-of-contents" aria-label="On this page">
        <strong>On this page</strong>
        <nav>
          {toc_nav}
        </nav>
      </aside>
    </div>
  </div>

  <script>
    function toggleMobileSidebar() {{
      const sidebar = document.getElementById('docsSidebar');
      const overlay = document.getElementById('sidebarOverlay');
      sidebar.classList.toggle('open');
      overlay.classList.toggle('active');
    }}

    function filterNavigation(query) {{
      const q = query.trim().toLowerCase();
      const items = document.querySelectorAll('#sidebarNavContainer [data-slot="sidebar-menu-button"]');
      const groups = document.querySelectorAll('#sidebarNavContainer .sidebar-group');
      let visibleCount = 0;

      items.forEach(btn => {{
        const title = btn.getAttribute('data-title') || '';
        const match = !q || title.includes(q);
        const li = btn.closest('li');
        if (li) li.style.display = match ? 'block' : 'none';
        if (match) visibleCount++;
      }});

      groups.forEach(group => {{
        const visibleItemsInGroup = group.querySelectorAll('li:not([style*="display: none"])');
        group.style.display = visibleItemsInGroup.length > 0 ? 'block' : 'none';
      }});

      const noResults = document.getElementById('noSearchResults');
      if (noResults) {{
        noResults.style.display = visibleCount === 0 ? 'block' : 'none';
      }}
    }}
  </script>
</body>
</html>'''

    out_folder = os.path.join(DOCS_DIR, slug)
    os.makedirs(out_folder, exist_ok=True)
    out_file = os.path.join(out_folder, "index.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(page_html)
    print(f"Generated docs page: {out_file}")

# Generate all 18 doc pages
for i, ch_def in enumerate(CHAPTER_DEFS):
    raw_md = chapter_map[ch_def["num"]]
    sections = parse_markdown_to_sections(raw_md, ch_def["num"])
    prev_ch = CHAPTER_DEFS[i - 1] if i > 0 else None
    next_ch = CHAPTER_DEFS[i + 1] if i < len(CHAPTER_DEFS) - 1 else None
    build_docs_page(ch_def, prev_ch, next_ch, sections)

print("All 18 documentation pages generated successfully.")

# Build Main Landing Page
landing_html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Triple Match item sorting kit | Setup & Customization Guide</title>
  <link rel="icon" type="image/png" href="images/icon.png" />
  <link rel="stylesheet" href="../assets/style.css" />
</head>
<body class="site-home">
  <header class="home-topbar">
    <a class="brand-lockup" href="index.html" aria-label="Triple Match documentation home">
      <span class="brand-mark"><img src="images/icon.png" alt="Triple Match" /></span>
      <span>
        <strong>Triple Match</strong>
        <small>Item Sorting Kit</small>
      </span>
    </a>
    <div class="home-top-actions">
      <span class="version-pill">v1.0.0</span>
      <a class="top-link" href="docs/quick-setup/index.html">Open documentation</a>
    </div>
  </header>

  <section class="home-hero">
    <div class="hero-grid" aria-hidden="true"></div>
    <div class="hero-copy">
      <div class="eyebrow">
        <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        Unity 3D Puzzle Game Kit
      </div>
      <h1>Triple Match<br />item sorting kit</h1>
      <p class="tagline">The Complete Goods Sorting & Matching Foundation for Unity</p>
      <p class="hero-description">
        A complete, commercial-ready puzzle game template by bcyly Labs. Features ready-to-use game screens, custom items generator, procedural level generator & visual editor, 9 boosters, timed lives recovery, shop rewards, and multi-network ad flow architecture.
      </p>
      <div class="hero-actions">
        <a class="primary-action" href="docs/quick-setup/index.html">
          Start with Quick Setup <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
        </a>
        <a class="secondary-action" href="triple-match-sorting-kit-bcyly-labs.apk" download style="display: inline-flex; align-items: center; gap: 7px; color: #34d399; border-color: rgba(52, 211, 153, 0.4); background: rgba(52, 211, 153, 0.08);">
          <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg> Download APK (54.8 MB)
        </a>
        <a class="secondary-action" href="docs/level-editor/index.html">Level Editor Guide</a>
      </div>
      <div class="hero-facts">
        <span><svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> Unity 6000.3+ LTS</span>
        <span><svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/></svg> Visual & Batch Level Editor</span>
        <span><svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg> 9 Interactive Boosters</span>
        <span><svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg> IAP & Ads Monetization</span>
      </div>
    </div>
    <div class="hero-visual">
      <figure class="doc-figure" style="margin: 0;">
        <div class="doc-image-frame" style="box-shadow: 0 32px 60px rgba(0,0,0,.5); border-color: #344155;">
          <img src="images/01_Quick_Setup/04_game_running.png" alt="Triple Match in-game running screenshot" loading="eager" />
        </div>
      </figure>
      <div class="hero-visual-label">
        <span class="pulse-dot"></span> Commercial Ready Unity Puzzle Kit
      </div>
    </div>
  </section>

  <section class="home-section foundation-section">
    <div class="section-heading">
      <div>
        <span class="section-kicker">The foundation</span>
        <h2>Design handcrafted levels or batch-generate hundreds.</h2>
      </div>
      <p>
        The Level Generator & Visual Designer gives you complete creative freedom. Inspect 2D/3D cabinet layouts, paint item layers with depth, verify solvability, and automate entire campaign progressions.
      </p>
    </div>

    <div class="upgrade-feature-card">
      <div class="upgrade-feature-copy">
        <span class="component-number">01 · Core Editor Suite</span>
        <h3>Level Generator & Visual Designer</h3>
        <p>
          Author levels visually by placing shelves, painting item slots across 3 depth layers, and toggling locks and restrictions. Or leverage procedural generation with customizable shapes, difficulty sawtooth pacing, and built-in solvability verification.
        </p>
        <ul class="feature-checks">
          <li>Visual Shelf Designer & Cabinet Reshaper</li>
          <li>Procedural Single-Level & Batch Auto-Generator</li>
          <li>Solvability Simulator & Triplet Balance Matrix</li>
          <li>Automated Alphabet & Number Level Generator (36 Layouts)</li>
        </ul>
        <a class="text-action" href="docs/level-editor/index.html">
          Read the complete Level Editor guide <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
        </a>
      </div>
      <div class="upgrade-feature-media">
        <figure class="doc-figure" style="margin: 0;">
          <div class="doc-image-frame" style="border-radius: 12px; overflow: hidden;">
            <img src="images/04_Level_Editor/02_full_editor_window.png" alt="Level Editor window overview" loading="lazy" />
          </div>
        </figure>
      </div>
    </div>
  </section>

  <section class="home-section">
    <div class="compact-heading">
      <span class="section-kicker">Supporting components</span>
      <h2>A connected puzzle architecture.</h2>
      <p>
        Every system is modular, inspector-configurable, and designed for commercial release without writing complex custom code.
      </p>
    </div>

    <div class="component-grid" style="grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));">
      <a class="component-card" href="docs/items/index.html">
        <span class="component-icon"><svg xmlns="http://www.w3.org/2000/svg" width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg></span>
        <h3>Items Data Generator</h3>
        <p>Batch generate ItemData ScriptableObjects from sliced sprite sheets with auto ID detection and conflict handling.</p>
        <span class="card-link">Explore component <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></span>
      </a>

      <a class="component-card" href="docs/shelves-and-obstacles/index.html">
        <span class="component-icon"><svg xmlns="http://www.w3.org/2000/svg" width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg></span>
        <h3>Shelves & Obstacles</h3>
        <p>Full shelf match rules, triple match anywhere, locked shelves, restricted placement, movers, and slot obstacles.</p>
        <span class="card-link">Explore component <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></span>
      </a>

      <a class="component-card" href="docs/boosters/index.html">
        <span class="component-icon"><svg xmlns="http://www.w3.org/2000/svg" width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></span>
        <h3>9 Boosters Suite</h3>
        <p>Hint, Undo, Shuffle, Freeze Time, Extra Time, Hammer, Magnet, Magic Wand, and Unlock shelves.</p>
        <span class="card-link">Explore component <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></span>
      </a>

      <a class="component-card" href="docs/economy-and-rewards/index.html">
        <span class="component-icon"><svg xmlns="http://www.w3.org/2000/svg" width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg></span>
        <h3>Economy & Lives System</h3>
        <p>Coins balance, timed heart recovery intervals, out of lives popups, time bonus multipliers, and continue rescues.</p>
        <span class="card-link">Explore component <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></span>
      </a>

      <a class="component-card" href="docs/shop-and-iap/index.html">
        <span class="component-icon"><svg xmlns="http://www.w3.org/2000/svg" width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg></span>
        <h3>Shop & IAP Rewards</h3>
        <p>Configurable product assets, coin packs, bundle deals, infinite lives, remove ads, and reward delivery pipeline.</p>
        <span class="card-link">Explore component <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></span>
      </a>

      <a class="component-card" href="docs/ad-flow/index.html">
        <span class="component-icon"><svg xmlns="http://www.w3.org/2000/svg" width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg></span>
        <h3>Ad Flow Controller</h3>
        <p>Banner, App Open, interstitial level frequency, mid-game timers, and rewarded continue callbacks.</p>
        <span class="card-link">Explore component <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></span>
      </a>
    </div>
  </section>

  <section class="home-section documentation-map">
    <div class="compact-heading">
      <span class="section-kicker">Documentation structure</span>
      <h2>18 Comprehensive Chapters.</h2>
      <p>Structured, step-by-step guides supported by high-resolution Unity Editor screenshots for every single feature.</p>
    </div>

    <div class="category-grid">
      <div class="category-row">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>
        <span>
          <strong>Getting Started & Rebranding</strong>
          <small>Quick setup, quick reference guide, and rebranding game assets</small>
        </span>
      </div>
      <div class="category-row">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/></svg>
        <span>
          <strong>Items & Level Creation</strong>
          <small>Item data generator, visual designer, manual painting, and batch generator</small>
        </span>
      </div>
      <div class="category-row">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
        <span>
          <strong>Shelves, Boosters & Gameplay</strong>
          <small>Shelf match rules, locks, 9 boosters, lives system, and state machine flow</small>
        </span>
      </div>
      <div class="category-row">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg>
        <span>
          <strong>Monetization & Audio</strong>
          <small>IAP database setup, rewarded ad callbacks, and audio mixer routing</small>
        </span>
      </div>
      <div class="category-row">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
        <span>
          <strong>Reference & Verification</strong>
          <small>Data assets directory, full QA checklist, and common troubleshooting FAQ</small>
        </span>
      </div>
    </div>
  </section>

  <footer class="home-footer">
    <span>Triple Match item sorting kit</span>
    <span>Documentation v1.0.0 &middot; Developed by bcyly Labs</span>
  </footer>
</body>
</html>'''

landing_file = os.path.join(TARGET_DIR, "index.html")
with open(landing_file, "w", encoding="utf-8") as f:
    f.write(landing_html)
print(f"Generated landing page: {landing_file}")
