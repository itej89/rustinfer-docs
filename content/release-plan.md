---
title: Release plan
section: Overview
order: 6
summary: The four releases the SRS tags its requirements with, what each proves, and the fifteen issues of Release 1 in their implementation order.
---

# Release plan

Read from SRS §1.5 and the release tags on every requirement, the use-case to
release map in `docs/planning/use-cases.md`, and the Epic drafted in
`docs/planning/issues/01-epic-release-1.md` at commit `082df51`. The
requirement counts are from the [generated requirements page](ref-requirements.html),
counting each requirement under the first release it names.

| release | name in the SRS | requirements | what it proves (from the use-case map) |
|---|---|---|---|
| R1 | foundation | 90 | the AOT engine exists end to end on one GPU and on the CPU reference: UC-01, 02, 03, 04, 20 (slot), 21, 22, 23 |
| R2 | production serving | 44 | production single-node serving characteristics: UC-05 to UC-13 (TP), 24 |
| R3 | industry-standard feature set | 33 | parity with the TensorRT-LLM functions a serving stack needs: UC-13 (EP), 14, 15, 16, 17, 18 |
| R4 | beyond | 4 | scale-out and breadth: UC-19, Helios racks, multi-node, DPU-resident functions, mesh lowering |

The use-case document predates the R-tags and uses `v0.1`, `v0.2`, `v1.0`
and `later`; they map one to one onto R1 to R4.

## Release 1: what done looks like

The Epic's acceptance criteria, verbatim from the draft:

- A LLaMA-family HF checkpoint builds into a `.rie` for `cpu` and for `gfx950`.
- `inspect` describes it on a machine without a GPU.
- `run` generates tokens on the CPU reference and on an MI355X; outputs match.
- Every R1 generator is autotuned and validated against the CPU reference.
- CI is green: fmt, clippy, rustdoc, unsafe budget, deny, audit, 80 percent coverage.

The topology planner's interfaces exist in R1; its implementation is R2.

## Release 1 sequence

From the Epic. The numbers are Codeberg issue numbers; the Epic is #1.

```text
#2 scaffold
 └─ #3 Model IR ── #4 artifact ── #5 target+cpu ── #6 frontend
                   #7 Kernel IR ── #8 AMD lowering ── #9 generators+tuner
                                   (#3,#5,#9) ── #10 graph compiler ── #11 build/inspect
                                   #12 ROCm target ─┐
                                   (#10,#12) ── #13 executor ── #14 run
                                   #15 planner interfaces (after #3)
```

The per-issue table, with status, is on the [issue tracker](issues.html).

## What needs hardware

Two R1 issues cannot finish on a laptop. The autotuner and the catalog (#9)
need an MI300X or MI355X, and the ROCm target (#12) needs HIP; open issue
OI-008 records that a gfx950 host with vLLM and AITER is also the baseline
for the R2 and R3 performance targets (RI-NFR-003: 70 percent of vLLM's
output-token throughput in R2, 100 percent in R3; RI-NFR-006: 80 percent of
the best AITER GEMM per bucket by the end of R2). The resolution recorded is
to rent an MI355X node for R1 autotuning and the R2 acceptance run. No
RISC-V accelerator is on the bench (OI-003); the RISC-V backends stay
compile-tested stubs until one is.

## Versioning

The workspace version is `0.1.0`, declared once in `[workspace.package]`
(SWG-001 §11.3). `CHANGELOG.md` has one `[Unreleased]` entry and
`docs/api/CHANGELOG.md` one `[v0.1] — unreleased` entry; no tag exists.
