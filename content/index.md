---
title: rustinfer
section: Overview
order: 1
summary: The inference engine for AMD Instinct and RISC-V accelerators, read from its tree: what it is meant to be, what exists on 2026-11-14, and where the work is tracked.
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

This site is a reading of the tree at commit `8c7d47e` on `main`, the merge
of GitHub PR #49, first written on 2026-11-10, the day the project was specified and
scaffolded, and refreshed on 2026-11-11, 2026-11-12, 2026-11-13 and 2026-11-14. Everything on it was read from the source, the SRS, the ADRs and
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
| Specification: SRS-RI-v0.1 at version 0.4.8, 188 requirements, 28 groups, release tags R1 to R4 | <span class="state-ok">done</span> — v0.2 approved 2026-11-11 (PR #16); v0.3 from the seam audit and conformance review (#27, PR #28, 7913427) on 2026-11-12; on 2026-11-13 v0.3.1 (grouped rmsnorm, PR #42), v0.4 moving MXFP4 into Release 1 with ADR-010 (PR #41, c5582da), v0.4.1 the OCP MX scale rule (PR #43), v0.4.2 citing the external standards (PR #46, e7dbdc6) v0.4.3 the Conformance column of §1.4 with OI-016 and OCP OFP8 narrowed to saturating conversion (PR #50, 48c2820), v0.4.6 the OCP E5M2 dtype `fp8_e5m2` (PR #55, 6a18042), v0.4.7 letting the build read weights and binding the artifact to the ranges it used, with an ADR-002 amendment (PR #53, 8d58ad6), and v0.4.8 closing OI-014, Quark's nibble order (PR #49, 8c7d47e); v0.4.4 and v0.4.5 were reserved and not used. The [requirements](ref-requirements.html) page derives each requirement's state from the test tags of `docs/testing.md`: 39 implemented, 31 partial, 1 reserved only, 117 planned |
| Standards: the 25 that SRS §1.4 marks mandatory (15 from R1, 4 from R2, 6 from R3), each audited on 2026-11-13 and re-audited against `main` at b99720a, then at 8c7d47e on 2026-11-14 for the standards PRs #55, #53 and #49 touch | <span class="state-part">in part</span> — R1: 6 work (IEEE 754, FIPS 180-4, RFC 8259, ISO 8601, AMD Quark, compressed-tensors), 7 partly work, 2 are missing (AMDGPU code object V5, HIP); the R2 and R3 standards are not due yet. 32 gaps open, 31 of them R1, and 40 more recorded for a later release; 8 closed on 2026-11-13 by PR #52 (#51) and 7 on 2026-11-14 by PRs #55 (HFC-5) and #49 (QK-1 to QK-3, CT-1, CT-2, HFC-3); one found by the re-audit (SHA256-2, the build hashes at most 4 bytes of a used range); OCP OFP8's E5M2 audited item by item and conforming, its non-saturating mode out of scope by PR #50. The mandatory class comes from the Conformance column of §1.4 on `main` ([standards map](standards.html), [issues](issues.html#standards)) |
| Decisions: ADR-001 to ADR-010 | <span class="state-ok">done</span> — ADR-007 (LLVM 23 and the MLIR link, resolving OI-009) with GitHub PR #25, ADR-008 (hosting on GitHub) with PR #19, ADR-009 (placement names devices and tiers) with PR #28, all 2026-11-12; ADR-009's reachability rule clarified and its code merged (PR #32) on 2026-11-13; ADR-010 (MXFP4 in Release 1, OI-015 resolved following vLLM) with PR #41 on 2026-11-13; ADR-002 amended so the build may read weights and the identity covers the used ranges (PR #53); OI-014 resolved by PR #49; OI-016 (minimum Vulkan and SPIR-V version) open ([decisions](decisions.html)) |
| Workspace: 15 crates, dependency direction fixed, lints as design rules, MSRV 1.89 | <span class="state-ok">done</span> — PR #17 merged into `main` 2026-11-12; `rustinfer-sluice` added by PR #23, `rust-version` 1.89 with an `msrv` CI job by PR #25 ([crates](ref-crates.html)) |
| `rustinfer-core`: constants, settings, structured errors, `key=value` logging, version manifest | <span class="state-ok">done</span> — PR #17 merged; tested ([design](design.html)) |
| The `rustinfer` command: six subcommands parsed, paths validated, one error line on failure | <span class="state-ok">done</span> — PR #17 merged; every subcommand answers `not_implemented` after validation until #11 and #14; since PR #29 a usage error is the one structured line and `inspect`, `run`, `serve` and `bench` read an artifact argument at the boundary ([getting started](getting-started.html)) |
| Model IR: `rustinfer-mir`, the typed graph with one weight set, named functions, KV groups, twenty operators, validator and canonical JSON | <span class="state-ok">done</span> — Codeberg PR #19 merged into `main` as 2d75c5d on 2026-11-12, issue #3 closed; `ir_version` 2 with device, tier and shard placement (PR #32) and implicit operands as a registry column (PR #30, OI-013) on 2026-11-13; grouped rmsnorm (PR #42, #26), the MXFP4 dtypes `fp4x2` and `ue8m0` with the `mx` encoding (PR #43, #34) and KV-group encodings for fp8 and MXFP4 (PR #48) the same day; the OCP E5M2 dtype `fp8_e5m2`, taken only by `quantize` and `dequantize` (PR #55) ([design](design.html)) |
| Artifact: `rustinfer-artifact`, the `.rie` header, section table, content hash, verifying reader and atomic writer | <span class="state-ok">done</span> — Codeberg PR #21 merged into `main` as 678b084 on 2026-11-12, issue #4 closed; `format_version` 2 with a section table per version, a version in every JSON section, the kernels' `BinaryFormat` and the shared safetensors reader since PR #30 (2026-11-13); MXFP4 tensors with their scales in the weight manifest (PR #47), Plan KV geometry with scale bytes under `plan_version` 3 and the first-load cache key with the KV dtype (PR #48), and the #51 fixes: duplicate header keys refused and RFC 3339 timestamp ranges checked (PR #52); the used weight ranges with their SHA-256 in the checkpoint identity under `metadata_version` 2 (PR #49, SRS v0.4.7) ([artifact](artifact.html)) |
| Targets: `rustinfer-target`, the `Target`, `Catalog`, `Device` and `Launcher` traits, the architecture registry, the CPU reference target with every R1 operator in `f32`, four stub backends | <span class="state-ok">done</span> — GitHub PR #21 merged into `main` as f039b4d on 2026-11-12, issue #5 closed; 527 workspace tests passed and 96.44 percent line coverage in the PR's final test run; the OCP MX conversion oracle (PR #43) and bf16, fp8 and MXFP4 KV write, read and paged attention on the CPU reference (PR #48, part of #37) on 2026-11-13; the OCP E5M2 conversion, saturating, against an independent golden file (PR #55) ([hardware](hardware.html), [design](design.html)) |
| Planner: `rustinfer-planner`, the topology model and its JSON, `Placement`, the `Planner` trait and the single-device planner | <span class="state-ok">done</span> — GitHub PR #20 merged into `main` as d886a3c on 2026-11-12, issue #15 closed; discovery and the cost-model planner answer `not_implemented` until Release 2; placement v2 (device, tier, shard; `placement_version` 2; pinned placement checked at load) since PR #32 ([planner](planner.html)) |
| Sluice: `rustinfer-sluice`, the weight streamer: identity and header checks, byte-range reads, bounded staging, device-side transforms, three overlapped stages, `--verify-weights` digests | <span class="state-ok">done</span> — GitHub PR #23 merged into `main` as add4752 on 2026-11-12 (issue #18, closed 2026-11-13); the manifest's optional digest and the shared header reader since PR #30, digest recording waits on `build`; MXFP4 weights streamed packed, each scale tensor once, since PR #47 (#39 closed, 2026-11-13); every used range re-hashed at load and a mismatch refused naming the tensor (PR #49) ([Sluice](sluice.html)) |
| Frontend: `rustinfer-frontend`, `llama`, `mistral`, `qwen2` and `qwen3` from a Hugging Face directory to Model IR, weight manifest and checkpoint identity, behind the `Architecture` trait and its registry | <span class="state-ok">done</span> — GitHub PR #24 merged into `main` as 84449e7 on 2026-11-12, issue #6 closed; per-tensor dtype expectations since PR #33 (2026-11-13); Qwen3 QK norm lowers since PR #42 (#26 closed); the Transformers v5 `rope_parameters` read since PR #52; `llama3`/`yarn`/`dynamic` RoPE scaling (#31, R2), sliding windows and a `partial_rotary_factor` other than 1 (PR #55) refused by name in R1; Quark and compressed-tensors MXFP4 import, with checkpoint KV scales for `--kv-dtype fp8`, merged by PR #49 (8c7d47e, #35 closed 2026-11-14) ([frontend](frontend.html)) |
| Kernel IR: `rustinfer-kc`, the `kir` dialect, the typed `KernelBuilder`, the in-process MLIR/LLVM 23 link behind the `mlir` feature, host lowering to LLVM IR | <span class="state-ok">done</span> — GitHub PR #25 merged into `main` as ad51bce on 2026-11-12, issue #7 closed; 718 workspace tests passed with all features in the PR's final run ([kernel compiler](kernel-compiler.html)) |
| Conformance and seam fixes from the 2026-11-12 reviews (#27) | <span class="state-ok">done</span> — the SRS amendment (PR #28) and four pull requests merged on 2026-11-13: conformance defects (PR #29, with the test-tag rule of `docs/testing.md`), extension seams (PR #30), placement v2 (PR #32) and per-tensor frontend dtypes (PR #33); #27 closed 2026-11-13 ([issues](issues.html)) |
| AMD lowering (#8) | <span class="state-part">in progress</span> — PR #44, gfx942 and gfx950 code objects in-process with `lld`; merges only after GPU test #45 passes on MI300X and MI355X ([kernel compiler](kernel-compiler.html)) |
| MXFP4 in Release 1 (#34 to #39, ADR-010) | <span class="state-part">in progress</span> — #34 dtypes and oracle (PR #43) and #39 manifest and Sluice (PR #47) done; #37 KV dtypes on the CPU reference merged (PR #48), GPU kernels in #38; #35 frontend merged (PR #49, 2026-11-14); #36 precision pass and #38 AMD lowering open ([roadmap](roadmap.html)) |
| Generators and autotuner, graph compiler, build, ROCm target, executor, run | <span class="state-no">not started</span> — issues #9 to #14; #10 (graph compiler) is blocked by #9, which waits on #8 ([roadmap](roadmap.html)) |
| Any model running on any device | <span class="state-no">not started</span> ([supported models](supported-models.html)) |
| Documentation in the tree: six diagrams, entry points, observability, feature matrix, API changelog, the Model IR, Kernel IR, artifact, topology and placement schemas in `docs/api/` | <span class="state-ok">done</span> — kept current by every merged PR, last by GitHub PRs #55, #53 and #49, with `docs/testing.md` added by PR #29 and the `gpu-test` issue template by PR #40 ([design diagrams](design-diagrams.html)) |

## Where things live

| What | Where |
|---|---|
| Repository | [`github.com/itej89/rustinfer`](https://github.com/itej89/rustinfer), private, since the move from Codeberg on 2026-11-12 (ADR-008); `main` at 8c7d47e holds SRS v0.4.8, ADR-001 to ADR-010, the fifteen-crate workspace, the Model IR, the artifact crate, the planner interfaces, the target abstraction with the CPU reference, Sluice, the frontend, the Kernel IR with its MLIR link and the first MXFP4 pieces (Codeberg PRs #16, #17, #19 and #21 before the move; GitHub PRs #19 to #25, #28 to #30, #32, #33, #40 to #43, #46 to #50, #52, #53 and #55 after it, the numbers coincide by accident). This site: [`github.com/itej89/rustinfer-docs`](https://github.com/itej89/rustinfer-docs), published at <https://itej89.github.io/rustinfer-docs/> |
| Tracker | [GitHub issues](https://github.com/itej89/rustinfer/issues) #1 (Epic, Release 1), #2 to #15 and #18 (numbers kept from Codeberg), #26 (Qwen3 QK norm), #27 (tech debt), #31 (`llama3` RoPE, R2), #34 to #39 (MXFP4), #45 (GPU test of PR #44) and #51 (standards findings), dependencies linked, milestone `R1 — foundation`; #2 to #7, #15, #18, #26, #27, #34, #35 and #39 closed; GitHub PRs #19 (hosting), #20 (planner), #21 (target), #22 (README), #23 (Sluice), #24 (frontend), #25 (Kernel IR), #28 (SRS v0.3), #29 (conformance), #30 (seams), #32 (placement v2), #33 (frontend dtypes), #40 (GPU test template), #41 (SRS v0.4), #42 (grouped rmsnorm), #43 (MXFP4 oracle), #46 (SRS v0.4.2), #47 (MXFP4 Sluice), #48 (KV dtypes), #50 (SRS v0.4.3), #52 (standards fixes), #55 (E5M2, SRS v0.4.6), #53 (SRS v0.4.7) and #49 (MXFP4 import, SRS v0.4.8) merged; #44 and #56 open; CI on GitHub Actions, run 92 on `main` at 8c7d47e passed ([issues](issues.html)) |
| Specification | `docs/SRS-RI-v0.1.md` |
| Decisions | `docs/adr/ADR-001` to `ADR-010` |
| Planning | `docs/planning/`: the TensorRT-LLM feature inventory, 24 use cases, the device inventory, the issue drafts |
| Rules | `CONTRIBUTING.md`, SWG-001 v4.0 as adapted by ADR-001 and, since the move, ADR-008 (ADR-004 until 2026-11-12) |

## The shape it is built into

Three decisions produce everything else; they are set out in full under
[design](design.html).

**Three representations and nothing else between a model file and the
device.** The Model IR is a typed SSA graph with profile-bounded dynamic
dimensions that every frontend lowers to and every backend consumes. The
Kernel IR is a tile-level MLIR dialect with explicit layouts and no thread
identity, emitted by Rust generator functions. Two of the three are in the
code: the Model IR as `rustinfer-mir` since Codeberg PR #19, and the Kernel
IR as the `kir` dialect of `rustinfer-kc` since GitHub PR #25; the launch
form the Plan will be made of, `Launch` in `rustinfer-target`, exists since
GitHub PR #21, the Plan itself (#10) does not. The Plan is the static schedule
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
<li><a href="architecture-diagram.html"><span class="card-title">Architecture diagram</span><span class="card-note">rustinfer in the C4 model, context to code, with the layers, the standards, build-then-run and the deployment; every chip derived.</span></a></li>
<li><a href="design-diagrams.html"><span class="card-title">Design diagrams</span><span class="card-note">The six UML diagrams the tree keeps, drawn as cards and numbered steps from their source.</span></a></li>
<li><a href="features.html"><span class="card-title">Features</span><span class="card-note">Every feature with its release and its status today.</span></a></li>
<li><a href="supported-models.html"><span class="card-title">Supported models</span><span class="card-note">What will run in each release; nothing runs today.</span></a></li>
<li><a href="frontend.html"><span class="card-title">Frontend</span><span class="card-note">The LLaMA family into Model IR; the Architecture seam; the R1 gaps.</span></a></li>
<li><a href="kernel-compiler.html"><span class="card-title">Kernel compiler</span><span class="card-note">Generators, the Kernel IR, the lowerings, the catalog and the autotuner.</span></a></li>
<li><a href="runtime.html"><span class="card-title">Runtime and serving</span><span class="card-note">Executor, Sluice, scheduler, KV cache, sampler; what R1 has and what follows.</span></a></li>
<li><a href="hardware.html"><span class="card-title">Hardware</span><span class="card-note">The targets and the AMD and RISC-V device landscape the planner must describe.</span></a></li>
<li><a href="build-steps.html"><span class="card-title">Build steps</span><span class="card-note">Toolchain, the cargo gates, the CI scripts, coverage.</span></a></li>
<li><a href="deployment.html"><span class="card-title">Deployment</span><span class="card-note">One binary, one artifact, strict mode; what is not there yet.</span></a></li>
<li><a href="issues.html"><span class="card-title">Issue tracker</span><span class="card-note">#1 to #28 with blockers, branches and status.</span></a></li>
<li><a href="decisions.html"><span class="card-title">Decisions</span><span class="card-note">The ADRs, the owner's decisions, and the conclusions this site had to retract.</span></a></li>
<li><a href="ref-requirements.html"><span class="card-title">Requirements</span><span class="card-note">All 187, generated from the SRS.</span></a></li>
</ul>

## Reading order

Start with the **roadmap** and its measure, **progress**, then **design** for the three representations and the rules the
compiler enforces, then the **architecture diagram** and the **design diagrams**. **Features** and **supported
models** say what each release delivers and what exists today. **Compiler**
takes the frontend, the graph compiler and the kernel compiler in turn; **Runtime** covers
the executor, Sluice, the artifact cache and the planner. **Hardware** lists the
targets and the devices. **Development** has the engineering rules, the build
and the deployment story. **Trackers** hold the issues, the open questions and
the decisions. **Reference** is generated from the tree: requirements,
constants, error codes and crates.
