---
title: "OpenAI API 2.3.0"
navtitle: Overview
section: Standards
group: "Serving / OpenAI API 2.3.0"
order: 10
summary: The OpenAI request, response and stream-chunk shapes that rustinfer's server must accept and produce from R3, pinned to openai-openapi 2.3.0.
---

# OpenAI API 2.3.0

**Scope (SRS §1.4, OPENAI-API):** the request, response and stream-chunk
shapes of `/v1/chat/completions`, `/v1/completions` and `/v1/models`, for the
fields RI-SRV-001 lists: `n`, `logprobs`, `stop`, `seed`, `temperature`,
`top_p`, `max_tokens`, `response_format` and `tools` (the last two where
guided decoding supports them). Nothing else of the OpenAI API is claimed.

**Implementation:** none yet. The server is RI-SRV (SRS §3.2.18), started by
`rustinfer serve` (RI-CLI-009), both Release 3. On `origin/main` (`ccf02b3`)
the `serve` subcommand exists only as a stub:
`crates/rustinfer-cli/src/cli.rs:36` declares it ("Serve an OpenAI-compatible
HTTP API (RI-CLI-009)") and `crates/rustinfer-cli/src/commands.rs:97` returns
`NotImplemented { feature: "RI-CLI-009 serve" }`. No HTTP or JSON-schema code
for these endpoints exists, and the workspace has no HTTP dependency.

**Conformance:** mandatory from **R3**. The current release is R1, so nothing
is required yet.

**Source:** `specs/serving/openapi.yaml`, the OpenAI OpenAPI description
*OpenAI API* (`info.version` 2.3.0, OpenAPI 3.1.0, MIT licence) at commit
`a45d45bda635914987adad8f3b33f9f81847864a` of
<https://github.com/openai/openai-openapi>, downloaded 2026-11-13. The prose
reference is <https://platform.openai.com/docs/api-reference/chat>. The
schema has no clause numbers, so requirements cite the schema or path name
and its line in that file.

| | |
|---|---|
| Pages | [requirements](std-openai-api-requirements.html) · [audit](std-openai-api-audit.html) · [tracker](std-openai-api-tracker.html) |
| Conformance | mandatory R3 (RI-SRV-001, RI-CLI-009) |
| Audited | 2026-11-13, by reading `origin/main` `ccf02b3` and the SRS on branch `docs/srs-standards-conformance` |
| Result | later release: every item is R3 work; no R1 requirement depends on this standard |
| Open gaps | 0 (5 gaps, covering 18 requirement items, recorded as later release R3) |
