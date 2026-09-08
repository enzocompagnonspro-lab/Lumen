# LUMEN OS V1.7.1 — REAL-01 PowerShell 5.1 hotfix

## Symptom
`CERTIFY-REAL-01.ps1` stopped after a successful unittest line such as:

`test_catalog_truth (...) ... ok`

with PowerShell reporting `NativeCommandError`.

## Root cause
Python `unittest -v` writes its normal progress stream to STDERR. Windows PowerShell 5.1 converts native STDERR into PowerShell error records. Because the certification script intentionally uses `$ErrorActionPreference = "Stop"`, the pipeline could terminate even when Python returned exit code 0.

## Correction
The unittest phase now runs through `Start-Process` with explicit stdout/stderr evidence files. The certification gate is based only on the child process `ExitCode`.

This is a harness-only correction. No REAL-01 content, canon, Journey logic, source registry, threshold, Human Gate, or browser acceptance criterion was changed.

## Expected behavior
A passing test suite prints `REAL-01 UNIT TESTS PASS` and certification continues to the Golden Sanctuary hash check and real Chrome desktop/mobile E2E evidence generation.
