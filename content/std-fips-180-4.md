---
title: "FIPS 180-4"
navtitle: Overview
section: Standards
group: "Data and integrity / FIPS 180-4"
order: 10
summary: SHA-256 as the Secure Hash Standard defines it, used for the artifact hash, the checkpoint identity and the per-tensor weight digests.
---

# FIPS 180-4

**Scope (SRS §1.4, FIPS-180-4):** SHA-256 only. **Conformance:** mandatory R1. The
requirements that cite it are RI-ART-001 (the artifact header's hash of every
following byte), RI-ART-005 (the optional per-tensor digest), RI-ART-008 and
RI-SEC-004 (the checkpoint identity: `config.json` and every safetensors header) and
RI-WST-005 (Sluice's `--verify-weights`).

**Implementation:** SHA-256 is not written by rustinfer. It comes from the RustCrypto
`sha2` crate, pinned exactly (`Cargo.toml:52`, `sha2 = "=0.10.9"`), behind one type,
`rustinfer_artifact::Sha256` (`crates/rustinfer-artifact/src/hash.rs:20-64`):
`Sha256::of` hashes a byte slice (`hash.rs:35-39`) and the digest is carried in JSON
as 64 lowercase hex digits (`hash.rs:41-63`). Call sites on origin/main (`ccf02b3`):
the writer and reader of the artifact hash (`writer.rs:110`, `reader.rs:288`), the
safetensors header identity (`safetensors.rs:275`, `metadata.rs:109-114`), the
`config.json` hash (`crates/rustinfer-frontend/src/lowering.rs:127`,
`crates/rustinfer-sluice/src/checkpoint.rs:72`) and Sluice's streamed per-tensor
digest, which feeds `sha2::Sha256` chunk by chunk
(`crates/rustinfer-sluice/src/sluice.rs:265-280`).

**Source:** `specs/data/fips-180-4.pdf` (NIST, *FIPS PUB 180-4, Secure Hash Standard
(SHS)*, August 2015, doi:10.6028/NIST.FIPS.180-4,
https://csrc.nist.gov/pubs/fips/180-4/upd1/final). Free.

| | |
|---|---|
| Pages | [requirements](std-fips-180-4-requirements.html) · [audit](std-fips-180-4-audit.html) · [tracker](std-fips-180-4-tracker.html) |
| Audited | 2026-11-13, by reading origin/main and its tests against FIPS 180-4 |
| Algorithm (§5, §6.2) | conforms, through `sha2` 0.10.9; checked by the one-block "abc" vector |
| Digest form (§3.1, §6.2.2) | conforms: 256 bits, lowercase hex |
| Open gaps | 1: the known-answer tests cover one block only |

rustinfer does not claim FIPS validation. The standard's announcement says "Only
algorithm implementations that are validated by NIST will be considered as complying
with this standard" (item 8); `sha2` is not a validated module, and nothing in the
SRS asks for one. The claim is the algorithm and its output, nothing more.
