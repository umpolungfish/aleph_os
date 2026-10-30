"""
Per-program animated CFG GIFs for the ALEPH OS program corpus.

For each .aleph file, builds a directed dataflow graph (nodes = bound names
+ primitive letters; edges = dataflow by operation type) and renders a two-phase
animated GIF:

  Phase 1 — build: nodes appear in first-mention order; edges flash on first
             appearance; cross-origin nodes (Hebrew letter primitives) pulse gold.
  Phase 2 — flow: Gaussian pulse travels through the node order; operation edges
             light up by type; O_∞ / O_2d nodes pulse brightest.

Output directory: docs/programs/<name>.gif
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

from aleph_1 import LETTERS, PALACE_ORDER
import aleph_sefirot   # side-effect: registers Sefirot in LETTERS

PROGRAMS_DIR = ROOT / "programs"
OUT_DIR      = ROOT / "docs" / "programs"
BG           = "#0a0a15"

# ── color maps ────────────────────────────────────────────────────────────────

_TIER_COLOR = {
    "O_∞":  "#ffd700",
    "O_2d":   "#8a2be2",
    "O₂":    "#00ced1",
    "O₁":    "#ffa500",
    "O₀":    "#606060",
    "binding":"#20b2aa",
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

# All known letter / sefirot names for reference detection
_LETTER_NAMES: set[str] = {
    k.lower() for k in LETTERS
    if isinstance(k, str) and (k.replace("_", "").isalpha())
    and len(k) > 1
}

# ── parser ────────────────────────────────────────────────────────────────────

_KEYWORDS = {
    "let", "palace", "mediate", "system", "census", "d", "tier",
    "match", "probe_phi", "probe_omega", "probe_ph", "probe_om",
    "probe_phi", "probe_omega", "o_inf", "o_2d", "o_2", "o_1", "o_0",
}


def _extract_refs(text: str) -> list[str]:
    return [
        w.lower() for w in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", text)
        if w.lower() not in _KEYWORDS
    ]


def _op_for_line(line: str) -> str:
    l = line.lower()
    if re.search(r"\btensor\b|⊗", l):          return "tensor"
    if " x " in l:                              return "tensor"
    if re.search(r"\bmediate\b", l):            return "mediate"
    if re.search(r"\bjoin\b|∨", l):             return "join"
    if re.search(r"\bmeet\b|∧", l):             return "meet"
    if re.search(r"\bd\s*\(", l):               return "distance"
    if re.search(r"\bpalace\b", l):             return "palace"
    if re.search(r"\bprobe_", l):               return "probe"
    if re.search(r"\btier\s*\(", l):            return "probe"
    if re.search(r"::>", l):                    return "cast"
    return "mediate"


def parse_program(source: str) -> tuple[
    list[tuple[str, str, str]],   # edges (src, dst, op)
    list[str],                     # node_order (first-seen)
    set[str],                      # letter_nodes (primitive references)
]:
    edges: list[tuple[str, str, str]] = []
    node_order: list[str] = []
    seen: set[str] = set()
    local_env: set[str] = set()
    letter_nodes: set[str] = set()

    def _add(name: str) -> None:
        if name not in seen:
            seen.add(name)
            node_order.append(name)
        if name in _LETTER_NAMES:
            letter_nodes.add(name)

    def _refs(text: str) -> list[str]:
        return [t for t in _extract_refs(text)
                if t in _LETTER_NAMES or t in local_env]

    for raw in source.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(":"):
            continue

        # let binding
        m = re.match(r"let\s+(\w+)\s*=\s*(.+)", line, re.IGNORECASE)
        if m:
            bind = m.group(1).lower()
            expr = m.group(2)
            op   = _op_for_line(expr)
            _add(bind)
            local_env.add(bind)
            for ref in _refs(expr):
                r = ref.lower()
                _add(r)
                if r != bind:
                    edges.append((r, bind, op))
            continue

        # d(a, b)
        dm = re.match(r"d\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)", line, re.IGNORECASE)
        if dm:
            a, b = dm.group(1).lower(), dm.group(2).lower()
            if a in _LETTER_NAMES or a in local_env:
                _add(a)
            if b in _LETTER_NAMES or b in local_env:
                _add(b)
            if a in seen and b in seen:
                edges.append((a, b, "distance"))
            continue

        # bare tensor: a x b
        xm = re.match(r"(\w+)\s+x\s+(\w+)", line, re.IGNORECASE)
        if xm:
            a, b = xm.group(1).lower(), xm.group(2).lower()
            _add(a); _add(b)
            edges.append((a, b, "tensor"))
            continue

        # standalone probes / tier / palace
        pm = re.match(
            r"(probe_\w+|tier|palace\s*\(\d+\))\s*\(?\s*(\w+)\s*\)?",
            line, re.IGNORECASE
        )
        if pm:
            kind = "probe" if re.search(r"probe|tier", pm.group(1).lower()) else "palace"
            arg  = pm.group(2).lower()
            if arg in _LETTER_NAMES or arg in local_env:
                _add(arg)
                edges.append((arg, arg, kind))
            continue

    return edges, node_order, letter_nodes


# ── rendering ─────────────────────────────────────────────────────────────────

def _node_color(name: str, letter_nodes: set[str]) -> str:
    L = LETTERS.get(name) or LETTERS.get(name.lower())
    if L:
        return _TIER_COLOR.get(L.tier, "#20b2aa")
    return _TIER_COLOR["binding"]


def _node_size(name: str, degree: int) -> float:
    base = 120 if name in _LETTER_NAMES else 80
    return base + 60 * (np.log1p(degree) / np.log1p(10))


def render_frame(
    ax: plt.Axes,
    all_nodes: list[str],
    pos: dict,
    edges: list[tuple[str, str, str]],
    letter_nodes: set[str],
    base_colors: np.ndarray,
    base_sizes: np.ndarray,
    revealed: set[str] | None,
    pulse_center: int | None,
    pulse_sigma: int,
    N: int,
    title: str,
) -> None:
    ax.clear()
    ax.set_facecolor(BG)
    ax.set_axis_off()
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_title(title, color="white", fontsize=7.5, pad=6)

    nidx = {n: i for i, n in enumerate(all_nodes)}
    xs   = np.array([pos[n][0] for n in all_nodes])
    ys   = np.array([pos[n][1] for n in all_nodes])

    if revealed is not None:
        # Phase 1: build
        vis = [nidx[n] for n in all_nodes if n in revealed]
        for u, v, op in edges:
            if u not in revealed or v not in revealed:
                continue
            col = _OP_COLOR.get(op, "#4e79a7")
            lw  = 2.5 if op == "tensor" else (2.0 if op == "mediate" else 1.2)
            al  = 0.85 if op in ("tensor", "mediate") else 0.55
            ax.annotate("", xy=(pos[v][0], pos[v][1]), xytext=(pos[u][0], pos[u][1]),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, alpha=al),
                        zorder=1)
        if not vis:
            return
        colors = base_colors[vis].copy()
        sizes  = base_sizes[vis].copy()
        ax.scatter(xs[vis], ys[vis], c=colors, s=sizes,
                   zorder=3, linewidths=0.5, edgecolors="#ffffff33")
        for n in all_nodes:
            if n in revealed:
                ax.text(pos[n][0], pos[n][1], n, ha="center", va="center",
                        fontsize=4.5, color="#ffffff", fontweight="bold", zorder=4)

    else:
        # Phase 2: flow wave
        dists   = np.abs(np.arange(N) - pulse_center)
        dists   = np.minimum(dists, N - dists)
        weights = np.exp(-0.5 * (dists / pulse_sigma) ** 2)
        active  = {all_nodes[i] for i in range(N) if weights[i] > 0.3}

        for u, v, op in edges:
            near = u in active or v in active
            col  = _OP_COLOR.get(op, "#4e79a7")
            lw   = 2.5 if near else 0.8
            al   = 0.85 if near else 0.20
            ax.annotate("", xy=(pos[v][0], pos[v][1]), xytext=(pos[u][0], pos[u][1]),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, alpha=al),
                        zorder=1)

        blended = np.empty_like(base_colors)
        for i, n in enumerate(all_nodes):
            w = weights[i]
            target = _PULSE_GOLD if n in letter_nodes else _PULSE_WHITE
            blended[i] = np.clip(base_colors[i] * (1 - w) + target * w, 0, 1)
        sizes = base_sizes + base_sizes * 1.5 * weights

        ax.scatter(xs, ys, c=blended, s=sizes, zorder=3,
                   linewidths=0.5, edgecolors="#ffffff22")
        for n in all_nodes:
            ax.text(pos[n][0], pos[n][1], n, ha="center", va="center",
                    fontsize=4.5, color="#ffffff", fontweight="bold", zorder=4)


def fig_to_pil(fig, dpi):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=BG, bbox_inches="tight")
    buf.seek(0)
    return Image.open(buf).copy()


# ── per-program GIF ───────────────────────────────────────────────────────────

def generate_gif(
    fpath: Path,
    build_frames: int = 40,
    flow_frames:  int = 60,
    fps:          int = 12,
    dpi:          int = 100,
) -> None:
    prog_name = fpath.stem
    source    = fpath.read_text(encoding="utf-8")
    edges, node_order, letter_nodes = parse_program(source)

    if len(node_order) < 2:
        print(f"  [{prog_name}] too few nodes ({len(node_order)}), skipping")
        return

    G = nx.DiGraph()
    for n in node_order:
        G.add_node(n)
    for u, v, op in edges:
        for x in (u, v):
            if x not in G:
                G.add_node(x)
        if u != v:
            G.add_edge(u, v, op=op)

    if G.number_of_nodes() == 0:
        print(f"  [{prog_name}] empty graph, skipping")
        return

    # layout: spring for small graphs, shell for tiny
    N = len(node_order)
    if N <= 5:
        pos = nx.circular_layout(G)
    elif N <= 15:
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.spring_layout(G, k=0.5, iterations=200, seed=42)

    # ensure all nodes have positions
    for n in node_order:
        if n not in pos:
            pos[n] = (0.0, 0.0)

    degrees = dict(G.degree())
    all_nodes = node_order[:]   # nodes in first-seen order

    base_colors = np.array([
        mcolors.to_rgba(_node_color(n, letter_nodes)) for n in all_nodes
    ])
    base_sizes = np.array([
        _node_size(n, degrees.get(n, 0)) for n in all_nodes
    ])

    pulse_sigma   = max(2, N // 5)
    pulse_centers = np.linspace(0, N - 1, flow_frames).astype(int)
    total_frames  = build_frames + flow_frames

    edge_list = [(u, v, op) for u, v, op in edges if u in G and v in G]

    print(f"  [{prog_name}]  {N} nodes  {len(edge_list)} edges  "
          f"{len(letter_nodes)} primitives  → {total_frames} frames")

    fig, ax = plt.subplots(figsize=(8, 8), facecolor=BG)
    frames_pil = []

    for f in range(total_frames):
        if f < build_frames:
            k        = max(1, int((f + 1) / build_frames * N))
            revealed = set(all_nodes[:k])
            cur      = all_nodes[k - 1]
            is_prim  = cur in letter_nodes
            title    = (
                f"{prog_name} | {'primitive: ' if is_prim else 'binding: '}{cur} | "
                f"{len(edge_list)} dataflow edges"
            )
            render_frame(ax, all_nodes, pos, edge_list, letter_nodes,
                         base_colors, base_sizes, revealed,
                         None, pulse_sigma, N, title)
        else:
            fi     = f - build_frames
            center = pulse_centers[fi]
            cur    = all_nodes[center]
            title  = f"{prog_name} | wave: {cur} | μ∘δ = id"
            render_frame(ax, all_nodes, pos, edge_list, letter_nodes,
                         base_colors, base_sizes, None,
                         center, pulse_sigma, N, title)

        frames_pil.append(fig_to_pil(fig, dpi))

    plt.close(fig)

    out = OUT_DIR / f"{prog_name}.gif"
    frames_rgb = [fr.convert("RGB") for fr in frames_pil]
    frames_rgb[0].save(
        str(out), save_all=True, append_images=frames_rgb[1:],
        duration=1000 // fps, loop=0, optimize=False,
    )
    size_kb = out.stat().st_size // 1024
    print(f"    → {out.name}  ({size_kb} KB)")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    aleph_files = sorted(PROGRAMS_DIR.glob("*.aleph"))
    print(f"Generating per-program CFG GIFs for {len(aleph_files)} programs …\n")
    for fpath in aleph_files:
        generate_gif(fpath)
    print(f"\nDone. Output: {OUT_DIR}")


if __name__ == "__main__":
    main()
