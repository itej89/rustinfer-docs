---
title: "RFC 8259 tracker"
navtitle: Tracker
section: Standards
group: "Data and integrity / RFC 8259"
order: 23
summary: Gaps between rustinfer's JSON and RFC 8259 with its canonical profile: lossy reading of some reals, and no escaping test.
---

# RFC 8259 tracker

From the [audit](std-rfc-8259-audit.html) of 2026-11-13. No GitHub issue covers
either row.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| JSON-1 | A real can read back one unit in the last place off, so a Model IR document does not always round-trip "without loss" | RI-MIR-007 (canonical profile, P2); RFC 8259 §6 permits the precision limit, the profile does not | Open | `serde_json` is built without `float_roundtrip` (`Cargo.toml:51`). The fix is that feature on the workspace dependency, plus a test that round-trips many random finite `f64` attributes bit for bit. Until then the `Verifies RI-MIR-007` tags overstate the clause. Also matters for RI-GC-009 once a rebuild reads a document back |
| JSON-2 | No test writes and re-reads a string with a quotation mark, reverse solidus or control character | §7 | Open | Escaping is `serde_json`'s and correct today; the test would pin it for tensor and node names, which come from untrusted checkpoints |
