---
title: "ISO 8601-1:2019 tracker"
navtitle: Tracker
section: Standards
group: "Data and integrity / ISO 8601-1:2019"
order: 33
summary: Gaps between rustinfer's timestamps and the RFC 3339 profile of ISO 8601.
---

# ISO 8601-1:2019 tracker

From the [audit](std-iso-8601-audit.html) of 2026-11-13. Requirements are from RFC
3339, the profile the SRS names; ISO 8601 itself was not obtained. DT-1 was raised in
issue #51 and closed by PR #52; no GitHub issue covers DT-2 or DT-3.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| DT-1 | The `metadata` reader accepts a timestamp with an impossible month, day, hour, minute or second | RFC 3339 §5.6, §5.7 (secondary source for ISO 8601) | Fixed 2026-11-13 b99720a | `check_timestamp_ranges` (`crates/rustinfer-artifact/src/metadata.rs:226-256`, with `days_in_month` and `is_leap_year` at `:274-286`) checks month, day, hour, minute and second (60 only at `23:59:60` on a month's last day), naming the field. Tests: `crates/rustinfer-artifact/tests/timestamp.rs:45`, `:53` (each field by name), `:71` (day per month, leap years), `:99` (leap second), all `Verifies RI-ART-008` |
| DT-2 | The formatter's tests carry no requirement tag and miss calendar edges | RI-CLI-011; RFC 3339 §5.7 | Open | `crates/rustinfer-core/tests/logging.rs:35` and `:53` have no `Verifies RI-CLI-011` tag (docs/testing.md). Add known values for a non-leap century (2100-02-28 to 2100-03-01), a year end and the last millisecond of a day |
| DT-3 | A clock before 1970 is written as the epoch, silently | RI-ART-008 (the build time) | Open | `crates/rustinfer-core/src/logging.rs:144`. The text stays valid RFC 3339, so this is a correctness note, not a format gap: log a warning, or refuse to stamp an artifact |
