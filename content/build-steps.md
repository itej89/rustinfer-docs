---
title: Build steps
section: Development
order: 2
summary: The pinned toolchain (Rust 1.100.0, MSRV 1.89), the cargo gates, the CI jobs and their toolchains, coverage, the rocm feature flag, and the pinned LLVM 23; every command the tree's CI runs, in its order.
---

# Build steps

Read from `README.md`, `CONTRIBUTING.md`, `Cargo.toml`, `clippy.toml`,
`rustfmt.toml`, `deny.toml`, `.github/workflows/ci.yml` and `scripts/ci/` at
commit `082df51` (2026-11-11); the toolchain, the CI jobs, the `rocm` feature
and the pinned LLVM re-read at `81fbcba` (2026-11-14), after PRs #58, #60, #44
and #62.

## Toolchain

| item | value | where stated |
|---|---|---|
| Rust | **1.100.0**, pinned with `rustfmt`, `clippy` and `llvm-tools-preview`, profile `minimal` (owner decision of 2026-11-14, PR #60); rustup installs it on the first `cargo` command | `rust-toolchain.toml`, ADR-001 |
| MSRV | `rust-version = "1.89"`, edition 2021; checked by the `msrv` CI job | `[workspace.package]`, ADR-007 |
| external tools | `cargo-llvm-cov` 0.9.1 and `cargo-audit` 0.23.0, installed in CI as prebuilt binaries through `taiki-e/install-action`, which also installs `cargo-deny` 0.20.2 | `ci.yml` |
| ROCm | not needed to build or test; the ROCm backend is behind the `rocm` feature of `rustinfer-target-rocm`, which opens `libamdhip64.so.7` with `dlopen` at run time (RI-NFR-016) | `README.md`, the crate's `Cargo.toml` |
| MLIR, LLVM, `lld` | LLVM 23.1.6 from apt.llvm.org, exact package versions per Ubuntu codename (jammy, noble, resolute), for `--all-features` builds; see the last section | `scripts/ci/install_llvm.sh`, ADR-007 |

```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path --profile minimal
export PATH="$HOME/.cargo/bin:$PATH"
# rust-toolchain.toml selects 1.100.0 with rustfmt, clippy and llvm-tools-preview
rustup toolchain install 1.100.0 --profile minimal --component rustfmt,clippy,llvm-tools-preview
rustup toolchain install 1.89 --profile minimal     # only for the MSRV check
cargo install cargo-llvm-cov --locked
```

The `--no-modify-path` form is how the development host was set up; it means
the `export` line is needed in every shell, or in the shell's own profile by
hand.

## The local gates

`CONTRIBUTING.md` lists these as the checks to run before a PR; they are the
`lint` job of CI plus the tests.

```sh
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
RUSTDOCFLAGS="-D warnings" cargo doc --workspace --no-deps
cargo test --workspace
scripts/ci/check_unsafe_budget.sh
python3 scripts/ci/check_doc_freshness.py
python3 scripts/ci/validate_mermaid.py docs/uml/*.md
```

| check | what it enforces |
|---|---|
| `cargo fmt --check` | `rustfmt.toml`: edition 2021, `max_width = 100` |
| `cargo clippy -D warnings` | every lint of ADR-001 as an error: `pedantic` warnings become errors; the denied list is on [crates](ref-crates.html) |
| `cargo doc` with `-D warnings` | every public item documented, no broken intra-doc links; CI adds `--document-private-items` |
| `check_unsafe_budget.sh` | `unsafe` only under `crates/rustinfer-target-*/src/ffi` or `crates/rustinfer-kc/src/mlir`; the total may not exceed `scripts/ci/unsafe_budget.txt`, which holds `52` at `81fbcba` after the HIP binding and the `lld` shim (RI-NFR-011) |
| `check_doc_freshness.py` | every `docs/uml/*.md` carries the header SWG-001 §17.3 requires |
| `validate_mermaid.py` | every Mermaid block in the diagrams parses |

## The CI pipeline

`.github/workflows/ci.yml` at `81fbcba`, on push to `main` and on every pull
request, with `RUSTFLAGS: -D warnings` for every job, `permissions: contents:
read` at the top, `MLIR_SYS_230_PREFIX` and `TABLEGEN_230_PREFIX` set to
`/usr/lib/llvm-23`, and `timeout-minutes: 10` on every job. Five jobs; each
needs the one before except `msrv`, which runs beside `security` after `lint`,
so a failure blocks the next stage (SWG-001 §11.1). Every job prints
`rustc -V` and `cargo -V` first, so the log shows which compiler ran.

| job | toolchain | steps |
|---|---|---|
| `lint` | 1.100.0, `rustfmt`, `clippy` | checkout; rust-cache; install the pinned LLVM; format; clippy with `--all-features`; rustdoc with private items; unsafe budget; diagram headers; Mermaid parse |
| `msrv` | 1.89 (`RUSTUP_TOOLCHAIN` overrides `rust-toolchain.toml`) | checkout; rust-cache; install the pinned LLVM; `cargo check --workspace --all-features` on the declared `rust-version` (SWG-001 §18, ADR-007) |
| `security` | 1.100.0 | checkout; `cargo-deny` 0.20.2 and `cargo-audit` 0.23.0 as prebuilt binaries; `cargo deny check` (licences, advisories, sources per `deny.toml`); `cargo audit` for CVEs (RI-NFR-012) |
| `test` | 1.100.0, `llvm-tools-preview` | checkout; rust-cache; install the pinned LLVM; `cargo-llvm-cov` 0.9.1; `cargo llvm-cov --workspace --all-features --fail-under-lines 80 --lcov --output-path lcov.info` (RI-NFR-013), which runs the AMD lowering tests; the GPU tests are ignored without a GPU; upload `lcov.info` as the `coverage` artifact |
| `build` | 1.100.0 | checkout; rust-cache; install the pinned LLVM; `cargo build --release --workspace --all-features`; `cargo check --workspace` without the LLVM features (RI-NFR-016); smoke test `target/release/rustinfer --version` (RI-CLI-001); upload the binary as the `rustinfer` artifact |

To bump the toolchain, one pull request changes `channel` in
`rust-toolchain.toml` and every `toolchain:` input in `ci.yml` (the comment
in `rust-toolchain.toml`).

Every action is pinned to a full commit SHA with the tag in a comment, as
SWG-001 §11 asks (`actions/checkout` v4.4.0, `dtolnay/rust-toolchain` from
its stable branch of 2026-11, which installs the `toolchain:` input,
`Swatinem/rust-cache` v2.9.3, `taiki-e/install-action` v2.90.3 installing
`cargo-deny` 0.20.2, `cargo-audit` 0.23.0 and `cargo-llvm-cov` 0.9.1,
`actions/upload-artifact` v4.6.2). The first green run, run 7 of 2026-11-11 on Codeberg, took about
five and a half minutes for the four jobs in sequence.

### GitHub Actions

What changed and why: on 2026-11-12 the project moved from Codeberg to
GitHub because Codeberg's July 2026 terms amendment bans repositories that
mostly consist of AI-written code (ADR-008, superseding ADR-004). GitHub
Actions reads the same `.github/workflows/ci.yml`; GitHub PR #19 (9d448ce,
merged 2026-11-12) retargeted the jobs, and at `f039b4d` the workflow names
`ubuntu-latest` on every job, `timeout-minutes: 10`, a top-level
`permissions: contents: read`, a concurrency group with `cancel-in-progress`
and `actions/upload-artifact` v4.6.2 pinned by SHA.

| on GitHub | detail |
|---|---|
| Runners | GitHub's hosted `ubuntu-latest`, the label the workflow asked for on 2026-11-10 before Codeberg's labels replaced it; no label time limit, the jobs keep `timeout-minutes: 10` |
| Actions | pinned by full commit SHA with the tag in a comment, as before; the `https://github.com/` prefix Forgejo needed is dropped, short `owner/repo@sha` names resolve on github.com |
| Artifacts | `actions/upload-artifact` v4, the version Forgejo's artifact service refused |
| Runs | GitHub's run numbers restart at 1 on 2026-11-12; the Codeberg runs 1 to 11 did not move ([issues](issues.html)) |
| LLVM | no self-hosted runner was needed: every job but `security` installs the pinned LLVM 23 on the hosted runner with `scripts/ci/install_llvm.sh` and caches the compiled binding with `Swatinem/rust-cache` (ADR-007); `deny.toml` keeps `allow-wildcard-paths = true`, which is `cargo-deny`'s reading of version-less path dependencies, not the host's |

The three Codeberg rules learned from runs 3 to 6 and recorded in ADR-004
(short action names resolving against `data.forgejo.org`, which mirrors only
`actions/*`; `cargo-deny`'s wildcard reading; `upload-artifact` v4 refusing
any host but github.com) are history now; the [roadmap](roadmap.html) keeps
the account.

## Coverage

```sh
cargo llvm-cov --workspace --all-features --summary-only
```

The threshold is 80 percent of lines, per the SRS per crate (RI-NFR-013) and
in CI across the workspace. Integration tests under `crates/*/tests/` carry
a file-level allow for `unwrap`, `expect` and `panic` with a justification
comment, since `clippy.toml` permits them in tests.

## The `rocm` feature

`rustinfer-target-rocm` has features `default`, `rocm` and `rocm-test`
(`81fbcba`). Without `rocm` the crate compiles everywhere and the target
reports itself unsupported on device selection. With it, the crate opens the
HIP runtime with `dlopen` at run time, never at build time: the first of
`/opt/rocm/lib/libamdhip64.so.7`, `/usr/lib/x86_64-linux-gnu/libamdhip64.so.7`,
`/usr/lib64/libamdhip64.so.7` and `/usr/lib/libamdhip64.so.7` that loads, or
only the file named by `RUSTINFER_HIP_LIBRARY` once it passes its checks
(RI-SEC-001); `LD_LIBRARY_PATH` is never searched. A runtime whose major
version is not 7 is refused (RI-NFR-017). So the feature builds and its host
tests run, over a mock of the HIP function table, on a host without ROCm
(RI-NFR-016). `rocm-test` adds the hardware tests of the AMD lowering, which
compile kernels in process through `rustinfer-kc`'s `mlir` feature; they are
ignored without a GPU and run with `--ignored` on one (`docs/gpu-testing.md`;
[hardware](hardware.html)).

## The pinned LLVM

The kernel compiler links MLIR and LLVM 23 in process through `melior`
0.29.1 and `mlir-sys` 230.0.2, and links AMDGPU code objects with `lld` as a
library through a small C++ shim (`crates/rustinfer-kc/src/mlir/lld_shim.cpp`)
that returns `lld`'s messages instead of printing them (PR #44, ADR-007).
`scripts/ci/install_llvm.sh` installs LLVM 23.1.6 at exact package versions
per Ubuntu codename (jammy, noble, resolute) from apt.llvm.org, the key
checked against a recorded fingerprint, including `liblld-23-dev` for the
static `lld` libraries and `llvm-23` and `lld-23` for the code-object
regression test; `--prefix DIR` installs the same packages without sudo,
verifying the suite signature and every package hash. A build needs
`MLIR_SYS_230_PREFIX` and `TABLEGEN_230_PREFIX` pointing at the prefix
(`/usr/lib/llvm-23` after the apt install), and a C++17 compiler for the
shim. Builds without `--all-features` need no LLVM (RI-NFR-016).
