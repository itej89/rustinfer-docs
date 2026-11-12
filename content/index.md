---
title: rustinfer
section: Overview
order: 1
summary: The inference engine for AMD Instinct and RISC-V accelerators, read from its tree: what it is meant to be, what exists on 2026-11-12, and where the work is tracked.
---

# rustinfer

rustinfer is a compiled inference engine for AMD Instinct GPUs and RISC-V
accelerators, written in Rust: the model is compiled once per target into a
semi-static artifact that is a cache, never an obligation. Its specification says the mission is to
be the engine the industry standardises on for those two families, by owning
the whole path from model file to machine code: a model is lowered into a
**Model IR**, compiled for one named target into an **engine artifact** whose
kernels rustinfer generates itself from a **Kernel IR**, and executed by a
runtime that makes no graph, kernel, layout or memory decision at inference
time. No kernel library, no vendor BLAS, no Python, no NVIDIA.

This site is a reading of the tree at commit `f039b4d` on `main`, the merge
of GitHub PR #21, first written on 2026-11-10, the day the project was specified and
scaffolded, and refreshed on 2026-11-11 and 2026-11-12. Everything on it was read from the source, the SRS, the ADRs and
the planning documents in `docs/`; nothing was run on a GPU. Where a page
describes behaviour that does not exist yet it says so and names the issue
that will add it.

## Where it stands

**Done** means the code is in the tree and exercised by a test. **In
progress** means a branch exists and is not merged. **Planned** means an
approved-for-draft requirement and an issue exist. **Not started** means
only the requirement exists. The numbers behind this table, issues
closed, pull requests, the latest CI run, tests and coverage, are on the
[progress](progress.html) page, generated from GitHub and the tree; the
steps in order are the [roadmap](roadmap.html).

| Area | State |
|---|---|
| Specification: SRS-RI-v0.1 at version 0.2, 186 requirements, 28 groups, release tags R1 to R4 | <span class="state-ok">done</span> — status Approved 2026-11-11, PR #16 merged into `main` 2026-11-12; the SRS's own status field stays *Draft* until a release revises the document, so the [requirements](ref-requirements.html) page derives each requirement's state from the tests that cite it and the Epic's checklist instead |
| Decisions: ADR-001 to ADR-006, ADR-008 | <span class="state-ok">done</span> — ADR-008 (hosting on GitHub, superseding ADR-004) on `main` since GitHub PR #19 merged 2026-11-12; ADR-007 (the MLIR and LLVM link) is not written yet, it belongs to #7 ([decisions](decisions.html)) |
| Workspace: 14 crates, dependency direction fixed, lints as design rules | <span class="state-ok">done</span> — PR #17 merged into `main` 2026-11-12 ([crates](ref-crates.html)) |
| `rustinfer-core`: constants, settings, structured errors, `key=value` logging, version manifest | <span class="state-ok">done</span> — PR #17 merged; tested ([design](design.html)) |
| The `rustinfer` command: six subcommands parsed, paths validated, one error line on failure | <span class="state-ok">done</span> — PR #17 merged; every subcommand answers `not_implemented` after validation until #11 and #14 ([getting started](getting-started.html)) |
| Model IR: `rustinfer-mir`, the typed graph with one weight set, named functions, KV groups, twenty operators, validator and canonical JSON | <span class="state-ok">done</span> — Codeberg PR #19 merged into `main` as 2d75c5d on 2026-11-12, issue #3 closed ([design](design.html)) |
| Artifact: `rustinfer-artifact`, the `.rie` header, section table, content hash, verifying reader and atomic writer | <span class="state-ok">done</span> — Codeberg PR #21 merged into `main` as 678b084 on 2026-11-12, issue #4 closed ([artifact](artifact.html)) |
| Targets: `rustinfer-target`, the `Target`, `Catalog`, `Device` and `Launcher` traits, the architecture registry, the CPU reference target with every R1 operator in `f32`, four stub backends | <span class="state-ok">done</span> — GitHub PR #21 merged into `main` as f039b4d on 2026-11-12, issue #5 closed; 527 workspace tests passed and 96.44 percent line coverage in the PR's final test run ([hardware](hardware.html), [design](design.html)) |
| Planner: `rustinfer-planner`, the topology model and its JSON, `Placement`, the `Planner` trait and the single-device planner | <span class="state-ok">done</span> — GitHub PR #20 merged into `main` as d886a3c on 2026-11-12, issue #15 closed; discovery and the cost-model planner answer `not_implemented` until Release 2 ([planner](planner.html)) |
| Frontend, Kernel IR, compilers, Sluice, runtime | <span class="state-no">not started</span> — issues #6 to #14 and #18; Sluice (#18), the frontend (#6) and the Kernel IR (#7) are being implemented since 2026-11-12 and appear on the tracker when their branches are pushed ([issues](issues.html)) |
| Any model running on any device | <span class="state-no">not started</span> ([supported models](supported-models.html)) |
| Documentation in the tree: six diagrams, entry points, observability, feature matrix, API changelog, the Model IR, artifact, topology and placement schemas in `docs/api/` | <span class="state-ok">done</span> — kept current by every merged PR, last by GitHub PRs #20 and #21 ([design diagrams](design-diagrams.html)) |

## Where things live

| What | Where |
|---|---|
| Repository | [`github.com/itej89/rustinfer`](https://github.com/itej89/rustinfer), private, since the move from Codeberg on 2026-11-12 (ADR-008); `main` at f039b4d holds the approved SRS v0.2, ADR-001 to ADR-006 and ADR-008, the fourteen-crate workspace, the Model IR, the artifact crate, the planner interfaces and the target abstraction with the CPU reference (Codeberg PRs #16, #17, #19 and #21 before the move; GitHub PRs #19, #20 and #21 after it, the numbers coincide by accident). This site: [`github.com/itej89/rustinfer-docs`](https://github.com/itej89/rustinfer-docs), published at <https://itej89.github.io/rustinfer-docs/> |
| Tracker | [GitHub issues](https://github.com/itej89/rustinfer/issues) #1 (Epic, Release 1) and #2 to #15 and #18, numbers kept from Codeberg, dependencies linked, milestone `R1 — foundation`; #2, #3, #4, #5 and #15 closed; PRs #16 (SRS), #17 (scaffold), #19 (Model IR) and #21 (artifact) merged on Codeberg before the move, GitHub PRs #19 (hosting), #20 (planner) and #21 (target) after it; CI on GitHub Actions from run 1 of 2026-11-12, run 8 green on `main` at f039b4d, the Codeberg runs 1 to 11 left behind ([issues](issues.html)) |
| Specification | `docs/SRS-RI-v0.1.md` |
| Decisions | `docs/adr/ADR-001` to `ADR-006` and `ADR-008`; ADR-007 is written by #7 |
| Planning | `docs/planning/`: the TensorRT-LLM feature inventory, 24 use cases, the device inventory, the issue drafts |
| Rules | `CONTRIBUTING.md`, SWG-001 v4.0 as adapted by ADR-001 and, since the move, ADR-008 (ADR-004 until 2026-11-12) |

## The shape it is built into

Three decisions produce everything else; they are set out in full under
[design](design.html).

**Three representations and nothing else between a model file and the
device.** The Model IR is a typed SSA graph with profile-bounded dynamic
dimensions that every frontend lowers to and every backend consumes. The
Kernel IR is a tile-level MLIR dialect with explicit layouts and no thread
identity, emitted by Rust generator functions. Of the three only the Model
IR is in the code today, as `rustinfer-mir` since Codeberg PR #19; the
launch form the Plan will be made of, `Launch` in `rustinfer-target`, exists
since GitHub PR #21, the Plan itself (#10) and the Kernel IR (#7) do not. The Plan is the static schedule
the executor runs verbatim. ADR-005 calls this Apple's arrangement applied to
data-centre inference.

**Every kernel is generated, autotuned and validated.** There is no kernel
library and no vendor BLAS. Generators emit Kernel IR; the kernel compiler
lowers it through MLIR to AMD code objects, through MLIR's `spirv` dialect for
Vulkan-class devices, and through rustinfer's own lowering to RISC-V vector and
mesh targets. No kernel enters the catalog without validation against the CPU
reference target. In the code since GitHub PR #21: the `Target` trait family,
the registry, the CPU reference with every R1 operator, and the catalog
selection that serves only an entry validated on the catalog's architecture;
every other target's catalog is empty.

**The artifact is a cache, and strict mode makes it a requirement.** `build`
writes a `.rie` file; `run` and `serve` build the same file on first load and
reuse it; `--require-prebuilt` refuses to build at start. ADR-006 records why
the mandatory build step of the TensorRT engine model was dropped and its
properties kept.

<ul class="cards">
<li><a href="roadmap.html"><span class="card-title">Roadmap</span><span class="card-note">The steps to Release 1 in order, dated as they close, with the defects met on the way.</span></a></li>
<li><a href="progress.html"><span class="card-title">Progress</span><span class="card-note">Issues closed, PRs, CI, requirements, tests, coverage: the roadmap's measure.</span></a></li>
<li><a href="design.html"><span class="card-title">Design</span><span class="card-note">The three representations, the crates, the error contract, logging, settings and constants.</span></a></li>
<li><a href="design-diagrams.html"><span class="card-title">Design diagrams</span><span class="card-note">The six UML diagrams the tree keeps, rendered as committed.</span></a></li>
<li><a href="features.html"><span class="card-title">Features</span><span class="card-note">Every feature with its release and its status today.</span></a></li>
<li><a href="supported-models.html"><span class="card-title">Supported models</span><span class="card-note">What will run in each release; nothing runs today.</span></a></li>
<li><a href="kernel-compiler.html"><span class="card-title">Kernel compiler</span><span class="card-note">Generators, the Kernel IR, the lowerings, the catalog and the autotuner.</span></a></li>
<li><a href="runtime.html"><span class="card-title">Runtime and serving</span><span class="card-note">Executor, Sluice, scheduler, KV cache, sampler; what R1 has and what follows.</span></a></li>
<li><a href="hardware.html"><span class="card-title">Hardware</span><span class="card-note">The targets and the AMD and RISC-V device landscape the planner must describe.</span></a></li>
<li><a href="build-steps.html"><span class="card-title">Build steps</span><span class="card-note">Toolchain, the cargo gates, the CI scripts, coverage.</span></a></li>
<li><a href="deployment.html"><span class="card-title">Deployment</span><span class="card-note">One binary, one artifact, strict mode; what is not there yet.</span></a></li>
<li><a href="issues.html"><span class="card-title">Issue tracker</span><span class="card-note">#1 to #18 with blockers, branches and status.</span></a></li>
<li><a href="decisions.html"><span class="card-title">Decisions</span><span class="card-note">The ADRs, the owner's decisions, and the conclusions this site had to retract.</span></a></li>
<li><a href="ref-requirements.html"><span class="card-title">Requirements</span><span class="card-note">All 186, generated from the SRS.</span></a></li>
</ul>

## Reading order

Start with the **roadmap** and its measure, **progress**, then **design** for the three representations and the rules the
compiler enforces, then the **diagrams**. **Features** and **supported
models** say what each release delivers and what exists today. **Compiler**
takes the graph compiler and the kernel compiler in turn; **Runtime** covers
the executor, Sluice, the artifact cache and the planner. **Hardware** lists the
targets and the devices. **Development** has the engineering rules, the build
and the deployment story. **Trackers** hold the issues, the open questions and
the decisions. **Reference** is generated from the tree: requirements,
constants, error codes and crates.
