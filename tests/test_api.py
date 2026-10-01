import base64
import pathlib
import re
import sys

import pytest

import astroglyphs_2K as ag

_REPO = pathlib.Path(__file__).resolve().parent.parent
_PKG_FONTS = _REPO / "src" / "astroglyphs_2K" / "fonts"
_DIST_OUT = _REPO / "Out"
sys.path.insert(0, str(_REPO / "tools"))
import registry as R  # noqa: E402

# The astrology inventory the package promises to cover (must all have metrics).
SIGNS = "♈♉♊♋♌♍♎♏♐♑♒♓"
PLANETS = "☉☽☿♀♂♃♄♅♆♇☊☋♁"
POINTS = "⚸⚷⚳⚴⚵⚶♡⯰☾⚕⯲⊗\U0001F774⦶"
ASPECTS = "☌☍□△⚹⚻⚺∠⚼"
TEXT_MARKS = "℞°′″·0123456789"


# --- embedding --------------------------------------------------------------------------------
def test_family_stacks_name_the_single_embedded_family_first():
    for stack in (ag.FAMILY, ag.SYM_FAMILY, ag.TXT_FAMILY):
        assert stack.startswith("'Astroglyphs 2K'")
        assert '"' not in stack                 # drops safely into font-family="..."
        assert "sans-serif" in stack            # system fallbacks still present


def test_font_face_css_is_one_self_contained_face():
    css = ag.font_face_css()
    assert css.startswith("<style>") and css.endswith("</style>")
    assert css.count("@font-face") == 1
    assert 'font-family:"Astroglyphs 2K"' in css
    (b64,) = re.findall(r"base64,([A-Za-z0-9+/=]+)\)", css)
    assert base64.b64decode(b64)[:4] == b"wOF2"


def test_embed_false_is_empty():
    assert ag.font_face_css(embed=False) == ""


def test_deprecated_family_aliases_still_work():
    assert ag.SYMBOL_FAMILY_NAMES == ["Astroglyphs 2K"]
    assert ag.TEXT_FAMILY_NAME == "Astroglyphs 2K"


# --- inventory & metrics ----------------------------------------------------------------------
@pytest.mark.parametrize("ch", list(SIGNS + PLANETS + POINTS + ASPECTS + TEXT_MARKS))
def test_every_inventory_glyph_has_metrics(ch):
    m = ag.glyph_metrics(ch)
    assert m is not None, "no metrics for %r (U+%04X)" % (ch, ord(ch))
    adv, ymin, ymax, xmin, xmax = m
    assert adv > 0 and ymax >= ymin and xmax >= xmin


def test_glyph_metrics_accepts_int_and_str():
    assert ag.glyph_metrics("☉") == ag.glyph_metrics(0x2609)
    assert ag.glyph_metrics("") is None
    assert ag.glyph_metrics("ab") is None


def test_every_registry_glyph_is_in_the_unicode_font():
    for cp, slug, *_ in R.INVENTORY:
        assert ag.glyph_metrics(cp), slug
    for cp in R.COMPOSED:
        assert ag.glyph_metrics(cp), hex(cp)


def test_composed_glyphs_have_ink():
    for cp, (slug, *_r) in R.COMPOSED.items():
        adv, ymin, ymax, xmin, xmax = ag.glyph_metrics(cp)
        assert ymax > ymin and xmax > xmin, slug


def test_text_presentation_selector_is_present_and_invisible():
    assert ag.glyph_metrics(0xFE0E) == (0.0, 0.0, 0.0, 0.0, 0.0)


# --- names, alternates, lots ------------------------------------------------------------------
def test_glyph_by_name():
    assert ag.glyph("scorpio") == "♏"
    assert ag.glyph("lot_of_fortune") == "\U0001F774"
    with pytest.raises(KeyError):
        ag.glyph("nibiru")


def test_alternates_default_first():
    assert ag.alternates("pluto")[0] == "♇"
    assert "⯓" in ag.alternates("pluto")
    assert ag.alternates("uranus") == ["♅", "⛢"]


def test_lots_block_is_contiguous_in_paulus_order():
    order = ["lot_of_fortune", "lot_of_spirit", "lot_of_eros", "lot_of_necessity",
             "lot_of_courage", "lot_of_victory", "lot_of_nemesis"]
    assert list(ag.LOTS) == order
    assert [ag.LOTS[k] for k in order] == list(range(0xE100, 0xE107))


def test_lot_lookup_by_name_and_alias():
    assert ag.lot("eros") == ag.lot("Lot of Eros") == ag.lot("lot of love")
    assert ag.lot("lot of genius") == ag.lot("spirit") == ag.lot("daimon")
    with pytest.raises(KeyError):
        ag.lot("marriage")              # not curated: no established glyph


def test_lot_aliases_share_outlines():
    # E100/E101 are the same drawing as the Unicode Fortune / Spirit glyphs
    assert ag.glyph_metrics(0xE100) == ag.glyph_metrics(0x1F774)
    assert ag.glyph_metrics(0xE101) == ag.glyph_metrics(0x29B6)


# --- keyboard layouts -------------------------------------------------------------------------
def test_keys_to_unicode_pro_keeps_text():
    assert ag.keys_to_unicode("15a22°", "pro") == "15♈22°"
    assert ag.keys_to_unicode("J 3°h", "pro") == "♇ 3°♏"


def test_keys_to_unicode_pi_matches_astrotype_layout():
    assert ag.keys_to_unicode("1Q", "pi") == "☉♈"           # Sun, Aries
    assert ag.keys_to_unicode("rt", "pi") == "☊☋"           # nodes
    assert ag.keys_to_unicode(" ", "pi") == " "
    with pytest.raises(ValueError):
        ag.keys_to_unicode("x", "qwerty")


def test_every_key_maps_to_a_glyph_in_the_unicode_font():
    for km in (ag.PI_KEYMAP, ag.PRO_KEYMAP):
        for key, cp in km.items():
            assert ag.glyph_metrics(cp), (key, hex(cp))


def test_keyboard_fonts_carry_their_key_maps():
    from fontTools.ttLib import TTFont  # build/test-only dependency
    for name, km, text_ok in (("AstroglyphPi", ag.PI_KEYMAP, ""),
                              ("AstroglyphPro", ag.PRO_KEYMAP, "0123456789°′″.,")):
        cmap = TTFont(_PKG_FONTS / (name + ".ttf")).getBestCmap()
        for key in km:
            assert ord(key) in cmap, (name, key)
        for c in text_ok:
            assert ord(c) in cmap, (name, c)


# --- files ------------------------------------------------------------------------------------
_MAGIC = {"ttf": b"\x00\x01\x00\x00", "otf": b"OTTO", "woff2": b"wOF2"}


@pytest.mark.parametrize("font", ag.FONT_NAMES)
@pytest.mark.parametrize("fmt", ag.FONT_FORMATS)
def test_font_bytes_valid_magic(font, fmt):
    assert ag.font_bytes(font, fmt)[:4] == _MAGIC[fmt]


def test_font_bytes_rejects_bad_args():
    with pytest.raises(ValueError):
        ag.font_bytes("AstroSym", "ttf")
    with pytest.raises(ValueError):
        ag.font_bytes("AstroglyphPi", "pfm")


def test_save_fonts_writes_files(tmp_path):
    written = ag.save_fonts(tmp_path, formats=("ttf", "otf"))
    assert len(written) == len(ag.FONT_NAMES) * 2
    assert (tmp_path / "AstroglyphPi.otf").read_bytes()[:4] == b"OTTO"
    assert (tmp_path / "Astroglyphs2K.ttf").read_bytes()[:4] == b"\x00\x01\x00\x00"


def test_fonts_carry_ofl_licence_and_reserved_name_compliance():
    from fontTools.ttLib import TTFont
    for name in ag.FONT_NAMES:
        nt = TTFont(_PKG_FONTS / (ag.FONT_FILES[name] + ".ttf"))["name"]
        assert "Open Font License" in nt.getDebugName(13)
        assert nt.getDebugName(1) == name
        assert "Noto" not in nt.getDebugName(1)          # OFL Reserved Font Name


def test_attribution_present():
    assert "Open Font License" in ag.OFL_ATTRIBUTION
    assert ag.SOURCE_FONT_VERSIONS


# --- Out/ mirrors the package fonts byte-for-byte ---------------------------------------------
@pytest.mark.parametrize("font", ag.FONT_NAMES)
@pytest.mark.parametrize("fmt", ag.FONT_FORMATS)
def test_out_folder_mirrors_package_fonts(font, fmt):
    stem = ag.FONT_FILES[font]
    pkg = (_PKG_FONTS / f"{stem}.{fmt}").read_bytes()
    out = (_DIST_OUT / stem / fmt.upper() / f"{stem}.{fmt}").read_bytes()
    assert out == pkg, "Out/ is stale — run: python tools/build.py --out-only"


def test_out_folder_ships_licence():
    assert (_DIST_OUT / "OFL.txt").read_bytes() == (_REPO / "LICENSES" / "OFL.txt").read_bytes()
