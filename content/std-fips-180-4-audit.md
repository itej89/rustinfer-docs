---
title: "FIPS 180-4 audit"
navtitle: Audit
section: Standards
group: "Data and integrity / FIPS 180-4"
order: 12
summary: The audit of rustinfer's SHA-256 against FIPS 180-4, re-audited 2026-11-14 at 99c1ec7: the algorithm conforms through the pinned sha2 crate; the used-range digests conform, SHA256-2 closed by PR #57.
---

# FIPS 180-4 audit

**Re-audit of 2026-11-14 at `99c1ec7`**, against the [requirements](std-fips-180-4-requirements.html),
on origin/main after PR #57 (issue #51, merge `99c1ec7`: the build hashes exactly
the recorded used range, and Sluice's chunked digest is tested past one chunk). The
earlier re-audit that day was on `8c7d47e`, after PR #53 (`8d58ad6`, SRS v0.4.7: the checkpoint
identity covers the SHA-256 of every weight byte range the build used) and PR #49
(`8c7d47e`, the first used ranges: checkpoint KV scales) merged. History: first
audit 2026-11-13 on `ccf02b3`, re-read on `b99720a` after PR #52.

**Method.** Read `rustinfer-artifact`'s `hash.rs` and every `Sha256` and `sha2` call
site on origin/main (`8c7d47e`), the workspace pin of `sha2`, and the tests that
check a digest; for the re-audit, the used-range path end to end:
`UsedRange` (`crates/rustinfer-artifact/src/metadata.rs:120-131`), its check on load
(`verify_range`, `:180-196`), the build's digest (`crates/rustinfer-frontend/src/kv_scales.rs:57-71`,
`read_range` `:197-214`) and Sluice's (`crates/rustinfer-sluice/src/checkpoint.rs:79-121`);
on `99c1ec7`, the build's digest again (`used_ranges`, `crates/rustinfer-frontend/src/kv_scales.rs:61-75`;
`read_scale_bytes`, `:205-219`; `read_range`, `:223-240`) and the tests PR #57 added. The `sha2` crate's own source was not audited line by line: it is
the pinned dependency, and its output is checked against a published vector. Nothing
was run; the tests below are read.

| id | result | evidence |
|---|---|---|
| S1 length bound | **conforms** | every input is a byte slice or a tensor byte range; the largest realistic input, a whole shard header or tensor, is far below 2^61 bytes |
| S2 to S5 algorithm | **conforms** | `sha2::Sha256::digest` (`crates/rustinfer-artifact/src/hash.rs:37`), `sha2 = "=0.10.9"` (`Cargo.toml:55`). `crates/rustinfer-artifact/tests/identity.rs:155` `test_sha256_hex_round_trips` (`Verifies RI-ART-008`) checks `Sha256::of(b"abc")` against the published one-block value. `crates/rustinfer-artifact/tests/sha256_vectors.rs:54` (empty message), `:61` (NIST two-block 448-bit message, §6.2.2), `:69` (55, 56, 63 and 64 bytes, where the §5.1.1 padding moves to a second block) and `:82` (one million `a`), all `Verifies RI-ART-008`, check the rest. SHA256-1 closed |
| S6 digest form | **conforms** | 32 bytes in `Sha256::bytes` (`hash.rs:22-25`); printed as lowercase hex, most significant digit first (`hash.rs:41-50`), the §3.1 digit set; upper case is refused on reading (`hash.rs:54-73`, same test). `crates/rustinfer-artifact/tests/header.rs:87` `test_hash_field_is_sha256_of_every_byte_after_the_header` (`Verifies RI-ART-001`); `tests/refusals.rs:275` refuses one flipped payload byte (`Verifies RI-ART-003`) |
| S7 streamed digest | **conforms** | Sluice feeds each tensor to `sha2::Sha256::update` slice by slice (`crates/rustinfer-sluice/src/sluice.rs:265-280`). `crates/rustinfer-sluice/tests/verify.rs:23` `test_digests_are_the_sha256_of_each_needed_tensor` compares it with the one-shot `Sha256::of` for a tensor of 100 KiB and a small one; `verify.rs:51` detects one flipped byte. Both carry `Groundwork for RI-WST-005`, because the rest of that clause is not finished; the hashing itself is complete |
| S7 used-range digests | **conforms** (SHA256-2 fixed in `99c1ec7`) | The build hashes each used range's bytes in one shot, `Sha256::of(&bytes)` (`used_ranges`, `crates/rustinfer-frontend/src/kv_scales.rs:61-75`, digest at `:71`); the bytes are exactly the recorded range: `read_scale_bytes` refuses a KV scale range that is not one element of its dtype as `InvalidTensor` naming the tensor and `byte_range` (`:205-219`, check at `:207`), and `read_range` reads `range.length` bytes with no cap (`:223-240`), so a recorded range is never wider than the bytes hashed. Sluice re-hashes the recorded range at load by `sha2::Sha256::update` over 64 KiB chunks (`hash_range`, `crates/rustinfer-sluice/src/checkpoint.rs:102-124`), after checking the range lies inside the file (`:85-93`), and `verify_range` compares the digests by file, tensor and range (`crates/rustinfer-artifact/src/metadata.rs:180-196`). Tests: `test_used_ranges_hash_exactly_the_recorded_range` (`crates/rustinfer-frontend/src/kv_scales.rs:324`, `Verifies RI-ART-008`) checks each digest against `Sha256::of` of exactly its range and refuses a longer or shorter range; `test_kv_scale_range_other_than_its_element_size_is_refused` (`crates/rustinfer-frontend/tests/mxfp4_audit.rs:205`, `Groundwork for RI-KVC-008`); `test_one_changed_byte_anywhere_in_a_long_used_range_is_refused` (`crates/rustinfer-sluice/tests/used_ranges.rs:99`) loads a bf16 range of more than two chunks unchanged, so the chunked digest equals the one-pass one, and refuses one flipped byte at the first and last byte and either side of each chunk boundary; `test_used_range_longer_than_its_hashed_bytes_is_refused` (`:134`); `test_kv_scale_ranges_are_recorded_in_the_identity` (`crates/rustinfer-frontend/tests/mxfp4_kv_fp8.rs:140`); `test_unchanged_used_range_loads` (`crates/rustinfer-sluice/tests/used_ranges.rs:42`), `test_flipped_byte_in_a_used_range_is_refused_naming_the_tensor` (`:50`), `test_used_range_outside_the_file_is_refused` (`:148`); `test_verify_compares_used_range_digests` (`crates/rustinfer-artifact/tests/used_ranges.rs:75`); all `Verifies RI-ART-008` unless noted |
| S8 NIST validation | **not applicable** | no requirement asks for a validated module, and rustinfer claims none (see the [overview](std-fips-180-4.html)) |

**Result.** Every in-scope item conforms; state *works*. SHA256-1 was closed by
PR #52 (`b99720a`) and SHA256-2 by PR #57 (`99c1ec7`): the build now hashes exactly
the range it records and refuses a KV scale range wider than one element, and the
load's chunked digest is tested past two 64 KiB chunks. No gap is open.
