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
the one binary validates its arguments and answers `not_implemented`.

The [progress](progress.html) page is this roadmap's measure: every tracker
on this site counted by state, the [issues](issues.html) first, then the
[requirements](ref-requirements.html) by component, then the rest.

## 0. Specify — **done, 2026-11-10**

The TensorRT-LLM feature inventory, 24 use cases and the AMD and RISC-V
device inventory, then SRS-RI-v0.1 with 171 requirements in 27 groups,
every one tagged R1 to R4, and ADR-001 to ADR-006. The owner approved it on
2026-11-11 and PR #16 merged into `main` as 1c7a008, carrying v0.2. The Epic and the
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
steps will not fit a hosted runner at all.

**Three more were Codeberg's own rules.** Once the repository was public,
the hosted runners answered, and runs 3 to 6 each failed one step further
along: short action names resolve against `data.forgejo.org`, which mirrors
only `actions/*`; `cargo-deny` reads version-less workspace path
dependencies as wildcards; and `upload-artifact` v4 refuses any host but
github.com. Each got a one-line fix and a sentence in ADR-004 (`ac68ff1`,
`b252ea6`, `d380d0a`, `cc3e293`), and run 7 was green across lint,
security, test and build.

**Where it stands, 2026-11-11.** PR #17 merged into `main` as 33fadd0 after
PR #16, with CI green on run 8; issue #2 is closed. `main` now holds the
approved SRS, the six ADRs and the fourteen-crate workspace, and every later
branch has its base.

## 2. Model IR (#3)

The typed SSA graph every later step consumes: profile-bounded dynamic
dimensions, the R1 dtype set, the operator set, placement slots, a
validator that names the offending node, canonical JSON that round-trips
byte for byte, and its own version number ([design](design.html)). Blocked
on #2. Nothing else in Release 1 can start before it except the Kernel IR
chain.

## 3. Artifact (#4), target abstraction and CPU reference (#5), LLaMA frontend (#6)

Three steps that need only the Model IR and can run in parallel. The
`.rie` reader and writer with the bounded, hash-last protocol of ADR-002
([artifact](artifact.html)); the `Target` trait and the CPU reference that
is every other target's oracle, with the three RISC-V and SPIR-V stubs
failing at `catalog empty` ([hardware](hardware.html)); the LLaMA family
lowered from `config.json` and safetensors, refusing an unknown
`model_type` or a mismatched parameter by name
([supported models](supported-models.html)). The safetensors reader is open
issue OI-004.

## 4. Kernel IR and the MLIR link (#7), AMD lowering (#8)

The other chain, blocked only on #2. The tile-level dialect through
`melior`, LLVM and `lld` as libraries, and ADR-007 deciding how the pinned
LLVM is obtained (OI-009); then the `gpu` → `rocdl` → AMDGPU lowering with
MFMA, LDS and bounds-checked loads for gfx942 and gfx950
([kernel compiler](kernel-compiler.html)).

**The dependency that is easy to miss.** Linking LLVM will not fit a
ten-minute hosted runner, so step 4 needs a self-hosted Forgejo runner
before its CI can pass, decided together with ADR-007. That chain runs
backwards from the kernel compiler to a machine nobody would otherwise
provision, which is why ADR-004 names it now.

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

## 8. Planner interfaces (#15)

The topology model and the single-device placement that fills the Model
IR's slots, blocked only on #3 and off the critical path; its implementation
is Release 2 ([planner](planner.html)).

## What comes next

Release 2, production serving: in-flight batching, chunked prefill, the
overlap scheduler, prefix reuse on by default, HIP graphs, tensor
parallelism on one node, metrics and `bench`; 44 requirements, no issues
yet. Then Release 3, the industry-standard feature set (33 requirements)
and Release 4 (4). The [release plan](release-plan.html) has each.

## Dependencies, shortest path first

| Must happen | Before |
|---|---|
| ~~PR #16 merged~~ done 2026-11-11 | the SRS is approved; any requirement is implementable |
| ~~PR #17 merged (#2)~~ done 2026-11-11 | any branch has a base |
| Model IR (#3) | artifact, targets, frontend, graph compiler, planner |
| Kernel IR link (#7) and a self-hosted runner | any kernel compiles in CI |
| A gfx950 host (OI-008) | the catalog has a validated entry; `run` on a GPU |
| CPU reference (#5) | any kernel is validated |
| Graph compiler (#10) | `build` produces an artifact |
| Executor (#13) | `run` produces a token |

## What changed

Hand-maintained here, newest first; the generated pages never touch it.

| date | what |
|---|---|
| 2026-11-11 | The tracker created on Codeberg: Epic #1, issues #2 to #15 with dependencies linked, labels, milestone `R1 — foundation`. PR #16 (SRS, `docs/1-srs-rustinfer` → `main`) and PR #17 (scaffold, stacked on #16) opened. The post-coding gate for #2 passed with three findings fixed (`refactor(scaffold)`, `e91e002`). CI retargeted from `ubuntu-latest` to Codeberg's `codeberg-medium` runners with full-SHA pins, permissions and timeouts, after the first two runs were cancelled unanswered; ADR-004 updated. ADR-002 corrected to the SRS's section list. `LICENSE` added (`082df51`). This documentation site written and published locally, with its [progress](progress.html) page counted from the trackers. Repository made public so Codeberg's hosted runners serve it; runs 3 to 6 fixed one Codeberg rule each (ADR-004); run 7 green on `cc3e293`, PR #17 checklist steps 10d and 13e filled . Weights left the artifact (RI-ART-012) and Sluice (#18) became the weight streamer. SRS v0.2 after a review against vLLM V1, SGLang and Apple's stack: named functions over one weight set, KV groups, the cache key beyond tokens, device-resident request state, enumerated buckets with graph capture for any sub-plan, compression encodings in the IR; reserved interfaces in OI-012 |
| 2026-11-10 | The TensorRT-LLM feature inventory, the use cases and the device inventory written; SRS-RI-v0.1 written with 171 requirements; ADR-001 to ADR-006 accepted; the workspace scaffold built: 14 crates, `rustinfer-core`, the `rustinfer` command, CI, every mandatory file; 37 tests green, clippy and rustdoc clean |
