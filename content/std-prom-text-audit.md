---
title: "Prometheus text format 0.0.4 audit"
navtitle: Audit
section: Standards
group: "Serving / Prometheus text format 0.0.4"
order: 42
summary: The 2026-11-13 audit of rustinfer against the Prometheus text format; no metric is exported yet, which is expected before R3.
---

# Prometheus text format 0.0.4 audit

**Audit of 2026-11-13**, against the [requirements](std-prom-text-requirements.html).

**Method.** Read the SRS on branch `docs/srs-standards-conformance` (v0.4.3,
open PR #50): §1.4 row PROM-TEXT, §3.1.3, RI-SRV-002 and RI-OBS-001. Read
`docs/observability.md` on `origin/main` (`ccf02b3`). Searched the crates for
`prometheus`, `metrics`, `rustinfer_` metric names and any counter or
histogram type. No tests were run: there is no code to test.

**Finding.** No metric is maintained or exported, and nothing writes the text
format. The metric names, kinds and labels are planned in
`docs/observability.md:21` to `docs/observability.md:27`, and they already
follow the naming rules of PT-R4 (snake case, `rustinfer_` prefix, `_total`
on counters, `_seconds` on durations, no colons, no `__` labels). That is a
plan, not code, so it is not counted as conforming. RI-OBS-001 is R2 and the
endpoint RI-SRV-002 is R3, so every item is **later release**.

| item | requirement | result | evidence |
|---|---|---|---|
| PT-R1 | `Content-Type: text/plain; version=0.0.4` | later release (R3) | no endpoint; `serve` stub, `commands.rs:97` |
| PT-R2 | UTF-8, `\n`, final line feed | later release (R3) | no writer |
| PT-R3 | sample line syntax | later release (R3) | no writer |
| PT-R4 | metric and label names | later release (R3) | names planned in `docs/observability.md:21`; no code |
| PT-R5 | label value escaping | later release (R3) | no writer |
| PT-R6 | float values | later release (R3) | no writer |
| PT-R7 | `HELP` lines | later release (R3) | no writer |
| PT-R8 | `TYPE` lines before samples | later release (R3) | no writer |
| PT-R9 | one group per metric, unique lines | later release (R3) | no writer |
| PT-R10 | histogram buckets, `+Inf`, `_sum`, `_count` | later release (R3) | no writer |
| PT-R11 | the four counters of RI-OBS-001 | later release (R2 to maintain, R3 to export) | no metrics |
| PT-R12 | the gauge `rustinfer_kv_blocks` | later release (R2 to maintain, R3 to export) | no metrics |
| PT-R13 | the three histograms of RI-OBS-001 | later release (R2 to maintain, R3 to export) | no metrics; bucket bounds not yet chosen |

**Result:** later. 0 conform, 0 partial, 0 missing, 13 later release. No item
is a gap in R1.
