import base64

import pytest

import astroglyphs_2K as ag

# The astrology inventory the package promises to cover (must all have metrics).
SIGNS = "♈♉♊♋♌♍♎♏♐♑♒♓"
PLANETS = "☉☽☿♀♂♃♄♅♆♇☊☋"
POINTS = "⚸⚷⚳⚴⚵⚶♡⯰☾⚕⯲⊗"
ASPECTS = "☌☍□△⚹⚻⚺∠⚼"
TEXT_MARKS = "℞°′″·0123456789"


def test_family_stacks_name_embedded_first():
    # family names are single-quoted so the stacks drop safely into a double-quoted
    # `font-family="..."` SVG/HTML attribute as well as a CSS value
    assert ag.SYM_FAMILY.startswith("'AstroSym'")
    assert ag.TXT_FAMILY.startswith("'AstroText'")
    assert '"' not in ag.SYM_FAMILY and '"' not in ag.TXT_FAMILY
    # system fallbacks are still present
    assert "sans-serif" in ag.SYM_FAMILY and "sans-serif" in ag.TXT_FAMILY


def test_font_face_css_astroset_is_self_contained():
    css = ag.font_face_css()
    assert css.startswith("<style>") and css.endswith("</style>")
    # one face per symbol family + the text family
    assert css.count("@font-face") == len(ag.SYMBOL_FAMILY_NAMES) + 1
    assert "url(data:font/woff2;base64," in css
    for fam in ag.SYMBOL_FAMILY_NAMES + [ag.TEXT_FAMILY_NAME]:
        assert 'font-family:"%s"' % fam in css


def test_embed_false_is_empty():
    assert ag.font_face_css(embed=False) == ""


def test_fullset_is_larger_and_valid():
    astro = ag.font_face_css(fontset="astroset")
    full = ag.font_face_css(fontset="fullset")
    assert full.count("@font-face") == len(ag.SYMBOL_FAMILY_NAMES) + 1
    assert len(full) > len(astro) * 5           # the whole megacollection is much bigger
    # every inlined blob decodes as valid base64 (woff2 magic "wOF2")
    import re
    for b64 in re.findall(r"base64,([A-Za-z0-9+/=]+)\)", full):
        assert base64.b64decode(b64)[:4] == b"wOF2"


def test_bad_fontset_raises():
    with pytest.raises(ValueError):
        ag.font_face_css(fontset="everything")


@pytest.mark.parametrize("ch", list(SIGNS + PLANETS + POINTS + ASPECTS + TEXT_MARKS))
def test_every_inventory_glyph_has_metrics(ch):
    m = ag.glyph_metrics(ch)
    assert m is not None, "no metrics for %r (U+%04X)" % (ch, ord(ch))
    adv, ymin, ymax, xmin, xmax = m
    assert adv > 0 and ymax >= ymin and xmax >= xmin


def test_glyph_metrics_accepts_int_and_str():
    assert ag.glyph_metrics("☉") == ag.glyph_metrics(0x2609)
    assert ag.glyph_metrics("") is None       # not in inventory


def test_attribution_present():
    assert "Open Font License" in ag.OFL_ATTRIBUTION
    assert ag.SOURCE_FONT_VERSIONS  # non-empty provenance


# sfnt magic per format: TrueType (0x00010000), OpenType-CFF ("OTTO"), woff2 ("wOF2")
_MAGIC = {"ttf": b"\x00\x01\x00\x00", "otf": b"OTTO", "woff2": b"wOF2"}


@pytest.mark.parametrize("fontset", ag.FONT_SETS)
@pytest.mark.parametrize("fmt", ag.FONT_FORMATS)
def test_font_bytes_valid_magic(fontset, fmt):
    for fam in list(ag.SYMBOL_FAMILY_NAMES) + [ag.TEXT_FAMILY_NAME]:
        data = ag.font_bytes(fam, fontset, fmt)
        assert data[:4] == _MAGIC[fmt], f"{fam} {fontset} {fmt} bad magic {data[:4]!r}"


def test_font_bytes_rejects_bad_args():
    with pytest.raises(ValueError):
        ag.font_bytes("AstroSym", "everything", "ttf")
    with pytest.raises(ValueError):
        ag.font_bytes("AstroSym", "astroset", "pfm")
    with pytest.raises(ValueError):
        ag.font_bytes("NotAFamily", "astroset", "ttf")


def test_save_fonts_writes_files(tmp_path):
    written = ag.save_fonts(tmp_path, fontset="astroset", formats=("ttf", "otf"))
    assert len(written) == (len(ag.SYMBOL_FAMILY_NAMES) + 1) * 2
    for p in written:
        assert p.exists() and p.stat().st_size > 0
    # the otf really is OpenType-CFF, the ttf really is TrueType
    assert (tmp_path / "AstroText.otf").read_bytes()[:4] == b"OTTO"
    assert (tmp_path / "AstroText.ttf").read_bytes()[:4] == b"\x00\x01\x00\x00"
