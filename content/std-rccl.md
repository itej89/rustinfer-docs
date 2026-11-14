---
title: "RCCL ROCm 7.2"
navtitle: Overview
section: Standards
group: "Runtime / RCCL ROCm 7.2"
order: 20
summary: RCCL collectives, mandatory from R2 for tensor parallelism on one node; nothing is required or built in R1.
---

# RCCL ROCm 7.2

**Scope (SRS §1.4, RCCL):** all-reduce, all-gather, reduce-scatter, all-to-all.
**Conformance:** mandatory R2. The requirements that cite it are RI-ROC-006
(collectives through RCCL, R2; rustinfer's own small-message all-reduce, R3),
RI-DIST-001 (tensor parallelism up to 8 GPUs, one process per rank, R2) and
RI-SEC-001 (RCCL is one of the two shared libraries rustinfer may load).

**Implementation:** none yet, and none is due. No crate on origin/main (`ccf02b3`)
references RCCL or NCCL. The Model IR reserves the `collective` operator for R2
(`crates/rustinfer-mir/tests/operators.rs:85`, a `Reserved RI-MIR-004 (R2)` test),
and the CPU reference refuses it as "is R2"
(`crates/rustinfer-target/src/cpu/ops.rs:196`).

**Source:** `specs/runtime/rccl-7.2.4-library-specification.html` and
`rccl-7.2.4-api-library.html` (AMD, *RCCL library specification*, RCCL 2.27.7
documentation for ROCm 7.2.4, 2026-05-29,
https://rocm.docs.amd.com/projects/rccl/en/docs-7.2.4/). The SRS pins ROCm 7.0 to 7.2.

| | |
|---|---|
| Pages | [requirements](std-rccl-requirements.html) · [audit](std-rccl-audit.html) · [tracker](std-rccl-tracker.html) |
| Audited | 2026-11-13, by reading origin/main and the RCCL 2.27.7 specification |
| R1 items | none |
| R2 items | 7, all later release |
| Open gaps | 0 (6 items recorded as later release R2; no issue yet) |
