---
title: "PEFT v0.21.3 tracker"
navtitle: Tracker
section: Standards
group: "Model formats / PEFT v0.21.3"
order: 63
summary: Work needed for PEFT adapter conformance in R3.
---

# PEFT v0.21.3 tracker

From the [audit](std-peft-audit.html) of 2026-11-13. No GitHub issue covers
it yet.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| PEFT-1 | No LoRA adapter reader | PEFT-R1 to PEFT-R6; RI-FE-007 (R3) | **Later release R3** | The adapter's tensors go through the shared safetensors reader; `adapter_config.json` is bounded and typed (RI-SEC-003). Fields that change the weights (`use_rslora`, `rank_pattern`, `alpha_pattern`, `fan_in_fan_out`, `use_dora`, `bias`, `modules_to_save`) are honoured or refused by name, never ignored. |
