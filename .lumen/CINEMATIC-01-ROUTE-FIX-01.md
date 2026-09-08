# LUMEN CINEMATIC-01 — Route Fix 01

Observed blocker:
Playwright timed out waiting for #enterVoir.

Root cause:
The local REAL-01 server served files under /golden-journey/..., but when the
request targeted a nested directory such as /golden-journey/cinematic-voir/,
_file() rejected the directory with 404 instead of serving its index.html.

Correction:
- nested project directories resolve to their local index.html;
- project-root boundary is rechecked after index resolution;
- no product/canon change;
- rerun exact route probe and CINEMATIC-01 browser certification.

Golden Sanctuary remains immutable:
e056e7f7ab8b71cd82a05763d8390d61bc5afa50c5c50d1a34b21b90e1a72bb1
