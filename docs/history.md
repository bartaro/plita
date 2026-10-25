# plita development history

These notes describe earlier implementation stages, not the current feature set.
For the current specification and usage, see the [README](../README.md) and
[manuals](manual/en.md). Current documentation revision: 2026-10-25.

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
