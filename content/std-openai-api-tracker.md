---
title: "OpenAI API 2.3.0 tracker"
navtitle: Tracker
section: Standards
group: "Serving / OpenAI API 2.3.0"
order: 13
summary: The Release 3 work for the OpenAI API shapes; no open gap, since nothing is due before R3.
---

# OpenAI API 2.3.0 tracker

From the [audit](std-openai-api-audit.html). No gap is open: every item is
Release 3 work. The rows below list that work so it stays visible; they are
not counted as gaps. No GitHub issue covers them yet
(`gh issue list -R itej89/rustinfer --state all`, 2026-11-13).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| OAI-1 | The three endpoints under `/v1` (OA-R1 to OA-R4) | paths `/chat/completions`, `/completions`, `/models` | Later release R3 | RI-SRV-001, RI-CLI-009. `serve` is a stub (`crates/rustinfer-cli/src/commands.rs:97`) |
| OAI-2 | The request fields `n`, `logprobs`, `stop`, `seed`, `temperature`, `top_p`, `max_tokens`, `stream` (OA-R5 to OA-R11, OA-R14) | `CreateChatCompletionRequest`, `CreateCompletionRequest` | Later release R3 | `logprobs` is a boolean plus `top_logprobs` on chat and an integer 0 to 5 on completions; both are in scope |
| OAI-3 | `response_format` and `tools` (OA-R12, OA-R13) | `ResponseFormat*`, `ChatCompletionTool` | Later release R3 | Only "where guided decoding supports them"; the grammar backend is open issue OI-006 |
| OAI-4 | Response objects, stream chunks and the `data: [DONE]` frame (OA-R15 to OA-R17) | `CreateChatCompletionResponse`, `CreateChatCompletionStreamResponse`, `CreateCompletionResponse` | Later release R3 | The stream framing itself is on the [SSE tracker](std-sse-tracker.html) |
| OAI-5 | `ErrorResponse` bodies for 400, 429, 503 (OA-R18) | `Error`, `ErrorResponse` | Later release R3 | With RI-SRV-005; status codes on the [HTTP tracker](std-rfc-9110-tracker.html) |

## Notes for the SRS

- RI-SRV-001 names `max_tokens`. On chat the schema marks it deprecated in
  favour of `max_completion_tokens`. Clients that send only
  `max_completion_tokens` would lose their limit unless the server accepts
  both. The SRS may want to name both.
