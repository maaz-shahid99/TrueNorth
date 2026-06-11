# TrueNorth — Shared Specification (v1.0)

This document is the single source of truth for every author contributing to the TrueNorth plan. The canonical assumptions, pillar map, ID rules, and coherence rules below are **immutable**: do not restate them with modifications, do not extend L1/L2, and do not contradict them. If your reasoning requires a change, record it under "Open questions" in your own document instead.

## 1. Product vision

TrueNorth is an enterprise **Decision-Intelligence Operating System** deployable at any Fortune-500 company (Tesla-scale used as the mental model: manufacturing, supply chain, engineering, finance, HR, sales, legal — but industry-generic). It continuously ingests signals from every department (systems of record, meetings, documents, metrics), maintains a living organizational knowledge graph of goals, decisions, commitments, and outcomes, and — when a team proposes or makes a decision, typically after meetings — evaluates it against strategy, data, precedent, simulation, and risk, then issues a structured recommendation with reasoning, evidence citations, confidence, and a devil's-advocate minority report. It assists every level of the company, board to entry-level, in making better decisions.

## 2. Canonical assumptions (immutable)

- **Verdict scale:** Endorse / Endorse-with-conditions / Caution / Oppose
- **Stakes tiers:** S1 (existential/board-level) → S2 (executive) → S3 (departmental) → S4 (team/routine); human-in-the-loop gates scale with stakes
- **Invariant:** humans always retain decision authority; TrueNorth advises, records, and learns from outcomes
- **Deployment:** SaaS / VPC / on-prem / air-gapped; multi-tenant with hard isolation options; data residency honored
- **Red lines:** no covert monitoring, no individual surveillance scoring, no autonomous people decisions

## 3. Feature level definitions

| Level | Meaning | Granularity |
|---|---|---|
| L1 | Pillar — strategic capability area | the 12 pillars below; fixed |
| L2 | Capability group within a pillar | named groups below; fixed |
| L3 | Feature — concrete shippable function | ID + name + user story + description |
| L4 | Sub-feature spec | behavior, data touched, model/AI involvement, UX surface, acceptance criteria |
| L5 | Where warranted | NFRs, edge cases, failure modes, SLOs |

## 4. Canonical pillar map — L1 + L2 (final)

**DF — Data & Integration Fabric**
- DF-1 Connector library — prebuilt, versioned connectors (ERP/CRM/HRIS/PLM/MES/ITSM/lakehouse/M365/Google/Slack/Teams/Zoom/SharePoint/Confluence/Jira)
- DF-2 Ingestion & transformation pipelines — batch/CDC/streaming, schema mapping, document parsing
- DF-3 Data contracts & quality — SLAs, anomaly quarantine, quality scores
- DF-4 Privacy filtering & minimization — PII redaction, consent zones, purpose tags, applied pre-persistence
- DF-5 Metadata, lineage & catalog — source-field → recommendation-citation lineage
- DF-6 Residency & sovereignty routing — region pinning, cross-border transfer controls
- DF-7 External & market signal ingestion — news, regulatory, market/commodity, competitor, logistics feeds with source-reliability scoring

**KG — Organizational Knowledge Graph & Institutional Memory**
- KG-1 Ontology & schema management — Person, Team, Goal, Decision, Meeting, Project, Metric, Risk, Asset, Customer, Supplier, Policy, Contract; versioned tenant extensions
- KG-2 Graph construction & entity resolution
- KG-3 Temporal versioning & institutional memory — bitemporal as-of queries, decision genealogy, departure-resilient retention
- KG-4 Semantic retrieval layer — GraphRAG, permission-aware retrieval
- KG-5 Knowledge curation & feedback — SME validation queues, contested-fact resolution
- KG-6 Org-model awareness — reporting lines, RACI, decision rights, committees

**MI — Meeting & Communication Intelligence**
- MI-1 Capture & transcription — calendar-aware, diarization, multilingual
- MI-2 Decision & commitment extraction — decisions, action items, owners, deadlines, recorded dissent
- MI-3 Summaries & follow-through tracking
- MI-4 Pre-meeting intelligence — briefs, agenda quality, required-data checklists
- MI-5 Cross-meeting & cross-channel threading — topic genealogy
- MI-6 Consent, recording governance & privacy controls — per-jurisdiction consent, off-the-record zones, retention

**GA — Goal & Strategy Alignment**
- GA-1 Strategy & OKR graph — board→department→team→individual cascade
- GA-2 Conflict & overlap detection — contradictory goals, duplicated effort, orphan goals
- GA-3 Progress & health tracking — live metric binding, status inference
- GA-4 Alignment scoring — decisions/projects scored against the strategy graph
- GA-5 Strategy drift & review cadence
- GA-6 Initiative & bet portfolio — innovation pipeline, stage gates, kill/persevere signals

**DI — Decision Intelligence Engine (judgment core)**
- DI-1 Decision capture & structuring — records, options, criteria, assumptions, stakes S1–S4
- DI-2 Evidence & precedent assembly — citation-backed data/docs plus similar past decisions with outcomes
- DI-3 Multi-lens evaluation — financial, strategic, risk, legal, people, customer, ESG judges
- DI-4 Recommendation synthesis — verdict + reasoning + confidence + conditions + minority report
- DI-5 Devil's advocate & bias detection — red-team arguments; groupthink/sunk-cost/anchoring flags; pre-mortems
- DI-6 Uncertainty & calibration — what-would-change-my-mind, engine self-calibration
- DI-7 Review workflows & escalation — stakes-tiered HITL gates, sign-off, crisis/expedited fast path
- DI-8 Outcome tracking & learning loop

**SF — Simulation & Forecasting**
- SF-1 Forecasting library — demand, cashflow, headcount, capacity
- SF-2 Scenario & what-if modeling
- SF-3 Monte Carlo & sensitivity analysis
- SF-4 Org digital twin — cross-department impact propagation of a candidate decision
- SF-5 War-gaming & stress tests — incl. crisis simulations
- SF-6 Backtesting & forecast accuracy — realized-vs-forecast, accuracy SLAs

**WB — Department Workbenches**
- WB-0 Workbench framework — SDK, department ontology packs, KPI packs, lens packs
- WB-FIN Finance — FP&A, capital allocation, treasury, controllership
- WB-HR People — workforce planning, talent, comp; works-council-aware
- WB-OPS Operations & Supply Chain — manufacturing, quality, EHS, logistics, procurement & supplier risk
- WB-GTM Sales & Marketing — pipeline, pricing, campaigns, partner/dealer networks
- WB-ENG Engineering & Product — R&D portfolio, release decisions, tech debt
- WB-LGL Legal & Compliance — contracts, disputes, regulatory change, ESG disclosure
- WB-CS Customer Success & Support
- WB-CDV Corporate Development & IR — M&A pipeline, diligence rooms, integration tracking, board/investor narrative

**SX — Surfaces & Workflow Integration**
- SX-1 Web command centers — role-aware exec/lead/IC views
- SX-2 Conversational interface — org-aware assistant
- SX-3 In-flow plugins — Slack/Teams/Outlook/calendar
- SX-4 Mobile, frontline & notifications — deskless/factory-floor surfaces, digests, interruption budgets
- SX-5 API & extension platform — APIs, webhooks, marketplace
- SX-6 Accessibility & internationalization

**GV — Governance, Risk, Compliance & Responsible AI**
- GV-1 Policy engine — decision-rights matrix encoded
- GV-2 HITL gates & stakes-based controls
- GV-3 Audit & replay — immutable logs, reproducibility
- GV-4 Explainability & transparency
- GV-5 Regulatory compliance packs — EU AI Act, GDPR, SOX, sectoral, ESG disclosure
- GV-6 Ethics board tooling & red lines — prohibited uses incl. employee-surveillance bans
- GV-7 Model risk management

**SC — Security, Identity & Trust**
- SC-1 Identity & access — SSO/SCIM, RBAC+ABAC, decision-rights-aware authz
- SC-2 Data protection — encryption, BYOK, DLP, classification-aware retrieval
- SC-3 AI-specific security — prompt injection, retrieval poisoning, output exfiltration
- SC-4 Tenant & deployment isolation — SaaS/VPC/on-prem/air-gapped
- SC-5 Insider risk & abuse monitoring
- SC-6 Certifications — SOC 2, ISO 27001/42001, FedRAMP

**PL — Platform, AI Infrastructure & MLOps**
- PL-1 Model gateway & multi-LLM orchestration — stakes/cost routing
- PL-2 RAG & retrieval infrastructure
- PL-3 Agent orchestration framework
- PL-4 Evaluation harness — golden decision sets, judge calibration, regression evals
- PL-5 Fine-tuning & domain adaptation
- PL-6 Observability & cost management
- PL-7 Scale & reliability — multi-region, DR

**AD — Adoption, Value Realization & Analytics**
- AD-1 Onboarding & training academies
- AD-2 Change management toolkit — champions, maturity model, trust-building
- AD-3 Usage & health analytics
- AD-4 Value realization — decision ROI attribution
- AD-5 Feedback & co-design loops

## 5. Numbering & ID rules

- Only this document defines L1/L2 IDs. Authors mint IDs **only at L3 and below, only under L2s or WB codes they own**, numbered sequentially from 1: `DI-4-1` (L3), `DI-4-1-2` (L4), `WB-FIN-3-2`, etc.
- Every minted ID must match `^(DF|KG|MI|GA|DI|SF|WB(-[A-Z]{2,3})?|SX|GV|SC|PL|AD)(-\d+)+$` and be unique within its document.
- Cross-pillar needs are stated in one sentence citing the canonical L2 ID — never spec'd, never given a minted ID in a foreign pillar.
- Perspective docs may additionally number JTBD-n (jobs-to-be-done) and HQ-n (hard questions) locally.

## 6. Style & tone

Write third-person product-spec prose ("TrueNorth shall…"); first person only in "Decisions I face today" and "A day with TrueNorth" sections of perspective docs. US English, sentence-case headings, no marketing superlatives, no rhetorical questions outside "Hard questions."

## 7. Mermaid rules

Use only `flowchart TD|LR`, `sequenceDiagram`, `journey` (plus `erDiagram` for the L4 architecture document only and `gantt` for the roadmap document only). Node IDs alphanumeric; wrap every label containing spaces or punctuation in double quotes: `DI4a["Recommendation synthesis"]`. No HTML, no `<br>`, no `style`/`classDef`, max 25 nodes per diagram. One diagram per fenced block.

## 8. Cross-referencing

Never reference another planned document by filename or assume its contents (the master plan, written last, is the only exception). End every document with a "Dependencies & references" table using canonical pillar/L2 IDs and work-unit names only (see `01-work-unit-roster.md` for unit names).

## 9. Glossary seeds

- **Decision record** — the structured artifact at the heart of TrueNorth: context, options, criteria, assumptions, stakes tier, verdict, conditions, sign-offs, outcome.
- **Lens** — a domain-specific judge (financial, strategic, risk, legal, people, customer, ESG) contributing an assessment to a verdict.
- **Workbench** — a department-specific surface and feature pack built on the WB-0 framework.
- **Minority report** — the strongest argument against the issued verdict, always attached.
- **Calibration** — measured agreement between TrueNorth's confidence and realized outcomes.
