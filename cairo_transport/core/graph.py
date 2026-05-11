"""
graph.py — CSE112 Project
Weighted graph representation of Cairo's transportation network.
Supports both existing and potential-new roads, temporal traffic data.
"""

from collections import defaultdict
from core.data import NODES, EXISTING_ROADS, POTENTIAL_ROADS, TRAFFIC_FLOW
import math


class Graph:
    """
    Adjacency-list weighted graph.
    Each edge stores: distance, capacity, condition, cost (new roads only).
    """

    def __init__(self):
        # adj[u] = list of (v, attr_dict)
        self.adj: dict = defaultdict(list)
        self.nodes: dict = {}          # node_id -> node_data
        self.edge_attrs: dict = {}     # (u,v) -> attr_dict  (canonical: u <= v by str comparison)
        self.traffic: dict = {}        # (u,v) -> {morning, afternoon, evening, night}

    # ── Node management ──────────────────────────────────────────────────────
    def add_node(self, node_id, **attrs):
        self.nodes[node_id] = attrs

    # ── Edge management ──────────────────────────────────────────────────────
    def add_edge(self, u, v, distance, capacity=None,
                 condition=None, cost=None, is_new=False):
        attr = {
            "dist":   distance,
            "cap":    capacity,
            "cond":   condition,
            "cost":   cost,
            "is_new": is_new,
        }
        self.adj[u].append((v, attr))
        self.adj[v].append((u, attr))
        key = self._key(u, v)
        self.edge_attrs[key] = attr

    def _key(self, u, v):
        """Canonical undirected edge key."""
        su, sv = str(u), str(v)
        return (su, sv) if su < sv else (sv, su)

    def get_edge(self, u, v):
        return self.edge_attrs.get(self._key(u, v))

    def neighbors(self, u):
        return self.adj[u]          # [(v, attr), ...]

    def all_nodes(self):
        return list(self.nodes.keys())

    def all_edges(self):
        seen = set()
        result = []
        for u, nbrs in self.adj.items():
            for v, attr in nbrs:
                k = self._key(u, v)
                if k not in seen:
                    seen.add(k)
                    result.append((u, v, attr))
        return result

    # ── Haversine / Euclidean heuristic for A* ────────────────────────────
    def euclidean_dist(self, u, v):
        """Degree-based Euclidean distance (good enough as A* heuristic)."""
        nu, nv = self.nodes[u], self.nodes[v]
        dx = nu["x"] - nv["x"]
        dy = nu["y"] - nv["y"]
        # 1 degree ≈ 111 km
        return math.sqrt(dx**2 + dy**2) * 111

    # ── Time-dependent edge weight ─────────────────────────────────────────
    def travel_time(self, u, v, period="morning"):
        """
        Effective travel time (minutes) considering congestion.
        BPR (Bureau of Public Roads) function:
            t = t_free * (1 + 0.15 * (flow/capacity)^4)
        where t_free = distance / 60 km/h * 60 min
        """
        attr = self.get_edge(u, v)
        if attr is None:
            return float("inf")
        dist = attr["dist"]
        cap  = attr["cap"] or 3000
        flow_key = self._key(u, v)
        # look up traffic flow in both key directions
        flow_data = (
            TRAFFIC_FLOW.get((u, v)) or
            TRAFFIC_FLOW.get((v, u)) or
            {"morning": cap * 0.8, "afternoon": cap * 0.5,
             "evening": cap * 0.75, "night": cap * 0.2}
        )
        flow = flow_data.get(period, cap * 0.5)
        ratio = flow / cap
        # free-flow speed 60 km/h
        t_free = dist / 60 * 60          # minutes
        t_congested = t_free * (1 + 0.15 * ratio**4)
        return t_congested


# ─────────────────────────────────────────────────────────────
# Build the global Cairo graph from provided data
# ─────────────────────────────────────────────────────────────
def build_cairo_graph(include_potential=True) -> Graph:
    g = Graph()

    # Add all nodes
    for nid, attrs in NODES.items():
        g.add_node(nid, **attrs)

    # Add existing roads (bidirectional)
    for (u, v, dist, cap, cond) in EXISTING_ROADS:
        g.add_edge(u, v, dist, capacity=cap, condition=cond, is_new=False)

    # F9/F10 have no explicit roads in the dataset; connect to nearest nodes
    # so emergency routing always reaches the hospitals.
    if g.get_edge("F9", 3) is None:
        g.add_edge("F9", 3,  0.5, capacity=1500, condition=8, is_new=False)
        g.add_edge("F9", 10, 0.8, capacity=1500, condition=8, is_new=False)
    if g.get_edge("F10", 1) is None:
        g.add_edge("F10", 1,  0.3, capacity=1500, condition=8, is_new=False)
        g.add_edge("F10", 12, 2.0, capacity=1500, condition=7, is_new=False)

    # Optionally add potential new roads
    if include_potential:
        for (u, v, dist, cap, cost) in POTENTIAL_ROADS:
            # Only add if edge doesn't already exist
            if g.get_edge(u, v) is None:
                g.add_edge(u, v, dist, capacity=cap, cost=cost, is_new=True)

    return g


if __name__ == "__main__":
    g = build_cairo_graph()
    print(f"Nodes : {len(g.nodes)}")
    print(f"Edges : {len(g.all_edges())}")
    print(f"Travel time 1→3 (morning): {g.travel_time(1,3,'morning'):.2f} min")
