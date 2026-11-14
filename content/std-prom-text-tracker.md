---
title: "Prometheus text format 0.0.4 tracker"
navtitle: Tracker
section: Standards
group: "Serving / Prometheus text format 0.0.4"
order: 43
summary: The R2 metrics and R3 exposition work; no open gap, since nothing is due before R3.
---

# Prometheus text format 0.0.4 tracker

From the [audit](std-prom-text-audit.html). No gap is open: every item is
later-release work, listed so it stays visible and not counted as a gap. No
GitHub issue covers it yet (`gh issue list -R itej89/rustinfer --state all`,
2026-11-13).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| PROM-1 | Maintain the eight metrics of RI-OBS-001 with the kinds and labels of `docs/observability.md` (PT-R11 to PT-R13) | RI-OBS-001 | Later release R2 | The format needs histogram bucket bounds for the three `_seconds` metrics; `docs/observability.md` does not fix them yet |
| PROM-2 | Serve `GET /prometheus/metrics` with `Content-Type: text/plain; version=0.0.4` (PT-R1, PT-R2) | *Basic info*; *HTTP Content-Type requirements* | Later release R3 | RI-SRV-002. Prometheus 3.0 fails a scrape without a valid `Content-Type` |
| PROM-3 | Write the text format: lines, escaping, one `HELP` and `TYPE` per name before its samples, one group per metric, histogram conventions (PT-R3 to PT-R10) | *Line format*; *Comments, help text, and type information*; *Grouping and sorting*; *Histograms and summaries* | Later release R3 | A test should parse the output back with a format reader and check `le="+Inf"` equals `_count` |

## Notes for the SRS

- The prometheus.io page is unversioned. "0.0.4" survives only as the
  `version` parameter of the content type, and the page says a missing
  version falls back to "the most recent text format version". Pinning the
  prometheus/docs commit (here `9bc542d9e249`) alongside "0.0.4" would make
  the reference reproducible.
