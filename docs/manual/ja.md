# plita — 利用・開発マニュアル

[English](en.md) · [日本語](ja.md) · [한국어](ko.md) · [简体中文](zh-CN.md) · [繁體中文](zh-TW.md) · [Français](fr.md) · [Español](es.md) · [Deutsch](de.md)

DAISUKE OBA · ソース版 2026-10-18 · Cargoパッケージ版 0.0.1

## 1. 同梱内容

plitaは、デスクトップの制作アプリを作るためのRust製GUI基盤です。このリポジトリには5個の基盤クレートと3個の実行可能なサンプルを同梱しています。ネイティブウィンドウ、入力処理、GPU描画、ウィジェット、ドッキング、キャンバスのモデルを提供します。個別エミュレーターのGUI、ROM、ビルド済み実行ファイルは含みません。

- `plita`：公開APIと`prelude`による再公開、任意のPython補助機能。
- `plita_app`：`App`ビルダーと起動設定。
- `plita_window`：ネイティブイベントループと`PlitaProgram`インターフェース。
- `plita_render`：GPUリソースと描画。
- `plita_ui`：座標、描画リスト、ウィジェット、ドッキング、キャンバス、履歴のモデル。

## 2. 必要環境とビルド

Git、Rust 1.92以降、および対象環境用のリンカー・開発ツールを用意してください。WindowsのMSVCターゲットでは、Visual Studio Build ToolsのC++開発機能とWindows SDKが必要です。ウィンドウの表示には対応するGPUとドライバーも必要です。初回ビルドではCargoの依存関係をダウンロードします。再現性のため`Cargo.lock`を保持してください。

```powershell
git clone https://github.com/bartaro/plita.git
cd plita
cargo check --workspace --locked
cargo test --workspace --locked
```

ワークスペースではwgpuのDX12・GLES・Vulkanバックエンドを明示的に有効化しています。マニフェストでMetalは有効になっていません。すべてのOSやGPU構成で検証済みとは限らず、対象環境固有の依存関係や表示用ライブラリの準備が必要な場合があります。上のコマンドは検証手順であり、全環境での試験完了を示すものではありません。

## 3. サンプルの起動

リポジトリのルートで、以下を1つずつ実行します。次のサンプルを起動する前にウィンドウを閉じてください。

```powershell
cargo run --locked -p hello_plita
cargo run --locked -p docking_demo
cargo run --locked -p canvas_demo
```

現在の3サンプルは同じ`CreativeShell`を起動し、ウィンドウのタイトルと、`canvas_demo`では初期サイズが異なります。名前ごとに別の完成済みアプリが実装されているわけではありません。共通シェルにはメニューバー、ツール列、グリッドとアートボードのキャンバス、インスペクター、タイムライン、ステータスバーがあります。共通UIを試し、個別機能を組み込む際はソースも参照してください。

文字入力欄やメモリー入力欄にフォーカスがない状態で、次の操作を試せます。

- `1` / `V`：選択、`2` / `H`：パン、`3` / `R`：矩形、`4` / `T`：文字、`5` / `G`：グリッド。パンツールでキャンバスをドラッグし、ホイールで拡大縮小、`F`で表示をリセットします。
- オブジェクトを選択して本体や角のハンドルをドラッグできます。`Ctrl+D`で複製、`Delete` / `Backspace`で削除、矢印キーで1ワールド単位、`Shift`＋矢印キーで10単位移動します。`Ctrl+Z`で取り消し、`Ctrl+Y` / `Ctrl+Shift+Z`でやり直します。
- `Ctrl+1`から`Ctrl+6`でプロパティ・レイヤー・メモリー・タイムライン・ログ・診断の各パネルを選択します。`Ctrl+Shift+1`から`Ctrl+Shift+6`でフローティングパネルを開き、`Ctrl+0`で閉じます。`M`でメモリーエディターの表示を切り替えます。
- このデモの`Ctrl+S`はステータスバーにスナップショットのサイズを表示し、ファイルには保存しません。`Ctrl+O`はデモ文書をリセットします。完成した保存・読み込みダイアログとして扱わないでください。

## 4. アプリの起動方法

`hello_plita`のエントリーポイント全体は次のとおりです。

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

`App::new()`で`AppBuilder`を作り、`run()`で標準シェルを起動します。独自の状態を持つアプリでは、初期`Size`を受け取り`PlitaProgram`実装を返すファクトリーを`run_program`に渡します。`resize`・`handle_event`・`draw_list`を実装し、周期的な更新が必要なら`tick`を利用します。OSのイベント処理内から直接描画するのではなく、`UiResponse`で必要なUIの応答を返します。

`continuous_redraw(false)`では、更新や再描画要求に応じて描画します。連続描画は必要なアプリで有効にしてください。`draw_list`は描画命令を記述し、GPUへの送信はレンダラーが担当します。

## 5. 入力と補助ウィンドウ

UIの当たり判定とレイアウトにはplitaの論理座標を使います。DPI変換はウィンドウ層が担当します。ポインター、キーボード、IME、ファイルドロップのイベントがあります。受け取ったファイルパスの読み込み、解析、保存はアプリ側で実装してください。

`PointerDoubleClick`は2回目の`PointerUp`の後に届きます。同じボタンで完了した2回のクリックが500 ms以内、位置の差が6論理ピクセル以内のときに認識します。ドラッグ操作は除外し、各ネイティブウィンドウで独立して判定します。

独自アプリでは`AuxiliaryWindowDescriptor`で補助ウィンドウを定義し、そのリサイズ・イベント・描画リストのコールバックを実装できます。標準シェルの分離したメモリーエディターが扱うのはシェル内のデモ用バッファです。エミュレーターや別プロセスへ自動接続する機能ではありません。

`PlitaProgram::minimum_window_size()`と`auxiliary_window_minimum_size(id)`で、クライアント領域の最小サイズを論理座標で指定できます。既定の`None`では制限しません。`auxiliary_window_activation_request(id)`は任意の要求トークンを返します。明示的に復元・フォーカスを要求するたびに値を変えてください。同じ値のままでは繰り返しアクティブ化しません。補助ウィンドウの生成に失敗した場合は、定義を一度取り下げるかトークンを変えると再試行します。メインウィンドウは動作を継続します。

`auxiliary_draw_revision(id)`では、補助ウィンドウの描画リストを任意で保持できます。`Some(revision)`を返す場合は、ホバー・押下状態を含む表示内容の変化ごとに版番号を変え、`UiResponse`で再描画も要求してください。ネイティブのリサイズやDPI変更では保持内容を無効化します。アニメーションや共有画像のウィンドウでは、既定の`None`を返してください。最小化中は描画を省略し、サイズがゼロのリサイズイベントは無視します。

## 6. ドッキング、キャンバス、保存

`DockLayoutState`とドック座標の型でパネルの配置を表します。`DockLayoutProfile`はバージョン付きレイアウトプロファイルです。シェルはプロファイルのテキストを扱え、`AppBuilder::startup_layout_profile`で標準シェル起動時に復元できます。そのテキストをいつ、どこに保存するかはアプリで決めてください。メモリー内のレイアウトスロットはファイルへの永続保存の代わりにはなりません。

`CanvasDocument`と`LayerNode`は文書とレイヤーのモデルです。選択、矩形選択、スナップの補助機能と`CommandHistory`を使って編集操作を組み立てられます。`CommandRegistry`と`CommandDescriptor`はコマンドとショートカットの情報を記述します。完成したアプリ用ファイル形式や自動プロジェクト保存を提供するAPIではありません。モデルと独自コマンド、シリアライズ処理を接続してください。

`memory_viewer_address_at_point(rect, base_address, byte_count, position)`は、`draw_memory_viewer`に表示された16進数のバイト位置を`Option<u16>`のアドレスへ変換します。描画時と同じ矩形・開始アドレス、実際のバイト数、論理座標のポインター位置を渡してください。アドレス表示・ASCII欄・隙間・存在しないバイト・非表示行は`None`です。選択や書き込みはアプリ側で処理し、この関数自体はメモリーを変更しません。

## 7. フォントとアイコン

RobotoとRoboto Monoを`assets/fonts`に同梱しています。plitaは`fontdue`で文字をラスタライズし、小型ビットマップの代替描画も保持しています。インストール済みのシステムフォントも検索します。`PLITA_UI_FONT`・`PLITA_UI_FONT_FALLBACK`・`PLITA_MEMORY_FONT`でフォントファイルを指定する場合は、アプリ起動前に設定してください。表示したい文字を含むフォントが必要です。同梱のラテン文字用フォントだけでは日本語・中国語・韓国語を網羅しません。

`active_font_family`・`active_font_source`・`active_text_backend`・`active_memory_font_family`で使用中のフォントを調べられます。実行ファイルを移動する際はアセットの参照先を維持するか、適切なフォントパスを設定してください。ローダーにシステムフォントのパスが書かれていても、そのフォントファイルを同梱しているわけではありません。

LucideのSVGアイコンを52個同梱しています。`lucide_icon_names()`で対応名を取得し、`draw_lucide_icon`で描画します。`crates/plita_ui/assets/build_icons.py`でRustのパスデータを再生成する場合も、SVGとライセンス表示を保持してください。

## 8. 任意の描画ワーカー

`PlitaProgram`実装に次のメソッドを追加すると有効になります。

```rust
fn render_on_worker_thread(&self) -> bool {
    true
}
```

GPU処理と画面への提示を各ウィンドウのワーカーが担当します。ウィンドウ管理、入力、`tick`、描画リストの構築はイベントループ側に残ります。描画が遅いときは待機中の要求を最新フレームに集約するため、全フレームを保存する録画APIではありません。共有RGBA画像の全体更新は同じmutexの中で行い、ロックを短く保ってください。設定はレンダラー生成時に読み取るもので、実行中の切り替えスイッチではありません。既定は同期描画です。

レンダラーは不変RGBA画像の参照を保持してテクスチャキャッシュの識別衝突を防ぎ、頂点バッファと画像用の作業領域を再利用します。使われなくなった画像キャッシュは短いフレーム単位の保持期間後に解放します。共有RGBAデータはmutex内でコピーしてからGPUへ転送するため、更新も同じmutex内で行ってください。これらの内部変更に伴う既存の描画リスト呼び出しの変更は不要です。

検証上の制約（2026-10-18）：公開作業環境では、通常のワークスペース試験、GPUのオフスクリーン回帰試験2件、同期描画のネイティブウィンドウ試験が成功しました。一方、描画ワーカーのネイティブ試験は復元・リサイズ後にタイムアウトし、別のデスクトップ実行では異常終了しました。原因は未特定で、この環境でのワーカーの正常動作は確認できていません。安定動作が必要な場合は既定の同期描画を維持し、任意の描画ワーカーは対象環境で検証してから有効にしてください。

## 9. 任意のPython補助機能

Python 3.10以降と、1.8以上2未満のmaturinを適切なPython環境に用意してください。リポジトリのルートから次を実行します。

```powershell
cd crates/plita
maturin develop --features python
```

`python`機能は、共通の値の型を包むPyO3クラスと登録用の補助関数を提供します。RustのGUI全体が自動的にPythonアプリになるわけではありません。`#[pyclass]`や`#[pymodule]`を使うアプリのクレートには、マクロが`::pyo3`を参照するため、任意の`pyo3`依存関係も必要です。前の節のコマンドに戻る場合は、作業ディレクトリをリポジトリのルートに戻してください。

## 10. 問題の切り分けと検証

- ビルド失敗：最初のコンパイラーまたはリンカーのエラーを確認し、Rustの版と対象ツールチェーンを確認します。ロックファイルを保持してください。
- ウィンドウが出ない・GPU初期化失敗：ログとグラフィックスドライバーを確認します。ビルド成功だけではGUI動作の確認にはなりません。
- 文字が欠ける：対象文字を持つフォントを指定し、`active_font_source`を確認します。
- UIが止まる：イベント処理、`tick`、描画リスト生成を短く保ちます。描画ワーカーはアプリのロジックを並列化しません。
- ネイティブウィンドウの試験には操作可能なデスクトップが必要です。通常の単体試験とは別に表示を確認してください。

PowerShellで診断ログを有効にする例です。

```powershell
$env:RUST_LOG="debug,plita_window=trace,plita_render=trace"
cargo run --locked -p hello_plita
```

本書は公開ソースの説明であり、すべての環境での動作試験完了を保証するものではありません。`cargo doc --workspace --no-deps --locked`でAPI文書も生成できます。

動作するGPUがある環境では、外部データ不要の回帰試験を明示的に実行できます。`cargo test -p plita_render --locked offscreen_image_updates_and_draw_order -- --ignored --test-threads=1`と`cargo test -p plita_render --locked offscreen_cache_keeps_images_distinct_and_releases_old_sources -- --ignored --test-threads=1`です。通常のワークスペース試験はGPU試験とネイティブデスクトップ試験をスキップします。他の無効化済みベンチマークには外部入力と出力先の準備が必要なため、準備せずに全ignored試験を一括実行しないでください。

## 11. ライセンスと再配布

plitaのコードと本書はMITライセンスで、著作権者は2026 DAISUKE OBAです。コピーや主要部分の再配布ではMITの著作権表示と許諾文を保持してください。第三者のアセットには元のライセンスが適用されます。Roboto・Roboto MonoはOFL-1.1、LucideはISCで、由来となったFeatherのMIT表示も含みます。

[LICENSE](../../LICENSE)、[第三者の権利表示](../../THIRD_PARTY_NOTICES.md)、[依存関係の表示](../../licenses/DEPENDENCIES.md)、[アセットの出典](../../licenses/ASSET_PROVENANCE.json)を確認してください。フォント、アイコン、バイナリを配布するときは対応する表示を同梱します。macOSバイナリの配布前には、`dispatch`と`malloc_buf`について記録した独立した許諾文の不足を解決してください。このリポジトリはソースと表示文書の公開であり、将来のバイナリ配布では実際にリンクする依存関係の確認が必要です。

## 12. ソースへの案内

- [アプリビルダー](../../crates/plita_app/src/lib.rs)
- [ウィンドウとプログラムのインターフェース](../../crates/plita_window/src/lib.rs)
- [UIとモデルのAPI](../../crates/plita_ui/src/lib.rs)
- [レンダラー](../../crates/plita_render/src/lib.rs)
- [アイコンと生成方法](../../crates/plita_ui/assets/README.md)
- [描画ワーカーの詳細（日本語）](../render_worker_ja.md)
