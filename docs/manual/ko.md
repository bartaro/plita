# PLITA — 사용자 및 개발자 설명서

[English](en.md) · [日本語](ja.md) · [한국어](ko.md) · [简体中文](zh-CN.md) · [繁體中文](zh-TW.md) · [Français](fr.md) · [Español](es.md) · [Deutsch](de.md)

DAISUKE OBA · 소스 배포판 2026-10-11 · Cargo 패키지 버전 0.0.1

## 1. 포함된 구성 요소

PLITA는 데스크톱 제작 도구를 위한 Rust GUI 기반 라이브러리입니다. 이 저장소에는 프레임워크 크레이트 5개와 실행 가능한 예제 3개가 들어 있습니다. 네이티브 창, 입력 처리, GPU 렌더링, 위젯, 도킹 및 캔버스 모델을 제공합니다. 개별 에뮬레이터의 GUI, ROM, 빌드된 실행 파일은 포함하지 않습니다.

- `plita`: 공개 API와 `prelude` 재노출, 선택적 Python 도우미.
- `plita_app`: `App` 빌더와 시작 설정.
- `plita_window`: 네이티브 이벤트 루프와 `PlitaProgram` 인터페이스.
- `plita_render`: GPU 리소스와 렌더링.
- `plita_ui`: 좌표, 그리기 목록, 위젯, 도킹, 캔버스 및 이력 모델.

## 2. 요구 사항과 빌드

Git, Rust 1.92 이상, 대상 환경용 링커와 개발 도구를 설치하세요. Windows MSVC 대상에는 Visual Studio Build Tools의 C++ 개발 도구와 Windows SDK가 필요합니다. 창을 표시하려면 호환되는 GPU와 드라이버도 필요합니다. 첫 빌드에서는 Cargo 의존성을 다운로드합니다. 재현 가능한 빌드를 위해 `Cargo.lock`을 유지하세요.

```powershell
git clone https://github.com/bartaro/plita.git
cd plita
cargo check --workspace --locked
cargo test --workspace --locked
```

워크스페이스는 wgpu의 DX12, GLES, Vulkan 백엔드를 명시적으로 활성화합니다. 매니페스트에서 Metal은 활성화하지 않습니다. 모든 운영 체제와 GPU 구성이 검증되었다고 가정하지 마세요. 대상별 의존성과 디스플레이 라이브러리에 추가 설정이 필요할 수 있습니다. 위 명령은 검증 절차이며 모든 환경의 시험 통과를 뜻하지 않습니다.

## 3. 예제 실행

저장소 루트에서 한 번에 하나씩 실행하세요. 다음 예제를 실행하기 전에 창을 닫으세요.

```powershell
cargo run --locked -p hello_plita
cargo run --locked -p docking_demo
cargo run --locked -p canvas_demo
```

현재 세 예제는 모두 같은 `CreativeShell`을 실행합니다. 창 제목이 다르며 `canvas_demo`는 초기 크기도 다릅니다. 이름이 서로 다른 완성된 애플리케이션을 의미하지는 않습니다. 공통 셸에는 메뉴 모음, 도구 모음, 격자와 아트보드가 있는 캔버스, 인스펙터, 타임라인 및 상태 표시줄이 있습니다. 공통 UI를 살펴보고 개별 기능을 통합할 때 소스를 참고하세요.

텍스트 및 메모리 입력란에 포커스가 없을 때 다음 조작을 사용할 수 있습니다.

- `1` / `V`: 선택, `2` / `H`: 이동, `3` / `R`: 사각형, `4` / `T`: 텍스트, `5` / `G`: 격자. 이동 도구로 캔버스를 드래그하고 휠로 확대·축소하며 `F`로 화면을 초기화합니다.
- 객체나 모서리 핸들을 선택해 드래그합니다. `Ctrl+D`는 복제, `Delete` / `Backspace`는 삭제, 방향키는 월드 좌표 1단위 이동, `Shift` + 방향키는 10단위 이동입니다. `Ctrl+Z`는 실행 취소, `Ctrl+Y` / `Ctrl+Shift+Z`는 다시 실행입니다.
- `Ctrl+1`부터 `Ctrl+6`까지는 속성, 레이어, 메모리, 타임라인, 로그, 진단 패널을 선택합니다. `Ctrl+Shift+1`부터 `Ctrl+Shift+6`까지는 플로팅 패널을 열고 `Ctrl+0`은 닫습니다. `M`은 메모리 편집기 표시를 전환합니다.
- 이 데모에서 `Ctrl+S`는 상태 표시줄에 스냅샷 크기만 표시하며 파일을 저장하지 않습니다. `Ctrl+O`는 데모 문서를 초기화합니다. 완성된 파일 저장·열기 대화 상자로 생각하지 마세요.

## 4. 애플리케이션 시작

다음은 `hello_plita`의 전체 진입점입니다.

```rust
use plita::prelude::*;

fn main() -> Result<()> {
    App::new()
        .title("PLITA UI v1.0 - Creative Shell")
        .window_size(1280, 800)
        .clear_color(ClearColor::rgb(0.105, 0.111, 0.125))
        .continuous_redraw(false)
        .run()
}
```

`App::new()`는 `AppBuilder`를 만들고 `run()`은 기본 셸을 실행합니다. 자체 상태를 사용하는 앱은 초기 `Size`를 받아 `PlitaProgram` 구현을 반환하는 팩터리를 `run_program`에 전달합니다. `resize`, `handle_event`, `draw_list`를 구현하고 주기적 갱신이 필요하면 `tick`을 사용하세요. OS 이벤트 콜백에서 직접 그리는 대신 `UiResponse`로 필요한 UI 응답을 반환하세요.

`continuous_redraw(false)`에서는 갱신과 다시 그리기 요청에 따라 화면을 그립니다. 앱에 필요한 경우에만 연속 다시 그리기를 활성화하세요. `draw_list`는 그리기 명령을 기술하고 GPU 제출은 렌더러가 담당합니다.

## 5. 입력과 보조 창

UI 적중 검사와 배치에는 PLITA의 논리 좌표를 사용하세요. DPI 변환은 창 계층이 처리합니다. 포인터, 키보드, IME 및 파일 드롭 이벤트를 제공합니다. 전달받은 파일 경로를 열고 분석하고 저장하는 작업은 앱에서 구현해야 합니다.

`PointerDoubleClick`은 두 번째 `PointerUp` 뒤에 전달됩니다. 같은 버튼으로 완료한 두 클릭의 간격이 500 ms 이내이고 위치 차이가 6 논리 픽셀 이내여야 합니다. 드래그는 제외하며 각 네이티브 창은 독립적으로 판정합니다.

`AuxiliaryWindowDescriptor`로 보조 창을 정의하고 해당 창의 크기 변경, 이벤트 및 그리기 목록 콜백을 구현할 수 있습니다. 셸의 분리된 메모리 편집기는 셸이 보유한 데모 버퍼를 다룹니다. 에뮬레이터나 다른 프로세스에 자동으로 연결하지 않습니다.

## 6. 도킹, 캔버스와 저장

`DockLayoutState`와 도킹 기하 타입은 패널 배치를 나타냅니다. `DockLayoutProfile`은 버전 정보가 있는 배치 프로필입니다. 셸은 프로필 텍스트를 처리하며 `AppBuilder::startup_layout_profile`로 기본 셸 시작 시 복원할 수 있습니다. 텍스트를 언제 어디에 저장할지는 앱이 결정해야 합니다. 메모리의 배치 슬롯은 영구 파일 저장을 대신하지 않습니다.

`CanvasDocument`와 `LayerNode`는 문서와 레이어 모델입니다. 선택, 영역 선택, 스냅 도우미와 `CommandHistory`로 편집 동작을 구성할 수 있습니다. `CommandRegistry`와 `CommandDescriptor`는 명령과 단축키 정보를 나타냅니다. 이 API는 완성된 앱 파일 형식이나 자동 프로젝트 저장 기능을 제공하지 않습니다. 자체 명령과 직렬화에 모델을 연결하세요.

## 7. 글꼴과 아이콘

Roboto와 Roboto Mono를 `assets/fonts`에 포함합니다. 텍스트는 `fontdue`로 래스터화하며 작은 비트맵 대체 글꼴도 유지합니다. 설치된 시스템 글꼴도 검색합니다. `PLITA_UI_FONT`, `PLITA_UI_FONT_FALLBACK`, `PLITA_MEMORY_FONT`로 파일을 지정할 때는 앱 실행 전에 설정하세요. 글꼴에는 표시할 문자가 있어야 합니다. 포함된 라틴 문자 글꼴만으로는 한국어·중국어·일본어를 모두 표시할 수 없습니다.

`active_font_family`, `active_font_source`, `active_text_backend`, `active_memory_font_family`로 글꼴 선택을 진단할 수 있습니다. 실행 파일을 옮기면 자산 경로를 유지하거나 적절한 글꼴 경로를 설정하세요. 로더에 시스템 글꼴 경로가 있다고 해서 해당 글꼴 파일이 배포에 포함된 것은 아닙니다.

Lucide SVG 아이콘 52개를 포함합니다. `lucide_icon_names()`로 이름을 확인하고 `draw_lucide_icon`으로 그립니다. `crates/plita_ui/assets/build_icons.py`로 Rust 경로 데이터를 다시 생성할 때도 SVG와 라이선스 고지를 유지하세요.

## 8. 선택적 렌더링 작업 스레드

`PlitaProgram` 구현에 다음 메서드를 추가하면 활성화됩니다.

```rust
fn render_on_worker_thread(&self) -> bool {
    true
}
```

창마다 작업 스레드가 GPU 처리와 화면 표시를 맡습니다. 창 관리, 입력, `tick`, 그리기 목록 생성은 이벤트 루프 스레드에 남습니다. 렌더링이 느리면 대기 요청을 최신 프레임으로 합치므로 모든 프레임을 기록하는 API가 아닙니다. 공유 RGBA 이미지 전체를 같은 mutex 안에서 갱신하고 잠금 시간을 짧게 유지하세요. 설정은 렌더러 생성 시 읽으며 실행 중 전환 스위치가 아닙니다. 기본값은 동기 렌더링입니다.

## 9. 선택적 Python 도우미

적절한 Python 환경에 Python 3.10 이상과 maturin 1.8 이상, 2 미만을 준비하세요. 저장소 루트에서 실행합니다.

```powershell
cd crates/plita
maturin develop --features python
```

`python` 기능은 공통 값의 PyO3 래퍼와 등록 도우미를 제공합니다. Rust GUI 전체를 완전한 Python 앱으로 자동 변환하지 않습니다. `#[pyclass]` 또는 `#[pymodule]`을 쓰는 앱 크레이트에는 매크로가 `::pyo3`를 참조하므로 자체 선택적 `pyo3` 의존성도 필요합니다. 앞의 명령을 다시 사용할 때는 저장소 루트로 돌아가세요.

## 10. 문제 해결과 검증

- 빌드 실패: 첫 컴파일러 또는 링커 오류를 읽고 Rust 버전과 대상 도구 체인을 확인하세요. 잠금 파일을 유지하세요.
- 창이 열리지 않거나 GPU 초기화 실패: 로그와 그래픽 드라이버를 확인하세요. 빌드 성공만으로 GUI 동작이 검증되지는 않습니다.
- 문자가 빠짐: 해당 문자를 포함한 글꼴을 선택하고 `active_font_source`를 확인하세요.
- UI 멈춤: 이벤트 처리, `tick`, 그리기 목록 생성을 짧게 유지하세요. 렌더링 작업 스레드는 앱 로직을 병렬화하지 않습니다.
- 네이티브 창 시험에는 대화형 데스크톱이 필요합니다. 일반 단위 시험은 시각적 검증을 대신하지 않습니다.

PowerShell에서 진단 로그를 활성화하는 방법입니다.

```powershell
$env:RUST_LOG="debug,plita_window=trace,plita_render=trace"
cargo run --locked -p hello_plita
```

이 설명서는 공개 소스를 설명하며 모든 플랫폼의 실행 시험을 보증하지 않습니다. `cargo doc --workspace --no-deps --locked`로 API 문서도 생성할 수 있습니다.

## 11. 라이선스와 재배포

PLITA 코드와 이 설명서는 MIT 라이선스이며 저작권 표시는 (c) 2026 DAISUKE OBA입니다. 복제본이나 주요 부분을 재배포할 때 MIT 저작권 및 허가 고지를 유지하세요. 타사 자산은 자체 라이선스를 유지합니다. Roboto와 Roboto Mono는 OFL-1.1, Lucide는 ISC이며 원래 Feather의 MIT 고지도 포함합니다.

[LICENSE](../../LICENSE), [타사 고지](../../THIRD_PARTY_NOTICES.md), [의존성 고지](../../licenses/DEPENDENCIES.md), [자산 출처](../../licenses/ASSET_PROVENANCE.json)를 확인하세요. 글꼴, 아이콘, 바이너리를 배포할 때 관련 고지를 포함하세요. macOS 바이너리를 배포하기 전에 `dispatch`와 `malloc_buf`에 기록된 독립된 허가문 누락을 해결해야 합니다. 이 저장소는 소스와 고지를 공개하며 향후 바이너리 배포에는 실제로 링크되는 의존성 검토가 필요합니다.

## 12. 소스 안내

- [애플리케이션 빌더](../../crates/plita_app/src/lib.rs)
- [창과 프로그램 인터페이스](../../crates/plita_window/src/lib.rs)
- [UI와 모델 API](../../crates/plita_ui/src/lib.rs)
- [렌더러](../../crates/plita_render/src/lib.rs)
- [아이콘과 생성 방법](../../crates/plita_ui/assets/README.md)
- [렌더링 작업 스레드 상세 설명(일본어)](../render_worker_ja.md)
