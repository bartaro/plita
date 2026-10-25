# plita — Manuel utilisateur et développeur

[English](en.md) · [日本語](ja.md) · [한국어](ko.md) · [简体中文](zh-CN.md) · [繁體中文](zh-TW.md) · [Français](fr.md) · [Español](es.md) · [Deutsch](de.md)

DAISUKE OBA · Édition source du 2026-10-25 · Version du paquet Cargo : 0.0.1

## 1. Contenu de la distribution

plita est une base d'interface graphique en Rust pour les applications de création sur ordinateur. Ce dépôt contient cinq crates du framework et trois exemples exécutables. Il fournit des fenêtres natives, le routage des entrées, le dessin GPU, des widgets, l'ancrage des panneaux et des modèles de canevas. Les interfaces propres à des émulateurs, les ROM et les exécutables précompilés ne font pas partie de cette distribution.

- `plita` : API publique, réexportations `prelude` et aides Python facultatives.
- `plita_app` : constructeur `App` et configuration du lancement.
- `plita_window` : boucle d'événements native et interface `PlitaProgram`.
- `plita_render` : ressources GPU et rendu.
- `plita_ui` : géométrie, listes de dessin, widgets, ancrage, canevas et historique.

## 2. Prérequis et compilation

Installez Git, Rust 1.92 ou ultérieur, ainsi que l'éditeur de liens et les outils natifs adaptés à votre cible. Sous Windows avec la cible MSVC, installez les outils C++ de Visual Studio Build Tools et le SDK Windows. L'affichage d'une fenêtre nécessite un GPU et un pilote compatibles. La première compilation télécharge les dépendances Cargo ; conservez `Cargo.lock` pour pouvoir la reproduire.

```powershell
git clone https://github.com/bartaro/plita.git
cd plita
cargo check --workspace --locked
cargo test --workspace --locked
```

L'espace de travail active explicitement les moteurs DX12, GLES et Vulkan de wgpu. Metal n'est pas activé dans le manifeste. Ne supposez pas que tous les systèmes et toutes les configurations GPU ont été validés : des dépendances et bibliothèques d'affichage propres à la cible peuvent être nécessaires. Les commandes ci-dessus sont une procédure de vérification, pas une attestation de réussite sur toutes les plateformes.

## 3. Lancer les exemples

Exécutez une commande à la fois depuis la racine du dépôt. Fermez la fenêtre avant de lancer l'exemple suivant.

```powershell
cargo run --locked -p hello_plita
cargo run --locked -p docking_demo
cargo run --locked -p canvas_demo
```

Les trois exemples lancent actuellement le même `CreativeShell`. Seuls le titre et, pour `canvas_demo`, la taille initiale de la fenêtre diffèrent. Leurs noms ne désignent pas trois applications complètes distinctes. L'interface commune affiche une barre de menus, des outils, un canevas avec grille et plan de travail, un inspecteur, une chronologie et une barre d'état. Explorez cette interface et consultez le code lors de l'intégration d'une fonction.

Lorsque les champs de texte et de mémoire n'ont pas le focus, essayez ces commandes :

- `1` / `V` : sélection ; `2` / `H` : déplacement de la vue ; `3` / `R` : rectangle ; `4` / `T` : texte ; `5` / `G` : grille. Faites glisser le canevas avec l'outil de déplacement, zoomez avec la molette et appuyez sur `F` pour réinitialiser la vue.
- Sélectionnez un objet et faites glisser son corps ou ses poignées d'angle. `Ctrl+D` duplique ; `Delete` / `Backspace` supprime ; les flèches déplacent de 1 unité du monde, ou de 10 avec `Shift`. `Ctrl+Z` annule ; `Ctrl+Y` / `Ctrl+Shift+Z` rétablit.
- `Ctrl+1` à `Ctrl+6` sélectionnent les panneaux Propriétés, Calques, Mémoire, Chronologie, Journal et Diagnostic. `Ctrl+Shift+1` à `Ctrl+Shift+6` ouvrent des panneaux flottants ; `Ctrl+0` les ferme. `M` affiche ou masque l'éditeur mémoire.
- Dans cette démonstration, `Ctrl+S` indique seulement la taille d'un instantané dans la barre d'état, sans écrire de fichier. `Ctrl+O` réinitialise le document de démonstration. Ce ne sont pas des boîtes de dialogue complètes d'ouverture et d'enregistrement.

## 4. Démarrer une application

Voici le point d'entrée complet de `hello_plita` :

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

`App::new()` crée un `AppBuilder`. `run()` lance l'interface intégrée. Pour fournir votre propre état applicatif, passez à `run_program` une fabrique recevant la `Size` initiale et renvoyant une implémentation de `PlitaProgram`. Implémentez `resize`, `handle_event` et `draw_list` ; utilisez `tick` pour les mises à jour périodiques. Renvoyez la réponse UI nécessaire au moyen de `UiResponse`, sans dessiner directement dans un rappel d'événement du système.

Avec `continuous_redraw(false)`, le dessin suit les mises à jour et les demandes de rafraîchissement. N'activez le rafraîchissement continu que si l'application en a besoin. `draw_list` décrit les commandes de dessin ; le moteur de rendu gère leur soumission au GPU.

## 5. Entrées et fenêtres auxiliaires

Utilisez les coordonnées logiques de plita pour les tests de pointage et la disposition ; la couche fenêtre convertit les valeurs DPI. Les événements couvrent le pointeur, le clavier, l'IME et le dépôt de fichiers. L'ouverture, l'analyse et l'enregistrement d'un chemin reçu restent à la charge de l'application.

`PointerDoubleClick` suit le deuxième `PointerUp`. Il faut deux clics terminés avec le même bouton, espacés de 500 ms au maximum et situés à 6 pixels logiques au maximum l'un de l'autre. Les glissements sont exclus. Chaque fenêtre native possède son propre état de détection.

Une application peut définir des fenêtres auxiliaires avec `AuxiliaryWindowDescriptor` et leurs rappels de redimensionnement, d'événement et de dessin. L'éditeur mémoire détaché de l'interface intégrée utilise son tampon de démonstration ; il ne se connecte pas automatiquement à un émulateur ou à un autre processus.

`PlitaProgram::minimum_window_size()` et `auxiliary_window_minimum_size(id)` définissent la taille minimale de la zone cliente en coordonnées logiques ; `None`, la valeur par défaut, ne la limite pas. `auxiliary_window_activation_request(id)` renvoie un jeton facultatif : changez-le à chaque demande volontaire de restauration ou de focus. Un jeton inchangé ne réactive pas constamment la fenêtre. Après un échec de création d'une fenêtre auxiliaire, retirez sa définition ou changez le jeton pour réessayer ; la fenêtre principale continue de fonctionner.

`auxiliary_draw_revision(id)` permet de conserver la liste de dessin auxiliaire. Avec `Some(revision)`, changez la révision à chaque modification visible, y compris les états de survol et d'appui, et demandez aussi un rafraîchissement via `UiResponse`. Un redimensionnement natif ou un changement de DPI invalide la liste. Gardez la valeur par défaut `None` pour les animations et les images partagées. Le rendu est suspendu lorsque la fenêtre est réduite ; les redimensionnements de taille nulle sont ignorés.

`PlitaProgram::ime_allowed()` renvoie `true` par défaut. Renvoyez `false` si l’application doit recevoir les touches physiques sans interception par l’IME hôte. Cette politique est lue à la création des fenêtres principale et auxiliaires ; ce n’est pas un interrupteur dynamique et elle ne modifie pas le contexte de saisie des boîtes de dialogue de fichiers natives séparées. Les applications de saisie de texte doivent conserver la valeur par défaut.

`scale_factor_changed(scale_factor)` indique le nombre de pixels physiques par unité logique de la fenêtre principale. L’appel précède le premier dessin et `resize` lors d’une actualisation ou d’un changement de DPI. Mémorisez cette valeur pour aligner le contenu au pixel, tout en conservant les coordonnées logiques pour la disposition et les tests de position. Ce rappel ne fournit pas le DPI propre à une fenêtre auxiliaire.

## 6. Ancrage, canevas et persistance

`DockLayoutState` et les types géométriques d'ancrage décrivent la disposition des panneaux. `DockLayoutProfile` représente un profil de disposition versionné. L'interface intégrée traite ce profil sous forme de texte ; `AppBuilder::startup_layout_profile` le restaure à son lancement. L'application choisit quand et où enregistrer ce texte. Les emplacements de disposition en mémoire ne remplacent pas une sauvegarde durable dans un fichier.

`CanvasDocument` et `LayerNode` fournissent les modèles de document et de calques. Les aides de sélection, de sélection rectangulaire et d'accrochage, associées à `CommandHistory`, permettent de construire les opérations d'édition. `CommandRegistry` et `CommandDescriptor` décrivent les commandes et raccourcis. Ces API ne fournissent ni format de fichier applicatif complet ni sauvegarde automatique de projet. Reliez les modèles à vos commandes et à votre sérialisation.

`memory_viewer_address_at_point(rect, base_address, byte_count, position)` convertit la position d'un octet hexadécimal visible dans `draw_memory_viewer` en adresse `Option<u16>`. Fournissez le même rectangle et la même adresse de base que pour le dessin, le nombre réel d'octets et la position logique du pointeur. Les adresses affichées, le texte ASCII, les espaces, les octets absents et les lignes masquées renvoient `None`. L'application gère la sélection et l'écriture ; cette fonction ne modifie pas la mémoire.

## 7. Boutons de menu déroulant

`draw_menu_button` dessine la surface du bouton, son libellé et un chevron géométrique à droite. Le chevron ne dépend pas de la police : ne terminez pas le libellé par `v` ou un caractère de flèche. `expanded = false` l’oriente vers le bas ; utilisez `true` tant que le menu de l’application est ouvert pour l’orienter vers le haut.

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

Ce fragment produit des commandes dans une implémentation de `draw_list` ; il n’ouvre pas de fenêtre à lui seul. Suivez le survol et l’appui avec `ButtonInteractionState`, basculez l’état du menu après un appui et un relâchement sur le même bouton, puis transmettez cet état à `expanded`. Le libellé et la flèche partagent le rectangle d’origine comme zone de clic. L’application dessine les entrées et gère la sélection et la fermeture du menu.

`MenuButtonStyle` fournit la surface, la couleur de premier plan et l’échelle du texte pour l’état courant. `ButtonVisualState::Pressed` décale ensemble la surface et son contenu. `MenuButtonLayout::new` expose les zones du libellé et du chevron ; les libellés longs sont découpés pour ne pas recouvrir la flèche. Pour calculer la largeur, ajoutez `MENU_BUTTON_CHROME_WIDTH` (42 pixels logiques) à `measure_text_width(label, scale)`. Les couleurs de survol, d’appui et d’activation viennent du thème ; l’ouverture du menu est distincte de l’état visuel.

## 8. Polices et icônes

Roboto et Roboto Mono sont incluses dans `assets/fonts`. plita utilise `fontdue` pour la rastérisation du texte et conserve une petite police bitmap de secours. Il recherche également des polices système installées. `PLITA_UI_FONT`, `PLITA_UI_FONT_FALLBACK` et `PLITA_MEMORY_FONT` permettent de choisir des fichiers de police ; définissez ces variables avant le lancement. La police doit contenir les caractères à afficher. Les polices latines incluses ne couvrent pas intégralement le chinois, le japonais et le coréen.

`active_font_family`, `active_font_source`, `active_text_backend` et `active_memory_font_family` aident à diagnostiquer le choix de police. Si vous déplacez un exécutable, maintenez l'accès aux ressources ou configurez un chemin de police approprié. La présence d'un chemin de police système dans le chargeur ne signifie pas que son fichier est distribué.

Le dépôt inclut 52 icônes SVG Lucide. `lucide_icon_names()` en énumère les noms et `draw_lucide_icon` les dessine. Conservez les SVG et leurs mentions de licence lors de la régénération des tracés Rust avec `crates/plita_ui/assets/build_icons.py`.

## 9. Thread de rendu facultatif

Ajoutez cette méthode à votre implémentation de `PlitaProgram` pour l'activer :

```rust
fn render_on_worker_thread(&self) -> bool {
    true
}
```

Un thread par fenêtre prend en charge les opérations GPU et la présentation. La gestion des fenêtres, les entrées, `tick` et la construction des listes de dessin restent sur le thread de la boucle d'événements. Si le rendu ralentit, les demandes en attente sont regroupées pour ne garder que l'image la plus récente ; ce n'est pas une API d'enregistrement de toutes les images. Mettez à jour une image RGBA partagée entièrement sous le même mutex, en limitant la durée du verrouillage. L'option est lue à la création du moteur de rendu et ne sert pas d'interrupteur à chaud. Le rendu synchrone reste le choix par défaut.

Le moteur conserve les sources RGBA immuables pour éviter les collisions d'identité du cache de textures, réutilise les tampons de sommets et l'espace temporaire des images, puis libère les entrées inutilisées après quelques images. Les données RGBA partagées sont copiées sous mutex avant le transfert GPU ; effectuez les mises à jour sous ce même mutex. Les appels existants aux listes de dessin restent valables.

Limite de validation (2026-10-18) : les tests ordinaires du workspace, deux tests GPU hors écran et le test de fenêtre native à rendu synchrone ont réussi sur la machine de publication. En revanche, le test natif du worker a dépassé le délai après restauration/redimensionnement, et une autre exécution sur le bureau s'est terminée anormalement. La cause n'est pas isolée ; le bon fonctionnement natif du worker n'est donc pas confirmé dans cet environnement. Pour privilégier la fiabilité, gardez le rendu synchrone par défaut et validez le worker sur votre cible avant de l'activer.

## 10. Aides Python facultatives

Préparez Python 3.10 ou ultérieur et maturin de version au moins 1.8 et inférieure à 2 dans un environnement Python adapté. Depuis la racine du dépôt :

```powershell
cd crates/plita
maturin develop --features python
```

La fonctionnalité `python` fournit des classes PyO3 pour les valeurs courantes et des aides à l'enregistrement. Elle ne transforme pas automatiquement une interface Rust entière en application Python complète. Les crates applicatives utilisant `#[pyclass]` ou `#[pymodule]` doivent conserver leur propre dépendance facultative `pyo3`, car ces macros référencent `::pyo3`. Revenez à la racine du dépôt avant de réutiliser les commandes des sections précédentes.

## 11. Diagnostic et vérification

- Échec de compilation : lisez la première erreur du compilateur ou de l'éditeur de liens, vérifiez Rust et la chaîne d'outils cible, et conservez le fichier de verrouillage.
- Fenêtre absente ou échec d'initialisation GPU : examinez les journaux et le pilote graphique. Compiler ne suffit pas à valider l'interface.
- Caractères manquants : choisissez une police contenant les glyphes requis et vérifiez `active_font_source`.
- Interface bloquée : limitez le temps passé dans les événements, `tick` et la génération des listes de dessin. Le thread de rendu ne parallélise pas la logique applicative.
- Les tests de fenêtres natives nécessitent un bureau interactif. Les tests unitaires ordinaires ne remplacent pas la vérification visuelle.

Pour activer les journaux de diagnostic dans PowerShell :

```powershell
$env:RUST_LOG="debug,plita_window=trace,plita_render=trace"
cargo run --locked -p hello_plita
```

Ce manuel décrit le code publié sans certifier son exécution sur toutes les plateformes. La commande `cargo doc --workspace --no-deps --locked` génère également la documentation API.

Sur une machine disposant d'un GPU fonctionnel, lancez explicitement les deux tests autonomes : `cargo test -p plita_render --locked offscreen_image_updates_and_draw_order -- --ignored --test-threads=1` et `cargo test -p plita_render --locked offscreen_cache_keeps_images_distinct_and_releases_old_sources -- --ignored --test-threads=1`. Les tests ordinaires ignorent les tests GPU et de bureau natif. Les autres benchmarks ignorés nécessitent des données externes et des chemins de sortie ; ne lancez pas tous les tests ignored sans préparer ces entrées.

Le test facultatif `offscreen_fixture_snapshot_with_dpi` lit la liste de dessin et `scale_factor` (1.0 par défaut) depuis `PLITA_DRAW_FIXTURE`, puis écrit `gpu.json` et `desktop.rgba` aux dimensions physiques dans `PLITA_GPU_EVIDENCE`. Il exige un GPU et des données préparées explicitement. Il vérifie le chemin de rendu hors écran, pas la présentation d’une fenêtre native.

## 12. Licence et redistribution

Le code plita et ces manuels sont sous licence MIT, copyright (c) 2026 DAISUKE OBA. Conservez l'avis de copyright et le texte d'autorisation MIT lors de la redistribution de copies ou de parties substantielles. Les ressources tierces gardent leurs propres licences : OFL-1.1 pour Roboto et Roboto Mono ; ISC pour Lucide, avec l'avis MIT hérité de Feather.

Consultez [LICENSE](../../LICENSE), les [mentions tierces](../../THIRD_PARTY_NOTICES.md), les [mentions des dépendances](../../licenses/DEPENDENCIES.md) et la [provenance des ressources](../../licenses/ASSET_PROVENANCE.json). Joignez les mentions pertinentes aux polices, icônes et binaires distribués. Avant de distribuer des binaires macOS, résolvez les lacunes de textes d'autorisation distincts signalées pour `dispatch` et `malloc_buf`. Ce dépôt publie du code source et des mentions ; une future distribution binaire devra examiner les dépendances effectivement liées.

## 13. Repères dans les sources

- [Constructeur d'application](../../crates/plita_app/src/lib.rs)
- [Interface des fenêtres et programmes](../../crates/plita_window/src/lib.rs)
- [API de l'interface et des modèles](../../crates/plita_ui/src/lib.rs)
- [Moteur de rendu](../../crates/plita_render/src/lib.rs)
- [Icônes et génération](../../crates/plita_ui/assets/README.md)
- [Détails du thread de rendu, en japonais](../render_worker_ja.md)
- [Composant de bouton de menu](../../crates/plita_ui/src/menu_button.rs)
