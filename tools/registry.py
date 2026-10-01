"""registry.py — the single source of truth for every glyph astroglyphs_2K ships.

Three fonts are built from it (see build.py):

- **Astroglyphs 2K**  — Unicode font. Every glyph at its real codepoint; glyphs Unicode has no
  codepoint for (composed moon phases, Hermetic lots) live in the Private Use Area. ASCII text,
  ℞ ° ′ ″ come from Noto Sans, so one family renders a whole chart label.
- **AstroglyphPi**    — keyboard font, key-for-key compatible with AstrotypeP LT Std (PI_KEYS).
- **AstroglyphPro**   — keyboard font, mnemonic layout (PRO_KEYS). Digits, punctuation and the
  degree marks stay as plain text so ``15a22`` renders as 15♈22 in one font.

Stability rule: once released, a codepoint, PUA slot or key assignment is never reassigned.
New glyphs only take empty slots. Keys map to glyphs by codepoint, so both keyboard fonts can
be converted back to real Unicode text (``astroglyphs_2K.keys_to_unicode``).
"""
from __future__ import annotations

# --- Private Use Area plan (reserved ranges; never renumber) --------------------------------
PUA_ASTRONOMY = 0xE000      # E000–E0FF: astronomy glyphs with no text-style Unicode codepoint
PUA_LOTS = 0xE100           # E100–E1FF: lots, contiguous, Hermetic lots first (Paulus order)

# --- the Unicode inventory: (codepoint, slug, label, category) ------------------------------
SIGN_NAMES = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio",
              "sagittarius", "capricorn", "aquarius", "pisces"]

INVENTORY: list[tuple[int, str, str, str]] = (
    [(0x2648 + i, n, n.title(), "sign") for i, n in enumerate(SIGN_NAMES)]
    + [
        (0x2609, "sun", "Sun", "planet"),
        (0x263D, "moon", "Moon", "planet"),
        (0x263F, "mercury", "Mercury", "planet"),
        (0x2640, "venus", "Venus", "planet"),
        (0x2641, "earth", "Earth", "planet"),
        (0x2642, "mars", "Mars", "planet"),
        (0x2643, "jupiter", "Jupiter", "planet"),
        (0x2644, "saturn", "Saturn", "planet"),
        (0x2645, "uranus", "Uranus", "planet"),
        (0x2646, "neptune", "Neptune", "planet"),
        (0x2647, "pluto", "Pluto", "planet"),
        (0x260A, "north_node", "North Node", "node"),
        (0x260B, "south_node", "South Node", "node"),
        # points & asteroids
        (0x26B7, "chiron", "Chiron", "point"),
        (0x26B8, "black_moon_lilith", "Black Moon Lilith", "point"),
        (0x263E, "asteroid_lilith", "Asteroid / Dark Moon Lilith", "point"),
        (0x26B3, "ceres", "Ceres", "point"),
        (0x26B4, "pallas", "Pallas", "point"),
        (0x26B5, "juno", "Juno", "point"),
        (0x26B6, "vesta", "Vesta", "point"),
        (0x2661, "eros", "Eros (asteroid)", "point"),
        (0x2BF0, "eris", "Eris", "point"),
        (0x2BF2, "sedna", "Sedna", "point"),
        (0x2695, "hygiea", "Hygiea", "point"),
        (0x2BDB, "pholus", "Pholus", "point"),
        # aspects
        (0x260C, "conjunction", "Conjunction (0°)", "aspect"),
        (0x260D, "opposition", "Opposition (180°)", "aspect"),
        (0x25B3, "trine", "Trine (120°)", "aspect"),
        (0x25A1, "square", "Square (90°)", "aspect"),
        (0x26B9, "sextile", "Sextile (60°)", "aspect"),
        (0x26BB, "quincunx", "Quincunx (150°)", "aspect"),
        (0x26BA, "semisextile", "Semisextile (30°)", "aspect"),
        (0x2220, "semisquare", "Semisquare (45°)", "aspect"),
        (0x26BC, "sesquiquadrate", "Sesquiquadrate (135°)", "aspect"),
        (0x2BF5, "quintile", "Quintile (72°)", "aspect"),
        (0x2BF4, "novile", "Novile (40°)", "aspect"),
        (0x2BF3, "vigintile", "Vigintile (18°)", "aspect"),
        # marks
        (0x2726, "fixed_star", "Fixed star", "mark"),
        (0x00B7, "middle_dot", "Middle dot", "mark"),
        # lots (Unicode-encoded forms; PUA block below)
        (0x1F774, "lot_of_fortune", "Lot of Fortune", "lot"),
        (0x29B6, "lot_of_spirit", "Lot of Spirit", "lot"),
        # alternate forms
        (0x2BD3, "pluto_2", "Pluto, form two (circle, crescent, cross)", "alternate"),
        (0x2BD4, "pluto_3", "Pluto, form three", "alternate"),
        (0x2BD5, "pluto_4", "Pluto, form four", "alternate"),
        (0x2BD6, "pluto_5", "Pluto, form five", "alternate"),
        (0x26E2, "uranus_astronomical", "Uranus (astronomical)", "alternate"),
        (0x2BF1, "eris_2", "Eris, form two", "alternate"),
        (0x2BDA, "hygiea_2", "Hygiea, form two", "alternate"),
        (0x2297, "lot_of_fortune_x", "Lot of Fortune (circled times)", "alternate"),
        (0x24C8, "lot_of_spirit_s", "Lot of Spirit (circled S)", "alternate"),
        (0x221F, "semisquare_angle", "Semisquare (right angle form)", "alternate"),
        # astronomy & esoteric glyphs (needed by AstroglyphPi)
        (0x29B5, "circle_horizontal_bar", "Circle with horizontal bar", "astronomy"),
        (0x2296, "circled_minus", "Circled minus", "astronomy"),
        (0x2295, "circled_plus", "Circled plus", "astronomy"),
        (0x25CB, "white_circle", "White circle", "astronomy"),
        (0x25EF, "large_circle", "Large circle", "astronomy"),
        (0x25CF, "black_circle", "Black circle", "astronomy"),
        (0x2B24, "large_black_circle", "Large black circle", "astronomy"),
        (0x25D0, "circle_left_half_black", "Circle, left half black", "astronomy"),
        (0x25D1, "circle_right_half_black", "Circle, right half black", "astronomy"),
        (0x25D2, "circle_lower_half_black", "Circle, lower half black", "astronomy"),
        (0x25D3, "circle_upper_half_black", "Circle, upper half black", "astronomy"),
        (0x25D6, "left_half_black_circle", "Left half black circle", "astronomy"),
        (0x25D7, "right_half_black_circle", "Right half black circle", "astronomy"),
        (0x25E0, "upper_half_circle", "Upper half circle (horned crescent)", "astronomy"),
        (0x25E1, "lower_half_circle", "Lower half circle (horned crescent)", "astronomy"),
        (0x25BD, "down_triangle", "White down-pointing triangle", "astronomy"),
        (0x26E4, "pentagram", "Pentagram", "esoteric"),
        (0x2721, "hexagram", "Hexagram", "esoteric"),
        (0x1F701, "air", "Air (alchemical)", "esoteric"),
        (0x1F703, "earth_element", "Earth (alchemical)", "esoteric"),
        (0x1F70D, "sulfur", "Sulfur (alchemical)", "esoteric"),
        (0x25A9, "gateway", "Gateway", "esoteric"),
    ]
)

# --- glyphs Unicode has no codepoint for: composed in build.py -------------------------------
# moon phases (AstrotypeP B, C, M, Y). ("moon", dark_side, kind):
#   kind "gibbous"  = white disc with a dark crescent on dark_side
#   kind "crescent" = dark disc with a white crescent opposite dark_side
COMPOSED: dict[int, tuple[str, str, str, tuple]] = {
    PUA_ASTRONOMY + 1: ("moon_gibbous_dark_left", "Moon: white disc, dark crescent left",
                        "astronomy", ("moon", "left", "gibbous")),
    PUA_ASTRONOMY + 2: ("moon_gibbous_dark_right", "Moon: white disc, dark crescent right",
                        "astronomy", ("moon", "right", "gibbous")),
    PUA_ASTRONOMY + 3: ("moon_crescent_lit_right", "Moon: dark disc, white crescent right",
                        "astronomy", ("moon", "left", "crescent")),
    PUA_ASTRONOMY + 4: ("moon_crescent_lit_left", "Moon: dark disc, white crescent left",
                        "astronomy", ("moon", "right", "crescent")),
}

# The lots block: Hermetic lots in Paulus order. ("alias", cp) reuses an existing glyph;
# ("lot", planet_cp) composes the planet with a small Lot-of-Fortune index at lower right.
HERMETIC_LOTS = [
    ("lot_of_fortune", "Lot of Fortune", ("alias", 0x1F774), ["lot of the moon"]),
    ("lot_of_spirit", "Lot of Spirit", ("alias", 0x29B6), ["lot of the sun", "lot of the daimon",
                                                           "lot of genius"]),
    ("lot_of_eros", "Lot of Eros", ("lot", 0x2640), ["lot of venus", "lot of love"]),
    ("lot_of_necessity", "Lot of Necessity", ("lot", 0x263F), ["lot of mercury"]),
    ("lot_of_courage", "Lot of Courage", ("lot", 0x2642), ["lot of mars", "lot of daring"]),
    ("lot_of_victory", "Lot of Victory", ("lot", 0x2643), ["lot of jupiter"]),
    ("lot_of_nemesis", "Lot of Nemesis", ("lot", 0x2644), ["lot of saturn"]),
]
for _i, (_slug, _label, _how, _aliases) in enumerate(HERMETIC_LOTS):
    COMPOSED[PUA_LOTS + _i] = (_slug + "_pua" if _how[0] == "alias" else _slug, _label, "lot", _how)

# Alternate forms, default first. Renderers pick by name (e.g. ephemvis glyph_style).
ALTERNATES: dict[str, list[int]] = {
    "pluto": [0x2647, 0x2BD3, 0x2BD4, 0x2BD5, 0x2BD6],
    "uranus": [0x2645, 0x26E2],
    "eris": [0x2BF0, 0x2BF1],
    "hygiea": [0x2695, 0x2BDA],
    "lot_of_fortune": [0x1F774, 0x2297],
    "lot_of_spirit": [0x29B6, 0x24C8],
    "semisquare": [0x2220, 0x221F],
}

# --- keyboard layouts: (key, codepoint, identity, status, note) ------------------------------
# status: match = confident; check = likely match, still to confirm against AstrotypeP.
_LOT_KEYS = [
    ("È", 0x1F774, "Lot of Fortune (Moon)", "match", "Also at S in Pro"),
    ("É", 0x29B6, "Lot of Spirit (Sun)", "match", "Circle with vertical bar; alternate: circled S"),
    ("Ê", PUA_LOTS + 2, "Lot of Eros (Venus)", "match", "Composed: Venus with a lot index"),
    ("Ë", PUA_LOTS + 3, "Lot of Necessity (Mercury)", "match", "Composed: Mercury with a lot index"),
    ("Ì", PUA_LOTS + 4, "Lot of Courage (Mars)", "match", "Composed: Mars with a lot index"),
    ("Í", PUA_LOTS + 5, "Lot of Victory (Jupiter)", "match", "Composed: Jupiter with a lot index"),
    ("Î", PUA_LOTS + 6, "Lot of Nemesis (Saturn)", "match", "Composed: Saturn with a lot index"),
]

PI_KEYS: list[tuple[str, int, str, str, str]] = [
    # digits: the planets in order from the Sun
    ("0", 0x29B5, "Circle with horizontal bar", "check", "Meaning unconfirmed"),
    ("1", 0x2609, "Sun", "match", ""),
    ("2", 0x263F, "Mercury", "match", ""),
    ("3", 0x2640, "Venus", "match", ""),
    ("4", 0x2641, "Earth", "match", ""),
    ("5", 0x2642, "Mars", "match", ""),
    ("6", 0x2643, "Jupiter", "match", ""),
    ("7", 0x2644, "Saturn", "match", ""),
    ("8", 0x26E2, "Uranus (astronomical)", "match", "Alternate of a"),
    ("9", 0x2646, "Neptune", "match", ""),
    ("A", 0x2652, "Aquarius", "match", ""),
    ("B", PUA_ASTRONOMY + 1, "Moon: white disc, dark crescent left", "match", "Composed"),
    ("C", PUA_ASTRONOMY + 2, "Moon: white disc, dark crescent right", "match", "Composed"),
    ("D", 0x2649, "Taurus", "check", "Taurus also at W"),
    ("E", 0x264A, "Gemini", "match", ""),
    ("F", 0x260B, "South Node (calligraphic form)", "check", "Standard South Node is on t"),
    ("G", 0x264D, "Virgo (alternate form)", "match", "Renders the standard Virgo in v1"),
    ("H", 0x25A9, "Gateway", "check", "U+25A9 is the shape stand-in"),
    ("I", 0x264F, "Scorpio", "match", ""),
    ("J", 0x25CB, "White circle", "check", "Full moon?"),
    ("K", 0x2296, "Circle with bar inside", "check", ""),
    ("L", 0x2295, "Circled plus", "check", ""),
    ("M", PUA_ASTRONOMY + 3, "Moon: dark disc, white crescent right", "match", "Composed"),
    ("N", 0x25D0, "Moon: left half dark", "match", ""),
    ("O", 0x2650, "Sagittarius", "match", ""),
    ("P", 0x2651, "Capricorn", "match", ""),
    ("Q", 0x2648, "Aries", "match", ""),
    ("R", 0x264B, "Cancer", "match", ""),
    ("S", 0x2653, "Pisces", "match", ""),
    ("T", 0x264C, "Leo", "match", ""),
    ("U", 0x264E, "Libra", "match", ""),
    ("V", 0x25EF, "Large white circle", "check", ""),
    ("W", 0x2649, "Taurus (second form)", "check", "See D"),
    ("X", 0x25D1, "Moon: right half dark", "match", ""),
    ("Y", PUA_ASTRONOMY + 4, "Moon: dark disc, white crescent left", "match", "Composed"),
    ("Z", 0x264D, "Virgo", "match", ""),
    ("a", 0x2645, "Uranus (astrological)", "match", "Alternate of 8"),
    ("b", 0x25CF, "Black disc", "check", "b, c, v are all black discs"),
    ("c", 0x25CF, "Black disc (second form)", "check", "See b"),
    ("d", 0x26B5, "Juno", "check", ""),
    ("e", 0x211E, "Retrograde", "match", ""),
    ("f", 0x26B3, "Ceres", "check", ""),
    ("g", 0x25B3, "Trine", "match", ""),
    ("h", 0x25BD, "Down triangle", "check", ""),
    ("i", 0x2650, "Sagittarius (alternate form)", "match", "Renders the standard Sagittarius in v1"),
    ("j", 0x1F701, "Air (alchemical)", "check", ""),
    ("k", 0x1F703, "Earth (alchemical)", "check", ""),
    ("l", 0x2721, "Hexagram", "match", ""),
    ("m", 0x263D, "Crescent moon (waxing)", "match", ""),
    ("n", 0x25D7, "Right half black circle", "match", ""),
    ("o", 0x26BA, "Semisextile", "match", ""),
    ("p", 0x26BB, "Quincunx", "match", ""),
    ("q", 0x260C, "Conjunction", "match", ""),
    ("r", 0x260A, "North Node", "match", ""),
    ("s", 0x1F70D, "Sulfur (alchemical)", "check", ""),
    ("t", 0x260B, "South Node", "match", ""),
    ("u", 0x221F, "Semisquare (right angle form)", "check", ""),
    ("v", 0x2B24, "Large black circle", "check", "See b"),
    ("w", 0x260D, "Opposition", "match", ""),
    ("x", 0x25D6, "Left half black circle", "match", ""),
    ("y", 0x263E, "Crescent moon (waning)", "check", "Same as >?"),
    ("z", 0x25A1, "Square", "match", ""),
    ("!", 0x26B9, "Sextile", "match", ""),
    (",", 0x25E0, "Moon crescent (horned)", "check", "Shape stand-in"),
    (".", 0x25E1, "Moon crescent (horned, opposite)", "check", "Shape stand-in"),
    (":", 0x25D2, "Circle, lower half black", "match", ""),
    (";", 0x25D3, "Circle, upper half black", "match", ""),
    ("<", 0x2646, "Neptune (alternate form)", "match", "Renders the standard Neptune in v1"),
    (">", 0x263E, "Crescent moon (waning)", "check", "See y"),
    ("?", 0x26E4, "Pentagram", "match", ""),
] + _LOT_KEYS

PRO_KEYS: list[tuple[str, int, str, str, str]] = (
    [(chr(ord("a") + i), 0x2648 + i, n.title(), "match", "") for i, n in enumerate(SIGN_NAMES)]
    + [(k, cp, n, "match", "") for k, cp, n in [
        ("A", 0x2609, "Sun"), ("B", 0x263D, "Moon"), ("C", 0x263F, "Mercury"),
        ("D", 0x2640, "Venus"), ("E", 0x2642, "Mars"), ("F", 0x2643, "Jupiter"),
        ("G", 0x2644, "Saturn"), ("H", 0x2645, "Uranus"), ("I", 0x2646, "Neptune"),
        ("J", 0x2647, "Pluto"), ("K", 0x260A, "North Node"), ("L", 0x260B, "South Node"),
        ("M", 0x26B7, "Chiron"), ("N", 0x26B8, "Black Moon Lilith"), ("O", 0x26B3, "Ceres"),
        ("P", 0x26B4, "Pallas"), ("Q", 0x26B5, "Juno"), ("R", 0x26B6, "Vesta"),
        ("S", 0x1F774, "Lot of Fortune"), ("T", 0x2641, "Earth"), ("U", 0x2BF0, "Eris"),
        ("V", 0x2BF2, "Sedna"), ("W", 0x2BDA, "Hygiea"), ("X", 0x2661, "Eros (asteroid)"),
        ("Y", 0x2BDB, "Pholus"), ("Z", 0x211E, "Retrograde"),
        ("m", 0x260C, "Conjunction"), ("n", 0x260D, "Opposition"), ("o", 0x25B3, "Trine"),
        ("p", 0x25A1, "Square"), ("q", 0x26B9, "Sextile"), ("r", 0x26BB, "Quincunx"),
        ("s", 0x26BA, "Semisextile"), ("t", 0x2220, "Semisquare"),
        ("u", 0x26BC, "Sesquiquadrate"), ("v", 0x2BF5, "Quintile"), ("w", 0x2BF4, "Novile"),
        ("x", 0x2BF3, "Vigintile"), ("y", 0x2726, "Fixed star"),
        ("z", 0x2297, "Lot of Fortune (circled times)"),
        ("À", 0x2BD3, "Pluto, form two"), ("Á", 0x2BD4, "Pluto, form three"),
        ("Â", 0x2BD5, "Pluto, form four"), ("Ã", 0x2BD6, "Pluto, form five"),
        ("Ä", 0x26E2, "Uranus (astronomical)"), ("Å", 0x2BF1, "Eris, form two"),
        ("Æ", 0x263E, "Asteroid Lilith"),
    ]]
    + _LOT_KEYS
)

# Plain-text characters every Unicode/Pro font carries (from Noto Sans).
TEXT_CHARS = "".join(chr(c) for c in range(0x20, 0x7F)) + "℞°′″· "
# Characters that stay plain text in AstroglyphPro (everything ASCII that isn't a letter).
PRO_TEXT_CHARS = "".join(c for c in TEXT_CHARS if not c.isalpha() or c in "℞")
