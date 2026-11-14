---
title: "RCCL ROCm 7.2 audit"
navtitle: Audit
section: Standards
group: "Runtime / RCCL ROCm 7.2"
order: 22
summary: The 2026-11-13 audit of RCCL use in rustinfer: nothing is required before R2 and nothing is built.
---

# RCCL ROCm 7.2 audit

**Audit of 2026-11-13**, against the [requirements](std-rccl-requirements.html).

**Method.** Searched origin/main (`ccf02b3`) for `rccl` and `nccl` in every crate
(no match), read the R1 handling of the `collective` operator, and read the RCCL
2.27.7 specification in `specs/runtime/`. Nothing was run.

| id | result | evidence |
|---|---|---|
| C1 unique id | **later release** (R2) | RI-DIST-001: environment-variable rendezvous must carry the id from one rank to the rest |
| C2 communicator | **later release** (R2) | RI-DIST-001; needs HIP device selection first ([HIP-1](std-hip-tracker.html)) |
| C3 all-reduce | **later release** (R2) | RI-ROC-006 |
| C4 all-gather | **later release** (R2) | RI-ROC-006 |
| C5 reduce-scatter | **later release** (R2) | RI-ROC-006 |
| C6 all-to-all | **later release** (R2) | RI-ROC-006; the distinct-buffer rule must hold in the planner's buffer assignment |
| C7 result codes | **later release** (R2) | RI-ROC-002 sets the pattern for HIP; the same is expected for RCCL |

What R1 does instead is refuse: `collective` is a reserved operator in the Model IR
(`crates/rustinfer-mir/tests/operators.rs:85`, `Reserved RI-MIR-004 (R2)`), and the
CPU reference has no kernel for it (`crates/rustinfer-target/src/cpu/ops.rs:196`).
That refusal is the correct R1 behaviour.

**Result.** Nothing required yet; state *later*.
