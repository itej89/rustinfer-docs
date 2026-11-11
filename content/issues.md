---
title: Issue tracker
section: Trackers
order: 1
summary: The Epic and the fourteen Release 1 issues on Codeberg with their titles, blockers, branches and status on 2026-11-10.
---

# Issue tracker

Read from `docs/planning/issues/*.md` at commit `082df51`, which drafted the
bodies before the Codeberg tracker was populated so that the numbers would
match the branch names (SWG-001 §6.1 Step 0). The issues were created on
Codeberg on 2026-11-10 in this order, under milestone `R1 — foundation`,
with labels `epic`, `feature` and `infra`; the "blocked by" relations are
recorded as issue dependencies there as well as in the bodies.

**In progress** means a branch exists and is not merged. **Not started**
means the issue exists and no branch does.

| # | title | blocked by | branch | status |
|---|---|---|---|---|
| 1 | Epic: rustinfer Release 1 — foundation | — | — | <span class="state-part">in progress</span> — one of fourteen tasks in progress |
| 2 | Project scaffold: workspace, core, CLI, CI, mandatory files | — | `feat/2-project-scaffold`, stacked on `docs/1-srs-rustinfer` | <span class="state-part">in progress</span> — implementation green, post-coding gate run, PR #17 open since 2026-11-11 |
| 3 | Model IR: typed SSA graph, shapes, dtypes, validation, JSON round-trip | #2 | `feat/3-model-ir` | <span class="state-no">not started</span> |
| 4 | Artifact format: `.rie` header, section table, hash, bounded reader, writer | #3 | `feat/4-artifact-format` | <span class="state-no">not started</span> |
| 5 | Target abstraction and CPU reference target | #3 | `feat/5-target-and-cpu-reference` | <span class="state-no">not started</span> |
| 6 | Frontend: LLaMA family from a Hugging Face checkpoint | #3 | `feat/6-frontend-llama` | <span class="state-no">not started</span> |
| 7 | Kernel IR dialect and the MLIR/LLVM link | #2 | `feat/7-kernel-ir-and-mlir-link` | <span class="state-no">not started</span> — writes ADR-007 (OI-009) |
| 8 | AMD lowering: gpu → rocdl → AMDGPU with MFMA and LDS | #7 | `feat/8-amd-lowering` | <span class="state-no">not started</span> |
| 9 | R1 kernel generators, catalog and autotuner (`tune` command) | #5, #8 | `feat/9-generators-and-autotuner` | <span class="state-no">not started</span> — needs an MI300X or MI355X (OI-008) |
| 10 | Graph compiler: pass pipeline from Model IR to Plan | #3, #5, #9 | `feat/10-graph-compiler` | <span class="state-no">not started</span> |
| 11 | `build` and `inspect` commands | #4, #6, #10 | `feat/11-build-and-inspect` | <span class="state-no">not started</span> |
| 12 | ROCm target: HIP binding behind one FFI module | #5 | `feat/12-rocm-target` | <span class="state-no">not started</span> — raises the unsafe budget by its `ffi` count |
| 13 | Executor: static batch, KV block pool, sampler | #10, #12 | `feat/13-executor-static-batch` | <span class="state-no">not started</span> |
| 14 | `run` command end to end | #11, #13 | `feat/14-run-command` | <span class="state-no">not started</span> — closes the Epic's acceptance criteria |
| 15 | Planner: topology model and placement interfaces | #3 | `feat/15-planner-interfaces` | <span class="state-no">not started</span> |

## What each issue carries

Every draft follows the same shape: a feature description, the SRS
requirement ids it implements, its blockers, acceptance criteria that name a
test each, and the task checklist of the gates (requirements identified,
diagrams updated, security review, concurrency review, tests written first,
implementation green, post-coding gate, PR with the checklist). The
requirement ids per issue are in the drafts and on the
[features](features.html) page; the sequence is on the
[release plan](release-plan.html).

## Branches on Codeberg

| branch | holds | state on 2026-11-11 |
|---|---|---|
| `main` | the skeleton commit | — |
| `docs/1-srs-rustinfer` | the SRS, ADR-001 to ADR-006, planning documents, issue drafts | pushed; PR #16 to `main` open (2026-11-11) |
| `feat/2-project-scaffold` | the workspace, core, command, CI, mandatory files, `LICENSE`; rebased on the docs branch; `082df51` | pushed; PR #17 open (2026-11-11) |

## Pull requests (2026-11-11)

| PR | branch | base | holds | state |
|---|---|---|---|---|
| #16 | `docs/1-srs-rustinfer` | `main` | the SRS, ADR-001 to ADR-006, planning documents, issue drafts | open |
| #17 | `feat/2-project-scaffold` | `docs/1-srs-rustinfer` (stacked on #16) | the scaffold of issue #2, at `082df51` | open |

Issues #1 to #15 exist on Codeberg with their dependencies linked and the
milestone `R1 — foundation` set. Actions is enabled and the first pipeline
run was queued the same day; its result is not yet recorded here.

Two things only the owner can do: approve the SRS (its status moves from
Draft to Approved when #16 is merged), and decide the fate of the GitHub
mirror that ADR-004 says is not a source of truth.
