---
title: "Prometheus text format 0.0.4 requirements"
navtitle: Requirements
section: Standards
group: "Serving / Prometheus text format 0.0.4"
order: 41
summary: The lines, escaping, histogram conventions and content type of the Prometheus text format, applied to the metrics RI-OBS-001 defines.
---

# Prometheus text format 0.0.4 requirements

Source: `specs/serving/prometheus-exposition-formats.md` (prometheus/docs
commit `9bc542d9e249`), cited by heading, and for names
`specs/serving/prometheus-data-model.md` (same commit). The page uses "must"
in lower case; those sentences are quoted as requirements.

## Transport

| id | requirement | source |
|---|---|---|
| PT-R1 | `Content-Type` is `text/plain` with `version=0.0.4` ("A missing `version` value will lead to a fall-back to the most recent text format version"). "Starting with Prometheus 3.0, scrape targets **must** return a valid `Content-Type` header": a missing or unsupported one fails the scrape. Optional `Content-Encoding: gzip`. | *Basic info*; *HTTP Content-Type requirements* |
| PT-R2 | Encoding UTF-8 with `\n` line endings. "The last line must end with a line feed character." Empty lines are ignored. | *Basic info*; *Details* |

## Lines

| id | requirement | source |
|---|---|---|
| PT-R3 | A sample line is `metric_name [ "{" labels "}" ] value [ timestamp ]`; labels are `label_name="escaped_string"` separated by commas. Tokens are separated by blanks or tabs. | *Line format*; the EBNF under *Comments, help text, and type information* |
| PT-R4 | Names: metric names "SHOULD match the regex `[a-zA-Z_:][a-zA-Z0-9_:]*`", label names `[a-zA-Z_][a-zA-Z0-9_]*`; names outside that set "must be quoted and escaped". Colons are "reserved for user-defined recording rules" and "SHOULD NOT be used by exporters". Label names beginning with `__` "MUST be reserved for internal Prometheus use". | *Comments, help text, and type information*; *Data model* |
| PT-R5 | Label values: any UTF-8, but backslash, double quote and line feed "have to be escaped as `\\`, `\"`, and `\n`". | EBNF notes |
| PT-R6 | `value` is a float as Go's `ParseFloat()` reads it; `NaN`, `+Inf`, `-Inf` are valid. The optional timestamp is int64 milliseconds since the epoch. | EBNF notes |
| PT-R7 | `# HELP <name> <docstring>`: backslash and line feed escaped as `\\` and `\n`; "Only one `HELP` line may exist for any given metric name." | *Comments, help text, and type information* |
| PT-R8 | `# TYPE <name> <type>` with type `counter`, `gauge`, `histogram`, `summary` or `untyped`; only one per name; it "must appear before the first sample is reported for that metric name". Without it the type is `untyped`. | *Comments, help text, and type information* |
| PT-R9 | "All lines for a given metric must be provided as one single group, with the optional `HELP` and `TYPE` lines first." "Each line must have a unique combination of a metric name and labels." | *Grouping and sorting* |
| PT-R10 | A histogram `x` is written as `x_bucket{le="y"}` lines, `x_sum` and `x_count`. It "_must_ have a bucket with `{le="+Inf"}`. Its value _must_ be identical to the value of `x_count`." Buckets "must appear in increasing numerical order" of `le`. | *Histograms and summaries* |

## The metrics of RI-OBS-001

Types are those planned in `docs/observability.md` on `origin/main`. All
names and labels fit the legacy character set, so none needs quoting.

| id | metric | TYPE | lines it produces |
|---|---|---|---|
| PT-R11 | `rustinfer_requests_total{status}`, `rustinfer_tokens_total{phase}`, `rustinfer_kv_reuse_total{result}`, `rustinfer_errors_total{error_type}` | `counter` | one sample per label value, under one `HELP` and `TYPE` per name |
| PT-R12 | `rustinfer_kv_blocks{state}` | `gauge` | one sample per `state` |
| PT-R13 | `rustinfer_iteration_duration_seconds`, `rustinfer_ttft_seconds`, `rustinfer_tpot_seconds` | `histogram` | `_bucket{le=...}` lines in increasing order ending in `le="+Inf"`, `_sum`, `_count` (PT-R10) |

RI-OBS-001 also requires "no high-cardinality labels". That is the SRS's rule,
not the format's: the format only requires each name and label set to be
unique (PT-R9).
