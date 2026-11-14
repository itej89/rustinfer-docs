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
`--target` through the registry, and each answers `not_implemented`. Eight
components have behaviour, all merged by 2026-11-12: the core, the Model IR,
the artifact, the planner interfaces, the target abstraction with the CPU
reference, Sluice, the LLaMA-family frontend and the Kernel IR with its
MLIR link. The tech-debt work of #27 merged on 2026-11-13 and closed it. On
the same day MXFP4 moved into Release 1 (SRS v0.4, ADR-010), and its first
three pieces merged: the dtypes and the conversion oracle (#34), the manifest
and Sluice (#39), the KV dtypes on the CPU reference (part of #37); the 25
mandatory standards were audited and the defects found on `main` fixed (#51,
PR #52). The AMD lowering (#8) is PR #44, waiting on GPU test #45; the graph
compiler (#10) waits on #9, which waits on #8.

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
compact) that round-trips byte for byte, under `ir_version` 2 since PR #32
(2026-11-13; an all-empty version 1 document still reads); and a bounded
three-phase reader. PR #19 merged into `main` as 2d75c5d on 2026-11-12 with
CI green on run 10; 201 workspace tests, 95.50 percent line coverage in the
PR's checklist. The schema is `docs/api/model-ir.md` in the tree and the
read path is sequence diagram §4 ([design diagrams](design-diagrams.html)).

Two readings the PR records rather than decides: the `Profile` is a type of
the crate but not part of the document, because ADR-002 stores it as its own
artifact section; and "quantized tensors carry an encoding" is enforced as
an encoding present exactly when the dtype is fp8.

## 3. Artifact (#4), target abstraction and CPU reference (#5), LLaMA frontend (#6) — **done, 2026-11-12**

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
issue #5 is closed ([design](design.html), [hardware](hardware.html)).

The LLaMA-family frontend (#6) merged into `main` as 84449e7 on 2026-11-12
(GitHub PR #24) and issue #6 is closed: `rustinfer-frontend` lowers
`llama`, `mistral`, `qwen2` and `qwen3` from `config.json`, the optional
shard index and the safetensors headers into a validated Model IR document,
the weight manifest and the checkpoint identity, reading no weight byte;
everything that differs between architectures sits behind the
crate-internal `Architecture` trait and its `model_type` registry; the
safetensors reader is in-tree Rust (OI-004), shared with Sluice in
`rustinfer-artifact` since PR #30. 86 frontend tests, 672 in the
workspace in the PR's checklist. What the Model IR cannot yet say is refused
by name: Qwen3 QK norm (#26), `llama3`, `yarn` and `dynamic` RoPE scaling
(#31, R2), sliding windows; mixed dtypes were lifted by PR #33 on 2026-11-13,
with a dtype expectation per tensor ([frontend](frontend.html)).

## 4. Kernel IR and the MLIR link (#7), AMD lowering (#8) — #7 **done, 2026-11-12**; #8 next

The Kernel IR (#7) merged into `main` as ad51bce on 2026-11-12 (GitHub PR
#25) and issue #7 is closed: the `kir` dialect as a Rust operation table
from which the IRDL MLIR loads is generated, the typed `KernelBuilder`, and
behind the `mlir` feature `KernelContext`, which verifies the text, lowers
it for the host and translates it to LLVM IR in-process, byte-identical
across contexts and threads. ADR-007 resolves OI-009: LLVM 23.1 from
`apt.llvm.org`, `melior` 0.29.1, a static link, the install script in CI,
and an extracted prefix for developers without sudo
([kernel compiler](kernel-compiler.html)). The workspace MSRV became 1.89;
718 workspace tests passed with all features in the PR's final run.

**The dependency that was easy to miss, settled.** Linking LLVM did not fit
Codeberg's ten-minute hosted runner, which is why ADR-004 named a
self-hosted runner early. On GitHub's hosted runners the install script and
the link stay inside the ten-minute job timeout, so ADR-007 needs no
self-hosted runner.

**Next: the AMD lowering (#8)**, unblocked since #7 closed: the `gpu` →
`rocdl` → AMDGPU lowering with MFMA, LDS and bounds-checked loads for gfx942
and gfx950, complete when the code objects assemble and disassemble as
expected on a host without a GPU. The PR #25 review moved one criterion here
from #7: a module compiled to a code object in-process through the LLVM C
API and `lld` as a library, byte-identical when built twice, with
`liblld-23-dev` added to the install script.

## 5. Generators, catalog and autotuner (#9)

The R1 generator set, the catalog with validated-hardware records, and
`rustinfer tune`. Blocked on #5 and #8, and on hardware: the autotuner runs
on an MI300X or MI355X, which is not on the bench (OI-008; the recorded
resolution is to rent an MI355X node). This is the first step that cannot
complete on a laptop.

## 6. Graph compiler (#10), then build and inspect (#11)

Where the two chains meet: the logged pass pipeline from Model IR to Plan
([graph compiler](graph-compiler.html)), blocked on #3, #5 and #9; #3 and
#5 are closed, so #10 waits on #9 alone, and #9 on #8. The graph compiler
consumes the version 2 placement slot of ADR-009 from its first commit; then
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
explained decisions) under `placement_version` 1 (2 since PR #32, a device,
tier and shard per tensor), the `Planner` trait,
`SingleDevicePlanner` refusing a model whose footprint at the profile's
`max` exceeds the device's local tier, and `place`, the one call the rest of
R1 makes; discovery and the cost-model planner answer `not_implemented`
until Release 2, as the owner decided ([planner](planner.html)). The schema
is `docs/api/topology.md` in the tree.

## 9. Sluice, the weight streamer (#18) — **done, 2026-11-12**

Blocked by #4 and #5, both closed on 2026-11-12, and blocking the executor
(#13). GitHub PR #23 merged into `main` as add4752 on 2026-11-12:
`rustinfer-sluice` verifies the checkpoint identity and every needed
tensor's header before reading a byte, reads exactly the rank's byte
ranges through a staging pool bounded by `RUSTINFER_STAGING_BYTES`, applies
the `identity`, `transpose` and `pad` transforms on the device, overlaps
reads, copies and transforms on three threads, and digests every needed
tensor for `--verify-weights` ([Sluice](sluice.html)). 57 crate tests, 587
in the workspace, 96.43 percent line coverage in the PR's run. Issue #18
closed on 2026-11-13.

## 10. Conformance and seams (#27) — **done, 2026-11-13**

The reviews of 2026-11-12 (a seam audit of six crates and a conformance
review of the 79 requirement ids cited on `main`) became change request
#27, landing as five pull requests. The first, the SRS v0.3 amendment
with ADR-009, merged as GitHub PR #28 (7913427) on 2026-11-12:
RI-SEC-004 cites the checkpoint identity, RI-MIR-005 makes the placement
slot a device index, a tier index and a shard spec under `ir_version` 2,
RI-ART-005 adds a per-tensor digest, RI-ART-014 gives every JSON section its
own version, RI-FE-001 tags all four families R1 with the gaps named, and
OI-013 puts implicit launch operands in the operator registry. The code
followed on 2026-11-13:

| PR | merged | what |
|---|---|---|
| #29 conformance | 35f0b3b | the twelve conformance defects, each test-first: graph replay honours host-sync marks, the one-line CLI usage error, `--out` writability, `llvm_version` and the host triple in the version manifest, KV-group geometry and `plan_version` 2 in the Plan, error naming, a required `kernel_ir`, Sluice's zero block counted in the staging budget, the CPU operator list, pinned sections parsed at load (`check_pinned`), and the repository-wide retag under the new `docs/testing.md` rule ([engineering rules](engineering-rules.html)) |
| #30 seams | 742c08f | artifact `format_version` 2 with a section table per version and a version in every JSON section; `BinaryFormat` in `rustinfer-core` and recorded per kernel; one shared safetensors reader in `rustinfer-artifact` for the frontend and Sluice; the manifest's optional digest; `KernelQuery` keyed on every operand dtype and the encoding; implicit operands as a registry column, resolving OI-013; no catch-all over operators ([artifact](artifact.html)) |
| #32 placement v2 | 3df8c1b | Model IR `ir_version` 2 with device, tier and shard per slot, `placement_version` 2, the single-device planner emitting the new form, and the pinned placement checked against the pinned topology, including the reachability rule the owner set on 2026-11-13 (ADR-009) ([planner](planner.html)) |
| #33 frontend dtypes | 04a2a26 | a dtype expectation per tensor and a dtype policy per architecture, so mixed fp8 and bf16 checkpoints can be declared ([frontend](frontend.html)) |

#27 closed when PR #33 merged. The `llama3`, `yarn` and `dynamic` RoPE
scaling it had listed moved to issue #31, because the SRS places it in R2.

## 11. MXFP4 in Release 1 (#34 to #39) — in progress

The owner moved MXFP4 into Release 1 on 2026-11-13, from pre-quantized
checkpoints, quantization at build and the KV cache (SRS v0.4, ADR-010,
GitHub PR #41, c5582da; the scale rule of OCP MX v1.1 §6.3 Equation 4
corrected by SRS v0.4.1, PR #43). By default every target dequantizes the
weights to bf16 in the kernel; `--activations mxfp8|mxfp4` opts into the
gfx950 scaled MFMA (OI-015, following vLLM). A hardware test is a `gpu-test`
issue the owner runs by hand (PR #40, 8fb46f3).

| issue | what | state |
|---|---|---|
| #34 | `fp4x2` and `ue8m0` dtypes, the `mx` encoding, the OCP conversion oracle in the CPU reference | done, PR #43 (b21ae62) |
| #39 | MXFP4 in the weight manifest and Sluice: packed weights streamed once with their scale tensors, `U8` headers | done, PR #47 (ccf02b3) |
| #37 | `--kv-dtype bf16\|fp8\|mxfp4`: Model IR KV-group encodings, Plan geometry with scale bytes (`plan_version` 3), the first-load cache key, and quantized KV write, read and paged attention on the CPU reference | CPU half done, PR #48 (e218b8a); the GPU kernels are #38 |
| #35 | the frontend imports Quark and compressed-tensors MXFP4 checkpoints (`quantization_config`) | in PR #49 |
| #36 | `build --precision mxfp4` by RTN | open, needs #10 |
| #38 | AMD lowering of MXFP4: in-kernel bf16 dequantization, opt-in gfx950 scaled MFMA, the GPU KV kernels | open, needs #8 (PR #44) and #9 |

## 12. Standards conformance (#51) — fixes merged 2026-11-13

SRS v0.4.2 (PR #46, e7dbdc6) cites the 21 external standards the
requirements depend on; v0.4.3 (PR #50, 48c2820) classes each §1.4 reference
`mandatory R<n>` with a scope, `process`, `informative` or `internal`, adds
OI-016 (the minimum Vulkan and SPIR-V version, open) and narrows OCP OFP8 to
saturating conversion only. The 25 mandatory standards were audited the same
day ([standards map](standards.html)); the defects on `main` went into issue
#51 and were fixed test-first by PR #52 (b99720a): `serde_json` with
`float_roundtrip`, the Transformers v5 `rope_parameters`, duplicate
safetensors keys refused, RFC 3339 field ranges, and tests for RFC 8259
escapes, the FIPS 180-4 vectors and the fp8 identities. #51 stays open for
its SRS items (RI-KC-004 against the LLVM row, the RVV numeric plan, the
serving citations, OI-016). PR #53, an SRS amendment that lets the build
read weights and binds the artifact to the byte ranges it used, is open.

## What comes next

Release 2, production serving: in-flight batching, chunked prefill, the
overlap scheduler, prefix reuse on by default, HIP graphs, tensor
parallelism on one node, metrics and `bench`; 41 requirements, no issues
yet. Then Release 3, the industry-standard feature set (33 requirements)
and Release 4 (4). The [release plan](release-plan.html) has each.

## Dependencies, shortest path first

| Must happen | Before |
|---|---|
| ~~PR #16 merged~~ done 2026-11-12 | the SRS is approved; any requirement is implementable |
| ~~PR #17 merged (#2)~~ done 2026-11-12 | any branch has a base |
| ~~Model IR (#3)~~ done 2026-11-12 (PR #19) | artifact, targets, frontend, graph compiler, planner |
| ~~Kernel IR link (#7) and ADR-007's runner decision~~ done 2026-11-12 (GitHub PR #25) | any kernel compiles in CI |
| AMD lowering (#8): PR #44, then GPU test #45 on MI300X and MI355X | a code object exists; #9 can start; the MXFP4 kernels (#38) |
| A gfx950 host (OI-008) | the catalog has a validated entry; `run` on a GPU |
| ~~CPU reference (#5)~~ done 2026-11-12 (GitHub PR #21) | any kernel is validated |
| ~~Planner interfaces (#15)~~ done 2026-11-12 (GitHub PR #20) | the Model IR's slots are filled; the artifact's `topology` and `placement` sections have a schema |
| ~~Sluice (#18)~~ done 2026-11-12 (GitHub PR #23) | the executor has weights in device memory |
| ~~Frontend (#6)~~ done 2026-11-12 (GitHub PR #24) | `build` has a Model IR and a weight manifest |
| ~~Placement v2 in the code (#27, ADR-009)~~ done 2026-11-13 (GitHub PR #32) | the graph compiler and the executor read slots |
| ~~MXFP4 dtypes and oracle (#34)~~ done 2026-11-13 (GitHub PR #43) | every MXFP4 issue has a reference to match bit for bit |
| ~~MXFP4 manifest and Sluice (#39)~~ done 2026-11-13 (GitHub PR #47) | packed weights reach the device with their scales |
| MXFP4 frontend (#35): PR #49 | Quark and compressed-tensors checkpoints build |
| Graph compiler (#10) | `build` produces an artifact |
| Executor (#13) | `run` produces a token |

## What changed

Hand-maintained here, newest first; the generated pages never touch it.

| date | what |
|---|---|
| 2026-11-13 | Later the same day on GitHub: PR #42 (b621fed, #26 closed) grouped rmsnorm, so Qwen3 QK norm lowers; PR #40 (8fb46f3) the `gpu-test` issue template; PR #41 (c5582da) SRS v0.4 and ADR-010, MXFP4 in Release 1, issues #34 to #39 opened; PR #43 (b21ae62, #34 closed) the MXFP4 dtypes, `mx` encoding and OCP conversion oracle, SRS v0.4.1; PR #46 (e7dbdc6) SRS v0.4.2 citing the external standards; PR #47 (ccf02b3, #39 closed) MXFP4 in the weight manifest and Sluice; PR #48 (e218b8a, part of #37) the KV dtypes bf16, fp8 and MXFP4 on the CPU reference with `--kv-dtype`; PR #50 (48c2820) SRS v0.4.3, the Conformance column of §1.4, OI-016, OCP OFP8 narrowed to saturating conversion; PR #52 (b99720a) the #51 standards fixes. Open: PR #44 (#8, waits on GPU test #45), PR #49 (#35), PR #53 (SRS: the build may read weights). This site: the 25 mandatory standards with their four pages each and the map, gaps closed by PRs #48, #50 and #52 marked fixed with their evidence, the generated pages from b99720a |
| 2026-11-13 | The #27 code merged into `main` on GitHub: PR #29 (35f0b3b) the conformance defects and `docs/testing.md`, the rule that a test tags a requirement `Verifies`, `Groundwork for` or `Reserved`; PR #30 (742c08f) the extension seams, artifact `format_version` 2 with per-section versions, `BinaryFormat`, the shared safetensors reader, OI-013 resolved; PR #32 (3df8c1b) placement v2, `ir_version` 2, the reachability rule, ADR-009 in the code; PR #33 (04a2a26) per-tensor frontend dtypes. Issues #18 and #27 closed; #31 (`llama3` RoPE scaling, R2) opened. A v0.4 SRS amendment moving MXFP4 to R1 is proposed, in review. This site refreshed: generated pages from 04a2a26, the requirement state derived from the test tags alone (39 implemented, 27 partial, 1 reserved only, 120 planned, where the earlier citation-and-Epic rule counted 69 implemented), the tag rule on the [engineering rules](engineering-rules.html) page |
| 2026-11-12 | Four more pull requests merged into `main` on GitHub late in the day: PR #23 (add4752), issue #18: `rustinfer-sluice`, the weight streamer; PR #24 (84449e7), issue #6 closed: `rustinfer-frontend` for `llama`, `mistral`, `qwen2` and `qwen3` behind the `Architecture` trait and registry; PR #25 (ad51bce), issue #7 closed: the `kir` dialect, `KernelBuilder` and the in-process MLIR/LLVM 23 link behind the `mlir` feature, ADR-007, MSRV 1.89, the `msrv` CI job and `scripts/ci/install_llvm.sh`; PR #28 (7913427): SRS v0.3 and ADR-009 from the seam audit and conformance review (#27). Issues #26 (Qwen3 QK norm) and #27 (tech debt) opened. This site refreshed: generated pages from 7913427, a new [frontend](frontend.html) page, Sluice and the kernel compiler described from the code, the v0.3 contract changes on the artifact and planner pages marked specified versus in the code, ADR-007 and ADR-009 from their files |
| 2026-11-12 | Three pull requests merged into `main` on GitHub in the evening: PR #19 (9d448ce) with ADR-008 and the CI retarget to `ubuntu-latest`, `upload-artifact` v4 and a concurrency group; PR #20 (d886a3c), issue #15: `rustinfer-planner` with the topology model, `Placement`, the `Planner` trait, `SingleDevicePlanner` and `place`, the `TOPOLOGY_*`, `PLACEMENT_*` and `PLANNER_*` constants, `docs/api/topology.md`; PR #21 (f039b4d), issue #5: `rustinfer-target` with the `Target`, `Catalog`, `Device` and `Launcher` traits, the `Registry`, the CPU reference target over every R1 operator in `f32`, the `numeric` conversions, the four backend stubs and the command's registry, `build` and `tune` resolving `--target` first; 527 workspace tests, 96.44 percent line coverage; CI runs 6 and 8 green on `main`. Issues #3, #4, #5 and #15 closed; Sluice (#18), the frontend (#6) and the Kernel IR (#7) started. This site refreshed: generated pages from f039b4d, the targets and the planner described from the code, ADR-008 from the file |
| 2026-11-12 | Moved from Codeberg to GitHub after Codeberg's terms change on AI-written code: the code at [`github.com/itej89/rustinfer`](https://github.com/itej89/rustinfer) (private), issues #1 to #18 recreated with their numbers and dependencies, the migrated PRs #16 and #17 recorded as issues #16 and #17, the Codeberg pull requests and Actions runs 1 to 11 kept on the [issue tracker](issues.html) as history, GitHub Actions run 1 on `main`; ADR-008 (hosting on GitHub, superseding ADR-004) and the CI retarget to `ubuntu-latest` with `upload-artifact` v4 in the hosting pull request. This site moved to [`github.com/itej89/rustinfer-docs`](https://github.com/itej89/rustinfer-docs) and GitHub Pages at <https://itej89.github.io/rustinfer-docs/>, its tracker page now read through `gh api`. Before the move, Codeberg PR #21 merged the `.rie` artifact crate (#4) as 678b084; generated pages from 678b084 |
| 2026-11-12 | PRs #16 and #17 merged into `main` (1c7a008, 33fadd0) shortly after midnight; CI run 9 green on `main`. Issue #3 implemented on `feat/3-model-ir`: the `rustinfer-mir` crate with the document, functions, KV groups, the operator registry, the validator, canonical JSON and the bounded reader, `serde` and `serde_json` added as pinned dependencies, the `MODEL_IR_*` constants in `rustinfer-core`, the JSON schema in `docs/api/model-ir.md`, sequence diagram §4 and the API changelog; CI run 10 green; PR #19 merged as 2d75c5d, issue #3 closed. 201 workspace tests, 95.50 percent line coverage. #4, #5 and #15 started. This site refreshed: generated pages from 2d75c5d, the Model IR described from the code on the design page |
| 2026-11-11 | The tracker created on Codeberg: Epic #1, issues #2 to #15 with dependencies linked, labels, milestone `R1 — foundation`. PR #16 (SRS, `docs/1-srs-rustinfer` → `main`) and PR #17 (scaffold, stacked on #16) opened. The post-coding gate for #2 passed with three findings fixed (`refactor(scaffold)`, `e91e002`). CI retargeted from `ubuntu-latest` to Codeberg's `codeberg-medium` runners with full-SHA pins, permissions and timeouts, after the first two runs were cancelled unanswered; ADR-004 updated. ADR-002 corrected to the SRS's section list. `LICENSE` added (`082df51`). This documentation site written and published locally, with its [progress](progress.html) page counted from the trackers. Repository made public so Codeberg's hosted runners serve it; runs 3 to 6 fixed one Codeberg rule each (ADR-004); run 7 green on `cc3e293`, PR #17 checklist steps 10d and 13e filled . Weights left the artifact (RI-ART-012) and Sluice (#18) became the weight streamer. SRS v0.2 after a review against vLLM V1, SGLang and Apple's stack: named functions over one weight set, KV groups, the cache key beyond tokens, device-resident request state, enumerated buckets with graph capture for any sub-plan, compression encodings in the IR; reserved interfaces in OI-012 |
| 2026-11-10 | The TensorRT-LLM feature inventory, the use cases and the device inventory written; SRS-RI-v0.1 written with 171 requirements; ADR-001 to ADR-006 accepted; the workspace scaffold built: 14 crates, `rustinfer-core`, the `rustinfer` command, CI, every mandatory file; 37 tests green, clippy and rustdoc clean |
