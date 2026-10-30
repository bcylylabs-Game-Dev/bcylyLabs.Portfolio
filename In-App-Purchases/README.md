# bcylyLabs IAP static documentation

Open `index.html` in a browser. The complete manual and seven screenshots work offline; no package installation, server or JavaScript rendering is required. Optional JavaScript supplies navigation search, active-section tracking, code copying, mobile navigation, screenshot enlargement and printing.

## Files

- `index.html`: precompiled documentation index, user guide, developer reference and testing/troubleshooting.
- `assets/style.css`: a local copy of the portfolio documentation theme, with its remote font import removed for offline use.
- `assets/iap.css`: IAP manual layout and responsive/print additions.
- `assets/manual.js`: optional progressive enhancements.
- `assets/images/`: the seven supplied, unmodified screenshots.
- `content/`: package-only Markdown sources compiled into the manual.
- `build.mjs`: repeatable Node build from the four Markdown documents in the parent Documentation directory, including project-specific content filtering.

The manual intentionally excludes the Goods Sort integration guide. Project-specific names visible inside screenshots are example data, not required package configuration.

## Rebuild

Run `node build.mjs` from this folder (Node 18+). It reads the parent Markdown sources and updates index.html and content/. It does not modify the portfolio folder or copy new images/theme files automatically.

For deployment, copy this folder to any static host. No build step is required to serve the checked-in HTML. No hosting or publication was performed as part of this delivery.

## Styling reference

The UPFS and Triple Match documentation under `D:\bcylyLabs.Portfolio\Documentation_Website` were inspected read-only. The page follows their navy sidebar/topbar, blue accents, light canvas, section hierarchy, steps, callouts, code blocks, table styling and contents navigation. The reference folder was not modified.

Use the browser's Print command for the print stylesheet. That command is not a bundled PDF export.
