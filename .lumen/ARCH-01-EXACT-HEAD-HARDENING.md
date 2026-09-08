# ARCH-01 EXACT-HEAD HARDENING

Previous CI run was green but GitHub Actions checked the synthetic pull-request
merge commit instead of the PR head commit. The workflow now:

- checks out the exact PR head SHA;
- asserts git HEAD equals that SHA before any test;
- runs on Linux and Windows against that exact SHA;
- uses current Node-24-compatible checkout/setup-python actions;
- keeps Golden Sanctuary hash protection.

This correction does not change the LUMEN product or canonical assets.
