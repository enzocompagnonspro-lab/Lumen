# LUMEN REAL-01 — Playwright Mobile Gate 02

Observed blocker at HEAD:
8d6a4ea19c30cc45d7598e8f443dee345b822cff

Playwright 1.62 Python exposes Page.wait_for_function with rg as a keyword-only
argument. The first gate passed expected_stage positionally, causing:

TypeError: Page.wait_for_function() takes 2 positional arguments but 3 positional
arguments (and 1 keyword-only argument) were given.

Correction:
rg=expected_stage

No product change, no canonical visual change, no gate weakening.
Golden Sanctuary remains:
e056e7f7ab8b71cd82a05763d8390d61bc5afa50c5c50d1a34b21b90e1a72bb1
