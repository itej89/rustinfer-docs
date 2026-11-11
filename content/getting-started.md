---
title: Getting started
section: Overview
order: 3
summary: Install the toolchain, build and test the workspace, and run the rustinfer command; what each of its six subcommands does on 2026-11-10.
---

# Getting started

Read from `README.md`, `CONTRIBUTING.md`, `Cargo.toml` and
`crates/rustinfer-cli/` at commit `082df51`. The full gate list is on
[build steps](build-steps.html).

## Toolchain

The workspace declares `rust-version = "1.85"`, edition 2021, stable channel.
No ROCm is needed to build or test: the ROCm backend sits behind the `rocm`
feature of `rustinfer-target-rocm`, and the SRS requires every non-device test
to pass on a host without ROCm (RI-NFR-016).

```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path --profile minimal
export PATH="$HOME/.cargo/bin:$PATH"     # --no-modify-path leaves your shell files alone
rustup component add rustfmt clippy
```

The `--no-modify-path` form is how the toolchain was installed on the
development host; with it, every new shell needs the `export` line.

## Build and test

```sh
git clone git@codeberg.org:itej89/rustinfer.git
cd rustinfer
cargo build
cargo test --workspace
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo fmt --all --check
target/debug/rustinfer --version
```

`cargo build` compiles 14 crates and four pinned external dependencies (`clap`,
`thiserror`, `tracing`, `tracing-subscriber`). The test count per crate is on
the [crates](ref-crates.html) page.

## The command

`rustinfer` has six subcommands, one per entry in SRS §3.2.1. On 2026-11-10
every one of them parses its arguments, validates its paths at the boundary
(RI-CLI-012: inputs must exist, outputs must have a writable parent, paths are
canonicalised) and then returns the owning component's `not_implemented` error,
because the components behind them are issues #3 to #15. That is by design:
the command's contract is in place and tested before the behaviour.

| subcommand | arguments today | what happens today | arrives with |
|---|---|---|---|
| `build` | `--model <dir> --target <arch> --out <file>` | model directory and output parent checked; `error=not_implemented component=compiler` | #11 |
| `inspect` | `<artifact>` | file checked; `error=not_implemented component=artifact` | #11 |
| `run` | `<artifact or dir> [--require-prebuilt]` | path checked; a directory with `--require-prebuilt` is refused with `error=invalid component=cli` (RI-CLI-004); otherwise `component=runtime` | #14 |
| `tune` | `--target <arch>` | `error=not_implemented component=kc` | #9 |
| `bench` | `--engine <file>` | file checked; `component=runtime` | R2 (RI-CLI-008) |
| `serve` | `<artifact or dir> [--require-prebuilt]` | as `run` | R3 (RI-CLI-009) |

What is already real, and covered by the integration tests in
`crates/rustinfer-cli/tests/cli.rs`:

- `rustinfer --version` prints the name and version on stdout and exits 0.
- No subcommand, or a bad one, exits 2; any other failure exits 1
  (constants `EXIT_CODE_USAGE`, `EXIT_CODE_FAILURE`).
- A failure is one line on stderr, `error=<code> component=<name> detail="<text>"`,
  and stdout is empty. A missing file gives `error=not_found component=cli`.
- The first thing on stderr is the version manifest: one `info` line per entry
  for the software, the `rustc` that built it, the host, and each direct
  dependency with the version read from `Cargo.lock` at build time.
- `RUSTINFER_LOG` selects the level (`error`, `warn`, `info`, `debug`,
  `trace`; default `info`); an invalid value is `error=config component=core`.
  `RUSTINFER_CACHE_DIR` names the artifact cache, defaulting to
  `$XDG_CACHE_HOME/rustinfer` or `$HOME/.cache/rustinfer`.

A session with the binary built from `e91e002`, run for this page on the
development host (the only thing on this site that was executed):

```text
$ target/debug/rustinfer inspect /nonexistent.rie
ts=2026-11-11T05:34:31.420Z level=info component=manifest startup="version_manifest" kind="software" name="rustinfer-cli" version="0.1.0"
ts=2026-11-11T05:34:31.421Z level=info component=manifest startup="version_manifest" kind="toolchain" name="rustc" version="rustc 1.99.1 (58cf8f9c3 2026-10-13)"
ts=2026-11-11T05:34:31.421Z level=info component=manifest startup="version_manifest" kind="host" name="linux" version="x86_64"
ts=2026-11-11T05:34:31.421Z level=info component=manifest startup="version_manifest" kind="dependency" name="clap" version="4.5.60"
ts=2026-11-11T05:34:31.421Z level=info component=manifest startup="version_manifest" kind="dependency" name="thiserror" version="2.0.17"
ts=2026-11-11T05:34:31.421Z level=info component=manifest startup="version_manifest" kind="dependency" name="tracing" version="0.1.41"
ts=2026-11-11T05:34:31.421Z level=info component=manifest startup="version_manifest" kind="dependency" name="tracing-subscriber" version="0.3.20"
ts=2026-11-11T05:34:31.421Z level=error component=cli msg="/nonexistent.rie: No such file or directory (os error 2)" code="not_found"
error=not_found component=cli detail="/nonexistent.rie: No such file or directory (os error 2)"
$ echo $?
1
$ target/debug/rustinfer run /tmp --require-prebuilt 2>&1 | tail -1
error=invalid component=cli detail="/tmp is a model directory and --require-prebuilt forbids building"
```

The last line is the contract; the `error` log line above it is the same
failure through `tracing`. The detail is the error type's `Display` string and
may change; the `error=` and `component=` fields may not
([error codes](ref-error-codes.html)).

## What to do next

Nothing runs a model yet. The next thing that lands is the Model IR
(issue #3), then the artifact (#4), the target abstraction with the CPU
reference (#5) and the LLaMA frontend (#6); `build` and `inspect` become real
with #11 and `run` with #14. The order and blockers are on the
[issue tracker](issues.html).
