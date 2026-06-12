# TrueNorth

**An AI Decision-Intelligence Operating System for the enterprise.**

TrueNorth takes input from every department of a large company, understands its current goals, watches the decisions teams make in meetings, and tells them whether following a given decision is a good idea — with reasoning, cited evidence, calibrated confidence, and the strongest argument against itself. It is built for Fortune-500 scale and deployable as SaaS, VPC, on-prem, or air-gapped.

A human always decides. TrueNorth advises on a four-point scale — **Endorse / Endorse-with-conditions / Caution / Oppose** — routes each decision through human gates sized to its stakes, records everything immutably, and learns from outcomes. It never makes autonomous people decisions and never surveils individuals.

This repository is a **planning deliverable** (documentation, not application code): a comprehensive, multi-level product and engineering plan.

## Start here

- **[Master plan](docs/00-master-plan.md)** — executive summary, the decision lifecycle, and links to every document.
- **[Shared specification](docs/00-shared-specification.md)** — the 12-pillar taxonomy, canonical assumptions, and authoring rules.
- **[Work-unit roster](docs/01-work-unit-roster.md)** — who authored what.

## Structure

```
docs/
  00-master-plan.md            Navigable overview of the whole plan
  00-shared-specification.md   Canonical pillars (L1/L2), assumptions, rules
  01-work-unit-roster.md       Work units and ownership
  templates/                   Authoring templates
  architecture/                C4 levels 1-4
  features/                    L1->L4 feature catalogs for the 12 pillars
  perspectives/                15 stakeholder perspectives, board to frontline
  delivery/                    Responsible-AI deep dive and delivery roadmap
```

## The twelve pillars

Data & Integration Fabric (DF) · Organizational Knowledge Graph (KG) · Meeting & Communication Intelligence (MI) · Goal & Strategy Alignment (GA) · Decision Intelligence Engine (DI) · Simulation & Forecasting (SF) · Department Workbenches (WB) · Surfaces & Workflow Integration (SX) · Governance, Risk, Compliance & Responsible AI (GV) · Security, Identity & Trust (SC) · Platform, AI Infrastructure & MLOps (PL) · Adoption, Value Realization & Analytics (AD).

Diagrams throughout are written in [Mermaid](https://mermaid.js.org/) and render in most Markdown viewers.
