---
title: "RFC 8259"
navtitle: Overview
section: Standards
group: "Data and integrity / RFC 8259"
order: 20
summary: JSON text as rustinfer reads it (config.json, safetensors headers) and writes it (the canonical form of the Model IR and the artifact's JSON sections).
---

# RFC 8259

**Scope (SRS §1.4, RFC-8259):** JSON text; the canonical form of RI-MIR-007 is a
profile of it. **Conformance:** mandatory R1. The requirements that cite it are
RI-MIR-007 (canonical JSON: sorted keys, exact numerics), RI-GC-009 (byte-identical
sections), RI-ART-014 (every JSON section versioned), RI-FE-001 (`config.json`),
RI-SEC-003 (bounded parsing of untrusted JSON) and, from R3, RI-SRV-005 (malformed
request bodies).

**Implementation:** `serde_json` 1.0.154 with its default features and
`float_roundtrip` (`Cargo.toml:54`, since PR #52), no `preserve_order`. On origin/main
(`b99720a`):

- the Model IR's canonical writer and bounded reader,
  `crates/rustinfer-mir/src/json.rs:87-91` and `:122-134`, with non-finite reals
  refused before writing (`crates/rustinfer-mir/src/validate.rs:592`);
- the artifact's JSON sections, `crates/rustinfer-artifact/src/json.rs:88-98`
  (`to_canonical`) and `:101-116` (`from_canonical`: size bound, UTF-8 check,
  version field, typed parse);
- the inputs: `config.json` (`crates/rustinfer-frontend/src/lowering.rs:173-174`,
  `src/config.rs:92`) and the safetensors header, parsed by a reader that refuses a
  repeated key (`crates/rustinfer-artifact/src/safetensors.rs:577`,
  `src/unique_json.rs:24`).

**Source:** `specs/data/rfc8259.txt` (IETF, *RFC 8259 (STD 90), The JavaScript
Object Notation (JSON) Data Interchange Format*, T. Bray, Ed., December 2017,
https://www.rfc-editor.org/rfc/rfc8259). Free.

| | |
|---|---|
| Pages | [requirements](std-rfc-8259-requirements.html) · [audit](std-rfc-8259-audit.html) · [tracker](std-rfc-8259-tracker.html) |
| Audited | 2026-11-13, by reading origin/main and its tests, and a round-trip probe of `serde_json` 1.0.154; re-read at `b99720a` after PR #52 |
| JSON text written and read | conforms (§2 to §10) |
| Canonical profile | conforms: reals read back bit for bit since PR #52 (`float_roundtrip`) |
| Open gaps | 0 (JSON-1 and JSON-2 fixed in `b99720a`) |
