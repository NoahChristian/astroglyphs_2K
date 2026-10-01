# astroglyphs_2K

**OFL astrology glyph fonts** built from Noto: one Unicode font for charts and the web, plus
two keyboard fonts for typing in design and video apps, all sharing one set of drawings. The
package adds per-glyph metrics and one-line embedding helpers, so any chart renderer gets
**deterministic** astrology symbols instead of depending on whatever fonts the viewer has.

The good astrology fonts (Linotype Astrology Pi, AstrotypeP and friends) are proprietary and
can't be bundled. astroglyphs_2K builds compact fonts from the freely-licensed **Noto** family
instead.

```bash
pip install astroglyphs_2K
```

Just want the fonts? Every font is in the [`Out/`](Out) folder as ready-to-install **TTF**,
**OTF** and **WOFF2** files, with a guide to which one to use. No Python needed.

```python
import astroglyphs_2K as ag

svg = (ag.font_face_css()                      # <style> with the embedded @font-face rule
       + f'<text font-family={ag.FAMILY!r}>☉︎ 22°♏︎ 36′ ℞</text>')
```

## The three fonts

| Font | What it is | Size (woff2) |
|---|---|---:|
| **Astroglyphs 2K** | The Unicode font. Signs, planets, points, aspects, alternate forms, Hermetic lots, and plain text (digits, Latin, `℞ ° ′ ″`) in **one** family. This is what `font_face_css()` embeds. | 12 KB |
| **AstroglyphPi** | Keyboard font, key-for-key compatible with **AstrotypeP LT Std**. Swap the font in an existing document and the glyphs carry over. | 5 KB |
| **AstroglyphPro** | Keyboard font with a mnemonic layout: `a`–`l` signs in zodiac order, `A`–`L` Sun … South Node, `M`–`Z` points, `m`–`z` aspects. Digits, punctuation and `° ′ ″` stay text, so `15a22°` reads 15♈22°. | 8 KB |

The key maps are in [`spec/astroglyph_pi.csv`](spec/astroglyph_pi.csv) and
[`spec/astroglyph_pro.csv`](spec/astroglyph_pro.csv). `keys_to_unicode()` converts text typed in
either keyboard font back to real Unicode, so AstrotypeP-era text can be migrated.

**Alternate forms** are separate codepoints, default first: Pluto ♇ ⯓ ⯔ ⯕ ⯖, Uranus ♅ ⛢,
Eris ⯰ ⯱, Hygiea ⚕ ⯚, Lot of Fortune 🝴 ⊗, Lot of Spirit ⦶ Ⓢ, semisquare ∠ ∟. A renderer
chooses a form by codepoint (`ag.alternates("pluto")`).

**Lots.** Only lots with a glyph in use get one: the seven Hermetic lots. Fortune and Spirit use
established forms; Eros, Necessity, Courage, Victory and Nemesis are drawn as their planet with a
small lot index. All seven also sit in one contiguous Private Use block (`U+E100`–`E106`, Paulus
order) and on the keys `È`–`Î` in both keyboard fonts. The hundreds of other Arabic parts are best
shown as ⊗ plus a text label.

Codepoints, Private Use slots and key assignments are never reassigned once released; new glyphs
only take empty slots.

## Glyph inventory

Every glyph in Astroglyphs 2K. **Character** is the literal character; **Unicode name** is its
official name, so a row is identifiable even where the character can't render.

#### Zodiac signs

| Character | Codepoint | Unicode name | Description |
|:---:|:---|:---|:---|
| ♈ | U+2648 | ARIES | Aries |
| ♉ | U+2649 | TAURUS | Taurus |
| ♊ | U+264A | GEMINI | Gemini |
| ♋ | U+264B | CANCER | Cancer |
| ♌ | U+264C | LEO | Leo |
| ♍ | U+264D | VIRGO | Virgo |
| ♎ | U+264E | LIBRA | Libra |
| ♏ | U+264F | SCORPIUS | Scorpio |
| ♐ | U+2650 | SAGITTARIUS | Sagittarius |
| ♑ | U+2651 | CAPRICORN | Capricorn |
| ♒ | U+2652 | AQUARIUS | Aquarius |
| ♓ | U+2653 | PISCES | Pisces |

#### Luminaries, planets & nodes

| Character | Codepoint | Unicode name | Description |
|:---:|:---|:---|:---|
| ☉ | U+2609 | SUN | Sun |
| ☽ | U+263D | FIRST QUARTER MOON | Moon |
| ☿ | U+263F | MERCURY | Mercury |
| ♀ | U+2640 | FEMALE SIGN | Venus |
| ♁ | U+2641 | EARTH | Earth |
| ♂ | U+2642 | MALE SIGN | Mars |
| ♃ | U+2643 | JUPITER | Jupiter |
| ♄ | U+2644 | SATURN | Saturn |
| ♅ | U+2645 | URANUS | Uranus |
| ♆ | U+2646 | NEPTUNE | Neptune |
| ♇ | U+2647 | PLUTO | Pluto |
| ☊ | U+260A | ASCENDING NODE | North Node |
| ☋ | U+260B | DESCENDING NODE | South Node |

#### Points & asteroids

| Character | Codepoint | Unicode name | Description |
|:---:|:---|:---|:---|
| ⚷ | U+26B7 | CHIRON | Chiron |
| ⚸ | U+26B8 | BLACK MOON LILITH | Black Moon Lilith |
| ☾ | U+263E | LAST QUARTER MOON | Asteroid / Dark Moon Lilith |
| ⚳ | U+26B3 | CERES | Ceres |
| ⚴ | U+26B4 | PALLAS | Pallas |
| ⚵ | U+26B5 | JUNO | Juno |
| ⚶ | U+26B6 | VESTA | Vesta |
| ♡ | U+2661 | WHITE HEART SUIT | Eros (asteroid) |
| ⯰ | U+2BF0 | ERIS FORM ONE | Eris |
| ⯲ | U+2BF2 | SEDNA | Sedna |
| ⚕ | U+2695 | STAFF OF AESCULAPIUS | Hygiea |
| ⯛ | U+2BDB | PHOLUS | Pholus |

#### Aspects

| Character | Codepoint | Unicode name | Description |
|:---:|:---|:---|:---|
| ☌ | U+260C | CONJUNCTION | Conjunction (0°) |
| ☍ | U+260D | OPPOSITION | Opposition (180°) |
| △ | U+25B3 | WHITE UP-POINTING TRIANGLE | Trine (120°) |
| □ | U+25A1 | WHITE SQUARE | Square (90°) |
| ⚹ | U+26B9 | SEXTILE | Sextile (60°) |
| ⚻ | U+26BB | QUINCUNX | Quincunx (150°) |
| ⚺ | U+26BA | SEMISEXTILE | Semisextile (30°) |
| ∠ | U+2220 | ANGLE | Semisquare (45°) |
| ⚼ | U+26BC | SESQUIQUADRATE | Sesquiquadrate (135°) |
| ⯵ | U+2BF5 | RUSSIAN ASTROLOGICAL SYMBOL QUINTILE | Quintile (72°) |
| ⯴ | U+2BF4 | RUSSIAN ASTROLOGICAL SYMBOL NOVILE | Novile (40°) |
| ⯳ | U+2BF3 | RUSSIAN ASTROLOGICAL SYMBOL VIGINTILE | Vigintile (18°) |

#### Marks

| Character | Codepoint | Unicode name | Description |
|:---:|:---|:---|:---|
| ✦ | U+2726 | BLACK FOUR POINTED STAR | Fixed star |
| · | U+00B7 | MIDDLE DOT | Middle dot |

#### Lots

| Character | Codepoint | Unicode name | Description |
|:---:|:---|:---|:---|
| 🝴 | U+1F774 | LOT OF FORTUNE | Lot of Fortune |
| ⦶ | U+29B6 | CIRCLED VERTICAL BAR | Lot of Spirit |

#### Alternate forms

| Character | Codepoint | Unicode name | Description |
|:---:|:---|:---|:---|
| ⯓ | U+2BD3 | PLUTO FORM TWO | Pluto, form two (circle, crescent, cross) |
| ⯔ | U+2BD4 | PLUTO FORM THREE | Pluto, form three |
| ⯕ | U+2BD5 | PLUTO FORM FOUR | Pluto, form four |
| ⯖ | U+2BD6 | PLUTO FORM FIVE | Pluto, form five |
| ⛢ | U+26E2 | ASTRONOMICAL SYMBOL FOR URANUS | Uranus (astronomical) |
| ⯱ | U+2BF1 | ERIS FORM TWO | Eris, form two |
| ⯚ | U+2BDA | HYGIEA | Hygiea, form two |
| ⊗ | U+2297 | CIRCLED TIMES | Lot of Fortune (circled times) |
| Ⓢ | U+24C8 | CIRCLED LATIN CAPITAL LETTER S | Lot of Spirit (circled S) |
| ∟ | U+221F | RIGHT ANGLE | Semisquare (right angle form) |

#### Astronomy & esoteric glyphs (used by AstroglyphPi)

| Character | Codepoint | Unicode name | Description |
|:---:|:---|:---|:---|
| ⦵ | U+29B5 | CIRCLE WITH HORIZONTAL BAR | Circle with horizontal bar |
| ⊖ | U+2296 | CIRCLED MINUS | Circled minus |
| ⊕ | U+2295 | CIRCLED PLUS | Circled plus |
| ○ | U+25CB | WHITE CIRCLE | White circle |
| ◯ | U+25EF | LARGE CIRCLE | Large circle |
| ● | U+25CF | BLACK CIRCLE | Black circle |
| ⬤ | U+2B24 | BLACK LARGE CIRCLE | Large black circle |
| ◐ | U+25D0 | CIRCLE WITH LEFT HALF BLACK | Circle, left half black |
| ◑ | U+25D1 | CIRCLE WITH RIGHT HALF BLACK | Circle, right half black |
| ◒ | U+25D2 | CIRCLE WITH LOWER HALF BLACK | Circle, lower half black |
| ◓ | U+25D3 | CIRCLE WITH UPPER HALF BLACK | Circle, upper half black |
| ◖ | U+25D6 | LEFT HALF BLACK CIRCLE | Left half black circle |
| ◗ | U+25D7 | RIGHT HALF BLACK CIRCLE | Right half black circle |
| ◠ | U+25E0 | UPPER HALF CIRCLE | Upper half circle (horned crescent) |
| ◡ | U+25E1 | LOWER HALF CIRCLE | Lower half circle (horned crescent) |
| ▽ | U+25BD | WHITE DOWN-POINTING TRIANGLE | White down-pointing triangle |
| ⛤ | U+26E4 | PENTAGRAM | Pentagram |
| ✡ | U+2721 | STAR OF DAVID | Hexagram |
| 🜁 | U+1F701 | ALCHEMICAL SYMBOL FOR AIR | Air (alchemical) |
| 🜃 | U+1F703 | ALCHEMICAL SYMBOL FOR EARTH | Earth (alchemical) |
| 🜍 | U+1F70D | ALCHEMICAL SYMBOL FOR SULFUR | Sulfur (alchemical) |
| ▩ | U+25A9 | SQUARE WITH DIAGONAL CROSSHATCH FILL | Gateway |

#### Composed glyphs (Private Use Area)

Unicode has no codepoint for these, so they are drawn by `tools/build.py` and placed in
reserved Private Use ranges: `E000–E0FF` astronomy, `E100–E1FF` lots.

| Codepoint | Name | How it is drawn |
|:---|:---|:---|
| U+E001 | Moon: white disc, dark crescent left | Composed moon phase |
| U+E002 | Moon: white disc, dark crescent right | Composed moon phase |
| U+E003 | Moon: dark disc, white crescent right | Composed moon phase |
| U+E004 | Moon: dark disc, white crescent left | Composed moon phase |
| U+E100 | Lot of Fortune | Same drawing as U+1F774 |
| U+E101 | Lot of Spirit | Same drawing as U+29B6 |
| U+E102 | Lot of Eros | ♀ with a small lot index |
| U+E103 | Lot of Necessity | ☿ with a small lot index |
| U+E104 | Lot of Courage | ♂ with a small lot index |
| U+E105 | Lot of Victory | ♃ with a small lot index |
| U+E106 | Lot of Nemesis | ♄ with a small lot index |

## API

- `font_face_css(embed=True)` → a `<style>` element inlining Astroglyphs 2K as a `data:` woff2
  URI (self-contained; returns `""` when `embed=False`).
- `FAMILY` → the `font-family` stack (embedded family first, system fallbacks after).
  `SYM_FAMILY` and `TXT_FAMILY` remain, with symbol and text fallbacks respectively.
- `glyph(name)`, `alternates(name)`, `lot(name)` → characters by name, e.g. `glyph("scorpio")`,
  `alternates("pluto")`, `lot("lot of genius")` (aliases resolve: Genius and Daimon are Spirit).
- `keys_to_unicode(text, layout="pi" | "pro")` → convert keyboard-font text to Unicode.
- `glyph_metrics(ch)` → `(advance, ymin, ymax, xmin, xmax)` in fractions of the em (ink bounding
  box from the outline), for laying glyphs out without guessing.
- `save_fonts(dest, fonts=None, formats=("ttf","otf","woff2"))` writes the installable font
  files; `font_bytes(font, fmt)` returns one file's bytes.
- Data: `GLYPHS`, `ALTERNATES`, `LOTS`, `LOT_ALIASES`, `PI_KEYMAP`, `PRO_KEYMAP`,
  `GLYPH_METRICS`, `FONT_NAMES`, `FONT_FORMATS`, `OFL_ATTRIBUTION`, `SOURCE_FONT_VERSIONS`.

Upgrading from 0.1? See the [CHANGELOG](CHANGELOG.md): the four `Astro*` families became one,
and the `fontset=` argument is gone.

## Licensing

Code: **MIT**. Font data: **SIL Open Font License 1.1** — see [`LICENSES/OFL.txt`](LICENSES/OFL.txt)
and `astroglyphs_2K.OFL_ATTRIBUTION`. The fonts are renamed so they are not distributed under a
Noto Reserved Font Name. AstroglyphPi matches AstrotypeP's key *layout* only; every drawing comes
from Noto or is composed from Noto outlines.

## Rebuilding

```bash
pip install -e ".[build]"          # fonttools + brotli + skia-pathops
python tools/build.py              # fonts, src/astroglyphs_2K/_data.py, spec/*.csv and Out/
python tools/build.py --out-only   # just refresh Out/ from the committed package fonts
```

Everything is driven by [`tools/registry.py`](tools/registry.py). The build is deterministic:
the same vendored sources produce byte-identical outputs.

MIT © 2026 Elizabeth Huston, Ph.D. and Noah Christian, Ph.D. · glyphs © the Noto Project (OFL 1.1)
