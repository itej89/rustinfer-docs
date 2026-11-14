---
title: "FIPS 180-4 tracker"
navtitle: Tracker
section: Standards
group: "Data and integrity / FIPS 180-4"
order: 13
summary: Gaps between rustinfer's SHA-256 use and FIPS 180-4; SHA256-1 closed by PR #52, SHA256-2 (used-range digest paths) by PR #57; none open.
---

# FIPS 180-4 tracker

From the [audit](std-fips-180-4-audit.html) of 2026-11-13, re-audited against
`origin/main` `8c7d47e` on 2026-11-14 after PRs #53 and #49 added the used-range
digests, then against `99c1ec7` on 2026-11-14 after PR #57 (issue #51)
closed SHA256-2.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| SHA256-1 | The known-answer test covers only the one-block "abc" message | §5.1.1 (padding), §6.2.2 (multi-block computation) | Fixed 2026-11-13 b99720a | Issue #51, PR #52. Code unchanged (`crates/rustinfer-artifact/src/hash.rs:35-39`, `sha2::Sha256::digest`). Tests: `crates/rustinfer-artifact/tests/sha256_vectors.rs:54` empty message, `:61` two-block message, `:69` 55/56/63/64-byte padding boundary, `:82` one million `a` (all `Verifies RI-ART-008`) |
| SHA256-2 | The used-range digest is computed by two paths that agree only while a range is at most 4 bytes: the build reads `range.length.min(4)` bytes but records the full range, and Sluice's 64 KiB chunk loop has no test past one chunk | §6 (S7, an alternate method must yield identical results); RI-ART-008 | Fixed 2026-11-14 99c1ec7 | Found by the re-audit of `8c7d47e`; issue #51, PR #57. Build: a KV scale range must be exactly one element of its dtype, else it is refused as `InvalidTensor` naming the tensor and `byte_range` (`read_scale_bytes`, `crates/rustinfer-frontend/src/kv_scales.rs:205-219`, check at `:207`), and `read_range` reads exactly `range.length` bytes, no cap (`:223-240`); the digest is `Sha256::of` over those bytes (`:66-71`). Load: `hash_range` unchanged (`crates/rustinfer-sluice/src/checkpoint.rs:102-124`, 64 KiB chunks). Tests: `test_used_ranges_hash_exactly_the_recorded_range` (`crates/rustinfer-frontend/src/kv_scales.rs:324`, `Verifies RI-ART-008`); `test_kv_scale_range_other_than_its_element_size_is_refused` (`crates/rustinfer-frontend/tests/mxfp4_audit.rs:205`, `Groundwork for RI-KVC-008`); `test_one_changed_byte_anywhere_in_a_long_used_range_is_refused` (`crates/rustinfer-sluice/tests/used_ranges.rs:99`, a bf16 range of 3 x 64 KiB + 14 bytes, one byte flipped at either side of each chunk boundary) and `test_used_range_longer_than_its_hashed_bytes_is_refused` (`:134`), both `Verifies RI-ART-008`. |
