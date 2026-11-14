---
title: "OpenAI API 2.3.0 requirements"
navtitle: Requirements
section: Standards
group: "Serving / OpenAI API 2.3.0"
order: 11
summary: The endpoints, request fields, response objects and stream chunks of the OpenAI API that RI-SRV-001 puts in rustinfer's scope.
---

# OpenAI API 2.3.0 requirements

Source: `specs/serving/openapi.yaml` (openai-openapi, `info.version` 2.3.0,
commit `a45d45bda635`). References are `schema` or `path` names with their
line in that file. Only the parts in the SRS scope are listed: the three
endpoints, the fields RI-SRV-001 names, and the shapes needed to return them.
Required properties are those in the schema's `required` list.

## Endpoints

| id | requirement | source |
|---|---|---|
| OA-R1 | `POST /chat/completions` (`createChatCompletion`) takes an `application/json` body of `CreateChatCompletionRequest`. A 200 returns `application/json` `CreateChatCompletionResponse`, or `text/event-stream` of `CreateChatCompletionStreamResponse` chunks when `stream` is true. | path `/chat/completions` post, l. 2523 |
| OA-R2 | `POST /completions` (`createCompletion`) takes `CreateCompletionRequest`. A 200 returns `CreateCompletionResponse` as JSON, or as `text/event-stream` chunks of the same schema when `stream` is true. | path `/completions` post, l. 3915 |
| OA-R3 | `GET /models` (`listModels`) returns `ListModelsResponse`: `object` `"list"` and `data`, an array of `Model` (required `id`, `object` `"model"`, `created` Unix seconds, `owned_by`). | path `/models` l. 10501; `ListModelsResponse` l. 56523; `Model` l. 58417 |
| OA-R4 | The server base is `/v1` (`servers: https://api.openai.com/v1`), so the paths are served as `/v1/chat/completions`, `/v1/completions`, `/v1/models`, as RI-SRV-001 names them. | `servers`, l. 15 |

## Request fields

Chat requires `model` and `messages` (at least one item, a
`ChatCompletionRequestMessage`: developer, system, user, assistant, tool or
the deprecated function message, l. 44349). Completions requires `model` and
`prompt` (a string, an array of strings, an array of token ids, or an array
of token-id arrays).

| id | field | chat (`CreateChatCompletionRequest`, l. 46101) | completions (`CreateCompletionRequest`, l. 46819) |
|---|---|---|---|
| OA-R5 | `n` | integer 1 to 128, default 1: choices per input | the same |
| OA-R6 | `logprobs` | boolean, default false; with it `top_logprobs`, integer 0 to 20 ("`logprobs` must be set to `true` if this parameter is used") | integer 0 to 5: the number of most likely tokens to return per position |
| OA-R7 | `stop` | `StopConfiguration` (l. 78705): null, a string, or an array of 1 to 4 strings; "up to 4 sequences where the API will stop generating" | the same |
| OA-R8 | `seed` | int64; best effort determinism, "Determinism is not guaranteed" | integer, the same meaning |
| OA-R9 | `temperature` | number 0 to 2, default 1 (`ModelResponseProperties`, l. 58955) | number 0 to 2, default 1 |
| OA-R10 | `top_p` | number 0 to 1, default 1 (`ModelResponseProperties`) | number 0 to 1, default 1 |
| OA-R11 | `max_tokens` | integer, deprecated in favour of `max_completion_tokens` but still in the schema | integer, minimum 0, default 16 |
| OA-R12 | `response_format` | one of `ResponseFormatText` (`type` `"text"`, l. 73276), `ResponseFormatJsonObject` (`"json_object"`, l. 73198), `ResponseFormatJsonSchema` (`"json_schema"` with `json_schema.name` required, optional `schema` and `strict`, l. 73219), discriminated by `type` | not a field |
| OA-R13 | `tools` | array of `ChatCompletionTool` (`type` `"function"`, `function` a `FunctionObject` with required `name`, optional `description`, `parameters`, `strict`, l. 44934, 54070) or custom tools | not a field |
| OA-R14 | `stream` | boolean, default false: the response is server-sent events; `stream_options.include_usage` adds a final usage chunk (l. 44744) | the same; "the stream terminated by a `data: [DONE]` message" (l. 47010) |

The SRS makes `response_format` and `tools` conditional: "where guided
decoding supports them". The `logprobs` field means different things on the
two endpoints, and both meanings are in scope.

## Responses

| id | requirement | source |
|---|---|---|
| OA-R15 | A chat completion has required `id`, `object` `"chat.completion"`, `created` (Unix seconds), `model`, `choices`; optional `usage` (`CompletionUsage`, l. 45222: required `prompt_tokens`, `completion_tokens`, `total_tokens`). Each choice has required `index`, `message` (`ChatCompletionResponseMessage`, l. 44609: required `role` `"assistant"` and `content`, optional `tool_calls`), `finish_reason` (`stop`, `length`, `tool_calls`, `content_filter`, `function_call`) and `logprobs` (null, or `content` and `refusal` arrays of `ChatCompletionTokenLogprob`, l. 44875: `token`, `logprob`, `bytes`, `top_logprobs`). | `CreateChatCompletionResponse`, l. 46483 |
| OA-R16 | A stream chunk has required `id` (the same in every chunk), `object` `"chat.completion.chunk"`, `created` (the same in every chunk), `model`, `choices`; each choice has required `index` and `delta` (`ChatCompletionStreamResponseDelta`, l. 44797: `role`, `content`, `tool_calls`), and `finish_reason` null until the choice ends. `usage` is present only with `stream_options.include_usage`; `choices` may then be empty in that last chunk. The stream ends with the literal frame `data: [DONE]` followed by a blank line, "not a JSON chunk", with no `event:` field. | `CreateChatCompletionStreamResponse`, l. 46639; path `/chat/completions` 200, l. 2555 to 2590 |
| OA-R17 | A text completion has required `id`, `object` `"text_completion"`, `created`, `model`, `choices`; each choice has required `text`, `index`, `logprobs` (null, or `tokens`, `token_logprobs`, `top_logprobs`, `text_offset`) and `finish_reason` (`stop`, `length`, `content_filter`; null while a streamed completion is unfinished). | `CreateCompletionResponse`, l. 47066 |
| OA-R18 | Errors carry `ErrorResponse`: an `error` object with required `type`, `message`, `param` (string or null) and `code` (string or null). The operations document 400 for an invalid request, 429 (`InferenceRateLimited`, l. 124152) and 503 (`InferenceServiceUnavailable`, l. 124178, example code `server_is_overloaded`). A failure after a stream has started "may contain a JSON object with an `error` field" in a data frame. | `Error` l. 51612, `ErrorResponse` l. 51654 |

Out of scope: every other path, and request fields RI-SRV-001 does not list
(for example `logit_bias`, `frequency_penalty`, `audio`, `modalities`,
`web_search_options`, `prediction`, `store`). A server may ignore or refuse
them; the SRS does not say which.
