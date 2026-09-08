# OpenAI provider adapter policy

LUMEN PRIME V2 deliberately does **not** hard-code an unverified API model identifier.

Runtime configuration should supply a model identifier only when the target OpenAI surface exposes it.

Quality-first selection:
1. GPT-6 Astra / GPT-6 Pro when available and entitled.
2. GPT-5.6 Sol at High reasoning as fallback.

Environment variables reserved for an actual adapter:
- `LUMEN_OPENAI_FRONTIER_MODEL_ID`
- `LUMEN_OPENAI_PRIMARY_MODEL_ID`

The runtime must log the observed model returned by the provider before claiming which model executed a request.
