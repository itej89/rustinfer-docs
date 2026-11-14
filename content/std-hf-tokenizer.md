---
title: "Tokenizers v0.23.3"
navtitle: Overview
section: Standards
group: "Model formats / Tokenizers v0.23.3"
order: 30
summary: The Hugging Face Tokenizers tokenizer.json serialization and Transformers chat templates, required from R2 (encode and decode) and R3 (chat templates); nothing is required in R1.
---

# Tokenizers v0.23.3

**Scope** (SRS §1.4, HF-TOKENIZER): `tokenizer.json` encode and decode
(R2, RI-CLI-006), and chat templates as Transformers renders them (R3,
RI-SRV-003).
**Conformance:** mandatory from **R2**. In R1, `run` takes token ids only
(RI-CLI-006, "R1 (token ids); R2 (text through the tokenizer)"), so nothing
is required yet.

**Implementation:** none on origin/main `ccf02b3`. No crate reads
`tokenizer.json`; the frontend ignores it (a fixture writes an empty one,
`crates/rustinfer-frontend/tests/lower.rs:122`, to show other files are
ignored), and it is not part of the checkpoint identity.

**Source:** Hugging Face Tokenizers at tag **v0.23.3**,
https://github.com/huggingface/tokenizers/tree/v0.23.3:
`tokenizers/src/tokenizer/serialization.rs`, `tokenizer/mod.rs`,
`tokenizer/added_vocabulary.rs`, `models/mod.rs`,
`models/bpe/serialization.rs`; for chat templates, Transformers v5.23.0
`utils/chat_template_utils.py`. Local copies:
`specs/model-formats/tokenizers-v0.23.3-*`,
`specs/model-formats/transformers-v5.23.0-chat_template_utils.py`.

| | |
|---|---|
| Pages | [requirements](std-hf-tokenizer-requirements.html) · [audit](std-hf-tokenizer-audit.html) · [tracker](std-hf-tokenizer-tracker.html) |
| Audited | 2026-11-13, by searching origin/main for any tokenizer code (none) |
| R1 | nothing required |
| R2 | encode and decode of `tokenizer.json`: not started |
| R3 | chat templates: not started |
