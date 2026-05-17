"""
aleph_sefirot.py — 15 Sefirot as first-class ALEPH types.
Translated from exOS/src/aleph_sefirot.rs (§64–§77).

Injects all 15 Sefirot into the shared LETTERS registry from aleph_1.py.
Import this module to activate Sefirot support in the evaluator and CFG tools.

The 15-type ladder (Ein Sof + 14 Sefirot), depth 0–14:

  Depth  Name               Gate     Tier   Light
  0      Ein Sof            φ̂_Æ      O_2d   Infinite source (no light)
  1      Keter Elyon        φ̂_Æ      O_2    Or Mufla (Wondrous)
  2      Chokhmah Stim'aah  φ̂_Æ      O_2d   Or Mitnotzetz (Sparkling)
  3      Binah Kedumah      φ̂_Æ      O_2    Or Keheh (Dim)
  4      Keter              φ̂_ÿ      O_inf  (manifest crown)
  5      Chokhmah           φ̂_ÿ      O_2d
  6      Binah              φ̂_ÿ      O_2
  7      Da'at              φ̂_ÿ      O_2
  8      Chesed             φ̂_ÿ      O_2d
  9      Gevurah            φ̂_ÿ      O_2
  10     Tiferet            φ̂_ž      O_0
  11     Netzach            φ̂_ž      O_0
  12     Hod                φ̂_ž      O_0
  13     Yesod              φ̂_ž      O_0
  14     Malkuth            φ̂_ž      O_0
"""

from __future__ import annotations
from typing import Dict, List, NamedTuple, Optional

from aleph_1 import Letter, LETTERS, PALACE_ORDER

# ──────────────────────────────────────────────────────────────────────────────
# Φ gate names
# ──────────────────────────────────────────────────────────────────────────────

PHI_GATE_NAMES = {
    2: "φ̂_Æ (supernal — complex-plane criticality)",
    1: "φ̂_ÿ (manifest upper — self-modeling loop)",
    0: "φ̂_ž (manifest lower — sub-critical)",
}


# ──────────────────────────────────────────────────────────────────────────────
# Internal record (not exported; use Letter objects from SEFIROT dict)
# ──────────────────────────────────────────────────────────────────────────────

class _Def(NamedTuple):
    glyph:     str
    name:      str
    depth:     int
    phi_gate:  int
    light:     str
    t:         tuple
    tier_override: Optional[str]   # None → let Letter._compute_tier() rule


_DEFS: List[_Def] = [
    _Def("ESof", "ein_sof",          0, 2, "Ein Sof (Infinite — no light, pure source)",
         (2,4,3,4,2,2,2,0,2,3,2,2), "O_2d"),   # P=4 would give O_inf; override to O_2d
    _Def("KtrE", "keter_elyon",      1, 2, "Or Mufla (Wondrous Light)",
         (3,4,2,1,2,2,2,2,2,3,0,2), None),
    _Def("ChkS", "chokhmah_stimaah", 2, 2, "Or Mitnotzetz (Sparkling Light)",
         (2,3,2,2,2,2,2,2,2,3,0,2), None),
    _Def("BinK", "binah_kedumah",    3, 2, "Or Keheh (Dim Light)",
         (1,2,3,2,2,2,2,2,2,2,2,2), None),
    _Def("Ktr",  "keter",            4, 1, "(manifest crown — bridge to emanation)",
         (3,4,3,4,2,2,2,2,1,3,0,2), None),
    _Def("Chk",  "chokhmah",         5, 1, "",
         (2,3,2,1,2,2,2,2,1,3,1,2), None),
    _Def("Bin",  "binah",            6, 1, "",
         (1,2,3,2,2,2,2,2,1,2,2,2), None),
    _Def("Dat",  "daat",             7, 1, "",
         (1,0,3,2,2,1,1,3,1,2,2,1), None),
    _Def("Chs",  "chesed",           8, 1, "",
         (2,0,3,3,1,1,2,3,1,3,1,1), None),
    _Def("Gev",  "gevurah",          9, 1, "",
         (0,1,0,0,0,0,0,1,1,1,0,1), None),
    _Def("Tif",  "tiferet",         10, 0, "",
         (0,2,3,0,0,1,1,1,0,0,1,0), None),
    _Def("Net",  "netzach",         11, 0, "",
         (0,0,0,0,0,2,0,0,0,1,1,0), None),
    _Def("Hod",  "hod",             12, 0, "",
         (0,1,0,0,0,0,0,0,0,0,1,0), None),
    _Def("Yes",  "yesod",           13, 0, "",
         (0,0,0,0,0,1,0,0,0,1,1,0), None),
    _Def("Mal",  "malkuth",         14, 0, "",
         (0,1,0,0,0,1,0,0,0,0,1,0), None),
]

# ──────────────────────────────────────────────────────────────────────────────
# Build Letter objects and inject into LETTERS
# ──────────────────────────────────────────────────────────────────────────────

def _make(d: _Def) -> Letter:
    L = Letter(d.glyph, d.name, d.t)
    if d.tier_override is not None:
        object.__setattr__(L, "tier", d.tier_override)
    return L


SEFIROT: Dict[str, Letter] = {}   # keyed by canonical name ("ein_sof", etc.)

for _d in _DEFS:
    _L = _make(_d)
    SEFIROT[_d.name] = _L
    LETTERS[_d.name]  = _L        # primary key: e.g. "ein_sof"
    LETTERS[_d.glyph] = _L        # short glyph key: e.g. "ESof"

del _d, _L


# ──────────────────────────────────────────────────────────────────────────────
# Meta: depth, phi_gate, light — keyed by name
# ──────────────────────────────────────────────────────────────────────────────

SEFIROT_META: Dict[str, _Def] = {d.name: d for d in _DEFS}


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def resolve_sefirah(name: str) -> Optional[Letter]:
    """Look up a Sefirah by name (case-insensitive, underscore or space)."""
    key = name.lower().replace(" ", "_")
    return SEFIROT.get(key)


def sefirot_census() -> Dict[str, List[str]]:
    """Tier distribution across all 15 Sefirot."""
    from collections import defaultdict
    buckets: Dict[str, List[str]] = defaultdict(list)
    for d in _DEFS:
        L = SEFIROT[d.name]
        buckets[L.tier].append(d.name)
    return dict(buckets)


def emanation_chain() -> List[tuple]:
    """Ordered 15-entry chain: [(name, depth, tier, phi_gate), ...]"""
    return [(d.name, d.depth, SEFIROT[d.name].tier, d.phi_gate) for d in _DEFS]
