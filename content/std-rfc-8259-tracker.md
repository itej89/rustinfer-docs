---
title: "RFC 8259 tracker"
navtitle: Tracker
section: Standards
group: "Data and integrity / RFC 8259"
order: 23
summary: Gaps between rustinfer's JSON and RFC 8259 with its canonical profile; both closed by PR #52 (b99720a).
---

# RFC 8259 tracker

From the [audit](std-rfc-8259-audit.html) of 2026-11-13, re-audited against
`origin/main` `8c7d47e` on 2026-11-14 (metadata version 2, used ranges: no new gap). Both rows were raised in
issue #51 and closed by PR #52 (merge `b99720a`).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| JSON-1 | A real can read back one unit in the last place off, so a Model IR document does not always round-trip "without loss" | RI-MIR-007 (canonical profile, P2); RFC 8259 §6 permits the precision limit, the profile does not | Fixed 2026-11-13 b99720a | `float_roundtrip` is enabled on the workspace `serde_json` (`Cargo.toml:54`). Test: `crates/rustinfer-mir/tests/json_roundtrip.rs:229` `test_reals_round_trip_bit_for_bit_across_magnitudes` (100,000 seeded reals, bit for bit) and `:253` `test_hard_real_attribute_round_trips_through_the_document` (`394301.33835633675` through the document), both `Verifies RI-MIR-007` |
| JSON-2 | No test writes and re-reads a string with a quotation mark, reverse solidus or control character | §7 | Fixed 2026-11-13 b99720a | Escaping is `serde_json`'s (`crates/rustinfer-artifact/src/json.rs:97`, `:111`). Tests: `crates/rustinfer-artifact/tests/json_strings.rs:58` (every control character, `"` and `\` escaped on output and read back), `:76` (unescaped control character refused), `:92` (every escape and a surrogate pair decode), `:102` (lone surrogates refused) |
