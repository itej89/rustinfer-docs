---
title: "RFC 8259 audit"
navtitle: Audit
section: Standards
group: "Data and integrity / RFC 8259"
order: 22
summary: The audit of rustinfer's JSON against RFC 8259, re-audited 2026-11-14 at 8c7d47e: the text and the canonical profile conform, the used ranges of metadata version 2 included.
---

# RFC 8259 audit

**Re-audit of 2026-11-14**, against the [requirements](std-rfc-8259-requirements.html),
on origin/main `8c7d47e`, after PR #53 (`8d58ad6`, SRS v0.4.7) and PR #49
(`8c7d47e`) added the checkpoint identity's `used_ranges` to the metadata section,
now `metadata_version` 2. History: first audit 2026-11-13 on `ccf02b3`; re-audited
the same day on `b99720a` after PR #52 (issue #51).

**Method.** Read the JSON writers and readers on origin/main (`b99720a`; first
reading at `ccf02b3`) and their tests; listed the `serde_json` features the workspace enables
(first reading: `default`, `std`; on `b99720a` the workspace pin adds
`float_roundtrip`, `Cargo.toml:54`); read
the relevant parts of `serde_json` 1.0.154's source (string escaping, surrogate
handling, byte order mark). One probe was run in a scratch crate against the same
`serde_json` 1.0.154 with default features: two million `f64` values written with
`to_string` and read back with `from_str`, comparing bits. The scratch crate's
`target/` was deleted afterwards. The re-audit read the PR #52 code and tests; nothing
was run.

| id | result | evidence |
|---|---|---|
| J1, J7 grammar of what is written | **conforms** | every writer prints through `serde_json::to_string` or `to_vec` (`crates/rustinfer-mir/src/json.rs:90`, `crates/rustinfer-artifact/src/json.rs:97`). Re-read by the same parser in `crates/rustinfer-mir/tests/json_roundtrip.rs:19` and `:27` (`Verifies RI-MIR-007`), and per section in `crates/rustinfer-artifact/tests/plan.rs:233`, `metadata.rs:47`, `catalog.rs:54` |
| J2 literals | **conforms** | `serde_json` prints `true`, `false`, `null` in lower case |
| J3 no NaN or Infinity | **conforms** | the Model IR is the only place reals occur; a non-finite real is refused before writing (`crates/rustinfer-mir/src/validate.rs:592`), `crates/rustinfer-mir/tests/graph_validation.rs:217` (`Verifies RI-MIR-006`). The artifact and planner sections hold no floating-point field |
| J4 string escaping | **conforms** | `serde_json`'s `format_escaped_str_contents` escapes `"`, `\` and U+0000 to U+001F. `crates/rustinfer-artifact/tests/json_strings.rs:58` writes all 32 control characters, `"`, `\`, `/`, DEL and non-ASCII in a section string and reads it back unchanged (`Verifies RI-ART-008`); `:76` refuses an unescaped control character, `:92` decodes every §7 escape and a surrogate pair, `:102` refuses a lone surrogate (`Verifies RI-SEC-003`). The tests use the artifact's metadata strings; the Model IR's names go through the same `serde_json` writer and reader. JSON-2 closed |
| J5 UTF-8, no BOM | **conforms** | writers produce Rust strings (UTF-8) and never a BOM. The section reader refuses non-UTF-8 (`crates/rustinfer-artifact/src/json.rs:107`), `crates/rustinfer-artifact/tests/boundary.rs:199` (`Verifies RI-SEC-003`). A leading BOM is an error in `serde_json`, which §8.1 allows |
| J6 parser accepts the grammar, within limits | **conforms** | `serde_json` parses the full grammar. The limits rustinfer adds are of the kinds §9 permits: text size (`json.rs:106`, `crates/rustinfer-mir/src/json.rs:123`), nesting depth (`serde_json`'s recursion limit), number range (out-of-range numbers are errors), string contents (a lone surrogate escape is refused, `serde_json` `LoneLeadingSurrogateInHexEscape`). Malformed JSON is refused naming the section, `crates/rustinfer-artifact/tests/boundary.rs:144` (`Verifies RI-SEC-003`) |
| J8 unique names | **conforms** (a SHOULD) | writers build maps, so they never repeat a name. The safetensors header reader refuses a repeated name, naming it (`crates/rustinfer-artifact/src/unique_json.rs:24`, called from `safetensors.rs:577`; `crates/rustinfer-artifact/tests/safetensors_duplicates.rs:37`). The Model IR and section readers still parse into a `serde_json::Value` first (`crates/rustinfer-mir/src/json.rs:124`, `crates/rustinfer-artifact/src/json.rs:111`), which keeps the last of repeated names; those inputs are rustinfer's own output, and the RFC leaves the behaviour open |
| J9 integers above 2^53 | note | sizes and offsets are `u64` and exact in `serde_json`; a reader that is not `serde_json` would round those above 2^53 (over 8 PiB), far beyond any checkpoint |
| P1 sorted keys, compact | **conforms** | `serde_json::Value` maps are B-tree maps without `preserve_order`; `crates/rustinfer-mir/tests/json_roundtrip.rs:37` (`Verifies RI-MIR-007`), `crates/rustinfer-mir/tests/functions.rs:146` |
| P2 exact numerics | **conforms** | integers are exact. Reals are written in shortest round-trip form and, since PR #52, read back correctly rounded: the workspace `serde_json` enables `float_roundtrip` (`Cargo.toml:54`). Before it, the first probe found 593,094 of 2,000,000 random bit patterns read back as a different `f64` (first case `394301.33835633675` read as `394301.3383563367`). `crates/rustinfer-mir/tests/json_roundtrip.rs:229` round-trips 100,000 seeded reals of every magnitude and sign, subnormals and edge cases, bit for bit; `:253` round-trips the probe's first failure through `Document::to_json` and `from_json` (both `Verifies RI-MIR-007`). JSON-1 closed |
| P3 byte-identical sections | **conforms** for serialisation | `crates/rustinfer-artifact/tests/roundtrip.rs:64` and `:75` (`Groundwork for RI-GC-009`: deterministic compilation itself is #10) |
| P4 used ranges in the metadata section | **conforms** | Since `8c7d47e` the checkpoint identity carries `used_ranges`, each `{file, tensor, byte_range: {offset, length}, sha256}` (`crates/rustinfer-artifact/src/metadata.rs:108-131`), every struct `deny_unknown_fields`, the digest as 64 lowercase hex digits (`crates/rustinfer-artifact/src/hash.rs:41-63`), offsets and lengths as exact `u64` integers (see J9). An empty list is omitted (`skip_serializing_if`, `metadata.rs:114-116`), so an artifact that used no weight byte writes the same identity text as before apart from the version; the section is `metadata_version` 2, and a reader accepts 1 and 2, version 1 read as no used ranges (`crates/rustinfer-core/src/config/constants.rs:96-100`, `crates/rustinfer-artifact/src/json.rs:60-65`). The ranges are bounded in count and string length and checked against the recorded file size after the typed parse (`check_used_ranges`, `metadata.rs:245-286`). `test_used_ranges_round_trip_in_metadata_version_2` (`crates/rustinfer-artifact/tests/used_ranges.rs:32`) writes, reads back equal and finds `"metadata_version":2` and `"used_ranges"` in the canonical text; `test_used_range_outside_its_file_is_refused_naming_the_tensor` (`:50`); both `Verifies RI-ART-008` |

**Result.** JSON text conforms to RFC 8259, and the canonical profile conforms since
PR #52 (`b99720a`) made reals exact on reading (P2) and pinned the escaping with tests
(J4). The used ranges of metadata version 2 (PRs #53 and #49) are written and read
through the same canonical path and conform (P4); state *works*. No gap is open.
