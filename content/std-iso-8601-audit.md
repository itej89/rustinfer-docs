---
title: "ISO 8601-1:2019 audit"
navtitle: Audit
section: Standards
group: "Data and integrity / ISO 8601-1:2019"
order: 32
summary: The 2026-11-13 audit of rustinfer's timestamps against the RFC 3339 profile: written correctly; read back with the shape checked but not the field ranges.
---

# ISO 8601-1:2019 audit

**Audit of 2026-11-13**, against the [requirements](std-iso-8601-requirements.html),
which come from RFC 3339 because ISO 8601 itself is paywalled.

**Method.** Read `crates/rustinfer-core/src/logging.rs` and
`crates/rustinfer-artifact/src/metadata.rs` on origin/main (`ccf02b3`) and the tests
of both. Checked the civil-date arithmetic by hand against the test values. Nothing
was run.

| id | result | evidence |
|---|---|---|
| D1 grammar, three-digit fraction | **conforms** | `iso8601_from_unix` formats `{year:04}-{month:02}-{day:02}T{hh:02}:{mm:02}:{ss:02}.{millis:03}Z` (`crates/rustinfer-core/src/logging.rs:150-160`). `crates/rustinfer-core/tests/logging.rs:53` `test_iso8601_from_unix_known_values` (epoch, 2000-02-29, a 2025 instant); `tests/logging.rs:35` checks the `ts=` field's length and `Z`. Neither test carries a `Verifies` tag (DT-2). The metadata side: `crates/rustinfer-artifact/tests/metadata.rs:93` `test_timestamp_now_is_iso8601_utc` (`Verifies RI-ART-008`) |
| D2 UTC, "Z" | **conforms** | the time is `SystemTime` since the Unix epoch (`logging.rs:141-146`), UTC by definition; always "Z" |
| D3 field ranges, writing | **conforms** | Hinnant's `civil_from_days` (`logging.rs:191-215`) gives valid month and day for any day count; hours, minutes and seconds are remainders (`logging.rs:155-158`). The year is four digits until 9999 |
| D3 field ranges, reading | **partial** | `check_timestamp` checks length, separators and digits only (`crates/rustinfer-artifact/src/metadata.rs:183-201`), so `2026-13-45T25:61:61.000Z` passes. `crates/rustinfer-artifact/tests/metadata.rs:78` refuses `"yesterday"` only. DT-1 |
| D4 leap day, leap second | **conforms** | February 29 comes out in leap years (the 2000-02-29 test value). Unix time has no leap seconds, so ":60" is never written, which RFC 3339 allows ("should not generate timestamps involving inserted leap seconds until after" announcement) |
| D5 upper case | **conforms** | written upper case; the reader requires "T" and "Z" upper case (`metadata.rs:22-30`), a limit §5.6 permits |
| D6 sortable | **conforms** | fixed width, fixed precision, one offset |

**Also found.** `iso8601_now` falls back to the epoch when the clock is before
1970 (`logging.rs:144`, `unwrap_or_default`), so a host with a wrong clock writes
`1970-01-01T00:00:00.000Z` with no warning. The text is valid; the instant is not.
DT-3.

**Result.** Writing conforms; reading is partial (D3); state *part*.
