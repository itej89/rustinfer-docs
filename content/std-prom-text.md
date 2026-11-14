---
title: "Prometheus text format 0.0.4"
navtitle: Overview
section: Standards
group: "Serving / Prometheus text format 0.0.4"
order: 40
summary: The Prometheus text exposition format, version 0.0.4, which rustinfer's /prometheus/metrics endpoint must serve from R3 with the metrics RI-OBS-001 defines.
---

# Prometheus text format 0.0.4

**Scope (SRS §1.4, PROM-TEXT):** text format 0.0.4 on `/prometheus/metrics`
(RI-SRV-002). The metrics exposed are those of RI-OBS-001:
`rustinfer_requests_total{status}`, `rustinfer_iteration_duration_seconds`,
`rustinfer_ttft_seconds`, `rustinfer_tpot_seconds`,
`rustinfer_tokens_total{phase}`, `rustinfer_kv_blocks{state}`,
`rustinfer_kv_reuse_total{result}`, `rustinfer_errors_total{error_type}`.
OpenMetrics and the protobuf format are out of scope.

**Implementation:** none yet. RI-SRV-002 (the endpoint) is Release 3 and
RI-OBS-001 (maintaining the metrics) is Release 2. On `origin/main`
(`ccf02b3`) no metric is maintained or exported; the metric names and types
are planned in the signal inventory of `docs/observability.md:21` to
`docs/observability.md:27` (counters, histograms, one gauge), and `rustinfer
serve` is a stub (`crates/rustinfer-cli/src/commands.rs:97`).

**Conformance:** mandatory from **R3**. Nothing is required in R1.

**Source:** `specs/serving/prometheus-exposition-formats.md`, Prometheus
documentation, *Exposition formats*, section *Prometheus Text Format*, at
commit `9bc542d9e249` of <https://github.com/prometheus/docs> (published at
<https://prometheus.io/docs/instrumenting/exposition_formats/>), accessed
2026-11-13. The page has no version or date of its own; "0.0.4" is the
`version` parameter of its `Content-Type`. Name rules come from
`specs/serving/prometheus-data-model.md` (*Data model*, same commit). The
page has no numbered clauses, so requirements cite its headings.

| | |
|---|---|
| Pages | [requirements](std-prom-text-requirements.html) · [audit](std-prom-text-audit.html) · [tracker](std-prom-text-tracker.html) |
| Conformance | mandatory R3 (RI-SRV-002; metric names from RI-OBS-001, R2) |
| Audited | 2026-11-13, by reading `origin/main` `ccf02b3` and the SRS on branch `docs/srs-standards-conformance` |
| Result | later release: no exposition code exists, as expected before R3 |
| Open gaps | 0 (3 gaps, covering 13 requirement items, recorded as later release R2 and R3) |
