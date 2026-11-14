---
title: "PEFT v0.21.3"
navtitle: Overview
section: Standards
group: "Model formats / PEFT v0.21.3"
order: 60
summary: The Hugging Face PEFT adapter checkpoint format (adapter_config.json and LoRA tensors in adapter_model.safetensors), required from R3; nothing is required in R1.
---

# PEFT v0.21.3

**Scope** (SRS §1.4, PEFT): `adapter_config.json` and the LoRA tensors of
`adapter_model.safetensors`.
**Conformance:** mandatory from **R3**, through RI-FE-007 (LoRA adapter
directory read into adapter weights keyed by target module, rank checked
against `max_lora_rank`). RI-SEC-003 bounds "adapter configs" among the
files it covers; it applies once an adapter is read.

**Implementation:** none on origin/main `ccf02b3`. No crate reads
`adapter_config.json` or adapter tensors. The artifact reader's tests use a
`lora_slots` section name as test data
(`crates/rustinfer-artifact/src/reader.rs:312-364`); that is not an adapter
reader.

**Source:** Hugging Face PEFT at tag **v0.21.3**, "PEFT checkpoint format",
https://github.com/huggingface/peft/blob/v0.21.3/docs/source/developer_guides/checkpoint.md,
and the LoRA configuration `src/peft/tuners/lora/config.py` at the same tag.
The tensor container is safetensors (see the safetensors standard). Local
copies: `specs/model-formats/peft-v0.21.3-checkpoint.md`,
`specs/model-formats/peft-v0.21.3-lora-config.py`.

| | |
|---|---|
| Pages | [requirements](std-peft-requirements.html) · [audit](std-peft-audit.html) · [tracker](std-peft-tracker.html) |
| Audited | 2026-11-13, by searching origin/main for adapter code (none) |
| R1, R2 | nothing required |
| R3 | adapter reading: not started |
