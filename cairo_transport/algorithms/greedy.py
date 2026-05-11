"""
greedy.py — CSE112 Project
D. Greedy Algorithm Applications

  1. Traffic Signal Optimisation — Green-time allocation at intersections
     Greedy choice: give more green time to the road with highest current flow.
     Greedy is OPTIMAL here because problems are independent per intersection.

  2. Emergency Vehicle Preemption — Priority queue for clearing corridors
     Greedy choice: always clear the intersection with highest total delay first.

  3. Analysis of optimality / suboptimality in Cairo context.
"""

import heapq
from core.data import NODES, EXISTING_ROADS, TRAFFIC_FLOW


# ═══════════════════════════════════════════════════════════════
# 1. TRAFFIC SIGNAL GREEN-TIME ALLOCATION
# ═══════════════════════════════════════════════════════════════

def traffic_signal_optimization(period="morning"):
    """
    For each intersection (node with degree ≥ 2) allocate green time
    proportional to incoming traffic flow.

    Greedy rule: fraction of green time ∝ flow on each approach arm.
    Total cycle = 90 seconds (typical Cairo signal cycle).

    Returns list of
        {"intersection": node, "name": str, "arms": [(neighbour, flow, green_s)], "total_flow": int}
    sorted by total_flow descending (most congested first).
    """
    from collections import defaultdict
    CYCLE_S = 90    # signal cycle length in seconds
    MIN_GREEN = 10  # minimum green per arm in seconds

    # Build adjacency map with flows
    adj_flow = defaultdict(list)
    for (u, v, dist, cap, cond) in EXISTING_ROADS:
        tf  = TRAFFIC_FLOW.get((u, v)) or TRAFFIC_FLOW.get((v, u)) or {}
        flow = tf.get(period, cap * 0.5)
        adj_flow[u].append((v, flow))
        adj_flow[v].append((u, flow))

    results = []
    for node, arms in adj_flow.items():
        if len(arms) < 2:
            continue
        total_flow = sum(f for _, f in arms)
        green_times = []
        remaining   = CYCLE_S
        n_arms      = len(arms)

        # Greedy allocation: proportional to flow
        for i, (nbr, flow) in enumerate(arms):
            if i == n_arms - 1:
                # Last arm gets whatever is left
                g = max(MIN_GREEN, remaining)
            else:
                g = max(MIN_GREEN, int(CYCLE_S * flow / total_flow))
                remaining -= g
            green_times.append((nbr, int(flow), g))

        results.append({
            "intersection": node,
            "name":         NODES[node]["name"],
            "arms":         green_times,
            "total_flow":   total_flow,
        })

    results.sort(key=lambda x: x["total_flow"], reverse=True)
    return results


# ═══════════════════════════════════════════════════════════════
# 2. EMERGENCY VEHICLE PREEMPTION (Priority Queue)
# ═══════════════════════════════════════════════════════════════

def emergency_preemption(path: list, period="morning"):
    """
    Given an emergency vehicle path (list of node IDs), compute the
    optimal sequence of intersection preemptions to minimise total delay.

    Greedy rule: preempt the highest-delay intersection first.
    Delay at intersection i ≈ (red_time) × (flow / capacity)

    Parameters
    ----------
    path   : sequence of node IDs the vehicle will traverse
    period : traffic period

    Returns
    -------
    preemption_order : [(node, estimated_delay_s, time_saved_s)]
    total_time_saved : seconds
    """
    from collections import defaultdict
    CYCLE_S    = 90
    SPEED_KMPH = 80    # emergency vehicle speed

    # Build a quick capacity map
    cap_map = {}
    for (u, v, dist, cap, cond) in EXISTING_ROADS:
        cap_map[(u, v)] = cap
        cap_map[(v, u)] = cap

    # Compute delay at each intersection along the path
    intersections = []
    for i, node in enumerate(path[1:-1], start=1):   # skip start/end
        u = path[i-1]
        v = path[i+1]
        cap  = cap_map.get((u, node), 3000)
        tf   = TRAFFIC_FLOW.get((u, node)) or TRAFFIC_FLOW.get((node, u)) or {}
        flow = tf.get(period, cap * 0.5)
        ratio = flow / cap
        # Estimated red-time fraction: 0.5 cycle when ratio < 0.5, scales up
        red_fraction = 0.5 + 0.3 * ratio
        delay_s      = CYCLE_S * red_fraction
        # Preemption saves proportional to delay * remaining path
        remaining_km = sum(
            next((d for a,b,d,_,_ in EXISTING_ROADS if (a==path[j] and b==path[j+1])
                  or (b==path[j] and a==path[j+1])), 1)
            for j in range(i, len(path)-1)
        )
        priority = delay_s * remaining_km   # higher = preempt first
        intersections.append((priority, node, delay_s))

    # Max-heap (negate priority for heapq)
    heap = [(-p, n, d) for p, n, d in intersections]
    heapq.heapify(heap)

    preemption_order = []
    total_saved      = 0.0
    while heap:
        neg_p, node, delay = heapq.heappop(heap)
        saved = delay * 0.85   # preemption saves ~85% of expected delay
        preemption_order.append({
            "node":       node,
            "name":       NODES[node]["name"],
            "delay_s":    round(delay, 1),
            "time_saved": round(saved, 1),
        })
        total_saved += saved

    return preemption_order, round(total_saved, 1)


# ═══════════════════════════════════════════════════════════════
# 3. OPTIMALITY ANALYSIS
# ═══════════════════════════════════════════════════════════════

def greedy_optimality_analysis():
    """
    Returns a structured analysis of when the greedy signal approach
    is optimal vs. suboptimal in Cairo's context.
    """
    cases = [
        {
            "scenario": "Isolated intersection, single peak",
            "greedy":   "OPTIMAL",
            "reason":   "Proportional allocation minimises average wait with no coupling to other intersections.",
        },
        {
            "scenario": "Arterial corridor (several linked signals)",
            "greedy":   "SUBOPTIMAL",
            "reason":   "Green-wave coordination requires global planning; greedy local allocation can fragment the wave.",
        },
        {
            "scenario": "Emergency vehicle in low-density area (night)",
            "greedy":   "OPTIMAL",
            "reason":   "Conflict-free preemption always improves ETA; no trade-off with other vehicles.",
        },
        {
            "scenario": "Multiple simultaneous emergencies on shared corridor",
            "greedy":   "SUBOPTIMAL",
            "reason":   "Preempting for one vehicle may block another; a DP or ILP solution would be needed.",
        },
        {
            "scenario": "Bus fleet allocation (single route, linear gain)",
            "greedy":   "OPTIMAL",
            "reason":   "Fractional knapsack: greedy sort by value/weight gives optimal split (Greedy theorem).",
        },
        {
            "scenario": "Road maintenance budget (integer costs)",
            "greedy":   "SUBOPTIMAL",
            "reason":   "0/1 Knapsack is NP-hard; greedy (sort by benefit/cost) may miss the optimal subset.",
        },
    ]
    return cases


# ─────────────────────────────────────────────────────────────
# Quick self-test
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # 1. Traffic signals
    print("═" * 65)
    print("  TRAFFIC SIGNAL OPTIMISATION — Top 5 congested intersections (morning)")
    print("═" * 65)
    signals = traffic_signal_optimization("morning")
    for s in signals[:5]:
        print(f"\n  ▶ {s['name']}  (total flow: {s['total_flow']:,} veh/hr)")
        for nbr, flow, green in s["arms"]:
            print(f"      → {NODES[nbr]['name']:25s}  flow={flow:,}  green={green}s")

    # 2. Emergency preemption
    print("\n" + "═" * 65)
    print("  EMERGENCY PREEMPTION — Giza → Qasr El Aini Hospital")
    print("═" * 65)
    sample_path = [8, 10, 3, "F9"]   # approximate path
    order, saved = emergency_preemption(sample_path, "morning")
    for item in order:
        print(f"  Preempt {item['name']:25s}  delay={item['delay_s']}s  saved={item['time_saved']}s")
    print(f"\n  Total time saved: {saved} seconds ({saved/60:.1f} minutes)")

    # 3. Optimality analysis
    print("\n" + "═" * 65)
    print("  OPTIMALITY ANALYSIS")
    print("═" * 65)
    for c in greedy_optimality_analysis():
        print(f"\n  Scenario : {c['scenario']}")
        print(f"  Greedy   : {c['greedy']}")
        print(f"  Reason   : {c['reason']}")
