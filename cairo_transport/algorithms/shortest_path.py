"""
B. Shortest Path Algorithms

  1. Dijkstra's algorithm  — standard optimal route planning
  2. A* algorithm          — emergency vehicle routing (uses coordinate heuristic)
  3. Time-Dependent Dijkstra — accounts for morning/evening rush hours (BPR model)

All three return (distance, path) tuples.
Complexity:
  Dijkstra / A*  : O((V + E) log V)  with binary heap
  Time-dep       : same, with travel-time edge weights instead of distance
"""

import heapq
import math
from core.graph import Graph, build_cairo_graph
from core.data import NODES


# ─────────────────────────────────────────────────────────────
# 1. Dijkstra's Algorithm
# ─────────────────────────────────────────────────────────────
def dijkstra(g: Graph, source, target=None, weight="dist"):
    """
    Standard Dijkstra shortest-path on graph g.

    Parameters
    ----------
    g      : Graph
    source : start node
    target : if given, stop early and return single path
    weight : edge attribute to use as weight ("dist" or "travel_time")

    Returns
    -------
    dist   : dict of {node: best_distance_from_source}
    prev   : dict of {node: predecessor}
    """
    dist = {n: float("inf") for n in g.all_nodes()}
    prev = {n: None         for n in g.all_nodes()}
    dist[source] = 0.0

    # (distance, node)
    heap = [(0.0, str(source), source)]   # str for tie-breaking

    while heap:
        d, _, u = heapq.heappop(heap)

        if d > dist[u]:
            continue  # stale entry

        if target is not None and u == target:
            break

        for (v, attr) in g.neighbors(u):
            w = attr.get(weight, attr.get("dist", float("inf")))
            if w is None:
                w = float("inf")
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, str(v), v))

    return dist, prev


def reconstruct_path(prev, source, target):
    """Walk predecessor map to get the path list."""
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    if path and path[0] == source:
        return path
    return []   # no path


def shortest_path(g: Graph, source, target):
    """
    Returns (distance_km, path_list) for the shortest route by distance.
    """
    dist, prev = dijkstra(g, source, target, weight="dist")
    path = reconstruct_path(prev, source, target)
    return dist[target], path


# ─────────────────────────────────────────────────────────────
# 2. A* Algorithm  (emergency vehicle routing)
# ─────────────────────────────────────────────────────────────
def _heuristic(g: Graph, u, target):
    """
    Admissible heuristic: straight-line distance in km.
    Uses coordinate data (longitude/latitude, 1° ≈ 111 km).
    Never overestimates because roads can't be shorter than straight line.
    """
    try:
        return g.euclidean_dist(u, target)
    except (KeyError, TypeError):
        return 0.0


def astar(g: Graph, source, target, period="morning"):
    """
    A* search for emergency vehicle routing.
    Edge cost = travel_time(period) to find the FASTEST route.
    Heuristic = straight-line distance converted to minutes at 60 km/h.

    Returns (travel_time_minutes, path_list)
    """
    g_score = {n: float("inf") for n in g.all_nodes()}
    f_score = {n: float("inf") for n in g.all_nodes()}
    prev    = {n: None         for n in g.all_nodes()}
    g_score[source] = 0.0
    h0 = _heuristic(g, source, target)
    f_score[source] = h0

    # (f_score, tie-break, node)
    heap = [(f_score[source], str(source), source)]

    while heap:
        f, _, u = heapq.heappop(heap)

        if u == target:
            break

        if f > f_score[u]:
            continue

        for (v, attr) in g.neighbors(u):
            # Emergency vehicles travel at 80 km/h ignoring congestion (BPR disabled)
            dist_km   = attr["dist"]
            t_minutes = dist_km / 80 * 60   # time at 80 km/h
            ng = g_score[u] + t_minutes

            if ng < g_score[v]:
                g_score[v] = ng
                prev[v]    = u
                h          = _heuristic(g, v, target) / 80 * 60
                f_score[v] = ng + h
                heapq.heappush(heap, (f_score[v], str(v), v))

    path = reconstruct_path(prev, source, target)
    return g_score[target], path


# ─────────────────────────────────────────────────────────────
# 3. Time-Dependent Dijkstra
# ─────────────────────────────────────────────────────────────
def time_dependent_dijkstra(g: Graph, source, target, period="morning"):
    """
    Dijkstra where edge weight = BPR travel time for the given period.
    Periods: "morning" | "afternoon" | "evening" | "night"

    Returns (travel_time_minutes, path_list)
    """
    dist = {n: float("inf") for n in g.all_nodes()}
    prev = {n: None         for n in g.all_nodes()}
    dist[source] = 0.0

    heap = [(0.0, str(source), source)]

    while heap:
        d, _, u = heapq.heappop(heap)

        if d > dist[u]:
            continue
        if u == target:
            break

        for (v, attr) in g.neighbors(u):
            t = g.travel_time(u, v, period)
            nd = d + t
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, str(v), v))

    path = reconstruct_path(prev, source, target)
    return dist[target], path


# ─────────────────────────────────────────────────────────────
# Congestion analysis helper
# ─────────────────────────────────────────────────────────────
def congested_roads(g: Graph, period="morning", threshold=0.85):
    """
    Return list of (u, v, flow/capacity ratio) for congested roads.
    Default threshold: flow > 85% of capacity.
    """
    from core.data import TRAFFIC_FLOW
    result = []
    seen   = set()
    for (u, v, attr) in g.all_edges():
        key  = g._key(u, v)
        if key in seen:
            continue
        seen.add(key)
        cap = attr.get("cap") or 3000
        tf  = TRAFFIC_FLOW.get((u, v)) or TRAFFIC_FLOW.get((v, u))
        if tf is None:
            continue
        flow  = tf.get(period, 0)
        ratio = flow / cap
        if ratio >= threshold:
            result.append((u, v, round(ratio, 2)))
    result.sort(key=lambda x: x[2], reverse=True)
    return result


# ─────────────────────────────────────────────────────────────
# Alternate route suggestion (road closure simulation)
# ─────────────────────────────────────────────────────────────
def alternate_route(g: Graph, source, target, blocked_edges=None, period="morning"):
    """
    Find an alternate route avoiding blocked edges.
    Returns (time_minutes, path_list) or (inf, []) if disconnected.
    """
    if blocked_edges is None:
        blocked_edges = []

    blocked_set = set()
    for (u, v) in blocked_edges:
        blocked_set.add(g._key(u, v))

    dist = {n: float("inf") for n in g.all_nodes()}
    prev = {n: None         for n in g.all_nodes()}
    dist[source] = 0.0
    heap = [(0.0, str(source), source)]

    while heap:
        d, _, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == target:
            break
        for (v, attr) in g.neighbors(u):
            if g._key(u, v) in blocked_set:
                continue
            t  = g.travel_time(u, v, period)
            nd = d + t
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, str(v), v))

    path = reconstruct_path(prev, source, target)
    return dist[target], path


# ─────────────────────────────────────────────────────────────
# Memoized wrapper (DP enhancement)
# ─────────────────────────────────────────────────────────────
_memo_cache = {}

def memoized_shortest_path(g: Graph, source, target, period="morning"):
    """Caches time-dependent results so repeated queries are O(1)."""
    key = (source, target, period)
    if key not in _memo_cache:
        _memo_cache[key] = time_dependent_dijkstra(g, source, target, period)
    return _memo_cache[key]


# ─────────────────────────────────────────────────────────────
# Quick self-test
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    g = build_cairo_graph(include_potential=False)

    def name(n):
        return NODES[n]["name"]

    # 1. Standard Dijkstra
    d, path = shortest_path(g, 7, 13)
    print("═" * 60)
    print("  DIJKSTRA — 6th October City → New Admin Capital")
    print(f"  Distance : {d:.1f} km")
    print(f"  Path     : {' → '.join(name(n) for n in path)}")

    # 2. A* Emergency routing
    t, path = astar(g, 8, "F9")
    print("\n  A* — Emergency: Giza → Qasr El Aini Hospital")
    print(f"  ETA (80 km/h): {t:.1f} min")
    print(f"  Path          : {' → '.join(name(n) for n in path)}")

    # 3. Time-dependent
    for period in ["morning", "afternoon", "night"]:
        t, path = time_dependent_dijkstra(g, 4, 3, period)
        print(f"\n  TD-Dijkstra — New Cairo → Downtown  [{period}]")
        print(f"  Travel time : {t:.1f} min")
        print(f"  Path        : {' → '.join(name(n) for n in path)}")

    # 4. Congestion report
    print("\n  CONGESTED ROADS (morning, >85% capacity):")
    for u, v, ratio in congested_roads(g, "morning")[:5]:
        print(f"    {name(u):25s} ↔ {name(v):25s}  {ratio*100:.0f}% capacity")
