# plita — 使用與開發手冊

[English](en.md) · [日本語](ja.md) · [한국어](ko.md) · [简体中文](zh-CN.md) · [繁體中文](zh-TW.md) · [Français](fr.md) · [Español](es.md) · [Deutsch](de.md)

DAISUKE OBA · 原始碼版 2026-10-18 · Cargo 套件版本 0.0.1

## 1. 隨附內容

plita 是供桌面創作應用程式使用的 Rust GUI 基礎函式庫。本儲存庫包含 5 個框架 crate 與 3 個可執行範例，提供原生視窗、輸入路由、GPU 繪製、元件、停駐配置與畫布模型。不包含個別模擬器專用的 GUI、ROM 或預先編譯的執行檔。

- `plita`：公開 API、`prelude` 重新匯出及選用的 Python 輔助功能。
- `plita_app`：`App` 建構器與啟動設定。
- `plita_window`：原生事件迴圈與 `PlitaProgram` 介面。
- `plita_render`：GPU 資源與算繪。
- `plita_ui`：幾何型別、繪製清單、元件、停駐配置、畫布及歷程模型。

## 2. 環境需求與建置

請安裝 Git、Rust 1.92 以上版本，以及目標平台所需的連結器與開發工具。Windows MSVC 目標需要 Visual Studio Build Tools 的 C++ 開發工具及 Windows SDK。顯示視窗也需要相容的 GPU 與驅動程式。首次建置會下載 Cargo 相依套件；請保留 `Cargo.lock`，以便重現建置。

```powershell
git clone https://github.com/bartaro/plita.git
cd plita
cargo check --workspace --locked
cargo test --workspace --locked
```

工作區明確啟用了 wgpu 的 DX12、GLES 與 Vulkan 後端。資訊清單中未啟用 Metal。請勿假設所有作業系統與 GPU 組態都已驗證；目標平台的相依套件及顯示函式庫可能需要額外設定。以上指令是驗證步驟，不表示所有平台均已通過測試。

## 3. 執行範例

在儲存庫根目錄逐一執行。啟動下一個範例前，請先關閉目前的視窗。

```powershell
cargo run --locked -p hello_plita
cargo run --locked -p docking_demo
cargo run --locked -p canvas_demo
```

目前三個範例都啟動同一個 `CreativeShell`，差別在視窗標題，以及 `canvas_demo` 的初始大小。三個名稱不代表三個不同的完整應用程式。共用介面包含功能表列、工具列、格線與工作區域畫布、屬性檢視器、時間軸及狀態列。可用這些範例認識共用 UI；整合個別功能時，請一併參考原始碼。

文字或記憶體輸入欄位沒有焦點時，可以嘗試以下操作。

- `1` / `V`：選取；`2` / `H`：平移；`3` / `R`：矩形；`4` / `T`：文字；`5` / `G`：格線。用平移工具拖曳畫布，用滾輪縮放，按 `F` 重設檢視。
- 選取物件後可拖曳本體或角落控制點。`Ctrl+D` 複製；`Delete` / `Backspace` 刪除；方向鍵移動 1 個世界座標單位，`Shift` + 方向鍵移動 10 個單位。`Ctrl+Z` 復原；`Ctrl+Y` / `Ctrl+Shift+Z` 重做。
- `Ctrl+1` 至 `Ctrl+6` 依序選擇屬性、圖層、記憶體、時間軸、紀錄與診斷面板。`Ctrl+Shift+1` 至 `Ctrl+Shift+6` 開啟浮動面板，`Ctrl+0` 關閉它們。`M` 切換記憶體編輯器的顯示狀態。
- 此範例的 `Ctrl+S` 只在狀態列顯示快照大小，不會寫入檔案；`Ctrl+O` 會重設示範文件。這些快速鍵並非完整的檔案儲存或開啟對話方塊。

## 4. 啟動應用程式

以下是 `hello_plita` 的完整進入點。

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

`App::new()` 建立 `AppBuilder`，`run()` 啟動內建介面。若要使用自訂應用程式狀態，請將接收初始 `Size` 並傳回 `PlitaProgram` 實作的工廠函式傳入 `run_program`。實作 `resize`、`handle_event` 與 `draw_list`；需要週期更新時使用 `tick`。透過 `UiResponse` 傳回所需的 UI 回應，而非在 OS 事件回呼中直接繪製。

`continuous_redraw(false)` 依更新與重繪要求繪製畫面。只有應用程式需要時才啟用連續重繪。`draw_list` 描述繪製指令，GPU 提交由算繪器負責。

## 5. 輸入與輔助視窗

UI 命中測試與版面配置使用 plita 的邏輯座標；視窗層負責 DPI 換算。事件涵蓋指標、鍵盤、IME 與檔案拖放。收到檔案路徑後，開啟、解析及儲存仍由應用程式實作。

`PointerDoubleClick` 在第二次 `PointerUp` 之後發出。同一按鈕完成兩次點擊，間隔不超過 500 ms，位置距離不超過 6 個邏輯像素，才會被辨識。拖曳操作不計入雙擊。每個原生視窗會獨立判定。

自訂應用程式可用 `AuxiliaryWindowDescriptor` 定義輔助視窗，並實作該視窗的大小調整、事件及繪製清單回呼。內建介面的獨立記憶體編輯器操作的是介面持有的示範緩衝區，不會自動連線至模擬器或其他程序。

`PlitaProgram::minimum_window_size()`與`auxiliary_window_minimum_size(id)`以邏輯座標指定用戶端區域的最小尺寸；預設值`None`不限制縮放。`auxiliary_window_activation_request(id)`傳回可選的請求權杖。每次主動請求還原視窗或取得焦點時，請變更權杖；相同權杖不會反覆啟用視窗。輔助視窗建立失敗後，可撤回視窗定義或變更權杖以重試，主視窗會繼續執行。

`auxiliary_draw_revision(id)`可選擇保留輔助視窗的繪製清單。傳回`Some(revision)`時，每次可見內容變化（包含懸停及按下狀態）都應更新版本，並透過`UiResponse`請求重繪。視窗大小或DPI變更會使保留的清單失效。動畫或共用影像視窗應傳回預設值`None`。視窗最小化時略過渲染，尺寸為零的大小變更事件會被忽略。

## 6. 停駐配置、畫布與永久儲存

`DockLayoutState` 與停駐幾何型別描述面板配置。`DockLayoutProfile` 表示附有版本的配置設定。內建介面支援設定文字，`AppBuilder::startup_layout_profile` 可在啟動內建介面時還原設定。應用程式必須自行決定何時、在何處儲存文字。記憶體中的配置儲存槽不能取代永久檔案儲存。

`CanvasDocument` 與 `LayerNode` 提供文件及圖層模型。選取、框選、貼齊輔助功能與 `CommandHistory` 可用於建立編輯操作。`CommandRegistry` 與 `CommandDescriptor` 描述指令及快速鍵資訊。這些 API 不提供完整的應用程式檔案格式或自動專案儲存系統；請將模型連接至自訂指令及序列化程式碼。

`memory_viewer_address_at_point(rect, base_address, byte_count, position)`將`draw_memory_viewer`中可見的十六進位元組位置轉換為`Option<u16>`位址。請傳入與繪製時相同的矩形及起始位址、實際位元組數，以及邏輯指標座標。位址標籤、ASCII區域、間隙、不存在的位元組和隱藏列傳回`None`。選取及寫入由應用程式處理，此函式不會修改記憶體。

## 7. 字型與圖示

`assets/fonts` 隨附 Roboto 與 Roboto Mono。plita 透過 `fontdue` 點陣化文字，並保留小型點陣備援字型，也會尋找已安裝的系統字型。可用 `PLITA_UI_FONT`、`PLITA_UI_FONT_FALLBACK`、`PLITA_MEMORY_FONT` 指定字型檔，請在啟動應用程式前設定。字型必須包含要顯示的字元。隨附的拉丁字型不足以涵蓋所有中日韓文字。

`active_font_family`、`active_font_source`、`active_text_backend` 與 `active_memory_font_family` 可用來診斷字型選擇。移動執行檔時，請維持資源目錄可存取，或設定適當的字型路徑。載入器列出系統字型路徑，不代表散布內容包含該字型檔。

儲存庫隨附 52 個 Lucide SVG 圖示。`lucide_icon_names()` 列出支援的名稱，`draw_lucide_icon` 用於繪製。以 `crates/plita_ui/assets/build_icons.py` 重新產生 Rust 路徑資料時，請保留 SVG 與授權聲明。

## 8. 選用的算繪工作執行緒

在 `PlitaProgram` 實作中加入以下方法即可啟用。

```rust
fn render_on_worker_thread(&self) -> bool {
    true
}
```

各視窗的工作執行緒負責 GPU 操作與畫面呈現。視窗管理、輸入、`tick` 及繪製清單建立仍在事件迴圈執行緒進行。算繪較慢時，會將待處理要求合併為最新畫面，因此它不是無損逐格錄影 API。共用 RGBA 影像應在同一個 mutex 內完成整張更新，並盡量縮短鎖定時間。設定在建立算繪器時讀取，不是執行中的切換開關。預設採用同步算繪。

渲染器保留不可變RGBA來源以防止紋理快取識別衝突，並重複使用頂點緩衝區及影像暫存空間。未使用的影像快取會在短暫的影格保留期後釋放。共用RGBA資料在mutex內複製後上傳至GPU，因此更新也應在同一mutex內進行。這些內部變更不要求修改既有繪製清單呼叫。

驗證限制（2026-10-18）：在發佈工作環境中，一般工作區測試、兩個離屏GPU回歸測試及原生同步視窗測試已通過。但原生渲染工作執行緒測試在還原及調整大小後逾時，另一次桌面執行則異常終止。原因尚未確定，因此尚未確認工作執行緒在此環境中能正常運作。需要可靠運作時，請保留預設同步渲染；啟用可選工作執行緒前，請在目標環境中驗證。

## 9. 選用的 Python 輔助功能

請在適當的 Python 環境準備 Python 3.10 以上版本，以及 1.8 以上、未滿 2 的 maturin。從儲存庫根目錄執行：

```powershell
cd crates/plita
maturin develop --features python
```

`python` 功能提供常用值型別的 PyO3 包裝類別及註冊輔助函式，不會自動將整個 Rust GUI 轉換為完整 Python 應用程式。使用 `#[pyclass]` 或 `#[pymodule]` 的應用程式 crate 仍須自行加入選用的 `pyo3` 相依套件，因為這些巨集參照 `::pyo3`。再次執行前面章節的指令前，請回到儲存庫根目錄。

## 10. 疑難排解與驗證

- 建置失敗：查看第一個編譯器或連結器錯誤，確認 Rust 版本及目標工具鏈，並保留鎖定檔。
- 未顯示視窗或 GPU 初始化失敗：查看紀錄及顯示卡驅動程式。建置成功不代表 GUI 運作已通過驗證。
- 字元缺漏：選擇含有所需字元的字型，並檢查 `active_font_source`。
- UI 停頓：縮短事件處理、`tick` 及繪製清單建立的耗時。算繪工作執行緒不會平行化應用程式邏輯。
- 原生視窗測試需要可互動的桌面；一般單元測試不能取代目視檢查。

在 PowerShell 啟用診斷紀錄：

```powershell
$env:RUST_LOG="debug,plita_window=trace,plita_render=trace"
cargo run --locked -p hello_plita
```

本手冊說明公開的原始碼，不保證所有平台都已完成執行測試。也可用 `cargo doc --workspace --no-deps --locked` 產生 API 文件。

在GPU正常運作的環境中，可明確執行兩個無需外部資料的回歸測試：`cargo test -p plita_render --locked offscreen_image_updates_and_draw_order -- --ignored --test-threads=1`與`cargo test -p plita_render --locked offscreen_cache_keeps_images_distinct_and_releases_old_sources -- --ignored --test-threads=1`。一般工作區測試會略過GPU及原生桌面測試。其他ignored基準測試需要外部輸入與輸出路徑，請勿在未準備輸入時執行所有ignored測試。

## 11. 授權與再散布

plita 程式碼與本手冊採用 MIT 授權，著作權為 (c) 2026 DAISUKE OBA。再散布副本或重要部分時，請保留 MIT 著作權聲明與授權文字。第三方資源保留原有授權：Roboto 與 Roboto Mono 採用 OFL-1.1；Lucide 採用 ISC，並包含源自 Feather 的 MIT 聲明。

請閱讀 [LICENSE](../../LICENSE)、[第三方聲明](../../THIRD_PARTY_NOTICES.md)、[相依套件聲明](../../licenses/DEPENDENCIES.md)及[資源來源](../../licenses/ASSET_PROVENANCE.json)。散布字型、圖示及二進位檔時，請附上相關聲明。散布 macOS 二進位檔前，須先處理紀錄中 `dispatch` 與 `malloc_buf` 缺少獨立授權文字的問題。本儲存庫公開原始碼與聲明；未來散布二進位檔時，仍需檢查實際連結的相依套件。

## 12. 原始碼導覽

- [應用程式建構器](../../crates/plita_app/src/lib.rs)
- [視窗與程式介面](../../crates/plita_window/src/lib.rs)
- [UI 與模型 API](../../crates/plita_ui/src/lib.rs)
- [算繪器](../../crates/plita_render/src/lib.rs)
- [圖示資源與產生方法](../../crates/plita_ui/assets/README.md)
- [算繪工作執行緒詳解（日文）](../render_worker_ja.md)
