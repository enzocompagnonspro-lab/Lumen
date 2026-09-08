# SYSTEM ARCHITECTURE

## 1. Experience Plane

### Frontend stack
- Next.js + TypeScript
- React
- React Three Fiber / Three.js for 2.5D and selective 3D
- Motion for UI transitions
- GSAP only for choreographed cinematic timelines that are awkward in Motion
- XState for the Journey state machine
- Web Audio API for spatial ambience and ducking
- PWA-capable responsive shell

### Rendering strategy
LUMEN uses progressive fidelity:
- HIGH: desktop GPU — layered parallax, shaders, particles, spatial sound
- BALANCED: mobile/high-end tablet — reduced particles/shaders
- SAFE: low-power/reduced-motion — canonical still composition + semantic UI

The canonical composition must survive every tier.

### Performance budgets
- LCP target < 2.5s on supported production networks
- interaction latency < 100 ms for local UI responses
- 60 fps preferred desktop, stable 30+ fps minimum animated mobile
- reduced-motion mode must be a first-class implementation, not a CSS afterthought

## 2. Intelligence Plane

### LUMEN Governor
Responsibilities:
- understand objective
- load only relevant canon/state
- select specialists
- apply model/cost policy
- require citations/provenance
- synthesize a single coherent result
- never self-close a Human Gate

### Specialist desks
- SOURCE_SCOUT
- TRUTH_SYNTHESIZER
- KNOWLEDGE_ARCHITECT
- JOURNEY_GUIDE
- PRACTICE_DESIGNER
- ART_DIRECTOR
- VIDEO_DIRECTOR
- AUDIO_DIRECTOR
- SOFTWARE_ARCHITECT
- CODEX_WORKER
- INDEPENDENT_REVIEWER

## 3. Knowledge Plane

Canonical editorial content stays Git-versioned.
User state and evidence stay in Neon.

Hybrid knowledge search:
- PostgreSQL full-text
- pgvector
- `text-embedding-3-large`
- reranking/synthesis by Governor

Every important assertion becomes a ClaimRecord and must point to SourceRecords.

## 4. Creative Plane

### Figma
Canonical design tokens, component library, layouts, motion specification, Code Connect.

### Adobe
Creative finishing, image edits, composition, boards, and model-provider tournament studio.

### Image Tournament
Provider-neutral SceneSpec.
Default candidates:
- GPT-Image-2
- Gemini image/Imagen candidate exposed by approved provider
- Adobe/Runway candidate where appropriate

### Video Tournament
Default candidates:
- Veo 3.1
- Runway Gen-4.5
- Kling 3.0 / Omni candidate

A shot may choose a different renderer based on:
- identity consistency
- camera control
- motion physics
- prompt/reference adherence
- audio requirements
- artifacts
- cost

### Audio
- Lyria 3.5: music composition
- GPT-Realtime-2.1: interactive spoken LUMEN guide
- HeyGen: translated/lip-synced derivatives of pre-rendered human/avatar video

## 5. Engineering Plane

Canonical repository target:
`enzocompagnonspro-lab/Lumen`

Repository layout target:

```
apps/web
packages/ui
packages/scene-engine
packages/journey-engine
packages/knowledge
packages/model-gateway
packages/evidence
packages/media-spec
content/lessons
content/sources
canon/assets
canon/manifests
contracts/tasks
evidence
tests
AGENTS.md
```

Codex writes only to isolated branches/worktrees.

CI:
- format/lint/typecheck
- unit tests
- schema tests
- Golden hash guard
- Playwright E2E
- desktop/mobile screenshots
- visual diff
- axe accessibility
- build
- Vercel preview

## 6. Data Plane

Neon environments:
- DEV
- STAGING
- PROD

Core tables:
- users
- journey_state
- source_records
- claim_records
- knowledge_objects
- practice_records
- reflection_metadata
- evidence_records
- model_runs
- task_contracts
- review_records
- media_jobs
- cost_ledger

Private reflection text should remain local-first initially.
Cloud sync of raw private reflections is opt-in later.

## 7. Trust Plane

Automation ceiling: L3.

L0 read
L1 draft
L2 safe isolated write
L3 PR / preview / staged media
L4 Human Gate

Human-only:
- canonical visual promotion
- doctrine change
- merge to production branch
- production deploy
- LIVE payments
- irreversible data changes
- budget increases
