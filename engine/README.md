# TrueNorth Decision Engine

The judgment core of TrueNorth, made runnable. Give it a decision a team is about to
make; it returns a governed recommendation on the canonical scale —
**Endorse / Endorse-with-conditions / Caution / Oppose** — with cited evidence,
calibrated confidence, and an always-attached minority report.

This is **increment 1**: the Python engine for the first decision type, **release
go/no-go**, with real GitHub evidence. Later increments add the web UI, auth, the
immutable audit store, Docker/Helm, and the eval harness.

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
python -m venv .venv && . .venv/Scripts/activate   # Windows; use bin/activate on macOS/Linux
pip install -e ".[dev]"
cp .env.example .env        # then fill in ANTHROPIC_API_KEY (and GITHUB_TOKEN for real evidence)
```

## Run

CLI:

```bash
truenorth "Should we ship release 2.4 tonight?" --repo owner/name
```

API:

```bash
uvicorn truenorth_engine.api:app --reload
# POST http://127.0.0.1:8000/v1/decisions
#   {"decision_type":"release_go_no_go","question":"Ship 2.4 tonight?","repo":"owner/name"}
```

## Test

```bash
pytest          # schema + routing tests (no API key needed)
ruff check .    # lint
```

The schema/routing tests run offline; the end-to-end judgment run needs `ANTHROPIC_API_KEY`
and is exercised via the CLI or the API endpoint.

## Layout

```
truenorth_engine/
  schemas.py        canonical L4 data model (verdict scale, stakes tiers, decision record)
  config.py         settings + stakes->model routing (PL-1)
  model_gateway.py  Anthropic Messages API wrapper: structured outputs + prompt caching
  lenses.py         multi-lens evaluation (DI-3)
  pipeline.py       the orchestration loop (DI engine)
  evidence/github.py  release go/no-go evidence connector (DF-1)
  api.py            FastAPI surface (SX-5)
  cli.py            terminal entrypoint
```

See [../docs/features/decision-and-simulation.md](../docs/features/decision-and-simulation.md)
for the full feature specification this implements.
