"""astroglyphs_2K — OFL astrology glyph fonts (the "best of Noto") + metrics + embedding.

A tiny, zero-runtime-dependency toolkit that gives any chart renderer a deterministic,
embeddable set of astrology glyphs. The good astrology fonts are proprietary; this builds
compact fonts from the freely-licensed **Noto** family (SIL Open Font License) plus real
per-glyph metrics, so charts render identically on every device.

Three fonts, one glyph set:

- **Astroglyphs 2K** — the Unicode font. Signs, planets, points, aspects, alternate forms,
  Hermetic lots and plain text (digits, Latin, ℞ ° ′ ″) in ONE family. This is the one to
  embed in charts (``font_face_css()``).
- **AstroglyphPi**   — keyboard font, key-for-key compatible with AstrotypeP LT Std.
- **AstroglyphPro**  — keyboard font with a mnemonic layout (a–l = the signs in order,
  A–L = Sun … South Node); digits and punctuation stay text.

Quick use (inline in an SVG or HTML):
    import astroglyphs_2K as ag
    svg = ag.font_face_css() + '<text font-family=%r>%s</text>' % (ag.FAMILY, "☉︎ 22°♏︎")

Regenerate the bundled data with ``python tools/build.py`` (build-only dependencies).
"""

import importlib.resources as _res

from ._data import (  # noqa: F401
    ALTERNATES,
    FAMILY_NAME,
    FONT_FILES,
    FONT_NAMES,
    GLYPH_METRICS,
    GLYPHS,
    LOT_ALIASES,
    LOTS,
    OFL_ATTRIBUTION,
    PI_KEYMAP,
    PRO_KEYMAP,
    SOURCE_FONT_VERSIONS,
    WOFF2_B64,
)

__version__ = "0.2.0"

# System fallbacks (used when embedding is off, or a viewer strips the embedded face).
# Family names are single-quoted so the stacks are valid both in a CSS `font-family:` value
# AND inside a double-quoted SVG/HTML `font-family="..."` attribute.
_SYM_FALLBACK = "'Segoe UI Symbol','Noto Sans Symbols2','Apple Symbols',system-ui,sans-serif"
_TXT_FALLBACK = "system-ui,-apple-system,'Segoe UI',Roboto,sans-serif"

#: font-family stack: the embedded family first, then system symbol fonts
FAMILY = "'%s',%s" % (FAMILY_NAME, _SYM_FALLBACK)
#: stack for symbol glyphs (same embedded family; symbol fallbacks)
SYM_FAMILY = FAMILY
#: stack for text — numerals, labels, ℞ ° ′ ″ (same embedded family; text fallbacks)
TXT_FAMILY = "'%s',%s" % (FAMILY_NAME, _TXT_FALLBACK)

#: Deprecated since 0.2.0 — everything is one family now. Kept so older callers still work.
SYMBOL_FAMILY_NAMES = [FAMILY_NAME]
TEXT_FAMILY_NAME = FAMILY_NAME

#: the font file formats shipped as package data
FONT_FORMATS = ("ttf", "otf", "woff2")

__all__ = [
    "__version__", "FAMILY", "FAMILY_NAME", "SYM_FAMILY", "TXT_FAMILY", "font_face_css",
    "glyph", "glyph_metrics", "alternates", "lot", "keys_to_unicode", "save_fonts",
    "font_bytes", "GLYPHS", "ALTERNATES", "LOTS", "LOT_ALIASES", "PI_KEYMAP", "PRO_KEYMAP",
    "GLYPH_METRICS", "FONT_NAMES", "FONT_FORMATS", "OFL_ATTRIBUTION", "SOURCE_FONT_VERSIONS",
]


def font_face_css(embed: bool = True) -> str:
    """A ``<style>`` element with the ``@font-face`` rule for Astroglyphs 2K, inlined as a
    ``data:`` woff2 URI (self-contained: no network, no external files). Returns ``""`` when
    ``embed`` is False — then ``FAMILY`` falls back to the viewer's system fonts."""
    if not embed:
        return ""
    return ('<style>@font-face{font-family:"%s";src:url(data:font/woff2;base64,%s) '
            'format("woff2");font-weight:100 900;}</style>' % (FAMILY_NAME, WOFF2_B64))


def font_bytes(font: str = FAMILY_NAME, fmt: str = "ttf") -> bytes:
    """Raw bytes of one packaged font file. ``font`` is a name from ``FONT_NAMES``
    ("Astroglyphs 2K", "AstroglyphPi", "AstroglyphPro"); ``fmt`` is "ttf", "otf" or "woff2"."""
    if font not in FONT_FILES:
        raise ValueError("font must be one of %r, not %r" % (FONT_NAMES, font))
    if fmt not in FONT_FORMATS:
        raise ValueError("fmt must be one of %r, not %r" % (FONT_FORMATS, fmt))
    return _res.files(__name__).joinpath("fonts").joinpath(
        FONT_FILES[font] + "." + fmt).read_bytes()


def save_fonts(dest_dir, fonts=None, formats=FONT_FORMATS) -> list:
    """Write installable font files into ``dest_dir`` and return the paths written.

    ``fonts`` defaults to all three (``FONT_NAMES``); ``formats`` to ttf, otf and woff2::

        import astroglyphs_2K as ag
        ag.save_fonts("~/astro-fonts", formats=("otf",))
    """
    import os
    import pathlib
    dest = pathlib.Path(os.path.expanduser(str(dest_dir)))
    dest.mkdir(parents=True, exist_ok=True)
    written = []
    for font in fonts or FONT_NAMES:
        for fmt in formats:
            out = dest / (FONT_FILES[font] + "." + fmt)
            out.write_bytes(font_bytes(font, fmt))
            written.append(out)
    return written


def glyph(name: str) -> str:
    """The character for a glyph by name, e.g. ``glyph("scorpio")`` → "♏",
    ``glyph("lot_of_nemesis")`` → its Private Use character. Raises KeyError if unknown."""
    return chr(GLYPHS[name])


def alternates(name: str) -> list:
    """All forms of a glyph that has alternates, default first —
    e.g. ``alternates("pluto")`` → ["♇", "⯓", "⯔", "⯕", "⯖"]."""
    return [chr(cp) for cp in ALTERNATES[name]]


def lot(name: str) -> str:
    """A Hermetic lot glyph by name or alias, from the contiguous lots block —
    ``lot("eros")``, ``lot("lot of genius")`` (= Spirit). Raises KeyError if unknown."""
    key = name.strip().lower()
    slug = key.replace(" ", "_")
    for cand in (slug, "lot_of_" + slug, LOT_ALIASES.get(key),
                 LOT_ALIASES.get("lot of " + key), LOT_ALIASES.get("lot of the " + key)):
        if cand in LOTS:
            return chr(LOTS[cand])
    raise KeyError(name)


def keys_to_unicode(text: str, layout: str = "pi") -> str:
    """Convert text typed in a keyboard font to real Unicode glyph text.

    ``layout="pi"`` for AstroglyphPi (and AstrotypeP LT Std documents), ``"pro"`` for
    AstroglyphPro. Characters that aren't glyph keys pass through unchanged, so for "pro"
    digits and degree marks survive: ``keys_to_unicode("15a22°", "pro")`` → "15♈22°".
    """
    maps = {"pi": PI_KEYMAP, "pro": PRO_KEYMAP}
    if layout not in maps:
        raise ValueError("layout must be 'pi' or 'pro', not %r" % layout)
    m = maps[layout]
    return "".join(chr(m[c]) if c in m else c for c in text)


def glyph_metrics(ch):
    """Metrics for a glyph as ``(advance, ymin, ymax, xmin, xmax)`` in fractions of the em
    (ink bounding box from the outline), or ``None`` if the glyph isn't in Astroglyphs 2K.

    ``ch`` may be a single-character string or an int codepoint.
    """
    if isinstance(ch, str):
        if len(ch) != 1:
            return None
        cp = ord(ch)
    else:
        cp = int(ch)
    return GLYPH_METRICS.get(cp)
