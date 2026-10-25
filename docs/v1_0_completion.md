# plita framework scope

Current source documentation: 2026-10-25. Cargo package version: 0.0.1.
The v1.0 milestone describes the framework surface; it is not the Cargo version.

## Implemented framework surface

- Native main and auxiliary windows with lifecycle, minimum-size, activation and retained draw-list hooks.
- Application-owned logic through `PlitaProgram`, including creation-time IME policy and main-window DPI notifications.
- GPU draw lists for panels, gradients, triangle meshes, clips and immutable/shared RGBA images.
- Reusable menu buttons with geometric arrows, clipped captions and app-owned popup state.
- Retained widget/event models, text input with IME preedit/commit and UTF-8 cursor boundaries, scrollbars and a memory editor.
- Dock Tree geometry, fixed/floating/detached panels, layout profiles, in-memory slots and startup restoration hooks.
- Canvas documents and layers, selection/marquee/snap helpers, movement, resizing and command history.
- Theme tokens, 52 bundled Lucide icons, Roboto/Roboto Mono and optional Python helpers.
- Three examples using the shared `CreativeShell`: `hello_plita`, `docking_demo`, `canvas_demo`.

## Application responsibilities

The application supplies popup entries and actions, persistent document formats,
project save/load behavior and native file dialogs. Demo snapshot and layout
slots are in-memory examples. The detached memory editor edits a demo buffer;
connecting it to an application's memory model is a separate integration.

## Validation boundaries

Run `cargo fmt --all -- --check`, `cargo check --workspace --locked`,
`cargo test --workspace --locked` and `python docs/manual/build.py --check`.
GPU and native desktop tests are opt-in and are not implied by normal test success.
The native render-worker limitation recorded on 2026-10-18 remains open; use the
default synchronous path where reliable native presentation is required.

See the [README](../README.md), [English manual](manual/en.md),
[Japanese manual](manual/ja.md) and [render-worker guide](render_worker_ja.md)
for setup, APIs, operation and detailed test prerequisites.
