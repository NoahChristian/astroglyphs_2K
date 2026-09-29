# Changelog

All notable changes to **astroglyphs_2K** are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- **`Out/` download folder** — every font file as ready-to-install `Out/<fontset>/<FORMAT>/`
  (`astroset` / `fullset` × `TTF` / `OTF` / `WOFF2`) plus `OFL.txt`, byte-identical to the
  package data. `tools/build.py` refreshes it on every build (`--out-only` to refresh alone),
  and a test fails if it drifts from `src/astroglyphs_2K/fonts/`.

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

[0.1.0]: https://github.com/NoahChristian/astroglyphs_2K/releases/tag/v0.1.0
