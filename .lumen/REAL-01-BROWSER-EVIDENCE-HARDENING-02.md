# REAL-01 Browser Evidence Hardening 02

This correction:
- makes Chrome screenshot calls PowerShell-5.1-safe via Start-Process;
- evaluates the real Chrome exit code;
- stores Chrome stdout/stderr per screenshot;
- requires each screenshot to exist and exceed the size gate;
- treats only the three known lumen_os.py validate runtime files as safe generated dirt;
- backs up their local diff before restoring them;
- refuses to clean any unexpected user/source modification.

No LUMEN content or canonical visual is changed.
Golden Sanctuary SHA256 remains:
e056e7f7ab8b71cd82a05763d8390d61bc5afa50c5c50d1a34b21b90e1a72bb1
