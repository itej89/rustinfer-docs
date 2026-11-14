---
title: "HTTP RFC 9110 and RFC 9112 requirements"
navtitle: Requirements
section: Standards
group: "Serving / HTTP RFC 9110 and RFC 9112"
order: 21
summary: The HTTP/1.1 parsing, framing, connection and status-code rules an origin server must follow, limited to what rustinfer's server uses.
---

# HTTP RFC 9110 and RFC 9112 requirements

Sources: `specs/serving/rfc9110.txt` (RFC 9110, June 2022),
`specs/serving/rfc9112.txt` (RFC 9112, June 2022), and for 429 only
`specs/serving/rfc6585.txt` (RFC 6585, April 2012). Section numbers are those
of each RFC. Only rules that bind an origin server in our scope are listed:
rules for clients, proxies, caches, ranges, conditional requests, `Upgrade`,
`CONNECT` and TLS are out of scope.

## Message syntax and parsing (RFC 9112)

| id | requirement | source |
|---|---|---|
| H-R1 | "A recipient MUST parse an HTTP message as a sequence of octets in an encoding that is a superset of US-ASCII", not as a Unicode string. | RFC 9112 §2.2 |
| H-R2 | A recipient of a bare CR "MUST consider that element to be invalid or replace each bare CR with SP". A sender "MUST NOT send whitespace between the start-line and the first header field"; a recipient that receives it "MUST either reject the message as invalid or consume each whitespace-preceded line". | RFC 9112 §2.2 |
| H-R3 | A server that receives octets not matching the HTTP-message grammar "SHOULD respond with a 400 (Bad Request) response and close the connection". | RFC 9112 §2.2 |
| H-R4 | "A server that receives a request-target longer than any URI it wishes to parse MUST respond with a 414 (URI Too Long)"; a method longer than any it implements SHOULD get 501. Request-lines of at least 8000 octets are RECOMMENDED. | RFC 9112 §3 |
| H-R5 | "A server MUST respond with a 400 (Bad Request) status code to any HTTP/1.1 request message that lacks a Host header field" or has more than one, or an invalid one. | RFC 9112 §3.2 |
| H-R6 | The status-line is `HTTP-version SP status-code SP [ reason-phrase ]`; "A server MUST send the space that separates the status-code from the reason-phrase even when the reason-phrase is absent". | RFC 9112 §4 |
| H-R7 | "A server MUST reject, with a response status code of 400 (Bad Request), any received request message that contains whitespace between a header field name and colon." | RFC 9112 §5.1 |
| H-R8 | Request body length: with both `Content-Length` and `Transfer-Encoding` the server MAY reject or use `Transfer-Encoding` alone, and "MUST close the connection after responding"; if `chunked` is not the final transfer coding the server "MUST respond with the 400 (Bad Request) status code and then close the connection"; an invalid `Content-Length` is "an unrecoverable error" and the server "MUST respond with a 400 (Bad Request) status code and then close the connection"; with neither field the body length is zero. | RFC 9112 §6.1, §6.3 items 3 to 7 |
| H-R9 | "A recipient MUST be able to parse the chunked transfer coding" (request bodies may arrive chunked). A server that receives a transfer coding it does not understand SHOULD respond with 501. | RFC 9112 §6.1, §7.1 |
| H-R10 | "A server MUST NOT send a response containing Transfer-Encoding unless the corresponding request indicates HTTP/1.1." A streamed response therefore uses chunked coding only to HTTP/1.1 clients, and otherwise is delimited by closing the connection. | RFC 9112 §6.1, §6.3 item 8 |
| H-R11 | Persistence: HTTP/1.1 connections persist unless `close` is sent. "A server MUST read the entire request message body or close the connection after sending its response." A server that does not support persistent connections "MUST send the "close" connection option in every response". | RFC 9112 §9.3 |
| H-R12 | Pipelined requests: the server "MUST send the corresponding responses in the same order that the requests were received". | RFC 9112 §9.3.2 |
| H-R13 | A server that receives `Connection: close` "MUST initiate closure of the connection ... after it sends the final response" and "MUST NOT process any further requests received on that connection"; the same applies after the server itself sends `close`. | RFC 9112 §9.6 |

## Semantics (RFC 9110)

| id | requirement | source |
|---|---|---|
| H-R14 | "All general-purpose servers MUST support the methods GET and HEAD." A method that is "recognized and implemented, but not allowed for the target resource" SHOULD get 405, and an unrecognized one SHOULD get 501. A 405 response MUST carry an `Allow` header field. | RFC 9110 §9.1, §15.5.6, §10.2.1 |
| H-R15 | Headers on responses: "An origin server with a clock ... MUST generate a Date header field in all 2xx ... and 4xx (Client Error) responses"; a sender of content "SHOULD generate a Content-Type header field"; without `Transfer-Encoding` an origin server "SHOULD send a Content-Length header field when the content size is known". | RFC 9110 §6.6.1, §8.3, §8.6 |
| H-R16 | Status codes used by RI-SRV: 200 OK (§15.3.1; for POST the content is "the status of, or results obtained from, the action"); 400 Bad Request for "malformed request syntax" (§15.5.1); 404 Not Found for an unknown path (§15.5.5); 413 Content Too Large when "the request content is larger than the server is willing or able to process" (§15.5.14); 415 Unsupported Media Type for a body that is not JSON (§15.5.16); 500 Internal Server Error (§15.6.1); 503 Service Unavailable for "a temporary overload" (§15.6.4). | RFC 9110 §15 |
| H-R17 | 4xx and 5xx responses: "the server SHOULD send a representation containing an explanation of the error situation, and whether it is a temporary or permanent condition". | RFC 9110 §15.5, §15.6 |
| H-R18 | `Retry-After` (an HTTP-date or delay-seconds) MAY accompany 503 and 413; with 503 "Retry-After indicates how long the service is expected to be unavailable". | RFC 9110 §10.2.3, §15.6.4, §15.5.14 |
| H-R19 | 429 Too Many Requests: "the user has sent too many requests in a given amount of time"; the representation SHOULD explain the condition and MAY include `Retry-After`. | RFC 6585 §4 (not RFC 9110) |

Defensive parsing (RFC 9110 §2.3: "A recipient SHOULD parse a received
protocol element defensively ... and fit within a reasonable buffer size")
is the basis for RI-SRV-005's size limits.
