# Clean-room implementation note

plita UI v1.0 is a clean-room implementation generated from the project specification.

The implementation is intentionally limited to original project scaffolding, original Rust source code,
and public API usage of dependencies. It does not copy code from egui, iced, Slint, GPUI, Vello examples,
Learn WGPU examples, or other GUI frameworks.

Third-party crates are used through their public APIs and remain under their
respective licenses. plita project code is released under the MIT License,
copyright (c) 2026 DAISUKE OBA. Vendored Lucide/Feather icon data and bundled
Roboto/Roboto Mono fonts are third-party assets, covered by the separate terms
in THIRD_PARTY_NOTICES.md. This implementation note does not claim ownership
of those assets or independently prove the provenance of every source line.

The v1.0 framework APIs (`PlitaProgram`, Dock Tree geometry/profile, command registry, canvas document model, style tokens, and demo apps) are implemented in this repository from the handoff specification and local tests.

Phase 1 adds an original tiny 5x7 rectangle bitmap font solely as a bootstrap debug/UI label renderer. It is not copied from any external font file or GUI toolkit.
