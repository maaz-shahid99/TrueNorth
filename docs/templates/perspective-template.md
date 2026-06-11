# Perspective document template

Replace every guidance line (in *italics*) with real content. Keep all twelve sections, in this order, with these exact heading names. Target 3,000–5,000 words (the CEO/Board/Investors document may run to 1.5×).

---

# [Role] perspective

## 1. Front matter

| Field | Value |
|---|---|
| Doc ID | PERS-[ROLE] |
| Role | *e.g., Chief Financial Officer* |
| Owning unit | *e.g., U17 Perspective CFO & Finance* |
| Pillars referenced | *canonical L1/L2 IDs only* |
| Version | 1.0 |

## 2. Role & mandate

*Who I am, what I am accountable for, and what success looks like in 3 years if TrueNorth works.*

## 3. Decisions I face today

*First person. Table: decision, cadence, stakes (S1–S4), current pain.*

| Decision | Cadence | Stakes | Current pain |
|---|---|---|---|

## 4. Jobs-to-be-done

*Numbered JTBD-1…n, each one sentence in the form "When [situation], I want [capability], so I can [outcome]." Ranked by importance.*

## 5. A day with TrueNorth

*First-person narrative of a realistic working day/quarter with the product, followed by Mermaid diagram #1: a `sequenceDiagram` of one concrete decision flow involving this role and TrueNorth.*

## 6. Feature requirements I own

*Full L3/L4 feature tree under the WB-* code(s) this unit owns, per the shared specification's level definitions and ID rules. Include Mermaid diagram #2: a `flowchart` capability map of the workbench. Units owning no workbench instead diagram their top cross-pillar dependency chain and state "No owned workbench" here.*

## 7. Cross-pillar needs

*Table: one-sentence need → canonical L2 ID it depends on. No specs, no minted foreign IDs.*

| Need | Depends on |
|---|---|

## 8. Red lines & veto conditions

*What would make me veto, distrust, or shut off this system. Be specific and opinionated.*

## 9. Adoption & workflow integration

*What I would actually change in my week; what I would ignore; what must never be required of me.*

## 10. Success metrics & value model

*KPIs I would measure TrueNorth by, leading indicators, and payback logic.*

## 11. Hard questions for the build team

*Numbered HQ-1…n. The uncomfortable questions.*

## 12. Dependencies & references

*Table of canonical pillar/L2 IDs and work-unit names only — no filenames.*

| Reference | Type | Why |
|---|---|---|
