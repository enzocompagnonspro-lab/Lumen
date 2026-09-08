# LUMEN-SCENE-ENGINE-01R2 — fidelity-first correction

This iteration answers T-007R = ITERATE.

## Changes
- Removed whole-stage tilt during ordinary parallax.
- Removed per-layer scale at rest.
- Switched cloud / portal / gold canonical cutouts from screen blending to normal compositing at rest.
- Kept the exact canonical base alignment so the resting frame should reconstruct the canon almost pixel-for-pixel.
- Kept differential translation with reduced amplitudes to preserve crisp typography and architecture.
- Portal still receives an interactive brightness lift only on hover/focus and during traversal.
- Tightened browser QA: rest MAE <= 2.5, motion delta bounded, and rest sharpness ratio >= 0.90.

## Why
01R proved multi-layer motion but lost too much sharpness. 01R2 prioritizes canonical fidelity first, then motion.
