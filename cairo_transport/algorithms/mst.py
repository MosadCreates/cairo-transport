"""
Infrastructure Network Design using Kruskal's Algorithm.

Modifications for the transportation problem:
  1. Population-weighted edges: edges connecting high-population areas get a
     discount factor so they are selected first.
  2. Critical-facility guarantee: hospitals (F9, F10) and the new capital (13)
     are forced into the MST by giving their incident edges near-zero weight.
  3. Existing roads cost nothing to "use" (cost = 0); potential roads cost
     their construction budget.

--- Complexity Analysis ---
Time Complexity: O(E log E)  [due to sorting edges in Kruskal]
Space Complexity: O(V + E)  [for storing graph and union-find structures]
"""

import math
from core.graph import Graph, build_cairo_graph
from core.data import NODES, EXISTING_ROADS, POTENTIAL_ROADS, CRITICAL_NODES


# ─────────────────────────────────────────────────────────────
# Union-Find (Disjoint Set Union) with path compression + union by rank
# ─────────────────────────────────────────────────────────────
class UnionFind:
    def __init__(self, nodes):
        self.parent = {n: n for n in nodes}
        self.rank   = {n: 0  for n in nodes}

    def find(self, x):
        # Path compression
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y) -> bool:
        """Returns True if x and y were in different sets (edge added)."""
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        # Union by rank
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True


# ─────────────────────────────────────────────────────────────
# Edge weight function
# ─────────────────────────────────────────────────────────────
MAX_POP = max(v.get("pop", 1) for v in NODES.values()) or 1

def _population_factor(u, v) -> float:
    """
    Returns a multiplier in (0, 1].
    Higher average population → smaller multiplier → edge preferred.
    Formula: 1 - 0.5 * (avg_pop / max_pop)
    """
    pop_u = NODES.get(u, {}).get("pop", 0)
    pop_v = NODES.get(v, {}).get("pop", 0)
    avg   = (pop_u + pop_v) / 2
    return 1.0 - 0.5 * (avg / MAX_POP)


def edge_weight(u, v, dist, cost, is_new: bool) -> float:
    """
    Effective MST weight.
    - Existing roads: weight = distance × population_factor  (no monetary cost)
    - New roads:      weight = cost × population_factor       (minimize spend)
    Critical facility edges get weight /= 1000 (force inclusion).
    """
    is_critical = (u in CRITICAL_NODES or v in CRITICAL_NODES)
    pf = _population_factor(u, v)

    if is_new:
        w = cost * pf
    else:
        w = dist * pf

    if is_critical:
        w /= 1000.0
    return w


# ─────────────────────────────────────────────────────────────
# Kruskal's Algorithm
# ─────────────────────────────────────────────────────────────
def kruskal_mst(g: Graph):
    """
    Run Kruskal's algorithm on the Cairo graph.

    Returns
    -------
    mst_edges : list of (u, v, attr, weight)
    total_cost : total construction cost of NEW roads selected (M EGP)
    total_dist : total distance in MST (km)
    """
    all_nodes = g.all_nodes()
    uf = UnionFind(all_nodes)

    # Build edge list with computed weights
    raw_edges = []
    for (u, v, attr) in g.all_edges():
        dist   = attr["dist"]
        cost   = attr.get("cost") or 0
        is_new = attr.get("is_new", False)
        w      = edge_weight(u, v, dist, cost, is_new)
        raw_edges.append((w, u, v, attr))

    # Sort edges by weight ascending
    raw_edges.sort(key=lambda e: e[0])

    mst_edges   = []
    total_cost  = 0.0
    total_dist  = 0.0
    needed      = len(all_nodes) - 1

    for (w, u, v, attr) in raw_edges:
        if uf.union(u, v):
            mst_edges.append((u, v, attr, w))
            total_dist += attr["dist"]
            if attr.get("is_new"):
                total_cost += attr.get("cost", 0)
            if len(mst_edges) == needed:
                break

    return mst_edges, total_cost, total_dist


# ─────────────────────────────────────────────────────────────
# Analysis helpers
# ─────────────────────────────────────────────────────────────
def analyze_mst(mst_edges):
    new_roads  = [(u, v, a) for u, v, a, _ in mst_edges if a.get("is_new")]
    exist_roads= [(u, v, a) for u, v, a, _ in mst_edges if not a.get("is_new")]
    total_cost = sum(a.get("cost", 0) for _, _, a in new_roads)
    total_dist = sum(a["dist"] for _, _, a, _ in mst_edges)
    critical_covered = [
        n for n in CRITICAL_NODES
        if any(u == n or v == n for u, v, _, _ in mst_edges)
    ]
    return {
        "total_edges":       len(mst_edges),
        "existing_roads":    len(exist_roads),
        "new_roads":         len(new_roads),
        "new_roads_detail":  [(NODES[u]["name"], NODES[v]["name"], a.get("cost", 0))
                              for u, v, a in new_roads],
        "total_dist_km":     round(total_dist, 1),
        "construction_cost": round(total_cost, 0),
        "critical_covered":  critical_covered,
    }


# ─────────────────────────────────────────────────────────────
# Quick self-test
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    g = build_cairo_graph(include_potential=True)
    mst, cost, dist = kruskal_mst(g)
    info = analyze_mst(mst)

    print("═" * 60)
    print("  KRUSKAL'S MST — Infrastructure Network Design")
    print("═" * 60)
    print(f"  Total edges in MST   : {info['total_edges']}")
    print(f"  Existing roads used  : {info['existing_roads']}")
    print(f"  New roads to build   : {info['new_roads']}")
    print(f"  Total network dist   : {info['total_dist_km']} km")
    print(f"  Construction cost    : {info['construction_cost']:,.0f} M EGP")
    print(f"  Critical nodes covered: {info['critical_covered']}")
    print("\n  New roads recommended:")
    for frm, to, c in info["new_roads_detail"]:
        print(f"    {frm:30s} ↔ {to:30s}  {c:,} M EGP")
