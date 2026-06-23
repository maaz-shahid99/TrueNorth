# TrueNorth — Compliance control mapping

How TrueNorth's **implemented** controls map to the obligations that matter for an
AI-assisted decision system. This is an engineering reference, not legal advice; it tracks
what exists in code today and flags what is still planned.

TrueNorth is **advisory**: it never executes a decision, a human always decides, and every
judgment is recorded immutably. That posture is what most of these controls build on.

---

## EU AI Act (high-risk AI system obligations)

| Obligation | TrueNorth control | Status |
|---|---|---|
| **Human oversight** (Art. 14) | Stakes-tiered review gates (DI-7) **plus** the decision-rights policy engine (GV-1/GV-2): a reviewer must approve before a gated decision counts. Injection-flagged inputs always force review. | ✅ implemented |
| **Transparency** (Art. 13) | Every verdict ships with reasoning, per-lens rationale, cited evidence, a devil's-advocate counter-case, and a mandatory minority report. | ✅ implemented |
| **Record-keeping / logging** (Art. 12) | Append-only, SHA-256 **hash-chained** audit ledger; `GET /v1/audit/verify` proves integrity. Decisions, outcomes, reviews, goals, and policies are all logged. | ✅ implemented |
| **Accuracy & robustness** (Art. 15) | Golden-set eval + deterministic grader; per-tenant **calibration / Brier score** (DI-8) tracks whether confidence matches reality; live-call retry/backoff. | ✅ implemented |
| **Risk management** (Art. 9) | Multi-lens risk evaluation, scenario forecasting for high-stakes decisions, devil's advocate + bias flags. | ✅ implemented |
| **Cybersecurity** (Art. 15) | Prompt-injection / retrieval-poisoning screening on inputs and evidence (SC-3); auth + RBAC + tenant isolation. | ✅ implemented (BYOK/DLP planned) |
| Conformity documentation | This file + the planning docs under `docs/`. | ◑ partial |

## GDPR

| Principle | TrueNorth control | Status |
|---|---|---|
| **Data minimization / purpose limitation** | Connectors gather only the fields a decision type needs; no covert ingestion. | ✅ implemented |
| **Access control** | RBAC (viewer/requester/reviewer/admin) + per-request auth; tenant-scoped reads/writes. | ✅ implemented |
| **Tenant / data isolation** | Every store operation is scoped to the caller's `tenant_id` (hard isolation). | ✅ implemented |
| **Right to explanation** | Full, human-readable reasoning trace recorded on every decision. | ✅ implemented |
| **Consent (meeting data)** | The meeting-intelligence flow requires an explicit consent confirmation (MI-6) before a transcript is processed. | ✅ implemented (UI gate) |
| Erasure / retention schedules | Append-only ledger keeps history; formal retention/erasure workflows. | ◯ planned |

## SOX (financial-decision controls)

| Control | TrueNorth control | Status |
|---|---|---|
| **Audit trail** | Tamper-evident hash chain; nothing is updated or deleted, only appended. | ✅ implemented |
| **Segregation of duties** | A requester cannot approve their own decision; review requires the `reviewer`/`admin` role per policy. | ✅ implemented |
| **Authorization thresholds** | Decision-rights policies gate by stakes, decision type, verdict, goal conflict, or model spend (e.g. "spend ≥ $X requires admin sign-off"). | ✅ implemented |
| **Reproducibility** | The decision record captures every input and output the judge used. | ✅ implemented |

---

## Security posture (SC)

- **Identity & access**: API keys (SHA-256 hashed) and Google SSO → engine JWT; RBAC with
  attribute-based gating via the policy engine.
- **Tenant isolation**: enforced on every query.
- **AI-specific security (SC-3)**: injection/poisoning screening flags suspicious inputs and
  forces human review rather than acting on them.
- **Rate limiting**: per-principal limit on the judgment endpoint.

## Known gaps / planned

- **BYOK / KMS-managed encryption** and **DLP / classification-aware retrieval** (SC-2).
- **Formal retention & erasure** workflows (GDPR).
- **Certifications** (SOC 2 / ISO 27001 / 42001) — process, not code.
- **Model risk management** documentation (GV-7) beyond the eval harness.
