---
title: "Server-sent events (WHATWG 2026-11-13) tracker"
navtitle: Tracker
section: Standards
group: "Serving / Server-sent events (WHATWG 2026-11-13)"
order: 33
summary: The Release 3 streaming work; no open gap, since nothing is due before R3.
---

# Server-sent events (WHATWG 2026-11-13) tracker

From the [audit](std-sse-audit.html). No gap is open: every item is Release 3
work, listed so it stays visible and not counted as a gap. No GitHub issue
covers it yet (`gh issue list -R itej89/rustinfer --state all`, 2026-11-13).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| SSE-1 | Stream responses as `text/event-stream` with status 200, and refuse before streaming with a normal error response (SSE-R1, SSE-R2) | §9.2.2, §9.2.5 | Later release R3 | A failure after the stream starts goes in a `data` frame as an OpenAI `error` object ([OAI-4](std-openai-api-tracker.html)) |
| SSE-2 | Write each chunk as one UTF-8 `data:` line ending in a blank line, never a raw CR or LF in a value (SSE-R3 to SSE-R7) | §9.2.5, §9.2.6 | Later release R3 | Compact JSON escapes line breaks inside strings, so one chunk fits on one line; a test should parse the stream back with a §9.2.6 reader |
| SSE-3 | Keep-alive comments on long silences, and flush each event rather than buffer (SSE-R8) | §9.2.7 | Later release R3 | Authoring notes, not mandatory; long prefill can leave a stream idle for seconds |
