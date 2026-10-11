# PLITA UI v1.0 Completion Notes

This note records the v1.0 completion surface implemented from the 2026-05-20 handoff.

## Completion Checklist

- Dock Tree geometry allocation: `DockLayoutState::allocate_geometry()`
- fixed/floating/detached dock basics: tab close, detach, attach, restore, floating shortcuts
- layout save/load/reset/profile: JSON seed, slots A/B, `DockLayoutProfile`, startup profile restore hook
- Canvas document model: `CanvasDocument`, `LayerNode`, object/layer tree export
- multi-select/marquee/snap: selection set, marquee selection API, snap helpers
- command registry + undo/redo: `CommandRegistry` and existing canvas command history
- text input / IME: focused text input, caret, preedit, commit, UTF-8 cursor boundaries
- style/theme token: `ThemeTokens`
- basic widgets: retained `Widget` trait and widget-tree roles
- demo apps: `hello_plita`, `docking_demo`, `canvas_demo`
- CI commands: `cargo fmt --all --check`, `cargo check --workspace`, `cargo test --workspace`
- shortcut regression tests: Ctrl+Shift+0, Ctrl+Shift+number, physical-key fallback, copy/paste
- clean-room docs: `README.md`, `CLEAN_ROOM.md`, `THIRD_PARTY_NOTICES.md`

KOKURA-GUI is intentionally separate from PLITA itself and should be implemented as a PLITA application using `PlitaProgram`.
