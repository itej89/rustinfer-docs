---
title: "RFC 8259 requirements"
navtitle: Requirements
section: Standards
group: "Data and integrity / RFC 8259"
order: 21
summary: The MUST-level rules of RFC 8259 for JSON generators and parsers, and the canonical profile rustinfer builds on them.
---

# RFC 8259 requirements

Source: `specs/data/rfc8259.txt` (IETF, RFC 8259, December 2017). Scope from SRS
§1.4: JSON text, with the canonical form of RI-MIR-007 as a profile of it. The
RFC's MUST rules are listed first; its SHOULD and interoperability notes after them,
because the canonical profile turns some of them into rules of its own.

## MUST rules of the RFC

| id | section | requirement |
|---|---|---|
| J1 | §2 | "A JSON text is a serialized value": `JSON-text = ws value ws`; whitespace is space, tab, line feed and carriage return only. |
| J2 | §3 | "A JSON value MUST be an object, array, number, or string, or one of the following three literal names: false null true"; "The literal names MUST be lowercase." |
| J3 | §6 | The number grammar `[ minus ] int [ frac ] [ exp ]`; "Leading zeros are not allowed"; "Numeric values that cannot be represented in the grammar below (such as Infinity and NaN) are not permitted." |
| J4 | §7 | Inside a string, "the characters that MUST be escaped: quotation mark, reverse solidus, and the control characters (U+0000 through U+001F)". |
| J5 | §8.1 | "JSON text exchanged between systems that are not part of a closed ecosystem MUST be encoded using UTF-8"; "Implementations MUST NOT add a byte order mark (U+FEFF)"; a parser "MAY ignore" one. |
| J6 | §9 | "A JSON parser MUST accept all texts that conform to the JSON grammar." It "may set limits on the size of texts", "the maximum depth of nesting", "the range and precision of numbers" and "the length and character contents of strings". |
| J7 | §10 | A generator's output "MUST strictly conform to the JSON grammar." |

## SHOULD rules and interoperability notes

| id | section | note |
|---|---|---|
| J8 | §4 | "The names within an object SHOULD be unique"; with duplicates, receivers' behaviour "is unpredictable". |
| J9 | §6 | Integers in [-(2^53)+1, 2^53-1] are interoperable "in the sense that implementations will agree exactly on their numeric values"; precision beyond binary64 is not. |
| J10 | §8.2 | A lone surrogate escape such as `"\uDEAD"` is allowed by the grammar, with unpredictable results. |

## The canonical profile (RI-MIR-007, RI-GC-009)

rustinfer's own rules on top of the RFC, from the SRS, not the RFC:

| id | source | requirement |
|---|---|---|
| P1 | RI-MIR-007 | Keys sorted at every level, compact form (no insignificant whitespace). |
| P2 | RI-MIR-007 | "exact numerics ... without loss": a document round-trips to the same values, so every integer and every real reads back bit for bit. |
| P3 | RI-GC-009 | Identical inputs give byte-identical sections. |
