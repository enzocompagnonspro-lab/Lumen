# HOTFIX 1.7.2 — REAL-01 browser E2E

The previous gate expected `REAL01_E2E_PASS` from the same Chrome `--dump-dom` invocation that triggered a dynamic JavaScript navigation. That is not deterministic.

1. Chrome A executes `?qa=e2e-seed` and writes the complete journey state to localStorage.
2. Chrome A exits.
3. Chrome B starts with the exact same temporary browser profile.
4. Chrome B opens `?qa=e2e-verify`.
5. The gate requires `REAL01_E2E_PASS`.

This proves persistence across a browser restart, which is stricter than a same-process reload. No product content, canonical asset, acceptance threshold, or human gate is changed. Diagnostic DOM and stderr files are preserved under `evidence/real-01/windows/` on failure.
