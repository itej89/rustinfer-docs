---
title: Roadmap
section: Overview
order: 2
summary: The steps to Release 1 in dependency order, each marked done with its date when its issue closes, with what exists, what is blocked and on what, and the defects found on the way; measured by the progress page.
---

# Roadmap

The sequence, decided 2026-11-10 in the Epic (#1). Its logic is that the
first step fixes the rules and the dependency graph so every later step is
one crate's worth of work behind a gate, and that the two compiler chains
(the Model IR chain and the Kernel IR chain) can proceed side by side until
the graph compiler joins them.

Today a change means an issue, a branch named after it, tests that cite
requirement ids, the post-coding gate, and a pull request whose template is
the standard's 15-step checklist. Nothing runs a model; every subcommand of
the one binary validates its arguments, `build` and `tune` resolve their
`--target` through the registry, and each answers `not_implemented`. Five
components have behaviour, all merged by 2026-11-12: the core, the Model IR,
the artifact, the planner interfaces and the target abstraction with the CPU
reference.

The [progress](progress.html) page is this roadmap's measure: every tracker
on this site counted by state, the [issues](issues.html) first, then the
[requirements](ref-requirements.html) by component, then the rest.

## 0. Specify — **done, 2026-11-10**

The TensorRT-LLM feature inventory, 24 use cases and the AMD and RISC-V
device inventory, then SRS-RI-v0.1 with 171 requirements in 27 groups,
every one tagged R1 to R4, and ADR-001 to ADR-006. The owner approved it on
2026-11-11 and PR #16 merged into `main` as 1c7a008 on 2026-11-12, carrying
v0.2 with 186 requirements in 28 groups. The Epic and the
fourteen issue bodies were drafted in the tree before the tracker existed so
the numbers would match the branch names.

**One defect stood between here and there**: ADR-002, written before the
SRS was rewritten, still listed six artifact sections under retired `RI-ENG`
and `RI-CMP` ids while RI-ART-002 lists nine plus `lora_slots`. Found by the
first reading for this site on 2026-11-10; corrected on the docs branch on
2026-11-11.

## 1. Scaffold (#2) — **done, 2026-11-11**

Fourteen crates, one per box of the component diagram, dependencies
downward only and enforced by Cargo; `rustinfer-core` with constants
defined once, typed settings read once, the `StructuredError` contract and
ten error codes, `key=value` logging with ISO-8601 timestamps, and a version
manifest whose dependency versions come from `Cargo.lock` at build time; the
`rustinfer` command with its six subcommands parsed, paths canonicalised at
the boundary, `--require-prebuilt` refusing a directory, one error line on
stderr and exit codes 1 and 2; CI as lint → security → test → build; every
mandatory file ([design](design.html), [build steps](build-steps.html)).
40 tests, 89.15 percent line coverage, clippy pedantic and rustdoc clean,
zero `unsafe`.

**Three defects stood between the green build and the gate**, found by the
post-coding audit of 2026-11-11 and fixed in `e91e002`:

- Two functions were over the standard's 20-line rule: the command
  dispatcher at 54 body lines and the manifest builder at 27. Both were
  split, one function per subcommand.
- The calendar arithmetic that produces timestamps carried its day-count
  constants as bare literals; they are now named.
- `run` and `serve` duplicated the artifact-source check; it is one shared
  function.

**A fourth was in the pipeline, not the code.** The workflow asked for
`ubuntu-latest`, a label Codeberg's hosted runners never answer, so the
first two CI runs of 2026-11-11 sat unclaimed and were cancelled. Every job
now runs on `codeberg-medium` within its ten-minute limit, with the actions
pinned to full commit SHAs, `permissions: contents: read` and
`timeout-minutes: 10`, and the two tools the jobs install are prebuilt
binaries so they fit; ADR-004 records the labels and that the LLVM-linking
steps will not fit a hosted runner at all. Since the move to GitHub on
2026-11-12 (ADR-008) the jobs run on `ubuntu-latest` again, the label the
workflow first asked for ([build steps](build-steps.html)).

**Three more were Codeberg's own rules**, and they went with Codeberg. Once the repository was public,
the hosted runners answered, and runs 3 to 6 each failed one step further
along: short action names resolve against `data.forgejo.org`, which mirrors
only `actions/*`; `cargo-deny` reads version-less workspace path
dependencies as wildcards; and `upload-artifact` v4 refuses any host but
github.com. Each got a one-line fix and a sentence in ADR-004 (`ac68ff1`,
`b252ea6`, `d380d0a`, `cc3e293`), and run 7 was green across lint,
security, test and build.

**Where it stands.** PR #17 merged into `main` as 33fadd0 on 2026-11-12
after PR #16, with CI green on run 8 and on run 9 for `main`; issue #2 is
closed. `main` holds the approved SRS, the six ADRs and the fourteen-crate
workspace, and every later branch has its base.

## 2. Model IR (#3) — **done, 2026-11-12**

The typed SSA graph every later step consumes, as the crate `rustinfer-mir`
([design](design.html)): a `Document` holding one weight set as tensor
descriptors (name, dtype, shape, an encoding when quantized, a placement
slot) and never a weight byte; the named functions `prefill` and `decode`,
each a list of nodes in definition-before-use order; KV groups the attention
nodes name; the twenty operators of RI-MIR-004 in one static registry of
release, arity and dtype rules; a validator that refuses the first fault
naming the function, the node and the field; canonical JSON (sorted keys,
compact) that round-trips byte for byte under `ir_version` 1; and a bounded
three-phase reader. PR #19 merged into `main` as 2d75c5d on 2026-11-12 with
CI green on run 10; 201 workspace tests, 95.50 percent line coverage in the
PR's checklist. The schema is `docs/api/model-ir.md` in the tree and the
read path is sequence diagram §4 ([design diagrams](design-diagrams.html)).

Two readings the PR records rather than decides: the `Profile` is a type of
the crate but not part of the document, because ADR-002 stores it as its own
artifact section; and "quantized tensors carry an encoding" is enforced as
an encoding present exactly when the dtype is fp8.

## 3. Artifact (#4), target abstraction and CPU reference (#5), LLaMA frontend (#6) — #4 and #5 done 2026-11-12, #6 in progress

The artifact (#4) merged into `main` as 678b084 on 2026-11-12 (Codeberg PR
#21, the last before the move): the crate `rustinfer-artifact` with the
`.rie` header, the section table, the content hash, the verifying reader and
the atomic writer, and issue #4 is closed. The target abstraction (#5)
merged into `main` as f039b4d the same evening (GitHub PR #21, a different
pull request from the Codeberg one of that number): `rustinfer-target` with
the `Target`, `Catalog`, `Device` and `Launcher` traits, the `Registry`
resolving an architecture string and nothing else, the CPU reference target
with every R1 operator as `f32` functions, the `numeric` conversions for
bf16, fp16 and fp8, the four backend crates as stubs with an empty catalog
and no device, and the command's registry of six strings; 527 workspace
tests passed and 96.44 percent line coverage in the PR's final test run;
issue #5 is closed ([design](design.html), [hardware](hardware.html)). The
LLaMA frontend (#6) is being implemented since 2026-11-12; its branch
appears on the [issue tracker](issues.html) when pushed.

Three steps that need only the Model IR and can run in parallel. The
`.rie` reader and writer with the bounded, hash-last protocol of ADR-002
([artifact](artifact.html)); the `Target` trait and the CPU reference that
is every other target's oracle, with the three RISC-V and SPIR-V stubs
failing at `catalog empty` ([hardware](hardware.html)); the LLaMA family
lowered from `config.json` and safetensors, refusing an unknown
`model_type` or a mismatched parameter by name
([supported models](supported-models.html)). The safetensors reader is open
issue OI-004.

## 4. Kernel IR and the MLIR link (#7), AMD lowering (#8) — #7 in progress

The other chain, blocked only on #2; #7 is being implemented since
2026-11-12. The tile-level dialect through
`melior`, LLVM and `lld` as libraries, and ADR-007 deciding how the pinned
LLVM is obtained (OI-009); then the `gpu` → `rocdl` → AMDGPU lowering with
MFMA, LDS and bounds-checked loads for gfx942 and gfx950
([kernel compiler](kernel-compiler.html)).

**The dependency that is easy to miss.** Linking LLVM did not fit
Codeberg's ten-minute hosted runner, which is why ADR-004 named a
self-hosted runner early. GitHub's hosted runners have no such ceiling
(ADR-008); whether step 4 still needs a larger or self-hosted runner is
decided in ADR-007 together with how the pinned LLVM is obtained (OI-009).
That chain runs backwards from the kernel compiler to a machine nobody would
otherwise provision.

## 5. Generators, catalog and autotuner (#9)

The R1 generator set, the catalog with validated-hardware records, and
`rustinfer tune`. Blocked on #5 and #8, and on hardware: the autotuner runs
on an MI300X or MI355X, which is not on the bench (OI-008; the recorded
resolution is to rent an MI355X node). This is the first step that cannot
complete on a laptop.

## 6. Graph compiler (#10), then build and inspect (#11)

Where the two chains meet: the logged pass pipeline from Model IR to Plan
([graph compiler](graph-compiler.html)), blocked on #3, #5 and #9; then
`build` and `inspect` wired through frontend, compiler, kernel compiler and
artifact writer, with the cache-keyed first-load build of ADR-006
([artifact as cache](artifact-cache.html)), blocked on #4, #6 and #10.

## 7. ROCm target (#12), executor (#13), run (#14)

The HIP binding behind one `ffi` module, raising the unsafe budget from
zero by exactly its count, blocked on #5 and on hardware; the static-batch
executor with the O(1) KV block pool and the one-launch sampler, blocked on
#10 and #12 ([runtime](runtime.html)); and `run` end to end, blocked on #11
and #13, which closes the Epic's acceptance criteria: a LLaMA checkpoint
built for `cpu` and `gfx950`, inspected without a GPU, generating the same
tokens on the CPU reference and an MI355X, every generator autotuned and
validated, CI green.

## 8. Planner interfaces (#15) — **done, 2026-11-12**

The topology model and the single-device placement that fills the Model
IR's slots, unblocked since #3 closed and off the critical path. GitHub PR
#20 merged into `main` as d886a3c on 2026-11-12 and issue #15 is closed:
`rustinfer-planner` with `Topology` (devices, memory tiers, links, offload
engines) in and out of canonical JSON under `topology_version` 1,
`Placement` (a tier per tensor, a device per node path, the strategy and
explained decisions) under `placement_version` 1, the `Planner` trait,
`SingleDevicePlanner` refusing a model whose footprint at the profile's
`max` exceeds the device's local tier, and `place`, the one call the rest of
R1 makes; discovery and the cost-model planner answer `not_implemented`
until Release 2, as the owner decided ([planner](planner.html)). The schema
is `docs/api/topology.md` in the tree.

## 9. Sluice, the weight streamer (#18) — in progress

Blocked by #4 and #5, both closed on 2026-11-12, and blocking the executor
(#13): the byte-range reads from the checkpoint, the bounded staging
budget, the device-side layout transforms and the overlapped copy queues
that put every weight the rank needs into device memory from the artifact's
weight manifest ([Sluice](sluice.html)). Being implemented since
2026-11-12; its branch appears on the [issue tracker](issues.html) when
pushed.

## What comes next

Release 2, production serving: in-flight batching, chunked prefill, the
overlap scheduler, prefix reuse on by default, HIP graphs, tensor
parallelism on one node, metrics and `bench`; 44 requirements, no issues
yet. Then Release 3, the industry-standard feature set (33 requirements)
and Release 4 (4). The [release plan](release-plan.html) has each.

## Dependencies, shortest path first

| Must happen | Before |
|---|---|
| ~~PR #16 merged~~ done 2026-11-12 | the SRS is approved; any requirement is implementable |
| ~~PR #17 merged (#2)~~ done 2026-11-12 | any branch has a base |
| ~~Model IR (#3)~~ done 2026-11-12 (PR #19) | artifact, targets, frontend, graph compiler, planner |
| Kernel IR link (#7) and ADR-007's runner decision | any kernel compiles in CI |
| A gfx950 host (OI-008) | the catalog has a validated entry; `run` on a GPU |
| ~~CPU reference (#5)~~ done 2026-11-12 (GitHub PR #21) | any kernel is validated |
| ~~Planner interfaces (#15)~~ done 2026-11-12 (GitHub PR #20) | the Model IR's slots are filled; the artifact's `topology` and `placement` sections have a schema |
| Sluice (#18) | the executor has weights in device memory |
| Graph compiler (#10) | `build` produces an artifact |
| Executor (#13) | `run` produces a token |

## What changed

Hand-maintained here, newest first; the generated pages never touch it.

| date | what |
|---|---|
| 2026-11-12 | Three pull requests merged into `main` on GitHub in the evening: PR #19 (9d448ce) with ADR-008 and the CI retarget to `ubuntu-latest`, `upload-artifact` v4 and a concurrency group; PR #20 (d886a3c), issue #15: `rustinfer-planner` with the topology model, `Placement`, the `Planner` trait, `SingleDevicePlanner` and `place`, the `TOPOLOGY_*`, `PLACEMENT_*` and `PLANNER_*` constants, `docs/api/topology.md`; PR #21 (f039b4d), issue #5: `rustinfer-target` with the `Target`, `Catalog`, `Device` and `Launcher` traits, the `Registry`, the CPU reference target over every R1 operator in `f32`, the `numeric` conversions, the four backend stubs and the command's registry, `build` and `tune` resolving `--target` first; 527 workspace tests, 96.44 percent line coverage; CI runs 6 and 8 green on `main`. Issues #3, #4, #5 and #15 closed; Sluice (#18), the frontend (#6) and the Kernel IR (#7) started. This site refreshed: generated pages from f039b4d, the targets and the planner described from the code, ADR-008 from the file |
| 2026-11-12 | Moved from Codeberg to GitHub after Codeberg's terms change on AI-written code: the code at [`github.com/itej89/rustinfer`](https://github.com/itej89/rustinfer) (private), issues #1 to #18 recreated with their numbers and dependencies, the migrated PRs #16 and #17 recorded as issues #16 and #17, the Codeberg pull requests and Actions runs 1 to 11 kept on the [issue tracker](issues.html) as history, GitHub Actions run 1 on `main`; ADR-008 (hosting on GitHub, superseding ADR-004) and the CI retarget to `ubuntu-latest` with `upload-artifact` v4 in the hosting pull request. This site moved to [`github.com/itej89/rustinfer-docs`](https://github.com/itej89/rustinfer-docs) and GitHub Pages at <https://itej89.github.io/rustinfer-docs/>, its tracker page now read through `gh api`. Before the move, Codeberg PR #21 merged the `.rie` artifact crate (#4) as 678b084; generated pages from 678b084 |
| 2026-11-12 | PRs #16 and #17 merged into `main` (1c7a008, 33fadd0) shortly after midnight; CI run 9 green on `main`. Issue #3 implemented on `feat/3-model-ir`: the `rustinfer-mir` crate with the document, functions, KV groups, the operator registry, the validator, canonical JSON and the bounded reader, `serde` and `serde_json` added as pinned dependencies, the `MODEL_IR_*` constants in `rustinfer-core`, the JSON schema in `docs/api/model-ir.md`, sequence diagram §4 and the API changelog; CI run 10 green; PR #19 merged as 2d75c5d, issue #3 closed. 201 workspace tests, 95.50 percent line coverage. #4, #5 and #15 started. This site refreshed: generated pages from 2d75c5d, the Model IR described from the code on the design page |
| 2026-11-11 | The tracker created on Codeberg: Epic #1, issues #2 to #15 with dependencies linked, labels, milestone `R1 — foundation`. PR #16 (SRS, `docs/1-srs-rustinfer` → `main`) and PR #17 (scaffold, stacked on #16) opened. The post-coding gate for #2 passed with three findings fixed (`refactor(scaffold)`, `e91e002`). CI retargeted from `ubuntu-latest` to Codeberg's `codeberg-medium` runners with full-SHA pins, permissions and timeouts, after the first two runs were cancelled unanswered; ADR-004 updated. ADR-002 corrected to the SRS's section list. `LICENSE` added (`082df51`). This documentation site written and published locally, with its [progress](progress.html) page counted from the trackers. Repository made public so Codeberg's hosted runners serve it; runs 3 to 6 fixed one Codeberg rule each (ADR-004); run 7 green on `cc3e293`, PR #17 checklist steps 10d and 13e filled . Weights left the artifact (RI-ART-012) and Sluice (#18) became the weight streamer. SRS v0.2 after a review against vLLM V1, SGLang and Apple's stack: named functions over one weight set, KV groups, the cache key beyond tokens, device-resident request state, enumerated buckets with graph capture for any sub-plan, compression encodings in the IR; reserved interfaces in OI-012 |
| 2026-11-10 | The TensorRT-LLM feature inventory, the use cases and the device inventory written; SRS-RI-v0.1 written with 171 requirements; ADR-001 to ADR-006 accepted; the workspace scaffold built: 14 crates, `rustinfer-core`, the `rustinfer` command, CI, every mandatory file; 37 tests green, clippy and rustdoc clean |
