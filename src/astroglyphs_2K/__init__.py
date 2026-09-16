"""astroglyphs_2K — curated OFL astrology glyph fonts (the "best of Noto") + metrics + embedding.

A tiny, zero-runtime-dependency toolkit that gives any chart renderer a deterministic,
embeddable set of astrology glyphs. The good astrology fonts are proprietary; this subsets and
re-packages the freely-licensed **Noto** family (SIL Open Font License) into compact web fonts
plus real per-glyph metrics, so charts render identically on every device instead of depending
on whatever symbol font the viewer happens to have.

Glyph routing (all OFL, subset + renamed per the Reserved Font Name clause):
- **AstroSym**  (Noto Sans Symbols)   — planets, nodes, 12 signs, asteroids, Chiron, Lilith, Hygeia
- **AstroSym2** (Noto Sans Symbols 2) — the Sun, Eros, Eris, Sedna
- **AstroMath** (Noto Sans Math)      — ⊗ Part of Fortune
- **AstroText** (Noto Sans)           — digits, Latin, ℞ · ° · ′ · ″

Quick use (inline in an SVG or HTML):
    import astroglyphs_2K as ag
    svg = ag.font_face_css() + '<text font-family=%r>%s</text>' % (ag.SYM_FAMILY, "☉︎")

Regenerate the bundled data with ``python tools/build.py`` (needs fonttools + brotli; build-only).
"""

import base64 as _base64
import importlib.resources as _res

from ._data import (  # noqa: F401
    GLYPH_METRICS,
    OFL_ATTRIBUTION,
    SOURCE_FONT_VERSIONS,
    SYMBOL_FAMILY_NAMES,
    SYMBOLS_WOFF2_B64,
    TEXT_FAMILY_NAME,
    TEXT_WOFF2_B64,
)

__version__ = "0.1.0"

# System fallbacks (used when embedding is off, or a viewer strips the embedded face).
# Family names are single-quoted so the stacks are valid both in a CSS `font-family:` value
# AND inside a double-quoted SVG/HTML `font-family="..."` attribute (single quotes can't
# collide with the double-quote delimiter); font-family matching ignores quote style, so the
# `@font-face` rules below keep their double quotes and still bind to these single-quoted refs.
_SYM_FALLBACK = "'Segoe UI Symbol','Noto Sans Symbols2','Apple Symbols',system-ui,sans-serif"
_TXT_FALLBACK = "system-ui,-apple-system,'Segoe UI',Roboto,sans-serif"

#: font-family stack for symbol glyphs (embedded families first, then system fallbacks)
SYM_FAMILY = ",".join("'%s'" % n for n in SYMBOL_FAMILY_NAMES) + "," + _SYM_FALLBACK
#: font-family stack for text (numerals, labels, ℞/°/′/″)
TXT_FAMILY = "'%s',%s" % (TEXT_FAMILY_NAME, _TXT_FALLBACK)

#: the font file formats shipped as package data for each fontset
FONT_FORMATS = ("ttf", "otf", "woff2")
#: the fontsets available as installable/exportable files
FONT_SETS = ("astroset", "fullset")

__all__ = [
    "__version__", "SYM_FAMILY", "TXT_FAMILY", "font_face_css", "glyph_metrics",
    "GLYPH_METRICS", "SYMBOL_FAMILY_NAMES", "TEXT_FAMILY_NAME", "OFL_ATTRIBUTION",
    "SOURCE_FONT_VERSIONS", "save_fonts", "font_bytes", "FONT_FORMATS", "FONT_SETS",
]


def _face(fam, b64, weight=False):
    w = ";font-weight:100 900" if weight else ""
    return ('@font-face{font-family:"%s";src:url(data:font/woff2;base64,%s) '
            'format("woff2")%s;}' % (fam, b64, w))


def _fullset_b64(fam):
    """Base64 of a full-coverage woff2, read from package data (the 'fullset' perk)."""
    return _base64.b64encode(font_bytes(fam, "fullset", "woff2")).decode("ascii")


def _families():
    return list(SYMBOL_FAMILY_NAMES) + [TEXT_FAMILY_NAME]


def font_bytes(family: str, fontset: str = "astroset", fmt: str = "ttf") -> bytes:
    """Raw bytes of one packaged font file — ``family`` (e.g. "AstroSym", "AstroText"),
    ``fontset`` ("astroset" or "fullset") and ``fmt`` ("ttf", "otf" or "woff2")."""
    if fontset not in FONT_SETS:
        raise ValueError("fontset must be one of %r, not %r" % (FONT_SETS, fontset))
    if fmt not in FONT_FORMATS:
        raise ValueError("fmt must be one of %r, not %r" % (FONT_FORMATS, fmt))
    if family not in _families():
        raise ValueError("family must be one of %r, not %r" % (_families(), family))
    return (_res.files(__name__).joinpath("fonts").joinpath(fontset)
            .joinpath(family + "." + fmt).read_bytes())


def save_fonts(dest_dir, fontset: str = "astroset", formats=("ttf", "otf", "woff2")) -> list:
    """Write the packaged font files for ``fontset`` into ``dest_dir`` and return the paths.

    These are the renamed OFL glyph fonts: installable desktop fonts (``ttf`` native, ``otf``/CFF)
    plus the web font (``woff2``). ``"astroset"`` is the compact astrology subset; ``"fullset"`` is
    the whole renamed Noto family (much larger). Example — export installable fonts::

        import astroglyphs_2K as ag
        ag.save_fonts("~/astro-fonts", fontset="fullset", formats=("ttf", "otf"))
    """
    import os
    import pathlib
    dest = pathlib.Path(os.path.expanduser(str(dest_dir)))
    dest.mkdir(parents=True, exist_ok=True)
    written = []
    for fam in _families():
        for fmt in formats:
            out = dest / (fam + "." + fmt)
            out.write_bytes(font_bytes(fam, fontset, fmt))
            written.append(out)
    return written


def font_face_css(embed: bool = True, fontset: str = "astroset") -> str:
    """Return a ``<style>`` element with the ``@font-face`` rules for the embedded fonts.

    Each face inlines its woff2 as a ``data:`` URI, so the output is self-contained (no network,
    no external files). Returns ``""`` when ``embed`` is False — then ``SYM_FAMILY`` / ``TXT_FAMILY``
    fall back to the viewer's system fonts.

    ``fontset``:
      - ``"astroset"`` (default) — the compact curated astrology subset (~60 KB total). Covers
        everything astrology renders; the metrics in ``GLYPH_METRICS`` describe exactly this set.
      - ``"fullset"`` — the whole megacollection: the FULL Noto fonts (text + every symbol),
        under the same family names, for anyone who wants coverage beyond astrology. Much larger
        (a few MB inlined per document) — turn it up to 11 only when you need it.
    """
    if not embed:
        return ""
    if fontset == "astroset":
        faces = [_face(fam, b64)
                 for fam, b64 in zip(SYMBOL_FAMILY_NAMES, SYMBOLS_WOFF2_B64, strict=True)]
        faces.append(_face(TEXT_FAMILY_NAME, TEXT_WOFF2_B64, weight=True))
    elif fontset == "fullset":
        faces = [_face(fam, _fullset_b64(fam)) for fam in SYMBOL_FAMILY_NAMES]
        faces.append(_face(TEXT_FAMILY_NAME, _fullset_b64(TEXT_FAMILY_NAME), weight=True))
    else:
        raise ValueError("fontset must be 'astroset' or 'fullset', not %r" % fontset)
    return "<style>" + "".join(faces) + "</style>"


def glyph_metrics(ch):
    """Metrics for a glyph as ``(advance, ymin, ymax, xmin, xmax)`` in fractions of the em
    (ink bounding box from the outline), or ``None`` if the glyph isn't in the inventory.

    ``ch`` may be a single-character string or an int codepoint.
    """
    cp = ord(ch) if isinstance(ch, str) else int(ch)
    return GLYPH_METRICS.get(cp)
