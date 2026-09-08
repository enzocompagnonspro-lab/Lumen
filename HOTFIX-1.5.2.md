# LUMEN OS 1.5.2 — Journey persistence QA hardening

## Root cause
The previous E2E harness tried to certify persistent browser state from a `file://` origin and split seed/verify across Chrome invocations. That is not a reliable storage contract for production-grade QA.

## Fix
- Serve the Golden Sanctuary locally over `http://127.0.0.1:<ephemeral-port>`.
- Use a single Chrome invocation for the persistence test.
- Seed state through the same article-section click handlers used by the UI.
- Trigger a real browser `location.reload()`.
- Verify the Journey state after reload.
- Preserve the final DOM and local HTTP server logs in `evidence/` for diagnostics.
- Keep all visual and governance gates unchanged.

No canon, visual QA threshold, Human Gate, or public-write policy is relaxed.
