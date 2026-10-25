# plita — User and developer manual

[English](en.md) · [日本語](ja.md) · [한국어](ko.md) · [简体中文](zh-CN.md) · [繁體中文](zh-TW.md) · [Français](fr.md) · [Español](es.md) · [Deutsch](de.md)

DAISUKE OBA · Source edition 2026-10-25 · Cargo package version 0.0.1

## 1. What is included

plita is a Rust GUI foundation for creative desktop applications. This repository contains five framework crates and three executable examples. It provides native windows, input routing, GPU drawing, widgets, docking and canvas models. Application-specific emulator GUIs, ROMs and prebuilt executables are outside this distribution.

- `plita`: public API and `prelude` re-exports; optional Python helpers.
- `plita_app`: `App` builder and launch configuration.
- `plita_window`: native event loop and the `PlitaProgram` interface.
- `plita_render`: GPU resources and rendering.
- `plita_ui`: geometry, draw lists, widgets, docking, canvas and history models.

## 2. Requirements and build

Install Git and Rust 1.92 or later, including the native linker/toolchain for your target. On Windows with the MSVC target, install Visual Studio Build Tools with the C++ workload and Windows SDK. A compatible GPU and driver are needed to open a window. The first build downloads Cargo dependencies; keep `Cargo.lock` for reproducibility.

```powershell
git clone https://github.com/bartaro/plita.git
cd plita
cargo check --workspace --locked
cargo test --workspace --locked
```

The workspace explicitly enables the wgpu DX12, GLES and Vulkan backends. Metal is not enabled in the manifest. Do not assume that every OS or GPU configuration has been validated; target-specific dependencies and display libraries may require additional setup. The commands above are verification instructions, not a claim that every platform passed testing.

## 3. Start the examples

Run one command at a time from the repository root. Close the window before launching the next example.

```powershell
cargo run --locked -p hello_plita
cargo run --locked -p docking_demo
cargo run --locked -p canvas_demo
```

All three examples currently start the same `CreativeShell`; they differ in window title and, for `canvas_demo`, initial size. Their names do not identify three separate finished applications. The shell shows a menu bar, tool strip, grid/artboard canvas, inspector, timeline and status bar. Use the demos to explore the shared UI and consult the source when integrating a feature into your own application.

With text and memory input unfocused, try these shell controls:

- `1` / `V`: select; `2` / `H`: pan; `3` / `R`: box; `4` / `T`: text; `5` / `G`: grid. Drag the canvas with the pan tool, use the wheel to zoom, and press `F` to reset the view.
- Select an object and drag it or its corner handles. `Ctrl+D` duplicates; `Delete` / `Backspace` deletes; arrow keys move by 1 world unit and `Shift` + arrow keys by 10. `Ctrl+Z` undoes; `Ctrl+Y` / `Ctrl+Shift+Z` redoes.
- `Ctrl+1` through `Ctrl+6` select Properties, Layers, Memory, Timeline, Log and Diagnostics panels. `Ctrl+Shift+1` through `Ctrl+Shift+6` open floating panels; `Ctrl+0` closes them. `M` toggles the memory editor.
- In this demo, `Ctrl+S` reports a snapshot size in the status bar; it does not write a file. `Ctrl+O` resets the demo document. Do not treat these shortcuts as completed file-save/open dialogs.

## 4. Launch an application

The complete `hello_plita` entry point is:

```rust
use plita::prelude::*;

fn main() -> Result<()> {
    App::new()
        .title("plita UI v1.0 - Creative Shell")
        .window_size(1280, 800)
        .clear_color(ClearColor::rgb(0.105, 0.111, 0.125))
        .continuous_redraw(false)
        .run()
}
```

`App::new()` creates an `AppBuilder`. `run()` launches the built-in shell. To supply your own application state, use `run_program` with a factory receiving the initial `Size` and returning an implementation of `PlitaProgram`. Implement `resize`, `handle_event` and `draw_list`; use `tick` when periodic updates are needed. Return `UiResponse` to report the required UI response instead of drawing directly inside an OS event callback.

With `continuous_redraw(false)`, drawing is driven by updates and redraw requests. Enable continuous redraw only when the application needs it. `draw_list` describes drawing commands; the renderer owns GPU submission.

## 5. Input and auxiliary windows

Use plita's logical coordinates for UI hit testing and layout; the window layer handles DPI conversion. Events cover pointer, keyboard, IME and file drops. A received file path is input to your application: opening, parsing and saving that file remain application responsibilities.

`PointerDoubleClick` follows the second `PointerUp`. Recognition requires the same button, two completed clicks within 500 ms and positions within 6 logical pixels. Drag gestures are excluded. Each native window has independent detection state.

Custom applications can describe auxiliary windows through `AuxiliaryWindowDescriptor` and implement their resize, event and draw-list callbacks. The shell's detached memory editor works on its retained demonstration buffer; it is not automatically connected to an emulator or another process.

`PlitaProgram::minimum_window_size()` and `auxiliary_window_minimum_size(id)` specify minimum client sizes in logical coordinates; the default `None` leaves resizing unconstrained. `auxiliary_window_activation_request(id)` returns an optional request token: change it for each intentional restore/focus request. An unchanged token does not repeatedly activate the window. After an auxiliary-window creation failure, withdraw its descriptor or change the activation token to retry; the main window remains running.

`auxiliary_draw_revision(id)` optionally retains an auxiliary draw list. Return `Some(revision)` and change the revision whenever visible content changes, including hover and pressed states, while also requesting redraw through `UiResponse`. Native resize or DPI changes invalidate the retained list. Return the default `None` for animated or shared-image windows. Rendering is skipped while a window is minimized, and zero-sized resize events are ignored.

`PlitaProgram::ime_allowed()` defaults to `true`. Return `false` for an application that needs physical key input without host IME interception. The policy is read when the main and auxiliary windows are created; it is not a runtime toggle and does not change the input context of separate native file dialogs. Text applications should keep the default.

`scale_factor_changed(scale_factor)` reports the main window's physical pixels per logical UI unit. It is called before the first draw and before `resize` when DPI is refreshed or changed. Store the value when aligning pixel-based content, and continue using logical coordinates for layout and hit testing. This callback does not report an auxiliary window's independent DPI.

## 6. Docking, canvas and persistence

`DockLayoutState` and the dock geometry types describe panel placement. `DockLayoutProfile` represents a versioned layout profile. The shell supports layout profile text, and `AppBuilder::startup_layout_profile` restores it when launching the built-in shell. Your application must decide where and when to save that text; in-memory layout slots do not replace durable file storage.

`CanvasDocument` and `LayerNode` provide the document and layer model. Selection, marquee and snapping helpers, together with `CommandHistory`, support editor behavior. `CommandRegistry` and `CommandDescriptor` describe commands and shortcuts. These APIs do not supply a complete application file format or an automatic project-save system. Connect the models to your own commands and serialization.

`memory_viewer_address_at_point(rect, base_address, byte_count, position)` maps a visible hexadecimal byte in `draw_memory_viewer` to `Option<u16>`. Pass the same rectangle and base address as the renderer, the actual byte count, and a logical pointer position. Address labels, ASCII text, gaps, missing bytes and hidden rows return `None`. The application handles selection and writes; this helper does not modify memory.

## 7. Dropdown menu buttons

`draw_menu_button` draws a complete menu-button surface, caption and right-aligned geometric chevron. The indicator is independent of fonts: pass the caption without an appended `v` or arrow character. `expanded = false` points downward; `true` points upward while the application's popup is open.

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

This fragment builds drawing commands inside a `draw_list` implementation; it does not open a window by itself. Use `ButtonInteractionState` to track hover and press, toggle your popup state on a matching press/release, and pass that state as `expanded`. Route both the caption and the arrow through the original button rectangle. The application draws popup items and handles selection and dismissal.

`MenuButtonStyle` supplies the current surface, foreground color and text scale. `ButtonVisualState::Pressed` offsets the surface and its contents together. `MenuButtonLayout::new` exposes the caption and indicator regions; captions are clipped so they cannot cover the arrow. For automatic sizing, add `MENU_BUTTON_CHROME_WIDTH` (42 logical pixels) to `measure_text_width(label, scale)`. Select hover, pressed and active colors from your theme; popup opening is separate from visual state.

## 8. Fonts and icons

Roboto and Roboto Mono are bundled under `assets/fonts`. plita uses `fontdue` for text rasterization and retains a small bitmap fallback. Font discovery also checks installed system fonts. `PLITA_UI_FONT`, `PLITA_UI_FONT_FALLBACK` and `PLITA_MEMORY_FONT` can select font files; set them before starting the application. A font must contain the characters you want to display. The bundled Latin fonts alone are not a complete CJK font collection.

`active_font_family`, `active_font_source`, `active_text_backend` and `active_memory_font_family` help diagnose font selection. Keep the asset directory available when moving an executable, or configure an appropriate font path. System fonts are not bundled merely because their paths appear in the loader.

The repository includes 52 Lucide SVG icons. `lucide_icon_names()` lists supported names and `draw_lucide_icon` draws them. Preserve the SVGs and their notices when regenerating the Rust paths with `crates/plita_ui/assets/build_icons.py`.

## 9. Optional rendering worker

Add this method to your `PlitaProgram` implementation to opt in:

```rust
fn render_on_worker_thread(&self) -> bool {
    true
}
```

GPU work and presentation move to a worker for each window. Window management, input, `tick` and draw-list construction stay on the event-loop thread. Slow rendering coalesces pending requests to the latest frame; it is not a lossless frame-recording API. Update a shared RGBA image entirely under the same mutex and keep that lock short. The option is read when a renderer is created, rather than acting as a live toggle. The default is synchronous rendering.

The renderer retains immutable RGBA sources to prevent texture-cache identity collisions, reuses vertex buffers and temporary image storage, and releases unused image-cache entries after a short frame-based retention period. Shared RGBA data is copied under its mutex before GPU upload; keep updates inside that same mutex. These internal changes do not require changes to existing draw-list calls.

Validation note (2026-10-18): the normal workspace tests, two offscreen GPU regressions, and the native synchronous-window test passed on the publication machine. The native render-worker test timed out after restore/resize, and a separate desktop run terminated abnormally. The cause has not been isolated, so successful native worker operation is not confirmed for this environment. Keep the default synchronous rendering when reliability is required; validate the opt-in worker on your own target before enabling it.

## 10. Optional Python helpers

Python support requires Python 3.10 or later and maturin 1.8 or later, below 2, in a suitable Python environment. From the repository root:

```powershell
cd crates/plita
maturin develop --features python
```

The `python` feature provides PyO3 wrappers for common values and registration helpers. It does not turn every Rust GUI into a complete Python application. Application crates using `#[pyclass]` or `#[pymodule]` still need their own optional `pyo3` dependency, because those macros refer to `::pyo3`. Return to the repository root before using the earlier commands.

## 11. Troubleshooting and verification

- Build failure: read the first compiler or linker error, check the Rust version and target toolchain, and preserve the lockfile.
- No window or GPU initialization error: inspect logs and the installed graphics driver. A build alone does not prove GUI behavior.
- Missing characters: select a font containing those glyphs and check `active_font_source`.
- UI stalls: keep event handlers, `tick` and draw-list generation short. A rendering worker does not parallelize application logic.
- Native window tests require an interactive desktop; ordinary unit tests do not replace visual verification.

For diagnostic logging in PowerShell:

```powershell
$env:RUST_LOG="debug,plita_window=trace,plita_render=trace"
cargo run --locked -p hello_plita
```

The manuals describe the published source. They do not certify runtime testing on every platform. API documentation can also be generated with `cargo doc --workspace --no-deps --locked`.

Two self-contained GPU regression tests can be run explicitly on a machine with a working GPU: `cargo test -p plita_render --locked offscreen_image_updates_and_draw_order -- --ignored --test-threads=1` and `cargo test -p plita_render --locked offscreen_cache_keeps_images_distinct_and_releases_old_sources -- --ignored --test-threads=1`. Normal workspace tests skip GPU and native desktop tests. The other ignored benchmarks require external fixtures and output paths; do not run every ignored test without preparing those inputs.

The optional `offscreen_fixture_snapshot_with_dpi` test reads a draw-list fixture from `PLITA_DRAW_FIXTURE`, uses its `scale_factor` (default 1.0), and writes `gpu.json` and physical-size `desktop.rgba` to `PLITA_GPU_EVIDENCE`. It requires a GPU and an explicitly prepared fixture. It checks the offscreen encoder path, not native-window presentation.

## 12. License and redistribution

plita code and these manuals use the MIT License, copyright (c) 2026 DAISUKE OBA. Preserve the MIT copyright and permission notice when redistributing copies or substantial portions. Third-party assets retain their own licenses: Roboto and Roboto Mono use OFL-1.1; Lucide uses ISC and includes the inherited Feather MIT notice.

Read [LICENSE](../../LICENSE), [THIRD_PARTY_NOTICES](../../THIRD_PARTY_NOTICES.md), [dependency notices](../../licenses/DEPENDENCIES.md) and [asset provenance](../../licenses/ASSET_PROVENANCE.json). Include the relevant notices with distributed fonts, icons and binaries. Before distributing macOS binaries, resolve the standalone notice gaps recorded for `dispatch` and `malloc_buf`. This repository publishes source and notices; a future binary release needs a review of its actual linked dependencies.

## 13. Source map

- [Application builder](../../crates/plita_app/src/lib.rs)
- [Window and program interface](../../crates/plita_window/src/lib.rs)
- [UI and model APIs](../../crates/plita_ui/src/lib.rs)
- [Renderer](../../crates/plita_render/src/lib.rs)
- [Icon assets and generation](../../crates/plita_ui/assets/README.md)
- [Rendering-worker details (Japanese)](../render_worker_ja.md)
- [Menu-button component](../../crates/plita_ui/src/menu_button.rs)
