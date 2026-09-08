# QA AND GATES

## G0 Contract Gate
TaskContract schema valid. Authority and budget explicit.

## G1 Static Gate
Formatting, lint, typecheck, schema, content integrity.

## G2 Functional Gate
Unit + integration tests.

## G3 Experience Gate
Playwright E2E on desktop and mobile profiles.
Screenshots captured from real browser.

## G4 Canon Gate
Golden hashes / required visual landmarks / scene semantic contract.
Visual diff must be reviewed, not blindly thresholded.

## G5 Accessibility & Performance
axe
keyboard path
reduced motion
Web Vitals
GPU tier fallback

## G6 Evidence Gate
Every material claim/action linked to evidence.
No REPORTED→OBSERVED promotion.

## G7 Independent Review
Different logical reviewer.
Golden: preferably different provider (Claude Fable 5.1).

## G8 Human Golden Gate
Enzo approves canon.

## G9 Production Gate
Exact reviewed SHA only.
No production deploy from a moving branch.
