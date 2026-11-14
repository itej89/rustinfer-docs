---
title: "ISO 8601-1:2019"
navtitle: Overview
section: Standards
group: "Data and integrity / ISO 8601-1:2019"
order: 30
summary: UTC timestamps with milliseconds in the RFC 3339 profile of ISO 8601, used in every log line and in the artifact's metadata.
---

# ISO 8601-1:2019

**Scope (SRS §1.4, ISO-8601):** UTC date-time with milliseconds in the RFC 3339
profile, `YYYY-MM-DDTHH:MM:SS.mmmZ`. **Conformance:** mandatory R1. The requirements
that cite it are RI-CLI-011 (every log line has an ISO-8601 timestamp) and RI-ART-008
(the artifact's `metadata` timestamp, "ISO-8601 UTC").

**The standard is paywalled.** ISO 8601-1:2019 (with Amd 1:2022) is sold by ISO;
its catalogue page (https://www.iso.org/standard/70907.html) answered the download
with a bot challenge, so not even the abstract was obtained. The SRS row itself names
the profile used, RFC 3339, and limits the scope to it. The requirements here are
therefore taken from **RFC 3339** (IETF, *Date and Time on the Internet:
Timestamps*, G. Klyne and C. Newman, July 2002,
https://www.rfc-editor.org/rfc/rfc3339, `specs/data/rfc3339.txt`), a freely
available, authoritative profile of ISO 8601. Each is marked as from that secondary
source; no ISO clause number is cited.

**Implementation:** one formatter in `rustinfer-core`,
`crates/rustinfer-core/src/logging.rs:141-160` (`iso8601_now`,
`iso8601_from_unix`), a civil-date conversion from Unix days by Howard Hinnant's
algorithm without a date crate (`logging.rs:191-215`). The log line puts it first
(`logging.rs:75-81`). The artifact's metadata uses the same clock
(`crates/rustinfer-artifact/src/metadata.rs:57-59`) and checks the shape on reading
(`metadata.rs:183-201`).

| | |
|---|---|
| Pages | [requirements](std-iso-8601-requirements.html) · [audit](std-iso-8601-audit.html) · [tracker](std-iso-8601-tracker.html) |
| Audited | 2026-11-13, by reading origin/main and its tests against RFC 3339 |
| Writing | conforms |
| Reading (`metadata`) | **partial**: the shape is checked, the field ranges are not |
| Open gaps | 3 |
