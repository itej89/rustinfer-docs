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
3339, the profile the SRS names; ISO 8601 itself was not obtained. No GitHub issue
covers these rows.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| DT-1 | The `metadata` reader accepts a timestamp with an impossible month, day, hour, minute or second | RFC 3339 §5.6, §5.7 (secondary source for ISO 8601) | Open | `check_timestamp` (`crates/rustinfer-artifact/src/metadata.rs:183-201`) checks the shape only. Add the ranges (month 01-12, day by month and leap year, hour 00-23, minute 00-59, second 00-59, or 60 if leap seconds are to be read) and a refusal test per field |
| DT-2 | The formatter's tests carry no requirement tag and miss calendar edges | RI-CLI-011; RFC 3339 §5.7 | Open | `crates/rustinfer-core/tests/logging.rs:35` and `:53` have no `Verifies RI-CLI-011` tag (docs/testing.md). Add known values for a non-leap century (2100-02-28 to 2100-03-01), a year end and the last millisecond of a day |
| DT-3 | A clock before 1970 is written as the epoch, silently | RI-ART-008 (the build time) | Open | `crates/rustinfer-core/src/logging.rs:144`. The text stays valid RFC 3339, so this is a correctness note, not a format gap: log a warning, or refuse to stamp an artifact |
