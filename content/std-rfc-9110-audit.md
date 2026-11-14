---
title: "HTTP RFC 9110 and RFC 9112 audit"
navtitle: Audit
section: Standards
group: "Serving / HTTP RFC 9110 and RFC 9112"
order: 22
summary: The 2026-11-13 audit of rustinfer against the in-scope HTTP/1.1 rules; no HTTP code exists yet, which is expected before R3.
---

# HTTP RFC 9110 and RFC 9112 audit

**Audit of 2026-11-13**, against the [requirements](std-rfc-9110-requirements.html).

**Method.** Read the SRS on branch `docs/srs-standards-conformance` (v0.4.3,
open PR #50): §1.4 row RFC-9110, §3.1.4, RI-SRV-001, RI-SRV-002, RI-SRV-005.
Searched `origin/main` (`ccf02b3`) for any HTTP listener, parser or status
code (`git grep` for `http`, `hyper`, `axum`, `TcpListener`, `serve`) and read
the workspace dependencies. Open PRs #44, #48, #49, #50 do not touch serving.
No tests were run: there is no code to test.

**Finding.** There is no HTTP code and no HTTP dependency. `rustinfer serve`
returns `NotImplemented` (`crates/rustinfer-cli/src/commands.rs:97`); the
test `test_bench_and_serve_and_tune_reach_their_components`
(`crates/rustinfer-cli/tests/cli.rs:231`, `Verifies RI-CLI-001`) covers only
that refusal. Every item is **later release**: the requirements citing this
standard are all R3.

| item | requirement | result | evidence |
|---|---|---|---|
| H-R1 | octet parsing | later release (R3) | no parser |
| H-R2 | bare CR, whitespace after start-line | later release (R3) | no parser |
| H-R3 | 400 and close on bad grammar | later release (R3) | no parser |
| H-R4 | 414 for over-long target | later release (R3) | no parser |
| H-R5 | 400 on missing or repeated Host | later release (R3) | no parser |
| H-R6 | status-line form | later release (R3) | no responses |
| H-R7 | 400 on whitespace before colon | later release (R3) | no parser |
| H-R8 | request body length rules | later release (R3) | no parser |
| H-R9 | chunked request bodies | later release (R3) | no parser |
| H-R10 | no `Transfer-Encoding` to HTTP/1.0 | later release (R3) | no responses |
| H-R11 | persistence, read or close | later release (R3) | no connections |
| H-R12 | pipelined responses in order | later release (R3) | no connections |
| H-R13 | `Connection: close` | later release (R3) | no connections |
| H-R14 | GET and HEAD, 405 with `Allow`, 501 | later release (R3) | no routes |
| H-R15 | `Date`, `Content-Type`, `Content-Length` | later release (R3) | no responses |
| H-R16 | 200, 400, 404, 413, 415, 500, 503 | later release (R3) | RI-SRV-002 and RI-SRV-005 are R3 |
| H-R17 | error representations | later release (R3) | RI-SRV-005 is R3 |
| H-R18 | `Retry-After` | later release (R3) | no responses |
| H-R19 | 429 (RFC 6585) | later release (R3) | RI-SRV-005 is R3 |

**Result:** later. 0 conform, 0 partial, 0 missing, 19 later release. No
item is a gap in R1.
