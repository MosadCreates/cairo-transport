# CSE112 — Smart City Transportation Network Optimization
## Greater Cairo Metropolitan Area

---

## Project Structure

```
cairo_transport/
├── core/                    # Fundamental data (data.py, graph.py)
├── algorithms/              # AI & Optimization (mst, shortest_path, dp, greedy, ml)
├── utils/                   # Helper scripts (visualization, tests, transit)
├── docs/                    # Technical reports and documentation
├── outputs/                 # Generated figures (auto-created)
├── app.py                   # Streamlit Web App (Main Dashboard)
├── main.py                  # CLI Demo Runner
├── requirements.txt         # Project dependencies
└── Dockerfile               # Containerization configuration
    ├── fig1_network.png     # Full Cairo network map
    ├── fig2_mst.png         # MST overlay
    ├── fig3_paths.png       # Shortest path visualizations
    └── fig4_congestion.png  # Traffic congestion heat-maps
```

---

## Setup

```bash
pip install matplotlib
```

---

## Running the Demo

```bash
cd cairo_transport
pip install -r requirements.txt
```

### Running the Web App (Streamlit)
To launch the interactive dashboard with the side-by-side visualizer and ML predictions:
```bash
streamlit run app.py
```

### Running via Docker
If you have Docker installed, you can build and run the entire project seamlessly:
```bash
docker build -t cairo-transport-ai .
docker run -p 8501:8501 cairo-transport-ai
```
Then open `http://localhost:8501` in your browser.

### Running the CLI Demo
```bash
python main.py
```
When prompted, enter `y` to generate all 4 matplotlib figures.

---

## Running the Tests

To verify the correctness of the core algorithms, run the suite of unit tests:

```bash
python utils/test_algorithms.py
```

---

## Algorithms Implemented

### A. Minimum Spanning Tree — `mst.py`
- **Algorithm:** Kruskal's with Union-Find (path compression + union by rank)
- **Modification:** Population-weighted edges; critical facilities (hospitals, government) forced into MST
- **Complexity:** O(E log E) for sort + O(E α(V)) for Union-Find ≈ O(E log E)
- **Output:** Which of the 15 potential new roads to build, total cost

### B. Shortest Path — `shortest_path.py`
- **Dijkstra:** Standard SSSP for distance-based route planning
- **A\*:** Emergency vehicle routing using Euclidean coordinate heuristic (80 km/h)
- **Time-Dependent Dijkstra:** BPR congestion model for 4 traffic periods
- **Bonus:** Memoization cache, alternate route (road closure simulation)
- **Complexity:** O((V+E) log V) for all three

### C. Dynamic Programming — `dp_solutions.py`
1. **Bus Fleet Allocation:** Bounded knapsack over 10 routes, 250 buses → O(R×B)
2. **Road Maintenance Budget:** 0/1 Knapsack — maximize benefit within 500 M EGP budget → O(N×W)
3. **Metro Headway Optimization:** Discrete DP over headway values using round-trip fleet model

### D. Greedy Algorithms — `greedy.py`
- **Traffic Signals:** Green-time ∝ approach flow (provably optimal for isolated intersections)
- **Emergency Preemption:** Priority queue clearing highest-delay intersections first
- **Optimality Analysis:** 6 scenarios where greedy is optimal vs. suboptimal

### E. AI & Machine Learning — `ml_prediction.py`
- **Random Forest Regressor:** Built using `scikit-learn`
- **Features:** Temporal encoding, capacity, distance, and road condition
- **Function:** Predicts congestion ratio on hypothetical or existing road segments

### F. Web App UI — `app.py`
- **Streamlit Dashboard:** Fully interactive UI with tabs
- **Side-by-Side Comparison:** Compares Dijkstra's distance metrics against A* emergency ETA.
- **Deployment:** Containerized via Docker for easy deployment on platforms like Render or Vercel.

---

## Technical Report
See `TECHNICAL_REPORT.md` for the in-depth comprehensive report covering:
- System architecture and design decisions
- Algorithm implementations and modifications
- Time and space complexity derivation for all major components
- Performance evaluation results
- Challenges encountered and future work

---

## Key Results

| Component            | Metric                                | Value               |
|----------------------|---------------------------------------|---------------------|
| MST Infrastructure   | New roads to build                    | 5 roads             |
| MST Infrastructure   | Construction cost                     | 5,700 M EGP         |
| Emergency Response   | Giza → Qasr El Aini (A*)             | 3.1 min @ 80 km/h   |
| Traffic Opt.         | Morning vs. Night travel Downtown     | 23.7 → 21.1 min     |
| Bus Scheduling (DP)  | Fleet of 250 buses, 10 routes         | +16% passengers     |
| Road Maintenance     | Within 500 M EGP budget               | 19 roads repaired   |
| Metro Headway        | Optimal headway (50 trains)           | 2 min (3× frequency)|

---

## Dependencies
- Python 3.8+
- matplotlib (for visualization only)
- No other external libraries required
