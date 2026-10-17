# plita UI v1.0

plita UI is a clean-room Rust GUI foundation for lightweight creative desktop applications.

Author: **DAISUKE OBA**.

Project code is available under the [MIT License](LICENSE), copyright (c) 2026
DAISUKE OBA. Bundled Roboto and Roboto Mono fonts remain under OFL-1.1; Lucide
icons remain under ISC, with the inherited Feather MIT notice. These assets are
not relicensed by plita. See [third-party notices](THIRD_PARTY_NOTICES.md) for
copyright holders, full license texts, source links and redistribution guidance.

This public source workspace contains the five plita foundation crates and the
`hello_plita`, `docking_demo` and `canvas_demo` examples. Downstream applications,
emulator integrations, ROMs, development screenshots and prebuilt executables
are not part of this distribution.

## Manuals / 多言語説明書

The complete user and developer manual is included in the same eight languages
as the KITAQ series. Each edition covers setup, demo controls, application APIs,
docking and canvas models, fonts and icons, rendering workers, Python helpers,
troubleshooting and redistribution notices.

| Language | Read on GitHub | Offline HTML |
| --- | --- | --- |
| English | [Manual](docs/manual/en.md) | [HTML](docs/manual/en.html) |
| 日本語 | [説明書](docs/manual/ja.md) | [HTML](docs/manual/ja.html) |
| 한국어 | [설명서](docs/manual/ko.md) | [HTML](docs/manual/ko.html) |
| 简体中文 | [使用手册](docs/manual/zh-CN.md) | [HTML](docs/manual/zh-CN.html) |
| 繁體中文 | [使用手冊](docs/manual/zh-TW.md) | [HTML](docs/manual/zh-TW.html) |
| Français | [Manuel](docs/manual/fr.md) | [HTML](docs/manual/fr.html) |
| Español | [Manual](docs/manual/es.md) | [HTML](docs/manual/es.html) |
| Deutsch | [Handbuch](docs/manual/de.md) | [HTML](docs/manual/de.html) |

After cloning or downloading the repository, open `docs/manual/index.html` in a
browser. Keep the repository directory structure so that styles and source links
remain available. The HTML manuals work offline and use no external scripts or
font services. GitHub's normal file view displays HTML source; use the Markdown
links above for reading on GitHub. To regenerate HTML after editing Markdown:

```powershell
python docs/manual/build.py
python docs/manual/build.py --check
```

## Source update — 2026-10-18

- Reuse GPU vertex buffers and image scratch storage; retain immutable image
  sources safely and release unused texture-cache entries.
- Add optional minimum window sizes, explicit auxiliary-window restore/focus
  requests, and revision-based auxiliary draw-list retention to `PlitaProgram`.
  Existing implementations keep the default behavior without adding methods.
- Add `memory_viewer_address_at_point` for visible hexadecimal byte hit testing
  and align the memory viewer's headers and byte cells.
- Add opt-in offscreen GPU regression tests. See chapter 10 of each manual for
  the self-contained commands; fixture-based benchmarks need separate inputs.

The eight language manuals cover the new APIs and redraw requirements. The
Cargo package version remains `0.0.1`; this is a source update.

### Native render-worker validation limitation

Validation note (2026-10-18): the normal workspace tests, two offscreen GPU regressions, and the native synchronous-window test passed on the publication machine. The native render-worker test timed out after restore/resize, and a separate desktop run terminated abnormally. The cause has not been isolated, so successful native worker operation is not confirmed for this environment. Keep the default synchronous rendering when reliability is required; validate the opt-in worker on your own target before enabling it.

## Framework overview

v1.0 turns the Phase 2 shell into a reusable framework surface. plita now exposes a custom `PlitaProgram` app trait, retained Dock Tree geometry allocation, fixed/floating/detached dock operations, versioned layout profiles with startup restore support, canvas document/layer models, multi-select/marquee/snap model APIs, command registry metadata, style tokens, file-drop events, and demo applications.

- MIT-licensed repository skeleton
- Cargo workspace
- top-level `plita` re-export crate
- `plita_app` application builder
- `plita_window` winit event-loop integration
- `plita_render` wgpu surface/device setup
- Vello renderer initialization placeholder
- `plita_ui` crate with geometry, colors, draw lists, and a deterministic creative layout
- GPU rectangle pipeline for UI panels, grid, timeline, simple buttons, and bitmap bootstrap text
- resize handling with draw-list regeneration
- DPI/event logging
- keyboard/mouse/IME/file-drop logging hooks
- shared `PointerDoubleClick` routing for main and auxiliary windows
- unit tests for geometry, layout, draw lists, vertex generation, event routing, canvas hit testing, object creation, object dragging, and undo/redo
- `PlitaProgram` for custom apps on the plita window/render loop
- Dock Tree geometry allocation and profile text persistence
- Dock tab close, detach, attach, restore, and in-memory slot operations
- Canvas document snapshot, layer tree, multi-select, marquee selection, and snap helpers
- command registry metadata and shortcut regression coverage
- public style/theme tokens for app-facing widgets

## Why wgpu 28?

Vello 0.8.0 depends on `wgpu ^28.0.0` when its `wgpu` feature is enabled. Phase 1 therefore keeps `wgpu = "28.0.0"` so the renderer stack stays on one wgpu generation.

## Build

```powershell
cargo check --workspace
cargo test --workspace
cargo run -p hello_plita
cargo run -p docking_demo
cargo run -p canvas_demo
```

For verbose logs:

```powershell
$env:RUST_LOG="debug,plita_window=trace,plita_render=trace"
cargo run -p hello_plita
```

## Python Bindings

plita has an optional `python` feature for PyO3-based application bindings. It
re-exports PyO3 through `plita::python::prelude::*`, exposes common wrapper
classes such as `Point`, `Size`, `Rect`, `Color`, and `AppConfig`, and provides
small helpers for registering those classes, returning Python `bytes`, and
mapping plita app errors into Python exceptions.

To build plita's helper module directly:

```powershell
cd crates\plita
maturin develop --features python
```

Application crates can enable it from their own feature:

```toml
[features]
python = ["plita/python", "dep:pyo3"]

[dependencies]
pyo3 = { workspace = true, optional = true }
```

App crates that define `#[pyclass]` or `#[pymodule]` still keep an optional
`pyo3` dependency because PyO3's procedural macros expand through the `::pyo3`
crate path, but common binding glue should come from plita:

```rust
#[cfg(feature = "python")]
mod python_api {
    use plita::python::{self as plita_python, prelude::*};

    #[pymodule]
    fn my_app(_py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
        plita_python::add_plita_classes(module)?;
        Ok(())
    }
}
```

## Rendering workers

Custom apps can opt in to worker-thread GPU rendering with
`PlitaProgram::render_on_worker_thread()`. The default remains synchronous;
window management, input, UI ticks and draw-list construction stay on the
event-loop thread. See [the rendering-worker guide](docs/render_worker_ja.md)
for lifecycle, frame-coalescing and shared-image rules.

## Double-click events

Custom `PlitaProgram` implementations receive
`UiEvent::PointerDoubleClick { position, button }` after the second
`PointerUp`. plita recognizes two completed clicks when they use the same
pointer button, finish within 500 ms, and stay within 6 logical pixels.
Press-drag-release gestures are excluded, and detection is independent for the
main window and each auxiliary window.

## Expected result

A native window opens with a dark creative-app shell:

- top menu bar
- left tool strip
- central canvas with grid and artboard placeholder
- right inspector
- lower timeline
- bottom status bar

The bootstrap text uses the bundled Roboto UI font through plita's lightweight `fontdue` rasterizer, with an original tiny rectangle-based bitmap font kept as a deterministic fallback until the final text/IME subsystem is implemented.

The debugger memory editor opens as a detached native auxiliary window when the
default shell requests it. It edits the same retained memory buffer owned by the
parent shell, supports vertical scrolling for longer memory ranges, and renders
its memory/address text with the bundled Google Fonts Roboto Mono font.

## v1.0 Scope

plita v1.0 provides the framework foundation needed by production-tool style desktop apps: retained widget/event routing, command metadata, dock layout persistence, canvas document editing, text/IME routing, style tokens, and app-owned custom draw/event programs. Native OS file dialogs and advanced GPU text shaping can be layered on top without changing the public app trait.

## Clean-room note

The project documents a clean-room implementation approach based on the plita
UI specification and public dependency APIs. This design note is not an
independent proof of every source file's origin. See [CLEAN_ROOM.md](CLEAN_ROOM.md)
and [third-party notices](THIRD_PARTY_NOTICES.md) for the stated scope and the
separate provenance of bundled fonts and icons.

## Historical development notes

The phase notes below record earlier implementation stages. Use the current
manuals above and the source APIs for the present feature set.


## Phase 1 v2

This snapshot adds the retained `plita_ui::CreativeShell`, a lightweight widget tree, event routing, toolbar selection, splitter dragging, and status bar updates.

Run:

```powershell
cargo check --workspace
cargo test --workspace
cargo run -p hello_plita
```

## Phase 1 v3

This snapshot continues Phase 1 after Widget Tree + Event Routing and adds the first interactive desktop-shell behaviors:

- retained menu-bar item nodes: `FILE`, `EDIT`, `VIEW`, `WINDOW`, `HELP`
- active menu popup rendering
- keyboard shortcut routing with modifier state
- tool shortcuts: `1/V` = Select, `2/H` = Pan, `3/R` = Box, `4/T` = Text
- command-status shortcuts: `Ctrl+S`, `Ctrl+O`, `Ctrl+Z`, `Ctrl+Y`, `Ctrl+Shift+Z`
- canvas mouse-wheel zoom
- Pan tool drag on the canvas
- `F` to reset/fit the canvas view
- additional unit tests for menu opening, keyboard tool selection, and canvas zoom

Manual check:

```text
1. Click FILE/EDIT/VIEW/WINDOW/HELP; a small popup should appear.
2. Press 1/2/3/4 or V/H/R/T; the active tool should change.
3. Select PAN, drag in the canvas; the grid/artboard should move.
4. Wheel over the canvas; the zoom percentage should change.
5. Press F; zoom/pan should reset.
6. Press Ctrl+S/Ctrl+O/Ctrl+Z/Ctrl+Y; the status bar should show command status.
```

## Phase 1 v7

This snapshot extends the canvas object prototype:

- selected rectangle corner handles can be dragged to resize
- resize operations are undoable/redoable
- `Delete`/`Backspace` deletes the selected object through command history
- `Ctrl+D` duplicates the selected object
- arrow keys nudge the selected object; `Shift+Arrow` nudges by 10 world units
- inspector shows selected object position and size
- additional unit tests cover resize, delete/undo, duplicate, and nudge

Manual check:

```text
1. Select the blue rectangle.
2. Drag a corner handle; the object should resize.
3. Press Ctrl+Z/Ctrl+Y; the resize should undo/redo.
4. Press Ctrl+D; a duplicated rectangle should appear offset and selected.
5. Press Arrow keys / Shift+Arrow; the selected object should move.
6. Press Delete or Backspace; selected object should disappear.
7. Press Ctrl+Z; deleted object should come back.
```

## Phase 1 v7 notes

This source drop adds the first configurable grid-input prototype for dot/pixel/waveform-style editing, rich button/slider prototypes, a right-click context menu, and a floating debugger-style memory viewer window. These are still Phase 1 bootstrap widgets built from GPU rectangles and the 5x7 debug text renderer; later phases will move them into the formal widget/style/docking systems.


## Phase 1 v8 typography note

plita UI now bundles Roboto as its default UI font. Apps can still override it with `PLITA_UI_FONT` or a font placed in `assets/fonts/`. The plita source remains MIT-licensed; the bundled Roboto font remains under the SIL Open Font License 1.1.

## Phase 2 v2.1 note

This package includes the first shortcut-system cleanup after the floating dock shortcut fixes. `KeyInput` now normalizes the legacy key string before command handling, keeping ordinary logical shortcuts separate from Windows/JIS physical-key recovery for Ctrl+Shift+number.

## Phase 2 v3.0 note

This package introduces the Dock Layout State foundation on top of the v12 shortcut-stable floating dock implementation. The new `DockLayoutState` / `DockNode` / `DockPanelKind` model is synchronized with the existing inspector, bottom, and floating dock state, while preserving the confirmed v12 behavior. A deterministic JSON seed exporter is included through `CreativeShell::dock_layout_json()` and `DockLayoutState::to_json_pretty()` for future layout persistence work.


## Phase 2 v3.1 note

This package keeps the v13 `DockLayoutState` foundation and starts using it as the source of truth for fixed dock tabs. Inspector and bottom tab rectangles, plus their widget-tree nodes, are now derived from the Dock Tree tab groups. Runtime behavior remains intentionally conservative: no tab dragging or attach/detach is introduced yet, and the v12 shortcut fixes remain untouched.


## Phase 2 v3.7.1 note

This package keeps the bottom diagnostics visibility fix from v19 and adds a compact line-position hotfix. In a 743x354 window the bottom dock becomes about 72px high; the v19 test correctly exposed that the third diagnostics line could exceed `rect.bottom()`. v20 now uses a compact 10px diagnostics spacing table for bottom docks up to 80px high, so the title, layout summary, and layout seed size remain inside the visible bottom-dock bounds. Floating Diagnostics keeps the v18 behavior.


## Phase 2 v3.7.1 note

- Adds retained Dock Tree split ratio accessors.
- Persists `root_ratio` and `main_ratio` in the lightweight JSON seed.
- Shows `SPLIT ROOT ... MAIN ...` in Bottom DIAG and Floating Diagnostics.
- Does not yet connect live splitter dragging to Dock Tree ratios; this keeps v21 behavior stable.

## Shared Icons

plita now includes 52 vendored Lucide icons through
`plita::prelude::{draw_lucide_icon, lucide_icon_names}`. Icons are embedded in
applications, centered and aspect-preserving. SVG sources, regeneration scripts,
and upstream license are in `crates/plita_ui/assets`; see its README for usage.
Applications can use this shared API without a separate icon renderer.
