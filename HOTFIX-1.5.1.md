# LUMEN OS v1.5.1 — Browser persistence QA hotfix

The Living-02 product code and technical QA were already passing. The Windows certification could fail because the final persisted-state screenshot was launched as a second Chrome process immediately after a same-profile `--dump-dom` invocation. Chrome could still hold/release the temporary profile, causing the screenshot process to exit without writing the PNG.

## Fix
- Keep the same temporary Chrome profile.
- Seed state with `--dump-dom`.
- Wait briefly for LocalStorage/profile flush.
- Run **persistence verification and persisted screenshot in the same Chrome invocation** (`--dump-dom` + `--screenshot`).
- Explicitly wait for every capture to exist and exceed the minimum size.
- No QA threshold is relaxed.

Run `scripts/CERTIFY-LIVING-02.ps1` exactly as before.
