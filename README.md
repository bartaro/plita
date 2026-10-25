# plita

plita is a Rust GUI foundation for desktop creative tools. It provides native
windows, GPU drawing, input and text handling, docking, canvas models and reusable
controls. Applications own their data and behavior through `PlitaProgram`.

Author: **DAISUKE OBA** · **MIT License** · Cargo package version: **0.0.1**.
The v1.0 label used in some demo titles describes the framework milestone.

## Specification

| Area | What plita provides |
| --- | --- |
| Windows | winit event loop, main and auxiliary windows, minimum sizes, activation requests, main-window DPI notifications |
| Rendering | wgpu draw lists for panels, gradients, triangle meshes, clipped content and immutable/shared RGBA images |
| Input | Pointer, keyboard, double-click, IME, file-drop events and an application-level IME policy |
| Controls | Theme tokens, buttons, dropdown menu buttons with geometric arrows, text input, scrollbars and a memory editor |
| Docking | Fixed, floating and detached panels, split geometry and versioned layout profiles |
| Canvas | Document/layer models, selection, movement, resizing, snapping, command metadata and undo/redo |
| Text and icons | Bundled Roboto and Roboto Mono, system fallback fonts and 52 embedded Lucide icons |
| Integration | Custom Rust applications and optional Python value wrappers and registration helpers |

The source workspace contains five foundation crates (`plita`, `plita_app`,
`plita_window`, `plita_render`, `plita_ui`) and three sample applications.
Popup contents, file formats, file dialogs, project persistence and application
commands are implemented by the consuming application.

## Requirements and quick start

Install Git, Rust **1.92 or later**, and a linker for your target. Windows MSVC
builds need Visual Studio Build Tools with C++ tools and the Windows SDK.
Native rendering also needs a compatible GPU and driver. The first build may
download Cargo dependencies; keep `Cargo.lock` for reproducible dependency versions.

```powershell
git clone https://github.com/bartaro/plita.git
cd plita
cargo check --workspace --locked
cargo test --workspace --locked
cargo run --locked -p hello_plita
```

The workspace explicitly enables wgpu's DX12, GLES and Vulkan backends. Metal is
not enabled in this manifest. These build commands are validation procedures,
not a claim that every operating system or GPU configuration has been tested.

## Using the examples

Close one example before starting the next:

```powershell
cargo run --locked -p docking_demo
cargo run --locked -p canvas_demo
```

All three examples currently launch the shared `CreativeShell`; their titles
and initial sizes differ. The shell contains a menu bar, tools, a grid canvas,
inspector, timeline and status bar. Try these controls when a text or memory
input does not have focus:

- `1`–`5`: selection, pan, rectangle, text and grid tools; wheel to zoom and `F` to reset the view.
- Drag selected objects or their corner handles; `Ctrl+D` duplicates, `Delete` removes, and arrow keys move them.
- `Ctrl+Z` undoes; `Ctrl+Y` or `Ctrl+Shift+Z` redoes.
- `Ctrl+1`–`Ctrl+6` selects panels; `Ctrl+Shift+1`–`Ctrl+Shift+6` opens floating panels; `Ctrl+0` closes them.
- In this demo, `Ctrl+S` reports an in-memory snapshot size and `Ctrl+O` resets the demo document. They do not save or open files.

## Creating an application

The smallest entry point starts the built-in shell:

```rust
use plita::prelude::*;

fn main() -> Result<()> {
    App::new()
        .title("My plita application")
        .window_size(1280, 800)
        .continuous_redraw(false)
        .run()
}
```

For your own application state, implement `PlitaProgram::{resize, handle_event,
draw_list}` and pass a factory to `AppBuilder::run_program`. The factory receives
the initial logical `Size`. Use `tick` for periodic updates and `UiResponse` to
request redraws. Construct drawing commands in `DrawList`; the renderer submits
them to the GPU. With `continuous_redraw(false)`, redraws follow UI changes and
explicit requests.

### Dropdown menu buttons

```rust
use plita::prelude::*;

let mut list = DrawList::new(Color::rgb8(30, 30, 30));
let rect = Rect::new(12.0, 12.0, 100.0, 32.0);
let expanded = false;
draw_menu_button(
    &mut list,
    rect,
    "File",
    expanded,
    ButtonVisualState::Normal,
    MenuButtonStyle::new(PanelStyle::dark(), Color::rgb8(240, 240, 240), 1.22),
);
```

Use this drawing fragment inside `draw_list`. `expanded` controls the arrow:
down when closed, up when open. The caption is clipped separately from the
right-aligned arrow, so long names cannot obscure it. No arrow character is
needed in the label.

Track interactions with `ButtonInteractionState`, use the original `rect` as
the shared hit target for caption and arrow, and manage popup contents and
selection in your app. Pass state-specific theme colors through `MenuButtonStyle`.
`MenuButtonLayout::new` exposes the content regions. For automatic width, add
`MENU_BUTTON_CHROME_WIDTH` (42 logical pixels) to `measure_text_width(label, scale)`.

### Input, DPI and auxiliary windows

- `PlitaProgram::ime_allowed()` defaults to `true`. Physical-key applications can return `false`; the policy is read at main/auxiliary window creation, without changing separate native file dialogs.
- `scale_factor_changed(scale_factor)` reports the main window's physical pixels per logical unit before the first draw and before `resize` on DPI refresh/change. Layout and hit testing continue to use logical coordinates.
- `UiEvent::PointerDoubleClick` follows the second completed `PointerUp` within 500 ms and 6 logical pixels; drag gestures are excluded. Detection is independent for each window.
- Describe auxiliary windows with `AuxiliaryWindowDescriptor` and implement their input, resize and drawing callbacks. Optional minimum sizes, activation tokens and draw revisions control their lifecycle.

### Fonts, icons and Python

Set `PLITA_UI_FONT`, `PLITA_UI_FONT_FALLBACK` or `PLITA_MEMORY_FONT` before launch
when you need a particular font. Bundled Latin fonts do not cover all CJK text;
provide an appropriate installed fallback. Inspect `active_font_source()` when
diagnosing missing glyphs. `draw_lucide_icon` and `lucide_icon_names` expose the
52 bundled icons; see [the icon guide](crates/plita_ui/assets/README.md).

For optional Python helpers, install Python 3.10+ and maturin 1.8–1.x, then run:

```powershell
cd crates/plita
maturin develop --features python
```

The feature provides PyO3 wrappers and registration helpers. An application
defining `#[pyclass]` or `#[pymodule]` also needs its own optional `pyo3` dependency
and an application-specific module. Return to the repository root for the other
commands in this README. See chapter 10 of the manuals for details.

## Manuals / 多言語説明書

All eight editions describe the same public APIs. Read Markdown on GitHub or
open the generated HTML locally; HTML uses no external scripts, fonts or services.

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

Open `docs/manual/index.html` after cloning. Regenerate and check HTML with:

```powershell
python docs/manual/build.py
python docs/manual/build.py --check
cargo doc --workspace --no-deps --locked
```

Additional references: [framework scope](docs/v1_0_completion.md),
[render-worker guide (Japanese)](docs/render_worker_ja.md),
[historical development notes](docs/history.md).

## Validation and current limitations

```powershell
cargo fmt --all -- --check
cargo check --workspace --locked
cargo test --workspace --locked
python docs/manual/build.py --check
```

Normal tests skip GPU and native desktop probes. Chapter 11 of every manual
lists explicit opt-in commands and required inputs; do not run all ignored
tests without their fixtures and a suitable desktop.

Synchronous rendering is the default. `render_on_worker_thread()` opts into
coalesced GPU rendering on per-window workers; event handling, UI updates and
draw-list construction stay on the event-loop thread. At the 2026-10-18 native
validation, the worker path timed out after restore/resize and a separate run
terminated abnormally. Its reliable native operation remains unconfirmed.
The [worker guide](docs/render_worker_ja.md) records that boundary.

## License and redistribution

Project code and documentation are MIT licensed, copyright (c) 2026
**DAISUKE OBA**. Roboto and Roboto Mono retain OFL-1.1; Lucide retains ISC and
the inherited Feather MIT notices. Keep the applicable notices with source and
binary redistributions. Review the recorded `dispatch` and `malloc_buf` notice
gaps before distributing macOS binaries.

See [LICENSE](LICENSE), [third-party notices](THIRD_PARTY_NOTICES.md),
[dependency notices](licenses/DEPENDENCIES.md) and [CLEAN_ROOM.md](CLEAN_ROOM.md).
This public package contains framework source, assets and examples; application
integrations, ROMs, executables and development evidence are outside its scope.

## Update history

### 2026-10-25 — menu buttons, input policy and documentation

- Add shared `draw_menu_button`, `MenuButtonStyle` and `MenuButtonLayout` with a geometric open/closed arrow and separate caption clipping.
- Add the `PlitaProgram::ime_allowed()` creation policy and main-window `scale_factor_changed()` callback.
- Add an opt-in DPI-aware offscreen fixture snapshot test.
- Update all eight Markdown manuals and generated HTML; put specifications and usage before this history.
- Keep Cargo package version `0.0.1`; this is a source update.

### 2026-10-18 — rendering and window lifecycle

- Reuse GPU buffers and image scratch storage, retain immutable image identities and release unused image-cache entries.
- Add minimum window sizes, auxiliary-window activation requests and retained draw revisions.
- Add `memory_viewer_address_at_point` and explicit offscreen GPU regression tests.

Earlier implementation stages are preserved in [development history](docs/history.md).
