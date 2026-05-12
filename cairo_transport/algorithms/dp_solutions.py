"""
dp_solutions.py — CSE112 Project: Smart City Transportation
This module implements Dynamic Programming (DP) solutions to optimize 
public transit and infrastructure resources in Greater Cairo. [cite: 6, 10]

Core Concepts:
1. Bounded Knapsack: For Bus and Metro resource allocation. [cite: 69, 129]
2. 0/1 Knapsack: For road maintenance budget optimization. [cite: 70]
"""

from core.data import BUS_ROUTES, EXISTING_ROADS, TRAFFIC_FLOW, NODES, METRO_LINES
import math

# ═══════════════════════════════════════════════════════════════
# 1. BUS FLEET ALLOCATION (Bounded Knapsack)
# ═══════════════════════════════════════════════════════════════

def bus_fleet_allocation(total_buses: int = 250):
    """
    Goal: Distribute 'total_buses' across all routes to maximize passenger throughput. [cite: 69]
    
    Mathematical Model: Diminishing returns. 
    Adding the 50th bus adds fewer NEW passengers than adding the 1st bus.
    Formula: passengers = base * (1 - e^(-k/k_opt))

    Complexity:
    - Time: O(R * B * K) where R=Routes, B=Total Buses, K=Max buses per route.
    - Space: O(R * B) to store the DP table for backtracking.
    """
    routes = BUS_ROUTES
    R = len(routes)
    B = total_buses
    MAX_BUSES_PER_ROUTE = 50

    def gain(route, k):
        base = route["daily_passengers"]
        k_opt = route["buses"] * 1.5  # Saturation point constant
        if k == 0: return 0
        return int(base * (1 - math.exp(-k / k_opt)))

    # dp[i][b] = Max passengers using first 'i' routes with 'b' buses
    dp = [[0] * (B + 1) for _ in range(R + 1)]
    # alloc[i][b] = Number of buses assigned to route 'i' to get the value in dp[i][b]
    alloc = [[0] * (B + 1) for _ in range(R + 1)]

    for i in range(1, R + 1):
        route = routes[i - 1]
        for b in range(B + 1):
            best_val = dp[i-1][b] 
            best_k = 0
            # Try assigning 'k' buses to current route and take the rest from previous routes
            for k in range(1, min(b, MAX_BUSES_PER_ROUTE) + 1):
                val = dp[i-1][b-k] + gain(route, k)
                if val > best_val:
                    best_val = val
                    best_k = k
            dp[i][b] = best_val
            alloc[i][b] = best_k

    # Backtracking: Recovering the specific count for each route
    allocation = {}
    remaining = B
    for i in range(R, 0, -1):
        k = alloc[i][remaining]
        allocation[routes[i-1]["id"]] = k
        remaining -= k

    return allocation, dp[R][B], dp

# ═══════════════════════════════════════════════════════════════
# 2. ROAD MAINTENANCE BUDGET (0/1 Knapsack)
# ═══════════════════════════════════════════════════════════════

def road_maintenance_knapsack(budget_m_egp: int = 500):
    """
    Goal: Choose which road segments to repair to maximize 'Utility/Benefit' 
    under a strict financial budget. [cite: 70]

    Decision: To repair (1) or NOT repair (0) a specific segment.
    Benefit = Traffic Volume * (10 - Current Condition) * Distance

    Complexity:
    - Time: O(N * W) where N=Number of roads, W=Total Budget.
    - Space: O(N * W)
    """
    candidates = []
    for (u, v, dist, cap, cond) in EXISTING_ROADS:
        if cond >= 9: continue 
        
        tf = TRAFFIC_FLOW.get((u, v)) or TRAFFIC_FLOW.get((v, u)) or {}
        avg_flow = sum(tf.values()) / 4 if tf else cap * 0.5
        
        benefit = avg_flow * (10 - cond) * dist / 1000 
        cost_m = math.ceil(dist * 2) # Cost model: 2 Million EGP per KM
        
        candidates.append((NODES[u]["name"], NODES[v]["name"], cond, cost_m, round(benefit, 1)))

    N, W = len(candidates), budget_m_egp
    dp = [[0.0] * (W + 1) for _ in range(N + 1)]
    keep = [[False] * (W + 1) for _ in range(N + 1)]

    for i in range(1, N + 1):
        _, _, _, cost, benefit = candidates[i-1]
        for w in range(W + 1):
            dp[i][w] = dp[i-1][w]
            # Standard Knapsack check: Is current item better than the previous state?
            if cost <= w and dp[i-1][w - cost] + benefit > dp[i-1][w]:
                dp[i][w] = dp[i-1][w - cost] + benefit
                keep[i][w] = True

    # Backtracking: Finding the names of chosen roads
    chosen, w = [], W
    for i in range(N, 0, -1):
        if keep[i][w]:
            chosen.append(candidates[i-1])
            w -= candidates[i-1][3]

    return chosen, round(dp[N][W], 1), sum(r[3] for r in chosen)

# ═══════════════════════════════════════════════════════════════
# 3. METRO HEADWAY OPTIMISATION (Bounded Knapsack)
# ═══════════════════════════════════════════════════════════════

def metro_headway_optimization(total_fleet: int = 120):
    """
    Goal: Distribute limited Metro Trains across Line 1, 2, and 3 
    to achieve the highest overall passenger capacity growth. [cite: 129]

    Constraints: 
    - Minimum Headway: 2.0 min (Safety/Signal limit).
    - Maximum Headway: 10.0 min (Service quality limit).

    Complexity:
    - Time: O(L * F * K) where L=Lines, F=Fleet, K=Candidate options.
    - Space: O(L * F)
    """
    ROUND_TRIP = {"M1": 90, "M2": 70, "M3": 65}
    CURRENT_HEADWAY_BASE = 6.0
    MIN_HW, MAX_HW = 2.0, 10.0
    
    lines = METRO_LINES
    N, F = len(lines), total_fleet

    # Step 1: Pre-calculate the 'Utility' for every possible number of trains per line
    line_gains = []
    for line in lines:
        rt = ROUND_TRIP[line["id"]]
        base_pass = line["daily_passengers"]
        gains_for_line = {}
        
        for k in range(1, F + 1):
            hw = rt / k
            if MIN_HW <= hw <= MAX_HW:
                # Capacity is inversely proportional to headway
                projected = int(base_pass * (CURRENT_HEADWAY_BASE / hw))
                increase = projected - base_pass
                gains_for_line[k] = (increase, round(hw, 1))
            else:
                gains_for_line[k] = (-1e9, 0) # Invalid state
        line_gains.append(gains_for_line)

    # Step 2: Run DP to find the global optimum distribution
    dp = [[0] * (F + 1) for _ in range(N + 1)]
    parent = [[0] * (F + 1) for _ in range(N + 1)]

    for i in range(1, N + 1):
        for f in range(F + 1):
            dp[i][f] = dp[i-1][f]
            for k, (inc, hw) in line_gains[i-1].items():
                if k <= f and inc != -1e9:
                    if dp[i-1][f-k] + inc > dp[i][f]:
                        dp[i][f] = dp[i-1][f-k] + inc
                        parent[i][f] = k

    # Step 3: Backtrack and format results
    results = []
    rem_f = F
    for i in range(N, 0, -1):
        chosen_k = parent[i][rem_f]
        line = lines[i-1]
        if chosen_k > 0:
            inc, hw = line_gains[i-1][chosen_k]
            results.append({
                "line": line["name"],
                "current_pass": line["daily_passengers"],
                "optimal_hw": hw,
                "trains_needed": chosen_k,
                "projected_pass": line["daily_passengers"] + inc,
                "improvement_%": round((inc / line["daily_passengers"]) * 100, 1),
            })
            rem_f -= chosen_k
        else: # Default fallback if no improvement found
            results.append({
                "line": line["name"], 
                "current_pass": line["daily_passengers"],
                "optimal_hw": CURRENT_HEADWAY_BASE, 
                "trains_needed": 0, 
                "projected_pass": line["daily_passengers"],
                "improvement_%": 0.0
            })
            
    return results[::-1]

# ─────────────────────────────────────────────────────────────
# Quick self-test
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test bus allocation
    alloc, total_pass, _ = bus_fleet_allocation(total_buses=250)
    print(f"Total Daily Passengers: {total_pass:,}")

    # Test road maintenance
    roads, benefit, cost = road_maintenance_knapsack(500)
    print(f"Total Maintenance Benefit: {benefit}")

    # Test metro optimization
    for r in metro_headway_optimization(120):
        print(f"{r['line']}: {r['optimal_hw']} min headway with {r['trains_needed']} trains.")