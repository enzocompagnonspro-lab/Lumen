# LUMEN PRIME V2 + LUMEN OS

Synchronize an existing LUMEN OS workspace into the graph:

```powershell
python .\runtime\lumen_prime.py init-db
python .\runtime\lumen_prime.py sync-os --root "C:\path\to\LUMEN-OPERATING-SYSTEM-V1.5.2"
python .\runtime\lumen_prime.py stats
```

Build a context packet for a request:

```powershell
python .\runtime\lumen_prime.py context "analyse la progression de Vision et propose la prochaine action"
```

This does not call an external model by itself. It prepares the governed context and model-selection policy for the model runtime.
