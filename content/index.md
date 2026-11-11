---
title: rustinfer
section: Overview
order: 1
summary: The inference engine for AMD Instinct and RISC-V accelerators, read from its tree: what it is meant to be, what exists on 2026-11-10, and where the work is tracked.
---

# rustinfer

rustinfer is an ahead-of-time inference engine for AMD Instinct GPUs and
RISC-V accelerators, written in Rust. Its specification says the mission is to
be the engine the industry standardises on for those two families, by owning
the whole path from model file to machine code: a model is lowered into a
**Model IR**, compiled for one named target into an **engine artifact** whose
kernels rustinfer generates itself from a **Kernel IR**, and executed by a
runtime that makes no graph, kernel, layout or memory decision at inference
time. No kernel library, no vendor BLAS, no Python, no NVIDIA.

This site is a reading of the tree at commit `082df51` on branch
`feat/2-project-scaffold`, first written on 2026-11-10, the day the project
was specified and scaffolded, and refreshed on 2026-11-11. Everything on it was read from the source, the SRS, the ADRs and
the planning documents in `docs/`; nothing was run on a GPU. Where a page
describes behaviour that does not exist yet it says so and names the issue
that will add it.

## Where it stands

**Done** means the code is in the tree and exercised by a test. **In
progress** means a branch exists and is not merged. **Planned** means an
approved-for-draft requirement and an issue exist. **Not started** means
only the requirement exists.

| Area | State |
|---|---|
| Specification: SRS-RI-v0.1, 171 requirements, 27 groups, release tags R1 to R4 | <span class="state-ok">done</span>, status Draft until approved ([requirements](ref-requirements.html)) |
| Decisions: ADR-001 to ADR-006 | <span class="state-ok">done</span> ([decisions](decisions.html)) |
| Workspace: 14 crates, dependency direction fixed, lints as design rules | <span class="state-part">in progress</span> — on `feat/2-project-scaffold`, PR #17 open since 2026-11-11 ([crates](ref-crates.html)) |
| `rustinfer-core`: constants, settings, structured errors, `key=value` logging, version manifest | <span class="state-part">in progress</span> — same branch; tested ([design](design.html)) |
| The `rustinfer` command: six subcommands parsed, paths validated, one error line on failure | <span class="state-part">in progress</span> — every subcommand answers `not_implemented` after validation ([getting started](getting-started.html)) |
| Model IR, artifact, targets, frontend, compilers, runtime, planner | <span class="state-no">not started</span> — issues #3 to #15 ([issues](issues.html)) |
| Any model running on any device | <span class="state-no">not started</span> ([supported models](supported-models.html)) |
| Documentation in the tree: six diagrams, entry points, observability, feature matrix, API changelog | <span class="state-part">in progress</span> — same branch ([design diagrams](design-diagrams.html)) |

## Where things live

| What | Where |
|---|---|
| Repository | `codeberg.org/itej89/rustinfer`, private; `main` holds the skeleton commit, `docs/1-srs-rustinfer` the SRS and ADRs, `feat/2-project-scaffold` the workspace |
| Tracker | Codeberg issues #1 (Epic, Release 1) and #2 to #15 with dependencies linked, milestone `R1 — foundation`; PRs #16 (SRS) and #17 (scaffold) open since 2026-11-11; Actions enabled with the first run queued ([issues](issues.html)) |
| Specification | `docs/SRS-RI-v0.1.md` |
| Decisions | `docs/adr/ADR-001` to `ADR-006` |
| Planning | `docs/planning/`: the TensorRT-LLM feature inventory, 24 use cases, the device inventory, the issue drafts |
| Rules | `CONTRIBUTING.md`, SWG-001 v4.0 as adapted by ADR-001 and ADR-004 |

## The shape it is built into

Three decisions produce everything else; they are set out in full under
[design](design.html).

**Three representations and nothing else between a model file and the
device.** The Model IR is a typed SSA graph with profile-bounded dynamic
dimensions that every frontend lowers to and every backend consumes. The
Kernel IR is a tile-level MLIR dialect with explicit layouts and no thread
identity, emitted by Rust generator functions. The Plan is the static schedule
the executor runs verbatim. ADR-005 calls this Apple's arrangement applied to
data-centre inference.

**Every kernel is generated, autotuned and validated.** There is no kernel
library and no vendor BLAS. Generators emit Kernel IR; the kernel compiler
lowers it through MLIR to AMD code objects, through MLIR's `spirv` dialect for
Vulkan-class devices, and through rustinfer's own lowering to RISC-V vector and
mesh targets. No kernel enters the catalog without validation against the CPU
reference target.

**The artifact is a cache, and strict mode makes it a requirement.** `build`
writes a `.rie` file; `run` and `serve` build the same file on first load and
reuse it; `--require-prebuilt` refuses to build at start. ADR-006 records why
the mandatory build step of the TensorRT engine model was dropped and its
properties kept.

<ul class="cards">
<li><a href="design.html"><span class="card-title">Design</span><span class="card-note">The three representations, the crates, the error contract, logging, settings and constants.</span></a></li>
<li><a href="design-diagrams.html"><span class="card-title">Design diagrams</span><span class="card-note">The six UML diagrams the tree keeps, rendered as committed.</span></a></li>
<li><a href="features.html"><span class="card-title">Features</span><span class="card-note">Every feature with its release and its status today.</span></a></li>
<li><a href="supported-models.html"><span class="card-title">Supported models</span><span class="card-note">What will run in each release; nothing runs today.</span></a></li>
<li><a href="kernel-compiler.html"><span class="card-title">Kernel compiler</span><span class="card-note">Generators, the Kernel IR, the lowerings, the catalog and the autotuner.</span></a></li>
<li><a href="runtime.html"><span class="card-title">Runtime and serving</span><span class="card-note">Executor, scheduler, KV cache, sampler; what R1 has and what follows.</span></a></li>
<li><a href="hardware.html"><span class="card-title">Hardware</span><span class="card-note">The targets and the AMD and RISC-V device landscape the planner must describe.</span></a></li>
<li><a href="build-steps.html"><span class="card-title">Build steps</span><span class="card-note">Toolchain, the cargo gates, the CI scripts, coverage.</span></a></li>
<li><a href="deployment.html"><span class="card-title">Deployment</span><span class="card-note">One binary, one artifact, strict mode; what is not there yet.</span></a></li>
<li><a href="issues.html"><span class="card-title">Issue tracker</span><span class="card-note">#1 to #15 with blockers, branches and status.</span></a></li>
<li><a href="decisions.html"><span class="card-title">Decisions</span><span class="card-note">The ADRs, the owner's decisions, and the conclusions this site had to retract.</span></a></li>
<li><a href="ref-requirements.html"><span class="card-title">Requirements</span><span class="card-note">All 171, generated from the SRS.</span></a></li>
</ul>

## Reading order

Start with **design** for the three representations and the rules the
compiler enforces, then the **diagrams**. **Features** and **supported
models** say what each release delivers and what exists today. **Compiler**
takes the graph compiler and the kernel compiler in turn; **Runtime** covers
the executor, the artifact cache and the planner. **Hardware** lists the
targets and the devices. **Development** has the engineering rules, the build
and the deployment story. **Trackers** hold the issues, the open questions and
the decisions. **Reference** is generated from the tree: requirements,
constants, error codes and crates.
