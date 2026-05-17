"""
Animated ALEPH OS CFG — full program corpus.

Parses all .aleph programs, builds a directed dataflow graph where:
  - Nodes = Hebrew letter primes (22) + let-binding names across all programs
  - Edges = dataflow: operand → result, labeled by operation type

Node color by ouroboricity tier:
  O_inf  → gold   (#ffd700)
  O_2d   → indigo (#8a2be2)
  O_2    → cyan   (#00ced1)
  O_1    → amber  (#ffa500)
  O_0    → gray   (#808080)
  binding (computed) → teal (#20b2aa)
  system  → white (#eeeeee)

Edge color by operation:
  tensor   → #f28e2b (orange)
  mediate  → #4e79a7 (blue)
  join     → #59a14f (green)
  meet     → #e15759 (red)
  distance → #b07aa1 (purple)
  palace   → #cc44ff (magenta)
  probe    → #9c9c9c (gray)

Animation:
  Phase 1 — build: nodes appear program by program; cross-program reference
             nodes flash white; O_inf nodes larger.
  Phase 2 — flow wave: Gaussian pulse travels through definition order;
             O_inf hubs pulse gold; cross-program edges light amber.

Output: docs/animated_cfg_aleph.gif
"""

from __future__ import annotations
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx

from aleph_1 import LETTERS, Letter
import aleph_sefirot   # side-effect: registers Sefirot in LETTERS

PROGRAMS_DIR = ROOT / "programs"
OUT = ROOT / "docs" / "animated_cfg_aleph.gif"

BG = "#0a0a15"

_TIER_COLOR = {
    "O_inf":  "#ffd700",
    "O_2d":   "#8a2be2",
    "O_2":    "#00ced1",
    "O_1":    "#ffa500",
    "O_0":    "#606060",
    "binding":"#20b2aa",
    "system": "#eeeeee",
}

_OP_COLOR = {
    "tensor":   "#f28e2b",
    "mediate":  "#4e79a7",
    "join":     "#59a14f",
    "meet":     "#e15759",
    "distance": "#b07aa1",
    "palace":   "#cc44ff",
    "probe":    "#9c9c9c",
    "cast":     "#ffff66",
}

_PULSE_GOLD  = np.array(mcolors.to_rgba("#ffd700"))
_PULSE_WHITE = np.array(mcolors.to_rgba("#ffffff"))


# ──────────────────────────────────────────────────────────────────────────────
# 1.  PARSER — minimal re-impl that builds a graph, not a value
# ──────────────────────────────────────────────────────────────────────────────

# Known letter names (transliterations registered in aleph_1.py)
_LETTER_NAMES: set[str] = {
    k.lower() for k in LETTERS
    if isinstance(k, str) and k.isascii() and k.isalpha()
}

def _node_label(name: str) -> str:
    """Canonical lower-case node label."""
    return name.lower()


def _extract_refs(text: str) -> list[str]:
    """
    Pull all bare identifiers from an expression fragment that are known
    letter names or might be let-binding names (ascii word tokens).
    Excludes keywords: let, palace, mediate, d, tier, probe_Phi etc.
    """
    _KEYWORDS = {
        "let", "palace", "mediate", "system", "census",
        "d", "tier", "match", "probe_phi", "probe_omega",
        "probe_ph", "probe_om", "probe_Phi", "probe_Omega",
    }
    return [
        w.lower() for w in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", text)
        if w.lower() not in _KEYWORDS
    ]


def parse_program(
    source: str,
    program_name: str,
    global_env: set[str],
) -> tuple[
    list[tuple[str, str, str]],   # edges: (src, dst, op)
    list[str],                     # node definition order (first-seen)
    set[str],                      # cross-program references used
]:
    """
    Parse one .aleph program source.

    Returns:
      edges            – directed dataflow edges with operation label
      node_order       – nodes in order of first introduction
      cross_refs       – nodes used here but defined in a prior program
    """
    edges: list[tuple[str, str, str]] = []
    node_order: list[str] = []
    seen_here: set[str] = set()
    cross_refs: set[str] = set()
    local_env: set[str] = set(global_env)

    def _add_node(name: str) -> None:
        if name not in seen_here:
            seen_here.add(name)
            node_order.append(name)
            if name in global_env:
                cross_refs.add(name)

    def _refs_in(text: str) -> list[str]:
        tokens = _extract_refs(text)
        return [t for t in tokens
                if t in _LETTER_NAMES or t in local_env]

    def _op_for_line(line: str) -> str:
        l = line.lower()
        if re.search(r'\btensor\b|⊗|"x"', l):        return "tensor"
        if " x " in l and not re.search(r"\bx\s*=", l): return "tensor"
        if re.search(r"\bmediate\b", l):               return "mediate"
        if re.search(r"\bjoin\b|∨", l):                return "join"
        if re.search(r"\bmeet\b|∧", l):                return "meet"
        if re.search(r"\bd\s*\(", l):                  return "distance"
        if re.search(r"\bpalace\b", l):                 return "palace"
        if re.search(r"\bprobe_", l):                   return "probe"
        if re.search(r"\btier\s*\(", l):               return "probe"
        if re.search(r"::>", l):                       return "cast"
        return "mediate"

    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(":"):      # REPL command — skip
            continue

        # ── let binding ───────────────────────────────────────────────────
        m = re.match(r"let\s+(\w+)\s*=\s*(.+)", line, re.IGNORECASE)
        if m:
            bind_name = _node_label(m.group(1))
            expr_text = m.group(2)
            op = _op_for_line(expr_text)
            _add_node(bind_name)
            local_env.add(bind_name)
            for ref in _refs_in(expr_text):
                r = _node_label(ref)
                _add_node(r)
                if r != bind_name:
                    edges.append((r, bind_name, op))
            continue

        # ── d(a, b) — distance probe ──────────────────────────────────────
        dm = re.match(r"d\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)", line, re.IGNORECASE)
        if dm:
            a, b = _node_label(dm.group(1)), _node_label(dm.group(2))
            if a in _LETTER_NAMES or a in local_env:
                _add_node(a)
            if b in _LETTER_NAMES or b in local_env:
                _add_node(b)
            if (a in seen_here or a in global_env) and (b in seen_here or b in global_env):
                edges.append((a, b, "distance"))
                edges.append((b, a, "distance"))
            continue

        # ── bare tensor (voynich-style: a x b) ───────────────────────────
        xm = re.match(r"(\w+)\s+x\s+(\w+)", line, re.IGNORECASE)
        if xm:
            a, b = _node_label(xm.group(1)), _node_label(xm.group(2))
            _add_node(a); _add_node(b)
            edges.append((a, b, "tensor"))
            continue

        # ── probe_Φ / probe_Ω / tier / palace (standalone) ───────────────
        probe = re.match(r"(probe_\w+|tier|palace\s*\(\d+\))\s*\(?(\w+)\)?", line, re.IGNORECASE)
        if probe:
            op_tag = "probe" if "probe" in probe.group(1).lower() or "tier" in probe.group(1).lower() else "palace"
            arg = _node_label(probe.group(2))
            if arg in _LETTER_NAMES or arg in local_env:
                _add_node(arg)
                edges.append((arg, arg, op_tag))
            continue

    return edges, node_order, cross_refs


def load_all_programs() -> tuple[
    list[tuple[str, list[tuple[str,str,str]], list[str], set[str]]],
    nx.DiGraph,
]:
    """
    Load and parse every .aleph program.

    Returns:
      programs  – [(prog_name, edges, node_order, cross_refs), ...]
      G         – combined directed graph (all edges unioned)
    """
    aleph_files = sorted(PROGRAMS_DIR.glob("*.aleph"))
    programs: list[tuple[str, list, list, set]] = []
    G = nx.DiGraph()
    global_env: set[str] = set(_LETTER_NAMES)

    # Seed base letters
    for name in _LETTER_NAMES:
        letter = LETTERS.get(name) or LETTERS.get(name.capitalize())
        tier = letter.tier if letter else "O_0"
        G.add_node(name, tier=tier, kind="letter")

    for fpath in aleph_files:
        prog_name = fpath.stem
        source = fpath.read_text(encoding="utf-8")
        edges, node_order, cross_refs = parse_program(source, prog_name, global_env)

        for n in node_order:
            if n not in G:
                G.add_node(n, tier="binding", kind="binding")

        for (u, v, op) in edges:
            for n in (u, v):
                if n not in G:
                    G.add_node(n, tier="binding", kind="binding")
            if G.has_edge(u, v):
                G[u][v]["weight"] = G[u][v].get("weight", 1) + 1
            else:
                G.add_edge(u, v, op=op, weight=1)

        global_env.update(n for n in node_order)
        programs.append((prog_name, edges, node_order, cross_refs))
        print(f"  [{prog_name}] {len(node_order)} nodes, {len(edges)} edges, "
              f"{len(cross_refs)} cross-prog refs")

    return programs, G


# ──────────────────────────────────────────────────────────────────────────────
# 2.  RENDER FRAME
# ──────────────────────────────────────────────────────────────────────────────

def render_frame(
    ax: plt.Axes,
    all_nodes: list[str],
    pos: dict,
    edges: list[tuple[str, str, str]],
    base_colors: np.ndarray,
    base_sizes: np.ndarray,
    cross_edges: set[tuple[str, str]],
    revealed: set[str] | None,
    prog_flash: bool,
    pulse_center: int | None,
    pulse_sigma: int,
    N: int,
    title_str: str,
) -> None:
    ax.clear()
    ax.set_facecolor(BG)
    ax.set_axis_off()
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_title(title_str, color="white", fontsize=8, pad=6)

    xs = np.array([pos[n][0] for n in all_nodes])
    ys = np.array([pos[n][1] for n in all_nodes])
    node_idx = {n: i for i, n in enumerate(all_nodes)}

    if revealed is not None:
        # Phase 1: progressive build
        for (u, v, op) in edges:
            if u == v:
                continue
            if u not in revealed or v not in revealed:
                continue
            is_cf = (u, v) in cross_edges
            ec = mcolors.to_rgba(_OP_COLOR.get(op, "#555555"))
            lw = 2.2 if is_cf else 0.9
            al = 0.85 if is_cf else 0.30
            col = "#cc44ff" if is_cf else _OP_COLOR.get(op, "#555555")
            ax.annotate("", xy=(pos[v][0], pos[v][1]), xytext=(pos[u][0], pos[u][1]),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, alpha=al),
                        zorder=1)

        vis_idx = [node_idx[n] for n in all_nodes if n in revealed]
        if not vis_idx:
            return

        colors = base_colors[vis_idx].copy()
        sizes  = base_sizes[vis_idx].copy()

        if prog_flash:
            colors = np.tile(_PULSE_WHITE, (len(vis_idx), 1))
            sizes  = sizes * 2.0

        ax.scatter(xs[vis_idx], ys[vis_idx],
                   c=colors, s=sizes, zorder=3, linewidths=0.5,
                   edgecolors="#ffffff33")

    else:
        # Phase 2: flow wave
        dists   = np.abs(np.arange(N) - pulse_center)
        dists   = np.minimum(dists, N - dists)
        weights = np.exp(-0.5 * (dists / pulse_sigma) ** 2)

        active: set[str] = {all_nodes[i] for i in range(N) if weights[i] > 0.35}

        for (u, v, op) in edges:
            if u == v:
                continue
            is_cf = (u, v) in cross_edges
            near  = u in active or v in active
            col   = ("#ffb347" if (is_cf and near) else
                     "#cc44ff" if is_cf else
                     _OP_COLOR.get(op, "#555555"))
            lw    = 2.5 if (is_cf and near) else (1.6 if is_cf else 0.7)
            al    = 0.90 if (is_cf and near) else (0.55 if is_cf else 0.20)
            ax.annotate("", xy=(pos[v][0], pos[v][1]), xytext=(pos[u][0], pos[u][1]),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, alpha=al),
                        zorder=1)

        blended = np.empty_like(base_colors)
        for i, n in enumerate(all_nodes):
            w = weights[i]
            tier = ax.figure._aleph_tiers[n] if hasattr(ax.figure, "_aleph_tiers") else "O_0"
            target = _PULSE_GOLD if tier == "O_inf" else _PULSE_WHITE
            blended[i] = base_colors[i] * (1 - w) + target * w
        blended = np.clip(blended, 0, 1)
        sizes = base_sizes + base_sizes * 1.8 * weights

        ax.scatter(xs, ys, c=blended, s=sizes, zorder=3,
                   linewidths=0.5, edgecolors="#ffffff22")


def fig_to_pil(fig: plt.Figure, dpi: int) -> Image.Image:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=BG, bbox_inches="tight")
    buf.seek(0)
    return Image.open(buf).copy()


# ──────────────────────────────────────────────────────────────────────────────
# 3.  MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main(
    build_frames: int = 60,
    flow_frames: int  = 100,
    fps: int          = 18,
    dpi: int          = 110,
    figsize: tuple    = (9, 9),
) -> None:
    print("Parsing ALEPH OS programs …")
    programs, G = load_all_programs()

    # Largest weakly-connected component
    wcc = max(nx.weakly_connected_components(G), key=len)
    C = G.subgraph(wcc).copy()
    print(f"  Graph: {C.number_of_nodes()} nodes, {C.number_of_edges()} edges")

    # Node order: base letters first (by aleph-bet order), then bindings in definition order
    def_order: list[str] = []
    seen_order: set[str] = set()
    from aleph_1 import CANONICAL_GLYPHS
    name_by_glyph = {v.glyph: k for k, v in LETTERS.items()
                     if isinstance(k, str) and k.isascii() and k.isalpha() and len(k) > 1}
    # Base letters first in canonical aleph-bet order
    for glyph in CANONICAL_GLYPHS:
        for key, letter in LETTERS.items():
            if letter.glyph == glyph and isinstance(key, str) and key.isascii() and key.isalpha():
                lk = key.lower()
                if lk in C.nodes() and lk not in seen_order:
                    def_order.append(lk)
                    seen_order.add(lk)
                    break
    # Then binding nodes in program definition order
    for (_, _, node_order, _) in programs:
        for n in node_order:
            if n in C.nodes() and n not in seen_order:
                def_order.append(n)
                seen_order.add(n)

    all_nodes = def_order
    N = len(all_nodes)
    print(f"  Node order: {N} nodes")

    # Cross-program edges: edge (u,v) where u and v were introduced by different programs
    prog_of: dict[str, str] = {}
    for (prog_name, _, node_order, _) in programs:
        for n in node_order:
            if n not in prog_of:
                prog_of[n] = prog_name
    for n in all_nodes:
        if n not in prog_of:
            prog_of[n] = "_base"

    cross_edges: set[tuple[str, str]] = set()
    for u, v in C.edges():
        if prog_of.get(u, "_base") != prog_of.get(v, "_base"):
            cross_edges.add((u, v))
    print(f"  Cross-program edges: {len(cross_edges)}")

    # Tier dict for all nodes
    tier_map: dict[str, str] = {}
    for n in all_nodes:
        data = C.nodes[n]
        tier_map[n] = data.get("tier", "binding")

    # Layout
    print(f"  Spring layout ({N} nodes) …")
    pos = nx.spring_layout(C, k=0.12, iterations=400, seed=42)

    # Base colors by tier
    base_colors = np.array([
        mcolors.to_rgba(_TIER_COLOR.get(tier_map[n], "#20b2aa"))
        for n in all_nodes
    ])

    # Base sizes: O_inf large, base letters slightly bigger, bindings medium
    degrees = dict(C.degree())
    max_deg = max(degrees.values()) if degrees else 1
    base_sizes = np.array([
        (80 if tier_map[n] == "O_inf" else
         40 if tier_map[n] in ("O_2", "O_2d") else
         22 if tier_map[n] == "O_1" else
         14) + 40 * (np.log1p(degrees.get(n, 1)) / np.log1p(max_deg)) ** 1.5
        for n in all_nodes
    ])

    # Edges list for rendering
    all_edges: list[tuple[str, str, str]] = []
    for u, v, data in C.edges(data=True):
        all_edges.append((u, v, data.get("op", "mediate")))

    # Program boundary node positions (for flash detection)
    prog_boundary_nodes: list[str] = []
    for (_, _, node_order, cross_refs) in programs:
        if node_order:
            prog_boundary_nodes.append(node_order[0])

    pulse_sigma   = max(8, N // 14)
    pulse_centers = np.linspace(0, N - 1, flow_frames).astype(int)
    total_frames  = build_frames + flow_frames

    print(f"  Rendering {total_frames} frames …")
    fig, ax = plt.subplots(figsize=figsize, facecolor=BG)
    fig._aleph_tiers = tier_map   # pass tier info to render_frame

    frames_pil: list[Image.Image] = []
    n_programs = len(programs)

    for f in range(total_frames):
        print(f"\r  {(f+1)/total_frames*100:5.1f}%  frame {f+1}/{total_frames}", end="", flush=True)

        if f < build_frames:
            frac     = (f + 1) / build_frames
            k        = max(1, int(frac * N))
            revealed = set(all_nodes[:k])
            flash    = any(pb in all_nodes[:k] and all_nodes.index(pb) == k - 1
                           for pb in prog_boundary_nodes)
            prog_idx = sum(1 for (_, _, node_order, _) in programs
                           if any(n in revealed for n in node_order))
            o_inf_count = sum(1 for n in all_nodes[:k] if tier_map[n] == "O_inf")
            title = (
                f"ALEPH OS — full corpus | build {k}/{N} | "
                f"program {min(prog_idx, n_programs)}/{n_programs} | "
                f"{o_inf_count} O_∞ nodes | {len(cross_edges)} cross-prog edges"
            )
            render_frame(
                ax, all_nodes, pos, all_edges,
                base_colors, base_sizes, cross_edges,
                revealed=revealed, prog_flash=flash,
                pulse_center=None, pulse_sigma=pulse_sigma, N=N,
                title_str=title,
            )
        else:
            fi     = f - build_frames
            center = pulse_centers[fi]
            node_at = all_nodes[center]
            title = (
                f"ALEPH OS — full corpus | flow wave | "
                f"node: {node_at} [{tier_map[node_at]}] | "
                f"{len(cross_edges)} cross-prog edges"
            )
            render_frame(
                ax, all_nodes, pos, all_edges,
                base_colors, base_sizes, cross_edges,
                revealed=None, prog_flash=False,
                pulse_center=center, pulse_sigma=pulse_sigma, N=N,
                title_str=title,
            )

        frames_pil.append(fig_to_pil(fig, dpi))

    print()
    plt.close(fig)

    duration_ms = 1000 // fps
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"Assembling GIF → {OUT} …")
    frames_rgb = [fr.convert("RGB") for fr in frames_pil]
    frames_rgb[0].save(
        str(OUT),
        save_all=True,
        append_images=frames_rgb[1:],
        duration=duration_ms,
        loop=0,
        optimize=False,
    )
    sz = OUT.stat().st_size / (1024 * 1024)
    print(f"Done: {OUT}  ({sz:.1f} MB)")

    # Summary
    print(f"\nGraph summary:")
    print(f"  Nodes: {N}  (22 base letters + {N-22} bindings)")
    tier_counts: dict[str, int] = {}
    for n in all_nodes:
        t = tier_map[n]
        tier_counts[t] = tier_counts.get(t, 0) + 1
    for t, c in sorted(tier_counts.items()):
        marker = _TIER_COLOR.get(t, "#999")
        print(f"    {t:8s}: {c:3d} nodes")
    print(f"  Edges: {C.number_of_edges()}  ({len(cross_edges)} cross-program)")
    print(f"  Programs: {len(programs)}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-frames", type=int, default=60)
    ap.add_argument("--flow-frames",  type=int, default=100)
    ap.add_argument("--fps",  type=int, default=18)
    ap.add_argument("--dpi",  type=int, default=110)
    args = ap.parse_args()
    main(
        build_frames=args.build_frames,
        flow_frames=args.flow_frames,
        fps=args.fps,
        dpi=args.dpi,
    )
