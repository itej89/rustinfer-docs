---
title: "Tokenizers v0.23.3 tracker"
navtitle: Tracker
section: Standards
group: "Model formats / Tokenizers v0.23.3"
order: 33
summary: Work needed for tokenizer.json and chat-template conformance in R2 and R3.
---

# Tokenizers v0.23.3 tracker

From the [audit](std-hf-tokenizer-audit.html) of 2026-11-13. No GitHub
issue covers either item yet.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| TOK-1 | No `tokenizer.json` encode or decode | TOK-R1 to TOK-R5; RI-CLI-006 (R2) | **Later release R2** | Whether to depend on the `tokenizers` crate at v0.23.3 or write a reader is open; either way the file is an untrusted boundary (RI-SEC-003), to be bounded and checked, and its SHA-256 recorded in `metadata` once a build reads it (RI-SEC-004). |
| TOK-2 | No chat template rendering | TOK-R6; RI-SRV-003 (R3) | **Later release R3** | Needs a sandboxed Jinja renderer matching Transformers' environment (filters, globals, whitespace control). |
