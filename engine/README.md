# TrueNorth Decision Engine

The judgment core of TrueNorth, made runnable. Give it a decision a team is about to
make; it returns a governed recommendation on the canonical scale —
**Endorse / Endorse-with-conditions / Caution / Oppose** — with cited evidence,
calibrated confidence, and an always-attached minority report.

Built in phases. Done so far:

- **Phase 1** — judgment core for the first decision type, **release go/no-go**, with
  real GitHub evidence.
- **Phase 2** — **immutable audit store (GV-3)**: every evaluated decision is persisted
  to an append-only, SHA-256 hash-chained ledger, with outcome tracking (DI-8) and a
  chain-verification endpoint. SQLite by default; Postgres for deployment.
- **Phase 3** — **eval harness (PL-4)**: a golden decision set plus a deterministic
  grader that scores the engine's judgments against expectation bands (acceptable
  verdict set, lenses that must engage, confidence ceilings on thin evidence). Runs
  offline with a scripted gateway (CI gate) or live against the model.

Later phases add auth + multi-tenancy (SC-1), observability (PL-6), a second decision
type, and Docker/Helm packaging. The web UI is built separately against this API.

## How it works

A code-orchestrated workflow (not an open-ended agent — every step is a discrete,
auditable call to the Anthropic Messages API):

```
intake + stakes classification (DI-1)   ->  fast model (Haiku)
evidence gathering (DI-2, GitHub)        ->  no model
multi-lens evaluation (DI-3)             ->  one structured call per applicable lens
devil's advocate + bias scan (DI-5)      ->  one structured call
verdict synthesis (DI-4)                 ->  one structured call (adaptive thinking on high stakes)
decision record (GV-3 audit artifact)    ->  returned to caller
```

Models are routed by stakes tier (PL-1): S4→Haiku 4.5, S3→Sonnet 4.6, S1/S2→Opus 4.8.
The verdict shape is enforced with Anthropic **structured outputs**, so the model must
return exactly the `Recommendation` schema — no fragile parsing.

## Setup

```bash
cd engine
conda create -n truenorth python=3.12 -y
conda run -n truenorth pip install -e ".[dev]"     # add ".[dev,postgres]" to use Postgres
cp .env.example .env        # then fill in ANTHROPIC_API_KEY (and GITHUB_TOKEN for real evidence)
```

By default the audit ledger is a local SQLite file (`truenorth.db`). For a real
deployment, set `DATABASE_URL=postgresql+psycopg://user:pass@host:5432/truenorth`.

## Run

CLI:

```bash
truenorth "Should we ship release 2.4 tonight?" --repo owner/name
```

API:

```bash
uvicorn truenorth_engine.api:app --reload
# POST   /v1/decisions                  judge a decision (persisted to the ledger)
#        {"decision_type":"release_go_no_go","question":"Ship 2.4 tonight?","repo":"owner/name"}
# GET    /v1/decisions                  list recorded decisions (newest first)
# GET    /v1/decisions/{id}             fetch one recorded decision
# POST   /v1/decisions/{id}/outcomes    record what actually happened (DI-8)
# GET    /v1/decisions/{id}/outcomes    list recorded outcomes
# GET    /v1/audit/verify               verify the audit hash chain (GV-3)
```

## Test

```bash
pytest                    # schema + store + eval tests (no API key needed)
ruff check .              # lint
truenorth-eval --dry-run  # golden-set eval harness, offline (scripted gateway)
truenorth-eval            # golden-set eval against the live model (needs ANTHROPIC_API_KEY)
```

The schema/store/eval tests run offline; the end-to-end judgment run needs
`ANTHROPIC_API_KEY` and is exercised via the CLI, the API endpoint, or a live
`truenorth-eval`.

## Layout

```
truenorth_engine/
  schemas.py        canonical L4 data model (verdict scale, stakes tiers, decision record)
  config.py         settings + stakes->model routing (PL-1)
  model_gateway.py  Anthropic Messages API wrapper: structured outputs + prompt caching
  lenses.py         multi-lens evaluation (DI-3)
  pipeline.py       the orchestration loop (DI engine)
  evidence/github.py  release go/no-go evidence connector (DF-1)
  store/            immutable, hash-chained audit ledger (GV-3) + outcome log (DI-8)
  eval/             golden decision set + deterministic grader + runner (PL-4)
  api.py            FastAPI surface (SX-5)
  cli.py            terminal entrypoint
```

See [../docs/features/decision-and-simulation.md](../docs/features/decision-and-simulation.md)
for the full feature specification this implements.
