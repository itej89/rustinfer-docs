---
title: "HTTP RFC 9110 and RFC 9112"
navtitle: Overview
section: Standards
group: "Serving / HTTP RFC 9110 and RFC 9112"
order: 20
summary: HTTP semantics (RFC 9110) and HTTP/1.1 message syntax (RFC 9112) as rustinfer's server must use them from R3.
---

# HTTP RFC 9110 and RFC 9112

**Scope (SRS §1.4, RFC-9110):** HTTP/1.1 message syntax and the status codes
RI-SRV-002 and RI-SRV-005 use. SRS §3.1.4 fixes the transport: "HTTP/1.1 with
SSE (R3)". The status codes named are 200 (`/health` when the executor can
admit), 400 (malformed JSON), 429 or 503 (overload); size limits imply 413.

**Implementation:** none yet. The server is RI-SRV, Release 3. On
`origin/main` (`ccf02b3`) `rustinfer serve` is a stub that returns
`NotImplemented` (`crates/rustinfer-cli/src/commands.rs:97`), and the
workspace has no HTTP dependency (`Cargo.toml`, `[workspace.dependencies]`).

**Conformance:** mandatory from **R3**. Nothing is required in R1.

**Source:** `specs/serving/rfc9110.txt`, R. Fielding, M. Nottingham,
J. Reschke (Eds.), *RFC 9110, HTTP Semantics* (STD 97), June 2022,
<https://www.rfc-editor.org/rfc/rfc9110>; and `specs/serving/rfc9112.txt`,
*RFC 9112, HTTP/1.1* (STD 99), June 2022,
<https://www.rfc-editor.org/rfc/rfc9112>, updated by RFC 9931 (March 2026,
*Security Considerations for Optimistic Protocol Transitions in HTTP/1.1*,
which concerns `Upgrade` and `CONNECT` and does not touch our scope). 429 is
not defined in either: it is RFC 6585 §4 (`specs/serving/rfc6585.txt`),
cited here as a supporting source. All three downloaded 2026-11-13.

| | |
|---|---|
| Pages | [requirements](std-rfc-9110-requirements.html) · [audit](std-rfc-9110-audit.html) · [tracker](std-rfc-9110-tracker.html) |
| Conformance | mandatory R3 (RI-SRV-001, RI-SRV-002, RI-SRV-005) |
| Audited | 2026-11-13, by reading `origin/main` `ccf02b3` and the SRS on branch `docs/srs-standards-conformance` |
| Result | later release: no HTTP code exists, as expected before R3 |
| Open gaps | 0 (4 gaps, covering 19 requirement items, recorded as later release R3) |
