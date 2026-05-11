"""
main.py — CSE112 Project
Smart City Transportation Network Optimization System
Greater Cairo Metropolitan Area

Run:  python main.py
"""

import os

from core.data import NODES, BUS_ROUTES, METRO_LINES
from core.graph import build_cairo_graph
from algorithms.mst import kruskal_mst, analyze_mst
from algorithms.shortest_path import (shortest_path, astar, time_dependent_dijkstra,
                           congested_roads, alternate_route, memoized_shortest_path)
from algorithms.dp_solutions import bus_fleet_allocation, road_maintenance_knapsack, metro_headway_optimization
from algorithms.greedy import traffic_signal_optimization, emergency_preemption, greedy_optimality_analysis
from utils.transit_network import optimize_transit_route, analyze_transfer_points, propose_integrated_network_expansion


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
SEP = "═" * 68

def name(nid):
    return NODES[nid]["name"]

def path_str(path):
    return " → ".join(name(n) for n in path)

def header(title):
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)


# ─────────────────────────────────────────────────────────────
# Demo Sections
# ─────────────────────────────────────────────────────────────

def demo_mst(g):
    header("1. INFRASTRUCTURE DESIGN — Kruskal's MST")
    mst, cost, dist = kruskal_mst(g)
    info = analyze_mst(mst)
    print(f"  Total MST edges         : {info['total_edges']}")
    print(f"  Existing roads used     : {info['existing_roads']}")
    print(f"  New roads recommended   : {info['new_roads']}")
    print(f"  Total network distance  : {info['total_dist_km']} km")
    print(f"  Construction budget     : {info['construction_cost']:,.0f} M EGP")
    print(f"  Critical nodes covered  : "
          f"{[name(n) for n in info['critical_covered']]}")
    print("\n  New roads to build:")
    for frm, to, c in info["new_roads_detail"]:
        print(f"    {frm:30s} ↔ {to:30s}  {c:,} M EGP")


def demo_shortest_paths(g):
    header("2. TRAFFIC FLOW — Dijkstra & Time-Dependent Routing")

    # Standard Dijkstra
    d, path = shortest_path(g, 7, 13)
    print(f"\n  [Dijkstra] 6th October City → New Admin Capital")
    print(f"  Distance : {d:.1f} km")
    print(f"  Path     : {path_str(path)}")

    d2, path2 = shortest_path(g, 2, 1)
    print(f"\n  [Dijkstra] Nasr City → Maadi")
    print(f"  Distance : {d2:.1f} km")
    print(f"  Path     : {path_str(path2)}")

    # Time-dependent
    print("\n  [Time-Dependent] New Cairo → Downtown Cairo:")
    for period in ["morning", "afternoon", "evening", "night"]:
        t, path = time_dependent_dijkstra(g, 4, 3, period)
        print(f"    {period:11s}: {t:5.1f} min   {path_str(path)}")

    # Congestion report
    print("\n  [Congestion] Top 5 over-capacity roads (morning):")
    for u, v, ratio in congested_roads(g, "morning")[:5]:
        print(f"    {name(u):25s} ↔ {name(v):25s}  {ratio*100:.0f}% of capacity")

    # Alternate route
    t_normal, _   = time_dependent_dijkstra(g, 1, 3, "morning")
    t_alt,  a_path = alternate_route(g, 1, 3, blocked_edges=[(1,8)], period="morning")
    print(f"\n  [Alternate Route] Maadi → Downtown (road 1-8 blocked):")
    print(f"    Normal route : {t_normal:.1f} min")
    print(f"    Alternate    : {t_alt:.1f} min  {path_str(a_path)}")


def demo_emergency(g):
    header("3. EMERGENCY RESPONSE — A* Algorithm")

    scenarios = [
        (8,   "F9",  "Giza → Qasr El Aini Hospital"),
        (7,   "F10", "6th October City → Maadi Military Hospital"),
        (13,  "F9",  "New Admin Capital → Qasr El Aini Hospital"),
        (4,   "F10", "New Cairo → Maadi Military Hospital"),
    ]

    for src, tgt, desc in scenarios:
        t, path = astar(g, src, tgt)

        # Compare with standard Dijkstra (distance only)
        d_dist, d_path = shortest_path(g, src, tgt)
        t_dijkstra     = d_dist / 60 * 60   # ~60 km/h

        print(f"\n  {desc}")
        print(f"    A* path     : {path_str(path)}")
        print(f"    A* ETA      : {t:.1f} min  (80 km/h emergency speed)")
        print(f"    Dijkstra ETA: {t_dijkstra:.1f} min  (60 km/h normal speed)")
        print(f"    Time saved  : {t_dijkstra - t:.1f} min")

        # Preemption plan
        if len(path) > 2:
            order, saved = emergency_preemption(path, "morning")
            print(f"    Preemption plan ({len(order)} intersections, saves {saved:.0f}s):")
            for item in order[:3]:
                print(f"      ▶ {item['name']:25s}  save {item['time_saved']}s")


def demo_dp(g):
    header("4. PUBLIC TRANSIT — Dynamic Programming")

    # Bus fleet allocation
    print("\n  [Bus Fleet Allocation]  Total fleet: 250 buses")
    alloc, total_pass, _ = bus_fleet_allocation(total_buses=250)
    total_current = sum(r["daily_passengers"] for r in BUS_ROUTES)
    print(f"  Current total passengers : {total_current:,}")
    print(f"  Optimised total          : {total_pass:,}")
    print(f"  Improvement              : +{total_pass - total_current:,} "
          f"({(total_pass/total_current - 1)*100:.1f}%)")
    print("\n  Allocation per route:")
    for rid, buses in sorted(alloc.items()):
        route = next(r for r in BUS_ROUTES if r["id"] == rid)
        delta = buses - route["buses"]
        sign  = "+" if delta >= 0 else ""
        print(f"    {rid}: {buses:3d} buses (was {route['buses']:3d}, {sign}{delta:+d})")

    # Road maintenance
    print("\n  [Road Maintenance Knapsack]  Budget: 500 M EGP")
    roads, benefit, cost = road_maintenance_knapsack(500)
    print(f"  Roads selected: {len(roads)}   Cost: {cost} M EGP   "
          f"Benefit score: {benefit}")
    for u, v, cond, c, ben in roads:
        print(f"    {u:25s} ↔ {v:25s}  cond={cond}  cost={c}M  benefit={ben}")

    # Metro headways
    print("\n  [Metro Headway Optimisation]")
    for r in metro_headway_optimization():
        print(f"  {r['line']}")
        print(f"    Optimal headway : {r['optimal_hw']} min  "
              f"({r['trains_needed']} trains)")
        print(f"    Daily passengers: {r['current_pass']:,} → "
              f"{r['projected_pass']:,}  (+{r['improvement_%']}%)")


def demo_transit_network(g):
    header("4.5 MULTIMODAL TRANSIT & INTEGRATED NETWORK")

    # Transit Routing
    print("\n  [Multimodal Routing] Maadi → Mohandessin")
    t, path = optimize_transit_route(1, 9)
    print(f"    Optimal Transit Time: {t} minutes")
    print("    Path:")
    for p in path:
        print(f"      {NODES[p[0]]['name']} ({p[1]} {p[2]})")

    # Transfer points
    print("\n  [Transfer Hub Analysis] Top 3 Intersections")
    hubs = analyze_transfer_points()
    for h in hubs[:3]:
        print(f"    {h['name']:25s} | Metro: {h['metro_lines']}, Bus: {h['bus_lines']} | Score: {h['hub_score']}")

    # Proposed Expansion
    print("\n  [Proposed Network Expansion]")
    route = propose_integrated_network_expansion()
    print(f"    Route: {route['name']}")
    print(f"    Stops: {' → '.join(NODES[s]['name'] if s in NODES else s for s in route['stops'])}")
    print(f"    Est. Daily Passengers: {route['estimated_daily_demand']:,.0f}")


def demo_greedy(g):
    header("5. TRAFFIC SIGNALS — Greedy Optimisation")

    print("\n  Top 5 most congested intersections (morning signal plan):")
    signals = traffic_signal_optimization("morning")
    for s in signals[:5]:
        print(f"\n  ▶ {s['name']:25s}  total flow: {s['total_flow']:,} veh/hr")
        for nbr, flow, green in s["arms"]:
            bar = "█" * int(green / 90 * 30)
            print(f"      → {name(nbr):22s}  flow={flow:,}  green={green:2d}s  {bar}")

    print("\n  Greedy Optimality Analysis:")
    for c in greedy_optimality_analysis():
        tag = "✓ OPTIMAL   " if c["greedy"] == "OPTIMAL" else "✗ SUBOPTIMAL"
        print(f"\n  [{tag}] {c['scenario']}")
        print(f"    {c['reason']}")


def demo_memoization(g):
    header("6. MEMOIZATION — Route Query Performance")
    import time
    queries = [(4, 3, "morning"), (7, 13, "evening"),
               (4, 3, "morning"), (7, 13, "evening")]   # 2 cached repeats
    for src, tgt, period in queries:
        t0  = time.perf_counter()
        tt, path = memoized_shortest_path(g, src, tgt, period)
        t1  = time.perf_counter()
        ms  = (t1 - t0) * 1000
        hit = "CACHE HIT" if ms < 0.1 else "computed "
        print(f"  [{hit}] {name(src):20s}→{name(tgt):20s} "
              f"[{period:11s}]  {tt:.1f} min  ({ms:.3f} ms)")


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def main():
    print("\n" + "═" * 68)
    print("  CSE112 — Smart City Transportation Optimization")
    print("  Greater Cairo Metropolitan Area")
    print("  Algorithms: Kruskal's MST | Dijkstra | A* | DP | Greedy")
    print("═" * 68)

    g = build_cairo_graph(include_potential=True)
    print(f"\n  Graph loaded: {len(g.nodes)} nodes, {len(g.all_edges())} edges")

    demo_mst(g)
    demo_shortest_paths(g)
    demo_emergency(g)
    demo_dp(g)
    demo_transit_network(g)
    demo_greedy(g)
    demo_memoization(g)

    # Optional: generate visualizations
    print(f"\n{SEP}")
    ans = input("  Generate matplotlib figures? (y/n): ").strip().lower()
    if ans == "y":
        from utils.visualization import (plot_full_network, plot_mst,
                                   plot_shortest_paths, plot_congestion)
        os.makedirs("outputs", exist_ok=True)
        plot_full_network("outputs/fig1_network.png")
        plot_mst("outputs/fig2_mst.png")
        plot_shortest_paths("outputs/fig3_paths.png")
        plot_congestion("outputs/fig4_congestion.png")
        print("  Figures saved to outputs/")

    print(f"\n{SEP}")
    print("  Demo complete.")
    print(SEP + "\n")


if __name__ == "__main__":
    main()
