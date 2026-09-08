# LUMEN PRIME MODEL V2 — MEMORY + KNOWLEDGE GRAPH

LUMEN PRIME V2 is the governed intelligence layer for LUMEN.

## New in V2
- quality-first model policy
- GPT-6 Astra preference when actually available/entitled
- GPT-5.6 Sol fallback
- SQLite persistent memory
- typed knowledge graph
- synchronization with real LUMEN OS registries
- context packet builder
- evidence/provenance memory
- Journey-aware graph

## Important model truth
This package cannot switch the model of the ChatGPT conversation that created it. It is designed so the deployed LUMEN runtime can prefer the newest authorized frontier model and fall back safely.

## Windows certification
```powershell
Get-ChildItem .\*.ps1 | Unblock-File
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\CERTIFY-LUMEN-PRIME-V2.ps1
```

## Sync your live LUMEN OS after certification
```powershell
python .\runtime\lumen_prime.py sync-os --root "C:\Users\enzop\Downloads\LUMEN-OPERATING-SYSTEM-V1.5.2\LUMEN-OPERATING-SYSTEM-V1.5.2"
python .\runtime\lumen_prime.py stats
```
