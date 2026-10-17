# Third-party notices

plita project code is copyright (c) 2026 DAISUKE OBA and licensed under the
[MIT License](LICENSE). The fonts, icon data and dependencies listed here retain
their own copyrights and licenses. plita's MIT license does not relicense them.

## Bundled fonts

| Asset | Copyright holder | License | Full text |
| --- | --- | --- | --- |
| `assets/fonts/Roboto[wdth,wght].ttf` | Copyright 2011 The Roboto Project Authors | OFL-1.1 | [Roboto-OFL.txt](licenses/fonts/Roboto-OFL.txt) |
| `assets/fonts/RobotoMono-Regular.ttf` | Copyright 2015 The Roboto Mono Project Authors | OFL-1.1 | [RobotoMono-OFL.txt](licenses/fonts/RobotoMono-OFL.txt) |

The same notices are also present beside the font files in `assets/fonts/`.
Roboto is sourced from [Google Fonts](https://github.com/google/fonts/tree/bd8f81ddb5c74d5c8897b36ad88b440266245103/ofl/roboto).
Roboto Mono is sourced from [the Roboto Mono project](https://github.com/googlefonts/RobotoMono/tree/895ec691990d041dd727c7b5afa3ce56525d98e6/fonts/ttf).
The two bundled font binaries were verified byte-for-byte against those sources.
Their embedded copyright and OFL information agree with the bundled license texts.

When redistributing either font, include its copyright and complete OFL text.
Keep the font under OFL-1.1; do not sell the font by itself. Modified versions
must respect any Reserved Font Names declared by the applicable font license.
Bundling these fonts does not require plita source code to use the OFL.
See the [official OFL](https://openfontlicense.org/open-font-license-official-text/).

plita can load fonts installed on the operating system or supplied by a user.
Meiryo, Yu Gothic, Segoe UI, Helvetica, Noto and Inter names or paths in the code
are runtime lookup candidates; those font files are not included here.
Runtime access does not grant redistribution rights to those files.

## Bundled Lucide and Feather icon data

The 52 SVG files under `crates/plita_ui/assets/lucide/` and the generated
`crates/plita_ui/assets/lucide_paths.rs` contain third-party artwork.

- Lucide: ISC license; Copyright (c) 2026 Lucide Icons and Contributors for the
  current source snapshot. The preserved 0.468.0 license attributes Lucide to
  Lucide Contributors 2022 and Feather portions to Cole Bemis 2013-2022.
- Feather-derived icons: MIT license; the current upstream text states
  Copyright (c) 2013-present Cole Bemis. Both original notices are retained.

Retain both full upstream license files:

- [Lucide / Feather license](licenses/icons/Lucide-LICENSE), also preserved at
  [the SVG source directory](crates/plita_ui/assets/lucide/LICENSE).
- [Lucide 0.468.0 / Feather license](licenses/icons/Lucide-0.468.0-LICENSE).

44 SVGs match [Lucide commit 70562c1](https://github.com/lucide-icons/lucide/tree/70562c1ee1c4fdcf736fe97bc893fb8511927934/icons).
Eight older SVGs match [Lucide 0.468.0](https://github.com/lucide-icons/lucide/tree/0.468.0/icons):
`clipboard-paste`, `eraser`, `flip-horizontal-2`, `flip-vertical-2`, `package`,
`paint-bucket`, `pipette` and `trash-2`.
The conversion script changes the representation into SVG path strings; it does
not make the artwork original plita artwork. The notices are required when
redistributing these paths or a binary containing them, even without SVG files.
No in-window credit screen is required by these licenses; distribute the notices
and complete license texts with the software.

Hashes and exact verification sources are recorded in
[ASSET_PROVENANCE.json](licenses/ASSET_PROVENANCE.json).

## Rust dependencies

The resolved dependency graph includes 293 external packages across all target
platforms, optional Python support and build/test dependencies. Most permit MIT or
Apache-2.0; others use ISC, BSD, Zlib, CC0, Unicode terms or Apache with the LLVM
exception. They are separately licensed, not relicensed as plita code.

See [the versioned inventory](licenses/DEPENDENCIES.md),
[machine-readable metadata and source links](licenses/dependencies.json), and
the original texts in `licenses/dependencies/`.

Some expressions require multiple sets of terms: `dpi` declares
`Apache-2.0 AND MIT`; `unicode-ident` declares
`(MIT OR Apache-2.0) AND Unicode-3.0`. Retain the additional terms.
`r-efi` offers `MIT OR Apache-2.0 OR LGPL-2.1-or-later`; its LGPL option is not
mandatory, and a distributor can choose the MIT or Apache option.

This is a source distribution without vendored dependency implementation code
or prebuilt executables. For a binary release, retain the license, copyright and
applicable NOTICE files of the dependencies actually linked or bundled for that
target and feature set. Review platform SDKs, runtime libraries and separately
added assets as part of that binary package. Cargo metadata alone cannot certify
every file's origin or all obligations of a future binary distribution.

The `dispatch 0.2.0` and `malloc_buf 0.0.6` crates declare MIT in their published
metadata but do not ship standalone license texts; the corresponding upstream
release trees also lack them. Their original manifest declarations are retained.
Before distributing a macOS binary using these crates, obtain or verify the
appropriate upstream copyright and permission notices. This source-only plita
package does not redistribute those crates' implementation source or binaries.
