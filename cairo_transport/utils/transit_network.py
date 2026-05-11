"""
transit_network.py — CSE112 Project
Public Transit Optimization (Transfers & Integrated Network Design)

Requirements addressed:
- Design an integrated public transportation network
- Analyze and optimize transfer points between different transportation modes
"""

import heapq
from core.data import NODES, BUS_ROUTES, METRO_LINES

def build_multimodal_graph():
    """
    Builds a graph specifically for public transit, including both Bus and Metro.
    Edges represent travel time.
    Nodes are structured as (node_id, 'mode', 'line_id') to handle transfer penalties.
    """
    transit_graph = {}
    
    def add_edge(u, v, weight):
        if u not in transit_graph: transit_graph[u] = []
        if v not in transit_graph: transit_graph[v] = []
        transit_graph[u].append((v, weight))
        transit_graph[v].append((u, weight))

    # Add Metro Lines
    for line in METRO_LINES:
        stations = line["stations"]
        for i in range(len(stations) - 1):
            u = (stations[i], 'Metro', line['id'])
            v = (stations[i+1], 'Metro', line['id'])
            add_edge(u, v, 3.0)  # ~3 mins between metro stations
            
    # Add Bus Routes
    for route in BUS_ROUTES:
        stops = route["stops"]
        for i in range(len(stops) - 1):
            u = (stops[i], 'Bus', route['id'])
            v = (stops[i+1], 'Bus', route['id'])
            add_edge(u, v, 8.0)  # ~8 mins between bus stops
            
    # Add Transfer Edges at shared stations
    # If a geographic node has multiple transit stops, connect them with a transfer penalty
    location_groups = {}
    for node in transit_graph.keys():
        loc = node[0]
        if loc not in location_groups:
            location_groups[loc] = []
        location_groups[loc].append(node)
        
    TRANSFER_PENALTY_BUS_TO_METRO = 5.0  # minutes
    TRANSFER_PENALTY_BUS_TO_BUS = 10.0   # minutes
    TRANSFER_PENALTY_METRO_TO_METRO = 4.0 # minutes

    for loc, modes in location_groups.items():
        for i in range(len(modes)):
            for j in range(i + 1, len(modes)):
                u, v = modes[i], modes[j]
                # Determine penalty
                if u[1] == 'Metro' and v[1] == 'Metro':
                    penalty = TRANSFER_PENALTY_METRO_TO_METRO
                elif u[1] == 'Bus' and v[1] == 'Bus':
                    penalty = TRANSFER_PENALTY_BUS_TO_BUS
                else:
                    penalty = TRANSFER_PENALTY_BUS_TO_METRO
                add_edge(u, v, penalty)

    return transit_graph, location_groups

def optimize_transit_route(start_loc, end_loc):
    """
    Finds the optimal transit route between two locations, considering transfer penalties.
    Uses Dijkstra's algorithm on the multimodal graph.
    """
    transit_graph, location_groups = build_multimodal_graph()
    
    if start_loc not in location_groups or end_loc not in location_groups:
        return float('inf'), []

    # Virtual start and end nodes to connect to any available mode at the location
    virtual_start = (start_loc, 'Virtual', 'Start')
    virtual_end = (end_loc, 'Virtual', 'End')
    
    # We don't permanently add to graph, just handle in Dijkstra initialization
    dist = {node: float('inf') for node in transit_graph.keys()}
    prev = {node: None for node in transit_graph.keys()}
    
    heap = []
    # Start from any mode available at start_loc with 0 cost
    for start_node in location_groups[start_loc]:
        dist[start_node] = 0.0
        heapq.heappush(heap, (0.0, str(start_node), start_node))
        
    # Standard Dijkstra
    best_end_node = None
    min_end_dist = float('inf')

    while heap:
        d, _, u = heapq.heappop(heap)
        
        if d > dist.get(u, float('inf')):
            continue
            
        if u[0] == end_loc:
            if d < min_end_dist:
                min_end_dist = d
                best_end_node = u
            continue

        for v, weight in transit_graph.get(u, []):
            nd = d + weight
            if nd < dist.get(v, float('inf')):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, str(v), v))
                
    if best_end_node is None:
        return float('inf'), []
        
    # Reconstruct path
    path = []
    curr = best_end_node
    while curr is not None:
        path.append(curr)
        curr = prev[curr]
    path.reverse()
    
    return min_end_dist, path

def analyze_transfer_points():
    """
    Identifies the most critical transfer hubs in the network (nodes with the highest degree
    of intersecting transit lines) to prioritize for infrastructure upgrades.
    """
    _, location_groups = build_multimodal_graph()
    
    hub_scores = []
    for loc, nodes in location_groups.items():
        if len(nodes) > 1:
            bus_lines = sum(1 for n in nodes if n[1] == 'Bus')
            metro_lines = sum(1 for n in nodes if n[1] == 'Metro')
            score = (metro_lines * 2) + bus_lines  # Metro intersections carry more weight
            hub_scores.append({
                "node": loc,
                "name": NODES[loc]["name"] if loc in NODES else loc,
                "total_lines": len(nodes),
                "metro_lines": metro_lines,
                "bus_lines": bus_lines,
                "hub_score": score
            })
            
    # Sort by criticality
    hub_scores.sort(key=lambda x: x["hub_score"], reverse=True)
    return hub_scores

def propose_integrated_network_expansion():
    """
    Proposes a new integrated bus route that connects high-population areas that are 
    currently poorly connected to the Metro network.
    """
    _, location_groups = build_multimodal_graph()
    
    # Find all nodes connected to Metro
    metro_connected_nodes = set()
    for loc, nodes in location_groups.items():
        if any(n[1] == 'Metro' for n in nodes):
            metro_connected_nodes.add(loc)
            
    # Find high population nodes NOT on the Metro
    underserved = []
    for nid, attrs in NODES.items():
        if attrs.get("type") in ["Residential", "Mixed"] and nid not in metro_connected_nodes:
            underserved.append((nid, attrs["pop"]))
            
    underserved.sort(key=lambda x: x[1], reverse=True)
    
    # Propose a route connecting the top 3 underserved areas to the nearest major Metro hub (Ramses)
    top_underserved = [u[0] for u in underserved[:3]]
    proposed_route = {
        "id": "New-Express-1",
        "name": "Metro Feeder Express",
        "stops": top_underserved + ["F2"], # Connecting to Ramses Railway Station
        "estimated_daily_demand": sum(u[1] for u in underserved[:3]) * 0.05 # Assume 5% capture rate
    }
    
    return proposed_route

if __name__ == "__main__":
    print("═" * 65)
    print("  MULTIMODAL TRANSIT ROUTING (Bus + Metro + Transfers)")
    print("═" * 65)
    t, path = optimize_transit_route(1, 9) # Maadi to Mohandessin
    print(f"Optimal Transit Time: {t} minutes")
    print("Path:")
    for p in path:
        print(f"  {NODES[p[0]]['name']} ({p[1]} {p[2]})")

    print("\n═" * 65)
    print("  CRITICAL TRANSFER HUBS FOR UPGRADES")
    print("═" * 65)
    hubs = analyze_transfer_points()
    for h in hubs[:5]:
        print(f"  {h['name']:25s} | Metro: {h['metro_lines']}, Bus: {h['bus_lines']} | Score: {h['hub_score']}")
        
    print("\n═" * 65)
    print("  PROPOSED NETWORK EXPANSION")
    print("═" * 65)
    route = propose_integrated_network_expansion()
    print(f"  Proposed Route: {route['name']}")
    print(f"  Stops: {' -> '.join(NODES[s]['name'] if s in NODES else s for s in route['stops'])}")
    print(f"  Est. Daily Passengers: {route['estimated_daily_demand']:,.0f}")
