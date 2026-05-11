"""
visualization.py — CSE112 Project
Matplotlib-based visualizations for the Cairo transportation system.

Generates four figures:
  1. Full network map (existing + potential roads)
  2. MST overlay
  3. Shortest path highlight (Dijkstra / A*)
  4. Traffic congestion heat-map
"""

import matplotlib
matplotlib.use("Agg")      # headless backend for file export
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import math

from core.data import NODES, EXISTING_ROADS, POTENTIAL_ROADS, TRAFFIC_FLOW, CRITICAL_NODES
from core.graph import build_cairo_graph
from algorithms.mst import kruskal_mst
from algorithms.shortest_path import shortest_path, astar, congested_roads


# ─────────────────────────────────────────────────────────────
# Colours
# ─────────────────────────────────────────────────────────────
TYPE_COLOR = {
    "Residential": "#4CAF50",
    "Mixed":       "#2196F3",
    "Business":    "#FF9800",
    "Industrial":  "#9E9E9E",
    "Government":  "#9C27B0",
    "Airport":     "#F44336",
    "Transit Hub": "#00BCD4",
    "Education":   "#FFEB3B",
    "Tourism":     "#FF5722",
    "Sports":      "#3F51B5",
    "Medical":     "#E91E63",
    "Commercial":  "#795548",
}

def _pos(nid):
    n = NODES[nid]
    return n["x"], n["y"]

def _label(nid):
    name = NODES[nid]["name"]
    # Shorten long names
    subs = {
        "New Administrative Capital": "NAC",
        "Cairo Int'l Airport":        "Airport",
        "Ramses Railway Station":     "Ramses",
        "Cairo University":           "Cairo Uni.",
        "Al-Azhar University":        "Al-Azhar",
        "Egyptian Museum":            "Museum",
        "Cairo Int'l Stadium":        "Stadium",
        "Smart Village":              "Smart V.",
        "Cairo Festival City":        "Festival",
        "Qasr El Aini Hospital":      "Qasr Hosp.",
        "Maadi Military Hospital":    "Maadi Hosp.",
        "6th October City":           "6th Oct.",
    }
    return subs.get(name, name)


def _draw_edges(ax, edges, color="#BDBDBD", lw=0.8, alpha=0.5, style="-"):
    for (u, v, *_) in edges:
        xu, yu = _pos(u)
        xv, yv = _pos(v)
        ax.plot([xu, xv], [yu, yv], color=color,
                linewidth=lw, alpha=alpha, linestyle=style, zorder=1)


def _draw_nodes(ax, nodes=None, size=80):
    if nodes is None:
        nodes = list(NODES.keys())
    for nid in nodes:
        x, y = _pos(nid)
        ntype = NODES[nid]["type"]
        c     = TYPE_COLOR.get(ntype, "#607D8B")
        ax.scatter(x, y, s=size, c=c, zorder=3, edgecolors="#333", linewidths=0.4)
        ax.annotate(_label(nid), (x, y), textcoords="offset points",
                    xytext=(3, 3), fontsize=5.5, zorder=4,
                    fontfamily="monospace")


def _legend_patches(ax):
    patches = [mpatches.Patch(color=c, label=t) for t, c in TYPE_COLOR.items()]
    ax.legend(handles=patches, loc="lower left", fontsize=5.5,
              ncol=2, framealpha=0.8, title="Node type", title_fontsize=6)


# ─────────────────────────────────────────────────────────────
# Figure 1 — Full network
# ─────────────────────────────────────────────────────────────
def plot_full_network(out_path="fig1_network.png"):
    fig, ax = plt.subplots(figsize=(11, 8), dpi=150)
    ax.set_facecolor("#F5F5F5")
    fig.patch.set_facecolor("#ECEFF1")

    existing  = [(u, v) for u,v,*_ in EXISTING_ROADS]
    potential = [(u, v) for u,v,*_ in POTENTIAL_ROADS]

    _draw_edges(ax, [(u, v, None) for u,v in potential],
                color="#B0BEC5", lw=0.6, alpha=0.4, style="--")
    _draw_edges(ax, [(u, v, None) for u,v in existing],
                color="#546E7A", lw=1.2, alpha=0.7)

    _draw_nodes(ax, size=90)
    _legend_patches(ax)

    ax.set_title("Greater Cairo Transportation Network\n"
                 "Solid = existing roads  |  Dashed = potential new roads",
                 fontsize=10, fontweight="bold")
    ax.set_xlabel("Longitude", fontsize=8)
    ax.set_ylabel("Latitude", fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out_path}")


# ─────────────────────────────────────────────────────────────
# Figure 2 — MST overlay
# ─────────────────────────────────────────────────────────────
def plot_mst(out_path="fig2_mst.png"):
    g = build_cairo_graph(include_potential=True)
    mst, cost, dist = kruskal_mst(g)

    fig, ax = plt.subplots(figsize=(11, 8), dpi=150)
    ax.set_facecolor("#F5F5F5")
    fig.patch.set_facecolor("#ECEFF1")

    # Background: all existing edges (faint)
    _draw_edges(ax, [(u, v, None) for u,v,*_ in EXISTING_ROADS],
                color="#CFD8DC", lw=0.6, alpha=0.4)

    # MST edges
    for (u, v, attr, w) in mst:
        xu, yu = _pos(u)
        xv, yv = _pos(v)
        color = "#E53935" if attr.get("is_new") else "#1565C0"
        lw    = 2.0 if attr.get("is_new") else 1.6
        ax.plot([xu, xv], [yu, yv], color=color, linewidth=lw,
                alpha=0.85, zorder=2)

    _draw_nodes(ax, size=90)

    # Legend
    blue_line = mpatches.Patch(color="#1565C0", label="MST: existing road")
    red_line  = mpatches.Patch(color="#E53935", label="MST: new road to build")
    ax.legend(handles=[blue_line, red_line], loc="lower left",
              fontsize=7, framealpha=0.85)

    ax.set_title(
        f"Kruskal's MST — Infrastructure Network\n"
        f"Total dist: {dist:.0f} km  |  New construction cost: {cost:,.0f} M EGP",
        fontsize=10, fontweight="bold"
    )
    ax.set_xlabel("Longitude", fontsize=8)
    ax.set_ylabel("Latitude", fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out_path}")


# ─────────────────────────────────────────────────────────────
# Figure 3 — Shortest paths (Dijkstra + A*)
# ─────────────────────────────────────────────────────────────
def plot_shortest_paths(out_path="fig3_paths.png"):
    g = build_cairo_graph(include_potential=False)

    # Dijkstra: New Cairo → Downtown
    d_dist, d_path = shortest_path(g, 4, 3)
    # A*: Giza → Qasr El Aini Hospital
    a_time, a_path = astar(g, 8, "F9")

    fig, axes = plt.subplots(1, 2, figsize=(15, 7), dpi=130)
    fig.patch.set_facecolor("#ECEFF1")

    for ax, path, title, color in [
        (axes[0], d_path,
         f"Dijkstra: New Cairo → Downtown Cairo\nShortest distance: {d_dist:.1f} km",
         "#1565C0"),
        (axes[1], a_path,
         f"A*: Giza → Qasr El Aini Hospital\nETA (80 km/h): {a_time:.1f} min",
         "#B71C1C"),
    ]:
        ax.set_facecolor("#F5F5F5")
        _draw_edges(ax, [(u, v, None) for u,v,*_ in EXISTING_ROADS],
                    color="#CFD8DC", lw=0.7, alpha=0.4)
        _draw_nodes(ax, size=70)

        # Highlight path
        if len(path) >= 2:
            for i in range(len(path) - 1):
                xu, yu = _pos(path[i])
                xv, yv = _pos(path[i+1])
                ax.plot([xu, xv], [yu, yv], color=color,
                        linewidth=3.0, alpha=0.9, zorder=5)
            # Start / end markers
            ax.scatter(*_pos(path[0]),  s=200, c="green",  zorder=6, marker="*")
            ax.scatter(*_pos(path[-1]), s=200, c="red",    zorder=6, marker="*")

        ax.set_title(title, fontsize=9, fontweight="bold")
        ax.set_xlabel("Longitude", fontsize=8)
        ax.set_ylabel("Latitude", fontsize=8)

    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out_path}")


# ─────────────────────────────────────────────────────────────
# Figure 4 — Congestion heat-map
# ─────────────────────────────────────────────────────────────
def plot_congestion(out_path="fig4_congestion.png"):
    g = build_cairo_graph(include_potential=False)

    fig, axes = plt.subplots(1, 2, figsize=(15, 7), dpi=130)
    fig.patch.set_facecolor("#ECEFF1")
    cmap = plt.cm.RdYlGn_r    # red = high congestion, green = low

    for ax, period in zip(axes, ["morning", "evening"]):
        ax.set_facecolor("#263238")
        for (u, v, dist, cap, cond) in EXISTING_ROADS:
            tf    = TRAFFIC_FLOW.get((u, v)) or TRAFFIC_FLOW.get((v, u)) or {}
            flow  = tf.get(period, cap * 0.5)
            ratio = min(flow / cap, 1.0)
            color = cmap(ratio)
            xu, yu = _pos(u)
            xv, yv = _pos(v)
            ax.plot([xu, xv], [yu, yv], color=color,
                    linewidth=2.5 * (0.5 + ratio), alpha=0.85, zorder=2)

        # Node dots
        for nid in NODES:
            x, y = _pos(nid)
            ax.scatter(x, y, s=40, c="white", zorder=3, alpha=0.9,
                       edgecolors="#555", linewidths=0.3)

        ax.set_title(f"Traffic Congestion — {period.capitalize()} Peak",
                     fontsize=9, fontweight="bold", color="white")
        ax.set_xlabel("Longitude", fontsize=8, color="#AAA")
        ax.set_ylabel("Latitude", fontsize=8, color="#AAA")
        ax.tick_params(colors="#AAA")
        for spine in ax.spines.values():
            spine.set_edgecolor("#444")

    # Shared colour-bar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=mcolors.Normalize(0, 1))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=axes, fraction=0.025, pad=0.02)
    cbar.set_label("Flow / Capacity ratio", fontsize=8, color="white")
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white")

    plt.suptitle("Cairo Road Network — Congestion Levels\n"
                 "Green = free-flow  |  Red = near/over capacity",
                 fontsize=10, fontweight="bold", color="white",
                 y=1.01)
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved: {out_path}")


# ─────────────────────────────────────────────────────────────
# Entry point — generate all figures
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os, sys
    os.makedirs("outputs", exist_ok=True)
    print("Generating visualizations …")
    plot_full_network("outputs/fig1_network.png")
    plot_mst("outputs/fig2_mst.png")
    plot_shortest_paths("outputs/fig3_paths.png")
    plot_congestion("outputs/fig4_congestion.png")
    print("Done. All figures saved to outputs/")
