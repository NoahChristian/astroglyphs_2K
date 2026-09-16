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

## Glyph inventory

Every symbol in the curated set. **Character** is the literal Unicode character; **Glyph** is its
official Unicode name (so a row is identifiable even where the character can't render); **Origin**
is the Unicode block it comes from; **Contained in** is the renamed `Astro*` family that ships it.
All of these are in both the `astroset` (curated subset) and the `fullset`. `AstroText` also
carries the digits and Latin letters (not listed here).

#### Zodiac signs

| Character | Unicode | Glyph | Description | Origin | Contained in |
|:---:|:---|:---|:---|:---|:---|
| ♈ | U+2648 | ARIES | Aries | Miscellaneous Symbols | AstroSym |
| ♉ | U+2649 | TAURUS | Taurus | Miscellaneous Symbols | AstroSym |
| ♊ | U+264A | GEMINI | Gemini | Miscellaneous Symbols | AstroSym |
| ♋ | U+264B | CANCER | Cancer | Miscellaneous Symbols | AstroSym |
| ♌ | U+264C | LEO | Leo | Miscellaneous Symbols | AstroSym |
| ♍ | U+264D | VIRGO | Virgo | Miscellaneous Symbols | AstroSym |
| ♎ | U+264E | LIBRA | Libra | Miscellaneous Symbols | AstroSym |
| ♏ | U+264F | SCORPIUS | Scorpio | Miscellaneous Symbols | AstroSym |
| ♐ | U+2650 | SAGITTARIUS | Sagittarius | Miscellaneous Symbols | AstroSym |
| ♑ | U+2651 | CAPRICORN | Capricorn | Miscellaneous Symbols | AstroSym |
| ♒ | U+2652 | AQUARIUS | Aquarius | Miscellaneous Symbols | AstroSym |
| ♓ | U+2653 | PISCES | Pisces | Miscellaneous Symbols | AstroSym |

#### Luminaries, planets & nodes

| Character | Unicode | Glyph | Description | Origin | Contained in |
|:---:|:---|:---|:---|:---|:---|
| ☉ | U+2609 | SUN | Sun | Miscellaneous Symbols | AstroSym2 |
| ☽ | U+263D | FIRST QUARTER MOON | Moon | Miscellaneous Symbols | AstroSym |
| ☿ | U+263F | MERCURY | Mercury | Miscellaneous Symbols | AstroSym |
| ♀ | U+2640 | FEMALE SIGN | Venus | Miscellaneous Symbols | AstroSym |
| ♂ | U+2642 | MALE SIGN | Mars | Miscellaneous Symbols | AstroSym |
| ♃ | U+2643 | JUPITER | Jupiter | Miscellaneous Symbols | AstroSym |
| ♄ | U+2644 | SATURN | Saturn | Miscellaneous Symbols | AstroSym |
| ♅ | U+2645 | URANUS | Uranus | Miscellaneous Symbols | AstroSym |
| ♆ | U+2646 | NEPTUNE | Neptune | Miscellaneous Symbols | AstroSym |
| ♇ | U+2647 | PLUTO | Pluto | Miscellaneous Symbols | AstroSym |
| ☊ | U+260A | ASCENDING NODE | North Node (ascending / Rāhu) | Miscellaneous Symbols | AstroSym |
| ☋ | U+260B | DESCENDING NODE | South Node (descending / Ketu) | Miscellaneous Symbols | AstroSym |

#### Points, asteroids & lots

| Character | Unicode | Glyph | Description | Origin | Contained in |
|:---:|:---|:---|:---|:---|:---|
| ⚸ | U+26B8 | BLACK MOON LILITH | Black Moon Lilith (lunar apogee) | Miscellaneous Symbols | AstroSym |
| ⚷ | U+26B7 | CHIRON | Chiron | Miscellaneous Symbols | AstroSym |
| ⚳ | U+26B3 | CERES | Ceres | Miscellaneous Symbols | AstroSym |
| ⚴ | U+26B4 | PALLAS | Pallas | Miscellaneous Symbols | AstroSym |
| ⚵ | U+26B5 | JUNO | Juno | Miscellaneous Symbols | AstroSym |
| ⚶ | U+26B6 | VESTA | Vesta | Miscellaneous Symbols | AstroSym |
| ♡ | U+2661 | WHITE HEART SUIT | Eros | Miscellaneous Symbols | AstroSym2 |
| ⯰ | U+2BF0 | ERIS FORM ONE | Eris | Misc. Symbols and Arrows | AstroSym2 |
| ☾ | U+263E | LAST QUARTER MOON | Asteroid / Dark Moon Lilith | Miscellaneous Symbols | AstroSym |
| ⚕ | U+2695 | STAFF OF AESCULAPIUS | Hygeia | Miscellaneous Symbols | AstroSym |
| ⯲ | U+2BF2 | SEDNA | Sedna | Misc. Symbols and Arrows | AstroSym2 |
| ⊗ | U+2297 | CIRCLED TIMES | Part of Fortune (Lot of Fortune) | Mathematical Operators | AstroMath |

#### Aspects

| Character | Unicode | Glyph | Description | Origin | Contained in |
|:---:|:---|:---|:---|:---|:---|
| ☌ | U+260C | CONJUNCTION | Conjunction (0°) | Miscellaneous Symbols | AstroSym |
| ☍ | U+260D | OPPOSITION | Opposition (180°) | Miscellaneous Symbols | AstroSym |
| □ | U+25A1 | WHITE SQUARE | Square (90°) | Geometric Shapes | AstroSym2 |
| △ | U+25B3 | WHITE UP-POINTING TRIANGLE | Trine (120°) | Geometric Shapes | AstroSym2 |
| ⚹ | U+26B9 | SEXTILE | Sextile (60°) | Miscellaneous Symbols | AstroSym |
| ⚻ | U+26BB | QUINCUNX | Quincunx / inconjunct (150°) | Miscellaneous Symbols | AstroSym |
| ⚺ | U+26BA | SEMISEXTILE | Semi-sextile (30°) | Miscellaneous Symbols | AstroSym |
| ∠ | U+2220 | ANGLE | Semi-square (45°) | Mathematical Operators | AstroMath |
| ⚼ | U+26BC | SESQUIQUADRATE | Sesquiquadrate (135°) | Miscellaneous Symbols | AstroSym |

#### Marks & notation

| Character | Unicode | Glyph | Description | Origin | Contained in |
|:---:|:---|:---|:---|:---|:---|
| ✦ | U+2726 | BLACK FOUR POINTED STAR | Fixed-star marker | Dingbats | AstroSym2 |
| · | U+00B7 | MIDDLE DOT | Middle dot (separator) | Latin-1 Supplement | AstroSym / AstroText |
| ℞ | U+211E | PRESCRIPTION TAKE | Retrograde | Letterlike Symbols | AstroText |
| ° | U+00B0 | DEGREE SIGN | Degree | Latin-1 Supplement | AstroText |
| ′ | U+2032 | PRIME | Arcminute (prime) | General Punctuation | AstroText |
| ″ | U+2033 | DOUBLE PRIME | Arcsecond (double prime) | General Punctuation | AstroText |

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
