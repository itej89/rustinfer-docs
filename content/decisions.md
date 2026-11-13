---
title: Decisions and retracted conclusions
navtitle: Decisions
section: Trackers
order: 3
summary: ADR-001 to ADR-009 and the owner's decisions the SRS and ADRs record, each with its reason and date; the conclusions this site reached while reading and then had to retract.
---

# Decisions and retracted conclusions

A decision is recorded here when the tree states it: in an ADR, in the SRS
changelog or constraints, or in a planning document. The reason column is the
tree's, paraphrased. Most decisions below are dated 2026-11-10, the day the
project was specified; ADR-007, ADR-008 and ADR-009 and the owner's
decisions D-12 to D-15 are of 2026-11-12, D-16 and D-17 of 2026-11-13. Read
at commit `04a2a26`.

## Architecture decision records

| id | decision | reason | status |
|---|---|---|---|
| ADR-001 | Rust, stable, edition 2021, one workspace; SWG-001's Python and C++ rules mapped to `tracing`, `thiserror`, workspace lints, `cargo llvm-cov`, `cargo deny` and `cargo audit`; `unsafe` only in `ffi` modules with `// SAFETY:` and a CI count | memory safety at the FFI boundary with GPU runtimes, zero-cost abstractions on the inference path, one static binary | Decided 2026-11-10 |
| ADR-002 | One `.rie` file: fixed header with magic, version, target, producer, SHA-256 and a section table; small sections as canonical JSON; a weight manifest in place of weight bytes (amended 2026-11-11: the checkpoint is never copied, RI-ART-012); a reader that validates everything before exposing a byte; a writer that streams to a temp file, hashes last, `fsync`s and renames | the TensorRT engine's property of no inference-time decisions, plus inspectable without a GPU, integrity-checked, never half-written, memory-mappable, versioned | Decided 2026-11-10 |
| ADR-003 | One `Target` trait composed of `Catalog` (device-free), `Device` and `Launcher`; a backend is one crate, one registry entry, one lowering | the compiler must select kernels without a device, the runtime must launch them, and a RISC-V backend must be addable without touching compiler, planner or runtime | Decided 2026-11-10; revised the same day to remove kernel providers after ADR-005 |
| ADR-004 | Codeberg hosting with the standard's GitHub rules mapped to Forgejo; `.github/` paths kept; root `CODEOWNERS` symlink; `cargo audit` and `cargo outdated` in place of Renovate; Codeberg runner labels | Forgejo has the same concepts with different file locations and no enforced CODEOWNERS on the free tier | Decided 2026-11-10; runner labels added 2026-11-11; **superseded** by ADR-008 on 2026-11-12 |
| ADR-005 | Three representations (Model IR, Kernel IR, Plan) and no other interface; kernels as Rust generators lowered through MLIR to ROCDL and SPIR-V and through an own lowering to RISC-V; a fixed catalog plus one fuser; no kernel library, vendor BLAS or Python | a vendor library ties the engine to one vendor's cadence and leaves RISC-V without a path; Python reintroduces the host overhead the incumbents removed; Apple's stack shows the shape that scales across heterogeneous hardware | Decided 2026-11-10 |
| ADR-006 | The artifact is a cache: `build` writes it, `run` and `serve` build it on first load, `--require-prebuilt` forbids building; placement cached and pinnable the same way | TensorRT-LLM dropped its mandatory build in 1.2 and vLLM and SGLang compile on first load; keep the artifact's properties, not the obligation | Decided 2026-11-10 |
| ADR-007 | The pinned LLVM is **major 23, release line 23.1**, from `apt.llvm.org` (suite of the host's codename), bound through `melior` 0.29.1 and `mlir-sys` 230.0.2 at exact pins and linked statically; behind the Cargo feature `mlir` of `rustinfer-kc` (`kc` on the CLI), off by default so the workspace builds without LLVM; CI installs the packages with `scripts/ci/install_llvm.sh` (key fingerprint verified, exact version per codename) in `lint`, `msrv`, `test` and `build`, not `security`, inside the ten-minute job timeout on hosted runners, so no self-hosted runner; developers without sudo extract the same packages with `dpkg-deb -x` and set `MLIR_SYS_230_PREFIX` and `TABLEGEN_230_PREFIX`; the dialect defined in IRDL generated from the Rust operation table, no C++ built; `unsafe` allowed in `crates/rustinfer-kc/src/mlir/`, budget 0 to 5; one `KernelContext` per thread with MLIR multi-threading off; MSRV 1.89 for the feature's build dependencies. Resolves OI-009; amends ADR-001 (`unsafe`) and ADR-005 (how MLIR is linked) | the only option with no external process (RI-KC-008) that gives a dialect verifier, pass pipelines and LLVM IR translation from Rust; Ubuntu's MLIR is LLVM 18, which predates gfx950; release tarballs ship no MLIR; building LLVM in CI takes 30 to 90 minutes; `melior` maps one-to-one onto an LLVM major; a probe crate built in 16 s and lowered a kernel to LLVM IR in-process on the development host. LLVM 22 with `melior` 0.27.8 is the recorded fallback. Costs: `apt.llvm.org` keeps only its latest build, so the pin goes stale and must be bumped; test binaries of about 240 MB; 50 build-time crates. Still open: code-object emission with `lld` (#8), a hash-pinned package mirror, LLVM for RISC-V hosts (R3) | Decided 2026-11-12, accepted; on `main` since GitHub PR #25 (ad51bce) |
| ADR-008 | Hosting on GitHub: `github.com/itej89/rustinfer` is the only source of truth from 2026-11-12 and the Codeberg repository is retired by the owner, nothing pushed to it again; the tracker recreated so that issues #1 to #18 keep their numbers and the branch names and `Closes #N` keywords keep working; SWG-001's rules apply as written, with `.github/workflows/ci.yml` on hosted `ubuntu-latest` runners, `timeout-minutes: 10` per job, a top-level `permissions: contents: read` and a concurrency group that cancels a superseded run on the same ref, every action pinned `owner/repo@<sha>` with `upload-artifact` on the v4 line, `.github/CODEOWNERS` enforced by branch protection with the root symlink kept for tools, Dependabot available and enabled when the owner decides while `cargo audit` and `cargo deny` keep running; links and `Cargo.toml` point at GitHub; this site on GitHub Pages; whether #7's LLVM link still needs a larger or self-hosted runner goes to ADR-007 (it does not); supersedes ADR-004, which stays as the record of what Forgejo needed | Codeberg's terms amendment effective July 2026 bans repositories that consist mostly of code written by tools such as Claude, which rustinfer's does under the SWG-001 gates; the GitHub mirror already held an identical `main`; the standard was written for GitHub so every rule ADR-004 had to translate applies as written; another Forgejo or Gitea host or a self-hosted Forgejo would cost the same translation or operating work with no hosted CI of note. Costs the ADR records: the repository is private until the owner opens it and the history spans two hosts | Decided 2026-11-12, accepted; on `main` since GitHub PR #19 (9d448ce) |
| ADR-009 | A tensor's placement slot names a device index into the topology's devices, a memory-tier index t the device d can use (t is `devices[d].local_tier` or d is in `memory_tiers[t].reachable_from`, clarified 2026-11-13), and optionally a shard spec (`split` with axis, shard count and shard index, or `replicated`); a node's device slot stays a device index; both empty until the planner fills them; Model IR `ir_version` 2, whose reader accepts an all-empty version 1 document and refuses a filled version 1 slot as needing re-planning; the `placement` section records the same form under `placement_version` 2 and every JSON section carries its own version (RI-ART-014). The contract was fixed first by SRS v0.3; the code landed in GitHub PR #32 (#27) | a tier kind cannot tell eight GPUs' `hbm` or two sockets' `dram` apart, though the topology already indexes each tier, and cannot express a tensor-parallel shard or replica; the graph compiler and executor are about to read slots, and a change now costs one version bump while every shipped slot is empty, against a migration of every pinned artifact later. Rejected: a tier kind plus a device index (still no shard, two tiers of one kind indistinguishable), a free-form string key (untyped). Every index from a document is untrusted and checked against the topology | Decided 2026-11-12, accepted; on `main` since GitHub PR #28 (7913427); reachability clarified 2026-11-13; in the code since GitHub PR #32 (3df8c1b, 2026-11-13) |

## Decisions the owner made

Recorded in the SRS changelog, §1.2 and §2.5, and in the ADR contexts, from
the discussion that preceded the SRS. Each is a row the progress page counts
as decided; one is reopened only by a new ADR.

| id | decision | where recorded | status | reason given |
|---|---|---|---|---|
| D-1 | The mission is the industry-standard engine for AMD Instinct and RISC-V; NVIDIA is out of scope | SRS §1.2 | Decided 2026-11-10 | the goal is to own the whole path from model file to machine code on those two families |
| D-2 | No kernel library, no vendor BLAS, no Python, anywhere | SRS §1.2, §2.5; ADR-005 | Decided 2026-11-10 | the vendor's engine is not an industry standard; Python costs host time |
| D-3 | An own IR for RISC-V is acceptable | RI-KC-004 | Decided 2026-11-10 | no vendor kernel exists on RISC-V; the IR must be ours end to end |
| D-4 | Follow Apple's three-level model: Model IR as the single contract, a fixed kernel catalog plus a small fuser, portable IR finalised on the device, a planner across units | SRS §2.1; ADR-005 | Decided 2026-11-10 | it is the shape that scales across heterogeneous hardware |
| D-5 | MLIR is the route for the kernel compiler; MLIR and LLVM are linked, never shelled out to | ADR-005; RI-KC-008 | Decided 2026-11-10 | no toolchain dependency at build or load |
| D-6 | Keep the ahead-of-time engine but make the artifact a cache with a strict mode | ADR-006 | Decided 2026-11-10 | the lesson of TensorRT-LLM 1.2 |
| D-7 | Topology planner interfaces in Release 1, implementation in Release 2 | SRS changelog; RI-PLN | Decided 2026-11-10 | the R1 types must be shaped by the R2 job; the artifact format must not change for it |
| D-8 | High-concurrency API serving is the first-class workload; prefix reuse on by default | SRS §2.5, RI-SCH-003, RI-KVC-005 | Decided 2026-11-10 | defaults and the first benchmark follow the workload operators run |
| D-9 | The SRS is written with clean requirements before any component; SWG-001 applies in full | SRS §1.1, §2.5 | Decided 2026-11-10 | the standard's Step 0 |
| D-10 | Targets by architecture string, never by product name | RI-TGT-001 | Decided 2026-11-10 | product names are many-to-one |
| D-11 | Feature combinations not marked supported are refused, never attempted | RI-SEC-005, `docs/feature-matrix.md` | Decided 2026-11-10 | an untested pair is a wrong answer waiting |
| D-12 | The build-time input identity is the RI-ART-008 checkpoint identity (SHA-256 of `config.json`, each weight file's size and header hash); whole weight files are hashed only through `--verify-weights` | issue #27; SRS v0.3 RI-SEC-004 | Decided 2026-11-12 | hashing every byte of a 5 TB checkpoint at each build would dominate build time; size plus header hash detects a swapped or re-sharded file |
| D-13 | The placement slot names a device index and a tier index and may carry a shard spec; the Model IR version is bumped and the single-device planner emits the new form | issue #27; SRS v0.3 RI-MIR-005; ADR-009 | Decided 2026-11-12 | see ADR-009 |
| D-14 | The weight manifest gains an optional per-tensor digest, needed by `--verify-weights` | issue #27; SRS v0.3 RI-ART-005 | Decided 2026-11-12 | RI-WST-005 needs a reference value per tensor, so a rank verifies only the bytes it reads |
| D-15 | `llama`, `mistral`, `qwen2` and `qwen3` lower in R1, with Qwen3 QK norm tracked in #26 and the other R1 gaps refused by name | issue #27; SRS v0.3 RI-FE-001 | Decided 2026-11-12 | reconciles the SRS, which tagged only `llama` R1, with issue #6, which implemented four families |
| D-16 | A test cites a requirement with exactly one tag: `Verifies` only when the clause is fully implemented, `Groundwork for` while it is not, `Reserved` for a later-release refusal; a requirement is implemented only with a `Verifies` tag and no `Groundwork for` tag | issue #27; `docs/testing.md` (PR #29) | Decided 2026-11-13 | a bare citation counted a requirement as done when one test touched it; the tag says how much of the clause the code holds ([engineering rules](engineering-rules.html)) |
| D-17 | A placement's tier index must be one its device can use: the device's `local_tier` or a tier whose `reachable_from` lists the device | issue #27; SRS v0.3 RI-MIR-005 and ADR-009, clarified | Decided 2026-11-13 | "among that device's or the host's tiers" left reachable remote tiers undefined; the topology already records reachability |

## Reversals

None yet. The only revision is ADR-003's, on 2026-11-10, when ADR-005
removed the idea of pluggable kernel providers in favour of generators.

## Resolved since this site was first written

Discrepancies the first reading of 2026-11-10 found and the tree has since
closed; kept for one cycle so the next reader knows they were real.

| found | resolved |
|---|---|
| ADR-002 listed six sections (`plan`, `graph`, `profile`, `metadata`, `kernels`, `weights`) under older `RI-ENG` and `RI-CMP` ids while RI-ART-002 lists nine plus `lora_slots` | 2026-11-11: ADR-002 corrected on `docs/1-srs-rustinfer` to the nine R1 sections plus `lora_slots`, citing RI-ART, RI-GC and RI-PLN ids |
| No `LICENSE` file although the manifest and README said MIT | 2026-11-11: `LICENSE` (MIT) added at `082df51` |
| CI actions referenced by tag, no `timeout-minutes`, no `permissions` | 2026-11-11: full-SHA pins, `permissions: contents: read`, `timeout-minutes: 10`, Codeberg runner labels; recorded in ADR-004, the labels retired by ADR-008 |
| ADR-008 described here from its pull request while `main` at `678b084` still carried ADR-004's mapping | 2026-11-12: GitHub PR #19 merged as 9d448ce; the row above is now read from `docs/adr/ADR-008-hosting-on-github.md` |
| ADR-007 listed here as open, to be written by #7, with a self-hosted runner expected for the LLVM link | 2026-11-12: GitHub PR #25 merged as ad51bce with ADR-007 accepted; the hosted runners link LLVM 23 inside the job timeout, so no self-hosted runner is needed; OI-009 resolved |
| RI-FE-001 tagged only `llama` as R1 while issue #6 implemented four families | 2026-11-12: SRS v0.3 (GitHub PR #28) tags all four R1 with the gaps named |
| ADR-009 and the v0.3 artifact clauses specified but not in the code (`ir_version` 1, a tier kind per slot, unversioned JSON sections, pinned sections never parsed) | 2026-11-13: GitHub PRs #29, #30 and #32 (#27) put them in the code: artifact `format_version` 2 with a version per section, Model IR `ir_version` 2, `placement_version` 2, pinned placement checked at load |
| OI-013, implicit launch operands appended by the CPU launcher | 2026-11-13: GitHub PR #30 made them a column of the operator registry; OI-013 resolved |

## Retracted conclusions

Conclusions this site reached while reading and then disproved by reading
further. Kept so that the next reader does not reach them again.

| believed | disproved by |
|---|---|
| The scaffold branch is at `42e6c2d` | a post-coding refactor commit `e91e002` landed on the branch while this site was being written; the footer and the generators read the commit from git so this cannot recur |
| `--require-prebuilt` on a directory reports a dedicated error code | the CLI reports it under `invalid`; the `PrebuiltRequired` variant exists but maps to that code |
| The version manifest names the software `rustinfer` | it names the crate, `rustinfer-cli`, since the name comes from `CARGO_PKG_NAME` |
| The component diagram's edges are the Cargo dependencies today | every non-core crate depends only on `rustinfer-core` at `082df51`; the diagram's edges from the compilers, runtime and artifact to `mir`, `target` and `artifact` are added by the issues that need them |
