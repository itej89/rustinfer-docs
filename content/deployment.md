---
title: Deployment
section: Development
order: 3
summary: How a release will be deployed as of 2026-11-10; one static binary, one artifact per model and target, strict mode for production starts, two environment variables and two exit codes; and what does not exist yet.
---

# Deployment

Read from `README.md`, `.env.example`, `docs/entry-points.md`,
`docs/api/CHANGELOG.md`, `Cargo.toml`, `ci.yml` and ADR-006 at commit
`e91e002`. **Nothing here has been deployed.** The steps are the ones the
tree's design commits to, with each step marked Done, In progress, Planned
with its issue, or Not started.

## No packaging exists

There is no container image, no Dockerfile, no package, no release tag and
no install script. The only packaged output is the `rustinfer` binary that
the CI `build` job uploads as a workflow artifact after the smoke test. The
PR template's deployment audit step is answered "N/A, deployment not yet
enabled" until one of those appears. The standard's deployment section
activates when a Dockerfile, a publishable package version or a release job
exists; none does.

## The steps

| step | command or setting | status |
|---|---|---|
| 1. Build the binary | `cargo build --release --workspace`; the release profile is `lto = "thin"`, `codegen-units = 1`; the output is `target/release/rustinfer`, one static binary with no runtime interpreter (ADR-001) | <span class="state-part">in progress</span> — builds and passes `--version` on the scaffold branch |
| 2. Produce an artifact in CI | `rustinfer build --model <dir> --target gfx950 --out model.rie`; runs on any host, no GPU needed; byte-identical for identical inputs (RI-GC-009); input hashes recorded (RI-SEC-004) | Planned R1, #11 (needs #3 to #10) |
| 3. Check it | `rustinfer inspect model.rie`, under one second, no device | Planned R1, #11 |
| 4. Ship binary and artifact to the node | the artifact built on one host loads on any host with the same architecture and HIP runtime major version (RI-NFR-017) | Planned R1, #14 |
| 5. Run in production with strict mode | `rustinfer run model.rie --require-prebuilt` (R1) or `rustinfer serve model.rie --require-prebuilt` (R3); a model directory is refused, no compile at start (ADR-006, RI-CLI-004) | the refusal: <span class="state-part">in progress</span>; `run`: Planned R1, #14; `serve`: Not started, R3 |
| 6. Or let the node build on first load | `rustinfer run <dir>` builds into `RUSTINFER_CACHE_DIR` and reuses; for development and for fleets that accept a minutes-long first load | Planned R1, #11 |
| 7. Observe | stderr `key=value` logs; from R2 Prometheus metrics; from R3 `/health` and `/metrics` | logs: <span class="state-part">in progress</span>; the rest Not started |

## Configuration

Every variable rustinfer reads is in `.env.example`, which is committed;
`.env` never is (SWG-001 §13.3).

| variable | values | default | reads |
|---|---|---|---|
| `RUSTINFER_LOG` | `error`, `warn`, `info`, `debug`, `trace` | `info` | the log level (RI-CLI-011) |
| `RUSTINFER_CACHE_DIR` | a directory | `$XDG_CACHE_HOME/rustinfer`, else `$HOME/.cache/rustinfer` | where first-load artifacts go (RI-CLI-003) |

No variable is required. Both are read once at start into typed settings; an
invalid level stops the process with `error=config component=core` before
any work. The server's YAML configuration with `--set` overrides is R3 and
undesigned beyond RI-CLI-009.

## Exit codes and the error line

| code | meaning | constant |
|---|---|---|
| 0 | success; `--help` and `--version` also exit 0 | |
| 1 | any failure reported as a structured error | `EXIT_CODE_FAILURE` |
| 2 | invalid command-line usage | `EXIT_CODE_USAGE` |

On failure the last line of stderr is `error=<code> component=<name>
detail="<text>"` and stdout is empty, so a supervisor or a script can parse
the failure without reading the log. The codes are on
[error codes](ref-error-codes.html). The entry-point registry records:
`build` and `inspect` have no side effects; `run`, `tune`, `bench` and
`serve` initialise a device; `build` is idempotent; `tune` appends catalog
entries and re-runs replace by key; there is no timeout, with `bench` and
`serve` bounded by their configuration.

## Multi-GPU and multi-node

Tensor parallelism on one node runs one process per rank with
environment-variable rendezvous and collectives through the target, all ranks
verifying a shared build id and world size at start (RI-DIST-001, -004, R2).
Multi-node and rack scale-up are R4. Not started.
