# LUMEN REAL-01 — R008 ITERATE 04

Observed failure:
mobile-sanctuary DOM probe reported innerWidth=762 while the requested QA
capture size was 390x844.

Root cause:
Assert-LumenQaDom used Invoke-LumenChromeDump without passing the requested
viewport. The screenshot path did pass:
- --force-device-scale-factor=1
- --window-size=<requested size>

Therefore the gate compared a default Chrome DOM viewport to a 390px screenshot
request.

Correction:
The QA DOM probe now launches an isolated Chrome process with the SAME viewport,
scale, virtual-time and compositor flags as the screenshot path.

Acceptance remains strict:
- mobile innerWidth must equal 390
- mobile scrollWidth must be <=390
- requested QA stage must be present
- Golden Sanctuary hash remains immutable

No merge, deploy, canon change, or independent-review claim.
