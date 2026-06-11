# Architecture document template

Replace every guidance line (in *italics*) with real content. Keep all nine sections, in this order, with these exact heading names. Diagrams are Mermaid `flowchart` emulating C4 notation (the L4 document may also use `erDiagram` and `sequenceDiagram`).

---

# TrueNorth architecture — [C4 level]

## 1. Front matter

| Field | Value |
|---|---|
| Doc ID | ARCH-L[n] |
| C4 level | *1 System context / 2 Containers / 3 Components / 4 Code & data* |
| Owning unit | *e.g., U1 Architecture C4 L1+L2* |
| Version | 1.0 |

## 2. Scope & imported assumptions

*What this level covers and stops at. Restate (verbatim, unchanged) the canonical assumptions block from the shared specification that this design imports.*

## 3. Diagrams

*Mermaid flowcharts emulating C4 for this level. One short paragraph per diagram element explaining its responsibility. Max 25 nodes per diagram; split rather than crowd.*

## 4. Element catalog

*Table: ID, name, responsibility, pillar/L2 mapping, technology class (vendor-neutral, e.g., "graph database", "stream processor", "LLM gateway").*

| ID | Name | Responsibility | Pillar mapping | Technology class |
|---|---|---|---|---|

## 5. Interfaces & contracts

*Only the L4 document defines schemas and API shapes; L1–L3 documents name interfaces and their purpose only.*

## 6. Quality attributes

*How this design meets the NFR expectations implied by the shared specification (multi-deployment, residency, auditability, stakes-tiered HITL, scale).*

## 7. Architecture decisions

*ADR-style table: decision, alternatives considered, rationale.*

| # | Decision | Alternatives | Rationale |
|---|---|---|---|

## 8. Risks & open questions

*Technical risks at this level; any new global assumption required goes here, not asserted.*

## 9. Dependencies & references

*Table of canonical pillar/L2 IDs and work-unit names only — no filenames.*

| Reference | Type | Why |
|---|---|---|
