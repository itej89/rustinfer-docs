---
title: "Server-sent events (WHATWG 2026-11-13)"
navtitle: Overview
section: Standards
group: "Serving / Server-sent events (WHATWG 2026-11-13)"
order: 30
summary: The text/event-stream format of the WHATWG HTML Standard, which rustinfer's streamed completions must use from R3.
---

# Server-sent events (WHATWG 2026-11-13)

**Scope (SRS §1.4, SSE):** the `text/event-stream` format for streamed
responses. rustinfer is the server side only: it writes event streams for
`stream: true` requests on `/v1/chat/completions` and `/v1/completions`
(RI-SRV-001). The `EventSource` browser interface is out of scope, except
where its connection rules decide what a server must send.

**Implementation:** none yet. Streaming is part of RI-SRV-001, Release 3. On
`origin/main` (`ccf02b3`) `rustinfer serve` is a stub
(`crates/rustinfer-cli/src/commands.rs:97`) and nothing writes
`text/event-stream`.

**Conformance:** mandatory from **R3**. Nothing is required in R1.

**Source:** `specs/serving/sse.html` (with a text extraction
`specs/serving/sse.txt`), WHATWG, *HTML Living Standard*, §9.2 *Server-sent
events*, "Last Updated 13 November 2026",
<https://html.spec.whatwg.org/multipage/server-sent-events.html>, downloaded
2026-11-13. The SRS pins this snapshot date. The OpenAI-specific framing on
top of it (data-only events, the `data: [DONE]` terminator) is on the
[OpenAI API](std-openai-api-requirements.html) page.

| | |
|---|---|
| Pages | [requirements](std-sse-requirements.html) · [audit](std-sse-audit.html) · [tracker](std-sse-tracker.html) |
| Conformance | mandatory R3 (RI-SRV-001) |
| Audited | 2026-11-13, by reading `origin/main` `ccf02b3` and the SRS on branch `docs/srs-standards-conformance` |
| Result | later release: no streaming code exists, as expected before R3 |
| Open gaps | 0 (3 gaps, covering 8 requirement items, recorded as later release R3) |
