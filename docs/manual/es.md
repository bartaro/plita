# plita — Manual de uso y desarrollo

[English](en.md) · [日本語](ja.md) · [한국어](ko.md) · [简体中文](zh-CN.md) · [繁體中文](zh-TW.md) · [Français](fr.md) · [Español](es.md) · [Deutsch](de.md)

DAISUKE OBA · Edición del código fuente: 2026-10-11 · Versión del paquete Cargo: 0.0.1

## 1. Contenido de la distribución

plita es una base de interfaz gráfica en Rust para aplicaciones creativas de escritorio. Este repositorio contiene cinco crates del framework y tres ejemplos ejecutables. Ofrece ventanas nativas, gestión de entradas, dibujo mediante GPU, widgets, acoplamiento de paneles y modelos de lienzo. No incluye interfaces específicas de emuladores, ROM ni ejecutables precompilados.

- `plita`: API pública, reexportaciones mediante `prelude` y utilidades opcionales de Python.
- `plita_app`: constructor `App` y configuración de inicio.
- `plita_window`: bucle de eventos nativo e interfaz `PlitaProgram`.
- `plita_render`: recursos de GPU y renderizado.
- `plita_ui`: geometría, listas de dibujo, widgets, acoplamiento, lienzo e historial.

## 2. Requisitos y compilación

Instale Git, Rust 1.92 o posterior, y el enlazador y las herramientas nativas de la plataforma de destino. Para el destino MSVC de Windows, instale las herramientas de C++ de Visual Studio Build Tools y el SDK de Windows. Abrir una ventana requiere una GPU y un controlador compatibles. La primera compilación descarga las dependencias de Cargo; conserve `Cargo.lock` para poder reproducirla.

```powershell
git clone https://github.com/bartaro/plita.git
cd plita
cargo check --workspace --locked
cargo test --workspace --locked
```

El espacio de trabajo activa explícitamente los motores DX12, GLES y Vulkan de wgpu. Metal no está activado en el manifiesto. No presuponga que se han validado todos los sistemas operativos y configuraciones de GPU; las dependencias y bibliotecas de pantalla de cada plataforma pueden requerir preparación adicional. Los comandos anteriores son instrucciones de verificación, no una afirmación de que todas las plataformas hayan superado las pruebas.

## 3. Ejecutar los ejemplos

Ejecute un comando cada vez desde la raíz del repositorio. Cierre la ventana antes de iniciar el siguiente ejemplo.

```powershell
cargo run --locked -p hello_plita
cargo run --locked -p docking_demo
cargo run --locked -p canvas_demo
```

Los tres ejemplos inician actualmente el mismo `CreativeShell`. Cambian el título de la ventana y, en `canvas_demo`, su tamaño inicial. Sus nombres no identifican tres aplicaciones completas diferentes. La interfaz común muestra menús, herramientas, un lienzo con cuadrícula y mesa de trabajo, un inspector, una línea de tiempo y una barra de estado. Explore la interfaz compartida y consulte el código al integrar una función en su aplicación.

Cuando los campos de texto y memoria no tengan el foco, pruebe estos controles:

- `1` / `V`: selección; `2` / `H`: desplazamiento de la vista; `3` / `R`: rectángulo; `4` / `T`: texto; `5` / `G`: cuadrícula. Arrastre el lienzo con la herramienta de desplazamiento, use la rueda para ampliar y pulse `F` para restablecer la vista.
- Seleccione un objeto y arrastre su cuerpo o los controles de las esquinas. `Ctrl+D` duplica; `Delete` / `Backspace` elimina; las flechas mueven 1 unidad del mundo, o 10 con `Shift`. `Ctrl+Z` deshace; `Ctrl+Y` / `Ctrl+Shift+Z` rehace.
- `Ctrl+1` a `Ctrl+6` seleccionan Propiedades, Capas, Memoria, Línea de tiempo, Registro y Diagnóstico. `Ctrl+Shift+1` a `Ctrl+Shift+6` abren paneles flotantes; `Ctrl+0` los cierra. `M` muestra u oculta el editor de memoria.
- En esta demostración, `Ctrl+S` solo informa del tamaño de una instantánea en la barra de estado; no escribe un archivo. `Ctrl+O` restablece el documento de demostración. No son diálogos completos de apertura o guardado.

## 4. Iniciar una aplicación

Este es el punto de entrada completo de `hello_plita`:

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

`App::new()` crea un `AppBuilder`. `run()` inicia la interfaz incorporada. Para usar su propio estado de aplicación, pase a `run_program` una función de fábrica que reciba el `Size` inicial y devuelva una implementación de `PlitaProgram`. Implemente `resize`, `handle_event` y `draw_list`; utilice `tick` cuando necesite actualizaciones periódicas. Devuelva la respuesta de interfaz necesaria mediante `UiResponse`, en vez de dibujar directamente dentro de una devolución de llamada del sistema operativo.

Con `continuous_redraw(false)`, el dibujo responde a actualizaciones y solicitudes de redibujado. Active el redibujado continuo solo cuando sea necesario. `draw_list` describe las órdenes de dibujo; el renderizador se encarga de enviarlas a la GPU.

## 5. Entrada y ventanas auxiliares

Use las coordenadas lógicas de plita para las pruebas de posición y la disposición de la interfaz; la capa de ventanas realiza la conversión de DPI. Los eventos abarcan puntero, teclado, IME y archivos arrastrados. La aplicación debe implementar la apertura, el análisis y el guardado del archivo cuya ruta recibe.

`PointerDoubleClick` llega después del segundo `PointerUp`. Se requieren dos clics completados con el mismo botón, separados por un máximo de 500 ms y a una distancia máxima de 6 píxeles lógicos. Los gestos de arrastre se excluyen. Cada ventana nativa mantiene su propia detección.

Una aplicación puede definir ventanas auxiliares con `AuxiliaryWindowDescriptor` e implementar sus funciones de cambio de tamaño, eventos y listas de dibujo. El editor de memoria independiente de la interfaz incorporada utiliza su propio búfer de demostración; no se conecta automáticamente a un emulador ni a otro proceso.

## 6. Acoplamiento, lienzo y persistencia

`DockLayoutState` y los tipos geométricos de acoplamiento describen la disposición de los paneles. `DockLayoutProfile` representa un perfil de disposición con versión. La interfaz incorporada admite el perfil como texto, y `AppBuilder::startup_layout_profile` lo restaura al iniciarla. La aplicación decide cuándo y dónde guardar ese texto. Las posiciones de almacenamiento en memoria no sustituyen el guardado permanente en archivos.

`CanvasDocument` y `LayerNode` ofrecen los modelos de documento y capas. Las utilidades de selección, selección rectangular y ajuste, junto con `CommandHistory`, permiten construir operaciones de edición. `CommandRegistry` y `CommandDescriptor` describen comandos y atajos. Estas API no proporcionan un formato de archivo completo ni un sistema automático de guardado de proyectos. Conecte los modelos a sus propios comandos y a su serialización.

## 7. Fuentes e iconos

Roboto y Roboto Mono se incluyen en `assets/fonts`. plita rasteriza texto con `fontdue` y conserva una pequeña fuente de mapa de bits como alternativa. También busca fuentes instaladas en el sistema. `PLITA_UI_FONT`, `PLITA_UI_FONT_FALLBACK` y `PLITA_MEMORY_FONT` permiten seleccionar archivos de fuentes; configure estas variables antes de iniciar la aplicación. La fuente debe contener los caracteres que desea mostrar. Las fuentes latinas incluidas no cubren todos los caracteres chinos, japoneses y coreanos.

`active_font_family`, `active_font_source`, `active_text_backend` y `active_memory_font_family` ayudan a diagnosticar la selección. Si mueve un ejecutable, mantenga accesible el directorio de recursos o configure una ruta de fuente adecuada. Que el cargador mencione una ruta de fuente del sistema no significa que se distribuya ese archivo.

El repositorio incluye 52 iconos SVG de Lucide. `lucide_icon_names()` enumera sus nombres y `draw_lucide_icon` los dibuja. Conserve los SVG y sus avisos de licencia cuando regenere los trazados de Rust con `crates/plita_ui/assets/build_icons.py`.

## 8. Hilo opcional de renderizado

Añada este método a su implementación de `PlitaProgram` para activarlo:

```rust
fn render_on_worker_thread(&self) -> bool {
    true
}
```

Un hilo por ventana se ocupa de las operaciones de GPU y de presentar la imagen. La gestión de ventanas, la entrada, `tick` y la creación de listas de dibujo permanecen en el hilo del bucle de eventos. Si el renderizado se retrasa, las solicitudes pendientes se agrupan para conservar el fotograma más reciente; no es una API para grabar todos los fotogramas. Actualice toda la imagen RGBA compartida dentro del mismo mutex y mantenga breve el bloqueo. La opción se lee al crear el renderizador y no sirve para cambiar de modo durante la ejecución. El modo predeterminado es síncrono.

## 9. Utilidades opcionales de Python

Prepare Python 3.10 o posterior y maturin de versión igual o superior a 1.8 e inferior a 2 en un entorno de Python adecuado. Desde la raíz del repositorio:

```powershell
cd crates/plita
maturin develop --features python
```

La función `python` proporciona clases envoltorio de PyO3 para valores comunes y utilidades de registro. No convierte automáticamente toda una interfaz Rust en una aplicación Python completa. Los crates que usan `#[pyclass]` o `#[pymodule]` siguen necesitando su propia dependencia opcional de `pyo3`, porque esas macros hacen referencia a `::pyo3`. Vuelva a la raíz del repositorio antes de utilizar los comandos anteriores.

## 10. Diagnóstico y verificación

- Error de compilación: lea el primer error del compilador o enlazador, compruebe Rust y la cadena de herramientas del destino, y conserve el archivo de bloqueo.
- No aparece la ventana o falla la inicialización de GPU: revise los registros y el controlador gráfico. Una compilación correcta no verifica el funcionamiento de la interfaz.
- Faltan caracteres: elija una fuente con los glifos necesarios y compruebe `active_font_source`.
- La interfaz se bloquea: reduzca el trabajo de los eventos, `tick` y la creación de listas de dibujo. El hilo de renderizado no paraleliza la lógica de la aplicación.
- Las pruebas de ventanas nativas requieren un escritorio interactivo. Las pruebas unitarias comunes no sustituyen la comprobación visual.

Para activar los registros de diagnóstico en PowerShell:

```powershell
$env:RUST_LOG="debug,plita_window=trace,plita_render=trace"
cargo run --locked -p hello_plita
```

Este manual describe el código publicado sin certificar pruebas de ejecución en todas las plataformas. También puede generar documentación de la API con `cargo doc --workspace --no-deps --locked`.

## 11. Licencia y redistribución

El código de plita y estos manuales se distribuyen bajo la licencia MIT, copyright (c) 2026 DAISUKE OBA. Conserve el aviso de copyright y el texto de autorización MIT al redistribuir copias o partes sustanciales. Los recursos de terceros mantienen sus propias licencias: Roboto y Roboto Mono usan OFL-1.1; Lucide usa ISC e incluye el aviso MIT heredado de Feather.

Consulte [LICENSE](../../LICENSE), los [avisos de terceros](../../THIRD_PARTY_NOTICES.md), los [avisos de dependencias](../../licenses/DEPENDENCIES.md) y la [procedencia de recursos](../../licenses/ASSET_PROVENANCE.json). Adjunte los avisos pertinentes al distribuir fuentes, iconos y binarios. Antes de distribuir binarios de macOS, resuelva la falta de textos de autorización independientes registrada para `dispatch` y `malloc_buf`. Este repositorio publica código fuente y avisos; una futura distribución binaria requiere revisar las dependencias que realmente se enlacen.

## 12. Guía de archivos fuente

- [Constructor de aplicaciones](../../crates/plita_app/src/lib.rs)
- [Interfaz de ventanas y programas](../../crates/plita_window/src/lib.rs)
- [API de interfaz y modelos](../../crates/plita_ui/src/lib.rs)
- [Renderizador](../../crates/plita_render/src/lib.rs)
- [Iconos y generación](../../crates/plita_ui/assets/README.md)
- [Detalles del hilo de renderizado, en japonés](../render_worker_ja.md)
