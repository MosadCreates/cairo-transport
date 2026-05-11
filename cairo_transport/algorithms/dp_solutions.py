"""
dp_solutions.py — CSE112 Project
C. Dynamic Programming Solutions

  1. Bus Schedule Optimization  — 0/1 Knapsack variant
     Allocate a fixed pool of buses across routes to maximise passengers/bus.
     State: dp[i][b] = max passengers using first i routes with b buses total
     Time:  O(R × B)   Space: O(R × B)

  2. Road Maintenance Budget — 0/1 Knapsack
     Given budget B, choose which roads to repair to maximise benefit.
     Benefit = traffic_volume × (10 − current_condition)
     Time:  O(N × B_discrete)

  3. Vehicle Scheduling (metro headways) — DP interval scheduling
     Maximise metro capacity utilisation by choosing optimal headways.
"""

from core.data import BUS_ROUTES, EXISTING_ROADS, TRAFFIC_FLOW, NODES, METRO_LINES
import math


# ═══════════════════════════════════════════════════════════════
# 1. BUS FLEET ALLOCATION  (Bounded Knapsack)
# ═══════════════════════════════════════════════════════════════

def bus_fleet_allocation(total_buses: int = 250):
    """
    Distribute `total_buses` across all bus routes to maximise
    total daily passengers served.

    Each extra bus on a route adds passengers via a diminishing-returns model:
        passengers(route, k) = base_passengers * (1 - e^{-k / k_opt})
    where k_opt = buses that achieve 90 % of theoretical max.

    Returns
    -------
    allocation : dict {route_id: buses_assigned}
    total_pass : estimated total daily passengers
    dp_table   : the full DP table (for analysis)
    """
    routes = BUS_ROUTES
    R      = len(routes)
    B      = total_buses

    # Pre-compute passenger gain for each (route, #buses) combination
    # gain[i][b] = passengers if route i gets exactly b buses
    MAX_BUSES_PER_ROUTE = 50
    def gain(route, k):
        base = route["daily_passengers"]
        k_opt = route["buses"] * 1.5   # saturation point
        if k == 0:
            return 0
        return int(base * (1 - math.exp(-k / k_opt)))

    # DP table: dp[i][b] = max passengers using first i routes, b buses total
    dp   = [[0] * (B + 1) for _ in range(R + 1)]
    alloc = [[0] * (B + 1) for _ in range(R + 1)]   # store choice for backtrack

    for i in range(1, R + 1):
        route = routes[i - 1]
        for b in range(B + 1):
            best_val   = dp[i-1][b]   # give 0 buses to this route
            best_k     = 0
            for k in range(1, min(b, MAX_BUSES_PER_ROUTE) + 1):
                val = dp[i-1][b-k] + gain(route, k)
                if val > best_val:
                    best_val = val
                    best_k   = k
            dp[i][b]    = best_val
            alloc[i][b] = best_k

    # Backtrack to find optimal allocation
    allocation = {}
    remaining  = B
    for i in range(R, 0, -1):
        k = alloc[i][remaining]
        allocation[routes[i-1]["id"]] = k
        remaining -= k

    total_pass = dp[R][B]
    return allocation, total_pass, dp


# ═══════════════════════════════════════════════════════════════
# 2. ROAD MAINTENANCE BUDGET ALLOCATION  (0/1 Knapsack)
# ═══════════════════════════════════════════════════════════════

def road_maintenance_knapsack(budget_m_egp: int = 500):
    """
    Choose which roads to maintain within budget to maximise benefit.

    Benefit model:
        benefit = avg_daily_flow × (10 − condition) × distance
    Cost model (rough estimate):
        cost = distance × 2 M EGP/km  (resurfacing estimate)

    budget_m_egp : total maintenance budget in Million EGP

    Returns
    -------
    chosen_roads : list of (u, v, condition, cost, benefit)
    total_benefit, total_cost
    """
    # Build candidate list from existing roads with condition < 8
    candidates = []
    for (u, v, dist, cap, cond) in EXISTING_ROADS:
        if cond >= 9:
            continue    # already in good shape
        # average daily traffic volume (sum of all periods / 4)
        tf = TRAFFIC_FLOW.get((u, v)) or TRAFFIC_FLOW.get((v, u)) or {}
        avg_flow = sum(tf.values()) / 4 if tf else cap * 0.5
        benefit  = avg_flow * (10 - cond) * dist / 1000   # scaled
        cost_m   = math.ceil(dist * 2)                    # 2 M EGP per km
        name_u   = NODES[u]["name"]
        name_v   = NODES[v]["name"]
        candidates.append((name_u, name_v, cond, cost_m, round(benefit, 1)))

    N = len(candidates)
    W = budget_m_egp

    # Standard 0/1 Knapsack DP
    dp   = [[0.0] * (W + 1) for _ in range(N + 1)]
    keep = [[False] * (W + 1) for _ in range(N + 1)]

    for i in range(1, N + 1):
        _, _, _, cost, benefit = candidates[i-1]
        for w in range(W + 1):
            dp[i][w] = dp[i-1][w]
            if cost <= w and dp[i-1][w - cost] + benefit > dp[i-1][w]:
                dp[i][w]   = dp[i-1][w - cost] + benefit
                keep[i][w] = True

    # Backtrack
    chosen = []
    w = W
    for i in range(N, 0, -1):
        if keep[i][w]:
            chosen.append(candidates[i-1])
            w -= candidates[i-1][3]   # subtract cost

    total_benefit = dp[N][W]
    total_cost    = sum(r[3] for r in chosen)
    return chosen, round(total_benefit, 1), total_cost


# ═══════════════════════════════════════════════════════════════
# 3. METRO HEADWAY OPTIMISATION  (DP interval scheduling)
# ═══════════════════════════════════════════════════════════════

def metro_headway_optimization():
    """
    For each metro line determine the optimal headway (minutes between trains)
    to maximise passenger throughput given rolling-stock constraints.

    Model:
        throughput(headway) = daily_passengers_at_current_headway
                              × (current_headway / headway)
        Constraints:
            min_headway = 2 min  (safety)
            max_headway = 10 min (service standard)
            num_trains_needed = operating_hours / headway (simplified)
            max_trains = 50 per line

    Uses DP over discrete headway values (2-10 min, step 0.5).
    """
    # Fleet sizing: fleet = round_trip_time / headway
    # Estimated round-trip times per line (minutes)
    ROUND_TRIP = {"M1": 90, "M2": 70, "M3": 65}
    CURRENT_HEADWAY = 6   # minutes (baseline)
    MAX_FLEET       = 50  # trains available per line
    results         = []

    for line in METRO_LINES:
        base_pass  = line["daily_passengers"]
        rt         = ROUND_TRIP[line["id"]]
        # Discrete headway choices: 2 to 10 min, step 0.5
        headways   = [h / 2 for h in range(4, 21)]
        best_pass  = 0
        best_hw    = CURRENT_HEADWAY
        best_fleet = math.ceil(rt / CURRENT_HEADWAY)

        for hw in headways:
            fleet_needed = math.ceil(rt / hw)   # trains to maintain headway
            if fleet_needed > MAX_FLEET:
                continue
            # Passengers scale with frequency (1/headway) up to demand saturation
            projected = int(base_pass * (CURRENT_HEADWAY / hw))
            if projected > best_pass:
                best_pass  = projected
                best_hw    = hw
                best_fleet = fleet_needed

        improvement = round((best_pass - base_pass) / base_pass * 100, 1)
        results.append({
            "line":          line["name"],
            "current_pass":  base_pass,
            "optimal_hw":    best_hw,
            "trains_needed": best_fleet,
            "projected_pass":best_pass,
            "improvement_%": improvement,
        })
    return results


# ─────────────────────────────────────────────────────────────
# Quick self-test
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # 1. Bus fleet allocation
    print("═" * 65)
    print("  BUS FLEET ALLOCATION  (250 buses, 10 routes)")
    print("═" * 65)
    alloc, total_pass, _ = bus_fleet_allocation(total_buses=250)
    for rid, buses in sorted(alloc.items()):
        route = next(r for r in BUS_ROUTES if r["id"] == rid)
        print(f"  {rid}: {buses:3d} buses  (base {route['buses']:3d})  "
              f"→ {route['id']}")
    print(f"\n  Total estimated daily passengers: {total_pass:,}")

    # 2. Road maintenance
    print("\n" + "═" * 65)
    print("  ROAD MAINTENANCE KNAPSACK  (Budget: 500 M EGP)")
    print("═" * 65)
    roads, benefit, cost = road_maintenance_knapsack(500)
    for u, v, cond, c, ben in roads:
        print(f"  {u:25s} ↔ {v:25s}  cond={cond}  cost={c} M  benefit={ben}")
    print(f"\n  Total cost: {cost} M EGP   Total benefit score: {benefit}")

    # 3. Metro headway
    print("\n" + "═" * 65)
    print("  METRO HEADWAY OPTIMISATION")
    print("═" * 65)
    for r in metro_headway_optimization():
        print(f"  {r['line']}")
        print(f"    Optimal headway : {r['optimal_hw']} min  "
              f"({r['trains_needed']} trains)")
        print(f"    Passengers/day  : {r['current_pass']:,} → "
              f"{r['projected_pass']:,}  (+{r['improvement_%']}%)")
