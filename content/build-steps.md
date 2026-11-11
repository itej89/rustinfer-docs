---
title: Build steps
section: Development
order: 2
summary: The toolchain, the cargo gates, the four CI scripts, coverage, the rocm feature flag, and the pinned LLVM the kernel compiler will need; every command the tree's CI runs, in its order.
---

# Build steps

Read from `README.md`, `CONTRIBUTING.md`, `Cargo.toml`, `clippy.toml`,
`rustfmt.toml`, `deny.toml`, `.github/workflows/ci.yml` and `scripts/ci/` at
commit `e91e002`.

## Toolchain

| item | value | where stated |
|---|---|---|
| Rust | stable channel, edition 2021, `rust-version = "1.85"` | `[workspace.package]` |
| components | `rustfmt`, `clippy`; `llvm-tools-preview` for coverage | `ci.yml` |
| external tools | `cargo-llvm-cov`, `cargo-audit` (installed in CI with `cargo install --locked`); `cargo-deny` through its action | `ci.yml` |
| ROCm | not needed to build or test; the ROCm backend is behind the `rocm` feature of `rustinfer-target-rocm` (RI-NFR-016) | `README.md` |
| MLIR, LLVM | not yet a dependency; see the last section | SRS §2.4, OI-009 |

```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path --profile minimal
export PATH="$HOME/.cargo/bin:$PATH"
rustup component add rustfmt clippy llvm-tools-preview
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
| `check_unsafe_budget.sh` | `unsafe` only under `crates/rustinfer-target-*/src/ffi` or `crates/rustinfer-kc/src/mlir`; the total may not exceed `scripts/ci/unsafe_budget.txt`, which holds `0` (RI-NFR-011) |
| `check_doc_freshness.py` | every `docs/uml/*.md` carries the header SWG-001 §17.3 requires |
| `validate_mermaid.py` | every Mermaid block in the diagrams parses |

## The CI pipeline

`.github/workflows/ci.yml`, on push to `main` and on every pull request,
with `RUSTFLAGS: -D warnings` for every job. Four jobs, each needing the one
before, so a failure blocks the next stage (SWG-001 §11.1):

| job | steps |
|---|---|
| `lint` | checkout; stable toolchain with `rustfmt` and `clippy`; format; clippy; rustdoc with private items; unsafe budget; diagram headers; Mermaid parse |
| `security` | checkout; `cargo-deny` action (licences, advisories, sources per `deny.toml`); `cargo audit` for CVEs (RI-NFR-012) |
| `test` | checkout; toolchain with `llvm-tools-preview`; `cargo install cargo-llvm-cov`; `cargo llvm-cov --workspace --all-features --fail-under-lines 80 --lcov --output-path lcov.info` (RI-NFR-013); upload `lcov.info` as the `coverage` artifact |
| `build` | checkout; `cargo build --release --workspace`; smoke test `target/release/rustinfer --version` (RI-CLI-001); upload the binary as the `rustinfer` artifact |

The actions are referenced by tag at `e91e002` (`actions/checkout@v4`,
`dtolnay/rust-toolchain@stable`, `EmbarkStudios/cargo-deny-action@v2`,
`actions/upload-artifact@v4`); the standard's post-coding gate asks for
full-SHA pins, `timeout-minutes` and a `permissions` block, none of which the
file has at this commit. Forgejo Actions on Codeberg reads this path
(ADR-004).

## Coverage

```sh
cargo llvm-cov --workspace --all-features --summary-only
```

The threshold is 80 percent of lines, per the SRS per crate (RI-NFR-013) and
in CI across the workspace. Integration tests under `crates/*/tests/` carry
a file-level allow for `unwrap`, `expect` and `panic` with a justification
comment, since `clippy.toml` permits them in tests.

## The `rocm` feature

`rustinfer-target-rocm` has features `default` and `rocm`. Without `rocm`
the crate compiles everywhere and the target reports itself unsupported on
selection; with it the workspace links `libamdhip64`. The feature is empty
at `e91e002` (issue #12 fills it). The SRS requires that the kernel compiler
produce binaries for any target on any host, so only autotuning needs the
device (RI-NFR-016).

## The pinned LLVM

The kernel compiler links MLIR and LLVM through the `melior` crate at one
pinned version, with `lld` linked for code objects and no system LLVM
required (SRS §2.4, RI-KC-008). The SRS's reference table names LLVM 22.
Open issue OI-009 says building it in CI is slow and records the resolution
as a vendored prebuilt with a recorded hash; the draft of issue #7 says
ADR-007 will decide how CI and developers obtain it. At `e91e002` there is no
`melior` dependency, no ADR-007 and no LLVM in the build; the workspace
builds with four external crates. When #7 lands this page's toolchain table
gains a row.
