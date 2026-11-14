---
title: "FIPS 180-4 audit"
navtitle: Audit
section: Standards
group: "Data and integrity / FIPS 180-4"
order: 12
summary: The 2026-11-13 audit of rustinfer's SHA-256 against FIPS 180-4: the algorithm conforms through the pinned sha2 crate, checked by the NIST vectors since #52.
---

# FIPS 180-4 audit

**Audit of 2026-11-13**, against the [requirements](std-fips-180-4-requirements.html).

**Method.** Read `rustinfer-artifact`'s `hash.rs` and every `Sha256` and `sha2` call
site on origin/main (`b99720a`; first reading at `ccf02b3`), the workspace pin of `sha2`, and the tests that
check a digest. The `sha2` crate's own source was not audited line by line: it is
the pinned dependency, and its output is checked against a published vector. Nothing
was run; the tests below are read.

| id | result | evidence |
|---|---|---|
| S1 length bound | **conforms** | every input is a byte slice or a tensor byte range; the largest realistic input, a whole shard header or tensor, is far below 2^61 bytes |
| S2 to S5 algorithm | **conforms** | `sha2::Sha256::digest` (`crates/rustinfer-artifact/src/hash.rs:37`), `sha2 = "=0.10.9"` (`Cargo.toml:55`). `crates/rustinfer-artifact/tests/identity.rs:155` `test_sha256_hex_round_trips` (`Verifies RI-ART-008`) checks `Sha256::of(b"abc")` against the published one-block value. `crates/rustinfer-artifact/tests/sha256_vectors.rs:54` (empty message), `:61` (NIST two-block 448-bit message, §6.2.2), `:69` (55, 56, 63 and 64 bytes, where the §5.1.1 padding moves to a second block) and `:82` (one million `a`), all `Verifies RI-ART-008`, check the rest. SHA256-1 closed |
| S6 digest form | **conforms** | 32 bytes in `Sha256::bytes` (`hash.rs:22-25`); printed as lowercase hex, most significant digit first (`hash.rs:41-50`), the §3.1 digit set; upper case is refused on reading (`hash.rs:54-73`, same test). `crates/rustinfer-artifact/tests/header.rs:87` `test_hash_field_is_sha256_of_every_byte_after_the_header` (`Verifies RI-ART-001`); `tests/refusals.rs:275` refuses one flipped payload byte (`Verifies RI-ART-003`) |
| S7 streamed digest | **conforms** | Sluice feeds each tensor to `sha2::Sha256::update` slice by slice (`crates/rustinfer-sluice/src/sluice.rs:265-280`). `crates/rustinfer-sluice/tests/verify.rs:23` `test_digests_are_the_sha256_of_each_needed_tensor` compares it with the one-shot `Sha256::of` for a tensor of 100 KiB and a small one; `verify.rs:51` detects one flipped byte. Both carry `Groundwork for RI-WST-005`, because the rest of that clause is not finished; the hashing itself is complete |
| S8 NIST validation | **not applicable** | no requirement asks for a validated module, and rustinfer claims none (see the [overview](std-fips-180-4.html)) |

**Result.** Every in-scope item conforms; state *works*. The one test gap, SHA256-1,
was closed by PR #52 (`b99720a`); none is open.
