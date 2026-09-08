# LUMEN — T-007R Independent Review

**Decision: ITERATE**

01R proves the architecture: the browser observed real multi-layer motion and the main blockers from T-007 are technically addressed. However, the live frame is not yet production-grade because it visibly softens the canonical artwork.

## Validated
- Canon screenshot exact: sampled MAE = 0.
- Differential motion observed.
- Traveler / portal / foreground architecture are independent assets.
- COMPRENDRE uses a portal/camera traversal.
- VOIR and AGIR are explicitly locked.
- No debug overlay and no Community section.

## Blocking findings
1. **Sharpness regression.** Independent full-frame analysis: Laplacian variance ≈ 2245 (canon) → 1012 (live rest) → 605 (motion).
2. **Rest-state fidelity is too low.** Full-frame MAE ≈ 14.42 and SSIM ≈ 0.587. The portal is over-bloomed and text/architecture are softer.
3. **Cause identified.** Per-layer scale, whole-stage 3D rotation and screen blend on duplicated canonical pixels create resampling/brightness drift.
4. **Library remains flat.** This is allowed for this milestone but not a completed Library.

## Next acceptance criteria
- Rest browser MAE <= 2.5.
- Rest sharpness >= 90% of canon.
- Differential motion still observed.
- No whole-stage tilt during ordinary motion.
- Normal compositing at rest; no screen-blend duplication of canonical pixels.
- Portal traversal still functional.

## Next action
**LUMEN-SCENE-ENGINE-01R2** — fidelity-first parallax.
