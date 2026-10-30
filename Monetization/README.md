# bcylyLabs Monetization static manual

Open `index.html` directly in a browser. All four chapters and six supplied screenshots are already compiled into a static HTML/CSS documentation page. No server, dependency installation or client-side Markdown renderer is required.

## Included content

1. Documentation Index
2. User Guide
3. Developer Reference & API Examples
4. Testing & Troubleshooting

The manual is package-specific and excludes game integration guides. It follows the existing bcylyLabs IAP documentation's navy navigation, blue accents, light reading canvas, chapter cards, steps, tables, callouts, code blocks and contents layout.

## Layout and files

- `index.html`: precompiled complete manual.
- `assets/style.css`: shared portfolio documentation theme, copied locally without remote fonts.
- `assets/monetization.css`: matching documentation layout, responsive and print rules.
- `assets/manual.js`: optional navigation search, active-section tracking, mobile drawer, code copying, image zoom and print controls.
- `assets/images/`: all six supplied screenshots, copied without modifying image content.
- `content/`: local Markdown copies used for this compiled version.
- `build.mjs`: repeatable compiler using the four parent Markdown files.
- `validate.mjs`: structural checks for chapters, screenshots, local files, anchors and template leftovers.

## Rebuild and validate

Run these from this folder with Node 18 or later:

```text
node build.mjs
node validate.mjs
node --check assets/manual.js
```

The builder reads the parent Documentation folder and updates index.html/content/. It does not depend on the IAP documentation or portfolio folder. Screenshots and theme files are already included and do not need rebuilding.

The page works offline. External documentation/support links need internet only when followed. Print manual uses the browser's print dialog and a print stylesheet; a PDF is not bundled.

Copy the whole folder to any static host to serve it. This delivery did not publish or alter a hosted site, change the portfolio folder or edit package runtime code.
