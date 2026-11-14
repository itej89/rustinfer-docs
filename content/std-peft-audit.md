---
title: "PEFT v0.21.3 audit"
navtitle: Audit
section: Standards
group: "Model formats / PEFT v0.21.3"
order: 62
summary: The 2026-11-13 check of origin/main for PEFT adapter support, which R3 first requires.
---

# PEFT v0.21.3 audit

**Audit of 2026-11-13**, against the [requirements](std-peft-requirements.html),
on origin/main `ccf02b3`.

**Method.** Searched every crate on origin/main for `adapter_config`,
`lora`, `peft` and `max_lora_rank`; checked the release of RI-FE-007 (R3)
and the scope of RI-SEC-003.

| id | result | evidence |
|---|---|---|
| PEFT-R1 to PEFT-R6 | **later release** (R3) | No adapter reader exists. The only LoRA text on main is a `lora_slots` section name used as test data in the artifact reader's unit tests (`crates/rustinfer-artifact/src/reader.rs:312-364`). No `max_lora_rank` field exists yet. |

## Result

Nothing is required before R3 and nothing is implemented. State: **later**.
Work item on the [tracker](std-peft-tracker.html).
