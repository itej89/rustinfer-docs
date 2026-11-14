---
title: "FIPS 180-4 tracker"
navtitle: Tracker
section: Standards
group: "Data and integrity / FIPS 180-4"
order: 13
summary: Gaps between rustinfer's SHA-256 use and FIPS 180-4; the test-coverage gap was closed by PR #52.
---

# FIPS 180-4 tracker

From the [audit](std-fips-180-4-audit.html) of 2026-11-13.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| SHA256-1 | The known-answer test covers only the one-block "abc" message | §5.1.1 (padding), §6.2.2 (multi-block computation) | Fixed 2026-11-13 b99720a | Issue #51, PR #52. Code unchanged (`crates/rustinfer-artifact/src/hash.rs:35-39`, `sha2::Sha256::digest`). Tests: `crates/rustinfer-artifact/tests/sha256_vectors.rs:54` empty message, `:61` two-block message, `:69` 55/56/63/64-byte padding boundary, `:82` one million `a` (all `Verifies RI-ART-008`) |
