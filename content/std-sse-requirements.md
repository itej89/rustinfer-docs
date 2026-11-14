---
title: "Server-sent events (WHATWG 2026-11-13) requirements"
navtitle: Requirements
section: Standards
group: "Serving / Server-sent events (WHATWG 2026-11-13)"
order: 31
summary: What the text/event-stream format requires of a server that streams completions.
---

# Server-sent events (WHATWG 2026-11-13) requirements

Source: `specs/serving/sse.html`, WHATWG HTML Living Standard §9.2, last
updated 13 November 2026. Section numbers are those of that snapshot. The
standard is written mostly for user agents; the items below are the format
rules a server must meet for a conforming client to read its stream.

| id | requirement | source |
|---|---|---|
| SSE-R1 | "This event stream format's MIME type is `text/event-stream`." | §9.2.5 |
| SSE-R2 | The client fails the connection "if res's status is not 200, or if res's `Content-Type` is not `text/event-stream`". A stream is therefore sent only with 200 and that type; an error found before streaming starts is a normal non-200 response. | §9.2.2 (the `EventSource` constructor steps) |
| SSE-R3 | The stream follows the ABNF: `stream = [ bom ] *event`; `event = *( comment / field ) end-of-line`; `comment = colon *any-char end-of-line`; `field = 1*name-char [ colon [ space ] *any-char ] end-of-line`; `end-of-line = ( cr lf / cr / lf )`. | §9.2.5 |
| SSE-R4 | "Event streams in this format must always be encoded as UTF-8." | §9.2.5 |
| SSE-R5 | "Lines must be separated by either a ... (CRLF) character pair, a single ... (LF) character, or a single ... (CR) character." A field value cannot contain CR or LF (`any-char` excludes them), so a payload with a line break must be split over several `data` lines, which the reader joins with LF. | §9.2.5, §9.2.6 |
| SSE-R6 | An event is dispatched only at a blank line: "If the line is empty (a blank line) Dispatch the event". "If the file ends in the middle of an event, before the final empty line, the incomplete event is not dispatched." Every event must end with an empty line. | §9.2.6 |
| SSE-R7 | Field names are compared literally: `event`, `data`, `id`, `retry`; others are ignored. One space after the colon is stripped. A `data` field appends its value and LF to the data buffer; an event with an empty data buffer is not dispatched. | §9.2.6 |
| SSE-R8 | A line starting with a colon is a comment and is ignored. Authors "can include a comment line (one starting with a ':' character) every 15 seconds or so" to keep proxies from dropping idle connections; and "HTTP chunking can have unexpected negative effects on the reliability of this protocol" if a layer unaware of timing buffers it. | §9.2.6, §9.2.7 (authoring notes, not mandatory) |

Out of scope: the `EventSource` interface, reconnection and `retry`
handling, `Last-Event-ID` (§9.2.4), and connectionless push (§9.2.8). A
completion stream cannot be resumed, so rustinfer has no use for `id` or
`retry`.
