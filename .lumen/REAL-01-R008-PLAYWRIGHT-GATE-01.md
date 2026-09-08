# LUMEN REAL-01 — Playwright Mobile Gate 01

Observed limitation of raw Chrome headless on Windows:
--window-size=390,844 produced window.innerWidth=500 because the browser
window path is clamped before layout.

This is not accepted as a true 390 CSS-pixel mobile proof.

Correction:
- Playwright 1.62.0 BrowserContext viewport emulation;
- exact viewport 390x844 for mobile and 1672x941 for desktop;
- system Google Chrome executable, no bundled-browser download;
- innerWidth == requested width;
- documentElement.scrollWidth <= requested width;
- ody.scrollWidth <= requested width;
- mobile media query must be active;
- PNG dimensions must exactly match the requested viewport;
- QA-ready and QA-stage markers are mandatory;
- transmission screenshot must not equal canon;
- E2E persistence is re-proved across a fresh Chrome process/profile reopen.

Golden Sanctuary remains immutable:
e056e7f7ab8b71cd82a05763d8390d61bc5afa50c5c50d1a34b21b90e1a72bb1

No merge, deploy, canon promotion or independent-review claim.
