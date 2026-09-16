# astroglyphs_2K

Curated **OFL astrology glyph fonts** — the "best of Noto" — plus per-glyph metrics and one-line
embedding helpers, so any chart renderer gets **deterministic** astrology symbols instead of
depending on whatever fonts the viewer has installed.

The good astrology fonts (Linotype Astrology Pi and friends) are proprietary and can't be
bundled. astroglyphs_2K subsets the freely-licensed **Noto** family into compact web fonts you
can inline directly into an SVG or HTML page, and tells you exactly how big each glyph is.

```bash
pip install astroglyphs_2K
```

```python
import astroglyphs_2K as ag

svg = (ag.font_face_css()                      # <style> with the embedded @font-face rules
       + f'<text font-family={ag.SYM_FAMILY!r}>☉︎ ♄︎ ♏︎</text>'
       + f'<text font-family={ag.TXT_FAMILY!r}>22°℞ 36′</text>')
```

## What's inside

All glyphs are subset from Noto and **renamed** per the OFL Reserved Font Name clause:

| Family | Source (Noto) | Glyphs |
|---|---|---|
| `AstroSym`  | Noto Sans Symbols   | planets (Moon–Pluto), nodes, the 12 signs, asteroids, Chiron, Lilith, Hygeia, aspect symbols |
| `AstroSym2` | Noto Sans Symbols 2 | the Sun, Eros, Eris, Sedna |
| `AstroMath` | Noto Sans Math      | ⊗ Part of Fortune |
| `AstroText` | Noto Sans           | digits, Latin, `℞` · `°` · `′` · `″` |

`SYM_FAMILY` and `TXT_FAMILY` are ready-made `font-family` stacks (embedded families first,
system fallbacks after), so with `font_face_css(embed=False)` the page degrades gracefully to
the viewer's own fonts.

## API

- `font_face_css(embed=True)` → a `<style>` element inlining every font as a `data:` woff2 URI
  (self-contained; returns `""` when `embed=False`).
- `SYM_FAMILY`, `TXT_FAMILY` → `font-family` stacks.
- `glyph_metrics(ch)` → `(advance, ymin, ymax, xmin, xmax)` in fractions of the em (ink bounding
  box from the outline) — for laying glyphs out without guessing.
- `save_fonts(dest, fontset="astroset", formats=("ttf","otf","woff2"))` → write the packaged
  **installable font files** (TrueType `.ttf`, OpenType-CFF `.otf`, web `.woff2`) into a directory;
  `font_bytes(family, fontset, fmt)` returns one file's raw bytes. Both `astroset` (the compact
  astrology subset) and `fullset` (the whole renamed Noto family) are available.
- `GLYPH_METRICS`, `SYMBOL_FAMILY_NAMES`, `TEXT_FAMILY_NAME`, `FONT_SETS`, `FONT_FORMATS`,
  `OFL_ATTRIBUTION`.

## Licensing

Code: **MIT**. Bundled font data: **SIL Open Font License 1.1** (the subset Noto glyphs) — see
[`LICENSES/OFL.txt`](LICENSES/OFL.txt) and `astroglyphs_2K.OFL_ATTRIBUTION`. The subsets are
renamed (`Astro*`) so they are not distributed under a Noto Reserved Font Name.

## Rebuilding the data

```bash
pip install -e ".[build]"      # fonttools + brotli
python tools/build.py          # regenerates src/astroglyphs_2K/_data.py from tools/fonts/*.ttf
```

Deterministic: the same vendored sources produce the same `_data.py`.

MIT © 2026 Elizabeth Huston, Ph.D. and Noah Christian, Ph.D. · bundled glyphs © the Noto Project (OFL 1.1)
