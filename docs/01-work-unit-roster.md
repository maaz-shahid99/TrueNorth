# TrueNorth — Work-Unit Roster

27 work units produce the TrueNorth plan. Units U1–U26 are authored in parallel by independent workers; U27 (master plan) is written last and is the only document allowed to link other documents by filename. When citing another unit in a "Dependencies & references" table, use its unit name below — never its filename or assumed contents.

| # | Unit name | Persona | Owns | File(s) under docs/ |
|---|-----------|---------|------|---------------------|
| U1 | Architecture C4 L1+L2 | Chief software architect | System context + containers | architecture/L1-system-context.md, architecture/L2-containers.md |
| U2 | Architecture C4 L3 | Chief software architect | Components of core containers | architecture/L3-components.md |
| U3 | Architecture C4 L4 | Principal data architect | ER schemas, API surface, hero sequences | architecture/L4-data-and-apis.md |
| U4 | Catalog DF+KG | Principal PM, data platform | DF-1…7, KG-1…6 (L3+) | features/data-and-knowledge.md |
| U5 | Catalog MI+GA | Principal PM, productivity | MI-1…6, GA-1…6 (L3+) | features/meetings-and-alignment.md |
| U6 | Catalog DI+SF | Principal PM, decision science | DI-1…8, SF-1…6 (L3+) | features/decision-and-simulation.md |
| U7 | Catalog SX+WB-0 | Principal PM, experience | SX-1…6, WB-0 (L3+) | features/surfaces-and-workbench-framework.md |
| U8 | Catalog GV | Principal PM, AI governance | GV-1…7 (L3+) | features/governance-responsible-ai.md |
| U9 | Catalog SC | Principal PM, security | SC-1…6 (L3+) | features/security-trust.md |
| U10 | Catalog PL+AD | Principal PM, platform | PL-1…7, AD-1…5 (L3+) | features/platform-and-adoption.md |
| U11 | Perspective CEO/Board/Investors | CEO + board member + activist investor + M&A/IR lead | WB-CDV | perspectives/ceo-board-investors.md |
| U12 | Perspective CTO | CTO | no WB; cross-pillar needs | perspectives/cto.md |
| U13 | Perspective AI/ML Engineering | Head of AI + senior ML engineers | no WB; deep needs on PL/DI | perspectives/ai-ml-engineering.md |
| U14 | Perspective CIO & CDO | CIO + chief data officer | no WB; needs on DF/KG | perspectives/cio-cdo-data-platform.md |
| U15 | Perspective CISO | CISO | no WB; needs on SC/GV | perspectives/ciso-security.md |
| U16 | Perspective Legal & Compliance | GC + compliance officer + regulator/external-auditor lens | WB-LGL | perspectives/legal-compliance.md |
| U17 | Perspective CFO & Finance | CFO + FP&A lead | WB-FIN | perspectives/cfo-finance.md |
| U18 | Perspective CHRO & HR | CHRO + people analytics + works council & employee privacy lens | WB-HR | perspectives/chro-hr.md |
| U19 | Perspective COO & Operations | COO + plant manager + supply chain + procurement | WB-OPS | perspectives/coo-operations-supply-chain.md |
| U20 | Perspective CMO & GTM | CMO + sales leader + customer-success leader | WB-GTM, WB-CS | perspectives/cmo-gtm-customer.md |
| U21 | Perspective Engineering Team Leader | Eng team lead / line manager | WB-ENG | perspectives/engineering-team-leader.md |
| U22 | Perspective Senior IC | Staff engineer + senior analyst | no WB | perspectives/senior-ic.md |
| U23 | Perspective Frontline & Entry-Level | New grad + factory-floor worker + intern | no WB | perspectives/frontline-entry-level.md |
| U24 | Perspective Product & UX | CPO + head of design | no WB; journeys & principles only | perspectives/product-ux.md |
| U25 | Responsible-AI Deep Dive | Chief ethics officer | red-team scenarios, oversight org, EU AI Act mapping | delivery/responsible-ai-deep-dive.md |
| U26 | Roadmap & Delivery | VP program management | phases 0–4, build org, TCO, GTM | delivery/roadmap-and-delivery.md |
| U27 | Master Plan (wave 2) | Chief of staff | exec summary, doc map, glossary | 00-master-plan.md + ../README.md |

## Workbench ownership map (prevents duplication)

WB-FIN→U17 · WB-HR→U18 · WB-OPS→U19 · WB-GTM+WB-CS→U20 · WB-ENG→U21 · WB-LGL→U16 · WB-CDV→U11 · WB-0→U7. All other units own no workbench and state cross-pillar needs only.
