# TrueNorth — System Overview

TrueNorth is an enterprise **Decision-Intelligence OS**: software that takes a proposed
decision, evaluates it from multiple independent angles against evidence, strategy,
precedent and risk, and returns a structured, auditable recommendation — while a human
always keeps the final say. This document describes what is **actually built** today (the
engine and the web app), how it fits together, and how to run it.

> For the broader product vision (12 pillars across data, knowledge graph, meetings,
> simulation, governance, etc.), see the planning docs under [`docs/`](docs/). This file
> covers the implemented system.

---

## 1. What it does, in one pass

A user submits a decision (e.g. *"Ship release 2.4 tonight?"*). The engine:

1. **Classifies the stakes** (S1 existential → S4 routine).
2. **Gathers evidence** for that decision type from a connector (GitHub, Jira, or
   manually-entered facts), with source citations.
3. **Surfaces precedent** — similar past decisions and how they turned out.
4. **Pulls active goals** and judges **strategic alignment**.
5. Runs several **independent lenses** (financial, risk, customer, legal, …), each a
   separate judgment.
6. Runs a **devil's advocate** that argues the decision is a mistake and flags biases.
7. For high-stakes decisions, projects **what-if scenarios** (forecast).
8. **Synthesizes** one verdict — **Endorse / Endorse-with-conditions / Caution / Oppose** —
   with confidence, conditions, and a mandatory **minority report**.
9. Writes the whole thing to a **hash-chained audit ledger** and, if stakes warrant, puts
   it into a **pending human review** gate.

Later, a human records the **outcome**, which feeds a **calibration/learning loop** that
measures how well verdicts and confidence actually predicted reality.

Decisions can also be **extracted from meeting transcripts** (paste a transcript → candidate
decisions → send each to judgment).

---

## 2. Repository layout

```
TrueNorth/
  engine/                      # Python decision engine (FastAPI + Anthropic)
    truenorth_engine/
      api.py                   # FastAPI app — all HTTP endpoints
      pipeline.py              # the fixed, auditable decision workflow
      lenses.py                # multi-lens evaluation (DI-3) + per-type lens packs
      model_gateway.py         # Anthropic client: routing, retries, structured output
      config.py                # env-driven settings (Pydantic Settings)
      schemas.py               # the canonical data model (Pydantic) — the L4 schema
      review.py                # stakes-tiered human sign-off (DI-7 / GV-2)
      telemetry.py             # per-call token/cost/latency capture (PL-6)
      precedent.py             # institutional memory / precedent ranking (KG / DI-2)
      calibration.py           # learning loop: outcomes vs verdicts/confidence (DI-8)
      meetings.py              # transcript -> decision extraction (MI-2)
      auth/                    # API keys, RBAC, JWT/Google SSO, rate limiting
      evidence/                # connector abstraction + GitHub/Jira/manual connectors
      goals/                   # goal-source abstraction + Jira goal connector
      store/                   # SQLAlchemy + append-only hash-chained ledger
      eval/                    # golden set + deterministic grader + scripted gateway
    tests/                     # ~84 offline tests + 2 opt-in live tests
    migrations/                # Alembic
    Dockerfile, pyproject.toml, .env.example
  web/                         # Next.js 15 web app (App Router, React 19, TS, Tailwind)
    app/(app)/                 # authenticated pages
    app/(auth)/login           # dev login + Google SSO
    app/api/                   # BFF route handlers (proxy to the engine)
    components/                # ui / layout / decision / charts / strategy / meeting / …
    lib/                       # engine client, auth, data access, types, fixtures
    e2e/                       # Playwright smoke
  docs/                        # product/architecture planning docs (the vision)
  .github/workflows/ci.yml     # engine + web + e2e CI
```

---

## 3. Architecture

Three layers, with the engine credential never exposed to the browser:

```
Browser ──► Next.js BFF (app/api/*) ──► Engine API (/v1/*) ──► Anthropic
            (attaches credential          (auth, tenancy,        (judgment)
             server-side)                  pipeline, ledger)
```

- **Engine** (`engine/`): a stateless FastAPI service over a SQL store. All judgment logic
  lives here. Auth is per-request (API key or SSO JWT); every read/write is tenant-scoped.
- **Web** (`web/`): a Next.js app. The browser calls **BFF route handlers** under
  `app/api/*`, which attach the engine credential server-side and proxy to `ENGINE_URL`.
  This is the seam that carries either a shared dev API key or a per-user SSO JWT.
- **Demo/offline mode**: when no engine credential is configured, both `lib/data.ts` and the
  BFF routes fall back to **bundled fixtures** (`lib/mock.ts`), so the entire UI is fully
  demoable with no engine and no API key.

---

## 4. The decision pipeline (`pipeline.py`)

Deliberately **not** an open-ended agent — a fixed, logged sequence so every decision is
reproducible and auditable:

```
intake / stakes (DI-1)
   └─ evidence (DI-2, connectors)
        └─ precedent (KG / DI-2, similar past decisions + outcomes)
             └─ goal alignment (GA-4, if goals exist)
                  └─ lenses (DI-3, N independent domain judges)
                       └─ devil's advocate (DI-5, red-team + bias flags)
                            └─ scenario forecast (SF, high-stakes only)
                                 └─ synthesis (DI-4, one verdict + minority report)
                                      └─ decision record (GV-3 audit artifact)
                                           └─ review gate (DI-7 / GV-2)
```

Key properties:
- **Stakes-tiered model routing**: S1/S2 → Opus (with adaptive thinking on synthesis),
  S3 → Sonnet, S4 → Haiku (`config.py`).
- **Steps that need no model are skipped cheaply**: precedent and calibration are pure;
  alignment runs only when goals exist; forecast runs only for S1/S2. This keeps the
  offline **golden eval unchanged** (fresh store → no precedent/alignment/forecast blocks).
- Every model call goes through `model_gateway.py`, which records token/cost/latency
  telemetry and returns a validated Pydantic object (structured output).

---

## 5. Decision types & connectors (`evidence/`)

A **connector** turns a decision request into a cited evidence pack. The registry dispatches
by `decision_type`; adding a type = add a connector + a lens pack, no pipeline change.

| Decision type | Connector | Evidence | Lens pack |
|---|---|---|---|
| `release_go_no_go` | **GitHub** (live) | open bugs, CI pass rate, open PRs | risk · customer · strategic · people |
| `discount_approval` | Manual deal facts | discount %, margin, tier, term … | finance · strategy · customer · legal |
| `hiring_approval` | Manual hiring facts | role, level, comp, headcount plan … | people · finance · strategy · legal |
| `vendor_procurement` | Manual procurement facts | cost, term, data access, security … | finance · risk · legal · strategy |
| `budget_spend` | Manual budget facts | amount, line, remaining, return … | finance · strategy · risk |
| `project_go_no_go` | **Jira** (live) → manual brief fallback | open issues, WIP, blockers | strategy · risk · finance · customer |

Live connectors (GitHub, Jira) **degrade gracefully** to "unavailable" or to manually-entered
facts when not configured, rather than inventing numbers.

---

## 6. Data model (`schemas.py`)

The canonical Pydantic models (snake_case JSON over the wire). The core record:

- **`DecisionRequest`** — `decision_type`, `question`, `options`, `context`, `stakes?`,
  `repo?`, `inputs{}`.
- **`DecisionRecord`** (the audit artifact) — request, `stakes`, `model_used`, `evidence`,
  `lenses[]`, `devils_advocate`, `recommendation`, `review_required/state`, `precedents[]`,
  `alignment?`, `forecast?`, `usage`, `created_at`, `engine_version`, stable `id`.
- **`Recommendation`** — `verdict` (the 4-value scale), `reasoning`, `confidence` (0–1),
  `conditions[]`, `minority_report` (always required).
- **`LensAssessment` / `ScoredLens`**, **`DevilsAdvocate`**, **`EvidenceItem` / `EvidencePack`**.
- **`Precedent`**, **`Goal` / `GoalAlignment` / `GoalLink`**, **`Scenario` / `ScenarioForecast`**,
  **`ExtractedDecision` / `MeetingExtraction`**, **`Outcome`**, **`CalibrationReport`**,
  **`ReviewAction` / `ReviewStatus`**, **`ChainVerification`**, **`ApiKeyInfo`**.

Fixed scales (immutable canon): **Verdict** = Endorse / Endorse-with-conditions / Caution /
Oppose; **Stakes** = S1 (existential) → S4 (routine); **Review** = not_required / pending /
approved / rejected.

---

## 7. API surface (`api.py`)

All endpoints except `/healthz` require a credential and are RBAC-gated and tenant-scoped.

| Method & path | Permission | Purpose |
|---|---|---|
| `GET /healthz` | public | liveness |
| `POST /v1/auth/google` | public | verify Google ID token → mint TrueNorth JWT |
| `POST /v1/decisions` | `decision:create` | judge + persist (rate-limited) |
| `GET /v1/decisions` | `decision:list` | list (limit/offset) |
| `GET /v1/decisions/{id}` | `decision:read` | fetch one |
| `POST /v1/decisions/{id}/outcomes` | `outcome:write` | record what happened (DI-8) |
| `GET /v1/decisions/{id}/outcomes` | `decision:read` | list outcomes |
| `POST /v1/decisions/{id}/review` | `review:act` | approve / reject |
| `GET /v1/decisions/{id}/review` | `decision:read` | review state + history |
| `GET /v1/audit/verify` | `audit:verify` | verify the hash chain |
| `GET/POST /v1/keys`, `DELETE /v1/keys/{id}` | `admin` | API-key management |
| `GET /v1/goals` | `decision:list` | list active goals |
| `POST /v1/goals`, `DELETE /v1/goals/{id}` | `admin` | create / archive goals |
| `GET /v1/policies` | `decision:list` | list decision-rights policies |
| `POST /v1/policies`, `DELETE /v1/policies/{id}` | `admin` | create / archive policies |
| `POST /v1/meetings/extract` | `decision:create` | transcript → candidate decisions |
| `GET /v1/calibration` | `decision:list` | verdict/confidence vs realized outcomes |
| `GET /v1/value` | `decision:list` | realized value vs. engine spend (ROI) |

---

## 8. Auth, tenancy & security (`auth/`)

- **Credentials**: `Authorization: Bearer <token>` or `X-API-Key`. The resolver tries a
  TrueNorth **JWT** (Google SSO) first, then the **API-key store** (SHA-256 hashed; plaintext
  shown once at mint).
- **RBAC**: roles **viewer / requester / reviewer / admin** bundle atomic permissions
  (`decision:create/read/list`, `outcome:write`, `review:act`, `audit:verify`, `admin`).
- **Multi-tenancy**: every `Principal` carries a `tenant_id`; all store reads/writes are
  scoped to it (hard isolation between tenants).
- **Google SSO**: engine verifies the Google ID token and mints an HS256 JWT (tenant = email
  domain; admins via an allowlist). Web runs a dependency-free OAuth code flow → exchanges
  with the engine → stores the engine JWT in a session cookie. Inert until credentials set.
- **Rate limiting**: an in-process per-principal fixed-window limiter on `POST /v1/decisions`
  → `429` + `Retry-After` (configurable, default 60/min).

---

## 9. Audit ledger & integrity (`store/`)

- A single **append-only** table; no update/delete. Decisions, outcomes, reviews, and goals
  are all appended as entries.
- Each entry is **hash-chained** (SHA-256 over prev-hash + tenant + type + id + canonical
  payload + timestamp). `GET /v1/audit/verify` recomputes the chain from genesis and reports
  any tampering (insertion, deletion, reorder, edit).
- SQLite by default (zero infra); set `DATABASE_URL` to Postgres for deployment. Alembic
  migrations run on container start.

---

## 10. Distinctive capabilities

- **Institutional memory / precedent** (`precedent.py`): lexical ranking (token overlap +
  same-type bonus) over the tenant's past decisions; the top matches (with their recorded
  outcomes) are shown to synthesis and recorded on the decision.
- **Goal & strategy alignment** (`goals/`, alignment step): goals (board→dept→team) come from
  a manual store and/or a live Jira connector; a dedicated model step scores how a decision
  **advances vs. conflicts with** active goals.
- **Meeting intelligence** (`meetings.py`): one structured call extracts the decisions
  *made/proposed* in a transcript (owner, deadline, dissent). It proposes only — a human
  confirms and routes each into the judge.
- **Simulation / forecasting** (forecast step): for S1/S2 decisions, projects 2–4 scenarios
  (probability, projection, drivers) + an outlook.
- **Learning loop / calibration** (`calibration.py`): outcome coverage, success-rate by
  verdict, confidence-vs-reality buckets, and a **Brier score** — how well-calibrated the
  engine actually is.
- **Cost & observability** (`telemetry.py`): per-call tokens, cache hits, latency, and
  estimated USD cost, aggregated onto each decision.

---

## 11. Web app (`web/`)

Next.js 15 (App Router, React 19), Tailwind reproducing the **SnowUI** look; charts via
Recharts; icons via lucide.

**Pages**: Get started · Dashboard · New decision (stepper) · **From meeting** · Decisions
history (paginated) · Decision detail (the signature verdict screen) · Reviews queue ·
**Policies** · Audit (verify-chain) · Analytics (+ value & calibration) · **Goals** ·
Settings → Members/API keys · Settings → Connectors · Login.

**Decision detail** renders: verdict banner + confidence, minority report, alignment panel,
scenario forecast, conditions, lens cards, devil's-advocate panel, evidence list, precedent
panel, review controls, outcome recorder, and a cost/usage strip.

---

## 12. Build history (phases)

**Backend 1–7**: judgment core; hash-chained audit + outcomes; eval harness; auth + RBAC +
tenancy + review gates; observability + cost; connector abstraction + discount type;
packaging (Docker/Alembic).

**UI 1–7**: design system + shell + dev login; Decision Detail; new-decision stepper +
history + outcomes; dashboard + charts; reviews + audit; Google SSO; analytics + settings +
key management.

**Roadmap 8–14** (this arc):
- **8** — hardened live model path (typed errors, retry/backoff/timeout). *Live verification
  pending an `ANTHROPIC_API_KEY` run.*
- **9** — 4 new decision types + reusable manual connector + real Jira connector.
- **10a** — per-principal rate limiting, end-to-end pagination, Vitest + Testing Library,
  GitHub Actions CI.
- **10b** — Playwright e2e smoke + CI job. *Deploy + OpenTelemetry export parked (need a host).*
- **11** — institutional memory / precedent.
- **12** — goal & strategy alignment.
- **13** — meeting intelligence (transcript → decision extraction).
- **14** — learning loop / calibration (14a) + scenario forecasting (14b).
- **15** — governance & security depth: decision-rights **policy engine** + richer review
  gates (15a); **prompt-injection screening** of inputs/evidence + a compliance mapping
  (`engine/COMPLIANCE.md`) (15b).
- **16** — adoption & value: decision-ROI / **value-realization** analytics (16a); an
  onboarding banner + **Get started** page (16b).

The roadmap (8–16) is complete. Remaining work is operational, not feature-gated: the live
model run (Phase 8 verification) and deployment + OpenTelemetry export (rest of 10b).

---

## 13. Testing & CI

- **Engine**: ~84 offline tests (`pytest`) + `ruff`; 2 opt-in live tests that self-skip
  unless `TRUENORTH_LIVE_TESTS=1` and `ANTHROPIC_API_KEY` are set. The **golden set** +
  deterministic grader is the regression oracle for judgment quality.
- **Web**: `tsc --noEmit`, ESLint, **Vitest** (lib + component tests), and a **Playwright**
  e2e smoke (login → submit → verdict) that runs in demo mode.
- **CI** (`.github/workflows/ci.yml`): an engine job (ruff + pytest), a web job
  (typecheck + lint + vitest), and an e2e job (Playwright) on push to `main` and PRs.

---

## 14. Running locally

**Engine** (use the conda env `truenorth`):

```bash
cd engine
conda run -n truenorth pip install -e ".[dev]"
# offline checks
conda run -n truenorth ruff check truenorth_engine tests
conda run -n truenorth pytest -q
conda run -n truenorth truenorth-eval --dry-run        # golden set, no API key
# run the API (needs ANTHROPIC_API_KEY in env/.env to actually judge)
conda run -n truenorth uvicorn truenorth_engine.api:app --port 8000
# mint a dev key for the web app
conda run -n truenorth truenorth-admin mint --subject dev --role admin
```

**Web**:

```bash
cd web
npm install
npm run dev            # http://localhost:3000  (works offline on fixtures)
npm run typecheck && npm run lint && npm test
npm run test:e2e       # Playwright smoke
```

To wire the web app to a live engine, set `ENGINE_URL` and `ENGINE_API_KEY` (the minted key)
in `web/.env.local`. Without them, the UI runs in demo mode.

---

## 15. Configuration (engine env — see `engine/.env.example`)

- `ANTHROPIC_API_KEY` — required to actually judge.
- `DATABASE_URL` — SQLite by default; Postgres for deployment.
- `GITHUB_TOKEN`, `JIRA_BASE_URL/EMAIL/TOKEN`, `JIRA_GOAL_JQL` — optional connector creds.
- `GOOGLE_CLIENT_ID`, `TRUENORTH_JWT_SECRET`, `SSO_ADMIN_EMAILS` — optional SSO.
- `TRUENORTH_MODEL_S1..S4` — per-stakes model overrides.
- `MODEL_TIMEOUT_SECONDS`, `MODEL_MAX_RETRIES`, `MODEL_RETRY_BASE_DELAY` — live-call resilience.
- `RATE_LIMIT_PER_MINUTE` — per-principal judgment rate limit (0 disables).

---

## 16. Product invariants & red lines

- **Humans always retain decision authority** — TrueNorth advises, records, and learns; it
  never executes a decision.
- **Ground every claim in supplied evidence**; lower confidence when evidence is thin.
- **Red lines**: no covert monitoring, no individual surveillance scoring, no autonomous
  people decisions.
- **Tamper-evident by construction**: the audit chain is append-only and verifiable.

---

## 17. Known gaps / pending

- The **live model path** has been hardened but not yet exercised end-to-end against the real
  API (needs an `ANTHROPIC_API_KEY` run).
- **Deployment** + **OpenTelemetry export/dashboards** (rest of Phase 10b) need a host/OTLP
  endpoint.
- Connectors beyond GitHub/Jira (CRM/HRIS/etc.) and live meeting capture are future work.
- Deeper security/compliance (**BYOK, DLP, ABAC** beyond the policy engine; SOC 2 / ISO
  certifications; formal retention/erasure) — see `engine/COMPLIANCE.md` for current status.
