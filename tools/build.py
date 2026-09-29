#!/usr/bin/env python3
"""build.py — generate src/astroglyphs_2K/_data.py from the vendored Noto sources.

Subsets each Noto font to the astrology glyph inventory (routing every glyph to whichever
source font actually contains it, verified by cmap), renames the family per the OFL Reserved
Font Name clause, emits woff2, base64-encodes it, and extracts real per-glyph metrics.

Also mirrors the finished font files into the top-level Out/ folder (see sync_out).

Build-only. Needs: fonttools, brotli. Run:  python tools/build.py
Refresh only Out/ from the committed package fonts (no rebuild):  python tools/build.py --out-only
Deterministic: same sources -> same _data.py.
"""
from __future__ import annotations

import base64
import io
import pathlib

from fontTools.fontBuilder import FontBuilder
from fontTools.misc.transform import Identity
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

HERE = pathlib.Path(__file__).resolve().parent
FONTS = HERE / "fonts"
OUT = HERE.parent / "src" / "astroglyphs_2K" / "_data.py"
# Top-level, human-browsable copy of every installable font file: Out/<fontset>/<FORMAT>/...
DIST_OUT = HERE.parent / "Out"
FONT_SETS = ("astroset", "fullset")
FONT_EXTS = ("ttf", "otf", "woff2")

# Per-glyph em-scale corrections: a source font can draw a glyph larger than the rest of the
# inventory at the same em, so we scale its outline about its ink centre (advance unchanged, so
# it stays centred) to bring it into line. Applied to the subset, the fullset AND the metrics, so
# every consumer sees one consistent glyph size. The AstroSym2 Sun reads a touch big beside the
# AstroSym planets -> 90%.
GLYPH_EM_SCALE = {0x2609: 0.90}   # ☉ Sun (from Noto Sans Symbols 2)


def _apply_glyph_scales(font):
    """Scale each GLYPH_EM_SCALE glyph present in ``font`` about its ink centre (in place).
    Decomposes via pens, so it works for simple and composite glyphs; hmtx is left untouched."""
    if "glyf" not in font:
        return
    cmap = font.getBestCmap()
    glyf = font["glyf"]
    gs = font.getGlyphSet()
    for cp, s in GLYPH_EM_SCALE.items():
        gname = cmap.get(cp)
        if not gname:
            continue
        bp = BoundsPen(gs)
        gs[gname].draw(bp)
        if not bp.bounds:
            continue
        xmin, ymin, xmax, ymax = bp.bounds
        cx, cy = (xmin + xmax) / 2.0, (ymin + ymax) / 2.0
        t = Identity.translate(cx, cy).scale(s).translate(-cx, -cy)
        pen = TTGlyphPen(gs)
        gs[gname].draw(TransformPen(pen, t))
        glyf[gname] = pen.glyph()
        glyf[gname].recalcBounds(glyf)

# --- the astrology glyph inventory (the source of truth; a superset of ephemvis's needs) ---
SIGNS = "♈♉♊♋♌♍♎♏♐♑♒♓"                       # 2648-2653
PLANETS = "☉☽☿♀♂♃♄♅♆♇☊☋"                     # Sun..Pluto, North/South node
POINTS = "⚸⚷⚳⚴⚵⚶♡⯰☾⚕⯲⊗"                     # Lilith, Chiron, Ceres, Pallas, Juno, Vesta,
#                                               Eros, Eris, Asteroid-Lilith, Hygeia, Sedna, PoF
ASPECTS = "☌☍□△⚹⚻⚺∠⚼"                        # conj, opp, square, trine, sextile, quincunx,
#                                               semisextile, semisquare, sesquiquadrate
MISC_SYM = "✦·"                               # fixed-star marker, middle dot
FE0E = "︎"                                # text-presentation variation selector
SYMBOL_CHARS = SIGNS + PLANETS + POINTS + ASPECTS + MISC_SYM

# text side: printable ASCII (digits, Latin, punctuation) + the DMS/retrograde marks
TEXT_CHARS = "".join(chr(c) for c in range(0x20, 0x7F)) + "℞°′″·"

# source fonts, in priority order for routing symbol glyphs
SYMBOL_SOURCES = [
    ("AstroSym", "NotoSansSymbols.ttf"),
    ("AstroSym2", "NotoSansSymbols2.ttf"),
    ("AstroMath", "NotoSansMath.ttf"),
]
TEXT_SOURCE = ("AstroText", "NotoSans.ttf")


def _cmap(font):
    s = set()
    for t in font["cmap"].tables:
        if t.isUnicode():
            s |= set(t.cmap)
    return s


def _rename(font, new_family):
    """Rename the family everywhere in the name table (OFL Reserved Font Name compliance)."""
    name = font["name"]
    for rec in name.names:
        nid = rec.nameID
        if nid in (1, 16):          # family / typographic family
            rec.string = new_family
        elif nid in (4,):           # full name
            rec.string = new_family + " Regular"
        elif nid in (6,):           # postscript name
            rec.string = new_family.replace(" ", "") + "-Regular"


def _subset_font(src_path, unicodes, new_family):
    """Load a source font, apply the glyph-scale corrections, subset to ``unicodes`` and rename
    the family (OFL Reserved Font Name). Returns the TTFont with glyf outlines (no flavor set)."""
    font = TTFont(src_path)
    _apply_glyph_scales(font)
    ss = Subsetter(options=Options(glyph_names=False, notdef_outline=True,
                                   recalc_bounds=True, recalc_timestamp=False,
                                   drop_tables=[], name_IDs=[1, 4, 6, 16]))
    ss.populate(unicodes=unicodes)
    ss.subset(font)
    _rename(font, new_family)
    return font


def _woff2_b64(font):
    """Base64 of ``font`` saved as woff2 (the inline-embed form). Restores glyf flavor after."""
    font.flavor = "woff2"
    buf = io.BytesIO()
    font.save(buf)
    font.flavor = None
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _metrics_from_font(font, unicodes):
    """{codepoint: (adv, ymin, ymax, xmin, xmax)} as fractions of em, ink bbox from outlines."""
    upm = font["head"].unitsPerEm
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    gs = font.getGlyphSet()
    out = {}
    for cp in unicodes:
        gname = cmap.get(cp)
        if not gname:
            continue
        adv = hmtx[gname][0] / upm
        pen = BoundsPen(gs)
        gs[gname].draw(pen)
        if pen.bounds:
            xmin, ymin, xmax, ymax = (v / upm for v in pen.bounds)
        else:                       # blank glyph (e.g. space)
            xmin = ymin = xmax = ymax = 0.0
        out[cp] = (round(adv, 4), round(ymin, 4), round(ymax, 4), round(xmin, 4), round(xmax, 4))
    return out


def _to_otf(ttf):
    """Convert a TrueType (glyf) font to OpenType-CFF (.otf): real cubic charstrings via qu2cu,
    keeping the cmap, horizontal metrics and (renamed) name table. The Noto sources are TrueType,
    so a genuine installable .otf is built here rather than just rewrapping quadratic outlines."""
    go = ttf.getGlyphOrder()
    hmtx = ttf["hmtx"]
    upm = ttf["head"].unitsPerEm
    gs = ttf.getGlyphSet()
    charstrings = {}
    for g in go:
        pen = T2CharStringPen(hmtx[g][0], gs)
        gs[g].draw(Qu2CuPen(pen, max_err=1.0, all_cubic=True))
        charstrings[g] = pen.getCharString()
    fb = FontBuilder(upm, isTTF=False)
    fb.setupGlyphOrder(go)
    cmap = {}
    for t in ttf["cmap"].tables:
        if t.isUnicode():
            cmap.update(t.cmap)
    fb.setupCharacterMap(cmap)
    fb.setupHorizontalMetrics({g: (hmtx[g][0], hmtx[g][1]) for g in go})
    hh = ttf["hhea"]
    fb.setupHorizontalHeader(ascent=hh.ascent, descent=hh.descent, lineGap=hh.lineGap)
    nm = ttf["name"]

    def _n(i, d=""):
        r = nm.getDebugName(i)
        return r or d
    fam = _n(1, "Astro")
    ps = _n(6, fam.replace(" ", "") + "-Regular")
    full = _n(4, fam + " Regular")
    fb.setupNameTable({"familyName": fam, "styleName": _n(2, "Regular"),
                       "uniqueFontIdentifier": _n(3, ps), "fullName": full,
                       "psName": ps, "version": _n(5, "Version 1.000")})
    o = ttf["OS/2"]
    fb.setupOS2(sTypoAscender=o.sTypoAscender, sTypoDescender=o.sTypoDescender,
                sTypoLineGap=o.sTypoLineGap, usWinAscent=o.usWinAscent,
                usWinDescent=o.usWinDescent)
    fb.setupCFF(ps, {"FullName": full}, charstrings, {})
    fb.setupPost()
    return fb.font


def _emit_font_files(font, outdir, family):
    """Write ``family``.{ttf,otf,woff2} for ``font`` into ``outdir`` — installable desktop fonts
    (ttf native, otf/CFF converted) plus the web font. ``font`` must carry glyf outlines.
    Returns total bytes written."""
    outdir.mkdir(parents=True, exist_ok=True)
    otf = _to_otf(font)                          # build CFF from glyf before touching flavors
    total = 0
    for obj, flavor, ext in ((font, None, "ttf"), (font, "woff2", "woff2"), (otf, None, "otf")):
        obj.flavor = flavor
        p = outdir / (family + "." + ext)
        obj.save(p)
        total += p.stat().st_size
    font.flavor = None
    return total


def build_fullset_files():
    """The "turn it up to 11" set: the FULL Noto fonts (renamed) as ttf/otf/woff2 package data.
    Same family names as the astroset subsets, so the SYM_FAMILY/TXT_FAMILY stacks work for either
    set — fullset just makes every Noto glyph (text + all symbols) available."""
    outdir = OUT.parent / "fonts" / "fullset"
    for fam, fn in SYMBOL_SOURCES + [TEXT_SOURCE]:
        font = TTFont(FONTS / fn)
        _apply_glyph_scales(font)
        _rename(font, fam)
        kb = _emit_font_files(font, outdir, fam) // 1024
        print(f"fullset {fam:9} {kb:6} KB (ttf+otf+woff2)  ({fn})")


def sync_out():
    """Mirror the packaged font files into the top-level ``Out/`` folder, grouped by font set
    and format (``Out/astroset/TTF/AstroSym.ttf`` ...), plus the OFL licence. Byte-identical
    copies of ``src/astroglyphs_2K/fonts/*`` — so the repo offers direct downloads without pip.
    Stale files in Out/<fontset>/<FORMAT>/ are removed so the mirror never drifts."""
    import shutil
    pkg_fonts = OUT.parent / "fonts"
    for fs in FONT_SETS:
        for ext in FONT_EXTS:
            dest = DIST_OUT / fs / ext.upper()
            dest.mkdir(parents=True, exist_ok=True)
            srcs = sorted((pkg_fonts / fs).glob("*." + ext))
            keep = {f.name for f in srcs}
            for old in dest.iterdir():
                if old.name not in keep:
                    old.unlink()
            for f in srcs:
                shutil.copyfile(f, dest / f.name)
    shutil.copyfile(HERE.parent / "LICENSES" / "OFL.txt", DIST_OUT / "OFL.txt")
    print(f"synced font files -> {DIST_OUT}")


def main():
    routed = {name: [] for name, _ in SYMBOL_SOURCES}
    src_cmaps = {name: _cmap(TTFont(FONTS / fn)) for name, fn in SYMBOL_SOURCES}
    unresolved = []
    for ch in dict.fromkeys(SYMBOL_CHARS):        # dedupe, keep order
        cp = ord(ch)
        for name, _ in SYMBOL_SOURCES:
            if cp in src_cmaps[name]:
                routed[name].append(cp)
                break
        else:
            unresolved.append(ch)
    if unresolved:
        raise SystemExit("Symbol glyphs missing from all sources: "
                         + " ".join(f"{c!r}(U+{ord(c):04X})" for c in unresolved))

    astro_dir = OUT.parent / "fonts" / "astroset"
    sym_b64, metrics = [], {}
    fe0e = ord(FE0E)
    for name, fn in SYMBOL_SOURCES:
        cps = routed[name] + [fe0e]              # keep FE0E present so it never tofus
        font = _subset_font(FONTS / fn, cps, name)
        metrics.update(_metrics_from_font(font, routed[name]))
        sym_b64.append(_woff2_b64(font))
        _emit_font_files(font, astro_dir, name)   # astroset ttf/otf/woff2 files
        print(f"{name:9} {len(routed[name]):3} glyphs  {len(sym_b64[-1])//1024:4} KB b64")

    txt_cps = [ord(c) for c in dict.fromkeys(TEXT_CHARS)]
    tfont = _subset_font(FONTS / TEXT_SOURCE[1], txt_cps, TEXT_SOURCE[0])
    metrics.update(_metrics_from_font(tfont, txt_cps))
    txt_b64 = _woff2_b64(tfont)
    _emit_font_files(tfont, astro_dir, TEXT_SOURCE[0])
    print(f"{TEXT_SOURCE[0]:9} {len(txt_cps):3} glyphs  {len(txt_b64)//1024:4} KB b64")

    src_versions = {fn: TTFont(FONTS / fn)["name"].getDebugName(5)
                    for _, fn in SYMBOL_SOURCES + [TEXT_SOURCE]}
    ofl = (FONTS / "OFL.txt").read_text(encoding="utf-8").split("-----------------------------------")[0].strip()

    lines = ['"""Generated by tools/build.py — DO NOT EDIT. Subset OFL font data + glyph metrics."""',
             "# fmt: off",
             f"SYMBOL_FAMILY_NAMES = {[n for n, _ in SYMBOL_SOURCES]!r}",
             f"TEXT_FAMILY_NAME = {TEXT_SOURCE[0]!r}",
             "SYMBOLS_WOFF2_B64 = ["]
    for b in sym_b64:
        lines.append(f"    {b!r},")
    lines.append("]")
    lines.append(f"TEXT_WOFF2_B64 = {txt_b64!r}")
    lines.append("# codepoint -> (advance, ymin, ymax, xmin, xmax) as fractions of em (ink bbox)")
    lines.append("GLYPH_METRICS = {")
    for cp in sorted(metrics):
        lines.append(f"    0x{cp:04X}: {metrics[cp]!r},")
    lines.append("}")
    lines.append(f"SOURCE_FONT_VERSIONS = {src_versions!r}")
    lines.append(f"OFL_ATTRIBUTION = {ofl!r}")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT}  ({OUT.stat().st_size//1024} KB)  metrics for {len(metrics)} glyphs")
    print()
    build_fullset_files()
    sync_out()


if __name__ == "__main__":
    import sys
    if "--out-only" in sys.argv[1:]:   # just refresh Out/ from the committed package fonts
        sync_out()
    else:
        main()
