"""
interactive_maps.py — CSE112 Project
Plotly-based interactive visualizations for the Cairo transportation system.
"""

import plotly.graph_objects as go
from core.data import NODES, EXISTING_ROADS, POTENTIAL_ROADS, TRAFFIC_FLOW, CRITICAL_NODES
from algorithms.mst import kruskal_mst
from algorithms.shortest_path import shortest_path, astar, time_dependent_dijkstra

# ─────────────────────────────────────────────────────────────
# Colours & Helpers
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

def _get_node_trace(nodes_list=None, size=12):
    if nodes_list is None:
        nodes_list = list(NODES.keys())
    
    lons, lats, names, types, colors = [], [], [], [], []
    for nid in nodes_list:
        x, y = _pos(nid)
        node = NODES[nid]
        lons.append(x)
        lats.append(y)
        names.append(node["name"])
        types.append(node["type"])
        colors.append(TYPE_COLOR.get(node["type"], "#607D8B"))
        
    # Subtle Glow trace for light theme
    outline = go.Scattermapbox(
        lon=lons,
        lat=lats,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=size + 4,
            color="white",
            opacity=0.6
        ),
        showlegend=False,
        hoverinfo='none'
    )

    # Main trace
    main = go.Scattermapbox(
        lon=lons,
        lat=lats,
        mode='markers+text',
        marker=go.scattermapbox.Marker(
            size=size,
            color=colors,
            opacity=1.0,
        ),
        text=names,
        textposition="top center",
        textfont=dict(size=10, color="#374151"), # Dark gray text
        hoverinfo='text',
        hovertext=[f"<b>{name}</b><br>Type: {t}<br>ID: {idx}" for name, t, idx in zip(names, types, nodes_list)],
        name="Locations"
    )
    return [outline, main]

def _get_edge_trace(edges, color, width, name, opacity=0.8):
    lons = []
    lats = []
    for edge in edges:
        u, v = edge[0], edge[1]
        xu, yu = _pos(u)
        xv, yv = _pos(v)
        lons.extend([xu, xv, None])
        lats.extend([yu, yv, None])
    
    # Light shadow trace (subtle depth)
    shadow = go.Scattermapbox(
        lon=lons,
        lat=lats,
        mode='lines',
        line=dict(width=width + 2, color="#cbd5e1"), # Light gray shadow
        opacity=0.4,
        showlegend=False,
        hoverinfo='none'
    )
    
    # Main trace
    main = go.Scattermapbox(
        lon=lons,
        lat=lats,
        mode='lines',
        line=dict(width=width, color=color),
        opacity=opacity,
        name=name,
        hoverinfo='none'
    )
    
    return [shadow, main]

def _apply_layout(fig, title):
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=20, color="#111827")),
        paper_bgcolor="#FFFFFF", # Clean white background
        plot_bgcolor="#FFFFFF",
        mapbox=dict(
            style="carto-positron", # Light Google-like theme
            center=dict(lon=31.35, lat=30.0),
            zoom=9.2
        ),
        margin=dict(l=0, r=0, t=60, b=0),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.95,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(255, 255, 255, 0.8)",
            font=dict(color="#111827"),
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1
        )
    )

# ─────────────────────────────────────────────────────────────
# 1. Full Network Map
# ─────────────────────────────────────────────────────────────
def create_interactive_network():
    fig = go.Figure()
    
    # Potential Roads
    potential_edges = [(u, v) for u, v, *_ in POTENTIAL_ROADS]
    fig.add_traces(_get_edge_trace(potential_edges, "#64748b", 1.5, "Potential Roads", opacity=0.4))
    
    # Existing Roads (Darker and Thicker)
    existing_edges = [(u, v) for u, v, *_ in EXISTING_ROADS]
    fig.add_traces(_get_edge_trace(existing_edges, "#1e293b", 4.0, "Existing Roads"))
    
    # Nodes
    fig.add_traces(_get_node_trace())
    
    _apply_layout(fig, "Greater Cairo Transportation Network")
    return fig

# ─────────────────────────────────────────────────────────────
# 2. MST Map
# ─────────────────────────────────────────────────────────────
def create_interactive_mst(g):
    mst, cost, dist = kruskal_mst(g)
    
    fig = go.Figure()
    
    # Background (Existing)
    existing_edges = [(u, v) for u, v, *_ in EXISTING_ROADS]
    fig.add_traces(_get_edge_trace(existing_edges, "#64748b", 1.2, "Existing Network", opacity=0.4))
    
    # MST Edges
    new_mst, old_mst = [], []
    for (u, v, attr, w) in mst:
        if attr.get("is_new"): new_mst.append((u, v))
        else: old_mst.append((u, v))
            
    fig.add_traces(_get_edge_trace(old_mst, "#3b82f6", 3, "MST: Existing Road"))
    fig.add_traces(_get_edge_trace(new_mst, "#ef4444", 4.5, "MST: New Construction"))
    
    # Nodes
    fig.add_traces(_get_node_trace(size=14))
    
    _apply_layout(fig, f"Infrastructure Expansion (MST) - Cost: {cost:,.0f}M EGP")
    return fig

# ─────────────────────────────────────────────────────────────
# 3. Shortest Path Map
# ─────────────────────────────────────────────────────────────
def create_interactive_path(g, source, target, algo_type="dijkstra", period="morning"):
    fig = go.Figure()
    
    # Background (Darker/More distinct)
    existing_edges = [(u, v) for u, v, *_ in EXISTING_ROADS]
    fig.add_traces(_get_edge_trace(existing_edges, "#64748b", 1.2, "Road Network", opacity=0.3))
    
    # Path calculation
    path, title, color = [], "", "#2563eb" # Google Blue
    
    if algo_type == "dijkstra":
        _, path = shortest_path(g, source, target)
        title = f"Dijkstra: {NODES[source]['name']} → {NODES[target]['name']}"
    elif algo_type == "astar":
        _, path = astar(g, source, target)
        title = f"A* Emergency: {NODES[source]['name']} → {NODES[target]['name']}"
        color = "#ef4444"
    elif algo_type == "time_dependent":
        _, path = time_dependent_dijkstra(g, source, target, period)
        title = f"Rush Hour ({period.capitalize()}): {NODES[source]['name']} → {NODES[target]['name']}"
        color = "#f59e0b"
    
    if path and len(path) >= 2:
        path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
        fig.add_traces(_get_edge_trace(path_edges, color, 6, "Optimal Path", opacity=1.0))
        
        # Start/End Markers
        x_s, y_s = _pos(path[0])
        x_e, y_e = _pos(path[-1])
        fig.add_trace(go.Scattermapbox(
            lon=[x_s, x_e], lat=[y_s, y_e], mode='markers',
            marker=go.scattermapbox.Marker(size=22, color=['#22c55e', '#ef4444'], symbol='marker'),
            hoverinfo='text', hovertext=['START', 'DESTINATION'], showlegend=False
        ))
        
    fig.add_traces(_get_node_trace(size=8))
    _apply_layout(fig, title)
    return fig

# ─────────────────────────────────────────────────────────────
# 4. Congestion Map
# ─────────────────────────────────────────────────────────────
def create_interactive_congestion(period="morning"):
    fig = go.Figure()
    
    # We draw edges individually to have different colors
    for (u, v, dist, cap, cond) in EXISTING_ROADS:
        tf = TRAFFIC_FLOW.get((u, v)) or TRAFFIC_FLOW.get((v, u)) or {}
        flow = tf.get(period, cap * 0.5)
        ratio = min(flow / cap, 1.2)
        
        # Color interpolation
        r = int(min(255, ratio * 255))
        g = int(max(0, 255 - ratio * 255))
        color = f"rgb({r}, {g}, 0)"
        
        xu, yu = _pos(u)
        xv, yv = _pos(v)
        
        # Shadow for congestion roads (very subtle in light theme)
        fig.add_trace(go.Scattermapbox(
            lon=[xu, xv, None], lat=[yu, yv, None], mode='lines',
            line=dict(width=5 + ratio*4, color="#e2e8f0"), opacity=0.3, showlegend=False, hoverinfo='none'
        ))
        
        fig.add_trace(go.Scattermapbox(
            lon=[xu, xv, None], lat=[yu, yv, None], mode='lines',
            line=dict(width=3 + ratio*4, color=color), opacity=0.95,
            showlegend=False, hoverinfo='text',
            hovertext=f"Road: {NODES[u]['name']} - {NODES[v]['name']}<br>Congestion: {ratio*100:.1f}%"
        ))
        
    fig.add_traces(_get_node_trace(size=7))
    _apply_layout(fig, f"Real-Time Traffic Congestion - {period.capitalize()}")
    return fig
