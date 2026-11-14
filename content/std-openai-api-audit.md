---
title: "OpenAI API 2.3.0 audit"
navtitle: Audit
section: Standards
group: "Serving / OpenAI API 2.3.0"
order: 12
summary: The 2026-11-13 audit of rustinfer against the in-scope OpenAI API shapes; every item is Release 3 work and none is due yet.
---

# OpenAI API 2.3.0 audit

**Audit of 2026-11-13**, against the [requirements](std-openai-api-requirements.html).

**Method.** Read the SRS on branch `docs/srs-standards-conformance` (v0.4.3,
open PR #50): §1.4 row OPENAI-API, RI-SRV-001 to RI-SRV-005 and RI-CLI-009.
Searched `origin/main` (`ccf02b3`) for any server, route, request or
response type (`git grep` for `serve`, `chat/completions`, `axum`, `hyper`,
`http`, `RI-SRV`), read the `serve` stub and its test, and checked the
workspace dependencies in `Cargo.toml`. Open PRs #44, #48, #49 and #50 do not
touch serving. No tests were run: there is no code to test.

**Finding.** No HTTP server exists. `rustinfer serve` parses its arguments
(`crates/rustinfer-cli/src/cli.rs:89`, `ServeArgs`: `source`,
`--require-prebuilt`) and then fails with `error=not_implemented
component=runtime` (`crates/rustinfer-cli/src/commands.rs:97`). The test
`test_bench_and_serve_and_tune_reach_their_components`
(`crates/rustinfer-cli/tests/cli.rs:231`, tagged `Verifies RI-CLI-001`)
proves that failure path, not any part of this standard. RI-SRV-001 and
RI-CLI-009 are Release 3, so every item below is **later release**, which is
the expected state.

| item | requirement | result | evidence |
|---|---|---|---|
| OA-R1 | `POST /v1/chat/completions` | later release (R3) | no route; `serve` stub, `commands.rs:97` |
| OA-R2 | `POST /v1/completions` | later release (R3) | no route |
| OA-R3 | `GET /v1/models` and the `Model` object | later release (R3) | no route |
| OA-R4 | `/v1` base path | later release (R3) | no server |
| OA-R5 | `n` | later release (R3) | no request type |
| OA-R6 | `logprobs`, `top_logprobs` (chat); `logprobs` integer (completions) | later release (R3) | no request type |
| OA-R7 | `stop` | later release (R3) | no request type |
| OA-R8 | `seed` | later release (R3) | no request type |
| OA-R9 | `temperature` | later release (R3) | no request type |
| OA-R10 | `top_p` | later release (R3) | no request type |
| OA-R11 | `max_tokens` | later release (R3) | no request type |
| OA-R12 | `response_format` (where guided decoding supports it) | later release (R3) | no request type; guided decoding is open (OI-006) |
| OA-R13 | `tools` (where guided decoding supports it) | later release (R3) | no request type; OI-006 |
| OA-R14 | `stream`, `stream_options.include_usage` | later release (R3) | no streaming; see [SSE](std-sse.html) |
| OA-R15 | `chat.completion` object | later release (R3) | no response type |
| OA-R16 | `chat.completion.chunk` and the `data: [DONE]` terminator | later release (R3) | no response type |
| OA-R17 | `text_completion` object | later release (R3) | no response type |
| OA-R18 | `ErrorResponse` with 400, 429, 503 | later release (R3) | no server; RI-SRV-005 is R3 |

**Result:** later. 0 conform, 0 partial, 0 missing, 18 later release. No
item is a gap in R1.
