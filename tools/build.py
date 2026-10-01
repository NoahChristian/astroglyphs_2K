#!/usr/bin/env python3
"""build.py — build the three astroglyphs_2K fonts from the vendored Noto sources.

- **Astroglyphs 2K** (Unicode)   -> package data + ``_data.py`` (inline woff2 + metrics + maps)
- **AstroglyphPi**  (keyboard)   -> AstrotypeP LT Std-compatible key layout
- **AstroglyphPro** (keyboard)   -> mnemonic key layout, digits/punctuation stay text

Every glyph comes from ONE pool built from ``tools/registry.py``: outlines are taken from the
first Noto source that has the codepoint (decomposed, em-scale corrections applied), and the
few glyphs Unicode has no codepoint for (moon phases, Hermetic lots) are composed here. Each font
is then just a different character map onto that pool, so the three can never drift apart.

Outputs: src/astroglyphs_2K/fonts/<Font>.{ttf,otf,woff2}, src/astroglyphs_2K/_data.py,
spec/astroglyph_{pi,pro}.csv, and the Out/ download mirror.

Build-only. Needs: fonttools, brotli, skia-pathops.   Run:  python tools/build.py
Refresh only Out/ from the committed package fonts:      python tools/build.py --out-only
Deterministic: same sources -> same outputs (timestamps are pinned).
"""
from __future__ import annotations

import base64
import csv
import io
import pathlib
import shutil
import sys
import unicodedata

import pathops
from fontTools.fontBuilder import FontBuilder
from fontTools.misc.transform import Identity, Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import registry as R  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
FONTS = HERE / "fonts"
PKG = REPO / "src" / "astroglyphs_2K"
DATA_OUT = PKG / "_data.py"
PKG_FONTS = PKG / "fonts"
DIST_OUT = REPO / "Out"
SPEC = REPO / "spec"

VERSION = "0.2.0"
UPM = 1000
FIXED_TIME = 3870000000            # pinned head.created/modified (2026-08-21) for determinism
FONT_EXTS = ("ttf", "otf", "woff2")

# (file stem, family name) for each output font
UNICODE_FONT = ("Astroglyphs2K", "Astroglyphs 2K")
PI_FONT = ("AstroglyphPi", "AstroglyphPi")
PRO_FONT = ("AstroglyphPro", "AstroglyphPro")
FONT_LIST = (UNICODE_FONT, PI_FONT, PRO_FONT)

TEXT_SOURCE = "NotoSans.ttf"
SYMBOL_SOURCES = ["NotoSansSymbols.ttf", "NotoSansSymbols2.ttf", "NotoSansMath.ttf", "NotoSans.ttf"]

# Per-glyph em-scale corrections, applied about the ink centre (advance unchanged). The Symbols 2
# Sun draws a touch big beside the Symbols planets -> 90%.
GLYPH_EM_SCALE = {0x2609: 0.90}

# Composition geometry (font units)
LOT_PLANET_SCALE = 0.86            # planet size inside a composed lot glyph
LOT_INDEX_SCALE = 0.40             # the small Lot-of-Fortune index at lower right
LOT_GAP = 18                       # gap between planet and index
SIDE_BEARING = 51                  # matches Noto Sans Symbols' typical side bearing
MOON_OFFSET = 0.42                 # crescent terminator offset, as a fraction of the radius
MOON_STROKE = 0.085                # outline thickness, as a fraction of the radius


# ----------------------------------------------------------------------------- glyph pool ----
class Glyph:
    """An outline (recorded pen ops, font units) plus its advance width."""

    def __init__(self, rec: RecordingPen, advance: int):
        self.rec = rec
        self.advance = int(round(advance))

    def bounds(self):
        bp = BoundsPen(None)
        self.rec.replay(bp)
        return bp.bounds


class Sources:
    def __init__(self):
        self.fonts = {fn: TTFont(FONTS / fn) for fn in set(SYMBOL_SOURCES + [TEXT_SOURCE])}
        self.cmaps = {fn: f.getBestCmap() for fn, f in self.fonts.items()}
        self.gsets = {fn: f.getGlyphSet() for fn, f in self.fonts.items()}

    def find(self, cp, text=False):
        order = [TEXT_SOURCE] + SYMBOL_SOURCES if text else SYMBOL_SOURCES
        for fn in order:
            if cp in self.cmaps[fn]:
                return fn
        return None

    def glyph(self, cp, text=False) -> tuple[Glyph, str]:
        fn = self.find(cp, text)
        if fn is None:
            raise SystemExit(f"U+{cp:04X} {unicodedata.name(chr(cp), '?')} is in no source font")
        gs = self.gsets[fn]
        gname = self.cmaps[fn][cp]
        rec = DecomposingRecordingPen(gs)
        gs[gname].draw(rec)
        adv = self.fonts[fn]["hmtx"][gname][0]
        g = Glyph(_plain(rec), adv)
        s = GLYPH_EM_SCALE.get(cp)
        if s and g.bounds():
            xmin, ymin, xmax, ymax = g.bounds()
            cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
            g = _transformed(g, Identity.translate(cx, cy).scale(s).translate(-cx, -cy))
        return g, fn

    def notdef(self) -> Glyph:
        gs = self.gsets[TEXT_SOURCE]
        rec = DecomposingRecordingPen(gs)
        gs[".notdef"].draw(rec)
        return Glyph(_plain(rec), self.fonts[TEXT_SOURCE]["hmtx"][".notdef"][0])


def _plain(rec) -> RecordingPen:
    out = RecordingPen()
    rec.replay(out)
    return out


def _transformed(g: Glyph, t: Transform, advance=None) -> Glyph:
    out = RecordingPen()
    g.rec.replay(TransformPen(out, t))
    return Glyph(out, g.advance if advance is None else advance)


def _circle(path: pathops.Path, cx, cy, r):
    """Append a clockwise circle (4 cubic arcs) to a pathops Path."""
    k = 0.5522847498 * r
    path.moveTo(cx, cy + r)
    path.cubicTo(cx + k, cy + r, cx + r, cy + k, cx + r, cy)
    path.cubicTo(cx + r, cy - k, cx + k, cy - r, cx, cy - r)
    path.cubicTo(cx - k, cy - r, cx - r, cy - k, cx - r, cy)
    path.cubicTo(cx - r, cy + k, cx - k, cy + r, cx, cy + r)
    path.close()


def _disc(cx, cy, r):
    p = pathops.Path()
    _circle(p, cx, cy, r)
    return p


def _op(a, b, op):
    return pathops.op(a, b, op, fix_winding=True, keep_starting_points=False, clockwise=True)


def compose_moon(ref: Glyph, dark_side: str, kind: str) -> Glyph:
    """Moon phase sized and placed like the reference white circle (U+25CB)."""
    xmin, ymin, xmax, ymax = ref.bounds()
    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
    r = (xmax - xmin) / 2
    w = r * MOON_STROKE
    shift = r * MOON_OFFSET * (1 if dark_side == "left" else -1)
    D, U = pathops.PathOp.DIFFERENCE, pathops.PathOp.UNION
    if kind == "gibbous":       # white disc + outline, dark crescent on dark_side
        ring = _op(_disc(cx, cy, r), _disc(cx, cy, r - w), D)
        crescent = _op(_disc(cx, cy, r), _disc(cx + shift, cy, r), D)
        shape = _op(ring, crescent, U)
    else:                       # dark disc, white crescent opposite dark_side
        inner = r - w
        lit = _op(_disc(cx, cy, inner), _disc(cx - shift, cy, inner), D)   # sliver, far side
        shape = _op(_disc(cx, cy, r), lit, D)
    rec = RecordingPen()
    shape.draw(rec)
    return Glyph(rec, ref.advance)


def compose_lot(planet: Glyph, index: Glyph) -> Glyph:
    """Planet glyph with a small Lot-of-Fortune index at its lower right."""
    p = _transformed(planet, Identity.scale(LOT_PLANET_SCALE))
    pxmin, pymin, pxmax, pymax = p.bounds()
    p = _transformed(p, Identity.translate(SIDE_BEARING - pxmin, 0))
    pxmax += SIDE_BEARING - pxmin
    ixmin, iymin, ixmax, iymax = index.bounds()
    s = LOT_INDEX_SCALE
    tx = pxmax + LOT_GAP - ixmin * s
    ty = pymin - iymin * s
    i = _transformed(index, Identity.translate(tx, ty).scale(s))
    rec = RecordingPen()
    p.rec.replay(rec)
    i.rec.replay(rec)
    out = Glyph(rec, 0)
    out.advance = int(round(out.bounds()[2] + SIDE_BEARING))
    return out


def build_pool(src: Sources):
    """{codepoint: Glyph} for every Unicode + PUA glyph, plus {codepoint: source label}."""
    pool, origin = {}, {}
    for c in R.TEXT_CHARS:
        g, fn = src.glyph(ord(c), text=True)
        pool[ord(c)], origin[ord(c)] = g, fn
    for cp, *_ in R.INVENTORY:
        if cp in pool:
            continue
        g, fn = src.glyph(cp)
        pool[cp], origin[cp] = g, fn
    pool[0xFE0E] = Glyph(RecordingPen(), 0)      # text-presentation selector: present, invisible
    origin[0xFE0E] = "empty"
    for cp, (_slug, _label, _cat, how) in R.COMPOSED.items():
        if how[0] == "moon":
            pool[cp] = compose_moon(pool[0x25CB], how[1], how[2])
            origin[cp] = "composed (moon phase)"
        elif how[0] == "alias":
            pool[cp] = pool[how[1]]
            origin[cp] = f"same glyph as U+{how[1]:04X}"
        elif how[0] == "lot":
            pool[cp] = compose_lot(pool[how[1]], pool[0x1F774])
            origin[cp] = f"composed (U+{how[1]:04X} + lot index)"
    return pool, origin


# --------------------------------------------------------------------------- font output ----
def _gname(cp):
    return "space" if cp == 0x20 else (f"uni{cp:04X}" if cp <= 0xFFFF else f"u{cp:05X}")


def _name_table(family, stem, src_versions):
    ofl_url = "https://openfontlicense.org"
    return {
        "copyright": "Copyright 2022 The Noto Project Authors "
                     "(https://github.com/notofonts). Modifications copyright 2026 "
                     "Elizabeth Huston and Noah Christian.",
        "familyName": family,
        "styleName": "Regular",
        "uniqueFontIdentifier": f"{VERSION};{stem}-Regular",
        "fullName": f"{family} Regular",
        "psName": f"{stem}-Regular",
        "version": f"Version {VERSION}",
        "manufacturer": "astroglyphs_2K",
        "designer": "The Noto Project Authors; composition by Elizabeth Huston and Noah Christian",
        "description": "Astrology glyphs built from Noto (" + ", ".join(src_versions) + ").",
        "vendorURL": "https://github.com/NoahChristian/astroglyphs_2K",
        "licenseDescription": "This Font Software is licensed under the SIL Open Font License, "
                              "Version 1.1. This license is available with a FAQ at: " + ofl_url,
        "licenseInfoURL": ofl_url,
    }


def build_font(stem, family, cmap: dict[int, int], pool, notdef, src_versions) -> TTFont:
    """cmap: {char codepoint in this font: pool codepoint}. Returns a TrueType TTFont."""
    targets = sorted(set(cmap.values()))
    order = [".notdef"] + [_gname(cp) for cp in targets]
    glyphs, metrics = {}, {}

    def put(name, g: Glyph):
        pen = TTGlyphPen(None)
        g.rec.replay(Cu2QuPen(pen, max_err=1.0, reverse_direction=False))
        glyphs[name] = pen.glyph()
        b = g.bounds()
        metrics[name] = (g.advance, int(round(b[0])) if b else 0)

    put(".notdef", notdef)
    for cp in targets:
        put(_gname(cp), pool[cp])
    fb = FontBuilder(UPM, isTTF=True)
    fb.font.recalcTimestamp = False
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap({k: _gname(v) for k, v in cmap.items()})
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    ymax = max((g.yMax for g in glyphs.values() if hasattr(g, "yMax") and g.numberOfContours),
               default=1069)
    ymin = min((g.yMin for g in glyphs.values() if hasattr(g, "yMin") and g.numberOfContours),
               default=-293)
    fb.setupHorizontalHeader(ascent=1069, descent=-293, lineGap=0)
    fb.setupNameTable(_name_table(family, stem, src_versions))
    fb.setupOS2(sTypoAscender=1069, sTypoDescender=-293, sTypoLineGap=0,
                usWinAscent=max(1069, ymax), usWinDescent=max(293, -ymin),
                fsType=0, achVendID="NONE", fsSelection=0x40 | 0x80, version=4)
    fb.setupPost()
    head = fb.font["head"]
    head.created = head.modified = FIXED_TIME
    head.fontRevision = float(VERSION.rsplit(".", 1)[0]) if VERSION.count(".") else 1.0
    return fb.font


def _to_otf(ttf):
    """TrueType -> OpenType-CFF (.otf) with real cubic charstrings via qu2cu."""
    go = ttf.getGlyphOrder()
    hmtx = ttf["hmtx"]
    gs = ttf.getGlyphSet()
    charstrings = {}
    for g in go:
        pen = T2CharStringPen(hmtx[g][0], gs)
        gs[g].draw(Qu2CuPen(pen, max_err=1.0, all_cubic=True))
        charstrings[g] = pen.getCharString()
    fb = FontBuilder(ttf["head"].unitsPerEm, isTTF=False)
    fb.font.recalcTimestamp = False
    fb.setupGlyphOrder(go)
    fb.setupCharacterMap(ttf.getBestCmap())
    fb.setupHorizontalMetrics({g: hmtx[g] for g in go})
    hh = ttf["hhea"]
    fb.setupHorizontalHeader(ascent=hh.ascent, descent=hh.descent, lineGap=hh.lineGap)
    nm = ttf["name"]
    names = {key: nm.getDebugName(i) for key, i in (
        ("copyright", 0), ("familyName", 1), ("styleName", 2), ("uniqueFontIdentifier", 3),
        ("fullName", 4), ("version", 5), ("psName", 6), ("manufacturer", 8), ("designer", 9),
        ("description", 10), ("vendorURL", 11), ("licenseDescription", 13),
        ("licenseInfoURL", 14))}
    fb.setupNameTable(names)
    o = ttf["OS/2"]
    fb.setupOS2(sTypoAscender=o.sTypoAscender, sTypoDescender=o.sTypoDescender,
                sTypoLineGap=o.sTypoLineGap, usWinAscent=o.usWinAscent,
                usWinDescent=o.usWinDescent, fsType=0, achVendID="NONE",
                fsSelection=o.fsSelection, version=4)
    fb.setupCFF(names["psName"], {"FullName": names["fullName"]}, charstrings, {})
    fb.setupPost()
    head = fb.font["head"]
    head.created = head.modified = FIXED_TIME
    return fb.font


def emit(font: TTFont, stem: str) -> dict[str, bytes]:
    """Save ttf / otf / woff2 into the package fonts dir; return {ext: bytes}."""
    PKG_FONTS.mkdir(parents=True, exist_ok=True)
    otf = _to_otf(font)
    out = {}
    for obj, flavor, ext in ((font, None, "ttf"), (font, "woff2", "woff2"), (otf, None, "otf")):
        obj.flavor = flavor
        buf = io.BytesIO()
        obj.save(buf)
        out[ext] = buf.getvalue()
        (PKG_FONTS / f"{stem}.{ext}").write_bytes(out[ext])
    font.flavor = None
    return out


def metrics_for(font: TTFont, cps) -> dict[int, tuple]:
    """{codepoint: (adv, ymin, ymax, xmin, xmax)} as fractions of em, ink bbox from outlines."""
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    gs = font.getGlyphSet()
    out = {}
    for cp in cps:
        gname = cmap.get(cp)
        if not gname:
            continue
        pen = BoundsPen(gs)
        gs[gname].draw(pen)
        xmin, ymin, xmax, ymax = (v / UPM for v in pen.bounds) if pen.bounds else (0, 0, 0, 0)
        out[cp] = (round(hmtx[gname][0] / UPM, 4), round(ymin, 4), round(ymax, 4),
                   round(xmin, 4), round(xmax, 4))
    return out


# ----------------------------------------------------------------------- data + docs out ----
def uname(cp):
    if 0xE000 <= cp <= 0xF8FF:
        return "PRIVATE USE (" + R.COMPOSED[cp][1] + ")"
    known = {0x1F774: "LOT OF FORTUNE"}       # Unicode 15; older unicodedata lacks it
    return known.get(cp) or unicodedata.name(chr(cp), "")


def write_spec_csv(name, rows):
    SPEC.mkdir(exist_ok=True)
    with open(SPEC / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["key", "key_hex", "unicode", "unicode_name", "identity", "status", "note"])
        for k, cp, ident, st, note in rows:
            w.writerow([k, f"0x{ord(k):02X}", f"U+{cp:04X}", uname(cp), ident, st, note])


def write_data(woff2: bytes, metrics, src_versions):
    ofl = (FONTS / "OFL.txt").read_text(encoding="utf-8").split(
        "-----------------------------------")[0].strip()
    glyphs = {slug: cp for cp, slug, _l, _c in R.INVENTORY}
    glyphs.update({slug: cp for cp, (slug, *_r) in R.COMPOSED.items()})
    lots = {slug: R.PUA_LOTS + i for i, (slug, *_r) in enumerate(R.HERMETIC_LOTS)}
    lot_aliases = {a: slug for slug, _l, _h, aliases in R.HERMETIC_LOTS for a in aliases}
    L = ['"""Generated by tools/build.py — DO NOT EDIT. OFL font data, metrics and glyph maps."""',
         "# fmt: off",
         f"FAMILY_NAME = {UNICODE_FONT[1]!r}",
         f"FONT_NAMES = {[f for _s, f in FONT_LIST]!r}",
         f"FONT_FILES = {dict((f, s) for s, f in FONT_LIST)!r}",
         f"WOFF2_B64 = {base64.b64encode(woff2).decode('ascii')!r}",
         "# glyph slug -> codepoint (Unicode or Private Use)",
         "GLYPHS = {"]
    L += [f"    {k!r}: 0x{v:04X}," for k, v in glyphs.items()]
    L += ["}", "# name -> codepoints, default form first", "ALTERNATES = {"]
    L += [f"    {k!r}: [{', '.join(f'0x{c:04X}' for c in v)}]," for k, v in R.ALTERNATES.items()]
    L += ["}", "# the contiguous lots block (Private Use, Hermetic lots in Paulus order)",
          "LOTS = {"]
    L += [f"    {k!r}: 0x{v:04X}," for k, v in lots.items()]
    L += ["}", f"LOT_ALIASES = {lot_aliases!r}",
          "# keyboard font key -> Unicode/PUA codepoint it shows",
          "PI_KEYMAP = {"]
    L += [f"    {k!r}: 0x{cp:04X}," for k, cp, *_r in R.PI_KEYS]
    L += ["}", "PRO_KEYMAP = {"]
    L += [f"    {k!r}: 0x{cp:04X}," for k, cp, *_r in R.PRO_KEYS]
    L += ["}", "# codepoint -> (advance, ymin, ymax, xmin, xmax) as fractions of em (ink bbox)",
          "GLYPH_METRICS = {"]
    L += [f"    0x{cp:04X}: {metrics[cp]!r}," for cp in sorted(metrics)]
    L += ["}", f"SOURCE_FONT_VERSIONS = {src_versions!r}", f"OFL_ATTRIBUTION = {ofl!r}", ""]
    DATA_OUT.write_text("\n".join(L), encoding="utf-8")


def sync_out():
    """Mirror package fonts into Out/<Font>/<FORMAT>/ plus the OFL licence; prune stale files."""
    keep_dirs = {s for s, _f in FONT_LIST}
    if DIST_OUT.exists():
        for d in DIST_OUT.iterdir():
            if d.is_dir() and d.name not in keep_dirs:
                shutil.rmtree(d)
    for stem, _fam in FONT_LIST:
        for ext in FONT_EXTS:
            dest = DIST_OUT / stem / ext.upper()
            dest.mkdir(parents=True, exist_ok=True)
            for old in dest.iterdir():
                if old.name != f"{stem}.{ext}":
                    old.unlink()
            shutil.copyfile(PKG_FONTS / f"{stem}.{ext}", dest / f"{stem}.{ext}")
    shutil.copyfile(REPO / "LICENSES" / "OFL.txt", DIST_OUT / "OFL.txt")
    print(f"synced font files -> {DIST_OUT}")


def main():
    src = Sources()
    pool, origin = build_pool(src)
    notdef = src.notdef()
    src_versions = {fn: f["name"].getDebugName(5) for fn, f in sorted(src.fonts.items())}
    vers = [f"{fn[:-4]} {v.split(';')[0]}" for fn, v in src_versions.items()]

    # stale package fonts from the old four-family layout
    if PKG_FONTS.exists():
        for p in PKG_FONTS.iterdir():
            if p.is_dir():
                shutil.rmtree(p)

    # 1. Astroglyphs 2K: every pool glyph at its own codepoint
    uni_cmap = {cp: cp for cp in pool}
    uni = build_font(*UNICODE_FONT, uni_cmap, pool, notdef, vers)
    files = emit(uni, UNICODE_FONT[0])
    metrics = metrics_for(uni, sorted(pool))

    # 2. AstroglyphPi: AstrotypeP layout (space stays a space)
    pi_cmap = {0x20: 0x20, 0xA0: 0x20}
    pi_cmap.update({ord(k): cp for k, cp, *_r in R.PI_KEYS})
    emit(build_font(*PI_FONT, pi_cmap, pool, notdef, vers), PI_FONT[0])

    # 3. AstroglyphPro: mnemonic layout; non-letter text stays text
    pro_cmap = {ord(c): ord(c) for c in R.PRO_TEXT_CHARS}
    pro_cmap.update({ord(k): cp for k, cp, *_r in R.PRO_KEYS})
    emit(build_font(*PRO_FONT, pro_cmap, pool, notdef, vers), PRO_FONT[0])

    write_data(files["woff2"], metrics, src_versions)
    write_spec_csv("astroglyph_pi.csv", R.PI_KEYS)
    write_spec_csv("astroglyph_pro.csv", R.PRO_KEYS)
    for stem, fam in FONT_LIST:
        sizes = ", ".join(f"{ext} {(PKG_FONTS / f'{stem}.{ext}').stat().st_size // 1024} KB"
                          for ext in FONT_EXTS)
        print(f"{fam:15} {sizes}")
    print(f"wrote {DATA_OUT.relative_to(REPO)} ({DATA_OUT.stat().st_size // 1024} KB), "
          f"metrics for {len(metrics)} glyphs")
    sync_out()


if __name__ == "__main__":
    if "--out-only" in sys.argv[1:]:
        sync_out()
    else:
        main()
