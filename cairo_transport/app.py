import streamlit as st
import pandas as pd
import os

from core.data import NODES, EXISTING_ROADS, POTENTIAL_ROADS, CRITICAL_NODES, METRO_LINES, BUS_ROUTES
from core.graph import build_cairo_graph
from algorithms.shortest_path import shortest_path, astar, time_dependent_dijkstra
from algorithms.mst import kruskal_mst, analyze_mst
from algorithms.dp_solutions import bus_fleet_allocation, road_maintenance_knapsack, metro_headway_optimization
from algorithms.ml_prediction import train_congestion_model, predict_congestion
from algorithms.greedy import traffic_signal_optimization, emergency_preemption
from utils.interactive_maps import (
    create_interactive_network, 
    create_interactive_mst, 
    create_interactive_path, 
    create_interactive_congestion
)

# --- Page Config ---
st.set_page_config(
    page_title="Cairo Smart Transport AI",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Custom CSS for Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #f8fafc;
    }
    /* Hide Sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    /* Top Navbar Simulation */
    .nav-container {
        background-color: #ffffff;
        padding: 1rem 2rem;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
        border-bottom: none;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre;
        background-color: transparent;
        border-radius: 4px;
        color: #64748b;
        font-weight: 600;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        color: #3b82f6 !important;
        border-bottom: 2px solid #3b82f6 !important;
    }
    .stMetric {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }
    h1, h2, h3 {
        color: #0f172a;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Data Helpers ---
@st.cache_data
def get_graph(potential=True):
    return build_cairo_graph(include_potential=potential)

@st.cache_resource
def get_ml_model():
    model, df, mse, r2 = train_congestion_model()
    return model, df, mse, r2

# --- Header & Navigation ---
st.markdown("""
    <div class="nav-container">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 24px;">🚦</span>
            <span style="font-size: 20px; font-weight: 800; color: #0f172a;">Cairo AI Transport</span>
        </div>
        <div style="color: #64748b; font-size: 14px; font-weight: 500;">
            Smart City Optimization Dashboard
        </div>
    </div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "📊 Overview", 
    "🏗️ Infrastructure", 
    "🚀 Traffic & Emergency", 
    "🚌 Transit", 
    "🚦 Control", 
    "🔮 AI Predictor"
])

# ---------------------------------------------------------
# 1. 📊 NETWORK OVERVIEW
# ---------------------------------------------------------
with tabs[0]:
    st.title("Cairo Network Overview")
    st.markdown("Analyzing the current state of the Greater Cairo transportation network before optimization.")
    
    st.markdown("""
    <div class="step-card">
        <h3 style='margin-top:0'>Pipeline Sequence</h3>
        <p><b>1. Overview:</b> Load network graph and traffic data.</p>
        <p><b>2. Infrastructure (MST):</b> Design cost-efficient expansions connecting critical hubs.</p>
        <p><b>3. Traffic (Shortest Path):</b> Route vehicles around congestion and coordinate emergencies.</p>
        <p><b>4. Transit (DP):</b> Optimally allocate buses and metro resources.</p>
        <p><b>5. Real-Time (Greedy):</b> Actively control traffic signals and preemption.</p>
    </div>
    """, unsafe_allow_html=True)

    # Top level metrics
    col1, col2, col3, col4 = st.columns(4)
    total_pop = sum(n.get("pop", 0) for n in NODES.values())
    col1.metric("Total Nodes", len(NODES))
    col2.metric("Existing Roads", len(EXISTING_ROADS))
    col3.metric("Total Population", f"{total_pop:,}")
    col4.metric("Potential Roads", len(POTENTIAL_ROADS))

    st.divider()

    # Layout for data exploration
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("Neighborhoods & Facilities")
        nodes_df = pd.DataFrame.from_dict(NODES, orient='index')
        nodes_df = nodes_df[['name', 'type', 'pop']].reset_index().rename(columns={'index': 'ID'})
        st.dataframe(nodes_df, height=400, use_container_width=True)

    with right_col:
        st.subheader("Existing Road Infrastructure")
        roads_df = pd.DataFrame(EXISTING_ROADS, columns=["From", "To", "Dist (km)", "Cap (veh/h)", "Cond (1-10)"])
        # Replace IDs with names for readability
        roads_df['From'] = roads_df['From'].apply(lambda x: NODES[x]['name'])
        roads_df['To'] = roads_df['To'].apply(lambda x: NODES[x]['name'])
        st.dataframe(roads_df, height=400, use_container_width=True)

    st.subheader("Interactive Network Topology")
    st.plotly_chart(create_interactive_network(), use_container_width=True)

# ---------------------------------------------------------
# 2. 🏗️ INFRASTRUCTURE NETWORK DESIGN (MST)
# ---------------------------------------------------------
with tabs[1]:
    st.title("Infrastructure Network Expansion")
    st.markdown("Using **Kruskal's Algorithm** with population-weighted factors to design an optimal, cost-efficient road network.")

    g_full = get_graph(potential=True)
    mst_edges, cost, dist = kruskal_mst(g_full)
    info = analyze_mst(mst_edges)

    m1, m2, m3 = st.columns(3)
    m1.metric("Recommended New Roads", info['new_roads'])
    m2.metric("Total Construction Cost", f"{info['construction_cost']:,} M EGP")
    m3.metric("Total Spanning Distance", f"{info['total_dist_km']} km")

    st.divider()

    tab1, tab2 = st.tabs(["📊 Cost & Expansion Analysis", "🏥 Critical Connectivity"])
    
    with tab1:
        st.subheader("New Roads to Build")
        new_roads_df = pd.DataFrame(info['new_roads_detail'], columns=["From", "To", "Cost (M EGP)"])
        st.dataframe(new_roads_df, use_container_width=True)

    with tab2:
        st.subheader("Critical Connectivity Guaranteed")
        critical_names = [NODES[n]['name'] for n in CRITICAL_NODES]
        st.info("The algorithm structurally guarantees the inclusion of these key facilities by assigning near-zero weights to their incident edges.")
        for name in critical_names:
            st.markdown(f"- ✅ **{name}**")

    st.divider()
    st.subheader("Interactive MST Expansion Overlay")
    st.plotly_chart(create_interactive_mst(g_full), use_container_width=True)

# ---------------------------------------------------------
# 3. 🚀 TRAFFIC FLOW & EMERGENCY RESPONSE
# ---------------------------------------------------------
with tabs[2]:
    st.title("Traffic Flow & Emergency Optimization")
    st.markdown("Comparing **Dijkstra** (Standard) vs **A*** (Emergency) vs **Time-Dependent Dijkstra** (Rush Hour).")

    g_ex = get_graph(potential=False)
    nodes_list = list(NODES.keys())
    node_names = {n: NODES[n]["name"] for n in nodes_list}

    # Route Input
    exp = st.expander("🛠️ Route Configuration", expanded=True)
    with exp:
        c1, c2 = st.columns(2)
        src = c1.selectbox("Starting Location", nodes_list, format_func=lambda x: node_names[x], index=nodes_list.index(8))
        dst = c2.selectbox("Destination", nodes_list, format_func=lambda x: node_names[x], index=nodes_list.index("F9"))
        
        route_type = st.radio("Optimization Mode", ["Standard Routing (Dijkstra)", "Emergency Response (A*)", "Time-Dependent (Rush Hour)"], horizontal=True)

    # 1. Period selection (needed for Time-Dependent Dijkstra)
    period = "morning"
    if route_type == "Time-Dependent (Rush Hour)":
        period = st.selectbox("Select Rush Hour Period", ["morning", "afternoon", "evening", "night"])

    # 2. Execution logic
    if st.button("Execute Optimization", type="primary"):
        if route_type == "Standard Routing (Dijkstra)":
            dist_val, path = shortest_path(g_ex, src, dst)
            if path:
                st.subheader("Dijkstra's Algorithm Result")
                colA, colB = st.columns(2)
                colA.metric("Total Distance", f"{dist_val:.2f} km")
                colB.metric("Algorithm Complexity", "O((V+E) log V)")
                st.success(" → ".join([node_names[n] for n in path]))
                st.info("💡 **Why Dijkstra?** It guarantees the optimal path by incrementally exploring shortest known routes, ideal for standard distance-based navigation.")
            else:
                st.error("No path found.")

        elif route_type == "Emergency Response (A*)":
            time_val, path = astar(g_ex, src, dst)
            if path:
                st.subheader("A* Emergency Search Result")
                colA, colB = st.columns(2)
                colA.metric("Estimated ETA", f"{time_val:.1f} mins", delta="At 80 km/h", delta_color="inverse")
                colB.metric("Heuristic Used", "Euclidean Distance")
                st.success(" → ".join([node_names[n] for n in path]))
                st.info("💡 **Why A*?** By using a heuristic (straight-line distance), A* heavily prioritizes searching in the direction of the destination, drastically reducing computation time for emergency routing.")
            else:
                st.error("No path found.")

        elif route_type == "Time-Dependent (Rush Hour)":
            time_val, path = time_dependent_dijkstra(g_ex, src, dst, period)
            if path:
                st.subheader(f"Time-Dependent Routing ({period.capitalize()})")
                st.metric("Total Travel Time", f"{time_val:.1f} mins")
                st.warning(" → ".join([node_names[n] for n in path]))
                st.info("💡 **Why Time-Dependent?** It calculates weights dynamically based on real-time traffic flow models (BPR function), avoiding congested areas during peak hours.")
            else:
                st.error("No path found.")

    # 3. Interactive Path Visualization
    st.divider()
    st.subheader("Interactive Route Visualization")
    
    m_algo = "dijkstra"
    if route_type == "Emergency Response (A*)":
        m_algo = "astar"
    elif route_type == "Time-Dependent (Rush Hour)":
        m_algo = "time_dependent"
    
    fig_path = create_interactive_path(g_ex, src, dst, algo_type=m_algo, period=period)
    st.plotly_chart(fig_path, use_container_width=True)

# ---------------------------------------------------------
# 4. 🚌 PUBLIC TRANSIT & RESOURCE OPTIMIZATION (DP)
# ---------------------------------------------------------
with tabs[3]:
    st.title("Public Transit & Resource Optimization")
    st.markdown("Solving large-scale allocation problems using **Dynamic Programming**.")

    st.info("💡 **Why Dynamic Programming?** DP efficiently solves resource allocation problems by breaking them into smaller overlapping subproblems. Here, we use variations of the Knapsack problem to maximize coverage with limited resources.")
    
    col_dp1, col_dp2 = st.columns(2)

    with col_dp1:
        st.subheader("Bus Fleet Allocation (Knapsack DP)")
        total_buses = st.slider("Total Available Fleet", 50, 500, 250)
        alloc, total_pass, _ = bus_fleet_allocation(total_buses)
        st.metric("Total Daily Passengers Served", f"{total_pass:,}")

        alloc_data = [{"Route": k, "Buses": v} for k, v in alloc.items()]
        st.bar_chart(pd.DataFrame(alloc_data).set_index("Route"))

    with col_dp2:
        st.subheader("Road Maintenance Budget (0/1 Knapsack)")
        budget = st.slider("Maintenance Budget (M EGP)", 100, 1000, 500)
        selected_roads, total_benefit, actual_cost = road_maintenance_knapsack(budget)
        st.metric("Total Benefit Score", f"{total_benefit:.1f}")
        st.metric("Actual Budget Used", f"{actual_cost} M EGP")
        st.write(f"Selected {len(selected_roads)} road segments for repair.")

    st.divider()

    st.subheader("Metro Network Efficiency (Fleet DP)")
    
    # Input for total available trains to be distributed by the DP algorithm
    total_metro_fleet = st.number_input("Total Metro Trains Available", 50, 300, 120)
    
    # Execute the Bounded Knapsack DP optimization
    metro_results = metro_headway_optimization(total_metro_fleet)
    
    # Create dynamic columns based on the number of metro lines
    m_cols = st.columns(len(metro_results))
    
    for i, res in enumerate(metro_results):
        # Display optimal headway as the main metric and assigned trains as the delta
        m_cols[i].metric(
            res['line'], 
            f"{res['optimal_hw']} min", 
            delta=f"{res['trains_needed']} Trains"
        )
        # Show the percentage of improvement in passenger capacity
        m_cols[i].write(f"Growth: **+{res['improvement_%']}%**")
# ---------------------------------------------------------
# 5. 🚦 REAL-TIME TRAFFIC & PREEMPTION (Greedy)
# ---------------------------------------------------------
with tabs[4]:
    st.title("Real-Time Traffic & Preemption")
    st.markdown("Applying **Greedy Algorithms** for intersection signal control and emergency priority.")

    st.info("💡 **Why Greedy?** Greedy algorithms make locally optimal choices at each stage. For independent intersection signals and time-critical emergency preemption, local greedy choices guarantee the global optimum response time.")

    tab_signal, tab_emerg = st.tabs(["🚦 Traffic Signal Optimization", "🚑 Emergency Preemption"])
    
    with tab_signal:
        st.subheader("Traffic Signal Optimization")
        period = st.selectbox("Current Period", ["morning", "afternoon", "evening", "night"])
        signals = traffic_signal_optimization(period)
    
        st.write("Top congested intersections requiring active management:")
        for s in signals[:5]:
            with st.expander(f"{s['name']} (Total Flow: {s['total_flow']} veh/hr)"):
                for nbr, flow, green in s["arms"]:
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"To **{NODES[nbr]['name']}**: {flow} veh/hr")
                    c1.progress(min(green / 90.0, 1.0))
                    c2.markdown(f"**{green}s Green**")

    with tab_emerg:
        st.subheader("Emergency Vehicle Preemption")
        nodes_list = list(NODES.keys())
        node_names = {n: NODES[n]["name"] for n in nodes_list}
        p_src = st.selectbox("Emergency Start", nodes_list, format_func=lambda x: node_names[x], index=nodes_list.index(8), key="p_src") # Giza
        p_dst = "F9" # Qasr Hosp
        g_ex = get_graph(potential=False)
        _, path = astar(g_ex, p_src, p_dst)
        if path:
            preempts, saved_time = emergency_preemption(path)
        else:
            preempts, saved_time = [], 0.0
    
        colP1, colP2 = st.columns(2)
        colP1.metric("Total Time Saved", f"{saved_time:.1f} sec")
        colP1.write(f"Preempted {len(preempts)} signals along the path.")
    
        with colP2:
            st.write("Signal Preemption Queue:")
            if preempts:
                for p in preempts:
                    st.markdown(f"- **{NODES[p['node']]['name']}**: Saved {p['time_saved']:.1f}s")
            else:
                st.write("No preemption needed or path not found.")

# ---------------------------------------------------------
# 6. AI CONGESTION PREDICTOR (ML)
# ---------------------------------------------------------
with tabs[5]:
    st.title("AI-Based Congestion Forecasting")
    st.markdown("A **Random Forest** model trained to predict traffic congestion based on road attributes.")

    st.info("💡 **Why Random Forest?** An ensemble learning method was selected to capture non-linear relationships between road conditions, time-of-day, and traffic volume. It automatically handles feature interactions better than simple linear models.")

    model, df, mse, r2 = get_ml_model()

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Model R² Score", f"{r2:.3f}")
    mc2.metric("Mean Squared Error", f"{mse:.4f}")
    mc3.metric("Training Set Size", f"{len(df)} segments")

    st.divider()

    st.subheader("Real-Time Prediction Interface")
    p_col1, p_col2 = st.columns(2)
    dist = p_col1.number_input("Segment Distance (km)", 1.0, 100.0, 5.0)
    cap = p_col1.number_input("Segment Capacity (veh/hr)", 500, 6000, 3000)
    cond = p_col2.slider("Road Quality (1-10)", 1, 10, 7)
    time = p_col2.selectbox("Time of Day", ["morning", "afternoon", "evening", "night"])

    if st.button("🔮 Predict Congestion Ratio"):
        pred = predict_congestion(model, dist, cap, cond, time)
        ratio = pred * 100
        if ratio > 85:
            st.error(f"Prediction: {ratio:.1f}% - HIGH CONGESTION EXPECTED")
        elif ratio > 60:
            st.warning(f"Prediction: {ratio:.1f}% - MODERATE TRAFFIC")
        else:
            st.success(f"Prediction: {ratio:.1f}% - CLEAR FLOW")

    st.divider()
    st.subheader(f"System-wide Congestion Forecast: {time.capitalize()}")
    st.plotly_chart(create_interactive_congestion(time), use_container_width=True)

