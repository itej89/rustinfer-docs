---
title: "Tokenizers v0.23.3 audit"
navtitle: Audit
section: Standards
group: "Model formats / Tokenizers v0.23.3"
order: 32
summary: The 2026-11-13 check of origin/main for tokenizer support, which R2 first requires.
---

# Tokenizers v0.23.3 audit

**Audit of 2026-11-13**, against the [requirements](std-hf-tokenizer-requirements.html),
on origin/main `ccf02b3`.

**Method.** Searched every crate on origin/main for `tokenizer`,
`tokenizer.json` and chat-template code, and for a dependency on a tokenizer
library; checked the release of each citing requirement in the SRS
(RI-CLI-006, RI-SRV-003).

| id | result | evidence |
|---|---|---|
| TOK-R1 to TOK-R5 | **later release** (R2) | No code reads `tokenizer.json`. The only mention is a test fixture that writes `{}` to show the frontend ignores other files (`crates/rustinfer-frontend/tests/lower.rs:122`). RI-CLI-006 takes token ids in R1. |
| TOK-R6 | **later release** (R3) | No chat template rendering; the server (RI-SRV) is R3. |

## Result

Nothing is required in R1 and nothing is implemented. State: **later**.
Work items on the [tracker](std-hf-tokenizer-tracker.html).
