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

**Implementation:** `serde_json` 1.0.154 with default features only (`Cargo.toml:51`;
`cargo tree -e features` shows `default` and `std`, no `preserve_order`, no
`float_roundtrip`). On origin/main (`ccf02b3`):

- the Model IR's canonical writer and bounded reader,
  `crates/rustinfer-mir/src/json.rs:87-91` and `:122-134`, with non-finite reals
  refused before writing (`crates/rustinfer-mir/src/validate.rs:592`);
- the artifact's JSON sections, `crates/rustinfer-artifact/src/json.rs:88-98`
  (`to_canonical`) and `:101-116` (`from_canonical`: size bound, UTF-8 check,
  version field, typed parse);
- the inputs: `config.json` (`crates/rustinfer-frontend/src/lowering.rs:173-174`,
  `src/config.rs:92`) and the safetensors header
  (`crates/rustinfer-artifact/src/safetensors.rs:558`).

**Source:** `specs/data/rfc8259.txt` (IETF, *RFC 8259 (STD 90), The JavaScript
Object Notation (JSON) Data Interchange Format*, T. Bray, Ed., December 2017,
https://www.rfc-editor.org/rfc/rfc8259). Free.

| | |
|---|---|
| Pages | [requirements](std-rfc-8259-requirements.html) · [audit](std-rfc-8259-audit.html) · [tracker](std-rfc-8259-tracker.html) |
| Audited | 2026-11-13, by reading origin/main and its tests, and a round-trip probe of `serde_json` 1.0.154 |
| JSON text written and read | conforms (§2 to §10) |
| Canonical profile | **partial**: about one real in ten in [0, 10^6) does not read back to the same `f64` |
| Open gaps | 2 |
