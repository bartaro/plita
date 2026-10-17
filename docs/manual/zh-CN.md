# plita — 使用与开发手册

[English](en.md) · [日本語](ja.md) · [한국어](ko.md) · [简体中文](zh-CN.md) · [繁體中文](zh-TW.md) · [Français](fr.md) · [Español](es.md) · [Deutsch](de.md)

DAISUKE OBA · 源码版 2026-10-18 · Cargo 包版本 0.0.1

## 1. 包含的内容

plita 是面向桌面创作应用的 Rust GUI 基础库。本仓库包含 5 个框架 crate 和 3 个可运行示例，提供原生窗口、输入路由、GPU 绘制、控件、停靠和画布模型。不包含各个模拟器专用的 GUI、ROM 或预编译可执行文件。

- `plita`：公开 API、`prelude` 重新导出及可选的 Python 辅助功能。
- `plita_app`：`App` 构建器与启动配置。
- `plita_window`：原生事件循环与 `PlitaProgram` 接口。
- `plita_render`：GPU 资源与渲染。
- `plita_ui`：几何类型、绘制列表、控件、停靠、画布及历史记录模型。

## 2. 环境要求与构建

请安装 Git、Rust 1.92 或更高版本，以及目标平台所需的链接器和开发工具。Windows MSVC 目标需要 Visual Studio Build Tools 的 C++ 开发组件和 Windows SDK。显示窗口还需要兼容的 GPU 与驱动程序。首次构建会下载 Cargo 依赖项；请保留 `Cargo.lock`，以便复现构建。

```powershell
git clone https://github.com/bartaro/plita.git
cd plita
cargo check --workspace --locked
cargo test --workspace --locked
```

工作区明确启用了 wgpu 的 DX12、GLES 和 Vulkan 后端。清单中未启用 Metal。请勿假定所有操作系统和 GPU 配置都已验证；目标平台的依赖项与显示库可能需要额外配置。以上命令是验证步骤，并不表示所有平台均已通过测试。

## 3. 运行示例

在仓库根目录下逐条运行。启动下一个示例前，请先关闭当前窗口。

```powershell
cargo run --locked -p hello_plita
cargo run --locked -p docking_demo
cargo run --locked -p canvas_demo
```

目前三个示例都启动同一个 `CreativeShell`，区别在于窗口标题，以及 `canvas_demo` 的初始窗口大小。三个名称并不代表三个不同的完整应用。公共界面包含菜单栏、工具栏、网格与画板、检查器、时间轴和状态栏。可用这些示例了解公共 UI；将功能接入自己的应用时，请同时阅读源码。

当文本或内存输入框没有焦点时，可以尝试以下操作。

- `1` / `V`：选择；`2` / `H`：平移；`3` / `R`：矩形；`4` / `T`：文本；`5` / `G`：网格。用平移工具拖动画布，用滚轮缩放，按 `F` 重置视图。
- 选择对象后可拖动本体或角部控制点。`Ctrl+D` 复制；`Delete` / `Backspace` 删除；方向键移动 1 个世界坐标单位，`Shift` + 方向键移动 10 个单位。`Ctrl+Z` 撤销；`Ctrl+Y` / `Ctrl+Shift+Z` 重做。
- `Ctrl+1` 至 `Ctrl+6` 依次选择属性、图层、内存、时间轴、日志和诊断面板。`Ctrl+Shift+1` 至 `Ctrl+Shift+6` 打开浮动面板，`Ctrl+0` 关闭它们。`M` 切换内存编辑器的显示状态。
- 本示例的 `Ctrl+S` 只在状态栏报告快照大小，不会写入文件；`Ctrl+O` 会重置演示文档。这些快捷键并不是完整的文件保存或打开对话框。

## 4. 启动应用

下面是 `hello_plita` 的完整入口代码。

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

`App::new()` 创建 `AppBuilder`，`run()` 启动内置界面。要使用自己的应用状态，请向 `run_program` 传入工厂函数，它接收初始 `Size` 并返回一个 `PlitaProgram` 实现。实现 `resize`、`handle_event` 和 `draw_list`；需要周期更新时使用 `tick`。通过 `UiResponse` 返回所需的 UI 响应，而不是在 OS 事件回调中直接绘制。

`continuous_redraw(false)` 根据更新和重绘请求进行绘制。仅在应用需要时开启连续重绘。`draw_list` 描述绘制命令，GPU 提交由渲染器负责。

## 5. 输入与辅助窗口

UI 命中测试和布局使用 plita 的逻辑坐标；窗口层负责 DPI 换算。事件包括指针、键盘、IME 和文件拖放。收到文件路径后，打开、解析和保存文件仍由应用实现。

`PointerDoubleClick` 在第二次 `PointerUp` 之后发出。同一按钮完成两次点击，间隔不超过 500 ms，位置距离不超过 6 个逻辑像素，才会被识别。拖动操作不计入双击。每个原生窗口独立进行判断。

自定义应用可通过 `AuxiliaryWindowDescriptor` 定义辅助窗口，并实现该窗口的大小调整、事件和绘制列表回调。内置界面的独立内存编辑器操作的是界面持有的演示缓冲区，不会自动连接模拟器或其他进程。

`PlitaProgram::minimum_window_size()`和`auxiliary_window_minimum_size(id)`以逻辑坐标指定客户区的最小尺寸；默认值`None`不限制缩放。`auxiliary_window_activation_request(id)`返回可选的请求令牌。每次主动请求恢复窗口或获取焦点时，请更改令牌；相同令牌不会反复激活窗口。辅助窗口创建失败后，可撤回窗口定义或更改令牌以重试，主窗口会继续运行。

`auxiliary_draw_revision(id)`可选择保留辅助窗口的绘制列表。返回`Some(revision)`时，每次可见内容变化（包括悬停和按下状态）都应更新版本，并通过`UiResponse`请求重绘。窗口大小或DPI变化会使保留的列表失效。动画或共享图像窗口应返回默认值`None`。窗口最小化时跳过渲染，尺寸为零的大小变化事件会被忽略。

## 6. 停靠、画布与持久化

`DockLayoutState` 和停靠几何类型描述面板布局。`DockLayoutProfile` 表示带版本的布局配置。内置界面支持配置文本，`AppBuilder::startup_layout_profile` 可在启动内置界面时恢复它。应用必须自行决定何时、在何处保存文本。内存中的布局槽位不能代替持久化文件保存。

`CanvasDocument` 与 `LayerNode` 提供文档和图层模型。选择、框选、吸附辅助功能与 `CommandHistory` 可用于实现编辑操作。`CommandRegistry` 和 `CommandDescriptor` 描述命令与快捷键信息。这些 API 不提供完整的应用文件格式或自动项目保存系统；请将模型连接到自己的命令与序列化代码。

`memory_viewer_address_at_point(rect, base_address, byte_count, position)`将`draw_memory_viewer`中可见的十六进制字节位置转换为`Option<u16>`地址。请传入与绘制时相同的矩形和起始地址、实际字节数以及逻辑指针坐标。地址标签、ASCII区域、间隙、不存在的字节和隐藏行返回`None`。选择及写入由应用处理，此函数不会修改内存。

## 7. 字体与图标

`assets/fonts` 中附带 Roboto 和 Roboto Mono。plita 通过 `fontdue` 栅格化文字，并保留小型位图备用字体，也会查找已安装的系统字体。可用 `PLITA_UI_FONT`、`PLITA_UI_FONT_FALLBACK`、`PLITA_MEMORY_FONT` 指定字体文件，请在启动应用前设置。字体必须包含要显示的字符。附带的拉丁文字体不足以覆盖全部中日韩文字。

`active_font_family`、`active_font_source`、`active_text_backend` 和 `active_memory_font_family` 可用于诊断字体选择。移动可执行文件时，请确保资源目录仍然可访问，或配置合适的字体路径。加载器出现系统字体路径，并不表示分发包包含该字体文件。

仓库附带 52 个 Lucide SVG 图标。`lucide_icon_names()` 列出支持的名称，`draw_lucide_icon` 用于绘制。使用 `crates/plita_ui/assets/build_icons.py` 重新生成 Rust 路径数据时，请保留 SVG 和许可声明。

## 8. 可选的渲染工作线程

向 `PlitaProgram` 实现添加以下方法即可启用。

```rust
fn render_on_worker_thread(&self) -> bool {
    true
}
```

每个窗口的工作线程负责 GPU 操作与画面呈现。窗口管理、输入、`tick` 和绘制列表生成仍在事件循环线程中进行。渲染较慢时会将待处理请求合并为最新帧，因此它不是无损逐帧录制 API。共享 RGBA 图像应在同一个 mutex 内完成整幅更新，并尽量缩短持锁时间。该选项在创建渲染器时读取，不是运行中切换开关。默认采用同步渲染。

渲染器保留不可变RGBA源以防止纹理缓存标识冲突，并复用顶点缓冲区及图像临时存储。未使用的图像缓存会在短暂的帧保留期后释放。共享RGBA数据在mutex内复制后上传至GPU，因此更新也应在同一mutex内进行。这些内部更改不要求修改现有绘制列表调用。

验证限制（2026-10-18）：在发布工作环境中，普通工作区测试、两个离屏GPU回归测试和原生同步窗口测试已通过。但原生渲染工作线程测试在恢复及调整大小后超时，另一次桌面运行异常终止。原因尚未确定，因此尚未确认工作线程在此环境中能正常运行。需要可靠运行时，请保留默认同步渲染；启用可选工作线程前，请在目标环境中验证。

## 9. 可选的 Python 辅助功能

在适当的 Python 环境中准备 Python 3.10 或更高版本，以及 1.8 以上、2 以下的 maturin。从仓库根目录运行：

```powershell
cd crates/plita
maturin develop --features python
```

`python` 功能提供常用值类型的 PyO3 包装类和注册辅助函数，不会自动把整个 Rust GUI 转换为完整的 Python 应用。使用 `#[pyclass]` 或 `#[pymodule]` 的应用 crate 仍需要自己的可选 `pyo3` 依赖项，因为这些宏引用 `::pyo3`。再次执行前面章节的命令时，请返回仓库根目录。

## 10. 故障排查与验证

- 构建失败：查看首个编译器或链接器错误，确认 Rust 版本与目标工具链，并保留锁定文件。
- 不显示窗口或 GPU 初始化失败：查看日志和显卡驱动。仅构建成功不能证明 GUI 正常工作。
- 字符缺失：选择包含对应字符的字体，并检查 `active_font_source`。
- UI 停顿：缩短事件处理、`tick` 和绘制列表生成的耗时。渲染工作线程不会并行化应用逻辑。
- 原生窗口测试需要可交互的桌面；普通单元测试不能代替视觉检查。

在 PowerShell 中启用诊断日志：

```powershell
$env:RUST_LOG="debug,plita_window=trace,plita_render=trace"
cargo run --locked -p hello_plita
```

本手册描述发布的源码，并不保证所有平台都完成了运行测试。也可以使用 `cargo doc --workspace --no-deps --locked` 生成 API 文档。

在GPU正常工作的环境中，可显式运行两个无需外部数据的回归测试：`cargo test -p plita_render --locked offscreen_image_updates_and_draw_order -- --ignored --test-threads=1`和`cargo test -p plita_render --locked offscreen_cache_keeps_images_distinct_and_releases_old_sources -- --ignored --test-threads=1`。普通工作区测试会跳过GPU及原生桌面测试。其他ignored基准测试需要外部输入和输出路径，请勿在未准备输入时运行所有ignored测试。

## 11. 许可与再分发

plita 代码和本手册采用 MIT 许可证，版权为 (c) 2026 DAISUKE OBA。再分发副本或重要部分时，请保留 MIT 版权声明与许可文本。第三方资源保留原有许可证：Roboto 与 Roboto Mono 采用 OFL-1.1；Lucide 采用 ISC，并包含继承自 Feather 的 MIT 声明。

请阅读 [LICENSE](../../LICENSE)、[第三方声明](../../THIRD_PARTY_NOTICES.md)、[依赖项声明](../../licenses/DEPENDENCIES.md)和[资源来源](../../licenses/ASSET_PROVENANCE.json)。分发字体、图标和二进制文件时，请附带相关声明。在分发 macOS 二进制文件前，需解决记录中 `dispatch` 与 `malloc_buf` 缺少独立许可文本的问题。本仓库发布源码与声明；未来发布二进制文件时，还需检查实际链接的依赖项。

## 12. 源码导航

- [应用构建器](../../crates/plita_app/src/lib.rs)
- [窗口与程序接口](../../crates/plita_window/src/lib.rs)
- [UI 与模型 API](../../crates/plita_ui/src/lib.rs)
- [渲染器](../../crates/plita_render/src/lib.rs)
- [图标资源与生成方法](../../crates/plita_ui/assets/README.md)
- [渲染工作线程详解（日语）](../render_worker_ja.md)
