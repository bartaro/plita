# plita — Benutzer- und Entwicklerhandbuch

[English](en.md) · [日本語](ja.md) · [한국어](ko.md) · [简体中文](zh-CN.md) · [繁體中文](zh-TW.md) · [Français](fr.md) · [Español](es.md) · [Deutsch](de.md)

DAISUKE OBA · Quelltextausgabe vom 2026-10-25 · Cargo-Paketversion 0.0.1

## 1. Lieferumfang

plita ist eine Rust-GUI-Grundlage für kreative Desktop-Anwendungen. Dieses Repository enthält fünf Framework-Crates und drei ausführbare Beispiele. Es stellt native Fenster, Eingabeverarbeitung, GPU-Zeichnen, Widgets, andockbare Bedienfelder und Canvas-Modelle bereit. Anwendungsspezifische Emulator-Oberflächen, ROMs und vorkompilierte Programme gehören nicht zum Lieferumfang.

- `plita`: öffentliche API, `prelude`-Reexporte und optionale Python-Hilfsfunktionen.
- `plita_app`: `App`-Builder und Startkonfiguration.
- `plita_window`: native Ereignisschleife und Schnittstelle `PlitaProgram`.
- `plita_render`: GPU-Ressourcen und Rendering.
- `plita_ui`: Geometrie, Zeichenlisten, Widgets, Docking-, Canvas- und Verlaufsmodelle.

## 2. Voraussetzungen und Build

Installieren Sie Git, Rust ab Version 1.92 sowie Linker und native Entwicklungswerkzeuge für das Zielsystem. Unter Windows mit dem MSVC-Ziel werden die C++-Werkzeuge der Visual Studio Build Tools und das Windows SDK benötigt. Ein Fenster erfordert eine kompatible GPU mit passendem Treiber. Beim ersten Build lädt Cargo Abhängigkeiten herunter. Behalten Sie `Cargo.lock` für reproduzierbare Builds bei.

```powershell
git clone https://github.com/bartaro/plita.git
cd plita
cargo check --workspace --locked
cargo test --workspace --locked
```

Der Workspace aktiviert ausdrücklich die wgpu-Backends DX12, GLES und Vulkan. Metal ist im Manifest nicht aktiviert. Gehen Sie nicht davon aus, dass jedes Betriebssystem und jede GPU-Konfiguration geprüft wurde. Zielspezifische Abhängigkeiten und Anzeigebibliotheken können zusätzliche Einrichtung erfordern. Die obigen Befehle sind Prüfanweisungen und keine Bestätigung erfolgreicher Tests auf allen Plattformen.

## 3. Beispiele starten

Führen Sie jeweils einen Befehl im Stammverzeichnis des Repositorys aus. Schließen Sie das Fenster, bevor Sie das nächste Beispiel starten.

```powershell
cargo run --locked -p hello_plita
cargo run --locked -p docking_demo
cargo run --locked -p canvas_demo
```

Alle drei Beispiele starten derzeit dieselbe `CreativeShell`. Sie unterscheiden sich im Fenstertitel und bei `canvas_demo` auch in der Anfangsgröße. Die Namen bezeichnen keine drei eigenständigen fertigen Anwendungen. Die gemeinsame Oberfläche zeigt Menüleiste, Werkzeuge, Canvas mit Raster und Zeichenfläche, Inspektor, Zeitleiste und Statusleiste. Erkunden Sie diese Oberfläche und lesen Sie beim Einbau einer Funktion auch den Quelltext.

Wenn Text- und Speichereingaben keinen Fokus haben, können Sie diese Bedienung ausprobieren:

- `1` / `V`: Auswahl; `2` / `H`: Ansicht verschieben; `3` / `R`: Rechteck; `4` / `T`: Text; `5` / `G`: Raster. Ziehen Sie den Canvas mit dem Verschiebewerkzeug, zoomen Sie mit dem Mausrad und setzen Sie die Ansicht mit `F` zurück.
- Wählen Sie ein Objekt und ziehen Sie es oder seine Eckgriffe. `Ctrl+D` dupliziert; `Delete` / `Backspace` löscht; Pfeiltasten verschieben um 1 Welteinheit, mit `Shift` um 10. `Ctrl+Z` macht rückgängig; `Ctrl+Y` / `Ctrl+Shift+Z` stellt wieder her.
- `Ctrl+1` bis `Ctrl+6` wählen Eigenschaften, Ebenen, Speicher, Zeitleiste, Protokoll und Diagnose. `Ctrl+Shift+1` bis `Ctrl+Shift+6` öffnen schwebende Bedienfelder; `Ctrl+0` schließt sie. `M` blendet den Speichereditor ein oder aus.
- In dieser Demo zeigt `Ctrl+S` nur die Größe eines Schnappschusses in der Statusleiste an und schreibt keine Datei. `Ctrl+O` setzt das Demo-Dokument zurück. Diese Kürzel sind keine vollständigen Dateiöffnungs- oder Speicherdialoge.

## 4. Eine Anwendung starten

Dies ist der vollständige Einstiegspunkt von `hello_plita`:

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

`App::new()` erzeugt einen `AppBuilder`. `run()` startet die eingebaute Oberfläche. Für einen eigenen Anwendungszustand übergeben Sie an `run_program` eine Factory, die die anfängliche `Size` erhält und eine Implementierung von `PlitaProgram` zurückgibt. Implementieren Sie `resize`, `handle_event` und `draw_list`; nutzen Sie `tick` für regelmäßige Aktualisierungen. Geben Sie die nötige UI-Reaktion über `UiResponse` zurück, statt direkt in einem Betriebssystem-Ereignisrückruf zu zeichnen.

Mit `continuous_redraw(false)` wird aufgrund von Aktualisierungen und Neuzeichnungsanforderungen gezeichnet. Aktivieren Sie kontinuierliches Neuzeichnen nur bei Bedarf. `draw_list` beschreibt Zeichenbefehle; der Renderer übernimmt deren Übergabe an die GPU.

## 5. Eingaben und Zusatzfenster

Verwenden Sie die logischen Koordinaten von plita für Treffertests und Layout. Die Fensterschicht übernimmt die DPI-Umrechnung. Ereignisse umfassen Zeiger, Tastatur, IME und abgelegte Dateien. Das Öffnen, Auswerten und Speichern einer empfangenen Datei bleibt Aufgabe der Anwendung.

`PointerDoubleClick` folgt auf das zweite `PointerUp`. Erforderlich sind zwei abgeschlossene Klicks mit derselben Taste innerhalb von 500 ms und mit höchstens 6 logischen Pixeln Abstand. Ziehgesten werden ausgeschlossen. Jedes native Fenster führt seine eigene Erkennung.

Eigene Anwendungen können Zusatzfenster mit `AuxiliaryWindowDescriptor` beschreiben und Rückrufe für Größenänderung, Ereignisse und Zeichenlisten implementieren. Der abgetrennte Speichereditor der eingebauten Oberfläche bearbeitet deren Demonstrationspuffer. Er verbindet sich nicht automatisch mit einem Emulator oder einem anderen Prozess.

`PlitaProgram::minimum_window_size()` und `auxiliary_window_minimum_size(id)` legen die Mindestgröße des Clientbereichs in logischen Koordinaten fest. Der Standardwert `None` setzt keine Grenze. `auxiliary_window_activation_request(id)` liefert ein optionales Anforderungstoken: Ändern Sie es bei jeder beabsichtigten Wiederherstellung oder Fokussierung. Ein unverändertes Token aktiviert das Fenster nicht wiederholt. Nach einem Fehler beim Erstellen eines Zusatzfensters ziehen Sie dessen Definition zurück oder ändern das Token, um es erneut zu versuchen; das Hauptfenster läuft weiter.

`auxiliary_draw_revision(id)` erlaubt es, die Zeichenliste eines Zusatzfensters beizubehalten. Bei `Some(revision)` ändern Sie die Revision bei jeder sichtbaren Änderung, einschließlich Hover- und Druckzuständen, und fordern über `UiResponse` auch ein Neuzeichnen an. Native Größen- oder DPI-Änderungen machen die Liste ungültig. Für Animationen und gemeinsam genutzte Bilder bleibt der Standardwert `None` geeignet. Minimierte Fenster werden nicht gerendert; Größenänderungen auf null werden ignoriert.

`PlitaProgram::ime_allowed()` liefert standardmäßig `true`. Geben Sie `false` zurück, wenn Ihre Anwendung physische Tasten ohne Abfangen durch die Host-IME benötigt. Diese Einstellung wird beim Erstellen des Hauptfensters und der Zusatzfenster gelesen; sie ist kein Laufzeitschalter und verändert den Eingabekontext separater nativer Dateidialoge nicht. Texteingabeprogramme sollten den Standard beibehalten.

`scale_factor_changed(scale_factor)` meldet die physischen Pixel pro logischer Einheit des Hauptfensters. Der Aufruf erfolgt vor dem ersten Zeichnen und vor `resize`, wenn die DPI aktualisiert oder geändert wird. Speichern Sie den Wert zum Ausrichten pixelbasierter Inhalte; Layout und Trefferprüfung verwenden weiterhin logische Koordinaten. Dieser Callback meldet nicht die eigenständige DPI eines Zusatzfensters.

## 6. Docking, Canvas und Speicherung

`DockLayoutState` und die Docking-Geometrietypen beschreiben die Anordnung der Bedienfelder. `DockLayoutProfile` ist ein versioniertes Layoutprofil. Die eingebaute Oberfläche verarbeitet Profiltext; `AppBuilder::startup_layout_profile` stellt ihn beim Start dieser Oberfläche wieder her. Wann und wo der Text gespeichert wird, entscheidet die Anwendung. Layoutplätze im Arbeitsspeicher ersetzen keine dauerhafte Speicherung in Dateien.

`CanvasDocument` und `LayerNode` stellen Dokument- und Ebenenmodelle bereit. Auswahl, Rechteckauswahl und Einrasthilfen ermöglichen zusammen mit `CommandHistory` die Umsetzung von Bearbeitungsfunktionen. `CommandRegistry` und `CommandDescriptor` beschreiben Befehle und Tastenkürzel. Diese APIs liefern weder ein vollständiges Anwendungsdateiformat noch eine automatische Projektspeicherung. Verbinden Sie die Modelle mit eigenen Befehlen und Ihrer Serialisierung.

`memory_viewer_address_at_point(rect, base_address, byte_count, position)` ordnet einem sichtbaren Hexadezimalbyte in `draw_memory_viewer` eine Adresse vom Typ `Option<u16>` zu. Übergeben Sie dasselbe Rechteck und dieselbe Basisadresse wie beim Zeichnen, die tatsächliche Byteanzahl und die logische Zeigerposition. Adressbeschriftungen, ASCII-Text, Zwischenräume, fehlende Bytes und ausgeblendete Zeilen ergeben `None`. Auswahl und Schreibzugriffe übernimmt die Anwendung; diese Funktion verändert keinen Speicher.

## 7. Schaltflächen für Dropdown-Menüs

`draw_menu_button` zeichnet die Schaltfläche, ihre Beschriftung und einen geometrischen Pfeil am rechten Rand. Der Pfeil ist unabhängig von der Schrift: Hängen Sie kein `v` oder Pfeilzeichen an die Beschriftung an. Bei `expanded = false` zeigt er nach unten; setzen Sie den Wert während eines geöffneten Menüs auf `true`, damit er nach oben zeigt.

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

Dieser Ausschnitt erzeugt Zeichenbefehle innerhalb einer `draw_list`-Implementierung und öffnet allein kein Fenster. Verfolgen Sie Zeiger und Tastendruck mit `ButtonInteractionState`, schalten Sie den Menüzustand nach Drücken und Loslassen auf derselben Schaltfläche um und übergeben Sie ihn als `expanded`. Beschriftung und Pfeil verwenden das ursprüngliche Rechteck als gemeinsame Klickfläche. Die Anwendung zeichnet die Menüeinträge und verarbeitet Auswahl und Schließen.

`MenuButtonStyle` enthält Oberfläche, Vordergrundfarbe und Textskalierung für den aktuellen Zustand. `ButtonVisualState::Pressed` verschiebt Oberfläche und Inhalt gemeinsam. `MenuButtonLayout::new` liefert die Bereiche für Beschriftung und Pfeil; lange Beschriftungen werden abgeschnitten, damit sie den Pfeil nicht verdecken. Addieren Sie für die automatische Breite `MENU_BUTTON_CHROME_WIDTH` (42 logische Pixel) zu `measure_text_width(label, scale)`. Die Farben für Zeigerkontakt, Drücken und Aktivierung kommen aus dem Theme; der geöffnete Menüzustand wird getrennt vom visuellen Zustand verwaltet.

## 8. Schriftarten und Symbole

Roboto und Roboto Mono liegen unter `assets/fonts`. plita rastert Text mit `fontdue` und behält eine kleine Bitmap-Ersatzschrift bei. Es sucht außerdem nach installierten Systemschriften. Mit `PLITA_UI_FONT`, `PLITA_UI_FONT_FALLBACK` und `PLITA_MEMORY_FONT` lassen sich Schriftdateien auswählen; setzen Sie diese Variablen vor dem Programmstart. Die Schrift muss die gewünschten Zeichen enthalten. Die mitgelieferten lateinischen Schriften decken Chinesisch, Japanisch und Koreanisch nicht vollständig ab.

`active_font_family`, `active_font_source`, `active_text_backend` und `active_memory_font_family` helfen bei der Diagnose der Schriftauswahl. Wenn Sie ein Programm verschieben, erhalten Sie den Zugriff auf das Ressourcenverzeichnis oder konfigurieren Sie einen passenden Schriftpfad. Ein Systemschriftpfad im Ladecode bedeutet nicht, dass diese Schriftdatei mitgeliefert wird.

Das Repository enthält 52 Lucide-SVG-Symbole. `lucide_icon_names()` listet ihre Namen auf; `draw_lucide_icon` zeichnet sie. Behalten Sie die SVGs und Lizenzhinweise bei, wenn Sie mit `crates/plita_ui/assets/build_icons.py` die Rust-Pfaddaten neu erzeugen.

## 9. Optionaler Rendering-Thread

Fügen Sie Ihrer `PlitaProgram`-Implementierung diese Methode hinzu, um ihn zu aktivieren:

```rust
fn render_on_worker_thread(&self) -> bool {
    true
}
```

Ein Arbeitsthread pro Fenster übernimmt GPU-Arbeit und Bildausgabe. Fensterverwaltung, Eingaben, `tick` und der Aufbau der Zeichenlisten bleiben auf dem Thread der Ereignisschleife. Bei langsamem Rendering werden ausstehende Anforderungen auf das neueste Bild zusammengefasst. Dies ist keine API zur lückenlosen Aufnahme aller Bilder. Aktualisieren Sie ein geteiltes RGBA-Bild vollständig unter demselben Mutex und halten Sie die Sperre kurz. Die Option wird beim Erzeugen des Renderers gelesen und ist kein Schalter für den laufenden Betrieb. Standardmäßig wird synchron gerendert.

Der Renderer hält unveränderliche RGBA-Quellen fest, um Identitätskollisionen im Texturcache zu verhindern, verwendet Vertexpuffer und temporären Bildspeicher erneut und gibt unbenutzte Cache-Einträge nach einer kurzen Anzahl von Frames frei. Gemeinsam genutzte RGBA-Daten werden unter ihrem Mutex kopiert und anschließend zur GPU übertragen; aktualisieren Sie sie unter demselben Mutex. Bestehende Aufrufe für Zeichenlisten bleiben unverändert.

Validierungsgrenze (2026-10-18): Auf dem Veröffentlichungsrechner waren die normalen Workspace-Tests, zwei Offscreen-GPU-Regressionstests und der native Fenstertest mit synchronem Rendering erfolgreich. Der native Worker-Test überschritt nach Wiederherstellung und Größenänderung das Zeitlimit; ein weiterer Desktoplauf brach abnormal ab. Die Ursache ist noch nicht eingegrenzt, daher ist der native Workerbetrieb in dieser Umgebung nicht bestätigt. Behalten Sie für zuverlässigen Betrieb das synchrone Rendering als Standard bei und prüfen Sie den optionalen Worker vor der Aktivierung auf dem Zielsystem.

## 10. Optionale Python-Hilfsfunktionen

Richten Sie Python ab Version 3.10 und maturin ab 1.8, aber unter 2, in einer geeigneten Python-Umgebung ein. Vom Stammverzeichnis des Repositorys aus:

```powershell
cd crates/plita
maturin develop --features python
```

Das Feature `python` liefert PyO3-Wrapper für gemeinsame Wertetypen und Registrierungshilfen. Es verwandelt nicht automatisch eine ganze Rust-Oberfläche in eine vollständige Python-Anwendung. Anwendungs-Crates mit `#[pyclass]` oder `#[pymodule]` benötigen weiterhin eine eigene optionale Abhängigkeit von `pyo3`, da diese Makros auf `::pyo3` verweisen. Wechseln Sie vor den früheren Befehlen wieder ins Stammverzeichnis des Repositorys.

## 11. Fehlersuche und Prüfung

- Build-Fehler: Lesen Sie den ersten Compiler- oder Linkerfehler, prüfen Sie Rust-Version und Ziel-Toolchain und behalten Sie die Lockdatei bei.
- Kein Fenster oder fehlgeschlagene GPU-Initialisierung: Prüfen Sie Protokolle und Grafiktreiber. Ein erfolgreicher Build bestätigt noch keine funktionierende Oberfläche.
- Fehlende Zeichen: Wählen Sie eine Schrift mit den nötigen Glyphen und prüfen Sie `active_font_source`.
- Stockende Oberfläche: Halten Sie Ereignisbehandlung, `tick` und Zeichenlistenerstellung kurz. Der Rendering-Thread parallelisiert keine Anwendungslogik.
- Tests nativer Fenster benötigen einen interaktiven Desktop. Gewöhnliche Unit-Tests ersetzen keine Sichtprüfung.

Diagnoseprotokolle in PowerShell aktivieren:

```powershell
$env:RUST_LOG="debug,plita_window=trace,plita_render=trace"
cargo run --locked -p hello_plita
```

Dieses Handbuch beschreibt den veröffentlichten Quelltext und bestätigt keine Laufzeittests auf sämtlichen Plattformen. Mit `cargo doc --workspace --no-deps --locked` können Sie zusätzlich die API-Dokumentation erzeugen.

Auf einem Rechner mit funktionierender GPU lassen sich zwei eigenständige Regressionstests ausdrücklich starten: `cargo test -p plita_render --locked offscreen_image_updates_and_draw_order -- --ignored --test-threads=1` und `cargo test -p plita_render --locked offscreen_cache_keeps_images_distinct_and_releases_old_sources -- --ignored --test-threads=1`. Normale Workspace-Tests überspringen GPU- und native Desktoptests. Die anderen ignorierten Benchmarks benötigen externe Eingabedaten und Ausgabepfade; führen Sie nicht alle ignored-Tests ohne diese Vorbereitung aus.

Der optionale Test `offscreen_fixture_snapshot_with_dpi` liest die Zeichenliste und `scale_factor` (Standard 1.0) aus `PLITA_DRAW_FIXTURE` und schreibt `gpu.json` sowie `desktop.rgba` in physischer Größe nach `PLITA_GPU_EVIDENCE`. Er benötigt eine GPU und ausdrücklich vorbereitete Eingabedaten. Geprüft wird der Offscreen-Encoder, nicht die Anzeige eines nativen Fensters.

## 12. Lizenz und Weitergabe

plita-Code und diese Handbücher stehen unter der MIT-Lizenz, Copyright (c) 2026 DAISUKE OBA. Behalten Sie bei der Weitergabe von Kopien oder wesentlichen Teilen den MIT-Urheberrechts- und Erlaubnisvermerk bei. Fremde Ressourcen behalten ihre eigenen Lizenzen: Roboto und Roboto Mono verwenden OFL-1.1; Lucide verwendet ISC einschließlich des übernommenen MIT-Hinweises von Feather.

Lesen Sie [LICENSE](../../LICENSE), die [Drittanbieterhinweise](../../THIRD_PARTY_NOTICES.md), die [Abhängigkeitshinweise](../../licenses/DEPENDENCIES.md) und die [Herkunft der Ressourcen](../../licenses/ASSET_PROVENANCE.json). Legen Sie weitergegebenen Schriften, Symbolen und Binärdateien die jeweils nötigen Hinweise bei. Klären Sie vor der Weitergabe von macOS-Binärdateien die dokumentierten Lücken bei eigenständigen Erlaubnistexten für `dispatch` und `malloc_buf`. Dieses Repository veröffentlicht Quelltext und Hinweise; eine spätere Binärverteilung erfordert die Prüfung der tatsächlich eingebundenen Abhängigkeiten.

## 13. Orientierung im Quelltext

- [Anwendungs-Builder](../../crates/plita_app/src/lib.rs)
- [Fenster- und Programmschnittstelle](../../crates/plita_window/src/lib.rs)
- [UI- und Modell-APIs](../../crates/plita_ui/src/lib.rs)
- [Renderer](../../crates/plita_render/src/lib.rs)
- [Symbole und Erzeugung](../../crates/plita_ui/assets/README.md)
- [Einzelheiten zum Rendering-Thread auf Japanisch](../render_worker_ja.md)
- [Menüschaltflächen-Komponente](../../crates/plita_ui/src/menu_button.rs)
