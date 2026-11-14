---
title: "HTTP RFC 9110 and RFC 9112 tracker"
navtitle: Tracker
section: Standards
group: "Serving / HTTP RFC 9110 and RFC 9112"
order: 23
summary: The Release 3 HTTP work for rustinfer's server; no open gap, since nothing is due before R3.
---

# HTTP RFC 9110 and RFC 9112 tracker

From the [audit](std-rfc-9110-audit.html). No gap is open: every item is
Release 3 work, listed so it stays visible and not counted as a gap. No GitHub
issue covers it yet (`gh issue list -R itej89/rustinfer --state all`,
2026-11-13).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| HTTP-1 | HTTP/1.1 request parsing and framing (H-R1 to H-R9) | RFC 9112 §2.2, §3, §3.2, §5.1, §6, §7.1 | Later release R3 | Most of this comes with a mature HTTP library; the choice is a new dependency under SWG-001 §18 |
| HTTP-2 | Response framing and connections: status-line, chunked only to HTTP/1.1, persistence, pipelining order, `close` (H-R6, H-R10 to H-R13) | RFC 9112 §4, §6.1, §9.3, §9.6 | Later release R3 | Streamed responses (SSE) need chunked or close-delimited bodies |
| HTTP-3 | Methods and response headers: GET and HEAD, 405 with `Allow`, `Date`, `Content-Type`, `Content-Length` (H-R14, H-R15) | RFC 9110 §6.6.1, §8.3, §8.6, §9.1, §10.2.1 | Later release R3 | |
| HTTP-4 | Status codes of RI-SRV-002 and RI-SRV-005, with explanatory bodies and `Retry-After` (H-R16 to H-R19) | RFC 9110 §10.2.3, §15; RFC 6585 §4 | Later release R3 | Bodies in the OpenAI `ErrorResponse` shape ([OAI-5](std-openai-api-tracker.html)) |

## Notes for the SRS

- The RFC-9110 row scopes "the status codes RI-SRV-002 and RI-SRV-005 use",
  and RI-SRV-005 names 429. 429 is defined by RFC 6585 §4, not RFC 9110 or
  RFC 9112. The §1.4 row may want to add RFC 6585.
- RI-SRV-002 says `/health` returns 200 "only when the executor can admit"
  but not what it returns otherwise. 503 (RFC 9110 §15.6.4) is the usual
  choice.
- RI-SRV-005 says size limits are enforced but names no status. 413 Content
  Too Large (RFC 9110 §15.5.14) is the code for an over-size body, and 414
  (RFC 9112 §3) is mandatory for an over-long target.
