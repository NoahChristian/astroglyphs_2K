# Changelog

All notable changes to **astroglyphs_2K** are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.1] — 2026-10-05

### Fixed
- **The fonts now render in Microsoft Word on Windows.** All three declared no code pages
  (`OS/2.ulCodePageRange1 = 0`, fontTools' default), which Windows reads as "this font cannot
  set text": Word listed the family but rendered Courier New instead. Font viewers were
  unaffected, since they draw from the `cmap` directly. The fonts now declare bit 0 (cp1252
  Latin 1), which all three cover. Verified against Word 16.0 — `AstroglyphPi` at 20 pt went
  from Courier's 95.9 pt advance to its own 149.7 pt.
- `OS/2.panose` is no longer all zeros. It does not cause the substitution, but it decides
  *which* face Windows picks when a font really is missing. Astroglyphs 2K declares Latin text,
  the two keyboard fonts declare Latin pictorial.

Glyph outlines, character maps and metrics are unchanged from 0.2.0; installed copies should be
replaced to pick up the fix.

## [0.2.0] — 2026-10-01

One glyph set, three fonts. **Breaking:** the four `Astro*` families and the `fontset=`
argument are replaced (see *Changed*).

### Added
- **AstroglyphPi** — keyboard font, key-for-key compatible with AstrotypeP LT Std (layout only;
  all drawings from Noto). Existing AstrotypeP documents can switch font without retyping.
- **AstroglyphPro** — keyboard font with a mnemonic layout; digits, punctuation and `° ′ ″`
  stay text.
- **Alternate forms** at their Unicode codepoints: Pluto forms two–five (⯓ ⯔ ⯕ ⯖), astronomical
  Uranus ⛢, Eris form two ⯱, Hygiea ⯚, circled-S Spirit Ⓢ, right-angle semisquare ∟.
  `alternates(name)` lists them, default first.
- **Hermetic lots**: Lot of Fortune at its Unicode 15 codepoint U+1F774, Lot of Spirit ⦶, and
  composed Eros, Necessity, Courage, Victory and Nemesis glyphs; all seven in a contiguous
  Private Use block (U+E100–E106, Paulus order). `lot(name)` resolves aliases (Genius/Daimon =
  Spirit, Love = Eros, Daring = Courage).
- Astronomy and esoteric glyphs needed by AstroglyphPi: composed moon phases (U+E001–E004),
  half-filled circles, crescents, pentagram, hexagram, alchemical air/earth/sulfur, gateway.
- More points and aspects: Earth ♁, Pholus ⯛, quintile ⯵, novile ⯴, vigintile ⯳.
- `glyph(name)`, `keys_to_unicode(text, layout)`, and the `GLYPHS`, `ALTERNATES`, `LOTS`,
  `LOT_ALIASES`, `PI_KEYMAP`, `PRO_KEYMAP` maps.
- `tools/registry.py` — the single source of truth for every glyph and key; `spec/*.csv` key maps
  are generated from it.
- Fonts now carry full OFL licence and copyright entries in their name tables.

### Changed
- **`Out/` download folder** of ready-to-install TTF/OTF/WOFF2 files, kept byte-identical
  to the package data by the build and checked by a test.
- **One family.** `AstroSym`, `AstroSym2`, `AstroMath` and `AstroText` are merged into
  **Astroglyphs 2K**. `font_face_css()` now emits one `@font-face` (12 KB woff2, down from
  ~49 KB across four). `FAMILY` is the new stack; `SYM_FAMILY` / `TXT_FAMILY` now both start with
  the single family. `SYMBOL_FAMILY_NAMES` / `TEXT_FAMILY_NAME` remain as deprecated aliases.
- `font_bytes(font, fmt)` and `save_fonts(dest, fonts, formats)` take font names from
  `FONT_NAMES` instead of a family + `fontset`.
- `Out/` is now `Out/<Font>/<FORMAT>/`, with a guide to choosing a font.
- Hinting is no longer carried over from Noto (no visible effect at chart sizes).

### Removed
- The `fullset` (whole renamed Noto fonts, ~8 MB) and the `fontset=` argument.
- `SYMBOLS_WOFF2_B64` / `TEXT_WOFF2_B64`; use `WOFF2_B64` or `font_face_css()`.

## [0.1.0] — 2026-09-15

Initial release — curated OFL astrology glyph fonts + metrics + embedding helpers.

### Added
- **Curated "best of Noto" astrology glyphs**, subset from the Noto family and renamed per the
  OFL Reserved Font Name clause: `AstroSym` (Noto Sans Symbols — planets, nodes, 12 signs,
  asteroids, Chiron, Lilith, Hygeia, aspect symbols), `AstroSym2` (Noto Sans Symbols 2 — Sun,
  Eros, Eris, Sedna), `AstroMath` (Noto Sans Math — ⊗ Part of Fortune), `AstroText` (Noto Sans —
  digits, Latin, ℞ · ° · ′ · ″).
- **`font_face_css(embed=True, fontset="astroset")`** — self-contained `<style>` inlining the
  fonts as `data:` woff2 URIs. `fontset="fullset"` swaps in the full Noto coverage (text + every
  symbol) under the same family names for anyone who needs more than astrology.
- **`SYM_FAMILY` / `TXT_FAMILY`** ready-made `font-family` stacks (embedded first, system
  fallbacks after, so `embed=False` degrades gracefully).
- **`glyph_metrics(ch)` / `GLYPH_METRICS`** — real per-glyph ink-bbox metrics (advance, ymin,
  ymax, xmin, xmax as em fractions) from the source outlines, for precise layout.
- **Installable font files** — each fontset (`astroset`, `fullset`) is shipped as `.ttf`
  (TrueType, native), `.otf` (OpenType-CFF, converted via qu2cu) and `.woff2` package data.
  `save_fonts(dest, fontset, formats)` writes them to a directory and `font_bytes(family,
  fontset, fmt)` returns the raw bytes — so the glyphs are usable as embedded web fonts *and*
  as installable desktop fonts, not only as base64.
- Zero runtime dependencies. `tools/build.py` regenerates the data + font files from the vendored
  Noto sources (needs fonttools + brotli; build-only) and is deterministic.

[0.2.1]: https://github.com/NoahChristian/astroglyphs_2K/releases/tag/v0.2.1
[0.2.0]: https://github.com/NoahChristian/astroglyphs_2K/releases/tag/v0.2.0
[0.1.0]: https://github.com/NoahChristian/astroglyphs_2K/releases/tag/v0.1.0
