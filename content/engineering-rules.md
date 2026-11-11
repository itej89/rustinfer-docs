---
title: Engineering rules
section: Development
order: 1
summary: SWG-001 as the tree adopts it; the gates every change passes, the branch and issue conventions, the design rules and what enforces each, and the mandatory files the repository keeps.
---

# Engineering rules

Read from `CONTRIBUTING.md`, ADR-001, ADR-004, `Cargo.toml`, `clippy.toml`,
`.github/` and `scripts/ci/` at commit `082df51`. The standard is SWG-001,
Software Development Guidelines v4.0 of 2026-10-03, as adapted for Rust by
ADR-001 and for Codeberg by ADR-004; `CONTRIBUTING.md` says it is the
checklist and the standard and the ADRs are the authority.

## The gates

Every change, in order: the pre-coding gate, implementation test-first, the
post-coding gate, the PR gate. A PR without an SRS requirement, updated
diagrams, and tests that reference the requirement id is rejected. Branches
are named `{feat|fix|refactor|test|docs|ci|chore}/{issue}-{kebab-description}`,
nothing is committed to `main` directly, and PRs close their issue with
`Closes #N`. The SRS is written before the Epic and the Epic before the
issues (SWG-001 §6.1 Step 0), which is why the tracker numbers were fixed in
`docs/planning/issues/` before the tracker existed.

The PR template, `.github/PULL_REQUEST_TEMPLATE.md`, is the standard's
15-step merge-readiness checklist with evidence pasted per step: SRS and
design audit, coverage, performance, concurrency, security, exception and
logging audit, external boundary integrity, schema versioning, first test
run, rebase, integration tests, refactoring, linter, final test run,
artifact verification, deployment audit, and two reviewer sign-offs.

## Hosting on Codeberg

ADR-004 maps the standard's GitHub-specific rules: Forgejo issues, milestones
and labels with the same `Closes #N` workflow; the workflow stays at
`.github/workflows/ci.yml` because Forgejo Actions reads that path;
`.github/CODEOWNERS` is canonical with a root `CODEOWNERS` symlink so
Forgejo's reviewer suggestion finds it, with approvals enforced by branch
protection rather than the file; Renovate is unavailable on the free tier so
`cargo audit` and `cargo outdated` run in CI instead; repository secrets keep
their names; `runs-on: ubuntu-latest` becomes Codeberg's own runner label
`codeberg-medium`, with every job under its ten-minute limit and tools
installed as pinned prebuilt binaries, and the ADR notes that the issues
linking LLVM will need a self-hosted Forgejo runner (added 2026-11-11, see
[build steps](build-steps.html)). The GitHub mirror created the same day is
not a source of truth.

## Design rules and what enforces each

From `CONTRIBUTING.md`, verbatim in substance.

| rule | enforced by |
|---|---|
| One crate per component; dependencies point downward; the source tree mirrors the component diagram | Cargo refuses cycles; review against `docs/uml/component-diagram.md` |
| The public API is the `pub use` list of `lib.rs`; everything else crate-private | `missing_docs = deny` makes every public item a documented decision |
| One error enum per crate implementing `StructuredError`; no `unwrap`, `expect`, `panic`, `todo`, `unimplemented` in production code | workspace clippy lints, denied; `clippy.toml` allows `unwrap` and `expect` in tests |
| No `println` or `eprintln` outside the entry point's error path | `print_stdout`, `print_stderr` denied; `tracing` for everything else |
| Every domain string and threshold defined once in `rustinfer-core::config::constants` | review; the `configuration` skill checklist |
| Environment read once, at the boundary, into typed `Settings` | `Settings::from_env` is the only reader |
| Logging `key=value`, ISO-8601, level, component; configured once; version manifest first | `rustinfer-core::logging` and `manifest`; CLI integration tests |
| `unsafe` only in backend `ffi` modules and the MLIR binding layer, each block with `// SAFETY:`; the count may not grow without an ADR | `unsafe_code = deny` workspace-wide; `scripts/ci/check_unsafe_budget.sh` against `unsafe_budget.txt` (0) |
| Functions do one thing at one level of abstraction, at most 20 lines excluding docs; no boolean selector arguments; no negative conditionals; no magic numbers | review against SWG-001 §5 (G15, G25, G29, G30, G34) |
| Names: `snake_case` items, `PascalCase` types, `SCREAMING_SNAKE` constants; `is_`, `has_`, `can_` for booleans; no abbreviations outside ISA and domain terms (`tp`, `kv`, `rvv`) | review against SWG-001 §4 and the Rust API guidelines |
| Rustdoc on every public item: what, errors, panics, example where non-trivial | `missing_docs`, `missing_errors_doc`, `missing_panics_doc` denied |
| Tests `test_{unit}_{condition}_{outcome}`; unit tests under 100 ms; one assertion idea per test; boundary cases explicit | review; `cargo llvm-cov --fail-under-lines 80` in CI |
| Dependencies: exact pins in the workspace manifest, `Cargo.lock` committed, `cargo deny` and `cargo audit` clean, the `new-dep` skill for any addition | the CI `security` job |
| Feature pairs recorded in `docs/feature-matrix.md`; unlisted pairs refused in code | RI-SEC-005; review |
| Diagrams, `docs/entry-points.md`, `docs/api/CHANGELOG.md`, `docs/observability.md` updated in the same PR as the code | PR template §1; `scripts/ci/check_doc_freshness.py` |

## The mandatory files

What SWG-001 §1 requires and the scaffold branch carries:

| file | holds |
|---|---|
| `docs/SRS-RI-v0.1.md` | the specification, IEEE 830 format, `RI-{COMP}-{SEQ}` ids with priority, status, release and rationale |
| `docs/adr/ADR-001` to `ADR-006` | decisions with context, decision, alternatives and consequences |
| `docs/uml/*.md` | six diagrams with a freshness header (`diagram`, `component`, `last_updated`, `last_updated_by`, `pr`) |
| `docs/entry-points.md` | the registry: the command's trigger, invocation, env vars, reads, writes, side effects, idempotency, error behaviour, timeout, SRS reference; the library surfaces |
| `docs/observability.md` | tier assessment and signal inventory |
| `docs/feature-matrix.md` | the combination matrix |
| `docs/api/CHANGELOG.md`, `CHANGELOG.md` | external-interface changes marked **BREAKING** where so; Keep a Changelog for the rest |
| `.env.example` | every variable rustinfer reads, with placeholders; `.env` is never committed |
| `.github/workflows/ci.yml`, `CODEOWNERS`, `PULL_REQUEST_TEMPLATE.md` | the pipeline, ownership, the checklist |
| `README.md`, `CONTRIBUTING.md`, `LICENSE` (MIT, added 2026-11-11 at `082df51`) | |
| `scripts/ci/` | the four checks CI runs beyond cargo |

## How to contribute

Pick an issue from the [tracker](issues.html) whose blockers are closed,
branch from the base its draft names, write the tests that cite the
requirement ids first, implement until green, run the local checks on
[build steps](build-steps.html), then open the PR with the template filled.
Every rule above that says "review" is a reviewer's job; everything else
fails the build.
