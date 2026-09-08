# VERIFIED TOOL SELECTION — 2026-09-08

The plan was re-checked against current official product documentation and connected tool schemas.

## OpenAI
- GPT-6 Astra is listed in OpenAI API docs as the most capable flagship model for hardest end-to-end work.
- GPT-5.6 Sol remains the flagship complex-professional model and current reliable fallback.
- GPT-Image-2 is the current state-of-the-art OpenAI image generation/editing model.
- text-embedding-3-large is the most capable OpenAI embedding model.
- GPT-Realtime-2.1 family is listed for realtime speech/tool workflows.

Official:
https://developers.openai.com/api/docs/models
https://developers.openai.com/api/docs/models/gpt-image-2
https://developers.openai.com/api/docs/models/text-embedding-3-large

## Anthropic
- Claude Fable 5.1 is Anthropic's most capable generally available model for ambitious coding/knowledge work.
- Claude Opus 5 is a strong lower-cost independent reviewer.

Official:
https://www.anthropic.com/claude/fable
https://www.anthropic.com/news/claude-opus-5

## Google
- Gemini 3.8 Flash is production-ready and designed for long-running software/agent workflows.
- Veo 3.1 is the current video generation line to target.
- Lyria 3.5 is Google's newest music generation model.

Official:
https://ai.google.dev/gemini-api/docs/latest-model
https://ai.google.dev/gemini-api/docs/changelog
https://deepmind.google/models/lyria/

## Figma
Figma's MCP/agent stack now supports structured design context and write operations, making it appropriate as the editable design source of truth.

Official:
https://www.figma.com/blog/the-figma-canvas-is-now-open-to-agents/
https://www.figma.com/mcp-catalog/

## Adobe
Firefly exposes multiple partner image/video models in one studio, including GPT Image/Gemini/Imagen/Runway image paths and Veo/Runway/Kling video paths. This supports LUMEN's tournament strategy.

Official:
https://helpx.adobe.com/firefly/web/create-mood-boards/firefly-boards/use-non-adobe-models-to-generate-images.html
https://helpx.adobe.com/firefly/web/work-with-audio-and-video/work-with-video/generate-videos-using-non-adobe-models.html

## Connected connector verification
In this ChatGPT environment, connected tool schemas were inspected for:
- Figma design read/write, motion and Code Connect
- Adobe generation/editing
- GitHub repo/PR/CI operations (write currently returns 403)
- Neon branching/Auth/Data API/storage/snapshots
- Vercel previews/deployments/logs
- HeyGen translation/lip-sync/glossary
- Google Drive
- Notion

This architecture therefore distinguishes:
AVAILABLE CONNECTOR
AVAILABLE API MODEL
CANDIDATE
HUMAN-GATED
instead of treating all named tools as already active.
