---
title: "FIPS 180-4 audit"
navtitle: Audit
section: Standards
group: "Data and integrity / FIPS 180-4"
order: 12
summary: The audit of rustinfer's SHA-256 against FIPS 180-4, re-audited 2026-11-14 at 8c7d47e: the algorithm conforms through the pinned sha2 crate; the new used-range digests conform, with one coverage gap.
---

# FIPS 180-4 audit

**Re-audit of 2026-11-14**, against the [requirements](std-fips-180-4-requirements.html),
on origin/main `8c7d47e`, after PR #53 (`8d58ad6`, SRS v0.4.7: the checkpoint
identity covers the SHA-256 of every weight byte range the build used) and PR #49
(`8c7d47e`, the first used ranges: checkpoint KV scales) merged. History: first
audit 2026-11-13 on `ccf02b3`, re-read on `b99720a` after PR #52.

**Method.** Read `rustinfer-artifact`'s `hash.rs` and every `Sha256` and `sha2` call
site on origin/main (`8c7d47e`), the workspace pin of `sha2`, and the tests that
check a digest; for the re-audit, the used-range path end to end:
`UsedRange` (`crates/rustinfer-artifact/src/metadata.rs:120-131`), its check on load
(`verify_range`, `:180-196`), the build's digest (`crates/rustinfer-frontend/src/kv_scales.rs:57-71`,
`read_range` `:197-214`) and Sluice's (`crates/rustinfer-sluice/src/checkpoint.rs:79-121`). The `sha2` crate's own source was not audited line by line: it is
the pinned dependency, and its output is checked against a published vector. Nothing
was run; the tests below are read.

| id | result | evidence |
|---|---|---|
| S1 length bound | **conforms** | every input is a byte slice or a tensor byte range; the largest realistic input, a whole shard header or tensor, is far below 2^61 bytes |
| S2 to S5 algorithm | **conforms** | `sha2::Sha256::digest` (`crates/rustinfer-artifact/src/hash.rs:37`), `sha2 = "=0.10.9"` (`Cargo.toml:55`). `crates/rustinfer-artifact/tests/identity.rs:155` `test_sha256_hex_round_trips` (`Verifies RI-ART-008`) checks `Sha256::of(b"abc")` against the published one-block value. `crates/rustinfer-artifact/tests/sha256_vectors.rs:54` (empty message), `:61` (NIST two-block 448-bit message, §6.2.2), `:69` (55, 56, 63 and 64 bytes, where the §5.1.1 padding moves to a second block) and `:82` (one million `a`), all `Verifies RI-ART-008`, check the rest. SHA256-1 closed |
| S6 digest form | **conforms** | 32 bytes in `Sha256::bytes` (`hash.rs:22-25`); printed as lowercase hex, most significant digit first (`hash.rs:41-50`), the §3.1 digit set; upper case is refused on reading (`hash.rs:54-73`, same test). `crates/rustinfer-artifact/tests/header.rs:87` `test_hash_field_is_sha256_of_every_byte_after_the_header` (`Verifies RI-ART-001`); `tests/refusals.rs:275` refuses one flipped payload byte (`Verifies RI-ART-003`) |
| S7 streamed digest | **conforms** | Sluice feeds each tensor to `sha2::Sha256::update` slice by slice (`crates/rustinfer-sluice/src/sluice.rs:265-280`). `crates/rustinfer-sluice/tests/verify.rs:23` `test_digests_are_the_sha256_of_each_needed_tensor` compares it with the one-shot `Sha256::of` for a tensor of 100 KiB and a small one; `verify.rs:51` detects one flipped byte. Both carry `Groundwork for RI-WST-005`, because the rest of that clause is not finished; the hashing itself is complete |
| S7 used-range digests | **conforms**, coverage gap (SHA256-2) | The build hashes each used range's bytes in one shot, `Sha256::of(&bytes)` (`crates/rustinfer-frontend/src/kv_scales.rs:62-67`); Sluice re-hashes the recorded range at load by `sha2::Sha256::update` over 64 KiB chunks (`hash_range`, `crates/rustinfer-sluice/src/checkpoint.rs:100-121`), after checking the range lies inside the file (`:85-93`), and `verify_range` compares the digests by file, tensor and range (`crates/rustinfer-artifact/src/metadata.rs:180-196`). The two agree for every range recorded today: the only used ranges are KV scales, which `locate` admits only as one-element bf16, fp16 or fp32 tensors (`kv_scales.rs:158-179`), whose header range is 2 or 4 bytes, and `read_range` reads `range.length.min(4)` bytes (`:204`), so the digest covers the whole recorded range. But that cap is silent: a used range over 4 bytes would be recorded with its full length and the digest of its first 4 bytes, and every load would then refuse the checkpoint. Sluice's chunk loop is exercised with one 4-byte chunk only. Tests: `test_kv_scale_ranges_are_recorded_in_the_identity` (`crates/rustinfer-frontend/tests/mxfp4_kv_fp8.rs:140`) compares each recorded digest with `Sha256::of` of exactly the range's file bytes; `test_unchanged_used_range_loads` (`crates/rustinfer-sluice/tests/used_ranges.rs:42`), `test_flipped_byte_in_a_used_range_is_refused_naming_the_tensor` (`:50`), `test_used_range_outside_the_file_is_refused` (`:71`); `test_verify_compares_used_range_digests` (`crates/rustinfer-artifact/tests/used_ranges.rs:75`); all `Verifies RI-ART-008` |
| S8 NIST validation | **not applicable** | no requirement asks for a validated module, and rustinfer claims none (see the [overview](std-fips-180-4.html)) |

**Result.** Every in-scope item conforms; state *works*. SHA256-1 was closed by
PR #52 (`b99720a`). The used-range digests added by PRs #53 and #49 conform for
every range the build records today; SHA256-2 is open for the silent 4-byte cap in
the build's read and the untested multi-chunk path at load.
