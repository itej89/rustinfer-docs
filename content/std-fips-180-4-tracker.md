---
title: "FIPS 180-4 tracker"
navtitle: Tracker
section: Standards
group: "Data and integrity / FIPS 180-4"
order: 13
summary: Gaps between rustinfer's SHA-256 use and FIPS 180-4; SHA256-1 closed by PR #52, SHA256-2 (used-range digest paths) open.
---

# FIPS 180-4 tracker

From the [audit](std-fips-180-4-audit.html) of 2026-11-13, re-audited against
`origin/main` `8c7d47e` on 2026-11-14 after PRs #53 and #49 added the used-range
digests.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| SHA256-1 | The known-answer test covers only the one-block "abc" message | §5.1.1 (padding), §6.2.2 (multi-block computation) | Fixed 2026-11-13 b99720a | Issue #51, PR #52. Code unchanged (`crates/rustinfer-artifact/src/hash.rs:35-39`, `sha2::Sha256::digest`). Tests: `crates/rustinfer-artifact/tests/sha256_vectors.rs:54` empty message, `:61` two-block message, `:69` 55/56/63/64-byte padding boundary, `:82` one million `a` (all `Verifies RI-ART-008`) |
| SHA256-2 | The used-range digest is computed by two paths that agree only while a range is at most 4 bytes: the build reads `range.length.min(4)` bytes but records the full range, and Sluice's 64 KiB chunk loop has no test past one chunk | §6 (S7, an alternate method must yield identical results); RI-ART-008 | Open | Found by the re-audit of `8c7d47e`. Build: `read_range` (`crates/rustinfer-frontend/src/kv_scales.rs:197-214`, cap at `:204`), digest at `:62-67`. Load: `hash_range` (`crates/rustinfer-sluice/src/checkpoint.rs:100-121`). Today's only used ranges are KV scales of 2 or 4 bytes (`kv_scales.rs:158-179`), so no wrong digest is recorded, and `crates/rustinfer-frontend/tests/mxfp4_kv_fp8.rs:140` checks it. The way: read and hash exactly `range.length` bytes in the build (or refuse a longer range), and a Sluice test of a range over 64 KiB against `Sha256::of`. No issue yet. |
