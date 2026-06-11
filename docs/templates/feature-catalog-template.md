# Feature-catalog document template

Replace every guidance line (in *italics*) with real content. Keep all eight sections, in this order, with these exact heading names. Target 3,000–5,000 words **per pillar** covered by the document. This is the "extreme minute detail" layer of the plan: L3 coverage must be complete per L2; cut L4 detail before cutting L3 coverage.

---

# [Pillar(s)] feature catalog

## 1. Front matter

| Field | Value |
|---|---|
| Doc ID | CAT-[CODES] |
| Pillars covered | *e.g., DI, SF* |
| Owning unit | *e.g., U6 Catalog DI+SF* |
| Version | 1.0 |

## 2. Pillar overview & scope boundary

*One paragraph per pillar on purpose and value. Then an explicit "NOT in this pillar" list, each line pointing to the canonical L2 ID where that concern actually lives.*

## 3. L2 index & capability map

*Table of the pillar's canonical L2 groups (from the shared specification, unchanged). Then one Mermaid `flowchart` capability map per pillar.*

## 4. Feature trees (per L2 group)

*For each canonical L2 group, in order:*

### [L2 ID] [L2 name]

*Scope restatement (one sentence, consistent with the shared specification).*

#### [L3 ID] [Feature name]

- **User story:** *As a [role], I want [function], so that [outcome].*
- **Description:** *What it does and why it matters.*

##### [L4 ID] [Sub-feature name]

- **Behavior:** *…*
- **Data touched:** *…*
- **Model/AI involvement:** *none / extractive / generative / judge / simulation — with one line of detail*
- **UX surface:** *cite canonical SX L2 IDs*
- **Acceptance criteria:** *testable bullets*
- **L5 notes (where warranted):** *NFRs, edge cases, failure modes, SLOs*

*Close section 4 with one Mermaid `sequenceDiagram` of the pillar's single most important end-to-end flow (one per pillar).*

## 5. Cross-pillar dependencies

*Two tables: canonical L2 IDs this pillar CONSUMES, and what this pillar PROVIDES that other pillars cite.*

## 6. Pillar-level NFRs

*Availability, latency, scale, accuracy/calibration targets, cost envelopes — quantified, assumptions marked.*

## 7. Open questions

*Including any new global assumption your reasoning required (do not assert it elsewhere).*

## 8. Dependencies & references

*Table of canonical pillar/L2 IDs and work-unit names only — no filenames.*

| Reference | Type | Why |
|---|---|---|
